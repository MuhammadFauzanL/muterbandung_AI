"use client";

import Image from 'next/image';
import Link from 'next/link';
import { EXPLORE_DESTINATIONS } from '@/constants';
import { Heart, LayoutGrid, List } from 'lucide-react';
import type { ExploreDestination } from '@/types';

export function PersonalizedDestinationsSection() {
  return (
    <section id="foryou" className="bg-white py-10 pb-16">
      <div className="mx-auto max-w-[1180px] px-5 sm:px-8">
        <div className="flex flex-col sm:flex-row sm:items-end justify-between mb-8 gap-4">
          <div>
            <h2 className="text-[28px] font-semibold tracking-tight text-slate-950">
              Destinasi Untukmu
            </h2>
            <p className="text-[14px] text-slate-500 mt-1">
              Ditemukan {EXPLORE_DESTINATIONS.length} tempat menarik sesuai kriteria.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button className="h-8 w-8 flex items-center justify-center rounded-md bg-[#0E75BC] text-white">
              <LayoutGrid className="h-4 w-4" />
            </button>
            <button className="h-8 w-8 flex items-center justify-center rounded-md border border-slate-200 text-slate-500 hover:bg-slate-50">
              <List className="h-4 w-4" />
            </button>
          </div>
        </div>

        <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
          {EXPLORE_DESTINATIONS.map((dest) => (
            <PersonalizedCard key={dest.id} destination={dest} />
          ))}
          {/* Repeat some items to make it 6 as shown in screenshot if needed */}
          {EXPLORE_DESTINATIONS.slice(0, 2).map((dest) => (
            <PersonalizedCard key={dest.id + '-copy'} destination={dest} />
          ))}
        </div>
      </div>
    </section>
  );
}

function PersonalizedCard({ destination }: { destination: ExploreDestination }) {
  return (
    <article className="overflow-hidden rounded-[20px] border border-[#D9E8F3] bg-white shadow-sm hover:shadow-md transition-shadow">
      <div className="relative h-[184px] overflow-hidden">
        <Image
          src={destination.image}
          alt={destination.title}
          fill
          sizes="(min-width: 1024px) 390px, (min-width: 640px) 50vw, 100vw"
          className="object-cover"
        />
        <div className="absolute left-3 top-3 rounded-full bg-white/95 px-3 py-1 text-[11px] font-bold text-[#0E75BC] shadow-sm uppercase tracking-wider">
          {destination.category}
        </div>
        <button
          type="button"
          className="absolute right-3 top-3 flex h-8 w-8 items-center justify-center rounded-full bg-white/95 text-slate-400 shadow-sm transition-colors hover:text-[#E54545]"
        >
          <Heart className="h-4 w-4" />
        </button>
      </div>

      <div className="p-4 pt-5">
        <div className="flex items-start justify-between gap-2">
          <h3 className="text-[17px] font-bold leading-tight text-slate-900">
            {destination.title}
          </h3>
          <div className="flex items-center gap-1 text-[#E54545] shrink-0 pt-0.5">
            <svg className="w-3.5 h-3.5 fill-current" viewBox="0 0 24 24"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
            <span className="text-[13px] font-bold">{destination.rating}</span>
          </div>
        </div>

        <div className="mt-3 flex items-center gap-4 text-[13px] text-slate-500 font-medium">
          <span className="flex items-center gap-1.5"><svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 5v2m0 4v2m0 4v2M5 5a2 2 0 00-2 2v3a2 2 0 110 4v3a2 2 0 002 2h14a2 2 0 002-2v-3a2 2 0 110-4V7a2 2 0 00-2-2H5z"></path></svg>{destination.price}</span>
          <span className="flex items-center gap-1.5"><svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>{destination.duration}</span>
        </div>

        <div className="mt-5 flex justify-end">
          <Link
            href={`/explore/${destination.id}`}
            className="rounded-full bg-[#E54545] px-6 py-2 text-[13px] font-bold text-white transition-colors hover:bg-[#d43b3b] shadow-sm"
          >
            Lihat Detail
          </Link>
        </div>
      </div>
    </article>
  );
}
