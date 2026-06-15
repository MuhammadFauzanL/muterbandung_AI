'use client';

import { useState } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import {
  Mountain,
  Utensils,
  ShoppingBag,
  Landmark,
  Home,
  PawPrint,
  Castle,
  GraduationCap,
  Leaf,
  Camera,
  PersonStanding,
  Rocket,
  Users,
  Smile,
  Building,
  TreePine,
  Moon,
  ArrowRight,
  Sparkles,
} from 'lucide-react';

// --- DATA CONSTANTS ---
const FAVORITE_PLACES = [
  { id: 'alam', label: 'Alam', icon: Mountain },
  { id: 'kuliner', label: 'Kuliner', icon: Utensils },
  { id: 'belanja', label: 'Belanja', icon: ShoppingBag },
  { id: 'sejarah', label: 'Sejarah', icon: Landmark },
  { id: 'budaya', label: 'Budaya', icon: Home },
  { id: 'satwa', label: 'Satwa', icon: PawPrint },
  { id: 'religi', label: 'Religi', icon: Castle },
  { id: 'edukasi', label: 'Edukasi', icon: GraduationCap },
];

const FAVORITE_ACTIVITIES = [
  { id: 'santai', label: 'Santai / Healing', desc: 'Tenangkan pikiran & jiwa.', icon: Leaf },
  { id: 'foto', label: 'Spot Foto', desc: 'Estetik dan hits.', icon: Camera },
  { id: 'petualangan', label: 'Petualangan', desc: 'Eksplorasi medan menantang.', icon: PersonStanding },
  { id: 'wahana', label: 'Wahana Ekstrem', desc: 'Adrenalin tinggi & seru.', icon: Rocket },
];

const TARGET_VISITORS = [
  { id: 'keluarga', label: 'Keluarga', icon: Users },
  { id: 'ramah_anak', label: 'Ramah Anak', icon: Smile },
];

const ATMOSPHERES = [
  { id: 'indoor', label: 'Indoor', icon: Building },
  { id: 'outdoor', label: 'Outdoor', icon: TreePine },
  { id: 'malam', label: 'Malam / City Light', icon: Moon },
];

// --- INTERFACES ---
interface PreferencesState {
  places: string[];
  activities: string[];
  visitor: string;
  atmospheres: string[];
  isFree: boolean;
}

export function PreferencesForm() {
  const [prefs, setPrefs] = useState<PreferencesState>({
    places: [],
    activities: [],
    visitor: '',
    atmospheres: [],
    isFree: false,
  });

  // --- HANDLERS ---
  const togglePlace = (id: string) => {
    setPrefs((prev) => {
      const isSelected = prev.places.includes(id);
      if (isSelected) {
        return { ...prev, places: prev.places.filter((p) => p !== id) };
      }
      if (prev.places.length >= 3) return prev; // Max 3
      return { ...prev, places: [...prev.places, id] };
    });
  };

  const toggleActivity = (id: string) => {
    setPrefs((prev) => {
      const isSelected = prev.activities.includes(id);
      if (isSelected) {
        return { ...prev, activities: prev.activities.filter((a) => a !== id) };
      }
      if (prev.activities.length >= 2) return prev; // Max 2
      return { ...prev, activities: [...prev.activities, id] };
    });
  };

  const setVisitor = (id: string) => {
    setPrefs((prev) => ({ ...prev, visitor: id }));
  };

  const toggleAtmosphere = (id: string) => {
    setPrefs((prev) => {
      const isSelected = prev.atmospheres.includes(id);
      if (isSelected) {
        return { ...prev, atmospheres: prev.atmospheres.filter((a) => a !== id) };
      }
      return { ...prev, atmospheres: [...prev.atmospheres, id] };
    });
  };

  const toggleFree = () => {
    setPrefs((prev) => ({ ...prev, isFree: !prev.isFree }));
  };

  return (
    <div className="flex min-h-screen flex-col lg:flex-row bg-[#F7F9FF]">
      {/* KIRI - Panel Maskot & Teks */}
      <div className="relative flex flex-1 flex-col items-center justify-center px-4 pt-6 pb-2 sm:px-12 sm:py-12 bg-[#F7F9FF] overflow-hidden lg:fixed lg:bottom-0 lg:left-0 lg:top-0 lg:w-[45%]">
        {/* Ornamen Latar Belakang */}
        <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-5" />
        <div className="absolute left-1/2 top-1/2 h-[500px] w-[500px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-red-500/5 blur-[100px]" />

        <div className="relative z-10 flex flex-col items-center text-center max-w-[420px]">
          {/* Speech Bubble */}
          <div className="relative mb-5 rounded-[20px] bg-white p-[3px] shadow-[0_20px_40px_-15px_rgba(0,0,0,0.05)]">
            <div className="rounded-[17px] bg-white px-5 py-2.5 sm:px-8 sm:py-5">
              <p className="text-[12px] sm:text-[15px] font-medium leading-[18px] sm:leading-[24px] text-[#051D2E]">
                Sampurasun! Sebelum mulai, aku ingin mengenal gaya liburanmu agar rekomendasiku lebih personal.
              </p>
            </div>
            {/* Segitiga bawah speech bubble */}
            <div className="absolute -bottom-2 left-1/2 h-4 w-4 -translate-x-1/2 rotate-45 border-b border-r border-transparent bg-white shadow-[8px_8px_16px_rgba(0,0,0,0.02)]" />
          </div>

          {/* Maskot */}
          <div className="mb-3 sm:mb-6">
            <Image
              src="/images/welcome-cepot.png"
              alt="Maskot Cepot MuterBandung"
              width={220}
              height={260}
              priority
              className="object-contain drop-shadow-xl w-[100px] h-[116px] sm:w-[220px] sm:h-[260px]"
            />
          </div>

          {/* Heading & Deskripsi */}
          <h1 className="text-[20px] sm:text-[28px] font-bold text-[#051D2E] tracking-tight">
            Biar Aku Kenal Kamu Dulu
          </h1>
          <p className="mt-1 sm:mt-3 text-[12px] sm:text-[15px] leading-[18px] sm:leading-[24px] text-[#40484D]">
            Atur preferensimu agar Cepot bisa meracik rencana perjalanan paling asyik buat kamu di Bandung.
          </p>
        </div>
      </div>

      {/* Spacing Kiri (karena fixed layout di layar besar) */}
      <div className="hidden lg:block lg:w-[45%]" />

      {/* KANAN - Scrollable Form Preferensi */}
      <div className="flex flex-1 flex-col items-center justify-start bg-[#ECF4FF] px-3 pt-2 pb-6 sm:px-6 lg:px-12 lg:py-12 min-h-screen">
        <div className="w-full max-w-[600px] rounded-[20px] bg-white shadow-[0_4px_12px_0_rgba(10,34,51,0.06)] border border-slate-200/50 flex flex-col relative overflow-hidden">
          
          {/* Form Header */}
          <div className="sticky top-0 z-20 flex items-center justify-between border-b border-slate-100 bg-white/95 px-4 py-3 sm:px-8 sm:py-6 backdrop-blur-md">
            <h2 className="text-[12px] sm:text-[14px] font-bold tracking-[0.05em] text-[#051D2E]">PREFERENSI WISATA</h2>
          </div>

          {/* Scrollable Body */}
          <div className="flex-1 px-4 py-4 sm:px-8 sm:py-8 space-y-4 sm:space-y-10">
            
            {/* 1. Tipe Tempat Favorit */}
            <section>
              <div className="mb-2 sm:mb-4">
                <h3 className="text-[14px] sm:text-[16px] font-bold text-[#051D2E]">Tipe Tempat Favorit</h3>
                <p className="mt-0.5 sm:mt-1 text-[11px] sm:text-[13px] text-[#40484D]">Pilih maksimal 3 yang kamu suka.</p>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 sm:gap-3">
                {FAVORITE_PLACES.map((place) => {
                  const isSelected = prefs.places.includes(place.id);
                  const Icon = place.icon;
                  return (
                    <button
                      key={place.id}
                      onClick={() => togglePlace(place.id)}
                      className={`flex items-center justify-start gap-2.5 rounded-[12px] border p-2 sm:p-4 transition-all active:scale-[0.98] ${
                        isSelected
                          ? 'border-[#00526E] bg-[#F0F7FC] shadow-sm'
                          : 'border-slate-200 bg-white hover:border-[#BFC8CE]'
                      }`}
                    >
                      <div className={`rounded-lg p-1.5 sm:p-2 shrink-0 ${isSelected ? 'bg-white' : 'bg-[#F7F9FF]'}`}>
                        <Icon className={`h-4 w-4 sm:h-6 sm:w-6 ${isSelected ? 'text-[#00526E]' : 'text-[#40484D]'}`} strokeWidth={isSelected ? 2.5 : 1.5} />
                      </div>
                      <span className={`text-[12px] sm:text-[13px] font-semibold ${isSelected ? 'text-[#00526E]' : 'text-[#40484D]'}`}>
                        {place.label}
                      </span>
                    </button>
                  );
                })}
              </div>
            </section>

            {/* 2. Aktivitas Favorit */}
            <section>
              <div className="mb-2 sm:mb-4">
                <h3 className="text-[14px] sm:text-[16px] font-bold text-[#051D2E]">Aktivitas Favorit</h3>
                <p className="mt-0.5 sm:mt-1 text-[11px] sm:text-[13px] text-[#40484D]">Pilih maksimal 2 aktivitas.</p>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-2 gap-2 sm:gap-3">
                {FAVORITE_ACTIVITIES.map((act) => {
                  const isSelected = prefs.activities.includes(act.id);
                  const Icon = act.icon;
                  return (
                    <button
                      key={act.id}
                      onClick={() => toggleActivity(act.id)}
                      className={`flex items-center gap-2.5 sm:gap-4 rounded-[12px] border p-2 sm:p-4 text-left transition-all active:scale-[0.98] ${
                        isSelected
                          ? 'border-[#00526E] bg-[#F0F7FC] shadow-sm'
                          : 'border-slate-200 bg-white hover:border-[#BFC8CE]'
                      }`}
                    >
                      <div className={`rounded-lg p-1.5 sm:p-2 shrink-0 ${isSelected ? 'bg-white' : 'bg-[#F7F9FF]'}`}>
                        <Icon className={`h-4 w-4 sm:h-6 sm:w-6 ${isSelected ? 'text-[#00526E]' : 'text-[#40484D]'}`} strokeWidth={isSelected ? 2.5 : 1.5} />
                      </div>
                      <div>
                        <span className={`block text-[12px] sm:text-[14px] font-semibold ${isSelected ? 'text-[#00526E]' : 'text-[#051D2E]'}`}>
                          {act.label}
                        </span>
                        <span className="hidden sm:block mt-0.5 sm:mt-1 text-[11px] sm:text-[12px] text-[#6B7280]">
                          {act.desc}
                        </span>
                      </div>
                    </button>
                  );
                })}
              </div>
            </section>

            {/* 3. Target Pengunjung */}
            <section>
              <div className="mb-2 sm:mb-4">
                <h3 className="text-[14px] sm:text-[16px] font-bold text-[#051D2E]">Target Pengunjung</h3>
                <p className="mt-0.5 sm:mt-1 text-[11px] sm:text-[13px] text-[#40484D]">Pilih satu yang paling sesuai.</p>
              </div>
              <div className="flex flex-wrap gap-3">
                {TARGET_VISITORS.map((visitor) => {
                  const isSelected = prefs.visitor === visitor.id;
                  const Icon = visitor.icon;
                  return (
                    <button
                      key={visitor.id}
                      onClick={() => setVisitor(visitor.id)}
                      className={`flex items-center gap-1.5 sm:gap-2 rounded-full border px-4 py-2 sm:px-5 sm:py-2.5 transition-all active:scale-[0.98] ${
                        isSelected
                          ? 'border-[#00526E] bg-[#00526E] text-white shadow-sm'
                          : 'border-slate-200 bg-white text-[#051D2E] hover:bg-slate-50'
                      }`}
                    >
                      <Icon className="h-3.5 w-3.5 sm:h-4 sm:w-4" strokeWidth={2} />
                      <span className="text-[12px] sm:text-[14px] font-semibold">{visitor.label}</span>
                    </button>
                  );
                })}
              </div>
            </section>

            {/* 4. Suasana yang Disukai */}
            <section>
              <div className="mb-2 sm:mb-4">
                <h3 className="text-[14px] sm:text-[16px] font-bold text-[#051D2E]">Suasana yang Disukai</h3>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 sm:gap-3">
                {ATMOSPHERES.map((atm) => {
                  const isSelected = prefs.atmospheres.includes(atm.id);
                  const Icon = atm.icon;
                  return (
                    <button
                      key={atm.id}
                      onClick={() => toggleAtmosphere(atm.id)}
                      className={`flex items-center justify-start gap-2.5 rounded-[12px] border p-2 sm:p-4 transition-all active:scale-[0.98] ${
                        isSelected
                          ? 'border-[#00526E] bg-[#F0F7FC] shadow-sm'
                          : 'border-slate-200 bg-white hover:border-[#BFC8CE]'
                      }`}
                    >
                      <div className={`rounded-lg p-1.5 sm:p-2 shrink-0 ${isSelected ? 'bg-white' : 'bg-[#F7F9FF]'}`}>
                        <Icon className={`h-4 w-4 sm:h-6 sm:w-6 ${isSelected ? 'text-[#00526E]' : 'text-[#40484D]'}`} strokeWidth={isSelected ? 2.5 : 1.5} />
                      </div>
                      <span className={`text-[12px] sm:text-[13px] font-semibold ${isSelected ? 'text-[#00526E]' : 'text-[#051D2E]'}`}>
                        {atm.label}
                      </span>
                    </button>
                  );
                })}
              </div>
            </section>

            {/* 5. Wisata Gratis */}
            <section>
              <div className="flex items-center justify-between rounded-[16px] bg-[#F0F4F8] p-2.5 sm:p-5">
                <div className="flex items-center gap-3 sm:gap-4">
                  <div className="flex h-7 w-7 sm:h-10 sm:w-10 shrink-0 items-center justify-center rounded-full bg-white text-[#E54545]">
                    <span className="font-bold text-[11px] sm:text-[14px]">Rp</span>
                  </div>
                  <div>
                    <h4 className="text-[13px] sm:text-[14px] font-bold text-[#051D2E]">Wisata Gratis (Free)</h4>
                    <p className="mt-0.5 text-[10px] sm:text-[12px] text-[#6B7280]">Tampilkan destinasi tanpa tiket.</p>
                  </div>
                </div>
                {/* Toggle Switch */}
                <button
                  onClick={toggleFree}
                  className={`relative inline-flex h-5 w-9 sm:h-6 sm:w-11 shrink-0 cursor-pointer items-center rounded-full transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-[#00526E] focus:ring-offset-2 ${
                    prefs.isFree ? 'bg-[#00526E]' : 'bg-slate-200'
                  }`}
                >
                  <span className="sr-only">Toggle wisata gratis</span>
                  <span
                    className={`inline-block h-4 w-4 sm:h-5 sm:w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                      prefs.isFree ? 'translate-x-4 sm:translate-x-5' : 'translate-x-0.5'
                    }`}
                  />
                </button>
              </div>
            </section>

            {/* 6. Kotak Info Cepot */}
            <section>
              <div className="relative overflow-hidden rounded-[12px] border border-[#CDE3F3] bg-[#EAF4FB] p-3 sm:p-5">
                <div className="relative z-10 flex items-start gap-2.5 sm:gap-4">
                  <Sparkles className="mt-0.5 sm:mt-1 h-3.5 w-3.5 sm:h-5 sm:w-5 shrink-0 text-[#00526E]" />
                  <div>
                    <h4 className="text-[11px] sm:text-[13px] font-bold uppercase tracking-wide text-[#00526E]">
                      CEPOT MEMAHAMI SELERAMU
                    </h4>
                    <p className="mt-0.5 sm:mt-1.5 text-[10px] sm:text-[13px] leading-relaxed text-[#00526E]/80">
                      Silakan pilih beberapa preferensi di atas! Cepot akan memberikan rekomendasi yang pas.
                    </p>
                  </div>
                </div>
                {/* Decoration */}
                <div className="absolute -right-6 -top-6 text-[#00526E] opacity-[0.03]">
                  <Sparkles className="h-20 w-20 sm:h-32 sm:w-32" />
                </div>
              </div>
            </section>
          </div>

          {/* Form Footer Actions */}
          <div className="sticky bottom-0 z-20 flex flex-col-reverse sm:flex-row items-center justify-between border-t border-slate-100 bg-white/95 px-4 py-3 sm:px-8 sm:py-5 backdrop-blur-md gap-2 sm:gap-4">
            <Link
              href="/"
              className="text-[13px] sm:text-[14px] font-bold text-[#40484D] hover:text-[#051D2E] transition-colors"
            >
              Lewati
            </Link>
            <Link
              href="/#foryou"
              className="group flex w-full sm:w-auto items-center justify-center gap-2 rounded-full bg-[#00526E] px-5 py-2.5 sm:px-6 sm:py-3 text-[13px] sm:text-[14px] font-semibold text-white transition-all hover:bg-[#00415C] active:scale-[0.98] shadow-md"
            >
              Mulai Jelajahi Bandung
              <ArrowRight className="h-3.5 w-3.5 sm:h-4 sm:w-4 transition-transform group-hover:translate-x-1" />
            </Link>
          </div>

        </div>
      </div>
    </div>
  );
}
