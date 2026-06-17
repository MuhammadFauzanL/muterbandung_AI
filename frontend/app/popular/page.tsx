import type { Metadata } from 'next';
import { PopularPageContent } from '@/components';

export const metadata: Metadata = {
  title: 'Destinasi Populer - MuterBandung',
  description: 'Daftar destinasi wisata populer di Bandung.',
};

export default function PopularPage() {
  return (
    <div className="min-h-screen bg-[#F5F8FC] text-slate-950 flex flex-col">
      <div className="flex-1">
        <PopularPageContent />
      </div>
    </div>
  );
}
