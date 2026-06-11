import Image from 'next/image';
import { MapPinIcon, StarIcon } from '@/components/ui/icons';
import type { AccommodationOption } from '@/types';

export function AccommodationCard({
  accommodation,
  eagerImage = false,
}: {
  accommodation: AccommodationOption;
  eagerImage?: boolean;
}) {
  return (
    <article className="grid overflow-hidden rounded-[14px] border border-[#DDEAF2] bg-white shadow-[0_10px_26px_rgba(17,73,112,0.06)] md:grid-cols-[220px_minmax(0,1fr)]">
      <div className="relative min-h-[190px]">
        <Image
          src={accommodation.image}
          alt={accommodation.name}
          fill
          loading={eagerImage ? 'eager' : 'lazy'}
          sizes="(min-width: 768px) 220px, 100vw"
          className="object-cover"
        />
        <span className="absolute left-3 top-3 rounded-full bg-white/92 px-3 py-1 text-[11px] font-semibold text-[#176E9E] shadow-sm">
          {accommodation.type}
        </span>
      </div>

      <div className="min-w-0 p-4">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
          <div className="min-w-0">
            <h2 className="text-[17px] font-semibold leading-6 text-[#202B37]">
              {accommodation.name}
            </h2>
            <div className="mt-1.5 flex flex-wrap items-center gap-x-3 gap-y-1 text-[12px] text-[#6A7E8E]">
              <span className="inline-flex items-center gap-1">
                <MapPinIcon />
                {accommodation.location}
              </span>
              <span>{accommodation.distance}</span>
            </div>
          </div>

          <div className="shrink-0 rounded-[10px] bg-[#FFF7E8] px-3 py-2 text-[#7C4F00]">
            <div className="flex items-center gap-1 text-[12px] font-bold">
              <StarIcon className="h-4 w-4" size={16} />
              {accommodation.rating}
            </div>
            <p className="mt-0.5 text-[10px] font-semibold text-[#9B7840]">
              {accommodation.reviewCount}
            </p>
          </div>
        </div>

        <p className="mt-3 text-[13px] leading-6 text-[#607382]">
          {accommodation.description}
        </p>

        <div className="mt-4 flex flex-wrap gap-2">
          {accommodation.highlights.map((highlight) => (
            <span
              key={highlight}
              className="rounded-full bg-[#EEF7FD] px-3 py-1.5 text-[11px] font-semibold text-[#23689A]"
            >
              {highlight}
            </span>
          ))}
        </div>

        <div className="mt-5 flex flex-col gap-3 border-t border-[#EDF4F8] pt-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-[11px] font-medium text-[#80909D]">Mulai dari</p>
            <p className="text-[18px] font-bold text-[#202B37]">
              {accommodation.price}
              <span className="text-[11px] font-semibold text-[#7B8B99]">
                {' '}
                / malam
              </span>
            </p>
          </div>
          <button
            type="button"
            className="inline-flex h-10 items-center justify-center rounded-[10px] bg-[#0E75BC] px-5 text-[12px] font-semibold text-white transition-colors hover:bg-[#095f99]"
          >
            Pilih Penginapan
          </button>
        </div>
      </div>
    </article>
  );
}
