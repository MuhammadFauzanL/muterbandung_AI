"use client";

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { SafeImage } from '@/components/ui/SafeImage';
import { Heart, MapPin, ArrowLeft } from 'lucide-react';
import { useFavorite } from '@/context/FavoriteContext';
import { destinationsService } from '@/services/destinations';
import type { Destination } from '@/types';

export function PopularPageContent() {
  const [destinations, setDestinations] = useState<Destination[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const { isFavorite, toggleFavorite } = useFavorite();
  const itemsPerPage = 12;

  useEffect(() => {
    async function fetchAllPopular() {
      try {
        // Fetch a larger limit, e.g. 50
        const data = await destinationsService.getPopular(50);
        setDestinations(data);
      } catch (error) {
        console.error("Gagal mengambil destinasi populer:", error);
      } finally {
        setIsLoading(false);
      }
    }
    fetchAllPopular();
  }, []);

  const totalPages = Math.ceil(destinations.length / itemsPerPage);
  const paginatedDestinations = destinations.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <main className="mx-auto max-w-[1180px] w-full px-4 py-8 sm:px-8 sm:py-12">
      <div className="mb-8">
        <Link 
          href="/" 
          className="inline-flex items-center gap-2 text-sm font-semibold text-[#0E75BC] hover:text-[#095f99] mb-4 transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          Kembali ke Beranda
        </Link>
        <h1 className="text-3xl sm:text-4xl font-bold text-[#112F43] tracking-tight">
          Destinasi Populer di Bandung
        </h1>
        <p className="mt-2 text-slate-500 text-sm sm:text-base max-w-2xl">
          Jelajahi tempat-tempat wisata yang paling sering dikunjungi dan menjadi favorit wisatawan di Bandung.
        </p>
      </div>

      {isLoading ? (
        <div className="grid gap-4 sm:gap-6 grid-cols-2 sm:grid-cols-3 lg:grid-cols-4">
          {Array.from({ length: 8 }).map((_, idx) => (
            <div key={idx} className="h-[240px] sm:h-[320px] w-full rounded-[16px] sm:rounded-2xl bg-slate-200 animate-pulse border border-slate-200/50"></div>
          ))}
        </div>
      ) : (
        <>
          <div className="grid gap-4 sm:gap-6 grid-cols-2 sm:grid-cols-3 lg:grid-cols-4">
            {paginatedDestinations.map((destination) => (
              <Link key={destination.id || destination.title} href={`/explore/${destination.slug || ''}`} className="block group">
                <article className="relative h-[240px] sm:h-[320px] w-full overflow-hidden rounded-[16px] sm:rounded-2xl shadow-sm border border-slate-200 sm:border-0">
                <SafeImage
                  src={destination.image}
                  alt={destination.title}
                  fill
                  sizes="(min-width: 1024px) 25vw, (min-width: 640px) 33vw, 50vw"
                  className="object-cover transition-transform duration-500 group-hover:scale-105"
                  category={destination.category}
                />
                <div className="absolute inset-0 bg-[linear-gradient(180deg,transparent_30%,rgba(15,23,42,0.85)_100%)]" />

                <button
                  type="button"
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    toggleFavorite(String(destination.id || ''));
                  }}
                  className={`absolute top-2 right-2 sm:top-3 sm:right-3 z-10 inline-flex h-7 w-7 sm:h-8 sm:w-8 items-center justify-center rounded-full bg-white/90 shadow-sm backdrop-blur-sm transition-colors ${isFavorite(String(destination.id || '')) ? 'text-[#E54545]' : 'text-slate-400 hover:text-[#E54545]'}`}
                >
                  <Heart className={`h-3.5 w-3.5 sm:h-4 sm:w-4 ${isFavorite(String(destination.id || '')) ? 'fill-current' : ''}`} />
                </button>

                <div className="absolute inset-x-0 bottom-0 p-3 sm:p-5 text-white">
                  <div className="flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-1.5 mb-1 sm:mb-1.5">
                    <span className="inline-flex w-fit items-center justify-center rounded bg-red-600 px-1 sm:px-1.5 py-[2px] sm:py-0.5 text-[10px] font-bold text-white shadow-sm">
                      ★ {destination.rating}
                    </span>
                    <span className="text-[10px] sm:text-[11px] font-medium text-white/90 line-clamp-1 flex items-center gap-1">
                      <MapPin className="h-2.5 w-2.5" />
                      {destination.location}
                    </span>
                  </div>
                  <h3 className="text-[13px] sm:text-[16px] font-bold leading-tight line-clamp-2">{destination.title}</h3>
                </div>
              </article>
            </Link>
            ))}
          </div>

          {/* Pagination Controls */}
          {totalPages > 1 && (
            <div className="mt-10 flex items-center justify-center gap-2">
              <button
                onClick={() => handlePageChange(currentPage - 1)}
                disabled={currentPage === 1}
                className="h-9 px-4 rounded-full text-sm font-semibold border border-[#D9E8F3] bg-white text-[#23689A] hover:bg-[#F3F8FC] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Prev
              </button>
              
              {Array.from({ length: totalPages }).map((_, idx) => {
                const page = idx + 1;
                return (
                  <button
                    key={page}
                    onClick={() => handlePageChange(page)}
                    className={`h-9 min-w-9 rounded-full text-sm font-semibold transition-colors ${
                      page === currentPage
                        ? 'bg-[#0E75BC] text-white shadow-md'
                        : 'border border-[#D9E8F3] bg-white text-[#23689A] hover:bg-[#F3F8FC]'
                    }`}
                  >
                    {page}
                  </button>
                );
              })}

              <button
                onClick={() => handlePageChange(currentPage + 1)}
                disabled={currentPage === totalPages}
                className="h-9 px-4 rounded-full text-sm font-semibold border border-[#D9E8F3] bg-white text-[#23689A] hover:bg-[#F3F8FC] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </main>
  );
}
