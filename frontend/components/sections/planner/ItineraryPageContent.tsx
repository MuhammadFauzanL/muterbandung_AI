"use client";

import Link from 'next/link';
import { usePlanner } from '@/context/PlannerContext';
import { ListChecks } from 'lucide-react';

// Import Sub-Components
import { SummaryBadges } from './itinerary/SummaryBadges';
import { AiInsightCard } from './itinerary/AiInsightCard';
import { SelectedAccommodations } from './itinerary/SelectedAccommodations';
import { BudgetSummary } from './itinerary/BudgetSummary';
import { ItineraryTimeline } from './itinerary/ItineraryTimeline';
import { RouteVisualization } from './itinerary/RouteVisualization';
import { AiHelpCta } from './itinerary/AiHelpCta';
import { BottomActionButtons } from './itinerary/BottomActionButtons';
import { DeleteConfirmationModal } from './itinerary/DeleteConfirmationModal';
import { useState } from 'react';

export function ItineraryPageContent() {
  const { destinations, accommodations, removeDestination, removeAccommodation } = usePlanner();
  const [itemToDelete, setItemToDelete] = useState<{ id?: string, name?: string, title: string, type: 'destination' | 'accommodation' } | null>(null);

  const generateTimeline = () => {
    let currentHour = 8;
    const timeline: { time: string; title: string; type: 'destination' | 'accommodation'; name: string; id?: string }[] = [];

    destinations.forEach((dest) => {
      timeline.push({
        time: `${currentHour.toString().padStart(2, '0')}:00`,
        title: dest.title,
        type: 'destination',
        name: dest.title,
        id: dest.id,
      });
      currentHour += 2; 
    });

    if (accommodations.length > 0) {
      accommodations.forEach((acc, index) => {
        const checkInHour = Math.max(14 + index, currentHour);
        timeline.push({
          time: `${checkInHour.toString().padStart(2, '0')}:00`,
          title: acc.name,
          type: 'accommodation',
          name: acc.name,
        });
        currentHour = checkInHour + 1;
      });
    }
    return timeline;
  };

  const timelineItems = generateTimeline();
  const totalAccommodationCost = accommodations.reduce((sum, acc) => sum + acc.totalPrice, 0);
  const totalDestinationCost = destinations.length * 25000;
  const grandTotal = totalDestinationCost + totalAccommodationCost;

  const maxNights = accommodations.reduce((max, acc) => Math.max(max, acc.nights), 0);
  const durationString = maxNights > 0 ? `${maxNights + 1} Hari ${maxNights} Malam` : "1 Hari";
  const maxGuests = accommodations.reduce((max, acc) => Math.max(max, acc.guests), 1);
  const firstAccommodationName = accommodations.length > 0 ? accommodations[0].name : undefined;

  return (
    <main className="mx-auto max-w-[1180px] px-3 sm:px-8 pt-3 pb-6 sm:py-12">
      {/* Centered Header */}
      <div className="mb-4 sm:mb-12 text-center max-w-2xl mx-auto">
        <h1 className="text-[24px] sm:text-[42px] font-bold tracking-tight text-[#112F43]">
          Perjalananmu Siap!
        </h1>
      </div>

      <div className="grid gap-3 sm:gap-10 lg:grid-cols-[340px_minmax(0,1fr)] items-start">
        {/* KOLOM KIRI: SUMMARY COLUMN */}
        <div className="space-y-3 sm:space-y-6">
          <SummaryBadges 
            destinationsCount={destinations.length}
            firstAccommodationName={firstAccommodationName}
            durationString={durationString}
            maxGuests={maxGuests}
            grandTotal={grandTotal}
          />
          <AiInsightCard />
          <SelectedAccommodations accommodations={accommodations} />
          <BudgetSummary 
            totalDestinationCost={totalDestinationCost}
            totalAccommodationCost={totalAccommodationCost}
            accommodations={accommodations}
            grandTotal={grandTotal}
          />
        </div>

        {/* KOLOM KANAN: TIMELINE COLUMN */}
        <div>
          <ItineraryTimeline 
            timelineItems={timelineItems}
            onRemoveDestination={(id, title) => setItemToDelete({ id, title, type: 'destination' })}
            onRemoveAccommodation={(name) => setItemToDelete({ name, title: name, type: 'accommodation' })}
          />

          {/* Rangkuman Perjalananmu (Middle Section of Right Column) */}
          <section className="mt-6 mb-6 sm:mt-12 sm:mb-12 rounded-[16px] sm:rounded-[24px] border border-[#CFE5F2] bg-[#F2FAFE] p-4 sm:p-8 shadow-sm">
            <div className="flex items-center justify-between gap-2 mb-4 sm:mb-8 border-b border-[#CFE5F2] pb-3 sm:pb-6">
              <h3 className="font-bold text-[14px] sm:text-[22px] text-[#112F43] flex items-center gap-1.5 sm:gap-3 leading-tight">
                <ListChecks className="h-4 w-4 sm:h-6 sm:w-6 text-[#0E75BC] shrink-0" /> Rangkuman Perjalanan
              </h3>
              <Link href="/explore" className="bg-white border border-[#0E75BC] text-[#0E75BC] px-2.5 sm:px-5 py-1 sm:py-2.5 rounded-full text-[10px] sm:text-xs font-bold shadow-sm hover:bg-slate-50 transition-colors flex items-center justify-center gap-1 shrink-0">
                <span className="text-xs sm:text-lg leading-none font-black">+</span> Tambah
              </Link>
            </div>
            
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-6">
              <div>
                <h4 className="text-[10px] sm:text-[11px] font-bold text-[#0E75BC] mb-1.5 sm:mb-4 tracking-wider uppercase">DESTINASI TERPILIH</h4>
                {destinations.length > 0 ? (
                  <ul className="space-y-1.5 sm:space-y-3">
                    {destinations.map((dest, i) => (
                      <li key={i} className="flex items-center gap-1.5 sm:gap-2">
                        <span className="h-3.5 w-3.5 sm:h-4 sm:w-4 rounded-full bg-[#112F43] flex items-center justify-center text-[8px] sm:text-[10px] text-white shrink-0">✔</span>
                        <span className="text-[12px] sm:text-sm text-[#557083] font-medium">{dest.title}</span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-[12px] sm:text-sm text-[#557083]">Belum ada.</p>
                )}
              </div>
              
              <div>
                <h4 className="text-[10px] sm:text-[11px] font-bold text-[#0E75BC] mb-1.5 sm:mb-4 tracking-wider uppercase mt-3 sm:mt-0">PENGINAPAN</h4>
                {accommodations.length > 0 ? (
                  <ul className="space-y-1.5 sm:space-y-3">
                    {accommodations.map((acc, i) => (
                      <li key={i} className="flex items-center gap-1.5 sm:gap-2">
                        <span className="h-3.5 w-3.5 sm:h-4 sm:w-4 rounded-full bg-[#112F43] flex items-center justify-center text-[8px] sm:text-[10px] text-white shrink-0">✔</span>
                        <span className="text-[12px] sm:text-sm text-[#557083] font-medium">{acc.name}</span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-[12px] sm:text-sm text-[#557083]">Belum ada.</p>
                )}
              </div>
              
              <div>
                <h4 className="text-[10px] sm:text-[11px] font-bold text-[#0E75BC] mb-1.5 sm:mb-4 tracking-wider uppercase mt-3 sm:mt-0">DURASI</h4>
                <p className="text-[12px] sm:text-sm text-[#557083] font-medium">{durationString}</p>
              </div>
            </div>
          </section>

          <RouteVisualization />

          <AiHelpCta />
        </div>
      </div>

      <BottomActionButtons />

      {/* Delete Modal */}
      <DeleteConfirmationModal
        isOpen={itemToDelete !== null}
        title={itemToDelete?.title || ''}
        onClose={() => setItemToDelete(null)}
        onConfirm={() => {
          if (itemToDelete?.type === 'destination' && itemToDelete.id) {
            removeDestination(itemToDelete.id);
          } else if (itemToDelete?.type === 'accommodation' && itemToDelete.name) {
            removeAccommodation(itemToDelete.name);
          }
          setItemToDelete(null);
        }}
      />
    </main>
  );
}
