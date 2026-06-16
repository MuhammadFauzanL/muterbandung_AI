import { ItineraryPageContent } from '@/components/sections/planner/ItineraryPageContent';

export default function ItineraryPage() {
  return (
    <div className="min-h-screen bg-[#F5F8FC] text-slate-950 flex flex-col">
      <div className="flex-1">
        <ItineraryPageContent />
      </div>
    </div>
  );
}
