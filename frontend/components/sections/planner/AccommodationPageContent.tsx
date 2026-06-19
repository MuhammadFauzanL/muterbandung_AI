"use client";

import { useEffect, useMemo, useState } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import { usePlanner } from '@/context/PlannerContext';
import { SafeImage } from '@/components/ui/SafeImage';
import { accommodationsService } from '@/services/accommodations';
import type { Accommodation, AccommodationFilterMetadata, AccommodationMeta } from '@/types';
import { MapPin, Star, Sparkles, Wallet, Search, X } from 'lucide-react';

type AccommodationFiltersState = {
  search: string;
  type: string | null;
  budget: 'under_250000' | 'under_500000' | 'under_1000000' | null;
  minRating: number | null;
  facility: string | null;
  sort: 'recommended' | 'nearest' | 'rating' | 'reviews' | 'price_low' | 'price_high';
};

const DEFAULT_META: AccommodationMeta = {
  page: 1,
  limit: 12,
  total: 0,
  totalPages: 0,
};

const DEFAULT_FILTERS: AccommodationFiltersState = {
  search: '',
  type: null,
  budget: null,
  minRating: null,
  facility: null,
  sort: 'recommended',
};

const BUDGET_OPTIONS: Array<{ label: string; value: AccommodationFiltersState['budget']; maxPrice?: number }> = [
  { label: '< 250k', value: 'under_250000', maxPrice: 250000 },
  { label: '< 500k', value: 'under_500000', maxPrice: 500000 },
  { label: '< 1jt', value: 'under_1000000', maxPrice: 1000000 },
];

function getMaxPrice(budget: AccommodationFiltersState['budget']) {
  return BUDGET_OPTIONS.find((item) => item.value === budget)?.maxPrice;
}

function useDebouncedValue<T>(value: T, delayMs: number): T {
  const [debouncedValue, setDebouncedValue] = useState(value);
  useEffect(() => {
    const timeoutId = window.setTimeout(() => setDebouncedValue(value), delayMs);
    return () => window.clearTimeout(timeoutId);
  }, [value, delayMs]);
  return debouncedValue;
}


function AccommodationTypeChips({
  filters,
  metadata,
  onChange,
  onReset,
}: {
  filters: AccommodationFiltersState;
  metadata: AccommodationFilterMetadata | null;
  onChange: (patch: Partial<AccommodationFiltersState>) => void;
  onReset: () => void;
}) {
  return (
    <div className="flex flex-nowrap sm:flex-wrap gap-2 overflow-x-auto pb-1 scrollbar-hide">
      <button
        type="button"
        onClick={onReset}
        className={`shrink-0 rounded-full border px-5 py-2 text-[13px] font-medium transition-colors ${
          !filters.type && !filters.budget && !filters.minRating && !filters.facility
            ? 'border-[#0E75BC] bg-[#0E75BC] text-white shadow-sm'
            : 'border-[#E1EEF6] bg-white text-[#23689A] hover:border-[#0E75BC] hover:text-[#0E75BC] hover:shadow-sm'
        }`}
      >
        Semua Penginapan
      </button>
      {(metadata?.types || []).map((option) => (
        <button
          key={option.value}
          type="button"
          onClick={() => onChange({ type: filters.type === option.value ? null : option.value })}
          className={`shrink-0 rounded-full border px-5 py-2 text-[13px] font-medium transition-colors ${
            filters.type === option.value
              ? 'border-[#0E75BC] bg-[#0E75BC] text-white shadow-sm'
              : 'border-[#E1EEF6] bg-white text-[#23689A] hover:border-[#0E75BC] hover:text-[#0E75BC] hover:shadow-sm'
          }`}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
}

function AccommodationFilterSidebar({
  filters,
  metadata,
  destinationMode,
  onChange,
}: {
  filters: AccommodationFiltersState;
  metadata: AccommodationFilterMetadata | null;
  destinationMode: boolean;
  onChange: (patch: Partial<AccommodationFiltersState>) => void;
}) {
  const facilityOptions = metadata?.facilityOptions.slice(0, 8) || [];

  return (
    <aside className="rounded-[24px] border border-[#E1EEF6] bg-white p-5 shadow-[0_8px_24px_rgba(31,90,145,0.06)]">
      <h2 className="text-[17px] font-bold text-[#143A5C]">Sesuaikan Hasil</h2>
      
      <div className="mt-5 space-y-6">
        {/* Search */}
        <div>
          <label className="flex items-center gap-2 rounded-xl border border-[#DDEAF2] bg-[#F4F9FD] px-3 py-2.5 text-[#476273] focus-within:border-[#0E75BC] focus-within:bg-white transition-colors">
            <Search className="h-4 w-4 shrink-0" />
            <input
              type="search"
              placeholder="Cari penginapan..."
              value={filters.search}
              onChange={(event) => onChange({ search: event.target.value })}
              className="min-w-0 flex-1 bg-transparent text-[13px] text-[#202B37] outline-none placeholder:text-[#7B8B99]"
            />
          </label>
        </div>

        {/* Urutkan */}
        <div>
          <h3 className="mb-3 text-[11px] font-bold uppercase tracking-[0.08em] text-[#7B8B99]">Urutkan</h3>
          <div className="grid grid-cols-2 gap-2">
            {[
              { label: 'Rekomendasi', value: 'recommended' },
              ...(destinationMode ? [{ label: 'Terdekat', value: 'nearest' }] : []),
              { label: 'Rating', value: 'rating' },
              { label: 'Ulasan', value: 'reviews' },
              { label: 'Termurah', value: 'price_low' },
            ].map((opt) => (
              <button
                key={opt.value}
                type="button"
                onClick={() => onChange({ sort: opt.value as AccommodationFiltersState['sort'] })}
                className={`flex items-center justify-center rounded-xl border py-2 px-2 text-[12px] font-medium transition-colors ${
                  filters.sort === opt.value
                    ? 'border-[#0E75BC] bg-[#F4F9FD] text-[#0E75BC]'
                    : 'border-[#E1EEF6] bg-white text-[#476273] hover:border-[#0E75BC] hover:text-[#0E75BC]'
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        {/* Budget */}
        <div>
          <h3 className="mb-3 text-[11px] font-bold uppercase tracking-[0.08em] text-[#7B8B99]">Budget per malam</h3>
          <div className="grid grid-cols-2 gap-2">
            {BUDGET_OPTIONS.map((opt) => (
              <button
                key={opt.value!}
                type="button"
                onClick={() => onChange({ budget: filters.budget === opt.value ? null : opt.value })}
                className={`flex items-center justify-center rounded-xl border py-2 px-2 text-[12px] font-medium transition-colors ${
                  filters.budget === opt.value
                    ? 'border-[#0E75BC] bg-[#F4F9FD] text-[#0E75BC]'
                    : 'border-[#E1EEF6] bg-white text-[#476273] hover:border-[#0E75BC] hover:text-[#0E75BC]'
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        {/* Rating */}
        <div>
          <h3 className="mb-3 text-[11px] font-bold uppercase tracking-[0.08em] text-[#7B8B99]">Minimal Rating</h3>
          <div className="flex gap-2">
            {[{label: '3+', value: 3}, {label: '4+', value: 4}, {label: '4.5+', value: 4.5}].map((opt) => (
              <button
                key={opt.value}
                type="button"
                onClick={() => onChange({ minRating: filters.minRating === opt.value ? null : opt.value })}
                className={`flex flex-1 items-center justify-center gap-1.5 rounded-xl border py-2 text-[12px] font-medium transition-colors ${
                  filters.minRating === opt.value
                    ? 'border-[#0E75BC] bg-[#F4F9FD] text-[#0E75BC]'
                    : 'border-[#E1EEF6] bg-white text-[#476273] hover:border-[#0E75BC] hover:text-[#0E75BC]'
                }`}
              >
                {opt.label}
                <Star className={`h-[12px] w-[12px] ${filters.minRating === opt.value ? 'text-[#0E75BC]' : 'text-[#F59E0B]'}`} fill="currentColor" />
              </button>
            ))}
          </div>
        </div>

        {/* Fasilitas */}
        {facilityOptions.length > 0 && (
          <div>
            <h3 className="mb-3 text-[11px] font-bold uppercase tracking-[0.08em] text-[#7B8B99]">Fasilitas</h3>
            <div className="flex flex-wrap gap-2">
              {facilityOptions.map((facility) => (
                <button
                  key={facility}
                  type="button"
                  onClick={() => onChange({ facility: filters.facility === facility ? null : facility })}
                  className={`rounded-full border px-4 py-1.5 text-[12px] font-medium transition-colors ${
                    filters.facility === facility
                      ? 'border-[#0E75BC] bg-[#F4F9FD] text-[#0E75BC]'
                      : 'border-[#E1EEF6] bg-white text-[#476273] hover:border-[#0E75BC] hover:text-[#0E75BC]'
                  }`}
                >
                  {facility}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </aside>
  );
}

function AccommodationCard({
  accommodation,
  onSelect,
  eagerImage = false,
}: {
  accommodation: Accommodation;
  onSelect: (acc: Accommodation) => void;
  eagerImage?: boolean;
}) {
  return (
    <article className="grid overflow-hidden rounded-[14px] border border-[#DDEAF2] bg-white shadow-[0_10px_26px_rgba(17,73,112,0.06)] md:grid-cols-[220px_minmax(0,1fr)]">
      <div className="relative min-h-[190px]">
        <SafeImage
          src={accommodation.image}
          alt={accommodation.name}
          fill
          loading={eagerImage ? 'eager' : 'lazy'}
          sizes="(min-width: 768px) 220px, 100vw"
          className="object-cover"
          category={accommodation.type || accommodation.category}
        />
        <span className="absolute left-3 top-3 rounded-full bg-white/92 px-3 py-1 text-[11px] font-semibold text-[#176E9E] shadow-sm">
          {accommodation.type || 'Penginapan'}
        </span>
      </div>

      <div className="min-w-0 p-3 sm:p-4">
        <div className="flex justify-between items-start gap-3">
          <div className="min-w-0">
            <h2 className="text-[17px] font-semibold leading-6 text-[#202B37]">
              {accommodation.name}
            </h2>
            <div className="mt-1.5 flex flex-wrap items-center gap-x-3 gap-y-1 text-[12px] text-[#6A7E8E]">
              <span className="inline-flex items-center gap-1">
                <MapPin className="h-4 w-4" />
                {accommodation.location}
              </span>
              <span>{accommodation.distance}</span>
            </div>
          </div>

          <div className="shrink-0 rounded-[10px] bg-[#FFF7E8] px-2.5 py-1.5 text-[#7C4F00] text-center">
            <div className="flex items-center justify-center gap-1 text-[12px] font-bold">
              <Star className="h-3.5 w-3.5 fill-current text-[#FBBF24]" />
              {accommodation.rating}
            </div>
            <p className="mt-0.5 text-[9px] font-semibold text-[#9B7840]">
              {accommodation.reviewCount}
            </p>
          </div>
        </div>

        <p className="mt-2 sm:mt-3 text-[12px] sm:text-[13px] leading-5 sm:leading-6 text-[#607382]">
          {accommodation.scoreReason || 'Penginapan aktif dari dataset akomodasi yang diurutkan berdasarkan jarak, rating, ulasan, dan kelengkapan data.'}
        </p>

        <div className="mt-2.5 sm:mt-4 flex flex-wrap gap-2">
          {accommodation.highlights.map((highlight) => (
            <span
              key={highlight}
              className="rounded-full bg-[#EEF7FD] px-3 py-1.5 text-[11px] font-semibold text-[#23689A]"
            >
              {highlight}
            </span>
          ))}
        </div>

        <div className="mt-3 sm:mt-5 flex flex-col gap-2 sm:gap-3 border-t border-[#EDF4F8] pt-3 sm:pt-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-[11px] font-medium text-[#80909D]">Mulai dari</p>
            <p className="text-[18px] font-bold text-[#202B37]">
              {accommodation.price}
            </p>
          </div>
          <button
            type="button"
            onClick={() => onSelect(accommodation)}
            className="inline-flex h-10 items-center justify-center rounded-[10px] bg-[#0E75BC] px-5 text-[12px] font-semibold text-white transition-colors hover:bg-[#095f99]"
          >
            Pilih Penginapan
          </button>
        </div>
      </div>
    </article>
  );
}

function CepotInsight() {
  return (
    <section className="relative overflow-hidden rounded-[16px] sm:rounded-[18px] border border-[#BFE8F0] bg-[#EAF8FB] px-3 py-3 sm:px-5 sm:py-4">
      <div className="relative z-10 flex items-start gap-3">
        <div className="relative h-10 w-10 sm:h-11 sm:w-11 shrink-0 overflow-hidden rounded-full bg-[#D8F0F6] ring-1 ring-white">
          <Image
            src="/images/welcome-cepot.png"
            alt="Cepot AI"
            fill
            sizes="44px"
            className="object-cover object-top"
          />
        </div>
        <div>
          <p className="flex items-center gap-1.5 text-[10px] sm:text-[11px] font-bold uppercase tracking-normal text-[#137CA6]">
            <Sparkles className="h-3 w-3 sm:h-4 sm:w-4" />
            Cepot AI Insight
          </p>
          <p className="mt-1 sm:mt-1.5 text-[12px] leading-5 sm:text-[13px] sm:leading-6 text-[#26485C]">
            Cepot AI mengurutkan penginapan dari jarak, rating, ulasan, harga, fasilitas, dan kelengkapan data agar pilihan istirahatmu lebih relevan.
          </p>
        </div>
      </div>
      <div className="absolute -right-8 bottom-0 h-24 w-24 rounded-full bg-white/35" />
    </section>
  );
}

function TripSidebar() {
  const { destinations, accommodations, removeDestination, removeAccommodation } = usePlanner();
  const router = useRouter();
  const [showToast, setShowToast] = useState(false);

  const handleSave = () => {
    if (accommodations.length === 0) {
      setShowToast(true);
      setTimeout(() => setShowToast(false), 3000);
      return;
    }
    router.push('/planner');
  };

  const totalAccommodationCost = accommodations.reduce((sum, acc) => sum + acc.totalPrice, 0);

  return (
    <aside className="relative rounded-[24px] border border-[#E1EEF6] bg-white p-5 sm:p-6 shadow-[0_8px_24px_rgba(31,90,145,0.06)]">
      {/* Toast Error Notification */}
      <div className={`absolute top-4 left-1/2 -translate-x-1/2 z-50 rounded-2xl border border-red-100 bg-white px-4 py-2.5 text-[13px] font-bold text-red-600 shadow-[0_12px_40px_rgba(0,0,0,0.12)] transition-all duration-300 flex items-center gap-2 whitespace-nowrap ${showToast ? 'opacity-100 translate-y-0' : 'opacity-0 -translate-y-4 pointer-events-none'}`}>
        <div className="flex items-center justify-center w-5 h-5 rounded-full bg-red-100 text-red-600">
          <svg fill="none" viewBox="0 0 24 24" strokeWidth={3} stroke="currentColor" className="w-3 h-3"><path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" /></svg>
        </div>
        Pilih hotel terlebih dahulu!
      </div>

      <h2 className="text-[16px] sm:text-[17px] font-bold text-[#143A5C]">
        Ringkasan Perjalanan
      </h2>

      <div className="mt-4 sm:mt-5 space-y-2.5 sm:space-y-3">
        {destinations.map((dest) => (
          <div key={dest.id} className="flex items-center gap-3 rounded-[14px] bg-[#EEF9FC] px-3.5 py-3 text-[12px] sm:text-[13px] font-semibold text-[#143A5C]">
            <MapPin className="h-4 w-4 shrink-0 text-[#0E75BC]" />
            <span className="flex-1 truncate">{dest.title}</span>
            <button onClick={() => removeDestination(dest.id)} className="shrink-0 text-[#F06161] hover:text-red-700 transition-colors">
              <X className="h-4 w-4" />
            </button>
          </div>
        ))}

        {accommodations.length > 0 ? (
          accommodations.map((acc) => (
            <div key={acc.name} className="flex items-center gap-3 rounded-[14px] bg-[#EEF9FC] px-3.5 py-3 text-[12px] sm:text-[13px] font-semibold text-[#143A5C]">
              <Wallet className="h-4 w-4 shrink-0 text-[#0E75BC]" />
              <span className="flex-1 truncate">{acc.name}</span>
              <button onClick={() => removeAccommodation(acc.name)} className="shrink-0 text-[#F06161] hover:text-red-700 transition-colors">
                <X className="h-4 w-4" />
              </button>
            </div>
          ))
        ) : (
          <div className="flex items-center gap-3 rounded-[14px] border border-[#E1EEF6] bg-white px-3.5 py-3 text-[12px] sm:text-[13px] text-[#7B8B99]">
            <Wallet className="h-4 w-4 shrink-0" />
            <span className="flex-1 truncate">Pilih penginapan...</span>
          </div>
        )}
      </div>

      <dl className="mt-5 space-y-3 border-t border-[#E1EEF6] pt-5 text-[12px] sm:text-[13px]">
        {accommodations.length > 0 ? (
          <>
            <div className="flex items-center justify-between gap-4">
              <dt className="text-[#7B8B99]">Penginapan Dipilih</dt>
              <dd className="font-bold text-[#143A5C]">{accommodations.length} Hotel</dd>
            </div>
            <div className="flex items-center justify-between gap-4">
              <dt className="text-[#7B8B99]">Estimasi Penginapan</dt>
              <dd className="font-bold text-[#0E75BC]">Rp{totalAccommodationCost.toLocaleString('id-ID')}</dd>
            </div>
          </>
        ) : (
          <div className="flex items-center justify-between gap-4">
            <dt className="text-[#7B8B99]">Pilih penginapan untuk melihat estimasi budget.</dt>
          </div>
        )}
      </dl>

      <div className="mt-5 space-y-3">
        <button
          type="button"
          onClick={handleSave}
          className="flex h-[42px] sm:h-[46px] w-full items-center justify-center gap-2 rounded-[14px] bg-[#0E75BC] px-4 text-[13px] sm:text-[14px] font-bold text-white transition-colors hover:bg-[#095f99] shadow-sm"
        >
          Simpan Pilihan
        </button>
        <Link
          href="/planner"
          className="flex h-[42px] sm:h-[46px] w-full items-center justify-center gap-2 rounded-[14px] border-[1.5px] border-[#0E75BC] bg-white px-4 text-[13px] sm:text-[14px] font-bold text-[#0E75BC] transition-colors hover:bg-[#F4F9FD]"
        >
          Kembali ke Planner
        </Link>
      </div>
    </aside>
  );
}

function HotelConfirmationModal({
  isOpen,
  onClose,
  hotel,
}: {
  isOpen: boolean;
  onClose: () => void;
  hotel: Accommodation | null;
}) {
  // Format dates: today and tomorrow
  const today = new Date();
  const tomorrow = new Date(today);
  tomorrow.setDate(tomorrow.getDate() + 1);

  const formatDateForInput = (date: Date) => date.toISOString().split('T')[0];

  const [checkIn, setCheckIn] = useState(formatDateForInput(today));
  const [checkOut, setCheckOut] = useState(formatDateForInput(tomorrow));
  const [guests, setGuests] = useState(2);

  const nights = useMemo(() => {
    const start = new Date(checkIn);
    const end = new Date(checkOut);
    const diffTime = end.getTime() - start.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays > 0 ? diffDays : 1;
  }, [checkIn, checkOut]);

  // Logika 1 Kamar untuk 2 Tamu
  const rooms = Math.ceil(guests / 2);

  const parsedBasePrice = useMemo(() => {
    if (!hotel || !hotel.price) return 0;
    // Extract the first sequence of digits and dots (e.g., "159.288" from "Mulai Rp 159.288/malam")
    const match = hotel.price.match(/[\d\.]+/);
    if (match && match[0]) {
      return parseInt(match[0].replace(/\./g, ''), 10);
    }
    return 0;
  }, [hotel]);
  const basePrice = Number.isFinite(parsedBasePrice) ? parsedBasePrice : 0;
  const totalEstimasi = basePrice * nights * rooms;

  const { addAccommodation } = usePlanner();

  if (!isOpen || !hotel) return null;

  const handleConfirm = () => {
    addAccommodation({
      name: hotel.name,
      basePrice,
      guests,
      rooms,
      nights,
      totalPrice: totalEstimasi,
      checkIn,
      checkOut,
      image: hotel.image,
      rating: hotel.rating ? parseFloat(String(hotel.rating)) : undefined,
      distance: hotel.distance,
      location: hotel.location,
      latitude: hotel.latitude,
      longitude: hotel.longitude,
    });
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 px-4 backdrop-blur-sm transition-all">
      <div className="relative w-full max-w-[420px] overflow-hidden rounded-[20px] bg-white shadow-2xl">
        <button
          onClick={onClose}
          className="absolute right-4 top-4 rounded-full p-2 text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-600"
        >
          <X className="h-4 w-4" />
        </button>

        <div className="p-5 pb-0">
          <h2 className="text-[16px] font-semibold text-[#0E75BC]">
            Konfirmasi Penginapan
          </h2>
          <div className="mt-1 flex flex-wrap items-center gap-x-2 gap-y-1 text-[13px]">
            <span className="font-semibold text-slate-900">{hotel.name}</span>
            <span className="flex items-center gap-1 text-[11px] font-bold text-[#7C4F00]">
              <Star className="h-3.5 w-3.5 fill-current text-[#FBBF24]" /> {hotel.rating}
            </span>
            <span className="hidden sm:inline text-slate-400">•</span>
            <span className="flex items-center gap-1 text-slate-500 text-[11px]">
              <MapPin className="h-3.5 w-3.5" /> {hotel.distance}
            </span>
          </div>
          <p className="mt-2 text-[18px] font-bold text-[#0E75BC]">
            {hotel.price}
          </p>
        </div>

        <div className="p-5">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-[11px] font-medium text-slate-500">Check-in</label>
              <input
                type="date"
                value={checkIn}
                onChange={(e) => setCheckIn(e.target.value)}
                className="w-full rounded-[8px] border border-slate-200 px-2.5 py-1.5 text-[13px] text-slate-900 outline-none focus:border-[#0E75BC]"
              />
            </div>
            <div>
              <label className="mb-1 block text-[11px] font-medium text-slate-500">Check-out</label>
              <input
                type="date"
                value={checkOut}
                onChange={(e) => setCheckOut(e.target.value)}
                className="w-full rounded-[8px] border border-slate-200 px-2.5 py-1.5 text-[13px] text-slate-900 outline-none focus:border-[#0E75BC]"
              />
            </div>
          </div>

          <div className="my-3 flex items-center justify-center">
            <div className="rounded-full bg-[#0E75BC] px-3 py-1 text-[10px] font-semibold text-white shadow-sm">
              {nights + 1} Hari {nights} Malam
            </div>
          </div>

          <div className="flex items-center justify-between rounded-[10px] bg-slate-50 p-3 border border-slate-100">
            <div>
              <p className="text-[12px] font-semibold text-slate-900">Jumlah Orang</p>
              <p className="text-[10px] text-slate-500">Dewasa / Anak</p>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={() => setGuests(Math.max(1, guests - 1))}
                className="flex h-7 w-7 items-center justify-center rounded-full border border-slate-300 bg-white text-slate-600 transition-colors hover:bg-slate-100"
              >
                -
              </button>
              <span className="w-3 text-center text-[13px] font-semibold text-slate-900">{guests}</span>
              <button
                onClick={() => setGuests(guests + 1)}
                className="flex h-7 w-7 items-center justify-center rounded-full bg-[#0E75BC] text-white transition-colors hover:bg-[#095f99]"
              >
                +
              </button>
            </div>
          </div>

          <div className="mt-4 rounded-[10px] border border-[#BFE8F0] bg-[#EAF8FB] p-3 flex gap-2.5">
            <div className="mt-0.5 text-[#137CA6]"><Sparkles className="h-3.5 w-3.5" /></div>
            <p className="text-[11px] leading-4 text-[#26485C]">
              <strong className="text-[#137CA6]">Cepot AI:</strong> &quot;Dengan {guests} tamu, kamu membutuhkan <strong>{rooms} kamar</strong>. Durasi menginap ini direkomendasikan agar seluruh destinasi dalam itinerary dapat dikunjungi dengan nyaman.&quot;
            </p>
          </div>

          <div className="mt-5 border-t border-slate-100 pt-4">
            <div className="space-y-2.5 text-[12px]">
              <div className="flex justify-between text-slate-600">
                <span>{hotel.name} ({nights} Mlm, {rooms} Kmr)</span>
                <span className="font-medium text-slate-900">Rp{(basePrice * nights * rooms).toLocaleString('id-ID')}</span>
              </div>
              <div className="flex justify-between text-slate-600">
                <span>Layanan & Fasilitas ({guests} Tamu)</span>
                <span className="font-medium text-emerald-600">Termasuk</span>
              </div>
              <div className="flex justify-between text-slate-600">
                <span>Pajak (AI Smart Optimized)</span>
                <span className="font-medium text-slate-900">Rp0</span>
              </div>
            </div>

            <div className="mt-3 flex items-center justify-between border-t border-slate-100 pt-3">
              <span className="text-[14px] font-bold text-[#0E75BC]">Total Estimasi</span>
              <span className="text-[18px] font-bold text-[#0E75BC]">Rp{totalEstimasi.toLocaleString('id-ID')}</span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2 border-t border-slate-100 p-5 bg-slate-50/50">
          <button
            onClick={onClose}
            className="flex-1 rounded-[10px] px-3 py-2.5 text-[13px] font-semibold text-slate-600 transition-colors hover:bg-slate-100"
          >
            Batal
          </button>
          <button
            onClick={handleConfirm}
            className="flex-[2] rounded-[10px] bg-[#0E75BC] px-3 py-2.5 text-[13px] font-semibold text-white transition-colors hover:bg-[#095f99] shadow-sm"
          >
            Tambahkan ke Perjalanan
          </button>
        </div>
      </div>
    </div>
  );
}



export function AccommodationPageContent() {
  const searchParams = useSearchParams();
  const destinationSlug = searchParams.get('destination');
  const destinationMode = Boolean(destinationSlug);
  const [selectedHotel, setSelectedHotel] = useState<Accommodation | null>(null);
  const [filters, setFilters] = useState<AccommodationFiltersState>(() => ({
    ...DEFAULT_FILTERS,
    // Auto-set sort to 'nearest' when coming from planner with a destination
    sort: destinationSlug ? 'nearest' : 'recommended',
  }));
  const [filterMetadata, setFilterMetadata] = useState<AccommodationFilterMetadata | null>(null);
  const [accommodations, setAccommodations] = useState<Accommodation[]>([]);
  const [meta, setMeta] = useState<AccommodationMeta>(DEFAULT_META);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Debounce search input to prevent API spam per keystroke
  const debouncedSearch = useDebouncedValue(filters.search, 400);

  useEffect(() => {
    let active = true;
    accommodationsService
      .getFilters()
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
    setLoading(true);
    setError(null);

    const params = {
      page: 1,
      limit: 12,
      search: debouncedSearch.trim() || undefined,
      type: filters.type,
      maxPrice: getMaxPrice(filters.budget),
      minRating: filters.minRating ?? undefined,
      facilities: filters.facility ? [filters.facility] : undefined,
      radiusKm: destinationMode ? 10 : undefined,
      sort: filters.sort,
    };

    const request = destinationSlug
      ? accommodationsService.getNearbyForDestination(destinationSlug, params)
      : accommodationsService.getAll(params);

    request
      .then((result) => {
        if (!active) return;
        setAccommodations(result.data);
        setMeta(result.meta);
      })
      .catch((fetchError: Error) => {
        if (!active) return;
        setError(fetchError.message || 'Gagal mengambil rekomendasi penginapan.');
        setAccommodations([]);
        setMeta(DEFAULT_META);
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [destinationSlug, destinationMode, debouncedSearch, filters.type, filters.budget, filters.minRating, filters.facility, filters.sort]);

  const updateFilters = (patch: Partial<AccommodationFiltersState>) => {
    setFilters((prev) => ({ ...prev, ...patch }));
  };

  const resetFilters = () => {
    setFilters(DEFAULT_FILTERS);
  };

  return (
    <main className="mx-auto max-w-[1180px] px-4 py-4 sm:py-6 sm:px-8">
      {/* Page Header */}
      <div className="mb-4 sm:mb-6">
        <h1 className="text-[24px] font-semibold leading-tight text-[#202B37] sm:text-[34px]">
          Pilih Penginapan
        </h1>
        <p className="mt-1 text-[13px] text-[#7B8B99]">
          {destinationMode
            ? 'Menampilkan penginapan terdekat dari destinasi wisata pilihanmu.'
            : 'Temukan penginapan terbaik untuk perjalananmu di Bandung.'}
        </p>
      </div>

      {/* Type Chips — full width, sticky like explore CategoryChips */}
      <div className="pointer-events-none sticky top-0 z-30 -mx-4 px-4 pb-2 pt-4 sm:mx-0 sm:px-0">
        <div className="pointer-events-auto">
          <AccommodationTypeChips
            filters={filters}
            metadata={filterMetadata}
            onChange={updateFilters}
            onReset={resetFilters}
          />
        </div>
      </div>

      {/* 2-column grid: Filter Sidebar + Content — same as explore */}
      <div className="mt-0 grid gap-6 lg:mt-2 lg:grid-cols-[280px_minmax(0,1fr)]">
        {/* Left Sidebar: Trip Summary First, then Filters (hidden on mobile, sticky on desktop) */}
        <div className="hidden lg:flex lg:flex-col lg:gap-5 lg:sticky lg:top-16 lg:self-start lg:max-h-[calc(100vh-4rem)] lg:overflow-y-auto lg:pb-6 scrollbar-hide">
          {/* Trip Summary at the TOP for clear visibility */}
          <TripSidebar />

          <AccommodationFilterSidebar
            filters={filters}
            metadata={filterMetadata}
            destinationMode={destinationMode}
            onChange={updateFilters}
          />
        </div>

        {/* Main Content Column */}
        <div className="min-w-0 space-y-5">
          {/* Cepot AI Insight */}
          <CepotInsight />

          {/* Trip Summary — visible only on mobile, above hotel list */}
          <div className="lg:hidden">
            <TripSidebar />
          </div>

          {/* Hotel List */}
          <section>
            <div className="mb-4">
              <h2 className="text-[18px] sm:text-[22px] font-bold text-[#143A5C]">
                {destinationMode ? 'Penginapan Terdekat dari Wisata Pilihan' : 'Rekomendasi terbaik di Bandung'}
              </h2>
              <p className="mt-1 text-[13px] text-[#7B8B99]">
                {loading
                  ? 'Memuat data penginapan aktif...'
                  : `Ditemukan ${meta.total} tempat dari data aktif.`}
              </p>
            </div>

            <div className="space-y-4">
              {loading && [...Array(4)].map((_, index) => (
                <div key={index} className="h-[220px] animate-pulse rounded-[14px] border border-slate-100 bg-slate-100" />
              ))}
              {!loading && error && (
                <div className="rounded-[14px] border border-red-100 bg-red-50 p-4 text-[13px] font-semibold text-red-600">
                  {error}
                </div>
              )}
              {!loading && !error && accommodations.length === 0 && (
                <div className="rounded-[14px] border border-dashed border-slate-200 bg-white p-6 text-center text-[13px] leading-6 text-slate-500">
                  Belum ada penginapan yang cocok dengan filter ini.<br />
                  Coba sesuaikan budget, rating, atau hapus pencarian.
                </div>
              )}
              {!loading && !error && accommodations.map((accommodation, index) => (
                <AccommodationCard
                  key={accommodation.id}
                  accommodation={accommodation}
                  onSelect={(acc) => setSelectedHotel(acc)}
                  eagerImage={index === 0}
                />
              ))}
            </div>
          </section>
        </div>
      </div>

      <HotelConfirmationModal
        isOpen={!!selectedHotel}
        onClose={() => setSelectedHotel(null)}
        hotel={selectedHotel}
      />
    </main>
  );
}
