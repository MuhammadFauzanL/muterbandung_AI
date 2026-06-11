document.addEventListener('DOMContentLoaded', () => {
    const searchForm = document.getElementById('search-form');
    const filterForm = document.getElementById('filter-form');
    const resultsContainer = document.getElementById('results-container');
    const loadingState = document.getElementById('loading-state');
    const suggestionTags = document.querySelectorAll('.suggestion-tag');
    const queryInput = document.getElementById('query');
    const useLocationBtn = document.getElementById('use-location-btn');
    const locationStatus = document.getElementById('location-status');
    let userLocation = { lat: null, lon: null };
    let lastSearchPayload = {};
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
    });

    function escapeHtml(value) {
        return String(value ?? '').replace(/[&<>"']/g, (char) => ({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;'
        }[char]));
    }

    // Handle suggestion tags
    suggestionTags.forEach(tag => {
        tag.addEventListener('click', () => {
            queryInput.value = tag.getAttribute('data-query');
            triggerSearch();
        });
    });

    // Handle Search Form Submission
    searchForm.addEventListener('submit', (e) => {
        e.preventDefault();
        triggerSearch();
    });

    // Handle Filter Form Submission
    filterForm.addEventListener('submit', (e) => {
        e.preventDefault();
        triggerSearch();
    });

    // Cross-Recommend: Wisata -> Penginapan Terdekat
    resultsContainer.addEventListener('click', (e) => {
        const btn = e.target.closest('.btn-cross-recommend');
        if (!btn) return;

        const lat = parseFloat(btn.dataset.lat);
        const lon = parseFloat(btn.dataset.lon);
        const wisataName = btn.dataset.name;

        // Switch module to Penginapan
        currentModule = 'penginapan';
        moduleBtns.forEach(b => b.classList.remove('active'));
        document.querySelector('[data-module="penginapan"]').classList.add('active');
        wisataFilters.classList.add('hidden');
        penginapanFilters.classList.remove('hidden');

        // Set query and coordinates
        queryInput.value = `Penginapan dekat ${wisataName}`;
        queryInput.placeholder = "Cari penginapan... (Misal: apartemen murah dekat stasiun)";
        userLocation = { lat, lon };
        updateLocationStatus(`Lokasi wisata: ${wisataName} (${lat.toFixed(4)}, ${lon.toFixed(4)})`, true);

        // Set radius to 15km (adaptive for mountain areas)
        const maxDistInput = document.getElementById('max_distance_km');
        if (maxDistInput) maxDistInput.value = '15';

        // Trigger search
        triggerSearch();
    });

    if (useLocationBtn) {
        useLocationBtn.addEventListener('click', () => {
            if (!navigator.geolocation) {
                updateLocationStatus('Browser tidak mendukung lokasi.', false);
                return;
            }

            useLocationBtn.disabled = true;
            updateLocationStatus('Mengambil lokasi...', true);
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    userLocation = {
                        lat: position.coords.latitude,
                        lon: position.coords.longitude
                    };
                    updateLocationStatus(
                        `Lokasi aktif (${userLocation.lat.toFixed(4)}, ${userLocation.lon.toFixed(4)})`,
                        true
                    );
                    useLocationBtn.disabled = false;
                    triggerSearch();
                },
                (error) => {
                    userLocation = { lat: null, lon: null };
                    updateLocationStatus(error.message || 'Izin lokasi ditolak.', false);
                    useLocationBtn.disabled = false;
                },
                {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 300000
                }
            );
        });
    }

    function updateLocationStatus(message, active) {
        if (!locationStatus) return;
        if (active) {
            locationStatus.innerHTML = `${escapeHtml(message)} <span id="clear-location-btn" style="cursor:pointer; color: #dc2626; margin-left: 8px; font-weight: bold; background: rgba(220, 38, 38, 0.1); padding: 2px 6px; border-radius: 4px;" title="Hapus Lokasi">✖</span>`;
            const clearBtn = document.getElementById('clear-location-btn');
            if (clearBtn) {
                clearBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    userLocation = { lat: null, lon: null };
                    updateLocationStatus('Lokasi belum aktif', false);
                    const maxDistInput = document.getElementById('max_distance_km');
                    if (maxDistInput) maxDistInput.value = '';
                    if (useLocationBtn) useLocationBtn.disabled = false;
                    triggerSearch();
                });
            }
        } else {
            locationStatus.textContent = message;
        }
        locationStatus.classList.toggle('active', Boolean(active));
    }

    function triggerSearch() {
        // Show Loading
        resultsContainer.innerHTML = '';
        loadingState.classList.remove('hidden');

        // Gather Data
        const payload = gatherFormData();
        lastSearchPayload = payload;

        // Fetch API
        const endpoint = currentModule === 'penginapan' ? '/api/penginapan/recommend' : '/api/recommend';
        fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        })
        .then(response => response.json())
        .then(data => {
            loadingState.classList.add('hidden');
            renderResults(data, payload);
        })
        .catch(error => {
            loadingState.classList.add('hidden');
            console.error('Error fetching recommendations:', error);
            renderError('Terjadi kesalahan saat menghubungi server AI. Pastikan backend Flask berjalan.');
        });
    }

    function gatherFormData() {
        const payload = {};
        
        // Query
        payload.query = queryInput.value.trim();

        // Filter Form Data
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
        if (minRating) payload.min_rating = parseFloat(minRating);

        const sortBy = formData.get('sort_by');
        payload.sort_by = sortBy || 'balanced';

        const maxDistanceKm = formData.get('max_distance_km');
        if (maxDistanceKm) payload.max_distance_km = parseFloat(maxDistanceKm);

        if (userLocation.lat !== null && userLocation.lon !== null) {
            payload.user_lat = userLocation.lat;
            payload.user_lon = userLocation.lon;
        }

        return payload;
    }

    function renderResults(data, searchPayload = {}) {
        if (!data) {
            renderError('Tidak ada data yang diterima dari server.');
            return;
        }

        const locationContext = data.location_context || {};
        const recommendations = data.recommendations || [];

        if (recommendations.length === 0) {
            const emptyIcon = currentModule === 'penginapan' ? 'bx-building-house' : 'bx-search-alt';
            const emptyTitle = currentModule === 'penginapan' ? 'Tidak ada penginapan ditemukan' : 'Tidak ada hasil';
            const emptyMsg = currentModule === 'penginapan'
                ? 'Tidak ditemukan penginapan yang cocok. Coba perluas radius pencarian atau ubah filter tipe properti.'
                : 'AI tidak menemukan destinasi yang cocok dengan kriteria Anda. Coba ubah filter atau gunakan kata kunci yang berbeda.';
            resultsContainer.innerHTML = `
                <div class="empty-state">
                    <div class="icon-wrapper"><i class='bx ${emptyIcon}'></i></div>
                    <h3>${emptyTitle}</h3>
                    <p>${emptyMsg}</p>
                </div>`;
            return;
        }

        if (locationContext.enabled) {
            const locationBadge = document.createElement('div');
            locationBadge.className = 'location-context-badge';
            const radiusText = locationContext.max_distance_km
                ? `radius ${parseFloat(locationContext.max_distance_km).toFixed(1)} km`
                : 'tanpa batas radius';
            locationBadge.innerHTML = `
                <i class='bx bx-current-location'></i>
                <span>Ranking ${escapeHtml(locationContext.sort_by || 'balanced')} memakai lokasi Anda, ${escapeHtml(radiusText)}.</span>
            `;
            resultsContainer.appendChild(locationBadge);
        }

        // Clear container first
        resultsContainer.innerHTML = '';

        // Render AI Intent Detection Badge if detected
        const aiBadge = data.ai_badge || {};
        const aiIntents = data.ai_intents || {};
        const activeIntents = Array.isArray(aiBadge.active_intents)
            ? aiBadge.active_intents
            : (Array.isArray(aiIntents.active_intents) ? aiIntents.active_intents : []);
        const intentScores = aiIntents.scores || {};

        if ((aiBadge.enabled || aiIntents.enabled) && activeIntents.length > 0) {
            const intentBadge = document.createElement('div');
            intentBadge.className = 'ai-intent-badge';
            const statusText = (data.fallback && data.fallback.used)
                ? 'filter AI dilonggarkan agar hasil tidak kosong'
                : 'diterapkan sebagai filter otomatis';
            
            // Generate intent tags with their scores
            const intentTagsHtml = activeIntents.map(intent => {
                const score = intentScores[intent];
                const scorePct = score ? Math.round(score * 100) + '%' : '';
                return `<span class="intent-tag">${escapeHtml(intent)} ${scorePct ? `(${escapeHtml(scorePct)})` : ''}</span>`;
            }).join('');

            intentBadge.innerHTML = `
                <div class="intent-icon"><i class='bx bxs-magic-wand'></i></div>
                <div class="intent-text">
                    <strong>${escapeHtml(aiBadge.label || 'Pencarian Cerdas AI')}:</strong> Preferensi Anda terdeteksi: 
                    <span class="intent-tags">
                        ${intentTagsHtml}
                    </span>
                    <span class="intent-status">(${escapeHtml(statusText)})</span>
                </div>
            `;
            resultsContainer.appendChild(intentBadge);
        }

        // AI Summary Bubble
        if (data.ai_summary) {
            const summaryDiv = document.createElement('div');
            summaryDiv.className = 'ai-summary-bubble';
            summaryDiv.innerHTML = `
                <div class="ai-avatar"><i class='bx bx-bot'></i></div>
                <div class="ai-text">
                    <strong>Asisten MuterBandung</strong>
                    <p>${escapeHtml(data.ai_summary)}</p>
                </div>
            `;
            resultsContainer.appendChild(summaryDiv);
        }

        let delay = 0;
        recommendations.forEach((item, index) => {
            if (currentModule === 'penginapan') {
                resultsContainer.appendChild(createPenginapanCard(item, index, delay));
            } else {
                resultsContainer.appendChild(createWisataCard(item, index, delay));
            }
            delay += 0.1;
        });

        // renderOlehOlehRecommendations(data, searchPayload);
    }

    
    function createWisataCard(item, index, delay) {
        const card = document.createElement('div');
        card.className = 'result-card';
        card.style.animationDelay = `${delay}s`;
        card.className = 'result-card';
            card.style.animationDelay = `${delay}s`;
            delay += 0.1;

            // Categories rendering (using item.category or item.multi_labels)
            let catHtml = '';
            if (item.category) {
                catHtml += `<span class="category-tag" style="background: rgba(99, 102, 241, 0.2); border: 1px solid var(--primary-color); color: white;">${escapeHtml(item.category)}</span>`;
            }
            if (item.multi_labels && Array.isArray(item.multi_labels)) {
                item.multi_labels.slice(0, 3).forEach(c => {
                    const label = String(c || '').trim();
                    if (label) {
                        catHtml += `<span class="category-tag">${escapeHtml(label)}</span>`;
                    }
                });
            }

            // Price Formatting
            const info = item.info_praktis || {};
            const priceHtml = escapeHtml(info.harga || 'Tidak ada info');

            // Rating Formatting
            const bd = item.score_breakdown || {};
            const ratingHtml = bd.google_rating ? `${parseFloat(bd.google_rating).toFixed(1)} / 5.0` : 'Belum dirating';
            const sentimentScore = bd.adjusted_sentiment_score !== undefined && bd.adjusted_sentiment_score !== null
                ? bd.adjusted_sentiment_score
                : bd.sentiment_score;
            const sentimentAvailable = bd.sentiment_available !== false;
            const sentimentSource = bd.sentiment_model_source ? escapeHtml(bd.sentiment_model_source) : 'Tidak tersedia';
            const reviewConfidenceLabel = bd.review_confidence_label ? escapeHtml(bd.review_confidence_label.replaceAll('_', ' ')) : '';
            const sentimentHtml = sentimentScore !== undefined && sentimentScore !== null
                ? (sentimentAvailable
                    ? `<span title="Skor Sentimen Terkalibrasi (${sentimentSource}${reviewConfidenceLabel ? `, ${reviewConfidenceLabel}` : ''})"><i class='bx bx-smile'></i> Sentimen: ${(parseFloat(sentimentScore)*100).toFixed(0)}%</span>`
                    : `<span title="Skor Sentimen belum tersedia"><i class='bx bx-smile'></i> Sentimen: N/A</span>`)
                : '';
            
            // Score Formatting
            const scorePercent = item.final_score ? parseFloat(item.final_score).toFixed(1) : '0.0';

            // Opening Hours
            const jamBuka = escapeHtml(info.jam_buka_weekday || 'Tidak ada info');
            const locationName = escapeHtml(item.location_name || 'Destinasi tanpa nama');
            const explanation = escapeHtml(item.alasan || 'Sesuai dengan filter dan preferensi Anda.');
            const duration = escapeHtml(info.estimasi_durasi || '-');
            const distanceLabel = item.distance_label ? escapeHtml(item.distance_label) : 'Jarak belum dihitung';
            const koordinat = Array.isArray(info.koordinat) ? info.koordinat : [];
            const media = item.media || {};
            const hasMedia = media.available === true;
            const mediaImageUrl = hasMedia && media.image_url ? escapeHtml(media.image_url) : '';
            const mediaLinks = [];
            if (hasMedia && media.destination_url) {
                mediaLinks.push(`<a class="media-link" href="${escapeHtml(media.destination_url)}" target="_blank" rel="noopener noreferrer"><i class='bx bx-map'></i> Maps</a>`);
            }
            if (hasMedia && media.website) {
                mediaLinks.push(`<a class="media-link" href="${escapeHtml(media.website)}" target="_blank" rel="noopener noreferrer"><i class='bx bx-link-external'></i> Website</a>`);
            }
            const mediaHtml = hasMedia ? `
                <div class="card-media">
                    ${mediaImageUrl ? `
                        <div class="card-media-visual">
                            <img src="${mediaImageUrl}" alt="${locationName}" loading="lazy" referrerpolicy="no-referrer" onerror="this.closest('.card-media-visual').classList.add('hidden')">
                        </div>
                    ` : ''}
                    ${mediaLinks.length ? `<div class="card-media-links">${mediaLinks.join('')}</div>` : ''}
                </div>
            ` : '';

            // HTML Structure
            card.innerHTML = `
                ${mediaHtml}
                <div class="card-header">
                    <div class="card-title-group">
                        <h3>${escapeHtml(item.rank || index + 1)}. ${locationName}</h3>
                        <div class="card-categories">
                            ${catHtml}
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
                            <span class="info-label">Harga Tiket</span>
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
                        <i class='bx bx-time-five'></i>
                        <div class="info-content">
                            <span class="info-label">Jam Operasional (Weekday)</span>
                            <span class="info-value">${jamBuka}</span>
                        </div>
                    </div>
                    <div class="info-item">
                        <i class='bx bx-stopwatch'></i>
                        <div class="info-content">
                            <span class="info-label">Estimasi Durasi</span>
                            <span class="info-value">${duration}</span>
                        </div>
                    </div>
                    <div class="info-item">
                        <i class='bx bx-map-pin'></i>
                        <div class="info-content">
                            <span class="info-label">Jarak</span>
                            <span class="info-value">${distanceLabel}</span>
                        </div>
                    </div>
                </div>

                <div class="card-explanation">
                    <strong><i class='bx bx-bulb'></i> Mengapa AI merekomendasikan ini?</strong><br>
                    ${explanation}
                </div>
                
                <div class="score-breakdown">
                    <span title="Berdasarkan Filter Keras"><i class='bx bx-check-shield'></i> Lolos Filter</span>
                    ${bd.similarity !== undefined ? `<span title="Skor Teks Natural"><i class='bx bx-text'></i> Teks: ${(bd.similarity*100).toFixed(0)}%</span>` : ''}
                    ${sentimentHtml}
                    ${bd.review_confidence !== undefined ? `<span title="Confidence Review berbasis p95"><i class='bx bx-bar-chart-alt-2'></i> Conf: ${(bd.review_confidence*100).toFixed(0)}%</span>` : ''}
                    ${bd.distance_score !== undefined && bd.distance_score !== null ? `<span title="Skor Kedekatan"><i class='bx bx-map-pin'></i> Jarak: ${(bd.distance_score*100).toFixed(0)}%</span>` : ''}
                </div>

                ${koordinat.length === 2 ? `
                <div class="cross-recommend-section">
                    <button class="btn-secondary btn-cross-recommend" type="button"
                            data-lat="${koordinat[0]}" data-lon="${koordinat[1]}" data-name="${locationName}">
                        <i class='bx bx-building-house'></i> Cari Penginapan Terdekat
                    </button>
                </div>
                ` : ''}
            `;
        return card;
    }

    function createPenginapanCard(item, index, delay) {
        const card = document.createElement('div');
        card.className = 'result-card';
        card.style.animationDelay = `${delay}s`;

        const bd = item.score_breakdown || {};
        let propClass = "hotel-badge";
        if (item.property_type === "apartment") propClass = "apartment-badge";
        if (item.property_type === "villa" || item.property_type === "vacation_rental") propClass = "villa-badge";

        const propTypeLabel = item.property_type ? item.property_type.replace('_', ' ').toUpperCase() : 'PENGINAPAN';

        // Fix: use item.hotel_adjusted_sentiment_label (actual field from penginapan_recommender.py)
        const sentimentLabel = item.hotel_adjusted_sentiment_label || 'Netral';
        let sentClass = "sentiment-neutral";
        if (sentimentLabel.toLowerCase().includes('positif')) sentClass = "sentiment-positive";
        if (sentimentLabel.toLowerCase().includes('negatif')) sentClass = "sentiment-negative";

        // Fix: use item.overall_rating (actual field from penginapan_recommender.py)
        const ratingHtml = item.overall_rating ? parseFloat(item.overall_rating).toFixed(1) + " / 5.0" : "Belum dirating";
        const priceHtml = item.price_lowest ? "Rp " + parseInt(item.price_lowest).toLocaleString("id-ID") : "Hubungi Pengelola";
        const distanceHtml = item.distance_label || "Jarak belum dihitung";
        const scorePercent = item.final_score ? parseFloat(item.final_score).toFixed(1) : '0.0';
        const locationName = escapeHtml(item.name || 'Penginapan tanpa nama');
        // Fix: use item.note (actual field from penginapan_recommender.py)
        const explanation = escapeHtml(item.note || 'Sesuai dengan filter dan preferensi Anda.');
        const reviewCount = item.reviews || 0;
        const imageUrl = item.primary_image_url ? escapeHtml(item.primary_image_url) : '';
        const mapLink = item.link ? escapeHtml(item.link) : '';

        card.innerHTML = `
            ${imageUrl ? `
            <div class="card-media">
                <div class="card-media-visual">
                    <img src="${imageUrl}" alt="${locationName}" loading="lazy" referrerpolicy="no-referrer" onerror="this.closest('.card-media-visual').classList.add('hidden')">
                </div>
                ${mapLink ? `<div class="card-media-links"><a class="media-link" href="${mapLink}" target="_blank" rel="noopener noreferrer"><i class='bx bx-map'></i> Lihat di Maps</a></div>` : ''}
            </div>
            ` : ''}
            <div class="card-header">
                <div class="card-title-group">
                    <h3>${item.rank || index + 1}. ${locationName}</h3>
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
                        <span class="info-value ${sentClass}">${sentimentLabel} (${reviewCount} ulasan)</span>
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
                ${bd.sentiment_score !== undefined ? `<span title="Skor Sentimen"><i class='bx bx-smile'></i> Sent: ${(bd.sentiment_score*100).toFixed(0)}%</span>` : ''}
                ${bd.property_type_priority_score < 1.0 ? `<span title="Prioritas Diturunkan"><i class='bx bx-down-arrow-alt'></i> Penalti Tipe: ${(bd.property_type_priority_score*100).toFixed(0)}%</span>` : ''}
            </div>
        `;

        return card;
    }

    function queryHasOlehOlehIntent(query) {
        return /\b(oleh-oleh|oleh oleh|buah tangan|souvenir|suvenir|snack|camilan|cemilan|keripik|bolu|brownies|donat|tahu susu|susu murni|kurma|kaos)\b/i.test(query || '');
    }

    function getAnchorLocation(recommendations) {
        if (userLocation.lat !== null && userLocation.lon !== null) {
            return {
                lat: userLocation.lat,
                lon: userLocation.lon,
                label: 'lokasi Anda'
            };
        }

        const top = recommendations && recommendations.length ? recommendations[0] : null;
        const coords = top && top.info_praktis && Array.isArray(top.info_praktis.koordinat)
            ? top.info_praktis.koordinat
            : [];
        if (coords.length >= 2 && Number.isFinite(parseFloat(coords[0])) && Number.isFinite(parseFloat(coords[1]))) {
            return {
                lat: parseFloat(coords[0]),
                lon: parseFloat(coords[1]),
                label: top.location_name || 'destinasi teratas'
            };
        }
        return null;
    }

    function buildOlehOlehPayload(wisataData, searchPayload) {
        const recommendations = wisataData.recommendations || [];
        const anchor = getAnchorLocation(recommendations);
        const query = searchPayload.query || '';
        const payload = {
            query: queryHasOlehOlehIntent(query) ? query : 'oleh-oleh Bandung',
            top_k: 5,
            sort_by: anchor ? 'nearest' : 'balanced'
        };
        if (anchor) {
            payload.user_lat = anchor.lat;
            payload.user_lon = anchor.lon;
            payload.max_distance_km = 15;
            payload.anchor_label = anchor.label;
        }
        return { payload, anchor };
    }

    function renderOlehOlehRecommendations(wisataData, searchPayload) {
        const recommendations = wisataData.recommendations || [];
        const hasOlehOlehIntent = queryHasOlehOlehIntent(searchPayload.query || '');
        if (!recommendations.length && !hasOlehOlehIntent) return;

        const { payload, anchor } = buildOlehOlehPayload(wisataData, searchPayload);
        const section = document.createElement('section');
        section.className = 'oleh-oleh-section';
        section.innerHTML = `
            <div class="oleh-oleh-header">
                <div>
                    <h3><i class='bx bx-shopping-bag'></i> Oleh-Oleh Pendukung</h3>
                    <p>${anchor ? `Dekat ${escapeHtml(anchor.label)}` : 'Pilihan umum Bandung Raya'}</p>
                </div>
                <span class="oleh-oleh-pill">harga estimasi</span>
            </div>
            <div class="oleh-oleh-loading">
                <div class="mini-spinner"></div>
                <span>Mengambil rekomendasi oleh-oleh...</span>
            </div>
        `;
        resultsContainer.appendChild(section);

        fetch('/api/oleh-oleh/recommend', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        })
        .then(response => response.json())
        .then(data => {
            if (!data || data.status === 'error') {
                section.remove();
                return;
            }
            renderOlehOlehSection(section, data, anchor);
        })
        .catch(error => {
            console.error('Error fetching oleh-oleh recommendations:', error);
            section.remove();
        });
    }

    function renderOlehOlehSection(section, data, anchor) {
        const items = data.recommendations || [];
        if (!items.length) {
            section.remove();
            return;
        }
        const cardsHtml = items.slice(0, 5).map(item => {
            const score = item.score !== undefined && item.score !== null ? parseFloat(item.score).toFixed(1) : '0.0';
            const warnings = Array.isArray(item.warnings) ? item.warnings : [];
            const warningHtml = warnings.length ? `<span class="oleh-warning">${escapeHtml(warnings[0].replaceAll('_', ' '))}</span>` : '';
            const price = item.price_range || 'Harga belum tersedia';
            const durability = item.daya_tahan_produk || item.daya_tahan_produk_class || 'Daya tahan belum tersedia';
            const product = item.produk_utama || item.category_label || 'Produk belum tersedia';
            const distance = item.distance_label || 'Jarak belum dihitung';
            const mapsLink = item.url ? `<a href="${escapeHtml(item.url)}" target="_blank" rel="noopener noreferrer"><i class='bx bx-map'></i> Maps</a>` : '';
            const websiteLink = item.website ? `<a href="${escapeHtml(item.website)}" target="_blank" rel="noopener noreferrer"><i class='bx bx-link-external'></i> Website</a>` : '';
            return `
                <article class="oleh-card">
                    ${item.image_url ? `<img src="${escapeHtml(item.image_url)}" alt="${escapeHtml(item.name)}" loading="lazy" referrerpolicy="no-referrer" onerror="this.classList.add('hidden')">` : ''}
                    <div class="oleh-card-body">
                        <div class="oleh-card-title">
                            <h4>${escapeHtml(item.rank)}. ${escapeHtml(item.name)}</h4>
                            <span>${score}%</span>
                        </div>
                        <p>${escapeHtml(product)}</p>
                        <div class="oleh-meta">
                            <span><i class='bx bx-purchase-tag-alt'></i> ${escapeHtml(price)}</span>
                            <span><i class='bx bx-time'></i> ${escapeHtml(durability)}</span>
                            <span><i class='bx bx-map-pin'></i> ${escapeHtml(distance)}</span>
                        </div>
                        <div class="oleh-links">
                            ${mapsLink}
                            ${websiteLink}
                            ${warningHtml}
                        </div>
                    </div>
                </article>
            `;
        }).join('');

        section.innerHTML = `
            <div class="oleh-oleh-header">
                <div>
                    <h3><i class='bx bx-shopping-bag'></i> Oleh-Oleh Pendukung</h3>
                    <p>${anchor ? `Dekat ${escapeHtml(anchor.label)}` : 'Pilihan umum Bandung Raya'}</p>
                </div>
                <span class="oleh-oleh-pill">harga estimasi</span>
            </div>
            <div class="oleh-grid">
                ${cardsHtml}
            </div>
        `;
    }

    function renderError(message) {
        resultsContainer.innerHTML = `
            <div class="empty-state">
                <div class="icon-wrapper" style="background: rgba(239, 68, 68, 0.1);">
                    <i class='bx bx-error-circle' style="color: #ef4444;"></i>
                </div>
                <h3>Pencarian Gagal</h3>
                <p>${escapeHtml(message)}</p>
            </div>
        `;
    }
});
