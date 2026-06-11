/**
 * Accommodation Page Content — Composer Component
 *
 * Assembles the accommodation selection page from smaller section components.
 */
import Link from 'next/link';
import { ACCOMMODATIONS } from '@/constants';
import { ArrowLeftIcon } from '@/components/ui/icons';
import { PlannerProgress } from './PlannerProgress';
import { AccommodationFilters } from './AccommodationFilters';
import { CepotInsight } from './CepotInsight';
import { AccommodationCard } from './AccommodationCard';
import { TripSidebar } from './TripSidebar';

export function AccommodationPageContent() {
  return (
    <main className="mx-auto max-w-[1180px] px-4 py-6 sm:px-8">
      <div className="mb-5 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <Link
            href="/planner"
            className="inline-flex items-center gap-2 text-[13px] font-semibold text-[#0E75BC] hover:text-[#095f99]"
          >
            <ArrowLeftIcon />
            Kembali ke itinerary
          </Link>
          <h1 className="mt-4 text-[28px] font-semibold leading-tight text-[#202B37] sm:text-[34px]">
            Pilih Penginapan
          </h1>
          <p className="mt-2 max-w-2xl text-[14px] leading-6 text-[#657786]">
            Rekomendasi penginapan disusun dari jarak ke destinasi, budget,
            dan ritme perjalanan yang sudah kamu pilih.
          </p>
        </div>

        <div className="w-full lg:max-w-[460px]">
          <PlannerProgress />
        </div>
      </div>

      <div className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_340px]">
        <div className="min-w-0 space-y-5">
          <AccommodationFilters />
          <CepotInsight />

          <section>
            <div className="mb-3 flex flex-col gap-1 sm:flex-row sm:items-end sm:justify-between">
              <div>
                <h2 className="text-[17px] font-semibold text-[#202B37]">
                  Rekomendasi Terbaik
                </h2>
                <p className="text-[12px] leading-5 text-[#7B8B99]">
                  3 penginapan cocok untuk itinerary Ciwidey.
                </p>
              </div>
              <button
                type="button"
                className="self-start rounded-full border border-[#DDEAF2] bg-white px-3 py-1.5 text-[12px] font-semibold text-[#23689A] transition-colors hover:border-[#0E75BC] hover:text-[#0E75BC] sm:self-auto"
              >
                Urutkan: Rekomendasi AI
              </button>
            </div>

            <div className="space-y-3">
              {ACCOMMODATIONS.map((accommodation, index) => (
                <AccommodationCard
                  key={accommodation.name}
                  accommodation={accommodation}
                  eagerImage={index === 0}
                />
              ))}
            </div>
          </section>
        </div>

        <div className="lg:sticky lg:top-6 lg:self-start">
          <TripSidebar />
        </div>
      </div>
    </main>
  );
}
