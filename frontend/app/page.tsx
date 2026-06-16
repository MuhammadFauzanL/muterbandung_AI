"use client";

import {
  HeroSection,
  PersonalizedDestinationsSection,
  PopularDestinationsSection,
  FeaturesSection,
  AIChatPromoSection,
  CategoryHighlightsSection,
} from '@/components';
import { useAuth } from '@/context/AuthContext';

/**
 * Home Page - MuterBandung Splash Screen
 *
 * This is the landing page for MuterBandung AI application.
 * It displays a hero section with call-to-action buttons for users
 * to start exploring Bandung destinations.
 */
export default function Home() {
  const { isLoggedIn } = useAuth();

  return (
    <div className="flex min-h-screen flex-col bg-white">
      <main className="flex-1">
        <HeroSection />
        {/* Filter Tags (Dihapus sesuai permintaan pengguna) */}
        {isLoggedIn && <PersonalizedDestinationsSection />}
        <PopularDestinationsSection />
        <FeaturesSection />
        <AIChatPromoSection />
        <CategoryHighlightsSection />
      </main>
    </div>
  );
}
