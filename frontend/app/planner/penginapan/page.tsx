import type { Metadata } from 'next';
import { AccommodationPageContent, Header } from '@/components';

export const metadata: Metadata = {
  title: 'Pilih Penginapan - MuterBandung AI',
  description:
    'Pilih penginapan terbaik untuk itinerary Bandung dengan rekomendasi Cepot AI.',
};

export default function PlannerAccommodationPage() {
  return (
    <div className="min-h-screen bg-[#F5F8FC] text-slate-950">
      <Header activeItem="planner" />
      <AccommodationPageContent />
      <footer className="border-t border-[#D9E8F3] bg-white">
        <div className="mx-auto flex max-w-[1180px] flex-col gap-1 px-4 py-5 text-sm text-slate-500 sm:px-8">
          <p className="font-semibold text-slate-900">MuterBandung</p>
          <p>© 2026 MuterBandung. Sampurasun! Powered by Cepot AI.</p>
        </div>
      </footer>
    </div>
  );
}
