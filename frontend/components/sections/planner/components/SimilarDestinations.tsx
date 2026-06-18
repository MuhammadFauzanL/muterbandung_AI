"use client";

import { useEffect, useState } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { Compass as TravelIcon, Loader2 } from 'lucide-react';
import { usePlanner } from '@/context/PlannerContext';
import { destinationsService } from '@/services/destinations';
import { recommendationsService } from '@/services/recommendations';
import type { ExploreDestination } from '@/types';

export function SimilarDestinations() {
  const { destinations } = usePlanner();
  const [similar, setSimilar] = useState<ExploreDestination[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const selectedIds = destinations.map((d) => d.id);
  const dominantIntent = destinations[0]?.primaryIntent || destinations[0]?.category;

  useEffect(() => {
    let active = true;

    setLoading(true);
    setError(null);

    const fetchSimilar = dominantIntent
      ? destinationsService.getExplore({
          intent: dominantIntent,
          limit: 8,
          sort: 'quality',
        })
      : recommendationsService.getDestinations({ limit: 8 });

    fetchSimilar
      .then((res) => {
        if (!active) return;
        const filtered = res.data
          .filter((d) => !selectedIds.includes(d.id))
          .slice(0, 4);
        setSimilar(filtered);
      })
      .catch(() => {
        if (active) setError('Gagal memuat wisata serupa.');
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => { active = false; };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [dominantIntent, selectedIds.join(',')]);

  const sectionTitle = dominantIntent
    ? `Wisata ${dominantIntent} Lainnya`
    : 'Wisata yang Mungkin Kamu Sukai';

  return (
    <section>
      <div className="mb-3 flex items-center gap-2 text-[#202B37]">
        <span className="text-[#0E75BC]">
          <TravelIcon />
        </span>
        <h2 className="text-[16px] font-semibold leading-6">
          {sectionTitle}
        </h2>
      </div>

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
            Belum ada wisata serupa ditemukan. Coba pilih destinasi dari halaman Explore.
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
