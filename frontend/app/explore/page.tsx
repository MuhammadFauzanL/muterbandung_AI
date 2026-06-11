import type { Metadata } from 'next';
import { ExplorePageContent, Header } from '@/components';

export const metadata: Metadata = {
  title: 'Explore Bandung - MuterBandung AI',
  description:
    'Cari rekomendasi destinasi Bandung dengan filter, rencana perjalanan, dan bantuan Cepot AI.',
};

export default function ExplorePage() {
  return (
    <div className="min-h-screen bg-[#F3F8FC] text-slate-950">
      <Header activeItem="explore" />
      <ExplorePageContent />
      <footer className="border-t border-[#D9E8F3] bg-white">
        <div className="mx-auto flex max-w-[1180px] flex-col gap-1 px-4 py-5 text-sm text-slate-500 sm:px-8">
          <p className="font-semibold text-slate-900">MuterBandung</p>
          <p>© 2026 MuterBandung. Sampurasun! Powered by Cepot AI.</p>
        </div>
      </footer>
    </div>
  );
}
