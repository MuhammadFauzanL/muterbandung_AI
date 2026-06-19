import type { Metadata } from 'next';
import { Suspense } from 'react';
import { AccommodationPageContent } from '@/components';

export const metadata: Metadata = {
  title: 'Pilih Penginapan - MuterBandung AI',
  description:
    'Pilih penginapan terbaik untuk itinerary Bandung dengan rekomendasi Cepot AI.',
};

export default function PlannerAccommodationPage() {
  return (
    <div className="min-h-screen bg-[#F5F8FC] text-slate-950 flex flex-col">
      <div className="flex-1">
        <Suspense fallback={<div className="mx-auto max-w-[1180px] px-4 py-8 text-sm font-semibold text-slate-500">Memuat penginapan...</div>}>
          <AccommodationPageContent />
        </Suspense>
      </div>
    </div>
  );
}
