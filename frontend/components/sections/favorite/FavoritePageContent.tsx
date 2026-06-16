"use client";

import Image from 'next/image';
import { useState } from 'react';
import { MapPin, Map, Building, Heart, PlusCircle, Star } from 'lucide-react';
import { usePlanner } from '@/context/PlannerContext';
import { useToast } from '@/context/ToastContext';
import Link from 'next/link';

type TabType = 'Destinasi' | 'Penginapan' | 'Itinerary';

const MOCK_FAVORITE_DESTINATIONS = [
  {
    id: 'kawah-putih',
    title: 'Kawah Putih Ciwidey',
    location: 'Bandung Selatan',
    rating: '4.8',
    description: 'Danau kawah vulkanik yang indah dengan tanah berwarna putih dan air...',
    image: 'https://lh3.googleusercontent.com/gps-cs-s/APNQkAFaFXwEw1U4JIxhDsJyjEZJ7dqvRVW5IsAh8vwhX9CJumOqs71mWd90VbeY4WWgvBh6nodCe9tVRNO4574wsSgJnHLeoZRcFa7oXmZYME4fvSDhQ6Vgmu9TRYT8z7sUSaSkjUk_vQ=w408-h306-k-no'
  },
  {
    id: 'lodge-maribaya',
    title: 'The Lodge Maribaya',
    location: 'Lembang',
    rating: '4.6',
    description: 'Kawasan wisata outdoor dengan pemandangan hutan pinus yang asri...',
    image: 'https://lh3.googleusercontent.com/gps-cs-s/APNQkAGag0VLevHCsTHhDlK95tp5oz82x5jCeIof-xVau_rViiNgCFEcFPKsH1LZ5CM1HkFmRhMH1tTXEWkANtLa8sCda9DP7Whkcphpp9YjHym9mU77UzkIf7osXRG1f_BK9UTJd0x50Q=w408-h272-k-no'
  },
  {
    id: 'orchid-forest',
    title: 'Orchid Forest Cikole',
    location: 'Lembang',
    rating: '4.7',
    description: 'Hutan anggrek terbesar di Indonesia dengan jembatan gantung kayu yang...',
    image: 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?q=80&w=600&auto=format&fit=crop'
  }
];

export function FavoritePageContent() {
  const [activeTab, setActiveTab] = useState<TabType>('Destinasi');
  const { addDestination } = usePlanner();
  const { showToast } = useToast();

  return (
    <main className="mx-auto max-w-[1180px] px-4 py-4 sm:px-8 sm:py-8">
      {/* Header Section */}
      <div className="mb-4 sm:mb-6">
        <h1 className="text-xl sm:text-[28px] font-bold text-[#112F43]">Favorit Saya</h1>
        <p className="text-xs sm:text-sm text-slate-500 mt-1.5 sm:mt-2 max-w-[600px] leading-relaxed">
          Semua destinasi, penginapan, dan itinerary yang kamu simpan ada di sini. Rencanakan perjalanan impianmu dengan mudah dari koleksi pilihanmu.
        </p>
      </div>

      {/* 3 Summary Cards */}
      <div className="grid grid-cols-3 gap-2 sm:gap-6 mb-6 sm:mb-8">
        <div className="bg-white rounded-xl sm:rounded-2xl border border-slate-200 p-2.5 sm:p-6 flex flex-col sm:flex-row items-center sm:gap-6 shadow-sm text-center sm:text-left">
          <div className="h-8 w-8 sm:h-14 sm:w-14 rounded-lg sm:rounded-xl bg-[#EAF6FC] flex items-center justify-center text-[#0E75BC] shrink-0 mb-1.5 sm:mb-0">
            <MapPin className="h-4 w-4 sm:h-6 sm:w-6" />
          </div>
          <div>
            <p className="text-[7px] sm:text-[11px] font-bold text-slate-500 uppercase tracking-widest line-clamp-1">Destinasi</p>
            <p className="text-base sm:text-[32px] font-black text-[#0B5C73] leading-none mt-0.5 sm:mt-1">12</p>
          </div>
        </div>
        <div className="bg-white rounded-xl sm:rounded-2xl border border-slate-200 p-2.5 sm:p-6 flex flex-col sm:flex-row items-center sm:gap-6 shadow-sm text-center sm:text-left">
          <div className="h-8 w-8 sm:h-14 sm:w-14 rounded-lg sm:rounded-xl bg-[#EAF6FC] flex items-center justify-center text-[#0E75BC] shrink-0 mb-1.5 sm:mb-0">
            <Building className="h-4 w-4 sm:h-6 sm:w-6" />
          </div>
          <div>
            <p className="text-[7px] sm:text-[11px] font-bold text-slate-500 uppercase tracking-widest line-clamp-1">Penginapan</p>
            <p className="text-base sm:text-[32px] font-black text-[#0B5C73] leading-none mt-0.5 sm:mt-1">5</p>
          </div>
        </div>
        <div className="bg-white rounded-xl sm:rounded-2xl border border-slate-200 p-2.5 sm:p-6 flex flex-col sm:flex-row items-center sm:gap-6 shadow-sm text-center sm:text-left">
          <div className="h-8 w-8 sm:h-14 sm:w-14 rounded-lg sm:rounded-xl bg-[#FCD3D1] flex items-center justify-center text-[#E94B35] shrink-0 mb-1.5 sm:mb-0">
            <Map className="h-4 w-4 sm:h-6 sm:w-6" />
          </div>
          <div>
            <p className="text-[7px] sm:text-[11px] font-bold text-slate-500 uppercase tracking-widest line-clamp-1">Itinerary</p>
            <p className="text-base sm:text-[32px] font-black text-[#112F43] leading-none mt-0.5 sm:mt-1">3</p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex w-full sm:w-auto items-center gap-1 sm:gap-2 mb-6 sm:mb-8 bg-[#EAF6FC] p-1.5 rounded-xl sm:rounded-full">
        {(['Destinasi', 'Penginapan', 'Itinerary'] as TabType[]).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`flex-1 sm:flex-none px-4 py-2.5 sm:px-8 sm:py-2.5 rounded-lg sm:rounded-full text-xs sm:text-sm font-bold transition-all ${
              activeTab === tab 
                ? 'bg-[#00526E] text-white shadow-md' 
                : 'text-slate-500 hover:text-[#00526E]'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Grid Content */}
      {activeTab === 'Destinasi' && (
        <div className="grid grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-6">
          {MOCK_FAVORITE_DESTINATIONS.map((dest) => (
            <article key={dest.id} className="overflow-hidden rounded-xl sm:rounded-2xl border border-slate-200 bg-white shadow-sm flex flex-col">
              <div className="relative h-[120px] sm:h-[200px] w-full bg-slate-100">
                <Image 
                  src={dest.image} 
                  alt={dest.title} 
                  fill 
                  className="object-cover" 
                />
                <div className="absolute top-2 right-2 sm:top-4 sm:right-4 h-6 w-6 sm:h-9 sm:w-9 bg-white rounded-full flex items-center justify-center shadow-sm text-[#E94B35]">
                  <Heart className="h-3 w-3 sm:h-5 sm:w-5 fill-current" />
                </div>
                <div className="absolute bottom-2 left-2 sm:bottom-4 sm:left-4 bg-[#7FE0F4] text-[#0B5C73] px-2 py-0.5 sm:px-3 sm:py-1 rounded-full text-[8px] sm:text-[11px] font-bold shadow-sm line-clamp-1 max-w-[80%]">
                  {dest.location}
                </div>
              </div>
              <div className="p-3 sm:p-5 flex-1 flex flex-col">
                <div className="flex flex-col sm:flex-row items-start justify-between gap-1 sm:gap-2 mb-1.5 sm:mb-2">
                  <h3 className="text-[12px] sm:text-[17px] font-bold text-[#112F43] leading-tight line-clamp-1">{dest.title}</h3>
                  <div className="flex items-center gap-1 text-[9px] sm:text-[13px] font-bold text-[#112F43] shrink-0">
                    <Star className="h-2.5 w-2.5 sm:h-3.5 sm:w-3.5 fill-current text-[#FBBF24]" />
                    {dest.rating}
                  </div>
                </div>
                <p className="hidden sm:block text-[11px] sm:text-[13px] text-slate-500 leading-relaxed mb-4 sm:mb-6 flex-1 line-clamp-2">
                  {dest.description}
                </p>
                <div className="space-y-1.5 sm:space-y-2 mt-auto">
                  <button 
                    onClick={() => {
                      addDestination({ id: dest.id, title: dest.title });
                      showToast(`${dest.title} ditambahkan ke perjalanan!`, 'success');
                    }}
                    className="w-full bg-[#00526E] text-white font-bold text-[9px] sm:text-[13px] py-1.5 sm:py-3 rounded-md sm:rounded-xl transition-colors hover:bg-[#00415C]"
                  >
                    Tambah
                  </button>
                  <button className="w-full bg-white text-[#00526E] border border-[#00526E] font-bold text-[9px] sm:text-[13px] py-1.5 sm:py-3 rounded-md sm:rounded-xl transition-colors hover:bg-slate-50">
                    Detail
                  </button>
                </div>
              </div>
            </article>
          ))}
        </div>
      )}

      {activeTab === 'Penginapan' && (
        <div className="flex flex-col items-center justify-center py-12 sm:py-20 px-4 bg-white rounded-xl sm:rounded-2xl border border-slate-200 shadow-sm text-center">
          <div className="h-12 w-12 sm:h-16 sm:w-16 bg-[#EAF6FC] rounded-full flex items-center justify-center text-[#0E75BC] mb-3 sm:mb-4">
            <Building className="h-6 w-6 sm:h-8 sm:w-8" />
          </div>
          <h3 className="text-[15px] sm:text-[18px] font-bold text-[#112F43] mb-1.5 sm:mb-2">Belum Ada Penginapan Tersimpan</h3>
          <p className="text-xs sm:text-sm text-slate-500 mb-4 sm:mb-6 max-w-sm">Temukan penginapan terbaik untuk perjalananmu dan simpan di sini agar mudah diakses nanti.</p>
          <Link href="/planner/penginapan" className="inline-flex items-center gap-1.5 sm:gap-2 bg-[#00526E] text-white px-5 py-2 sm:px-6 sm:py-2.5 rounded-full font-bold text-[11px] sm:text-sm transition-colors hover:bg-[#00415C]">
            <PlusCircle className="h-3.5 w-3.5 sm:h-4 sm:w-4" /> Cari Penginapan
          </Link>
        </div>
      )}

      {activeTab === 'Itinerary' && (
        <div className="flex flex-col items-center justify-center py-12 sm:py-20 px-4 bg-white rounded-xl sm:rounded-2xl border border-slate-200 shadow-sm text-center">
          <div className="h-12 w-12 sm:h-16 sm:w-16 bg-[#EAF6FC] rounded-full flex items-center justify-center text-[#0E75BC] mb-3 sm:mb-4">
            <Map className="h-6 w-6 sm:h-8 sm:w-8" />
          </div>
          <h3 className="text-[15px] sm:text-[18px] font-bold text-[#112F43] mb-1.5 sm:mb-2">Belum Ada Itinerary</h3>
          <p className="text-xs sm:text-sm text-slate-500 mb-4 sm:mb-6 max-w-sm">Gunakan bantuan AI kami untuk merencanakan perjalanan yang sempurna di Bandung.</p>
          <Link href="/planner/itinerary" className="inline-flex items-center gap-1.5 sm:gap-2 bg-[#00526E] text-white px-5 py-2 sm:px-6 sm:py-2.5 rounded-full font-bold text-[11px] sm:text-sm transition-colors hover:bg-[#00415C]">
            <PlusCircle className="h-3.5 w-3.5 sm:h-4 sm:w-4" /> Buat Itinerary Baru
          </Link>
        </div>
      )}

    </main>
  );
}

function StarIcon({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="currentColor" className={className}>
      <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z" />
    </svg>
  );
}
