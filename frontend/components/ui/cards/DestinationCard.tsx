/**
 * Destination Card Component
 *
 * Displays a tourist destination with image, location, price, and rating.
 * Used in the Popular Destinations section of the landing page.
 */
import { SafeImage } from '@/components/ui/SafeImage';
import type { Destination } from '@/types';
import { StarBadge } from '@/components/ui/badges';
import { MapPin, Heart } from 'lucide-react';

export function DestinationCard({
  title,
  location,
  price,
  rating,
  image,
  category,
}: Destination) {
  return (
    <article className="overflow-hidden rounded-[18px] border border-[#C8E1F0] bg-white shadow-[0_5px_10px_rgba(15,23,42,0.08)]">
      <div className="relative aspect-[1.32/1] overflow-hidden">
        <SafeImage
          src={image}
          alt={title}
          fill
          sizes="(min-width: 1280px) 370px, (min-width: 768px) 50vw, 100vw"
          className="object-cover"
          category={category}
        />
        <div className="absolute right-3 top-3">
          <StarBadge rating={rating} />
        </div>
      </div>

      <div className="space-y-2 px-4 pb-4 pt-3.5">
        <div className="flex items-center gap-1.5 text-[12px] font-medium text-[#0E75BC]">
          <MapPin className="h-3.5 w-3.5" />
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
            <Heart className="h-5 w-5" />
          </button>
        </div>
      </div>
    </article>
  );
}
