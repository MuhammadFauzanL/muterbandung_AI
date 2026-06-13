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
      'https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?q=80&w=900&auto=format&fit=crop',
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
      'https://images.unsplash.com/photo-1566073771259-6a8506099945?q=80&w=900&auto=format&fit=crop',
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
      'https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?q=80&w=900&auto=format&fit=crop',
    highlights: ['Kolam renang', 'Restoran', 'Akses kota'],
  },
] as const;

const FILTERS = ['Semua', 'Dekat Kawah Putih', 'Family stay', 'Cabin', 'Budget hemat'];




function AccommodationFilters() {
  return (
    <section className="rounded-[16px] border border-slate-200 bg-white p-4 shadow-sm">
      <div className="grid gap-3 md:grid-cols-[minmax(0,1fr)_150px_132px_140px]">
        <label className="flex h-12 items-center gap-2 rounded-xl border border-slate-200 bg-white px-3 text-slate-500 focus-within:border-[#0E75BC] transition-colors">
          <Search className="h-4 w-4" />
          <span className="sr-only">Cari penginapan</span>
          <input
            type="search"
            placeholder="Cari area atau nama penginapan"
            className="min-w-0 flex-1 bg-transparent text-[14px] text-slate-800 outline-none placeholder:text-slate-400"
          />
        </label>
        <button
          type="button"
          className="inline-flex h-12 items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-3 text-[14px] font-semibold text-slate-700 hover:border-slate-300 transition-colors"
        >
          <Calendar className="h-4 w-4" />
          12 Jun
        </button>
        <button
          type="button"
          className="inline-flex h-12 items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-3 text-[14px] font-semibold text-slate-700 hover:border-slate-300 transition-colors"
        >
          <Users className="h-4 w-4" />
          2 Tamu
        </button>
        <button
          type="button"
          className="inline-flex h-12 items-center justify-center rounded-xl bg-[#0E75BC] px-3 text-[14px] font-semibold text-white transition-colors hover:bg-[#095f99] shadow-sm"
        >
          Terapkan
        </button>
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        {FILTERS.map((filter, index) => (
          <button
            key={filter}
            type="button"
            className={`rounded-full border px-5 py-2.5 text-[13px] font-medium transition-colors ${index === 0
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

      <div className="min-w-0 p-4">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
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

          <div className="shrink-0 rounded-[10px] bg-[#FFF7E8] px-3 py-2 text-[#7C4F00]">
            <div className="flex items-center gap-1 text-[12px] font-bold">
              <Star className="h-4 w-4 fill-current text-[#FBBF24]" />
              {accommodation.rating}
            </div>
            <p className="mt-0.5 text-[10px] font-semibold text-[#9B7840]">
              {accommodation.reviewCount}
            </p>
          </div>
        </div>

        <p className="mt-3 text-[13px] leading-6 text-[#607382]">
          {accommodation.description}
        </p>

        <div className="mt-4 flex flex-wrap gap-2">
          {accommodation.highlights.map((highlight) => (
            <span
              key={highlight}
              className="rounded-full bg-[#EEF7FD] px-3 py-1.5 text-[11px] font-semibold text-[#23689A]"
            >
              {highlight}
            </span>
          ))}
        </div>

        <div className="mt-5 flex flex-col gap-3 border-t border-[#EDF4F8] pt-4 sm:flex-row sm:items-center sm:justify-between">
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
    <section className="relative overflow-hidden rounded-[18px] border border-[#BFE8F0] bg-[#EAF8FB] px-5 py-4">
      <div className="relative z-10 flex items-start gap-3">
        <div className="relative h-11 w-11 shrink-0 overflow-hidden rounded-full bg-[#D8F0F6] ring-1 ring-white">
          <Image
            src="/images/welcome-cepot.png"
            alt="Cepot AI"
            fill
            sizes="44px"
            className="object-cover object-top"
          />
        </div>
        <div>
          <p className="flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-normal text-[#137CA6]">
            <Sparkles className="h-4 w-4" />
            Cepot AI Insight
          </p>
          <p className="mt-1.5 text-[13px] leading-6 text-[#26485C]">
            Anda belum memilih destinasi wisata di tahap sebelumnya. Silakan &quot;Kembali&quot; untuk memilih tempat wisata terlebih dahulu, agar kami dapat merekomendasikan penginapan terdekat.
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
    <aside className="relative rounded-[16px] border border-[#DCEAF3] bg-white p-5 shadow-[0_10px_28px_rgba(17,73,112,0.07)]">
      {/* Toast Error Notification */}
      <div className={`absolute top-4 left-1/2 -translate-x-1/2 z-50 rounded-2xl border border-red-100 bg-white px-4 py-2.5 text-[13px] font-bold text-red-600 shadow-[0_12px_40px_rgba(0,0,0,0.12)] transition-all duration-300 flex items-center gap-2 whitespace-nowrap ${showToast ? 'opacity-100 translate-y-0' : 'opacity-0 -translate-y-4 pointer-events-none'}`}>
        <div className="flex items-center justify-center w-5 h-5 rounded-full bg-red-100 text-red-600">
          <svg fill="none" viewBox="0 0 24 24" strokeWidth={3} stroke="currentColor" className="w-3 h-3"><path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" /></svg>
        </div>
        Pilih hotel terlebih dahulu!
      </div>

      <h2 className="text-[15px] font-semibold text-[#202B37]">
        Ringkasan Perjalanan
      </h2>

      <div className="mt-4 space-y-2.5">
        {destinations.map((dest) => (
          <div key={dest.id} className="flex items-center gap-2 rounded-[10px] bg-[#EAF8FB] px-3 py-2.5 text-[12px] font-semibold text-[#246983]">
            <MapPin className="h-4 w-4" />
            <span className="flex-1">{dest.title}</span>
            <button onClick={() => removeDestination(dest.id)} className="text-red-400 hover:text-red-600">
              <X className="h-4 w-4" />
            </button>
          </div>
        ))}

        {accommodations.length > 0 ? (
          accommodations.map((acc) => (
            <div key={acc.name} className="flex items-center gap-2 rounded-[10px] bg-[#EAF8FB] px-3 py-2.5 text-[12px] font-semibold text-[#246983]">
              <Wallet className="h-4 w-4" />
              <span className="flex-1">{acc.name}</span>
              <button onClick={() => removeAccommodation(acc.name)} className="text-red-400 hover:text-red-600">
                <X className="h-4 w-4" />
              </button>
            </div>
          ))
        ) : (
          <div className="flex items-center gap-2 rounded-[10px] border border-[#E3EEF4] bg-white px-3 py-2.5 text-[12px] text-[#97A5B1]">
            <Wallet className="h-4 w-4" />
            <span className="flex-1">Pilih penginapan...</span>
          </div>
        )}
      </div>

      <dl className="mt-5 space-y-2.5 border-t border-[#EDF4F8] pt-4 text-[12px]">
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

      <div className="mt-5 space-y-3">
        <button
          onClick={handleSave}
          className="inline-flex h-11 w-full items-center justify-center rounded-[10px] bg-[#0E75BC] px-4 text-[13px] font-semibold text-white transition-colors hover:bg-[#095f99]"
        >
          Simpan Pilihan
        </button>
        <Link
          href="/planner"
          className="inline-flex h-11 w-full items-center justify-center rounded-[10px] border border-[#0E75BC] bg-white px-4 text-[13px] font-semibold text-[#0E75BC] transition-colors hover:bg-[#F2FAFE]"
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
      <div className="relative w-full max-w-[500px] overflow-hidden rounded-[20px] bg-white shadow-2xl">
        <button
          onClick={onClose}
          className="absolute right-4 top-4 rounded-full p-2 text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-600"
        >
          <X className="h-4 w-4" />
        </button>

        <div className="p-6 pb-0">
          <h2 className="text-[18px] font-semibold text-[#0E75BC]">
            Konfirmasi Penginapan
          </h2>
          <div className="mt-1 flex items-center gap-2 text-[14px]">
            <span className="font-semibold text-slate-900">{hotel.name}</span>
            <span className="flex items-center gap-1 text-[12px] font-bold text-[#7C4F00]">
              <Star className="h-4 w-4 fill-current text-[#FBBF24]" /> {hotel.rating}
            </span>
            <span className="text-slate-400">•</span>
            <span className="flex items-center gap-1 text-slate-500 text-[12px]">
              <MapPin className="h-4 w-4" /> {hotel.distance}
            </span>
          </div>
          <p className="mt-3 text-[20px] font-bold text-[#0E75BC]">
            {hotel.price} <span className="text-[12px] font-normal text-slate-500">/ malam</span>
          </p>
        </div>

        <div className="p-6">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="mb-1 block text-[12px] font-medium text-slate-500">Check-in</label>
              <input
                type="date"
                value={checkIn}
                onChange={(e) => setCheckIn(e.target.value)}
                className="w-full rounded-[10px] border border-slate-200 px-3 py-2 text-[14px] text-slate-900 outline-none focus:border-[#0E75BC]"
              />
            </div>
            <div>
              <label className="mb-1 block text-[12px] font-medium text-slate-500">Check-out</label>
              <input
                type="date"
                value={checkOut}
                onChange={(e) => setCheckOut(e.target.value)}
                className="w-full rounded-[10px] border border-slate-200 px-3 py-2 text-[14px] text-slate-900 outline-none focus:border-[#0E75BC]"
              />
            </div>
          </div>

          <div className="my-4 flex items-center justify-center">
            <div className="rounded-full bg-[#0E75BC] px-4 py-1.5 text-[11px] font-semibold text-white shadow-sm">
              {nights + 1} Hari {nights} Malam
            </div>
          </div>

          <div className="flex items-center justify-between rounded-[12px] bg-slate-50 p-4 border border-slate-100">
            <div>
              <p className="text-[13px] font-semibold text-slate-900">Jumlah Orang</p>
              <p className="text-[11px] text-slate-500">Dewasa / Anak</p>
            </div>
            <div className="flex items-center gap-4">
              <button
                onClick={() => setGuests(Math.max(1, guests - 1))}
                className="flex h-8 w-8 items-center justify-center rounded-full border border-slate-300 bg-white text-slate-600 transition-colors hover:bg-slate-100"
              >
                -
              </button>
              <span className="w-4 text-center font-semibold text-slate-900">{guests}</span>
              <button
                onClick={() => setGuests(guests + 1)}
                className="flex h-8 w-8 items-center justify-center rounded-full bg-[#0E75BC] text-white transition-colors hover:bg-[#095f99]"
              >
                +
              </button>
            </div>
          </div>

          <div className="mt-5 rounded-[12px] border border-[#BFE8F0] bg-[#EAF8FB] p-4 flex gap-3">
            <div className="mt-0.5 text-[#137CA6]"><Sparkles className="h-4 w-4" /></div>
            <p className="text-[12px] leading-5 text-[#26485C]">
              <strong className="text-[#137CA6]">Cepot AI:</strong> &quot;Dengan {guests} tamu, kamu membutuhkan <strong>{rooms} kamar</strong>. Durasi menginap ini direkomendasikan agar seluruh destinasi dalam itinerary dapat dikunjungi dengan nyaman.&quot;
            </p>
          </div>

          <div className="mt-6 border-t border-slate-100 pt-5">
            <div className="space-y-3 text-[13px]">
              <div className="flex justify-between text-slate-600">
                <span>{hotel.name} ({nights} Malam, {rooms} Kamar)</span>
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

            <div className="mt-4 flex items-center justify-between border-t border-slate-100 pt-4">
              <span className="text-[15px] font-bold text-[#0E75BC]">Total Estimasi</span>
              <span className="text-[20px] font-bold text-[#0E75BC]">Rp{totalEstimasi.toLocaleString('id-ID')}</span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3 border-t border-slate-100 p-6 bg-slate-50/50">
          <button
            onClick={onClose}
            className="flex-1 rounded-[12px] px-4 py-3.5 text-[14px] font-semibold text-slate-600 transition-colors hover:bg-slate-100"
          >
            Batal
          </button>
          <button
            onClick={handleConfirm}
            className="flex-[2] rounded-[12px] bg-[#0E75BC] px-4 py-3.5 text-[14px] font-semibold text-white transition-colors hover:bg-[#095f99] shadow-md"
          >
            Tambahkan ke Perjalanan
          </button>
        </div>
      </div>
    </div>
  );
}

function AccommodationSidebar() {
  return (
    <aside className="rounded-[16px] border border-slate-200 bg-white p-5 shadow-[0_8px_30px_rgb(0,0,0,0.04)]">
      <div className="mb-6 flex items-center gap-2">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5 text-slate-800">
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
        </svg>
        <h2 className="text-[17px] font-bold text-slate-900">
          Sesuaikan Hasil
        </h2>
      </div>

      <div className="space-y-6">
        <div>
          <h3 className="text-[11px] font-bold uppercase tracking-wider text-[#64748B] mb-3">
            Anggaran
          </h3>
          <div className="space-y-2.5">
            <label className="flex items-center gap-3 cursor-pointer">
              <input type="radio" name="budget" className="w-4 h-4 border-slate-300 text-[#0E75BC] focus:ring-[#0E75BC]" />
              <span className="text-[14px] text-slate-700">&lt; 500rb</span>
            </label>
            <label className="flex items-center gap-3 cursor-pointer">
              <input type="radio" name="budget" defaultChecked className="w-4 h-4 border-slate-300 text-[#0E75BC] focus:ring-[#0E75BC]" />
              <span className="text-[14px] text-slate-700">500rb - 1jt</span>
            </label>
            <label className="flex items-center gap-3 cursor-pointer">
              <input type="radio" name="budget" className="w-4 h-4 border-slate-300 text-[#0E75BC] focus:ring-[#0E75BC]" />
              <span className="text-[14px] text-slate-700">&gt; 1jt</span>
            </label>
          </div>
        </div>

        <div>
          <h3 className="text-[11px] font-bold uppercase tracking-wider text-[#64748B] mb-3">
            Tipe Properti
          </h3>
          <div className="space-y-2.5">
            <label className="flex items-center gap-3 cursor-pointer">
              <input type="checkbox" defaultChecked className="w-4 h-4 rounded border-slate-300 text-[#0E75BC] focus:ring-[#0E75BC]" />
              <span className="text-[14px] text-slate-700">Hotel</span>
            </label>
            <label className="flex items-center gap-3 cursor-pointer">
              <input type="checkbox" defaultChecked className="w-4 h-4 rounded border-slate-300 text-[#0E75BC] focus:ring-[#0E75BC]" />
              <span className="text-[14px] text-slate-700">Villa</span>
            </label>
            <label className="flex items-center gap-3 cursor-pointer">
              <input type="checkbox" className="w-4 h-4 rounded border-slate-300 text-[#0E75BC] focus:ring-[#0E75BC]" />
              <span className="text-[14px] text-slate-700">Glamping</span>
            </label>
          </div>
        </div>

        <div>
          <h3 className="text-[11px] font-bold uppercase tracking-wider text-[#64748B] mb-3">
            Rating
          </h3>
          <div className="space-y-2.5">
            <label className="flex items-center gap-3 cursor-pointer">
              <input type="radio" name="rating" className="w-4 h-4 border-slate-300 text-[#0E75BC] focus:ring-[#0E75BC]" />
              <span className="text-[14px] text-slate-700">3+ Bintang</span>
            </label>
            <label className="flex items-center gap-3 cursor-pointer">
              <input type="radio" name="rating" className="w-4 h-4 border-slate-300 text-[#0E75BC] focus:ring-[#0E75BC]" />
              <span className="text-[14px] text-slate-700">4+ Bintang</span>
            </label>
            <label className="flex items-center gap-3 cursor-pointer">
              <input type="radio" name="rating" defaultChecked className="w-4 h-4 border-slate-300 text-[#0E75BC] focus:ring-[#0E75BC]" />
              <span className="text-[14px] text-slate-700">4.5+ Bintang</span>
            </label>
          </div>
        </div>
      </div>

      <div className="mt-8 pt-4 border-t border-slate-100 flex flex-col gap-3">
        <button
          type="button"
          className="w-full rounded-xl bg-[#0E75BC] px-4 py-3.5 text-[14px] font-bold text-white transition-colors hover:bg-[#095f99] shadow-sm"
        >
          Terapkan Filters
        </button>
        <button
          type="button"
          className="flex w-full items-center justify-center gap-1.5 rounded-xl border border-slate-200 bg-white px-4 py-3.5 text-[14px] font-bold text-slate-500 hover:text-[#E54545] hover:border-[#E54545] transition-colors"
        >
          <svg fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-4 h-4"><path strokeLinecap="round" strokeLinejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99" /></svg>
          Reset Filter
        </button>
      </div>
    </aside>
  );
}

export function AccommodationPageContent() {
  const [selectedHotel, setSelectedHotel] = useState<AccommodationOption | null>(null);

  return (
    <main className="mx-auto max-w-[1180px] px-4 py-6 sm:px-8">
      <div className="mb-5 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <h1 className="text-[28px] font-semibold leading-tight text-[#202B37] sm:text-[34px]">
            Pilih Penginapan
          </h1>
          <p className="mt-2 max-w-2xl text-[14px] leading-6 text-[#657786]">
            Rekomendasi penginapan disusun dari jarak ke destinasi, budget,
            dan ritme perjalanan yang sudah kamu pilih.
          </p>
        </div>

        <div className="w-full lg:max-w-[460px]">

        </div>
      </div>

      <div className="flex flex-col-reverse gap-5 lg:grid lg:grid-cols-[minmax(0,1fr)_320px] xl:grid-cols-[minmax(0,1fr)_340px]">
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
                  onSelect={(acc) => setSelectedHotel(acc)}
                  eagerImage={index === 0}
                />
              ))}
            </div>
          </section>
        </div>

        <div className="flex flex-col gap-5 lg:sticky lg:top-6 lg:self-start">
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
