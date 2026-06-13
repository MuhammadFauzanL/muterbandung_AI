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
    <section id="explore" className="bg-[#F8FBFE] py-14 sm:py-16">
      <div className="mx-auto max-w-[1180px] px-5 sm:px-8">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <h2 className="text-[24px] sm:text-[28px] font-semibold tracking-normal text-slate-950">
              Destinasi Populer Bandung
            </h2>
            <p className="mt-1 text-[15px] sm:text-[18px] text-slate-600">
              Tempat populer wisatawan yang sering dikunjungi.
            </p>
          </div>

          <Link
            href="/explore"
            className="inline-flex items-center gap-2 self-start pt-1 text-[18px] font-medium text-[#0E75BC] hover:text-[#095f99]"
          >
            Lihat Semua
            <span className="text-xl leading-none">→</span>
          </Link>
        </div>

        <div className="mt-8 grid gap-4 sm:gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 relative">
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
    <article className="group relative h-[320px] w-full overflow-hidden rounded-2xl">
      <Image
        src={image}
        alt={title}
        fill
        sizes="(min-width: 1024px) 25vw, (min-width: 640px) 50vw, 100vw"
        className="object-cover transition-transform duration-500 group-hover:scale-105"
      />
      <div className="absolute inset-0 bg-[linear-gradient(180deg,transparent_40%,rgba(15,23,42,0.85)_100%)]" />

      <div className="absolute inset-x-0 bottom-0 p-5 text-white">
        <div className="flex items-center gap-1.5 mb-1.5">
          <span className="inline-flex items-center justify-center rounded bg-red-600 px-1.5 py-0.5 text-[10px] font-bold text-white shadow-sm">
            ★ {rating}
          </span>
          <span className="text-[11px] font-medium text-white/90">
            {location}
          </span>
        </div>
        <h3 className="text-[16px] font-bold leading-tight">{title}</h3>
      </div>
    </article>
  );
}
