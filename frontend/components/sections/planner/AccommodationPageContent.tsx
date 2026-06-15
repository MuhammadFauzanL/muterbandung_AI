"use client";

import { useState, useMemo } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { usePlanner } from '@/context/PlannerContext';
import { MapPin, Star, Sparkles, Calendar, Users, Wallet, Check, Search, ArrowLeft, X } from 'lucide-react';

type AccommodationOption = {
  name: string;
  type: string;
  location: string;
  distance: string;
  price: string;
  rating: string;
  reviewCount: string;
  description: string;
  image: string;
  highlights: readonly string[];
};

const ACCOMMODATIONS: readonly AccommodationOption[] = [
  {
    name: 'Bobocabin Ranca Upas',
    type: 'Cabin Alam',
    location: 'Ranca Upas, Ciwidey',
    distance: '2.4 km dari Kawah Putih',
    price: 'Rp520.000',
    rating: '4.8',
    reviewCount: '1.284 ulasan',
    description:
      'Cabin ringkas di area hutan pinus dengan akses cepat ke Ranca Upas dan jalur wisata Ciwidey.',
    image:
      'https://lh3.googleusercontent.com/gps-proxy/ALd4DhFQNQ81Dicl74zu40V7aXYY50dw0TH-lPCwm_rFUokItvPcAB2TR0TclWJS-39WNWfCJ_04IFMGsytAfz0mjmiv_2ft5DRYmyE0tyFhO6Q8WM81wJqxKvqNiKtB-0VBqYxss31T3exO_FUzUlc3d9J0f-idvXZvvVAfRhO6qZKDrOa9ali32Kou7Q=w455-h240-k-no',
    highlights: ['Dekat rute', 'View alam', 'Cocok pasangan'],
  },
  {
    name: 'Patuha Resort Ciwidey',
    type: 'Resort Keluarga',
    location: 'Sugihmukti, Pasirjambu',
    distance: '4.8 km dari Kawah Putih',
    price: 'Rp680.000',
    rating: '4.7',
    reviewCount: '842 ulasan',
    description:
      'Resort tenang dengan kamar keluarga, sarapan, dan area terbuka untuk istirahat setelah itinerary.',
    image:
      'https://lh3.googleusercontent.com/gps-cs-s/APNQkAEINPwRItiBa-w5a0baJmuuVumrV1ITN9jwyT2p_96DgsCe35Dr2WyED9858FVbmDDGeJUrv6XUoVepQsIyDRLiAvtNCd4UAVn0xPqFRYuSGP18ysRAcxChgCiuIN1WNCALULfvPQ=w416-h240-k-no',
    highlights: ['Sarapan', 'Kamar keluarga', 'Parkir luas'],
  },
  {
    name: 'Grand Sunshine Resort',
    type: 'Hotel Resort',
    location: 'Soreang, Bandung',
    distance: '18 km dari Kawah Putih',
    price: 'Rp850.000',
    rating: '4.9',
    reviewCount: '2.310 ulasan',
    description:
      'Pilihan paling nyaman untuk keluarga, dengan fasilitas lengkap dan akses balik ke Bandung yang mudah.',
    image:
      'https://lh3.googleusercontent.com/gps-cs-s/APNQkAHxUtQnsZfq1a1PWc2Y6__0XQVrIoI02cEtMtgkyOIKky2YGBLrfIqc6taBfnqP3D3gKeLiK2E4uxMLcgSy9GLOomkjEiV0tlVOH351NfYOeTxbBhjeDuELrIWzHnLMX1t5gwvCbhz1tjOO=w422-h240-k-no',
    highlights: ['Kolam renang', 'Restoran', 'Akses kota'],
  },
] as const;

const FILTERS = ['Semua', 'Dekat Kawah Putih', 'Family stay', 'Cabin', 'Budget hemat'];




function AccommodationFilters() {
  const [activeFilter, setActiveFilter] = useState<string | null>('Semua');

  return (
    <section className="rounded-[16px] border border-slate-200 bg-white p-3 sm:p-4 shadow-sm">
      <label className="flex h-10 sm:h-12 items-center gap-2 rounded-xl border border-slate-200 bg-white px-3 text-slate-500 focus-within:border-[#0E75BC] transition-colors">
        <Search className="h-4 w-4" />
        <span className="sr-only">Cari penginapan</span>
        <input
          type="search"
          placeholder="Cari area atau nama penginapan"
          className="min-w-0 flex-1 bg-transparent text-[13px] sm:text-[14px] text-slate-800 outline-none placeholder:text-slate-400"
        />
      </label>

      <div className="mt-3 sm:mt-4 flex flex-nowrap sm:flex-wrap gap-2 overflow-x-auto pb-1 sm:pb-0 scrollbar-hide">
        {FILTERS.map((filter, index) => (
          <button
            key={filter}
            type="button"
            onClick={() => setActiveFilter(activeFilter === filter ? null : filter)}
            className={`shrink-0 sm:shrink rounded-full border px-4 py-2 sm:px-5 sm:py-2.5 text-[12px] sm:text-[13px] font-medium transition-colors ${
              activeFilter === filter
                ? 'border-[#0E75BC] bg-[#F4F9FD] text-[#0E75BC]'
                : 'border-slate-200 bg-white text-slate-600 hover:border-[#0E75BC] hover:text-[#0E75BC]'
            }`}
          >
            {filter}
          </button>
        ))}
      </div>
    </section>
  );
}

function AccommodationCard({
  accommodation,
  onSelect,
  eagerImage = false,
}: {
  accommodation: AccommodationOption;
  onSelect: (acc: AccommodationOption) => void;
  eagerImage?: boolean;
}) {
  return (
    <article className="grid overflow-hidden rounded-[14px] border border-[#DDEAF2] bg-white shadow-[0_10px_26px_rgba(17,73,112,0.06)] md:grid-cols-[220px_minmax(0,1fr)]">
      <div className="relative min-h-[190px]">
        <Image
          src={accommodation.image}
          alt={accommodation.name}
          fill
          loading={eagerImage ? 'eager' : 'lazy'}
          sizes="(min-width: 768px) 220px, 100vw"
          className="object-cover"
        />
        <span className="absolute left-3 top-3 rounded-full bg-white/92 px-3 py-1 text-[11px] font-semibold text-[#176E9E] shadow-sm">
          {accommodation.type}
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
          {accommodation.description}
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
              <span className="text-[11px] font-semibold text-[#7B8B99]">
                {' '}
                / malam
              </span>
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
            Cepot AI menemukan 3 penginapan terbaik di sekitar destinasi yang kamu pilih, semuanya punya rating tinggi dan cocok untuk istirahat setelah berkeliling Ciwidey!
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
    <aside className="relative rounded-[16px] border border-[#DCEAF3] bg-white p-3 sm:p-5 shadow-[0_10px_28px_rgba(17,73,112,0.07)]">
      {/* Toast Error Notification */}
      <div className={`absolute top-4 left-1/2 -translate-x-1/2 z-50 rounded-2xl border border-red-100 bg-white px-4 py-2.5 text-[13px] font-bold text-red-600 shadow-[0_12px_40px_rgba(0,0,0,0.12)] transition-all duration-300 flex items-center gap-2 whitespace-nowrap ${showToast ? 'opacity-100 translate-y-0' : 'opacity-0 -translate-y-4 pointer-events-none'}`}>
        <div className="flex items-center justify-center w-5 h-5 rounded-full bg-red-100 text-red-600">
          <svg fill="none" viewBox="0 0 24 24" strokeWidth={3} stroke="currentColor" className="w-3 h-3"><path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" /></svg>
        </div>
        Pilih hotel terlebih dahulu!
      </div>

      <h2 className="text-[14px] sm:text-[15px] font-semibold text-[#202B37]">
        Ringkasan Perjalanan
      </h2>

      <div className="mt-3 sm:mt-4 space-y-2 sm:space-y-2.5">
        {destinations.map((dest) => (
          <div key={dest.id} className="flex items-center gap-2 rounded-[8px] sm:rounded-[10px] bg-[#EAF8FB] px-2.5 py-2 sm:px-3 sm:py-2.5 text-[11px] sm:text-[12px] font-semibold text-[#246983]">
            <MapPin className="h-3 w-3 sm:h-4 sm:w-4 text-[#0E75BC]" />
            <span className="flex-1">{dest.title}</span>
            <button onClick={() => removeDestination(dest.id)} className="text-red-400 hover:text-red-600">
              <X className="h-3 w-3 sm:h-4 sm:w-4" />
            </button>
          </div>
        ))}

        {accommodations.length > 0 ? (
          accommodations.map((acc) => (
            <div key={acc.name} className="flex items-center gap-2 rounded-[8px] sm:rounded-[10px] bg-[#EAF8FB] px-2.5 py-2 sm:px-3 sm:py-2.5 text-[11px] sm:text-[12px] font-semibold text-[#246983]">
              <Wallet className="h-3 w-3 sm:h-4 sm:w-4 text-[#0E75BC]" />
              <span className="flex-1">{acc.name}</span>
              <button onClick={() => removeAccommodation(acc.name)} className="text-red-400 hover:text-red-600">
                <X className="h-3 w-3 sm:h-4 sm:w-4" />
              </button>
            </div>
          ))
        ) : (
          <div className="flex items-center gap-2 rounded-[8px] sm:rounded-[10px] border border-[#E3EEF4] bg-white px-2.5 py-2 sm:px-3 sm:py-2.5 text-[11px] sm:text-[12px] text-[#97A5B1]">
            <Wallet className="h-3 w-3 sm:h-4 sm:w-4" />
            <span className="flex-1">Pilih penginapan...</span>
          </div>
        )}
      </div>

      <dl className="mt-3 sm:mt-5 space-y-1.5 sm:space-y-2.5 border-t border-[#EDF4F8] pt-3 sm:pt-4 text-[11px] sm:text-[12px]">
        {accommodations.length > 0 ? (
          <>
            <div className="flex items-center justify-between gap-4">
              <dt className="text-[#7B8B99]">Penginapan Dipilih</dt>
              <dd className="font-semibold text-[#202B37]">{accommodations.length} Hotel</dd>
            </div>
            <div className="flex items-center justify-between gap-4">
              <dt className="text-[#7B8B99]">Estimasi Penginapan</dt>
              <dd className="font-semibold text-[#0E75BC]">Rp{totalAccommodationCost.toLocaleString('id-ID')}</dd>
            </div>
          </>
        ) : (
          <div className="flex items-center justify-between gap-4">
            <dt className="text-[#7B8B99]">Pilih penginapan untuk melihat estimasi budget.</dt>
          </div>
        )}
      </dl>

      <div className="mt-3 sm:mt-5 space-y-2 sm:space-y-3">
        <button
          type="button"
          onClick={handleSave}
          className="inline-flex h-9 sm:h-11 w-full items-center justify-center gap-2 rounded-[8px] sm:rounded-[10px] bg-[#0E75BC] px-4 text-[12px] sm:text-[13px] font-semibold text-white transition-colors hover:bg-[#095f99] shadow-md"
        >
          Simpan Pilihan
        </button>
        <Link
          href="/planner"
          className="inline-flex h-9 sm:h-11 w-full items-center justify-center gap-2 rounded-[8px] sm:rounded-[10px] border border-[#0E75BC] bg-white px-4 text-[12px] sm:text-[13px] font-semibold text-[#0E75BC] transition-colors hover:bg-[#F2FAFE]"
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
  hotel: AccommodationOption | null;
}) {
  const router = useRouter();

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

  // Extract numeric price from "Rp750.000" string
  const basePrice = hotel ? parseInt(hotel.price.replace(/[^0-9]/g, ''), 10) : 0;
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
      checkOut
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
            {hotel.price} <span className="text-[11px] font-normal text-slate-500">/ malam</span>
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

function AccommodationSidebar() {
  const [isOpen, setIsOpen] = useState(false);
  const [budget, setBudget] = useState<string | null>(null);
  const [types, setTypes] = useState<string[]>([]);
  const [rating, setRating] = useState<string | null>(null);

  const handleBudgetToggle = (val: string) => setBudget(p => p === val ? null : val);
  const handleRatingToggle = (val: string) => setRating(p => p === val ? null : val);

  const handleTypeToggle = (val: string) => setTypes(p => p.includes(val) ? p.filter(t => t !== val) : [...p, val]);

  const handleReset = () => {
    setBudget(null);
    setTypes([]);
    setRating(null);
  };

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div 
          className="fixed inset-0 z-[10000] bg-slate-900/40 backdrop-blur-sm lg:hidden transition-opacity"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Mobile Trigger Button */}
      <div className="lg:hidden">
        <button 
          type="button"
          className="flex w-full items-center justify-center rounded-[16px] border border-slate-200 bg-white p-4 shadow-[0_8px_30px_rgb(0,0,0,0.04)] transition-colors active:bg-slate-50"
          onClick={() => setIsOpen(true)}
        >
          <div className="flex items-center gap-2">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5 text-slate-800">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
            </svg>
            <h2 className="text-[15px] font-bold text-slate-900">
              Sesuaikan Hasil
            </h2>
          </div>
        </button>
      </div>

      {/* Sidebar / Drawer */}
      <aside className={`fixed inset-y-0 left-0 z-[10010] w-[280px] bg-white p-5 shadow-2xl transition-transform lg:static lg:block lg:w-full lg:transform-none lg:rounded-[16px] lg:border lg:border-slate-200 lg:bg-white lg:p-5 lg:shadow-[0_8px_30px_rgb(0,0,0,0.04)] overflow-y-auto ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}`}>
        
        {/* Mobile Drawer Header */}
        <div className="flex items-center justify-between lg:hidden mb-6">
          <h2 className="text-[18px] font-bold text-slate-900">Sesuaikan Hasil</h2>
          <button type="button" onClick={() => setIsOpen(false)} className="rounded-full p-2 text-slate-500 hover:bg-slate-100 transition-colors">
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Desktop Sidebar Header */}
        <div className="hidden lg:flex items-center gap-2 mb-6">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5 text-slate-800">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
          </svg>
          <h2 className="text-[17px] font-bold text-slate-900">
            Sesuaikan Hasil
          </h2>
        </div>

        <form onSubmit={(e) => { e.preventDefault(); setIsOpen(false); }} onReset={handleReset} className="space-y-6">
        <div>
          <h3 className="text-[11px] font-bold uppercase tracking-wider text-[#64748B] mb-3">
            Anggaran
          </h3>
          <div className="space-y-2.5">
            {['< 500rb', '500rb - 1jt', '> 1jt'].map(b => (
              <button
                key={b}
                type="button"
                className="flex w-full items-center gap-3 cursor-pointer text-left group"
                onClick={() => setBudget(budget === b ? null : b)}
              >
                <div className={`w-4 h-4 rounded-full border flex shrink-0 items-center justify-center transition-colors ${budget === b ? 'border-[#0E75BC] bg-[#0E75BC]' : 'border-slate-300 bg-white group-hover:border-[#0E75BC]'}`}>
                  {budget === b && <div className="w-1.5 h-1.5 bg-white rounded-full" />}
                </div>
                <span className="text-[14px] text-slate-700">{b}</span>
              </button>
            ))}
          </div>
        </div>

        <div>
          <h3 className="text-[11px] font-bold uppercase tracking-wider text-[#64748B] mb-3">
            Tipe Properti
          </h3>
          <div className="space-y-2.5">
            {['Hotel', 'Villa', 'Glamping'].map(t => (
              <button
                key={t}
                type="button"
                className="flex w-full items-center gap-3 cursor-pointer text-left group"
                onClick={() => handleTypeToggle(t)}
              >
                <div className={`w-4 h-4 rounded border flex shrink-0 items-center justify-center transition-colors ${types.includes(t) ? 'border-[#0E75BC] bg-[#0E75BC]' : 'border-slate-300 bg-white group-hover:border-[#0E75BC]'}`}>
                  {types.includes(t) && (
                    <svg className="w-[10px] h-[10px] text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}><path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" /></svg>
                  )}
                </div>
                <span className="text-[14px] text-slate-700">{t}</span>
              </button>
            ))}
          </div>
        </div>

        <div>
          <h3 className="text-[11px] font-bold uppercase tracking-wider text-[#64748B] mb-3">
            Rating
          </h3>
          <div className="space-y-2.5">
            {['3+ Bintang', '4+ Bintang', '4.5+ Bintang'].map(r => (
              <button
                key={r}
                type="button"
                className="flex w-full items-center gap-3 cursor-pointer text-left group"
                onClick={() => setRating(rating === r ? null : r)}
              >
                <div className={`w-4 h-4 rounded-full border flex shrink-0 items-center justify-center transition-colors ${rating === r ? 'border-[#0E75BC] bg-[#0E75BC]' : 'border-slate-300 bg-white group-hover:border-[#0E75BC]'}`}>
                  {rating === r && <div className="w-1.5 h-1.5 bg-white rounded-full" />}
                </div>
                <span className="text-[14px] text-slate-700">{r}</span>
              </button>
            ))}
          </div>
        </div>

        <div className="mt-6 pt-4 border-t border-slate-100 flex flex-col gap-3">
          <button
            type="submit"
            className="w-full rounded-xl bg-[#0E75BC] px-4 py-3 sm:py-3.5 text-[13px] sm:text-[14px] font-bold text-white transition-colors hover:bg-[#095f99] shadow-sm"
          >
            Terapkan Filters
          </button>
          <button
            type="reset"
            className="flex w-full items-center justify-center gap-1.5 rounded-xl border border-slate-200 bg-white px-4 py-3 sm:py-3.5 text-[13px] sm:text-[14px] font-bold text-slate-500 hover:text-[#E54545] hover:border-[#E54545] transition-colors"
          >
            <svg fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-4 h-4"><path strokeLinecap="round" strokeLinejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99" /></svg>
            Reset Filter
          </button>
        </div>
      </form>
    </aside>
    </>
  );
}

export function AccommodationPageContent() {
  const [selectedHotel, setSelectedHotel] = useState<AccommodationOption | null>(null);

  return (
    <main className="mx-auto max-w-[1180px] px-4 py-4 sm:py-6 sm:px-8">
      <div className="mb-3 sm:mb-5 flex flex-col gap-2 sm:gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <h1 className="text-[24px] font-semibold leading-tight text-[#202B37] sm:text-[34px]">
            Pilih Penginapan
          </h1>
        </div>

        <div className="w-full lg:max-w-[460px]">

        </div>
      </div>

      <div className="flex flex-col-reverse gap-3 sm:gap-5 lg:grid lg:grid-cols-[minmax(0,1fr)_320px] xl:grid-cols-[minmax(0,1fr)_340px]">
        <div className="min-w-0 space-y-3 sm:space-y-5">
          <AccommodationFilters />
          <CepotInsight />

          <section>
            <div className="mb-3">
              <h2 className="text-[17px] font-semibold text-[#202B37]">
                Rekomendasi Terbaik
              </h2>
              <p className="mt-1 text-[12px] leading-5 text-[#7B8B99]">
                3 penginapan cocok untuk itinerary Ciwidey.
              </p>
            </div>

            <div className="space-y-3">
              {ACCOMMODATIONS.map((accommodation, index) => (
                <AccommodationCard
                  key={accommodation.name}
                  accommodation={accommodation}
                  onSelect={(acc) => setSelectedHotel(acc)}
                  eagerImage={index === 0}
                />
              ))}
            </div>
          </section>
        </div>

        <div className="flex flex-col gap-3 sm:gap-5 lg:sticky lg:top-6 lg:self-start">
          <TripSidebar />
          <AccommodationSidebar />
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
