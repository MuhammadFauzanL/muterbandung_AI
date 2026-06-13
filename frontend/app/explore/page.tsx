import type { Metadata } from 'next';
import { ExplorePageContent } from '@/components';

export const metadata: Metadata = {
  title: 'Explore Bandung - MuterBandung AI',
  description:
    'Cari rekomendasi destinasi Bandung dengan filter, rencana perjalanan, dan bantuan Cepot AI.',
};

export default function ExplorePage() {
  return (
    <div className="min-h-screen bg-[#F3F8FC] text-slate-950 flex flex-col">
      <ExplorePageContent />
    </div>
  );
}
