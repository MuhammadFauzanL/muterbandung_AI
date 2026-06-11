import Image from 'next/image';
import type { DestinationDetail } from '@/types';

export function NearbyStays({ destination }: { destination: DestinationDetail }) {
  return (
    <section className="rounded-2xl border border-[#D9E8F3] bg-white p-5 shadow-[0_12px_28px_rgba(15,23,42,0.06)]">
      <div className="flex items-center justify-between gap-3">
        <h2 className="text-lg font-semibold text-slate-950">
          Penginapan Terdekat
        </h2>
        <a
          href="#hotels"
          className="text-sm font-semibold text-[#0E75BC] hover:text-[#095f99]"
        >
          Lihat
        </a>
      </div>
      <div id="hotels" className="mt-4 space-y-3">
        {destination.nearbyStays.map((stay) => (
          <article
            key={stay.name}
            className="grid grid-cols-[86px_minmax(0,1fr)] gap-3 rounded-2xl border border-[#E1EEF6] bg-[#F8FBFE] p-2.5"
          >
            <div className="relative h-20 overflow-hidden rounded-xl">
              <Image
                src={stay.image}
                alt={stay.name}
                fill
                sizes="86px"
                className="object-cover"
              />
            </div>
            <div className="min-w-0 py-1">
              <h3 className="truncate text-sm font-semibold text-slate-950">
                {stay.name}
              </h3>
              <p className="mt-1 text-xs text-slate-500">{stay.location}</p>
              <p className="mt-2 text-xs font-semibold text-[#E54545]">
                {stay.price}
              </p>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
