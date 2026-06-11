import Image from 'next/image';
import { SIMILAR_DESTINATIONS } from '@/constants';
import { TravelIcon } from '@/components/ui/icons';

export function SimilarDestinations() {
  return (
    <section>
      <div className="mb-3 flex items-center gap-2 text-[#202B37]">
        <span className="text-[#0E75BC]">
          <TravelIcon />
        </span>
        <h2 className="text-[16px] font-semibold leading-6">
          Wisata Serupa yang Mungkin Kamu Sukai
        </h2>
      </div>
      <div className="grid gap-4 sm:grid-cols-2">
        {SIMILAR_DESTINATIONS.map((destination, index) => (
          <article
            key={destination.title}
            className="overflow-hidden rounded-[12px] border border-[#DDEAF2] bg-white shadow-[0_8px_22px_rgba(17,73,112,0.05)]"
          >
            <div className="relative h-[154px]">
              <Image
                src={destination.image}
                alt={destination.title}
                fill
                loading={index === 0 ? 'eager' : 'lazy'}
                sizes="(min-width: 640px) 50vw, 100vw"
                className="object-cover"
              />
            </div>
            <div className="px-4 py-3">
              <h3 className="text-[14px] font-semibold text-[#202B37]">
                {destination.title}
              </h3>
              <p className="mt-1 text-[12px] leading-5 text-[#6A7E8E]">
                {destination.description}
              </p>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
