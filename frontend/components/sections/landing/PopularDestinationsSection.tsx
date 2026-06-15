/**
 * Popular Destinations Section Component
 *
 * Displays a grid of popular tourist destinations in Bandung.
 * Uses DestinationCard for each destination item.
 */
import Image from 'next/image';
import Link from 'next/link';
import { POPULAR_DESTINATIONS } from '@/constants';
import type { Destination } from '@/types';

export function PopularDestinationsSection() {
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
            href="/explore"
            className="inline-flex items-center gap-1 sm:gap-2 text-[13px] sm:text-[18px] font-medium text-[#0E75BC] hover:text-[#095f99] shrink-0 bg-blue-50/50 px-2.5 py-1.5 rounded-full"
          >
            Lihat Semua
            <span className="text-sm sm:text-xl leading-none">→</span>
          </Link>
        </div>

        <div className="mt-3 sm:mt-8 grid gap-3 sm:gap-6 grid-cols-2 sm:grid-cols-2 lg:grid-cols-4 relative">
          {POPULAR_DESTINATIONS.map((destination) => (
            <PopularDestinationCard key={destination.title} {...destination} />
          ))}
          {/* Arrow button for carousel feel (just visual) */}
          <button className="absolute right-0 top-1/2 -translate-y-1/2 translate-x-1/2 flex h-10 w-10 items-center justify-center rounded-full bg-white shadow-lg border border-slate-100 text-[#14528E] hover:bg-slate-50 hidden lg:flex">
            <span className="text-xl leading-none font-bold">→</span>
          </button>
        </div>
      </div>
    </section>
  );
}

function PopularDestinationCard({
  title,
  location,
  rating,
  image,
}: Destination) {
  return (
    <article className="group relative h-[180px] sm:h-[320px] w-full overflow-hidden rounded-[16px] sm:rounded-2xl shadow-sm border border-slate-200 sm:border-0">
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
  );
}
