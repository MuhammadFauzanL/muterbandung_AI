from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sys
import os
import json

# Add Scripts directory to path so we can import our engines
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Scripts')))

try:
    from hybrid_engine import HybridBehaviourEngine
    from recommender import MuterBandungRecommender
except ImportError as e:
    print(f"Error loading AI Modules: {e}")
    sys.exit(1)

app = Flask(__name__, static_folder='static')
CORS(app)

print("Initializing AI Engines... This might take a few seconds.")
hybrid_engine = HybridBehaviourEngine()
recommender = MuterBandungRecommender()
print("AI Engines Ready!")

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/predict_behaviour', methods=['POST'])
def predict_behaviour():
    data = request.json
    current_category = data.get('current_category', 'Penginapan')
    time_context = data.get('time_context', 'Pagi')
    user_persona = data.get('user_persona', 'Culture Learner')
    
    # TAHAP 1: Behaviour Engine
    hasil_hybrid_str = hybrid_engine.predict_next(
        current_category=current_category,
        time_context=time_context,
        user_persona=user_persona
    )
    hasil_hybrid = json.loads(hasil_hybrid_str)
    
    # Mengembalikan Top 3 Prediksi
    return jsonify({
        "predictions": hasil_hybrid['recommendations']
    })

@app.route('/api/semantic_search', methods=['POST'])
def semantic_search():
    data = request.json
    query = data.get('query', '')
    
    # TAHAP 2: Recommender Engine (Semantic Search)
    if not query.strip():
        return jsonify({"places": []})
        
    hasil_tempat = recommender.recommend(query=query, top_k=3)
    
    return jsonify({
        "places": hasil_tempat.get('recommendations', [])
    })

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
