/**
 * Planner Page Content — Composer Component
 *
 * Assembles the AI planner page from smaller section components.
 */
import { SuccessBanner } from './SuccessBanner';
import { InsightCard } from './InsightCard';
import { RecommendationList } from './RecommendationList';
import { SimilarDestinations } from './SimilarDestinations';
import { TripSummary } from './TripSummary';
import { PlannerChatPrompt } from './PlannerChatPrompt';

export function PlannerPageContent() {
  return (
    <main className="mx-auto max-w-[1180px] px-4 py-6 sm:px-8">
      <SuccessBanner />

      <div className="mt-5 grid gap-5 lg:grid-cols-[minmax(0,1fr)_340px]">
        <div className="min-w-0 space-y-6">
          <InsightCard />
          <RecommendationList />
          <SimilarDestinations />
        </div>

        <div className="space-y-6">
          <TripSummary />
          <PlannerChatPrompt />
        </div>
      </div>
    </main>
  );
}
