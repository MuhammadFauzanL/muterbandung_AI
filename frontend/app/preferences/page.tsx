import type { Metadata } from 'next';
import { PreferencesForm } from '@/components/sections/preferences';

export const metadata: Metadata = {
  title: 'Preferensi Wisata - MuterBandung AI',
  description: 'Atur preferensi wisata Anda agar Cepot AI dapat memberikan rekomendasi destinasi yang paling sesuai di Bandung Raya.',
};

export default function PreferencesPage() {
  return (
    <div className="min-h-screen bg-[#F7F9FF] text-slate-900">
      <PreferencesForm />
    </div>
  );
}
