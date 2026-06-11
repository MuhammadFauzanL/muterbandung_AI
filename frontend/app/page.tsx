import {
  Header,
  HeroSection,
  PopularDestinationsSection,
  CategoryHighlightsSection,
  Footer,
} from '@/components';

/**
 * Home Page - MuterBandung Splash Screen
 *
 * This is the landing page for MuterBandung AI application.
 * It displays a hero section with call-to-action buttons for users
 * to start exploring Bandung destinations.
 *
 * Components:
 * - Header: Top navigation bar with logo and menu
 * - HeroSection: Main hero section with heading, description, and CTA buttons
 * - PopularDestinationsSection: Grid of popular tourist spots
 * - CategoryHighlightsSection: Mosaic of destination categories
 * - Footer: Footer with copyright and links
 */
export default function Home() {
  return (
    <div className="relative min-h-screen overflow-hidden bg-white text-slate-950">
      <Header />
      <main className="flex-1">
        <HeroSection />
        <PopularDestinationsSection />
        <CategoryHighlightsSection />
      </main>
      <Footer />
    </div>
  );
}
