/**
 * Destination Detail Page Content — Composer Component
 *
 * Assembles the destination detail page from smaller section components.
 */
import type { DestinationDetail } from '@/types';
import { DetailHero } from './DetailHero';
import { MetricBar } from './MetricBar';
import { AiReason } from './AiReason';
import { DestinationStory } from './DestinationStory';
import { Gallery } from './Gallery';
import { Facilities } from './Facilities';
import { Reviews } from './Reviews';
import { WeatherCard } from './WeatherCard';
import { NearbyStays } from './NearbyStays';
import { PlanCard } from './PlanCard';
import { BottomActions } from './BottomActions';

export function DestinationDetailPageContent({
  destination,
}: {
  destination: DestinationDetail;
}) {
  return (
    <main className="mx-auto max-w-[1180px] px-4 py-6 sm:px-8">
      <DetailHero destination={destination} />
      <MetricBar metrics={destination.metrics} />

      <div className="mt-6 grid gap-6 lg:grid-cols-[minmax(0,1fr)_320px]">
        <div className="space-y-6">
          <AiReason destination={destination} />
          <DestinationStory destination={destination} />
          <Gallery images={destination.gallery} />
          <Facilities facilities={destination.facilities} />
          <Reviews reviews={destination.reviews} />
        </div>

        <aside className="space-y-6 lg:sticky lg:top-6 lg:self-start">
          <WeatherCard destination={destination} />
          <NearbyStays destination={destination} />
          <PlanCard destination={destination} />
        </aside>
      </div>

      <BottomActions destination={destination} />
    </main>
  );
}
