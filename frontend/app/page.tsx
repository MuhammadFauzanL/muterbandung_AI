"use client";

import {
  HeroSection,
  PopularDestinationsSection,
  FeaturesSection,
  AIChatPromoSection,
  CategoryHighlightsSection,
} from '@/components';

/**
 * Home Page - MuterBandung Splash Screen
 *
 * This is the landing page for MuterBandung AI application.
 * It displays a hero section with call-to-action buttons for users
 * to start exploring Bandung destinations.
 */
export default function Home() {
  return (
    <div className="flex min-h-screen flex-col bg-white">
      <main className="flex-1">
        <HeroSection />
        {/* Filter Tags (Dihapus sesuai permintaan pengguna) */}
        <PopularDestinationsSection />
        <FeaturesSection />
        <AIChatPromoSection />
        <CategoryHighlightsSection />
      </main>
    </div>
  );
}
