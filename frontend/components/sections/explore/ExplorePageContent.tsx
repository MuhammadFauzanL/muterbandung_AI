"use client";

import { FormEvent, useEffect, useState } from 'react';
import Link from 'next/link';
import { Clock, Filter, Heart, Loader2, MapPin, Search, Wallet, X } from 'lucide-react';
import { SafeImage } from '@/components/ui/SafeImage';
import { usePlanner } from '@/context/PlannerContext';
import { destinationsService, type ExploreQueryParams } from '@/services/destinations';
import type {
  ExploreDestination,
  ExploreFilterMetadata,
  ExploreFilters,
  ExploreMeta,
} from '@/types';

const DEFAULT_FILTERS: ExploreFilters = {
  search: '',
  intent: null,
  budget: null,
  customMaxPrice: '',
  radiusKm: null,
  dayType: 'weekend',
  plannedTime: '08:00',
  minRating: null,
  childFriendly: false,
  openNow: false,
  needsAccommodation: false,
  sort: 'quality',
};

const DEFAULT_META: ExploreMeta = {
  page: 1,
  limit: 12,
  total: 0,
  totalPages: 0,
};

const BUDGET_OPTIONS: Array<{ label: string; value: ExploreFilters['budget'] }> = [
  { label: 'Gratis', value: 'free' },
  { label: '< 50k', value: 'under_50000' },
  { label: '< 100k', value: 'under_100000' },
  { label: 'Custom', value: 'custom' },
];

const RADIUS_OPTIONS = [5, 10, 25];
const FALLBACK_INTENTS = ['Alam', 'Keluarga', 'Kuliner', 'Edukasi'];

function hasUserLocation(filters: ExploreFilters) {
  return typeof filters.userLat === 'number' && typeof filters.userLng === 'number';
}

function parseCustomPrice(value: string) {
  const parsed = Number(value.replace(/[^\d]/g, ''));
  return Number.isFinite(parsed) && parsed > 0 ? parsed : undefined;
}

function buildExploreParams(filters: ExploreFilters, page: number): ExploreQueryParams {
  const maxPrice =
    filters.budget === 'under_50000'
      ? 50000
      : filters.budget === 'under_100000'
        ? 100000
        : filters.budget === 'custom'
          ? parseCustomPrice(filters.customMaxPrice)
          : undefined;

  const withLocation = hasUserLocation(filters);
  const sort = filters.sort === 'nearest' && !withLocation ? 'quality' : filters.sort;

  return {
    page,
    limit: 12,
    search: filters.search.trim() || undefined,
    intent: filters.intent,
    freeOnly: filters.budget === 'free' ? true : undefined,
    maxPrice,
    minRating: filters.minRating ?? undefined,
    childFriendly: filters.childFriendly || undefined,
    openNow: filters.openNow || undefined,
    dayType: filters.openNow ? filters.dayType : undefined,
    plannedTime: filters.openNow ? filters.plannedTime : undefined,
    userLat: withLocation ? filters.userLat : undefined,
    userLng: withLocation ? filters.userLng : undefined,
    radiusKm: withLocation ? filters.radiusKm : undefined,
    sort,
  };
}

function readStoredLocation(): Pick<ExploreFilters, 'userLat' | 'userLng'> {
  if (typeof window === 'undefined') return {};
  try {
    const stored = window.sessionStorage.getItem('muterbandung_location');
    if (!stored) return {};
    const parsed = JSON.parse(stored) as { lat?: number; lng?: number };
    if (typeof parsed.lat !== 'number' || typeof parsed.lng !== 'number') return {};
    return { userLat: parsed.lat, userLng: parsed.lng };
  } catch {
    window.sessionStorage.removeItem('muterbandung_location');
    return {};
  }
}

function useDebouncedValue<T>(value: T, delayMs: number): [T, () => void] {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      setDebouncedValue(value);
    }, delayMs);

    return () => {
      window.clearTimeout(timeoutId);
    };
  }, [value, delayMs]);

  return [debouncedValue, () => setDebouncedValue(value)];
}

function PlannerHero({
  searchValue,
  onSearchChange,
  onSubmit,
  onNearby,
}: {
  searchValue: string;
  onSearchChange: (value: string) => void;
  onSubmit: () => void;
  onNearby: () => void;
}) {
  const saranOptions = ['Cari yang lebih murah', 'Tambahkan wisata kuliner', 'Wisata dekat saya'];

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    onSubmit();
  };

  return (
    <section className="relative overflow-hidden rounded-[24px] px-5 py-6 text-white shadow-[0_18px_36px_rgba(31,90,145,0.18)] sm:px-10 sm:py-14">
      <SafeImage
        src="https://images.unsplash.com/photo-1588668214407-6ea9a6d8c272?q=80&w=1200&auto=format&fit=crop"
        alt="Mountain background"
        fill
        className="object-cover"
        priority
      />
      <div className="absolute inset-0 bg-[linear-gradient(135deg,rgba(14,117,188,0.75)_0%,rgba(20,58,92,0.85)_100%)]" />

      <div className="relative z-10 w-full">
        <h1 className="text-[24px] font-semibold leading-tight sm:text-[34px]">
          Rencana Seru di Bandung
        </h1>
        <form
          onSubmit={handleSubmit}
          className="mt-4 flex w-full max-w-[800px] items-center rounded-xl border border-white/20 bg-white p-1 shadow-[0_16px_32px_rgba(0,0,0,0.12)] backdrop-blur-sm"
        >
          <label className="sr-only" htmlFor="planner-search">
            Cari rencana perjalanan
          </label>
          <div className="flex flex-1 items-center gap-2 px-3 text-slate-500">
            <Search className="h-4 w-4 shrink-0" />
            <input
              id="planner-search"
              name="query"
              type="search"
              value={searchValue}
              onChange={(event) => onSearchChange(event.target.value)}
              placeholder="Mau mencari wisata apa?"
              className="h-8 min-w-0 flex-1 bg-transparent text-[13px] font-medium text-slate-900 outline-none placeholder:text-slate-500 sm:text-[15px]"
            />
          </div>
          <button
            type="submit"
            className="inline-flex h-8 items-center justify-center rounded-lg bg-[#0E75BC] px-6 text-[13px] font-bold text-white shadow-sm transition-colors hover:bg-[#0A5F9E]"
          >
            Cari
          </button>
        </form>
        <div className="scrollbar-hide mt-4 flex w-full items-center gap-3 overflow-x-auto whitespace-nowrap pb-2 text-[13px] text-white/90">
          <span className="shrink-0 font-semibold text-white/80">Saran Cepot:</span>
          {saranOptions.map((saran) => (
            <button
              key={saran}
              type="button"
              onClick={() => {
                if (saran === 'Wisata dekat saya') {
                  onNearby();
                  return;
                }
                onSearchChange(saran);
              }}
              className="shrink-0 rounded-full border border-white/10 bg-white/20 px-4 py-1.5 backdrop-blur-sm transition-colors hover:bg-white/30"
            >
              {saran}
            </button>
          ))}
        </div>
      </div>
    </section>
  );
}

function CategoryChips({
  metadata,
  activeIntent,
  nearbyActive,
  onSelectIntent,
  onNearby,
}: {
  metadata: ExploreFilterMetadata | null;
  activeIntent: string | null;
  nearbyActive: boolean;
  onSelectIntent: (intent: string | null) => void;
  onNearby: () => void;
}) {
  const dynamicIntents = metadata?.intents?.slice(0, 5).map((item) => item.value) || [];
  const intents = dynamicIntents.length ? dynamicIntents : FALLBACK_INTENTS;

  return (
    <div className="scrollbar-hide flex w-full items-center gap-3 overflow-x-auto whitespace-nowrap pb-2">
      <button
        type="button"
        onClick={() => onSelectIntent(null)}
        className={`shrink-0 rounded-full px-5 py-2 text-[14px] font-medium shadow-md transition-all ${
          !activeIntent && !nearbyActive
            ? 'border border-[#0E75BC] bg-[#0E75BC] text-white shadow-[#0E75BC]/30'
            : 'border border-[#E1EEF6] bg-white text-[#23689A] hover:border-[#0E75BC] hover:text-[#0E75BC] hover:shadow-lg'
        }`}
      >
        Semua Rekomendasi
      </button>
      {intents.map((intent) => (
        <button
          key={intent}
          type="button"
          onClick={() => onSelectIntent(intent)}
          className={`shrink-0 rounded-full px-5 py-2 text-[14px] font-medium shadow-md transition-all ${
            activeIntent === intent && !nearbyActive
              ? 'border border-[#0E75BC] bg-[#0E75BC] text-white shadow-[#0E75BC]/30'
              : 'border border-[#E1EEF6] bg-white text-[#23689A] hover:border-[#0E75BC] hover:text-[#0E75BC] hover:shadow-lg'
          }`}
        >
          {intent}
        </button>
      ))}
      <button
        type="button"
        onClick={onNearby}
        className={`shrink-0 rounded-full px-5 py-2 text-[14px] font-medium shadow-md transition-all ${
          nearbyActive
            ? 'border border-[#0E75BC] bg-[#0E75BC] text-white shadow-[#0E75BC]/30'
            : 'border border-[#E1EEF6] bg-white text-[#23689A] hover:border-[#0E75BC] hover:text-[#0E75BC] hover:shadow-lg'
        }`}
      >
        Dekat Saya
      </button>
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
        Rekomendasi ini berbasis AI-assisted scoring dari rating, ulasan,
        sentimen, label wisata, dan kelengkapan data. Lokasi hanya dipakai
        ketika kamu memilih fitur dekat saya.
      </p>
    </section>
  );
}

function ResultsSummary({
  isOpen,
  onClose,
  filters,
  onChange,
  onReset,
  onUseLocation,
  hasLocation,
  locationMessage,
  locationLoading,
}: {
  isOpen: boolean;
  onClose: () => void;
  filters: ExploreFilters;
  onChange: (patch: Partial<ExploreFilters>) => void;
  onReset: () => void;
  onUseLocation: () => void;
  hasLocation: boolean;
  locationMessage: string | null;
  locationLoading: boolean;
}) {
  const radiusIndex = Math.max(0, RADIUS_OPTIONS.indexOf(filters.radiusKm || 10));
  const update = (patch: Partial<ExploreFilters>) => onChange(patch);
  const handleViewResults = () => {
    onClose();
    document.getElementById('destinations')?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <>
      {isOpen && (
        <button
          type="button"
          aria-label="Tutup filter"
          className="fixed inset-0 z-[10000] bg-slate-900/40 backdrop-blur-sm transition-opacity lg:hidden"
          onClick={onClose}
        />
      )}

      <aside className={`fixed inset-y-0 left-0 z-[10010] w-[280px] overflow-y-auto bg-white p-5 shadow-2xl transition-transform lg:static lg:block lg:w-full lg:translate-x-0 lg:rounded-2xl lg:border lg:border-slate-200 lg:bg-white lg:p-5 lg:shadow-[0_8px_30px_rgb(0,0,0,0.04)] ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}`}>
        <div className="mb-4 flex items-center justify-between lg:hidden">
          <h2 className="text-[18px] font-bold text-slate-900">Sesuaikan Hasil</h2>
          <button type="button" onClick={onClose} className="rounded-full p-2 text-slate-500 hover:bg-slate-100">
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="mb-6 hidden lg:block">
          <h2 className="text-[19px] font-bold text-slate-900">Sesuaikan Hasil</h2>
        </div>

        <div className="space-y-6">
          <div>
            <h3 className="mb-3 text-[11px] font-bold uppercase tracking-wider text-[#64748B]">
              Budget Per Orang
            </h3>
            <div className="grid grid-cols-2 gap-2">
              {BUDGET_OPTIONS.map((budget) => (
                <button
                  key={budget.label}
                  type="button"
                  onClick={() => update({ budget: filters.budget === budget.value ? null : budget.value })}
                  className={`rounded-full border py-1.5 text-[13px] font-medium transition-colors ${
                    filters.budget === budget.value
                      ? 'border-[#0E75BC] bg-[#0E75BC] text-white shadow-sm'
                      : 'border-slate-200 text-slate-700 hover:border-[#0E75BC] hover:text-[#0E75BC]'
                  }`}
                >
                  {budget.label}
                </button>
              ))}
            </div>
            {filters.budget === 'custom' && (
              <input
                type="number"
                min="0"
                inputMode="numeric"
                value={filters.customMaxPrice}
                onChange={(event) => update({ customMaxPrice: event.target.value })}
                placeholder="Contoh: 75000"
                className="mt-3 w-full rounded-xl border border-slate-200 px-3 py-2 text-[13px] font-semibold text-slate-800 outline-none focus:border-[#0E75BC]"
              />
            )}
          </div>

          <div>
            <h3 className="mb-3 text-[11px] font-bold uppercase tracking-wider text-[#64748B]">
              Radius Jarak
            </h3>
            <div className="mb-2 px-1">
              <input
                type="range"
                min="0"
                max="2"
                step="1"
                value={radiusIndex}
                onChange={(event) => update({ radiusKm: RADIUS_OPTIONS[Number(event.target.value)] })}
                className="h-1.5 w-full cursor-pointer appearance-none rounded-full bg-[#EAF6FC] accent-[#0E75BC]"
                aria-label="Radius jarak dalam km"
              />
              <div className="mt-2 flex justify-between text-[11px] font-semibold text-slate-500">
                {RADIUS_OPTIONS.map((radius) => (
                  <span key={radius} className={filters.radiusKm === radius ? 'text-[#0E75BC]' : ''}>
                    {radius === 25 ? '25km+' : `${radius}km`}
                  </span>
                ))}
              </div>
            </div>
            <button
              type="button"
              onClick={onUseLocation}
              className="mt-2 flex items-center gap-1.5 text-[12px] font-bold text-[#0E75BC] hover:text-[#0A5F9E]"
            >
              {locationLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <MapPin className="h-4 w-4" />}
              {hasLocation ? 'Lokasi Saya Aktif' : 'Gunakan Lokasi Saya'}
            </button>
            {locationMessage && (
              <p className="mt-2 text-[11px] font-medium leading-5 text-slate-500">
                {locationMessage}
              </p>
            )}
          </div>

          <div>
            <h3 className="mb-3 text-[11px] font-bold uppercase tracking-wider text-[#64748B]">
              Waktu Kunjungan
            </h3>
            <p className="mb-2 text-[12px] font-medium text-slate-500">Tipe Hari</p>
            <div className="mb-4 grid grid-cols-2 gap-2">
              {[
                { label: 'Hari Kerja', value: 'weekday' as const },
                { label: 'Akhir Pekan', value: 'weekend' as const },
              ].map((day) => (
                <button
                  key={day.value}
                  type="button"
                  onClick={() => update({ dayType: filters.dayType === day.value ? null : day.value })}
                  className={`rounded-full border py-1.5 text-[13px] font-medium transition-colors ${
                    filters.dayType === day.value
                      ? 'border-[#0E75BC] bg-[#0E75BC] text-white shadow-sm'
                      : 'border-slate-200 text-slate-700 hover:border-[#0E75BC] hover:text-[#0E75BC]'
                  }`}
                >
                  {day.label}
                </button>
              ))}
            </div>
            <p className="mb-2 text-[12px] font-medium text-slate-500">Jam Rencana</p>
            <div className="flex items-center justify-between rounded-xl border border-transparent bg-[#F0F7FB] px-3 py-2 transition-colors focus-within:border-[#0E75BC] focus-within:bg-white">
              <input
                type="time"
                value={filters.plannedTime}
                onChange={(event) => update({ plannedTime: event.target.value })}
                className="w-full cursor-pointer bg-transparent text-[14px] font-semibold text-slate-900 outline-none"
              />
            </div>
          </div>

          <div>
            <h3 className="mb-3 text-[11px] font-bold uppercase tracking-wider text-[#64748B]">
              Minimal Rating
            </h3>
            <div className="grid grid-cols-3 gap-2">
              {[3, 4, 4.5].map((rating) => (
                <button
                  key={rating}
                  type="button"
                  onClick={() => update({ minRating: filters.minRating === rating ? null : rating })}
                  className={`rounded-full border py-1.5 text-[13px] font-medium transition-colors ${
                    filters.minRating === rating
                      ? 'border-slate-900 bg-slate-900 font-bold text-white shadow-sm'
                      : 'border-slate-200 text-slate-700 hover:border-[#0E75BC] hover:text-[#0E75BC]'
                  }`}
                >
                  {rating}+
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-4 pt-2">
            <ToggleRow
              label="Ramah Anak"
              active={filters.childFriendly}
              onClick={() => update({ childFriendly: !filters.childFriendly })}
            />
            <ToggleRow
              label="Buka Sekarang"
              active={filters.openNow}
              onClick={() => update({ openNow: !filters.openNow })}
            />
            <ToggleRow
              label="Butuh Penginapan"
              active={false}
              disabled
              note="Coming soon"
              onClick={() => undefined}
            />
          </div>
        </div>

        <div className="-mx-5 sticky bottom-0 z-20 mt-8 flex flex-col gap-3 border-t border-slate-100 bg-white px-5 pb-4 pt-4">
          <button
            type="button"
            onClick={handleViewResults}
            className="w-full rounded-xl bg-[#0E75BC] px-4 py-3.5 text-[14px] font-bold text-white shadow-sm transition-colors hover:bg-[#095f99]"
          >
            Lihat Hasil
          </button>
          <button
            type="button"
            onClick={onReset}
            className="flex w-full items-center justify-center gap-1.5 rounded-xl border border-slate-200 bg-white px-4 py-3.5 text-[14px] font-bold text-slate-500 transition-colors hover:border-[#E54545] hover:text-[#E54545]"
          >
            Reset Filter
          </button>
        </div>
      </aside>
    </>
  );
}

function ToggleRow({
  label,
  active,
  disabled = false,
  note,
  onClick,
}: {
  label: string;
  active: boolean;
  disabled?: boolean;
  note?: string;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      disabled={disabled}
      onClick={onClick}
      className={`flex w-full items-center justify-between text-left ${disabled ? 'cursor-not-allowed opacity-50' : 'cursor-pointer'}`}
    >
      <span className="text-[14px] font-medium text-slate-800">
        {label}
        {note && <span className="ml-2 text-[11px] text-slate-400">{note}</span>}
      </span>
      <span className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors ${active ? 'bg-[#0E75BC]' : 'bg-slate-200'}`}>
        <span className={`inline-block h-3.5 w-3.5 rounded-full bg-white transition-transform ${active ? 'translate-x-4' : 'translate-x-1'}`} />
      </span>
    </button>
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

  const isSelected = destinations.some((item) => item.id === destination.id);
  const displayCategory = destination.primaryIntent || destination.category;
  const detailHref = `/explore/${destination.slug || destination.id}`;

  const handlePilih = () => {
    if (!isSelected) {
      addDestination({ id: destination.id, title: destination.title });
      setShowToast(true);
      window.setTimeout(() => setShowToast(false), 3000);
    }
  };

  return (
    <article className="relative flex flex-col overflow-hidden rounded-[20px] border border-slate-200 bg-white shadow-[0_8px_24px_rgba(0,0,0,0.04)]">
      <div className={`absolute left-1/2 top-4 z-50 flex -translate-x-1/2 items-center gap-2 rounded-2xl border border-slate-100 bg-white px-4 py-2.5 text-[13px] font-bold text-slate-800 shadow-[0_12px_40px_rgba(0,0,0,0.12)] transition-all duration-300 ${showToast ? 'translate-y-0 opacity-100' : 'pointer-events-none -translate-y-4 opacity-0'}`}>
        <span className="flex h-5 w-5 items-center justify-center rounded-full bg-green-100 text-green-600">
          <svg fill="none" viewBox="0 0 24 24" strokeWidth={3} stroke="currentColor" className="h-3 w-3">
            <path strokeLinecap="round" strokeLinejoin="round" d="m4.5 12.75 6 6 9-13.5" />
          </svg>
        </span>
        Tersimpan!
      </div>

      <div className="relative h-[120px] w-full overflow-hidden sm:h-[200px]">
        <SafeImage
          src={destination.image}
          alt={destination.title}
          fill
          loading={eagerImage ? 'eager' : 'lazy'}
          sizes="(min-width: 1024px) 390px, (min-width: 640px) 50vw, 100vw"
          className="object-cover transition-transform duration-500 hover:scale-105"
          category={destination.category}
        />
        <div className="absolute left-2 top-2 rounded-full bg-white/95 px-2 py-0.5 text-[9px] font-bold text-[#0E75BC] shadow-sm backdrop-blur-sm sm:left-4 sm:top-4 sm:px-3 sm:py-1.5 sm:text-[12px]">
          {displayCategory}
        </div>
        <button
          type="button"
          onClick={() => setIsFavorite(!isFavorite)}
          aria-label={`Simpan ${destination.title}`}
          className={`absolute right-2 top-2 inline-flex h-6 w-6 items-center justify-center rounded-full bg-white/95 shadow-sm backdrop-blur-sm transition-colors sm:right-4 sm:top-4 sm:h-9 sm:w-9 ${isFavorite ? 'text-[#E54545]' : 'text-slate-400 hover:text-[#E54545]'}`}
        >
          <Heart className={`h-3 w-3 sm:h-5 sm:w-5 ${isFavorite ? 'fill-current' : ''}`} />
        </button>
      </div>

      <div className="flex flex-1 flex-col p-3 sm:p-5">
        <div className="mb-1 flex items-center gap-1.5 text-[9px] font-medium text-[#0E75BC] sm:text-xs">
          <MapPin className="h-2.5 w-2.5 shrink-0 sm:h-3.5 sm:w-3.5" />
          <span className="truncate">{destination.location}</span>
        </div>
        <div className="mb-2 flex flex-col items-start justify-between gap-1 sm:flex-row sm:gap-4">
          <h3 className="line-clamp-1 text-[12px] font-bold leading-tight text-slate-900 sm:line-clamp-none sm:text-[18px]">
            {destination.title}
          </h3>
          <span className="flex shrink-0 items-center gap-1 text-[10px] font-bold text-[#E54545] sm:text-[15px]">
            ★ {destination.rating}
          </span>
        </div>

        <div className="mb-2 grid grid-cols-1 gap-y-1 sm:mb-3 sm:grid-cols-2 sm:gap-y-1.5">
          <div className="flex items-center gap-1.5 text-[10px] font-medium text-slate-500 sm:gap-2 sm:text-[13px]">
            <Wallet className="h-3 w-3 shrink-0 sm:h-4 sm:w-4" />
            <span className="truncate">{destination.price}</span>
          </div>
          <div className="flex items-center gap-1.5 text-[10px] font-medium text-slate-500 sm:gap-2 sm:text-[13px]">
            <Clock className="h-3 w-3 shrink-0 sm:h-4 sm:w-4" />
            <span className="truncate">{destination.openingHoursLabel || 'Jam menyesuaikan'}</span>
          </div>
          <div className="flex items-center gap-1.5 text-[10px] font-medium text-slate-500 sm:gap-2 sm:text-[13px]">
            <MapPin className="h-3 w-3 shrink-0 sm:h-4 sm:w-4" />
            <span className="truncate">
              {typeof destination.distanceKm === 'number' ? `${destination.distanceKm} km` : 'Aktifkan lokasi'}
            </span>
          </div>
          <div className="flex items-center gap-1.5 text-[10px] font-medium text-slate-500 sm:gap-2 sm:text-[13px]">
            <Clock className="h-3 w-3 shrink-0 sm:h-4 sm:w-4" />
            <span className="truncate">Durasi: {destination.duration}</span>
          </div>
        </div>

        {destination.scoreReason && (
          <p className="mb-3 line-clamp-2 text-[10px] leading-4 text-slate-500 sm:text-[12px]">
            {destination.scoreReason}
          </p>
        )}

        <div className="mt-auto flex items-center justify-between border-t border-slate-100 pt-2 sm:pt-3">
          <Link
            href={detailHref}
            className="text-[10px] font-bold text-[#0E75BC] transition-colors hover:text-[#095f99] sm:text-[14px]"
          >
            Lihat Detail
          </Link>
          {isSelected ? (
            <Link
              href="/planner"
              className="rounded-lg border border-[#E54545]/20 bg-[#E54545]/10 px-3 py-1.5 text-[10px] font-bold text-[#E54545] transition-colors hover:bg-[#E54545]/20 sm:rounded-full sm:px-5 sm:py-2 sm:text-[13px]"
            >
              Lihat Planner
            </Link>
          ) : (
            <button
              onClick={handlePilih}
              type="button"
              className="rounded-lg bg-[#E54545] px-3 py-1.5 text-[10px] font-bold text-white shadow-sm transition-colors hover:bg-[#d43b3b] sm:rounded-full sm:px-5 sm:py-2 sm:text-[13px]"
            >
              Pilih
            </button>
          )}
        </div>
      </div>
    </article>
  );
}

function DestinationGrid({
  destinations,
  loading,
  error,
  meta,
  page,
  onPageChange,
}: {
  destinations: ExploreDestination[];
  loading: boolean;
  error: string | null;
  meta: ExploreMeta;
  page: number;
  onPageChange: (page: number) => void;
}) {
  const totalPages = meta.totalPages || 0;
  const startPage = Math.max(1, Math.min(page - 2, Math.max(1, totalPages - 4)));
  const visiblePages = Array.from(
    { length: Math.min(5, totalPages) },
    (_, index) => startPage + index,
  ).filter((item) => item <= totalPages);

  return (
    <section id="destinations" className="min-w-0">
      <div className="mb-2 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h2 className="text-xl font-bold tracking-normal text-[#1A202C] sm:text-[26px]">
            Rekomendasi terbaik di Bandung
          </h2>
          <p className="mt-0.5 text-xs font-medium text-[#718096] sm:text-[15px]">
            {loading ? 'Mengambil rekomendasi terbaru...' : `Ditemukan ${meta.total} tempat dari data aktif.`}
          </p>
        </div>
      </div>

      {error && (
        <div className="mt-4 rounded-2xl border border-red-100 bg-red-50 px-4 py-3 text-sm font-medium text-red-700">
          {error}
        </div>
      )}

      <div className="mt-4 grid grid-cols-2 gap-3 sm:gap-4 lg:gap-5">
        {loading
          ? Array.from({ length: 6 }).map((_, index) => (
              <div key={index} className="h-[280px] animate-pulse rounded-[20px] border border-slate-200 bg-white shadow-[0_8px_24px_rgba(0,0,0,0.04)]">
                <div className="h-[120px] rounded-t-[20px] bg-slate-200 sm:h-[200px]" />
                <div className="space-y-3 p-4">
                  <div className="h-3 w-1/2 rounded bg-slate-200" />
                  <div className="h-4 w-4/5 rounded bg-slate-200" />
                  <div className="h-3 w-full rounded bg-slate-200" />
                </div>
              </div>
            ))
          : destinations.map((destination, index) => (
              <DestinationCard
                key={destination.id}
                destination={destination}
                eagerImage={index === 0}
              />
            ))}
      </div>

      {!loading && !error && destinations.length === 0 && (
        <div className="mt-6 rounded-2xl border border-dashed border-slate-300 bg-white px-5 py-8 text-center">
          <h3 className="text-base font-bold text-slate-900">Belum ada destinasi yang cocok</h3>
          <p className="mt-2 text-sm text-slate-500">
            Coba longgarkan budget, rating, atau radius jarak untuk melihat rekomendasi lain.
          </p>
        </div>
      )}

      {totalPages > 1 && (
        <div className="mt-7 flex items-center justify-center gap-2">
          {visiblePages.map((item) => (
            <button
              key={item}
              type="button"
              onClick={() => onPageChange(item)}
              className={`h-9 min-w-9 rounded-full text-sm font-semibold ${
                item === page
                  ? 'bg-[#0E75BC] text-white'
                  : 'border border-[#D9E8F3] bg-white text-[#23689A]'
              }`}
            >
              {item}
            </button>
          ))}
        </div>
      )}
    </section>
  );
}

export function ExplorePageContent() {
  const [isFilterOpen, setIsFilterOpen] = useState(false);
  const [filters, setFilters] = useState<ExploreFilters>(DEFAULT_FILTERS);
  const [destinations, setDestinations] = useState<ExploreDestination[]>([]);
  const [filterMetadata, setFilterMetadata] = useState<ExploreFilterMetadata | null>(null);
  const [meta, setMeta] = useState<ExploreMeta>(DEFAULT_META);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [locationLoading, setLocationLoading] = useState(false);
  const [locationMessage, setLocationMessage] = useState<string | null>(null);
  const [debouncedSearch, flushSearch] = useDebouncedValue(filters.search, 400);
  const [debouncedCustomMaxPrice] = useDebouncedValue(filters.customMaxPrice, 500);
  const [debouncedPlannedTime] = useDebouncedValue(filters.plannedTime, 300);
  const {
    intent,
    budget,
    radiusKm,
    dayType,
    minRating,
    childFriendly,
    openNow,
    userLat,
    userLng,
    sort,
  } = filters;

  useEffect(() => {
    let active = true;
    const timeoutId = window.setTimeout(() => {
      const storedLocation = readStoredLocation();
      const restoredFilters = {
        ...DEFAULT_FILTERS,
        ...storedLocation,
      };

      if (!active || !hasUserLocation(restoredFilters)) return;
      setFilters((prev) => {
        if (hasUserLocation(prev)) return prev;
        return { ...prev, ...storedLocation };
      });
      setLocationMessage('Lokasi tersedia dari sesi browser ini.');
    }, 0);

    return () => {
      active = false;
      window.clearTimeout(timeoutId);
    };
  }, []);

  useEffect(() => {
    let active = true;
    destinationsService
      .getExploreFilters()
      .then((data) => {
        if (active) setFilterMetadata(data);
      })
      .catch(() => {
        if (active) setFilterMetadata(null);
      });
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    let active = true;
    const timeoutId = window.setTimeout(() => {
      const queryFilters: ExploreFilters = {
        ...DEFAULT_FILTERS,
        search: debouncedSearch,
        intent,
        budget,
        customMaxPrice: debouncedCustomMaxPrice,
        radiusKm,
        dayType,
        plannedTime: debouncedPlannedTime,
        minRating,
        childFriendly,
        openNow,
        userLat,
        userLng,
        sort,
      };

      setLoading(true);
      setError(null);
      destinationsService
        .getExplore(buildExploreParams(queryFilters, page))
        .then((result) => {
          if (!active) return;
          setDestinations(result.data);
          setMeta(result.meta);
        })
        .catch((fetchError: Error) => {
          if (!active) return;
          setError(fetchError.message || 'Gagal mengambil rekomendasi wisata.');
          setDestinations([]);
          setMeta(DEFAULT_META);
        })
        .finally(() => {
          if (active) setLoading(false);
        });
    }, 0);

    return () => {
      active = false;
      window.clearTimeout(timeoutId);
    };
  }, [
    page,
    debouncedSearch,
    debouncedCustomMaxPrice,
    debouncedPlannedTime,
    intent,
    budget,
    radiusKm,
    dayType,
    minRating,
    childFriendly,
    openNow,
    userLat,
    userLng,
    sort,
  ]);

  const updateFilters = (patch: Partial<ExploreFilters>) => {
    setError(null);
    setPage(1);
    setFilters((prev) => ({ ...prev, ...patch }));
  };

  const resetFilters = () => {
    setError(null);
    const resetValue = {
      ...DEFAULT_FILTERS,
      userLat: filters.userLat,
      userLng: filters.userLng,
    };
    setFilters(resetValue);
    setPage(1);
  };

  const requestLocation = () => {
    if (!navigator.geolocation) {
      setLocationMessage('Browser kamu belum mendukung akses lokasi.');
      return;
    }

    setLocationLoading(true);
    setLocationMessage('Meminta izin lokasi dari browser...');
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const nextLocation = {
          userLat: position.coords.latitude,
          userLng: position.coords.longitude,
          radiusKm: filters.radiusKm || 10,
          sort: 'nearest' as const,
        };
        window.sessionStorage.setItem(
          'muterbandung_location',
          JSON.stringify({ lat: nextLocation.userLat, lng: nextLocation.userLng }),
        );
        updateFilters(nextLocation);
        setLocationLoading(false);
        setLocationMessage('Lokasi aktif. Hasil bisa diurutkan berdasarkan jarak terdekat.');
      },
      () => {
        setLocationLoading(false);
        setLocationMessage('Lokasi tidak diizinkan. Rekomendasi umum tetap bisa digunakan.');
      },
      {
        enableHighAccuracy: true,
        maximumAge: 300000,
        timeout: 10000,
      },
    );
  };

  const selectIntent = (intent: string | null) => {
    updateFilters({
      intent,
      sort: hasUserLocation(filters) && filters.sort === 'nearest' ? 'nearest' as const : 'quality' as const,
      radiusKm: intent === null ? null : filters.radiusKm,
    });
  };

  const submitSearch = () => {
    setError(null);
    setPage(1);
    flushSearch();
  };

  const changePage = (nextPage: number) => {
    if (nextPage === page) return;
    setError(null);
    setPage(nextPage);
    document.getElementById('destinations')?.scrollIntoView({ behavior: 'smooth' });
  };

  const nearbyActive = filters.sort === 'nearest' && hasUserLocation(filters);

  return (
    <main id="planner" className="mx-auto w-full max-w-[1180px] overflow-x-hidden px-4 py-6 sm:px-8">
      <PlannerHero
        searchValue={filters.search}
        onSearchChange={(search) => updateFilters({ search })}
        onSubmit={submitSearch}
        onNearby={requestLocation}
      />

      <div className="mb-2 mt-5">
        <RecommendationBanner />
      </div>

      <div className="pointer-events-none sticky top-0 z-30 -mx-4 space-y-3 px-4 pb-2 pt-4 sm:mx-0 sm:px-0">
        <div className="pointer-events-auto">
          <CategoryChips
            metadata={filterMetadata}
            activeIntent={filters.intent}
            nearbyActive={nearbyActive}
            onSelectIntent={selectIntent}
            onNearby={requestLocation}
          />
        </div>
        <div className="pointer-events-auto lg:hidden">
          <button
            type="button"
            onClick={() => setIsFilterOpen(true)}
            className="flex w-full items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white py-3 text-[14px] font-bold text-slate-700 shadow-md"
          >
            <Filter className="h-4 w-4" />
            Sesuaikan Hasil Rekomendasi
          </button>
        </div>
      </div>

      <div className="mt-0 grid gap-6 lg:mt-2 lg:grid-cols-[280px_minmax(0,1fr)]">
        <ResultsSummary
          isOpen={isFilterOpen}
          onClose={() => setIsFilterOpen(false)}
          filters={filters}
          onChange={updateFilters}
          onReset={resetFilters}
          onUseLocation={requestLocation}
          hasLocation={hasUserLocation(filters)}
          locationMessage={locationMessage}
          locationLoading={locationLoading}
        />
        <DestinationGrid
          destinations={destinations}
          loading={loading}
          error={error}
          meta={meta}
          page={page}
          onPageChange={changePage}
        />
      </div>
    </main>
  );
}
