import Image from 'next/image';
import Link from 'next/link';
import { EXPLORE_DESTINATIONS } from '@/constants';
import {
  GridIcon,
  HeartIcon,
  ListIcon,
  LocationIcon,
} from '@/components/ui/icons';
import type { ExploreDestination } from '@/types';

function DestinationCard({
  destination,
  eagerImage = false,
}: {
  destination: ExploreDestination;
  eagerImage?: boolean;
}) {
  return (
    <article className="overflow-hidden rounded-2xl border border-[#D9E8F3] bg-white shadow-[0_12px_28px_rgba(15,23,42,0.07)]">
      <div className="relative h-[184px] overflow-hidden">
        <Image
          src={destination.image}
          alt={destination.title}
          fill
          loading={eagerImage ? 'eager' : 'lazy'}
          sizes="(min-width: 1024px) 390px, (min-width: 640px) 50vw, 100vw"
          className="object-cover"
        />
        <div className="absolute left-3 top-3 rounded-full bg-white/92 px-3 py-1 text-xs font-semibold text-[#0E75BC] shadow-sm">
          {destination.category}
        </div>
        <button
          type="button"
          aria-label={`Simpan ${destination.title}`}
          className="absolute right-3 top-3 inline-flex h-9 w-9 items-center justify-center rounded-full bg-white/92 text-slate-500 shadow-sm transition-colors hover:text-[#E54545]"
        >
          <HeartIcon className="h-5 w-5" />
        </button>
      </div>

      <div className="p-4">
        <div className="flex items-center gap-1.5 text-xs font-medium text-[#0E75BC]">
          <LocationIcon className="h-3.5 w-3.5" />
          <span>{destination.location}</span>
        </div>

        <h3 className="mt-2 text-[19px] font-semibold leading-tight text-slate-900">
          {destination.title}
        </h3>

        <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-500">
          <span>{destination.duration}</span>
          <span>{destination.price}</span>
          <span className="font-semibold text-[#E54545]">
            +{destination.rating}
          </span>
        </div>

        <div className="mt-4 flex items-center justify-between">
          <Link
            href={`/explore/${destination.id}`}
            className="text-sm font-semibold text-[#0E75BC] hover:text-[#095f99]"
          >
            Lihat Detail
          </Link>
          <button
            type="button"
            className="rounded-full bg-[#FFEDEE] px-4 py-2 text-xs font-semibold text-[#E54545] transition-colors hover:bg-[#FFDCDD]"
          >
            Pilih Rencana
          </button>
        </div>
      </div>
    </article>
  );
}

export function DestinationGrid() {
  return (
    <section id="destinations" className="min-w-0">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-sm font-semibold text-[#0E75BC]">
            Ditemukan 12 tempat sesuai hasil rekomendasi
          </p>
          <h2 className="mt-1 text-[28px] font-semibold tracking-normal text-slate-950">
            Destinasi Untukmu
          </h2>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            aria-label="Tampilan grid"
            className="inline-flex h-10 w-10 items-center justify-center rounded-xl bg-[#0E75BC] text-white"
          >
            <GridIcon />
          </button>
          <button
            type="button"
            aria-label="Tampilan daftar"
            className="inline-flex h-10 w-10 items-center justify-center rounded-xl border border-[#D7E8F2] bg-white text-[#23689A] transition-colors hover:border-[#0E75BC]"
          >
            <ListIcon />
          </button>
        </div>
      </div>

      <div className="mt-5 grid gap-5 md:grid-cols-2">
        {EXPLORE_DESTINATIONS.map((destination, index) => (
          <DestinationCard
            key={destination.id}
            destination={destination}
            eagerImage={index === 0}
          />
        ))}
      </div>

      <div className="mt-7 flex items-center justify-center gap-2">
        {[1, 2, 3].map((page) => (
          <button
            key={page}
            type="button"
            className={`h-9 min-w-9 rounded-full text-sm font-semibold ${
              page === 1
                ? 'bg-[#0E75BC] text-white'
                : 'border border-[#D9E8F3] bg-white text-[#23689A]'
            }`}
          >
            {page}
          </button>
        ))}
      </div>
    </section>
  );
}
