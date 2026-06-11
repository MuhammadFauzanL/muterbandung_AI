// STAGE 1: Minta Prediksi dari Hybrid Engine
document.getElementById('context-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const current_category = document.getElementById('current_category').value;
    const time_context = document.getElementById('time_context').value;
    const user_persona = document.getElementById('user_persona').value;

    const loadingPredict = document.getElementById('loading-predict');
    const predictionSection = document.getElementById('prediction-section');
    const chipsContainer = document.getElementById('chips-container');
    const resultSection = document.getElementById('result-section');

    // Reset UI
    resultSection.classList.add('hidden');
    predictionSection.classList.add('hidden');
    loadingPredict.classList.remove('hidden');

    try {
        const response = await fetch('/api/predict_behaviour', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ current_category, time_context, user_persona })
        });
        
        if (!response.ok) throw new Error("Gagal load prediksi");
        
        const data = await response.json();
        
        // Render Chips
        chipsContainer.innerHTML = '';
        data.predictions.forEach((pred, index) => {
            const chip = document.createElement('div');
            chip.className = 'chip-btn';
            
            // Icon simple mapping
            const iconMap = {
                "Kuliner": "🍽️", "Belanja": "🛍️", "Alam": "🌳", 
                "Hiburan": "🎉", "Santai/Healing": "☕", "Spot Foto": "📸",
                "Religi": "🕌", "Sejarah": "🏛️"
            };
            const icon = iconMap[pred.category] || "📍";
            
            chip.innerHTML = `
                <div class="chip-header">
                    <span>${icon} ${pred.category}</span>
                    <span>${(pred.score * 100).toFixed(0)}% Match</span>
                </div>
                <div class="chip-reason">${pred.reason}</div>
            `;
            
            // Kalau chip diklik, jalankan Semantic Search!
            chip.addEventListener('click', () => {
                // Set text search query to the category and trigger search
                document.getElementById('search_query').value = pred.category;
                triggerSemanticSearch(pred.category, user_persona);
            });
            
            chipsContainer.appendChild(chip);
        });

        loadingPredict.classList.add('hidden');
        predictionSection.classList.remove('hidden');
        predictionSection.scrollIntoView({ behavior: 'smooth' });

    } catch (error) {
        alert("Error: " + error.message);
        loadingPredict.classList.add('hidden');
    }
});

// STAGE 2: Semantic Search (Manual form submit)
document.getElementById('search-form').addEventListener('submit', (e) => {
    e.preventDefault();
    const query = document.getElementById('search_query').value;
    const user_persona = document.getElementById('user_persona').value;
    triggerSemanticSearch(query, user_persona);
});

async function triggerSemanticSearch(query, user_persona) {
    const loadingSearch = document.getElementById('loading-search');
    const resultSection = document.getElementById('result-section');
    const placesContainer = document.getElementById('places-container');

    resultSection.classList.add('hidden');
    loadingSearch.classList.remove('hidden');
    
    // Inject persona context (Opsional, agar mirip RAG)
    const persona_keywords = {
        "Nature Seeker": "alam tenang",
        "Urban Casual": "kota nongkrong",
        "Culture Learner": "sejarah budaya"
    };
    const finalQuery = `${query} ${persona_keywords[user_persona] || ""}`;

    try {
        const response = await fetch('/api/semantic_search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: finalQuery })
        });
        
        if (!response.ok) throw new Error("Gagal mencari tempat");
        const data = await response.json();
        
        placesContainer.innerHTML = '';
        data.places.forEach(place => {
            const similarityPercent = (place.score_breakdown.similarity * 100).toFixed(1);
            const card = document.createElement('div');
            card.className = 'place-card';
            card.innerHTML = `
                <div class="card-header">
                    <div class="place-name">${place.location_name}</div>
                    <div class="match-badge">${similarityPercent}% Cocok</div>
                </div>
                <div class="place-category">${place.category} • ${place.subcategory || 'Umum'}</div>
                <div class="place-sentiment">
                    <span>⭐ Sentimen: ${place.score_breakdown.sentiment_score.toFixed(2)}</span>
                </div>
                <div class="place-reason">
                    ${place.explanation || 'Rekomendasi terbaik berdasarkan profil Anda.'}
                </div>
            `;
            placesContainer.appendChild(card);
        });

        loadingSearch.classList.add('hidden');
        resultSection.classList.remove('hidden');
        resultSection.scrollIntoView({ behavior: 'smooth' });

    } catch (error) {
        alert("Error: " + error.message);
        loadingSearch.classList.add('hidden');
    }
}
