import type { Metadata } from 'next';
import { ExplorePageContent, PageShell } from '@/components';

export const metadata: Metadata = {
  title: 'Explore Bandung - MuterBandung AI',
  description:
    'Cari rekomendasi destinasi Bandung dengan filter, rencana perjalanan, dan bantuan Cepot AI.',
};

export default function ExplorePage() {
  return (
    <PageShell
      activeItem="explore"
      backgroundClassName="bg-[#F3F8FC]"
      footerVariant="compact"
    >
      <ExplorePageContent />
    </PageShell>
  );
}
