"use client";

import { useEffect, useState, useCallback } from 'react';
import { MapPin as PinIcon, Loader2, Navigation } from 'lucide-react';
import { usePlanner } from '@/context/PlannerContext';
import { destinationsService } from '@/services/destinations';
import { DestinationRecommendationCard } from './DestinationRecommendationCard';
import type { PlannerDestination } from './DestinationRecommendationCard';
import type { ExploreDestination } from '@/types';

function mapToPlannerDestination(dest: ExploreDestination): PlannerDestination {
  return {
    title: dest.title,
    id: dest.id,
    slug: dest.slug,
    category: dest.category || dest.primaryIntent || 'Wisata',
    description: dest.scoreReason || `Destinasi ${dest.category || 'wisata'} di ${dest.location}`,
    distance: dest.distanceKm != null ? `${dest.distanceKm.toFixed(1)} km` : '',
    duration: dest.duration || 'Durasi fleksibel',
    price: dest.price || 'Harga belum tersedia',
    rating: dest.rating || '0.0',
    image: dest.image || '',
    latitude: dest.latitude,
    longitude: dest.longitude,
  };
}

export function RecommendationList() {
  const { destinations, userLat, userLng, setUserLocation } = usePlanner();
  const [nearbyDestinations, setNearbyDestinations] = useState<PlannerDestination[]>([]);
  const [loading, setLoading] = useState(true); // start true to show skeleton
  const [error, setError] = useState<string | null>(null);
  const [locationLoading, setLocationLoading] = useState(false);
  const [locationStatus, setLocationStatus] = useState<'idle' | 'granted' | 'denied'>('idle');

  const firstDest = destinations[0];
  const selectedIds = destinations.map((d) => d.id);
  const hasLocation = !!(userLat && userLng);

  // ── Request user location (called by inline button) ──
  const requestLocation = useCallback(() => {
    if (!navigator.geolocation) {
      setLocationStatus('denied');
      return;
    }

    setLocationLoading(true);
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords;
        setUserLocation(latitude, longitude);
        // Also persist to sessionStorage so Explore page can reuse
        window.sessionStorage.setItem(
          'muterbandung_location',
          JSON.stringify({ lat: latitude, lng: longitude }),
        );
        setLocationStatus('granted');
        setLocationLoading(false);
      },
      () => {
        setLocationStatus('denied');
        setLocationLoading(false);
      },
      { enableHighAccuracy: true, maximumAge: 300000, timeout: 10000 },
    );
  }, [setUserLocation]);

  // ── Fetch recommendations ──
  useEffect(() => {
    let active = true;

    queueMicrotask(() => {
      if (!active) return;
      setLoading(true);
      setError(null);
    });

    // Progressive Enhancement:
    // 1. hasLocation + firstDest → nearest + intent filter (BEST)
    // 2. hasLocation only       → nearest sort
    // 3. firstDest only         → filter by intent, quality sort
    // 4. nothing                → quality sort fallback (still shows data!)
    const params: Record<string, unknown> = {
      limit: 6,
      sort: hasLocation ? 'nearest' : 'quality',
    };

    if (hasLocation) {
      params.userLat = userLat;
      params.userLng = userLng;
      params.radiusKm = 15;
    }

    if (firstDest?.primaryIntent) {
      params.intent = firstDest.primaryIntent;
    }

    destinationsService
      .getExplore(params)
      .then((res) => {
        if (!active) return;
        const filtered = res.data
          .filter((d) => !selectedIds.includes(d.id))
          .slice(0, 4);
        setNearbyDestinations(filtered.map(mapToPlannerDestination));
      })
      .catch(() => {
        if (active) setError('Gagal memuat destinasi sekitar.');
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => { active = false; };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userLat, userLng, firstDest?.id, selectedIds.join(',')]);

  // Dynamic title based on context
  const sectionTitle = hasLocation
    ? 'Destinasi Terdekat dari Lokasimu'
    : firstDest
      ? `Rekomendasi Serupa dengan ${firstDest.title}`
      : 'Destinasi Rekomendasi Terbaik';

  return (
    <section>
      <div className="mb-3 flex items-center justify-between">
        <div className="flex items-center gap-2 text-[#202B37]">
          <PinIcon className="h-4 w-4 text-[#0E75BC]" />
          <h2 className="text-[16px] font-semibold leading-6">
            {sectionTitle}
          </h2>
        </div>

      </div>

      {/* Elegant location prompt banner */}
      {!hasLocation && locationStatus !== 'denied' && (
        <div className="mb-4 flex items-center justify-between rounded-xl border border-[#BFE8F0] bg-[#EAF8FB] p-3 sm:p-4 shadow-sm transition-all">
          <div className="flex items-center gap-3">
            <div className="hidden sm:flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-white text-[#0E75BC] shadow-[0_4px_12px_rgba(14,117,188,0.1)]">
              <Navigation className="h-5 w-5" />
            </div>
            <div>
              <p className="text-[13px] sm:text-[14px] font-bold text-[#0E75BC]">Cari di Sekitarmu</p>
              <p className="mt-0.5 text-[11px] sm:text-[12px] text-[#6A7E8E] leading-tight">
                Izinkan akses lokasi untuk rekomendasi terdekat yang lebih akurat.
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={requestLocation}
            disabled={locationLoading}
            className="shrink-0 ml-2 rounded-full bg-[#0E75BC] px-4 py-2 text-[12px] font-semibold text-white shadow-sm transition-colors hover:bg-[#095f99] disabled:opacity-70"
          >
            {locationLoading ? (
              <span className="flex items-center gap-2">
                <Loader2 className="h-3 w-3 animate-spin" />
                <span>Memproses...</span>
              </span>
            ) : (
              'Aktifkan'
            )}
          </button>
        </div>
      )}

      {loading && (
        <div className="space-y-3">
          {[0, 1].map((i) => (
            <div key={i} className="flex animate-pulse gap-3 rounded-xl border border-[#DDEAF2] bg-white p-3">
              <div className="h-[100px] w-[140px] shrink-0 rounded-lg bg-slate-200" />
              <div className="flex-1 space-y-2 py-2">
                <div className="h-4 w-3/4 rounded bg-slate-200" />
                <div className="h-3 w-1/2 rounded bg-slate-200" />
                <div className="h-3 w-full rounded bg-slate-200" />
              </div>
            </div>
          ))}
        </div>
      )}

      {error && (
        <div className="rounded-xl border border-red-100 bg-red-50 px-4 py-3 text-[13px] text-red-600">
          {error}
        </div>
      )}

      {!loading && !error && nearbyDestinations.length === 0 && (
        <div className="rounded-xl border border-dashed border-[#BFE8F0] bg-[#F6FCFE] px-4 py-6 text-center">
          <p className="text-[13px] text-[#6A7E8E]">
            Belum ada destinasi ditemukan. Coba perluas pencarian di halaman Explore.
          </p>
        </div>
      )}

      {!loading && !error && nearbyDestinations.length > 0 && (
        <div className="space-y-3">
          {nearbyDestinations.map((destination) => (
            <DestinationRecommendationCard
              key={destination.title}
              destination={destination}
            />
          ))}
        </div>
      )}
    </section>
  );
}
