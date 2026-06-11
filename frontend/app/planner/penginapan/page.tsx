import type { Metadata } from 'next';
import { AccommodationPageContent, PageShell } from '@/components';

export const metadata: Metadata = {
  title: 'Pilih Penginapan - MuterBandung AI',
  description:
    'Pilih penginapan terbaik untuk itinerary Bandung dengan rekomendasi Cepot AI.',
};

export default function PlannerAccommodationPage() {
  return (
    <PageShell
      activeItem="planner"
      backgroundClassName="bg-[#F5F8FC]"
      footerVariant="compact"
    >
      <AccommodationPageContent />
    </PageShell>
  );
}
