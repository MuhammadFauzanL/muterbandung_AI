import Image from 'next/image';
import Link from 'next/link';
import { ArrowLeftIcon, LocationIcon } from '@/components/ui/icons';
import type { DestinationDetail } from '@/types';

export function DetailHero({ destination }: { destination: DestinationDetail }) {
  return (
    <section className="relative overflow-hidden rounded-[18px] bg-slate-900">
      <div className="relative h-[360px] sm:h-[430px]">
        <Image
          src={destination.heroImage}
          alt={destination.title}
          fill
          preload
          sizes="(min-width: 1180px) 1180px, 100vw"
          className="object-cover object-[center_58%] sm:object-center"
        />
        <div className="absolute inset-0 bg-[linear-gradient(180deg,rgba(15,23,42,0.06)_0%,rgba(15,23,42,0.2)_42%,rgba(15,23,42,0.78)_100%)]" />
      </div>

      <div className="absolute inset-x-0 bottom-0 px-5 pb-20 text-white sm:px-8">
        <Link
          href="/explore"
          className="mb-7 inline-flex items-center gap-2 rounded-full bg-white/92 px-4 py-2 text-sm font-semibold text-[#0E75BC] shadow-sm transition-colors hover:bg-white"
        >
          <ArrowLeftIcon />
          Kembali
        </Link>
        <p className="text-sm font-semibold uppercase tracking-[0.22em] text-[#D8EFFB]">
          {destination.category}
        </p>
        <h1 className="mt-3 max-w-[620px] text-[40px] font-semibold leading-[1.05] sm:text-[54px]">
          {destination.title}
        </h1>
        <div className="mt-4 flex items-center gap-2 text-sm font-medium text-white/88">
          <LocationIcon className="h-4 w-4 text-white" />
          <span>{destination.location}</span>
        </div>
      </div>
    </section>
  );
}
