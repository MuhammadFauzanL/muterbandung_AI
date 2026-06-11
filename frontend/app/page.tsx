import {
  HeroSection,
  PopularDestinationsSection,
  CategoryHighlightsSection,
  PageShell,
} from '@/components';

export default function Home() {
  return (
    <PageShell backgroundClassName="overflow-hidden bg-white">
      <main className="flex-1">
        <HeroSection />
        <PopularDestinationsSection />
        <CategoryHighlightsSection />
      </main>
    </PageShell>
  );
}
