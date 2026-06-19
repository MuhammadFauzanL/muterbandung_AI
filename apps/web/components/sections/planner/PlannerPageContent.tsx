"use client";

import { InsightCard } from './components/InsightCard';
import { RecommendationList } from './components/RecommendationList';
import { NearbyHotels } from './components/NearbyHotels';
import { SimilarDestinations } from './components/SimilarDestinations';
import { TripSummary } from './components/TripSummary';
import { PlannerChatPrompt } from './components/PlannerChatPrompt';

export function PlannerPageContent() {
  return (
    <main className="mx-auto max-w-[1180px] px-4 py-3 sm:py-6 sm:px-8">
      <div className="mb-2 sm:mb-4">
        <h1 className="text-[22px] sm:text-[28px] font-bold text-[#112F43]">Atur Perjalananmu</h1>
      </div>

      <div className="mt-2 sm:mt-5 grid gap-3 sm:gap-5 lg:grid-cols-[minmax(0,1fr)_340px]">
        <div className="min-w-0 space-y-3 sm:space-y-6 order-2 lg:order-1">
          <InsightCard />
          <RecommendationList />
          <NearbyHotels />
          <SimilarDestinations />
        </div>

        <div className="space-y-4 sm:space-y-6 order-1 lg:order-2">
          <TripSummary />
        </div>
      </div>
    </main>
  );
}
