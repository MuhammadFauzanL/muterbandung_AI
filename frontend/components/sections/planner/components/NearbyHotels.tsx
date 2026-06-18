"use client";

import { useEffect, useState } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { Building as BuildingIcon, Loader2 } from 'lucide-react';
import { usePlanner } from '@/context/PlannerContext';
import { accommodationsService } from '@/services/accommodations';
import type { Accommodation } from '@/types';

export function NearbyHotels() {
  const { destinations } = usePlanner();
  const [hotels, setHotels] = useState<Accommodation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const firstDest = destinations[0];

  useEffect(() => {
    let active = true;

    setLoading(true);
    setError(null);

    if (firstDest?.slug) {
      // If destination is selected → get accommodations near that destination
      accommodationsService
        .getNearbyForDestination(firstDest.slug, { limit: 3, sort: 'recommended' })
        .then((res) => {
          if (active) setHotels(res.data);
        })
        .catch(() => {
          if (active) setError('Gagal memuat penginapan terdekat.');
        })
        .finally(() => {
          if (active) setLoading(false);
        });
    } else {
      // Fallback: show popular/recommended accommodations
      accommodationsService
        .getAll({ limit: 3, sort: 'recommended' })
        .then((res) => {
          if (active) setHotels(res.data);
        })
        .catch(() => {
          if (active) setError('Gagal memuat penginapan.');
        })
        .finally(() => {
          if (active) setLoading(false);
        });
    }

    return () => { active = false; };
  }, [firstDest?.slug]);

  const sectionTitle = firstDest
    ? `Penginapan Dekat ${firstDest.title}`
    : 'Penginapan Rekomendasi';

  return (
    <section>
      <div className="mb-3 flex items-center gap-2 text-[#202B37]">
        <span className="text-[#0E75BC]">
          <BuildingIcon />
        </span>
        <h2 className="text-[16px] font-semibold leading-6">
          {sectionTitle}
        </h2>
      </div>

      {loading && (
        <div className="space-y-3">
          {[0, 1].map((i) => (
            <div key={i} className="flex animate-pulse gap-4 rounded-[12px] border border-[#DDEAF2] bg-white p-3">
              <div className="h-[100px] w-[140px] shrink-0 rounded-[8px] bg-slate-200" />
              <div className="flex-1 space-y-2 py-2">
                <div className="h-4 w-3/4 rounded bg-slate-200" />
                <div className="h-3 w-1/2 rounded bg-slate-200" />
                <div className="h-4 w-1/3 rounded bg-slate-200" />
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

      {!loading && !error && hotels.length === 0 && (
        <div className="rounded-xl border border-dashed border-[#BFE8F0] bg-[#F6FCFE] px-4 py-6 text-center">
          <p className="text-[13px] text-[#6A7E8E]">
            Belum ada penginapan ditemukan. Coba lihat opsi di halaman penginapan.
          </p>
        </div>
      )}

      {!loading && !error && hotels.length > 0 && (
        <div className="space-y-3">
          {hotels.map((hotel) => (
            <article key={hotel.id} className="flex gap-4 rounded-[12px] border border-[#DDEAF2] bg-white p-3 shadow-[0_8px_22px_rgba(17,73,112,0.05)]">
              <div className="relative h-[100px] w-[140px] shrink-0 overflow-hidden rounded-[8px] bg-slate-100">
                {hotel.image ? (
                  <Image src={hotel.image} alt={hotel.name} fill className="object-cover" sizes="140px" />
                ) : (
                  <div className="flex h-full w-full items-center justify-center text-[10px] text-slate-400">
                    <BuildingIcon className="h-6 w-6 text-slate-300" />
                  </div>
                )}
              </div>
              <div className="flex min-w-0 flex-1 flex-col justify-between py-1">
                <div>
                  <h3 className="text-[14px] font-semibold text-[#202B37] truncate">{hotel.name}</h3>
                  <p className="text-[12px] text-[#6A7E8E] truncate">{hotel.distance || hotel.location}</p>
                </div>
                <div className="flex items-center justify-between mt-2">
                  <div>
                    <p className="text-[10px] text-[#80909D]">Mulai dari</p>
                    <p className="text-[14px] font-bold text-[#0E75BC]">{hotel.price}</p>
                  </div>
                  <Link
                    href={firstDest?.slug ? `/planner/penginapan?destination=${firstDest.slug}` : '/planner/penginapan'}
                    className="rounded-[8px] bg-[#EAF6FC] px-3 py-1.5 text-[11px] font-semibold text-[#0E75BC] transition-colors hover:bg-[#DDEAF2]"
                  >
                    Lihat Detail
                  </Link>
                </div>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
