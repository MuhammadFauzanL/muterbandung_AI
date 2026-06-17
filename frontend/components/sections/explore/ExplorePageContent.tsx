"use client";

import { useState } from 'react';
import { SafeImage } from '@/components/ui/SafeImage';
import Link from 'next/link';
import { usePlanner } from '@/context/PlannerContext';
import {
  EXPLORE_CATEGORY_FILTERS,
  EXPLORE_DESTINATIONS,
  EXPLORE_FILTER_GROUPS,
  EXPLORE_STATS,
} from '@/constants';
import { MapPin, Heart, Wallet, Clock, Search, SlidersHorizontal, Filter, X } from 'lucide-react';
import type { ExploreDestination } from '@/types';



function PlannerHero() {
  const [activeSaran, setActiveSaran] = useState<string | null>(null);
  const saranOptions = ['Cari yang lebih murah', 'Tambahkan wisata kuliner', 'Wisata dekat Lembang'];

  return (
    <section className="relative overflow-hidden rounded-[24px] px-5 py-6 sm:px-10 sm:py-14 text-white shadow-[0_18px_36px_rgba(31,90,145,0.18)]">
      {/* Mountain Background Image */}
      <SafeImage
        src="https://images.unsplash.com/photo-1588668214407-6ea9a6d8c272?q=80&w=1200&auto=format&fit=crop"
        alt="Mountain background"
        fill
        className="object-cover"
        priority
      />
      {/* Dark Gradient Overlay for Readability */}
      <div className="absolute inset-0 bg-[linear-gradient(135deg,rgba(14,117,188,0.75)_0%,rgba(20,58,92,0.85)_100%)]" />

      <div className="relative z-10 w-full">
        <h1 className="text-[24px] font-semibold leading-tight sm:text-[34px]">
          Rencana Seru di Bandung
        </h1>
        <form className="mt-4 w-full max-w-[800px] flex items-center rounded-xl bg-white p-1 shadow-[0_16px_32px_rgba(0,0,0,0.12)] border border-white/20 backdrop-blur-sm">
          <label className="sr-only" htmlFor="planner-search">
            Cari rencana perjalanan
          </label>
          <div className="flex flex-1 items-center gap-2 px-3 text-slate-500">
            <Search className="h-4 w-4 shrink-0" />
            <input
              id="planner-search"
              name="query"
              type="search"
              placeholder="Mau mengubah rekomendasi?"
              className="h-8 min-w-0 flex-1 bg-transparent text-[13px] sm:text-[15px] text-slate-900 outline-none placeholder:text-slate-500 font-medium"
            />
          </div>
          <button
            type="submit"
            className="inline-flex h-8 items-center justify-center rounded-lg bg-[#0E75BC] px-6 text-[13px] font-bold text-white transition-colors hover:bg-[#0A5F9E] shadow-sm"
          >
            Cari
          </button>
        </form>
        <div className="mt-4 flex items-center gap-3 text-[13px] text-white/90 overflow-x-auto whitespace-nowrap pb-2 scrollbar-hide w-full">
          <span className="shrink-0 font-semibold text-white/80">Saran Cepot:</span>
          {saranOptions.map(saran => (
            <button
              key={saran}
              onClick={() => {
                const input = document.getElementById('planner-search') as HTMLInputElement;
                if (input) {
                  input.value = saran;
                  input.focus();
                }
              }}
              className="shrink-0 rounded-full px-4 py-1.5 backdrop-blur-sm transition-colors border bg-white/20 hover:bg-white/30 border-white/10"
            >
              {saran}
            </button>
          ))}
        </div>
      </div>
    </section>
  );
}

function CategoryChips() {
  const [active, setActive] = useState<string | null>('✨ Semua Rekomendasi');
  const categories = ['✨ Semua Rekomendasi', 'Alam', 'Keluarga', 'Kuliner', 'Edukasi', 'Dekat Saya'];
  return (
    <div className="flex items-center gap-3 overflow-x-auto whitespace-nowrap pb-2 scrollbar-hide w-full">
      {categories.map((filter) => (
        <button
          key={filter}
          type="button"
          onClick={() => setActive(filter === active ? null : filter)}
          className={`shrink-0 rounded-full px-5 py-2 text-[14px] font-medium transition-all shadow-md ${filter === active
              ? 'bg-[#0E75BC] text-white border border-[#0E75BC] shadow-[#0E75BC]/30'
              : 'border border-[#E1EEF6] bg-white text-[#23689A] hover:border-[#0E75BC] hover:text-[#0E75BC] hover:shadow-lg'
            }`}
        >
          {filter}
        </button>
      ))}
    </div>
  );
}

function RecommendationBanner() {
  return (
    <section className="rounded-2xl border border-[#CFE5F2] bg-[#EAF6FC] px-5 py-4 text-[#1D5F88]">
      <p className="text-sm font-semibold">
        Kenapa Cepot AI Merekomendasikan Ini?
      </p>
      <p className="mt-1 text-sm leading-6 text-[#45738F]">
        Destinasi ini cocok untuk keluarga dengan budget di bawah Rp100.000,
        memiliki akses nyaman, dan berkaitan hangat dengan suasana Bandung.
      </p>
    </section>
  );
}


function ResultsSummary({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  const [activeBudget, setActiveBudget] = useState<string | null>('Gratis');
  const [activeTipeHari, setActiveTipeHari] = useState<string | null>('Akhir Pekan');
  const [activeRating, setActiveRating] = useState<string | null>('4+');
  const [toggles, setToggles] = useState({ ramahAnak: false, bukaSekarang: true, butuhPenginapan: false });
  const budgetOptions = ['Gratis', '< 50k', '< 100k', 'Custom'];

  const handleReset = () => {
    setActiveBudget(null);
    setActiveTipeHari(null);
    setActiveRating(null);
    setToggles({ ramahAnak: false, bukaSekarang: false, butuhPenginapan: false });
  };

  const handleApply = () => {
    onClose();
    document.getElementById('destinations')?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-[10000] bg-slate-900/40 backdrop-blur-sm lg:hidden transition-opacity"
          onClick={onClose}
        />
      )}

      {/* Sidebar / Drawer */}
      <aside className={`fixed inset-y-0 left-0 z-[10010] w-[280px] bg-white p-5 shadow-2xl transition-transform lg:static lg:block lg:w-full lg:transform-none lg:rounded-2xl lg:border lg:border-slate-200 lg:bg-white lg:p-5 lg:shadow-[0_8px_30px_rgb(0,0,0,0.04)] overflow-y-auto ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}`}>
        <div className="flex items-center justify-between lg:hidden mb-4">
          <h2 className="text-[18px] font-bold text-slate-900">Sesuaikan Hasil</h2>
          <button onClick={onClose} className="rounded-full p-2 text-slate-500 hover:bg-slate-100">
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="mb-6 hidden lg:block">
          <h2 className="text-[19px] font-bold text-slate-900">
            Sesuaikan Hasil
          </h2>
        </div>

        <div className="space-y-6">
          {/* Budget */}
          <div>
            <h3 className="text-[11px] font-bold uppercase tracking-wider text-[#64748B] mb-3">
              Budget Per Orang
            </h3>
            <div className="grid grid-cols-2 gap-2">
              {budgetOptions.map(b => (
                <button
                  key={b}
                  onClick={() => setActiveBudget(activeBudget === b ? null : b)}
                  className={`rounded-full border py-1.5 text-[13px] font-medium transition-colors ${activeBudget === b ? 'border-[#0E75BC] bg-[#0E75BC] text-white shadow-sm' : 'border-slate-200 text-slate-700 hover:border-[#0E75BC] hover:text-[#0E75BC]'}`}
                >
                  {b}
                </button>
              ))}
            </div>
          </div>

          {/* Radius Jarak */}
          <div>
            <h3 className="text-[11px] font-bold uppercase tracking-wider text-[#64748B] mb-3">
              Radius Jarak
            </h3>
            <div className="px-1 mb-2">
              <input
                type="range"
                min="0"
                max="2"
                step="1"
                defaultValue="1"
                className="w-full h-1.5 bg-[#EAF6FC] rounded-full appearance-none cursor-pointer accent-[#0E75BC]"
                aria-label="Radius jarak dalam km"
              />
              <div className="flex justify-between text-[11px] font-semibold text-slate-500 mt-2">
                <span>5km</span>
                <span className="text-[#0E75BC]">10km</span>
                <span>25km+</span>
              </div>
            </div>
            <button className="mt-2 flex items-center gap-1.5 text-[12px] font-bold text-[#0E75BC] hover:text-[#0A5F9E]">
              <MapPin className="h-4 w-4" />
              Gunakan Lokasi Saya
            </button>
          </div>

          {/* Waktu Kunjungan */}
          <div>
            <h3 className="text-[11px] font-bold uppercase tracking-wider text-[#64748B] mb-3">
              Waktu Kunjungan
            </h3>
            <p className="text-[12px] font-medium text-slate-500 mb-2">Tipe Hari</p>
            <div className="grid grid-cols-2 gap-2 mb-4">
              {['Hari Kerja', 'Akhir Pekan'].map(th => (
                <button
                  key={th}
                  onClick={() => setActiveTipeHari(activeTipeHari === th ? null : th)}
                  className={`rounded-full border py-1.5 text-[13px] font-medium transition-colors ${activeTipeHari === th ? 'border-[#0E75BC] bg-[#0E75BC] text-white shadow-sm' : 'border-slate-200 text-slate-700 hover:border-[#0E75BC] hover:text-[#0E75BC]'}`}
                >
                  {th}
                </button>
              ))}
            </div>
            <p className="text-[12px] font-medium text-slate-500 mb-2">Jam Rencana</p>
            <div className="flex items-center justify-between rounded-xl bg-[#F0F7FB] px-3 py-2 border border-transparent focus-within:border-[#0E75BC] focus-within:bg-white transition-colors">
              <input type="time" defaultValue="08:00" className="bg-transparent text-[14px] font-semibold text-slate-900 outline-none w-full cursor-pointer" />
            </div>
          </div>

          {/* Minimal Rating */}
          <div>
            <h3 className="text-[11px] font-bold uppercase tracking-wider text-[#64748B] mb-3">
              Minimal Rating
            </h3>
            <div className="grid grid-cols-3 gap-2">
              {['3+', '4+', '4.5+'].map(r => (
                <button
                  key={r}
                  onClick={() => setActiveRating(activeRating === r ? null : r)}
                  className={`rounded-full border py-1.5 text-[13px] font-medium transition-colors ${activeRating === r ? 'border-slate-900 bg-slate-900 text-white font-bold shadow-sm' : 'border-slate-200 text-slate-700 hover:border-[#0E75BC] hover:text-[#0E75BC]'}`}
                >
                  {r}
                </button>
              ))}
            </div>
          </div>

          {/* Toggles */}
          <div className="space-y-4 pt-2">
            {Object.entries({
              ramahAnak: 'Ramah Anak',
              bukaSekarang: 'Buka Sekarang',
              butuhPenginapan: 'Butuh Penginapan'
            }).map(([key, label]) => (
              <div key={key} className="flex items-center justify-between cursor-pointer" onClick={() => setToggles(prev => ({ ...prev, [key]: !prev[key as keyof typeof toggles] }))}>
                <span className="text-[14px] font-medium text-slate-800">{label}</span>
                <div className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors ${toggles[key as keyof typeof toggles] ? 'bg-[#0E75BC]' : 'bg-slate-200'}`}>
                  <span className={`inline-block h-3.5 w-3.5 rounded-full bg-white transition-transform ${toggles[key as keyof typeof toggles] ? 'translate-x-4' : 'translate-x-1'}`}></span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="sticky bottom-0 z-20 mt-8 pt-4 pb-4 border-t border-slate-100 bg-white flex flex-col gap-3 -mx-5 px-5">
          <button
            type="button"
            onClick={handleApply}
            className="w-full rounded-xl bg-[#0E75BC] px-4 py-3.5 text-[14px] font-bold text-white transition-colors hover:bg-[#095f99] shadow-sm"
          >
            Terapkan Filters
          </button>
          <button
            type="button"
            onClick={handleReset}
            className="flex w-full items-center justify-center gap-1.5 rounded-xl border border-slate-200 bg-white px-4 py-3.5 text-[14px] font-bold text-slate-500 hover:text-[#E54545] hover:border-[#E54545] transition-colors"
          >
            <svg fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-4 h-4"><path strokeLinecap="round" strokeLinejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99" /></svg>
            Reset Filter
          </button>
        </div>
      </aside>
    </>
  );
}

function DestinationCard({
  destination,
  eagerImage = false,
}: {
  destination: ExploreDestination;
  eagerImage?: boolean;
}) {
  const { addDestination, destinations } = usePlanner();
  const [showToast, setShowToast] = useState(false);
  const [isFavorite, setIsFavorite] = useState(false);

  const isSelected = destinations.some((d) => d.id === destination.id);

  const handlePilih = () => {
    if (!isSelected) {
      addDestination({ id: destination.id, title: destination.title });
      setShowToast(true);
      setTimeout(() => setShowToast(false), 3000);
    }
  };

  return (
    <article className="relative overflow-hidden rounded-[20px] border border-slate-200 bg-white shadow-[0_8px_24px_rgba(0,0,0,0.04)] flex flex-col">
      {/* Toast Notification */}
      <div className={`absolute top-4 left-1/2 -translate-x-1/2 z-50 rounded-2xl border border-slate-100 bg-white px-4 py-2.5 text-[13px] font-bold text-slate-800 shadow-[0_12px_40px_rgba(0,0,0,0.12)] transition-all duration-300 flex items-center gap-2 ${showToast ? 'opacity-100 translate-y-0' : 'opacity-0 -translate-y-4 pointer-events-none'}`}>
        <div className="flex items-center justify-center w-5 h-5 rounded-full bg-green-100 text-green-600">
          <svg fill="none" viewBox="0 0 24 24" strokeWidth={3} stroke="currentColor" className="w-3 h-3"><path strokeLinecap="round" strokeLinejoin="round" d="m4.5 12.75 6 6 9-13.5" /></svg>
        </div>
        Tersimpan!
      </div>

      <div className="relative h-[120px] sm:h-[200px] w-full overflow-hidden">
        <SafeImage
          src={destination.image}
          alt={destination.title}
          fill
          loading={eagerImage ? 'eager' : 'lazy'}
          sizes="(min-width: 1024px) 390px, (min-width: 640px) 50vw, 100vw"
          className={`object-cover transition-transform duration-500 hover:scale-105 ${destination.id === 'sudut-pandang' ? 'object-bottom' : 'object-center'}`}
          category={destination.category}
        />
        <div className="absolute left-2 top-2 sm:left-4 sm:top-4 rounded-full bg-white/95 px-2 py-0.5 sm:px-3 sm:py-1.5 text-[9px] sm:text-[12px] font-bold text-[#0E75BC] shadow-sm backdrop-blur-sm">
          {destination.category}
        </div>
        <button
          type="button"
          onClick={() => setIsFavorite(!isFavorite)}
          aria-label={`Simpan ${destination.title}`}
          className={`absolute right-2 top-2 sm:right-4 sm:top-4 inline-flex h-6 w-6 sm:h-9 sm:w-9 items-center justify-center rounded-full bg-white/95 shadow-sm backdrop-blur-sm transition-colors ${isFavorite ? 'text-[#E54545]' : 'text-slate-400 hover:text-[#E54545]'}`}
        >
          <Heart className={`h-3 w-3 sm:h-5 sm:w-5 ${isFavorite ? 'fill-current' : ''}`} />
        </button>
      </div>

      <div className="flex flex-col flex-1 p-3 sm:p-5">
        <div className="flex items-center gap-1.5 text-[9px] sm:text-xs font-medium text-[#0E75BC] mb-1">
          <MapPin className="h-2.5 w-2.5 sm:h-3.5 sm:w-3.5" />
          <span className="truncate">{destination.location}</span>
        </div>
        <div className="flex flex-col sm:flex-row items-start justify-between gap-1 sm:gap-4 mb-2">
          <h3 className="text-[12px] sm:text-[18px] font-bold leading-tight text-slate-900 line-clamp-1 sm:line-clamp-none">
            {destination.title}
          </h3>
          <span className="flex items-center gap-1 text-[10px] sm:text-[15px] font-bold text-[#E54545] shrink-0">
            ★ {destination.rating}
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-y-1 sm:gap-y-1.5 mb-2 sm:mb-3">
          <div className="flex items-center gap-1.5 sm:gap-2 text-[10px] sm:text-[13px] font-medium text-slate-500">
            <Wallet className="h-3 w-3 sm:h-4 sm:w-4 shrink-0" />
            <span className="truncate">{destination.price}</span>
          </div>
          <div className="flex items-center gap-1.5 sm:gap-2 text-[10px] sm:text-[13px] font-medium text-slate-500">
            <Clock className="h-3 w-3 sm:h-4 sm:w-4 shrink-0" />
            <span className="truncate">07.00 - 17.00</span>
          </div>
          <div className="flex items-center gap-1.5 sm:gap-2 text-[10px] sm:text-[13px] font-medium text-slate-500">
            <MapPin className="h-3 w-3 sm:h-4 sm:w-4 shrink-0" />
            <span className="truncate">12.4 km</span>
          </div>
          <div className="flex items-center gap-1.5 sm:gap-2 text-[10px] sm:text-[13px] font-medium text-slate-500">
            <Clock className="h-3 w-3 sm:h-4 sm:w-4 shrink-0" />
            <span className="truncate">Durasi: {destination.duration}</span>
          </div>
        </div>

        <div className="mt-auto pt-2 sm:pt-3 border-t border-slate-100 flex items-center justify-between">
          <Link
            href={`/explore/${destination.id}`}
            className="text-[10px] sm:text-[14px] font-bold text-[#0E75BC] hover:text-[#095f99] transition-colors"
          >
            Lihat Detail
          </Link>
          {isSelected ? (
            <Link
              href="/planner"
              className="rounded-lg sm:rounded-full bg-[#E54545]/10 px-3 py-1.5 sm:px-5 sm:py-2 text-[10px] sm:text-[13px] font-bold text-[#E54545] transition-colors hover:bg-[#E54545]/20 shadow-none border border-[#E54545]/20"
            >
              Lihat Planner
            </Link>
          ) : (
            <button
              onClick={handlePilih}
              type="button"
              className="rounded-lg sm:rounded-full bg-[#E54545] px-3 py-1.5 sm:px-5 sm:py-2 text-[10px] sm:text-[13px] font-bold text-white transition-colors hover:bg-[#d43b3b] shadow-sm"
            >
              Pilih
            </button>
          )}
        </div>
      </div>
    </article>
  );
}

function DestinationGrid() {
  return (
    <section id="destinations" className="min-w-0">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between mb-2">
        <div>
          <h2 className="text-xl sm:text-[26px] font-bold tracking-normal text-[#1A202C]">
            Rekomendasi untukmu
          </h2>
          <p className="mt-0.5 text-xs sm:text-[15px] font-medium text-[#718096]">
            Ditemukan 12 tempat yang sedang populer.
          </p>
        </div>
      </div>

      <div className="mt-4 grid gap-3 grid-cols-2 sm:gap-4 lg:gap-5">
        {EXPLORE_DESTINATIONS.map((destination, index) => (
          <DestinationCard
            key={destination.id}
            destination={destination}
            eagerImage={index === 0}
          />
        ))}
      </div>

      <div className="mt-7 flex items-center justify-center gap-2">
        {[1, 2, 3].map((page) => (
          <button
            key={page}
            type="button"
            className={`h-9 min-w-9 rounded-full text-sm font-semibold ${page === 1
                ? 'bg-[#0E75BC] text-white'
                : 'border border-[#D9E8F3] bg-white text-[#23689A]'
              }`}
          >
            {page}
          </button>
        ))}
      </div>
    </section>
  );
}

export function ExplorePageContent() {
  const [isFilterOpen, setIsFilterOpen] = useState(false);

  return (
    <main id="planner" className="mx-auto max-w-[1180px] w-full px-4 py-6 sm:px-8 overflow-x-hidden">
      <PlannerHero />

      <div className="mt-5 mb-2">
        <RecommendationBanner />
      </div>

      <div className="sticky top-0 z-30 pt-4 pb-2 -mx-4 px-4 sm:mx-0 sm:px-0 space-y-3 pointer-events-none">
        <div className="pointer-events-auto">
          <CategoryChips />
        </div>
        <div className="lg:hidden pointer-events-auto">
          <button
            onClick={() => setIsFilterOpen(true)}
            className="flex w-full items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white py-3 text-[14px] font-bold text-slate-700 shadow-md"
          >
            <Filter className="h-4 w-4" />
            Sesuaikan Hasil Rekomendasi
          </button>
        </div>
      </div>

      <div className="mt-0 lg:mt-2 grid gap-6 lg:grid-cols-[280px_minmax(0,1fr)]">
        <ResultsSummary isOpen={isFilterOpen} onClose={() => setIsFilterOpen(false)} />
        <DestinationGrid />
      </div>
    </main>
  );
}
