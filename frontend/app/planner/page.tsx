import type { Metadata } from 'next';
import { PageShell, PlannerPageContent } from '@/components';

export const metadata: Metadata = {
  title: 'AI Planner - MuterBandung AI',
  description:
    'Susun perjalanan Bandung dengan rekomendasi destinasi dari Cepot AI.',
};

export default function PlannerPage() {
  return (
    <PageShell
      activeItem="planner"
      backgroundClassName="bg-[#F5F8FC]"
      footerVariant="compact"
    >
      <PlannerPageContent />
    </PageShell>
  );
}
