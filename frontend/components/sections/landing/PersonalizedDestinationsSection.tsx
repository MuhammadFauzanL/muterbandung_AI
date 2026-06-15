"use client";

import { useState } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { EXPLORE_DESTINATIONS } from '@/constants';
import { Heart } from 'lucide-react';
import type { ExploreDestination } from '@/types';

export function PersonalizedDestinationsSection() {
  return (
    <section id="foryou" className="bg-white pt-6 pb-6 sm:pt-10 sm:pb-10">
      <div className="mx-auto max-w-[1180px] px-5 sm:px-8">
        <div className="flex flex-col sm:flex-row sm:items-end justify-between mb-4 sm:mb-8 gap-2 sm:gap-4">
          <div>
            <h2 className="text-[22px] sm:text-[28px] font-semibold tracking-tight text-slate-950">
              Destinasi Untukmu
            </h2>
            <p className="text-[13px] sm:text-[14px] text-slate-500 mt-0.5 sm:mt-1">
              Ditemukan {EXPLORE_DESTINATIONS.length} tempat menarik sesuai kriteria.
            </p>
          </div>
        </div>

        <div className="flex overflow-x-auto snap-x snap-mandatory scroll-px-5 gap-4 sm:gap-6 pb-4 md:grid md:grid-cols-2 xl:grid-cols-3 hide-scrollbar -mx-5 px-5 sm:mx-0 sm:px-0">
          {EXPLORE_DESTINATIONS.map((dest) => (
            <div key={dest.id} className="snap-center shrink-0 w-[80vw] sm:w-auto">
              <PersonalizedCard destination={dest} />
            </div>
          ))}
          {/* Repeat some items to make it 6 as shown in screenshot if needed */}
          {EXPLORE_DESTINATIONS.slice(0, 2).map((dest) => (
            <div key={dest.id + '-copy'} className="snap-center shrink-0 w-[80vw] sm:w-auto">
              <PersonalizedCard destination={dest} />
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function PersonalizedCard({ destination }: { destination: ExploreDestination }) {
  const [isFavorited, setIsFavorited] = useState(false);

  return (
    <article className="h-full overflow-hidden rounded-[16px] sm:rounded-[20px] border border-[#D9E8F3] bg-white shadow-sm hover:shadow-md transition-shadow flex flex-col">
      <div className="relative h-[130px] sm:h-[184px] overflow-hidden shrink-0">
        <Image
          src={destination.image}
          alt={destination.title}
          fill
          sizes="(min-width: 1024px) 390px, (min-width: 640px) 50vw, 80vw"
          className="object-cover"
        />
        <div className="absolute left-2.5 top-2.5 sm:left-3 sm:top-3 rounded-full bg-white/95 px-2.5 py-0.5 sm:px-3 sm:py-1 text-[9px] sm:text-[11px] font-bold text-[#0E75BC] shadow-sm uppercase tracking-wider">
          {destination.category}
        </div>
        <button
          type="button"
          onClick={(e) => {
            e.preventDefault();
            setIsFavorited(!isFavorited);
          }}
          className={`absolute right-2.5 top-2.5 sm:right-3 sm:top-3 flex h-7 w-7 sm:h-8 sm:w-8 items-center justify-center rounded-full bg-white/95 shadow-sm transition-all duration-300 hover:scale-110 active:scale-95 ${
            isFavorited ? 'text-[#E54545]' : 'text-slate-400 hover:text-[#E54545]'
          }`}
        >
          <Heart className={`h-3.5 w-3.5 sm:h-4 sm:w-4 transition-all duration-300 ${isFavorited ? 'fill-[#E54545] scale-110' : 'fill-transparent'}`} />
        </button>
      </div>

      <div className="p-3.5 sm:p-4 sm:pt-5 flex flex-col flex-1">
        <div className="flex items-start justify-between gap-2">
          <h3 className="text-[14px] sm:text-[17px] font-bold leading-tight text-slate-900 line-clamp-2">
            {destination.title}
          </h3>
          <div className="flex items-center gap-0.5 sm:gap-1 text-[#E54545] shrink-0 pt-0.5">
            <svg className="w-3 h-3 sm:w-3.5 sm:h-3.5 fill-current" viewBox="0 0 24 24"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
            <span className="text-[11px] sm:text-[13px] font-bold">{destination.rating}</span>
          </div>
        </div>

        <div className="mt-2 sm:mt-3 flex items-center gap-3 sm:gap-4 text-[11px] sm:text-[13px] text-slate-500 font-medium">
          <span className="flex items-center gap-1 sm:gap-1.5"><svg className="w-3 h-3 sm:w-3.5 sm:h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 5v2m0 4v2m0 4v2M5 5a2 2 0 00-2 2v3a2 2 0 110 4v3a2 2 0 002 2h14a2 2 0 002-2v-3a2 2 0 110-4V7a2 2 0 00-2-2H5z"></path></svg>{destination.price}</span>
          <span className="flex items-center gap-1 sm:gap-1.5"><svg className="w-3 h-3 sm:w-3.5 sm:h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>{destination.duration}</span>
        </div>

        <div className="mt-auto pt-4 sm:mt-5 sm:pt-0 flex justify-end">
          <Link
            href={`/explore/${destination.id}`}
            className="rounded-full bg-[#E54545] px-5 py-1.5 sm:px-6 sm:py-2 text-[11px] sm:text-[13px] font-bold text-white transition-colors hover:bg-[#d43b3b] shadow-sm"
          >
            Lihat Detail
          </Link>
        </div>
      </div>
    </article>
  );
}
