import re
import sys
import codecs

with codecs.open(r'D:\File\file\Fauzan Lubada\PIJAK\Scripts\static\script.js', 'r', 'utf-8') as f:
    js = f.read()
orig_js = js

# 1. Add currentModule state
js = js.replace('let lastSearchPayload = {};', '''let lastSearchPayload = {};
    let currentModule = 'wisata';

    // Module Switcher Logic
    const moduleBtns = document.querySelectorAll('.module-btn');
    const wisataFilters = document.getElementById('wisata-filters');
    const penginapanFilters = document.getElementById('penginapan-filters');

    moduleBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            moduleBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            currentModule = btn.getAttribute('data-module');
            
            if (currentModule === 'penginapan') {
                wisataFilters.classList.add('hidden');
                penginapanFilters.classList.remove('hidden');
                queryInput.placeholder = "Cari penginapan... (Misal: apartemen murah dekat stasiun)";
            } else {
                wisataFilters.classList.remove('hidden');
                penginapanFilters.classList.add('hidden');
                queryInput.placeholder = "Ceritakan liburan impianmu... (Misal: wisata alam yang ramah anak)";
            }
            
            resultsContainer.innerHTML = `
                <div class="empty-state">
                    <div class="icon-wrapper">
                        <i class='bx ${currentModule === 'penginapan' ? 'bx-building-house' : 'bx-bot'}'></i>
                    </div>
                    <h3>AI ${currentModule === 'penginapan' ? 'Penginapan' : 'Recommender'} Siap</h3>
                    <p>Masukkan kata kunci atau atur filter di samping untuk menemukan ${currentModule === 'penginapan' ? 'penginapan' : 'destinasi wisata'} terbaik di Bandung Raya.</p>
                </div>
            `;
        });
    });''')

# 2. Update triggerSearch endpoint
js = js.replace("fetch('/api/recommend', {", "const endpoint = currentModule === 'penginapan' ? '/api/penginapan/recommend' : '/api/recommend';\n        fetch(endpoint, {")

# 3. Update gatherFormData
old_gather = '''        // Filter Form Data
        const formData = new FormData(filterForm);
        
        // Categories (multiple checkboxes)
        const categories = formData.getAll('categories');
        if (categories.length > 0) {
            payload.categories = categories;
        }

        // Other filters
        const maxPrice = formData.get('max_price');
        if (maxPrice) payload.max_price = parseInt(maxPrice);

        const minRating = formData.get('min_rating');
        if (minRating) payload.min_rating = parseFloat(minRating);

        payload.free_only = formData.get('free_only') === 'on';
        payload.open_now = formData.get('open_now') === 'on';

        const dayType = formData.get('day_type');
        if (dayType) payload.day_type = dayType;

        const openAtHour = formData.get('open_at_hour');
        if (openAtHour) payload.open_at_hour = openAtHour;'''

new_gather = '''        // Filter Form Data
        const formData = new FormData(filterForm);
        
        if (currentModule === 'penginapan') {
            const propertyTypes = formData.getAll('property_types');
            if (propertyTypes.length > 0) {
                payload.property_types = propertyTypes;
            }
        } else {
            const categories = formData.getAll('categories');
            if (categories.length > 0) {
                payload.categories = categories;
            }
            payload.free_only = formData.get('free_only') === 'on';
            payload.open_now = formData.get('open_now') === 'on';
            const dayType = formData.get('day_type');
            if (dayType) payload.day_type = dayType;
            const openAtHour = formData.get('open_at_hour');
            if (openAtHour) payload.open_at_hour = openAtHour;
        }

        const maxPrice = formData.get('max_price');
        if (maxPrice) payload.max_price = parseInt(maxPrice);

        const minRating = formData.get('min_rating');
        if (minRating) payload.min_rating = parseFloat(minRating);'''
js = js.replace(old_gather, new_gather)

# 4. Remove Oleh-oleh logic
js = js.replace("renderOlehOlehRecommendations(data, searchPayload);", "// renderOlehOlehRecommendations(data, searchPayload);")
js = js.replace("if (queryHasOlehOlehIntent(searchPayload.query || '')) {", "if (false && queryHasOlehOlehIntent(searchPayload.query || '')) {")

# 6. Fork Card Rendering
lines = js.split('\n')
new_lines = []
skip = False
for line in lines:
    if line.strip() == "let delay = 0;":
        new_lines.append(line)
        new_lines.append("        recommendations.forEach((item, index) => {")
        new_lines.append("            if (currentModule === 'penginapan') {")
        new_lines.append("                resultsContainer.appendChild(createPenginapanCard(item, index, delay));")
        new_lines.append("            } else {")
        new_lines.append("                resultsContainer.appendChild(createWisataCard(item, index, delay));")
        new_lines.append("            }")
        new_lines.append("            delay += 0.1;")
        new_lines.append("        });")
        skip = True
    elif line.strip() == "resultsContainer.appendChild(card);" and skip:
        skip = False
    elif line.strip() == "});" and skip:
        pass
    else:
        if not skip:
            new_lines.append(line)

js = "\n".join(new_lines)

card_logic_match = re.search(r"recommendations\.forEach\(\(item, index\) => \{\s*const card = document\.createElement\('div'\);\s*(.*?)\s*resultsContainer\.appendChild\(card\);\s*\}\);", orig_js, re.DOTALL)
wisata_card_logic = card_logic_match.group(1) if card_logic_match else ""

penginapan_card_logic = '''
            const bd = item.score_breakdown || {};
            let propClass = "hotel-badge";
            if(item.property_type === "apartment") propClass = "apartment-badge";
            if(item.property_type === "villa" || item.property_type === "vacation_rental") propClass = "villa-badge";
            
            const propTypeLabel = item.property_type ? item.property_type.replace('_', ' ').toUpperCase() : 'PENGINAPAN';
            
            const sentimentLabel = bd.sentiment_label || 'Netral';
            let sentClass = "sentiment-neutral";
            if(sentimentLabel.toLowerCase() === 'positif') sentClass = "sentiment-positive";
            if(sentimentLabel.toLowerCase() === 'negatif') sentClass = "sentiment-negative";
            
            const ratingHtml = bd.rating ? parseFloat(bd.rating).toFixed(1) + " / 5.0" : "Belum dirating";
            const priceHtml = item.price_lowest ? "Rp " + parseInt(item.price_lowest).toLocaleString("id-ID") : "Hubungi Pengelola";
            const distanceHtml = item.distance_label || "Jarak belum dihitung";
            const scorePercent = item.final_score ? parseFloat(item.final_score).toFixed(1) : '0.0';
            const locationName = escapeHtml(item.name || 'Penginapan tanpa nama');
            const explanation = escapeHtml(item.alasan || 'Sesuai dengan filter dan preferensi Anda.');
            
            card.innerHTML = `
                <div class="card-header">
                    <div class="card-title-group">
                        <h3>${index + 1}. ${locationName}</h3>
                        <div class="card-categories">
                            <span class="category-tag ${propClass}">${propTypeLabel}</span>
                        </div>
                    </div>
                    <div class="score-badge">
                        <span class="score-value">${scorePercent}%</span>
                        <span class="score-label">Kecocokan</span>
                    </div>
                </div>

                <div class="card-info-grid">
                    <div class="info-item">
                        <i class='bx bx-money'></i>
                        <div class="info-content">
                            <span class="info-label">Mulai Dari</span>
                            <span class="info-value">${priceHtml}</span>
                        </div>
                    </div>
                    <div class="info-item">
                        <i class='bx bx-star'></i>
                        <div class="info-content">
                            <span class="info-label">Google Rating</span>
                            <span class="info-value">${ratingHtml}</span>
                        </div>
                    </div>
                    <div class="info-item">
                        <i class='bx bx-smile'></i>
                        <div class="info-content">
                            <span class="info-label">Review Sentimen</span>
                            <span class="info-value ${sentClass}">${sentimentLabel}</span>
                        </div>
                    </div>
                    <div class="info-item">
                        <i class='bx bx-map-pin'></i>
                        <div class="info-content">
                            <span class="info-label">Jarak</span>
                            <span class="info-value">${distanceHtml}</span>
                        </div>
                    </div>
                </div>

                <div class="card-explanation">
                    <strong><i class='bx bx-bulb'></i> Mengapa direkomendasikan?</strong><br>
                    ${explanation}
                </div>
                
                <div class="score-breakdown">
                    <span title="Berdasarkan Filter Keras"><i class='bx bx-check-shield'></i> Lolos Filter</span>
                    ${bd.distance_score !== undefined ? `<span title="Skor Kedekatan"><i class='bx bx-map-pin'></i> Jarak: ${(bd.distance_score*100).toFixed(0)}%</span>` : ''}
                    ${bd.sentiment_score_adjusted !== undefined ? `<span title="Skor Sentimen"><i class='bx bx-smile'></i> Sent: ${(bd.sentiment_score_adjusted*100).toFixed(0)}%</span>` : ''}
                    ${bd.property_type_priority_score < 1.0 ? `<span title="Prioritas Diturunkan"><i class='bx bx-down-arrow-alt'></i> Penalti Tipe: ${(bd.property_type_priority_score*100).toFixed(0)}%</span>` : ''}
                </div>
            `;
'''

helpers = f'''
    function createWisataCard(item, index, delay) {{
        const card = document.createElement('div');
        card.className = 'result-card';
        card.style.animationDelay = `${{delay}}s`;
        {wisata_card_logic}
        return card;
    }}

    function createPenginapanCard(item, index, delay) {{
        const card = document.createElement('div');
        card.className = 'result-card';
        card.style.animationDelay = `${{delay}}s`;
        {penginapan_card_logic}
        return card;
    }}
'''

js = js.replace("function queryHasOlehOlehIntent", helpers + "\n    function queryHasOlehOlehIntent")

with codecs.open(r'D:\File\file\Fauzan Lubada\PIJAK\Scripts\static\script.js', 'w', 'utf-8') as f:
    f.write(js)
