import nbformat as nbf


NOTEBOOK_PATH = "Notebooks/wisata_training.ipynb"
MARKER = "MUTERBANDUNG_LLM_PROMPT_GUARD_VALIDATOR_2026_05_25"


def append_llm_guard_section():
    with open(NOTEBOOK_PATH, "r", encoding="utf-8") as handle:
        notebook = nbf.read(handle, as_version=4)

    notebook.cells = [
        cell
        for cell in notebook.cells
        if MARKER not in "".join(cell.get("source", ""))
    ]

    markdown = f"""## LLM Prompt Guard + Output Validator

`{MARKER}`

Tahap ini menambahkan pagar produksi untuk lapisan LLM MuterBandung. LLM tetap hanya menjadi explanation layer: kandidat, ranking, harga, jarak, jam buka, sentiment, media URL, dan real-world flags harus berasal dari `llm_evidence_pack`.

Komponen yang ditambahkan:

- `Scripts/llm_guard.py`: pembuat `llm_prompt_guard` dan validator output LLM.
- `POST /api/recommend`: sekarang mengembalikan `llm_evidence_pack` dan `llm_prompt_guard`.
- `POST /api/llm/validate`: menolak output LLM yang mengarang destinasi, harga, jarak, URL gambar/link, website, rating, atau fasilitas.
- `candidate.media`: kontrak media aman. Jika URL gambar/link belum ada di curated dataset, `media.available=false`.

Catatan audit media:

- Pada saat guard dibuat, dataset curated aktif belum memiliki kolom URL gambar atau link destinasi.
- Raw Apify/Google Maps punya kandidat `imageUrl`, `url`, dan `website`.
- Status terbaru: media enrichment sudah dilakukan pada bagian pipeline media enrichment setelah guard ini.
"""

    code = """# Smoke test LLM guard dan validator output
# Jalankan dari root project PIJAK.

import sys
sys.path.insert(0, "Scripts")

from llm_evidence_pack import build_llm_evidence_pack
from llm_guard import build_llm_prompt_guard, validate_llm_output

sample_response = {
    "status": "success",
    "query": "wisata alam sejuk",
    "recommendations": [
        {
            "rank": 1,
            "location_id": "loc_001",
            "location_name": "Contoh Destinasi",
            "category": "Wisata Alam",
            "multi_labels": ["Alam"],
            "label_taxonomy": {"primary_intent": "Alam", "core_labels": ["Alam"]},
            "final_score": 88.5,
            "distance_km": None,
            "distance_label": None,
            "score_breakdown": {
                "sentiment_score": 0.91,
                "sentiment_model_source": "tfidf_linearsvc",
                "sentiment_model_version": "run_nlp_pipeline_v2",
                "sentiment_available": True,
            },
            "sentiment_metadata": {
                "sentiment_score": 0.91,
                "sentiment_model_source": "tfidf_linearsvc",
                "sentiment_model_version": "run_nlp_pipeline_v2",
                "sentiment_available": True,
            },
            "realworld_flags": {"coordinate_verified": True, "safety_verified": True},
            "info_praktis": {
                "harga": "Rp 15.000",
                "jam_buka_weekday": "08:00 - 17:00",
                "jam_buka_weekend": "08:00 - 17:00",
                "estimasi_durasi": "90 menit",
                "koordinat": [-6.9, 107.6],
            },
            "alasan": "Cocok dengan intent alam.",
        }
    ],
}

pack = build_llm_evidence_pack(sample_response)
guard = build_llm_prompt_guard(pack)
candidate = pack["candidates"][0]

llm_output = {
    "schema_version": "muterbandung.llm_output.v1",
    "answer": "Rekomendasi ini disusun sesuai evidence pack.",
    "selected_destination_ids": [candidate["destination_id"]],
    "destination_summaries": [
        {
            "destination_id": candidate["destination_id"],
            "rank": candidate["rank"],
            "name": candidate["name"],
            "why": candidate["backend_reason"],
            "price": candidate["practical_info"]["price"],
            "opening_hours": candidate["practical_info"]["opening_hours"],
            "distance_label": candidate["practical_info"]["distance_label"],
            "media": candidate["media"],
            "limitations": candidate["limitations"],
        }
    ],
    "warnings": [],
    "follow_up_question": None,
}

print("prompt_guard_schema:", guard["schema_version"])
print("valid_output:", validate_llm_output(llm_output, pack)["valid"])

llm_output["destination_summaries"][0]["price"] = "Rp 999.000"
print("fake_price_rejected:", not validate_llm_output(llm_output, pack)["valid"])
"""

    notebook.cells.append(nbf.v4.new_markdown_cell(markdown))
    notebook.cells.append(nbf.v4.new_code_cell(code))

    with open(NOTEBOOK_PATH, "w", encoding="utf-8") as handle:
        nbf.write(notebook, handle)

    print(f"Updated {NOTEBOOK_PATH}")


if __name__ == "__main__":
    append_llm_guard_section()
