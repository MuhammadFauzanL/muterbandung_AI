"use client";

import { useEffect, useState } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { Compass as TravelIcon, Sparkles } from 'lucide-react';
import { usePlanner } from '@/context/PlannerContext';
import { destinationsService } from '@/services/destinations';
import { recommendationsService } from '@/services/recommendations';
import type { ExploreDestination } from '@/types';

type FallbackSource = 'intent' | 'category' | 'ai' | 'popular';

export function SimilarDestinations() {
  const { destinations } = usePlanner();
  const [similar, setSimilar] = useState<ExploreDestination[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [source, setSource] = useState<FallbackSource>('popular');

  const selectedIds = destinations.map((d) => d.id);
  const firstDest = destinations[0];
  const primaryIntent = firstDest?.primaryIntent;
  const category = firstDest?.category;

  useEffect(() => {
    let active = true;

    setLoading(true);
    setError(null);

    /**
     * Cascading Fallback Strategy:
     * 1. If primaryIntent exists → search by intent (same "vibe")
     * 2. If category exists → search by category (same type)
     * 3. If user is logged in → AI personal recommendations
     * 4. Final fallback → popular destinations
     *
     * At each level, if results (after filtering duplicates) are < 2,
     * we fall through to the next level and merge results.
     */
    async function fetchWithFallback() {
      const MAX_CARDS = 4;
      const MIN_ACCEPTABLE = 2;
      let results: ExploreDestination[] = [];
      let activeSource: FallbackSource = 'popular';

      // ── Level 1: Same Intent ──
      if (primaryIntent) {
        try {
          const res = await destinationsService.getExplore({
            intent: primaryIntent,
            limit: 12,
            sort: 'quality',
          });
          const filtered = res.data.filter((d) => !selectedIds.includes(d.id));
          if (filtered.length > 0) {
            results = filtered.slice(0, MAX_CARDS);
            activeSource = 'intent';
          }
        } catch {
          // silently fall through
        }
      }

      // ── Level 2: Same Category (if intent gave < MIN results) ──
      if (results.length < MIN_ACCEPTABLE && category) {
        try {
          const res = await destinationsService.getExplore({
            category: category,
            limit: 12,
            sort: 'quality',
          });
          const existingIds = new Set([...selectedIds, ...results.map((r) => r.id)]);
          const filtered = res.data.filter((d) => !existingIds.has(d.id));
          if (filtered.length > 0) {
            results = [...results, ...filtered].slice(0, MAX_CARDS);
            if (activeSource === 'popular') activeSource = 'category';
          }
        } catch {
          // silently fall through
        }
      }

      // ── Level 3: AI Personal Recommendation ──
      if (results.length < MIN_ACCEPTABLE) {
        try {
          const res = await recommendationsService.getDestinations({
            limit: 12,
            requireAuth: true,
          });
          const existingIds = new Set([...selectedIds, ...results.map((r) => r.id)]);
          const filtered = res.data.filter((d) => !existingIds.has(d.id));
          if (filtered.length > 0) {
            results = [...results, ...filtered].slice(0, MAX_CARDS);
            if (activeSource === 'popular') activeSource = 'ai';
          }
        } catch {
          // silently fall through
        }
      }

      // ── Level 4: Popular Destinations (final fallback) ──
      if (results.length < MIN_ACCEPTABLE) {
        try {
          const res = await destinationsService.getExplore({
            limit: 12,
            sort: 'popular',
          });
          const existingIds = new Set([...selectedIds, ...results.map((r) => r.id)]);
          const filtered = res.data.filter((d) => !existingIds.has(d.id));
          results = [...results, ...filtered].slice(0, MAX_CARDS);
          if (activeSource === 'popular') activeSource = 'popular';
        } catch {
          // silently fall through
        }
      }

      if (!active) return;

      setSimilar(results);
      setSource(activeSource);
    }

    fetchWithFallback()
      .catch(() => {
        if (active) setError('Gagal memuat wisata serupa.');
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => { active = false; };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [primaryIntent, category, selectedIds.join(',')]);

  // Dynamic section title based on source
  const sectionTitle = (() => {
    if (source === 'intent' && primaryIntent) return `Wisata ${primaryIntent} Lainnya`;
    if (source === 'category' && category) return `${category} Lainnya`;
    if (source === 'ai') return 'Rekomendasi AI Untukmu';
    return 'Wisata Populer Lainnya';
  })();

  const sourceLabel = (() => {
    if (source === 'intent') return 'Berdasarkan jenis wisata yang sama';
    if (source === 'category') return 'Berdasarkan kategori serupa';
    if (source === 'ai') return 'Dipilihkan Cepot AI khusus untukmu';
    return 'Wisata populer di Bandung';
  })();

  return (
    <section>
      <div className="mb-1 flex items-center gap-2 text-[#202B37]">
        <span className="text-[#0E75BC]">
          {source === 'ai' ? <Sparkles /> : <TravelIcon />}
        </span>
        <h2 className="text-[16px] font-semibold leading-6">
          {sectionTitle}
        </h2>
      </div>
      <p className="mb-3 text-[11px] text-[#7B8B99]">{sourceLabel}</p>

      {loading && (
        <div className="grid gap-3 sm:gap-4 grid-cols-2">
          {[0, 1].map((i) => (
            <div key={i} className="animate-pulse overflow-hidden rounded-[12px] border border-[#DDEAF2] bg-white">
              <div className="h-[90px] sm:h-[154px] bg-slate-200" />
              <div className="space-y-2 px-3 py-3">
                <div className="h-4 w-3/4 rounded bg-slate-200" />
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

      {!loading && !error && similar.length === 0 && (
        <div className="rounded-xl border border-dashed border-[#BFE8F0] bg-[#F6FCFE] px-4 py-6 text-center">
          <p className="text-[13px] text-[#6A7E8E]">
            Belum ada wisata serupa ditemukan. Coba pilih destinasi dari halaman{' '}
            <Link href="/explore" className="font-semibold text-[#0E75BC] underline">Explore</Link>.
          </p>
        </div>
      )}

      {!loading && !error && similar.length > 0 && (
        <div className="grid gap-3 sm:gap-4 grid-cols-2 sm:grid-cols-2">
          {similar.map((destination, index) => (
            <Link
              key={destination.id}
              href={`/explore/${destination.slug || destination.id}`}
              className="group overflow-hidden rounded-[12px] border border-[#DDEAF2] bg-white shadow-[0_8px_22px_rgba(17,73,112,0.05)] transition-shadow hover:shadow-[0_12px_32px_rgba(17,73,112,0.1)]"
            >
              <div className="relative h-[90px] sm:h-[154px] overflow-hidden">
                {destination.image ? (
                  <Image
                    src={destination.image}
                    alt={destination.title}
                    fill
                    loading={index === 0 ? 'eager' : 'lazy'}
                    sizes="(min-width: 640px) 50vw, 50vw"
                    className="object-cover transition-transform duration-500 group-hover:scale-105"
                  />
                ) : (
                  <div className="flex h-full w-full items-center justify-center bg-slate-100 text-[10px] text-slate-400">
                    No Image
                  </div>
                )}
                <div className="absolute left-2 top-2 rounded-full bg-white/90 px-2 py-0.5 text-[9px] font-semibold text-[#0E75BC] shadow-sm backdrop-blur-sm">
                  {destination.primaryIntent || destination.category}
                </div>
              </div>
              <div className="px-2.5 py-2 sm:px-4 sm:py-3">
                <h3 className="text-[11px] sm:text-[14px] font-semibold text-[#202B37] line-clamp-1">
                  {destination.title}
                </h3>
                <p className="mt-0.5 sm:mt-1 text-[9px] sm:text-[12px] leading-snug sm:leading-5 text-[#6A7E8E] line-clamp-2">
                  ★ {destination.rating} · {destination.price}
                </p>
              </div>
            </Link>
          ))}
        </div>
      )}
    </section>
  );
}
