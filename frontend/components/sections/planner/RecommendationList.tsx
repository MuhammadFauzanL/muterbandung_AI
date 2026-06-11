import Image from 'next/image';
import { NEARBY_DESTINATIONS } from '@/constants';
import {
  ClockIcon,
  MapPinIcon as PinIcon,
  WalletIcon,
} from '@/components/ui/icons';
import type { PlannerDestination } from '@/types';

function DestinationRecommendationCard({
  destination,
}: {
  destination: PlannerDestination;
}) {
  return (
    <article className="grid overflow-hidden rounded-[12px] border border-[#DDEAF2] bg-white shadow-[0_8px_22px_rgba(17,73,112,0.05)] sm:grid-cols-[178px_minmax(0,1fr)]">
      <div className="relative min-h-[150px] sm:min-h-0">
        <Image
          src={destination.image}
          alt={destination.title}
          fill
          sizes="(min-width: 640px) 178px, 100vw"
          className="object-cover"
        />
        <span className="absolute left-3 top-3 rounded-full bg-white/92 px-2.5 py-1 text-[11px] font-semibold text-[#176E9E] shadow-sm">
          +{destination.rating}
        </span>
      </div>

      <div className="min-w-0 px-4 py-3.5">
        <div className="flex items-start justify-between gap-3">
          <div>
            <span className="rounded-full bg-[#EAF6FC] px-3 py-1 text-[11px] font-semibold text-[#2882A9]">
              {destination.category}
            </span>
            <h3 className="mt-2 text-[16px] font-semibold leading-6 text-[#202B37]">
              {destination.title}
            </h3>
          </div>
          <span className="shrink-0 text-right text-[11px] font-semibold text-[#0E75BC]">
            {destination.distance}
          </span>
        </div>

        <p className="mt-1.5 text-[12px] leading-5 text-[#6A7E8E]">
          {destination.description}
        </p>

        <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-[11px] text-[#80909D]">
            <span className="inline-flex items-center gap-1">
              <ClockIcon />
              {destination.duration}
            </span>
            <span className="inline-flex items-center gap-1">
              <WalletIcon />
              {destination.price}
            </span>
          </div>
          <button
            type="button"
            className="inline-flex h-8 items-center justify-center rounded-[8px] bg-[#0E75BC] px-4 text-[11px] font-semibold text-white transition-colors hover:bg-[#095f99]"
          >
            + Tambahkan ke Perjalanan
          </button>
        </div>
      </div>
    </article>
  );
}

export function RecommendationList() {
  return (
    <section>
      <div className="mb-3 flex items-center gap-2 text-[#202B37]">
        <PinIcon className="h-4 w-4 text-[#0E75BC]" />
        <h2 className="text-[16px] font-semibold leading-6">
          Destinasi Sekitar yang Direkomendasikan
        </h2>
      </div>

      <div className="space-y-3">
        {NEARBY_DESTINATIONS.map((destination) => (
          <DestinationRecommendationCard
            key={destination.title}
            destination={destination}
          />
        ))}
      </div>
    </section>
  );
}
