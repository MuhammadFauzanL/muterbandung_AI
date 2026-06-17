"use client";

/**
 * Popular Destinations Section Component
 *
 * Displays a grid of popular tourist destinations in Bandung.
 * Uses DestinationCard for each destination item.
 */
import { useState, useEffect, useRef } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { destinationsService } from '@/services/destinations';
import type { Destination } from '@/types';

export function PopularDestinationsSection() {
  const [destinations, setDestinations] = useState<Destination[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const scrollRef = useRef<HTMLDivElement>(null);
  const [scroll, setScroll] = useState({ start: true, end: false });

  const handleScroll = () => {
    if (scrollRef.current) {
      const { scrollLeft, scrollWidth, clientWidth } = scrollRef.current;
      setScroll({
        start: scrollLeft <= 10,
        end: Math.ceil(scrollLeft + clientWidth) >= scrollWidth - 5
      });
    }
  };

  useEffect(() => {
    handleScroll();
  }, [destinations]);

  useEffect(() => {
    async function fetchPopular() {
      try {
        const data = await destinationsService.getPopular(10);
        setDestinations(data);
      } catch (error) {
        console.error("Gagal mengambil destinasi populer:", error);
      } finally {
        setIsLoading(false);
      }
    }
    fetchPopular();
  }, []);

  return (
    <section id="explore" className="bg-[#F8FBFE] py-6 sm:py-10">
      <div className="mx-auto max-w-[1180px] px-4 sm:px-8">
        <div className="flex flex-row items-center justify-between gap-2 mb-4 sm:mb-5">
          <div>
            <h2 className="text-[18px] sm:text-[28px] font-semibold tracking-normal text-slate-950">
              Destinasi Populer
            </h2>
            <p className="mt-0 sm:mt-1 text-[12px] sm:text-[18px] text-slate-600">
              Sering dikunjungi wisatawan.
            </p>
          </div>

          <Link
            href="/popular"
            className="inline-flex items-center gap-1 sm:gap-2 text-[13px] sm:text-[18px] font-medium text-[#0E75BC] hover:text-[#095f99] shrink-0 bg-blue-50/50 px-2.5 py-1.5 rounded-full transition-colors"
          >
            Lihat Semua
            <span className="text-sm sm:text-xl leading-none">→</span>
          </Link>
        </div>

        <div className="relative mt-3 sm:mt-8 -mx-4 sm:mx-0">
          <div 
            ref={scrollRef}
            onScroll={handleScroll}
            className="flex overflow-x-auto snap-x snap-mandatory gap-3 sm:gap-6 pb-4 px-4 sm:px-0 [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none]"
          >
            {isLoading ? (
              // Skeleton Loading
              Array.from({ length: 4 }).map((_, idx) => (
                <div key={idx} className="h-[180px] sm:h-[320px] w-[240px] sm:w-[320px] shrink-0 snap-center rounded-[16px] sm:rounded-2xl bg-slate-200 animate-pulse border border-slate-200/50"></div>
              ))
            ) : (
              destinations.map((destination) => (
                <PopularDestinationCard key={destination.id || destination.title} {...destination} />
              ))
            )}
          </div>

          {/* Custom Arrows like Login Form */}
          {!scroll.start && (
            <div className="absolute left-0 top-0 bottom-4 flex w-12 items-center justify-start pointer-events-none bg-gradient-to-r from-[#F8FBFE] to-transparent pl-1 sm:pl-0">
              <div className="flex h-8 w-8 sm:h-10 sm:w-10 items-center justify-center rounded-full bg-white/90 shadow-md backdrop-blur-sm -ml-2 sm:-ml-5">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#0E75BC" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="animate-pulse"><path d="M15 18l-6-6 6-6"/></svg>
              </div>
            </div>
          )}
          {!scroll.end && destinations.length > 0 && (
            <div className="absolute right-0 top-0 bottom-4 flex w-12 items-center justify-end pointer-events-none bg-gradient-to-l from-[#F8FBFE] to-transparent pr-1 sm:pr-0">
              <div className="flex h-8 w-8 sm:h-10 sm:w-10 items-center justify-center rounded-full bg-white/90 shadow-md backdrop-blur-sm -mr-2 sm:-mr-5">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#0E75BC" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="animate-pulse"><path d="M9 18l6-6-6-6"/></svg>
              </div>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}

function PopularDestinationCard({
  slug,
  title,
  location,
  rating,
  image,
}: Destination) {
  return (
    <Link href={`/explore/${slug || ''}`} className="block shrink-0 snap-center group">
      <article className="relative h-[180px] sm:h-[320px] w-[240px] sm:w-[320px] overflow-hidden rounded-[16px] sm:rounded-2xl shadow-sm border border-slate-200 sm:border-0 cursor-pointer">
        <Image
        src={image}
        alt={title}
        fill
        sizes="(min-width: 1024px) 25vw, (min-width: 640px) 50vw, 50vw"
        className="object-cover transition-transform duration-500 group-hover:scale-105"
      />
      <div className="absolute inset-0 bg-[linear-gradient(180deg,transparent_30%,rgba(15,23,42,0.85)_100%)]" />

      <div className="absolute inset-x-0 bottom-0 p-3 sm:p-5 text-white">
        <div className="flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-1.5 mb-1 sm:mb-1.5">
          <span className="inline-flex w-fit items-center justify-center rounded bg-red-600 px-1 sm:px-1.5 py-[2px] sm:py-0.5 text-[8px] sm:text-[10px] font-bold text-white shadow-sm">
            ★ {rating}
          </span>
          <span className="text-[9px] sm:text-[11px] font-medium text-white/90 line-clamp-1">
            {location}
          </span>
        </div>
        <h3 className="text-[12px] sm:text-[16px] font-bold leading-tight line-clamp-2">{title}</h3>
      </div>
    </article>
    </Link>
  );
}
