"use client";

import Image from 'next/image';
import { usePlanner } from '@/context/PlannerContext';
import { useToast } from '@/context/ToastContext';
import { Clock as ClockIcon, Wallet as WalletIcon } from 'lucide-react';

export type PlannerDestination = {
  title: string;
  id?: string;
  slug?: string;
  category: string;
  description: string;
  distance: string;
  duration: string;
  price: string;
  rating: string;
  image: string;
  latitude?: number;
  longitude?: number;
};

export function DestinationRecommendationCard({
  destination,
}: {
  destination: PlannerDestination;
}) {
  const { addDestination } = usePlanner();
  const { showToast } = useToast();

  return (
    <article className="grid overflow-hidden rounded-xl border border-[#DDEAF2] bg-white shadow-[0_8px_22px_rgba(17,73,112,0.05)] grid-cols-[110px_minmax(0,1fr)] sm:grid-cols-[178px_minmax(0,1fr)]">
      <div className="relative h-[110px] sm:h-auto sm:min-h-0">
        <Image
          src={destination.image}
          alt={destination.title}
          fill
          sizes="(min-width: 640px) 178px, 110px"
          className="object-cover"
        />
        <span className="absolute left-1.5 top-1.5 sm:left-3 sm:top-3 rounded-full bg-white/92 px-1.5 py-0.5 sm:px-2.5 sm:py-1 text-[8px] sm:text-[11px] font-semibold text-[#176E9E] shadow-sm">
          +{destination.rating}
        </span>
      </div>

      <div className="min-w-0 px-2.5 py-2 sm:px-4 sm:py-3.5 flex flex-col justify-between">
        <div className="flex items-start justify-between gap-1.5 sm:gap-3">
          <div className="min-w-0">
            <span className="rounded-full bg-[#EAF6FC] px-1.5 py-0.5 sm:px-3 sm:py-1 text-[8px] sm:text-[11px] font-semibold text-[#2882A9] inline-block mb-1">
              {destination.category}
            </span>
            <h3 className="text-[12px] sm:text-[16px] font-semibold leading-tight sm:leading-6 text-[#202B37] truncate sm:whitespace-normal">
              {destination.title}
            </h3>
          </div>
          <span className="shrink-0 text-right text-[9px] sm:text-[11px] font-semibold text-[#0E75BC] mt-1">
            {destination.distance}
          </span>
        </div>

        <p className="hidden sm:block mt-1.5 text-[12px] leading-5 text-[#6A7E8E] line-clamp-2">
          {destination.description}
        </p>

        <div className="mt-2 sm:mt-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-1.5 sm:gap-3">
          <div className="flex flex-wrap items-center gap-x-2 sm:gap-x-3 gap-y-1 text-[9px] sm:text-[11px] text-[#80909D]">
            <span className="inline-flex items-center gap-1">
              <ClockIcon className="h-3 w-3 sm:h-4 sm:w-4" />
              {destination.duration}
            </span>
            <span className="inline-flex items-center gap-1">
              <WalletIcon className="h-3 w-3 sm:h-4 sm:w-4" />
              {destination.price}
            </span>
          </div>
          <button
            onClick={() => {
              addDestination({
                id: destination.id || destination.title,
                title: destination.title,
                slug: destination.slug,
                category: destination.category,
                image: destination.image,
                latitude: destination.latitude,
                longitude: destination.longitude,
              });
              showToast(`${destination.title} berhasil ditambahkan ke perjalanan!`, 'success');
            }}
            type="button"
            className="inline-flex h-6 sm:h-8 items-center justify-center rounded-md sm:rounded-[8px] bg-[#0E75BC] px-2.5 sm:px-4 text-[9px] sm:text-[11px] font-semibold text-white transition-colors hover:bg-[#095f99] w-full sm:w-auto mt-1 sm:mt-0"
          >
            + Tambah
          </button>
        </div>
      </div>
    </article>
  );
}
