# Import torch first to avoid DLL conflict under Windows
import torch
import sys
import os
import math
import re
from datetime import datetime, timezone
from uuid import uuid4
from flask import Flask, render_template, request, jsonify
from werkzeug.exceptions import BadRequest

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Ensure recommender is importable
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from recommender import MuterBandungRecommender, RUNTIME_CANDIDATE_DB_PATH
from oleh_oleh_recommender import OlehOlehRecommender, DEFAULT_OLEH_OLEH_DATASET_PATH
from penginapan_recommender import PenginapanRecommender, DEFAULT_PENGINAPAN_DATASET_PATH
from llm_evidence_pack import build_llm_evidence_pack, build_oleh_oleh_evidence_pack
from llm_service import generate_rag_summary
from llm_guard import build_llm_prompt_guard, validate_llm_output

app = Flask(__name__)

API_SCHEMA_VERSION = "muterbandung.api.recommend.v1"
OLEH_OLEH_API_SCHEMA_VERSION = "muterbandung.api.oleh_oleh.recommend.v1"
PENGINAPAN_API_SCHEMA_VERSION = "muterbandung.api.penginapan.recommend.v1"
MAX_QUERY_LENGTH = 500
MAX_CATEGORY_COUNT = 20
MAX_CATEGORY_LENGTH = 64
MAX_TOP_K = 20
MAX_PRICE = 10_000_000
MAX_DISTANCE_KM = 200.0
VALID_SORT_MODES = {"relevance", "balanced", "nearest"}
VALID_DAY_TYPES = {"weekday", "weekend"}
VALID_PENGINAPAN_PROPERTY_TYPES = {
    "hotel",
    "guest_house",
    "villa",
    "apartment",
    "vacation_rental",
    "room_level_listing",
}
DEFAULT_DATASET_PATH = (
    os.getenv("MUTERBANDUNG_DATASET_PATH")
    or os.getenv("MUTERBANDUNG_DB_PATH")
    or RUNTIME_CANDIDATE_DB_PATH
)
DEFAULT_OLEH_OLEH_PATH = (
    os.getenv("MUTERBANDUNG_OLEH_OLEH_DATASET_PATH")
    or DEFAULT_OLEH_OLEH_DATASET_PATH
)
DEFAULT_PENGINAPAN_PATH = (
    os.getenv("MUTERBANDUNG_PENGINAPAN_DATASET_PATH")
    or DEFAULT_PENGINAPAN_DATASET_PATH
)


def _utc_now_iso():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _data_version():
    path = getattr(engine, "source_db_path", None) if engine is not None else None
    if not path or not os.path.exists(path):
        return "unknown"
    return f"{os.path.basename(path)}:{int(os.path.getmtime(path))}"


def _oleh_oleh_data_version():
    path = getattr(oleh_oleh_engine, "dataset_path", None) if oleh_oleh_engine is not None else None
    if not path or not os.path.exists(path):
        return "unknown"
    return f"{os.path.basename(path)}:{int(os.path.getmtime(path))}"


def _penginapan_data_version():
    path = getattr(penginapan_engine, "dataset_path", None) if penginapan_engine is not None else None
    if not path or not os.path.exists(path):
        return "unknown"
    return f"{os.path.basename(path)}:{int(os.path.getmtime(path))}"


def _response_metadata(request_id=None):
    return {
        "api_schema_version": API_SCHEMA_VERSION,
        "data_version": _data_version(),
        "request_id": request_id or str(uuid4()),
        "generated_at": _utc_now_iso(),
    }


def _oleh_oleh_response_metadata(request_id=None):
    return {
        "api_schema_version": OLEH_OLEH_API_SCHEMA_VERSION,
        "data_version": _oleh_oleh_data_version(),
        "request_id": request_id or str(uuid4()),
        "generated_at": _utc_now_iso(),
    }


def _penginapan_response_metadata(request_id=None):
    return {
        "api_schema_version": PENGINAPAN_API_SCHEMA_VERSION,
        "data_version": _penginapan_data_version(),
        "request_id": request_id or str(uuid4()),
        "generated_at": _utc_now_iso(),
        "ranking_mode": "distance_weighted_baseline",
    }


def _error_response(message, errors, status_code=400, metadata=None):
    payload = {
        "status": "error",
        "message": message,
        "errors": errors,
    }
    payload.update(metadata or _response_metadata())
    return jsonify(payload), status_code


def _load_json_body():
    raw_body = request.get_data(cache=True)
    if not raw_body or not raw_body.strip():
        return {}, []
    if not request.is_json:
        return None, ["Content-Type must be application/json."]
    try:
        data = request.get_json(silent=False)
    except BadRequest:
        return None, ["Malformed JSON body."]
    if data is None:
        return {}, []
    if not isinstance(data, dict):
        return None, ["JSON body must be an object."]
    return data, []


def _parse_optional_text(data, field, errors, max_length):
    value = data.get(field)
    if value is None:
        return None
    if not isinstance(value, str):
        errors.append(f"{field} must be a string.")
        return None
    value = value.strip()
    if not value:
        return None
    if len(value) > max_length:
        errors.append(f"{field} must be at most {max_length} characters.")
        return None
    return value


def _parse_categories(data, errors):
    value = data.get("categories", [])
    if value is None or value == "":
        return None
    raw_items = value if isinstance(value, list) else [value]
    if len(raw_items) > MAX_CATEGORY_COUNT:
        errors.append(f"categories must contain at most {MAX_CATEGORY_COUNT} items.")
        return None

    categories = []
    for item in raw_items:
        if not isinstance(item, str):
            errors.append("categories items must be strings.")
            continue
        item = item.strip()
        if not item:
            continue
        if len(item) > MAX_CATEGORY_LENGTH:
            errors.append(f"categories items must be at most {MAX_CATEGORY_LENGTH} characters.")
            continue
        categories.append(item)
    return categories or None


def _parse_property_types(data, errors):
    value = data.get("property_types")
    if value is None or value == "":
        value = data.get("property_type")
    if value is None or value == "":
        return None
    raw_items = value if isinstance(value, list) else [value]
    property_types = []
    for item in raw_items:
        if not isinstance(item, str):
            errors.append("property_types items must be strings.")
            continue
        normalized = item.strip().lower()
        if not normalized:
            continue
        if normalized not in VALID_PENGINAPAN_PROPERTY_TYPES:
            errors.append(
                f"property_types must contain only: {', '.join(sorted(VALID_PENGINAPAN_PROPERTY_TYPES))}."
            )
            continue
        property_types.append(normalized)
    return property_types or None


def _parse_bool(data, field, errors, default=False):
    value = data.get(field)
    if value is None or value == "":
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, int) and value in (0, 1):
        return bool(value)
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes", "y", "on"}:
            return True
        if normalized in {"false", "0", "no", "n", "off"}:
            return False
    errors.append(f"{field} must be a boolean.")
    return default


def _parse_int(data, field, errors, default=None, min_value=None, max_value=None):
    value = data.get(field)
    if value is None or value == "":
        return default
    if isinstance(value, bool):
        errors.append(f"{field} must be an integer.")
        return default
    if isinstance(value, float) and not value.is_integer():
        errors.append(f"{field} must be an integer.")
        return default
    if isinstance(value, str) and not re.fullmatch(r"-?\d+", value.strip()):
        errors.append(f"{field} must be an integer.")
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        errors.append(f"{field} must be an integer.")
        return default
    if min_value is not None and parsed < min_value:
        errors.append(f"{field} must be greater than or equal to {min_value}.")
    if max_value is not None and parsed > max_value:
        errors.append(f"{field} must be less than or equal to {max_value}.")
    return parsed


def _parse_float(data, field, errors, default=None, min_value=None, max_value=None):
    value = data.get(field)
    if value is None or value == "":
        return default
    if isinstance(value, bool):
        errors.append(f"{field} must be a number.")
        return default
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        errors.append(f"{field} must be a number.")
        return default
    if not math.isfinite(parsed):
        errors.append(f"{field} must be a finite number.")
        return default
    if min_value is not None and parsed < min_value:
        errors.append(f"{field} must be greater than or equal to {min_value}.")
    if max_value is not None and parsed > max_value:
        errors.append(f"{field} must be less than or equal to {max_value}.")
    return parsed


def _parse_choice(data, field, errors, valid_values, default=None):
    value = data.get(field)
    if value is None or value == "":
        return default
    if not isinstance(value, str):
        errors.append(f"{field} must be a string.")
        return default
    value = value.strip().lower()
    if value not in valid_values:
        errors.append(f"{field} must be one of: {', '.join(sorted(valid_values))}.")
        return default
    return value


def _parse_open_at_hour(data, errors):
    value = data.get("open_at_hour")
    if value is None or value == "":
        return None
    if not isinstance(value, str):
        errors.append("open_at_hour must be a string in HH:MM format.")
        return None
    value = value.strip()
    match = re.fullmatch(r"(\d{1,2}):([0-5]\d)", value)
    if not match:
        errors.append("open_at_hour must use HH:MM format.")
        return None
    hour = int(match.group(1))
    minute = int(match.group(2))
    if hour > 23:
        errors.append("open_at_hour hour must be between 00 and 23.")
        return None
    return f"{hour:02d}:{minute:02d}"


def _parse_recommend_payload(data):
    errors = []
    parsed = {
        "query": _parse_optional_text(data, "query", errors, MAX_QUERY_LENGTH),
        "categories": _parse_categories(data, errors),
        "max_price": _parse_int(data, "max_price", errors, min_value=0, max_value=MAX_PRICE),
        "min_rating": _parse_float(data, "min_rating", errors, min_value=0.0, max_value=5.0),
        "user_lat": _parse_float(data, "user_lat", errors, min_value=-90.0, max_value=90.0),
        "user_lon": _parse_float(data, "user_lon", errors, min_value=-180.0, max_value=180.0),
        "max_distance_km": _parse_float(data, "max_distance_km", errors, min_value=0.1, max_value=MAX_DISTANCE_KM),
        "sort_by": _parse_choice(data, "sort_by", errors, VALID_SORT_MODES, default="balanced"),
        "free_only": _parse_bool(data, "free_only", errors, default=False),
        "open_now": _parse_bool(data, "open_now", errors, default=False),
        "day_type": _parse_choice(data, "day_type", errors, VALID_DAY_TYPES),
        "open_at_hour": _parse_open_at_hour(data, errors),
        "top_k": _parse_int(data, "top_k", errors, default=5, min_value=1, max_value=MAX_TOP_K),
    }

    has_lat = parsed["user_lat"] is not None
    has_lon = parsed["user_lon"] is not None
    if has_lat != has_lon:
        errors.append("user_lat and user_lon must be provided together.")
    if parsed["max_distance_km"] is not None and not (has_lat and has_lon):
        errors.append("max_distance_km requires user_lat and user_lon.")

    return parsed, errors

# Initialize the recommender engine
# Note: In production, consider lazy loading or application context
print("Initializing MuterBandungRecommender...")
try:
    engine = MuterBandungRecommender(db_path=DEFAULT_DATASET_PATH)
    print("Engine initialized successfully.")
except Exception as e:
    print(f"Error initializing engine: {e}")
    engine = None

print("Initializing OlehOlehRecommender...")
try:
    oleh_oleh_engine = OlehOlehRecommender(dataset_path=DEFAULT_OLEH_OLEH_PATH)
    print("Oleh-oleh engine initialized successfully.")
except Exception as e:
    print(f"Error initializing oleh-oleh engine: {e}")
    oleh_oleh_engine = None

print("Initializing PenginapanRecommender...")
try:
    penginapan_engine = PenginapanRecommender(dataset_path=DEFAULT_PENGINAPAN_PATH)
    print("Penginapan engine initialized successfully.")
except Exception as e:
    print(f"Error initializing penginapan engine: {e}")
    penginapan_engine = None

def _generate_ai_summary(results, module="wisata"):
    """Rule-based text generator that summarizes recommendations naturally."""
    recs = results.get("recommendations", [])
    query = results.get("query", "")
    if not recs:
        return None

    top = recs[0]
    total = results.get("after_filtering") or results.get("total_results") or len(recs)

    if module == "penginapan":
        name = top.get("name", "Penginapan")
        rating = top.get("overall_rating")
        price = top.get("price_lowest")
        sentiment = top.get("hotel_adjusted_sentiment_label", "")
        distance = top.get("distance_km")

        parts = [f"Dari {total} penginapan yang cocok, rekomendasi teratas adalah {name}"]
        if rating:
            parts[0] += f" dengan rating {float(rating):.1f}/5.0"
        parts[0] += "."
        if price:
            parts.append(f"Harga mulai dari Rp {int(price):,}.".replace(",", "."))
        if sentiment:
            parts.append(f"Ulasan tamu secara umum bernada {sentiment.lower()}.")
        if distance is not None:
            parts.append(f"Jaraknya sekitar {float(distance):.1f} km dari titik pencarian Anda.")
        return " ".join(parts)
    else:
        name = top.get("location_name", "Destinasi")
        info = top.get("info_praktis", {})
        harga = info.get("harga", "")
        bd = top.get("score_breakdown", {})
        sentiment_label = bd.get("sentiment_label", "")

        parts = [f"Dari {total} destinasi yang cocok, pilihan terbaik adalah {name}"]
        if harga and harga != "Tidak ada info":
            parts[0] += f" dengan harga tiket {harga}"
        parts[0] += "."
        if sentiment_label:
            parts.append(f"Ulasan pengunjung didominasi respon {sentiment_label.lower()}.")
        if len(recs) > 1:
            second = recs[1].get("location_name", "")
            if second:
                parts.append(f"Alternatif lainnya adalah {second}.")
        return " ".join(parts)


@app.route('/')
def index():
    """Render the main UI page."""
    return render_template('index.html')

@app.route('/api/recommend', methods=['POST'])
def recommend_api():
    """API endpoint to get recommendations based on JSON payload."""
    metadata = _response_metadata()
    if engine is None:
        return _error_response(
            "Recommender engine failed to initialize.",
            ["Recommender engine failed to initialize."],
            status_code=500,
            metadata=metadata,
        )

    data, json_errors = _load_json_body()
    if json_errors:
        return _error_response("Invalid request body.", json_errors, status_code=400, metadata=metadata)

    parsed, validation_errors = _parse_recommend_payload(data)
    if validation_errors:
        return _error_response("Invalid request parameters.", validation_errors, status_code=400, metadata=metadata)

    try:
        # Run recommendation
        results = engine.recommend(
            query=parsed["query"],
            categories=parsed["categories"],
            max_price=parsed["max_price"],
            min_rating=parsed["min_rating"],
            free_only=parsed["free_only"],
            open_now=parsed["open_now"],
            day_type=parsed["day_type"],
            open_at_hour=parsed["open_at_hour"],
            user_lat=parsed["user_lat"],
            user_lon=parsed["user_lon"],
            max_distance_km=parsed["max_distance_km"],
            sort_by=parsed["sort_by"],
            top_k=parsed["top_k"],
            explain=True
        )
        evidence_pack = build_llm_evidence_pack(results)
        results["llm_evidence_pack"] = evidence_pack
        results["llm_prompt_guard"] = build_llm_prompt_guard(evidence_pack)
        
        rag_summary = generate_rag_summary(parsed["query"], evidence_pack, module="wisata")
        if rag_summary:
            results["ai_summary"] = rag_summary
        else:
            results["ai_summary"] = _generate_ai_summary(results, module="wisata")
        results.update(metadata)
        return jsonify(results)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return _error_response("Recommendation failed.", [str(e)], status_code=500, metadata=metadata)


@app.route('/api/oleh-oleh/recommend', methods=['POST'])
def oleh_oleh_recommend_api():
    """API endpoint for oleh-oleh recommendations."""
    metadata = _oleh_oleh_response_metadata()
    if oleh_oleh_engine is None:
        return _error_response(
            "Oleh-oleh recommender failed to initialize.",
            ["Oleh-oleh recommender failed to initialize."],
            status_code=500,
            metadata=metadata,
        )

    data, json_errors = _load_json_body()
    if json_errors:
        return _error_response("Invalid request body.", json_errors, status_code=400, metadata=metadata)

    parsed, validation_errors = _parse_recommend_payload(data)
    include_non_main = _parse_bool(data, "include_non_main", validation_errors, default=False)
    if validation_errors:
        return _error_response("Invalid request parameters.", validation_errors, status_code=400, metadata=metadata)

    try:
        results = oleh_oleh_engine.recommend(
            query=parsed["query"],
            categories=parsed["categories"],
            max_price=parsed["max_price"],
            user_lat=parsed["user_lat"],
            user_lon=parsed["user_lon"],
            max_distance_km=parsed["max_distance_km"],
            sort_by=parsed["sort_by"],
            top_k=parsed["top_k"],
            include_non_main=include_non_main,
        )
        results["llm_evidence_pack"] = build_oleh_oleh_evidence_pack(results)
        results.update(metadata)
        return jsonify(results)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return _error_response("Oleh-oleh recommendation failed.", [str(e)], status_code=500, metadata=metadata)


@app.route('/api/penginapan/recommend', methods=['POST'])
def penginapan_recommend_api():
    """Baseline API endpoint for distance-weighted penginapan recommendations."""
    metadata = _penginapan_response_metadata()
    if penginapan_engine is None:
        return _error_response(
            "Penginapan recommender failed to initialize.",
            ["Penginapan recommender failed to initialize."],
            status_code=500,
            metadata=metadata,
        )

    data, json_errors = _load_json_body()
    if json_errors:
        return _error_response("Invalid request body.", json_errors, status_code=400, metadata=metadata)

    parsed, validation_errors = _parse_recommend_payload(data)
    property_types = _parse_property_types(data, validation_errors)
    if validation_errors:
        return _error_response("Invalid request parameters.", validation_errors, status_code=400, metadata=metadata)

    try:
        results = penginapan_engine.recommend(
            query=parsed["query"],
            property_types=property_types,
            max_price=parsed["max_price"],
            min_rating=parsed["min_rating"],
            user_lat=parsed["user_lat"],
            user_lon=parsed["user_lon"],
            max_distance_km=parsed["max_distance_km"],
            sort_by=parsed["sort_by"],
            top_k=parsed["top_k"],
        )
        evidence_pack = {"recommendations": results.get("recommendations", [])[:3]}
        rag_summary = generate_rag_summary(parsed["query"], evidence_pack, module="penginapan")
        if rag_summary:
            results["ai_summary"] = rag_summary
        else:
            results["ai_summary"] = _generate_ai_summary(results, module="penginapan")
        results.update(metadata)
        return jsonify(results)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return _error_response("Penginapan recommendation failed.", [str(e)], status_code=500, metadata=metadata)


@app.route('/api/llm/validate', methods=['POST'])
def validate_llm_api():
    """Validate an LLM JSON answer against a MuterBandung evidence pack."""
    metadata = _response_metadata()
    data, json_errors = _load_json_body()
    if json_errors:
        return _error_response("Invalid request body.", json_errors, status_code=400, metadata=metadata)

    evidence_pack = data.get("llm_evidence_pack") or data.get("evidence_pack")
    llm_output = data.get("llm_output")

    if not isinstance(evidence_pack, dict):
        payload = {
            "valid": False,
            "errors": ["Request must include llm_evidence_pack or evidence_pack object."],
            "warnings": [],
            "sanitized_output": None,
        }
        payload.update(metadata)
        return jsonify(payload), 400

    result = validate_llm_output(llm_output, evidence_pack)
    result.update(metadata)
    return jsonify(result), 200 if result.get("valid") else 422

if __name__ == '__main__':
    # Run server
    debug_enabled = os.getenv('FLASK_DEBUG', '').lower() in ('1', 'true', 'yes')
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', '5000'))
    app.run(host=host, port=port, debug=debug_enabled)
