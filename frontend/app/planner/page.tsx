import type { Metadata } from 'next';
import { PlannerPageContent } from '@/components';

export const metadata: Metadata = {
  title: 'AI Planner - MuterBandung AI',
  description:
    'Susun perjalanan Bandung dengan rekomendasi destinasi dari Cepot AI.',
};

export default function PlannerPage() {
  return (
    <div className="min-h-screen bg-[#F5F8FC] text-slate-950 flex flex-col">
      <div className="flex-1">
        <PlannerPageContent />
      </div>
    </div>
  );
}
