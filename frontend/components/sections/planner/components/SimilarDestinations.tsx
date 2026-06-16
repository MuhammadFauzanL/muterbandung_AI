import Image from 'next/image';
import { Compass as TravelIcon } from 'lucide-react';

type SimilarDestination = {
  title: string;
  description: string;
  image: string;
};

const SIMILAR_DESTINATIONS: readonly SimilarDestination[] = [
  {
    title: 'Tangkuban Perahu',
    description: 'Kawah vulkanik ikonik di Bandung Utara.',
    image: 'https://lh3.googleusercontent.com/gps-cs-s/APNQkAHifK93cLCMZlOTIDe2ADjcVI95LAsq2Wxb5-enWtH3RtVZsqHW9kMuWH0HZBWIGs1wJRY8YSq7bjbL1vlfhHygyxxA9kh6JlHCZz_YH9UDTo9jWaWjJJcTTCTfj6UQ3QAFnPFB=w529-h298-k-no',
  },
  {
    title: 'Orchid Forest',
    description: 'Hutan pinus dengan koleksi anggrek langka.',
    image:
      'https://lh3.googleusercontent.com/gps-cs-s/APNQkAERgQbdJmcea-WVQRIwQMsij89snO3wRz4DvqGMvC6PEpLybyoAELon0RD5_UCkLTcxELcSIgdncpF9SSN8xBO97qLNlfaeUCSUPmv0D8lusqVsXWhDXBTEm9KHbrk_OvYVq6XzjQ=w397-h298-k-no',
  },
] as const;

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
      <div className="grid gap-3 sm:gap-4 grid-cols-2 sm:grid-cols-2">
        {SIMILAR_DESTINATIONS.map((destination, index) => (
          <article
            key={destination.title}
            className="overflow-hidden rounded-[12px] border border-[#DDEAF2] bg-white shadow-[0_8px_22px_rgba(17,73,112,0.05)]"
          >
            <div className="relative h-[90px] sm:h-[154px]">
              <Image
                src={destination.image}
                alt={destination.title}
                fill
                loading={index === 0 ? 'eager' : 'lazy'}
                sizes="(min-width: 640px) 50vw, 50vw"
                className="object-cover"
              />
            </div>
            <div className="px-2.5 py-2 sm:px-4 sm:py-3">
              <h3 className="text-[11px] sm:text-[14px] font-semibold text-[#202B37] line-clamp-1">
                {destination.title}
              </h3>
              <p className="mt-0.5 sm:mt-1 text-[9px] sm:text-[12px] leading-snug sm:leading-5 text-[#6A7E8E] line-clamp-2">
                {destination.description}
              </p>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
