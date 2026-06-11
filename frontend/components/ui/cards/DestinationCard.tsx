import Image from 'next/image';
import type { Destination } from '@/types';
import { LocationIcon, HeartIcon } from '@/components/ui/icons';
import { StarBadge } from '@/components/ui/badges';

export function DestinationCard({
  title,
  location,
  price,
  rating,
  image,
}: Destination) {
  return (
    <article className="overflow-hidden rounded-[18px] border border-[#C8E1F0] bg-white shadow-[0_5px_10px_rgba(15,23,42,0.08)]">
      <div className="relative aspect-[1.32/1] overflow-hidden">
        <Image
          src={image}
          alt={title}
          fill
          sizes="(min-width: 1280px) 370px, (min-width: 768px) 50vw, 100vw"
          className="object-cover"
        />
        <div className="absolute right-3 top-3">
          <StarBadge rating={rating} />
        </div>
      </div>

      <div className="space-y-2 px-4 pb-4 pt-3.5">
        <div className="flex items-center gap-1.5 text-[12px] font-medium text-[#0E75BC]">
          <LocationIcon />
          <span>{location}</span>
        </div>

        <h3 className="text-[19px] font-semibold leading-tight text-slate-900">
          {title}
        </h3>

        <div className="flex items-center justify-between pt-1">
          <span className="text-[16px] font-semibold text-slate-800">
            {price}
          </span>
          <button
            type="button"
            aria-label={`Simpan ${title}`}
            className="inline-flex h-9 w-9 items-center justify-center rounded-full transition-colors hover:bg-slate-100"
          >
            <HeartIcon />
          </button>
        </div>
      </div>
    </article>
  );
}
