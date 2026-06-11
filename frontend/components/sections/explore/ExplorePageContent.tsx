/**
 * Explore Page Content — Composer Component
 *
 * Assembles the explore/search page from smaller section components.
 */
import { PlannerHero } from './PlannerHero';
import { CategoryChips } from './CategoryChips';
import { RecommendationBanner } from './RecommendationBanner';
import { ResultsSummary } from './ResultsSummary';
import { DestinationGrid } from './DestinationGrid';

export function ExplorePageContent() {
  return (
    <main id="planner" className="mx-auto max-w-[1180px] px-4 py-6 sm:px-8">
      <PlannerHero />

      <div className="mt-5 space-y-4">
        <CategoryChips />
        <RecommendationBanner />
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-[280px_minmax(0,1fr)]">
        <ResultsSummary />
        <DestinationGrid />
      </div>
    </main>
  );
}
