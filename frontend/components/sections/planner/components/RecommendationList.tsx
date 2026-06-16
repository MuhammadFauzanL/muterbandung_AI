import { MapPin as PinIcon } from 'lucide-react';
import { DestinationRecommendationCard } from './DestinationRecommendationCard';
import type { PlannerDestination } from './DestinationRecommendationCard';

const NEARBY_DESTINATIONS: readonly PlannerDestination[] = [
  {
    title: 'Situ Patenggang',
    category: 'Alam',
    description:
      'Danau legendaris dengan pemandangan kebun teh yang menyejukkan mata.',
    distance: '25m away',
    duration: '1-2 hours',
    price: 'Rp15.000',
    rating: '4.8',
    image:
      'https://lh3.googleusercontent.com/gps-cs-s/APNQkAHISCcZ-O9qL9owcEdr85SSmYhdV_k7EGg20tmtLbPJixb7f8rGwu60QbHvaZnaiXkLWCdzAAnWN_3mt2tCMnc4G05K-QmNphCtvDBDbvgY9cl1uAWWRYD6banb_Y4fVcEMa-vfZw=w408-h306-k-no',
  },
  {
    title: 'Ranca Upas',
    category: 'Alam',
    description:
      'Area perkemahan rasa alam camping ground yang asri di tengah hutan pinus.',
    distance: '1.5km away',
    duration: '2-3 hours',
    price: 'Rp25.000',
    rating: '4.6',
    image: 'https://lh3.googleusercontent.com/gps-cs-s/APNQkAG8DCU30cz4EEgrJPvJaMhP8rbS5HQITRlZurNtY3MtrCdeby1UldfcmMVhcNqQaWajGEUJ6VB09bDIwR4fpUTWlx8LvVWfrS3TJYcLYonHI44ge2nWoMlgJftRndPgTa0KQYcp=w408-h269-k-no',
  },
] as const;

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
