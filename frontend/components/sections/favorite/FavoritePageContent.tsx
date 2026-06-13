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
    image: '/destinations/kawah-putih.svg'
  },
  {
    id: 'lodge-maribaya',
    title: 'The Lodge Maribaya',
    location: 'Lembang',
    rating: '4.6',
    description: 'Kawasan wisata outdoor dengan pemandangan hutan pinus yang asri...',
    image: 'https://images.unsplash.com/photo-1524661135-423995f22d0b?q=80&w=600&auto=format&fit=crop'
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
    <main className="mx-auto max-w-[1180px] px-4 py-8 sm:px-8">
      {/* Header Section */}
      <div className="mb-8">
        <h1 className="text-[28px] font-bold text-[#112F43]">Favorit Saya</h1>
        <p className="text-sm text-slate-500 mt-2 max-w-[600px] leading-relaxed">
          Semua destinasi, penginapan, dan itinerary yang kamu simpan ada di sini. Rencanakan perjalanan impianmu dengan mudah dari koleksi pilihanmu.
        </p>
      </div>

      {/* 3 Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
        <div className="bg-white rounded-2xl border border-slate-200 p-6 flex items-center gap-6 shadow-sm">
          <div className="h-14 w-14 rounded-xl bg-[#EAF6FC] flex items-center justify-center text-[#0E75BC] shrink-0">
            <MapPin className="h-6 w-6" />
          </div>
          <div>
            <p className="text-[11px] font-bold text-slate-500 uppercase tracking-widest">Destinasi Favorit</p>
            <p className="text-[32px] font-black text-[#0B5C73] leading-none mt-1">12</p>
          </div>
        </div>
        <div className="bg-white rounded-2xl border border-slate-200 p-6 flex items-center gap-6 shadow-sm">
          <div className="h-14 w-14 rounded-xl bg-[#EAF6FC] flex items-center justify-center text-[#0E75BC] shrink-0">
            <Building className="h-6 w-6" />
          </div>
          <div>
            <p className="text-[11px] font-bold text-slate-500 uppercase tracking-widest">Penginapan Favorit</p>
            <p className="text-[32px] font-black text-[#0B5C73] leading-none mt-1">5</p>
          </div>
        </div>
        <div className="bg-white rounded-2xl border border-slate-200 p-6 flex items-center gap-6 shadow-sm">
          <div className="h-14 w-14 rounded-xl bg-[#FCD3D1] flex items-center justify-center text-[#E94B35] shrink-0">
            <Map className="h-6 w-6" />
          </div>
          <div>
            <p className="text-[11px] font-bold text-slate-500 uppercase tracking-widest">Itinerary Tersimpan</p>
            <p className="text-[32px] font-black text-[#112F43] leading-none mt-1">3</p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex flex-wrap items-center gap-2 mb-8 bg-[#EAF6FC] p-1.5 rounded-full inline-flex">
        {(['Destinasi', 'Penginapan', 'Itinerary'] as TabType[]).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-8 py-2.5 rounded-full text-sm font-bold transition-all ${
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
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {MOCK_FAVORITE_DESTINATIONS.map((dest) => (
            <article key={dest.id} className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm flex flex-col">
              <div className="relative h-[200px] w-full bg-slate-100">
                <Image 
                  src={dest.image} 
                  alt={dest.title} 
                  fill 
                  className="object-cover" 
                />
                <div className="absolute top-4 right-4 h-9 w-9 bg-white rounded-full flex items-center justify-center shadow-sm text-[#E94B35]">
                  <Heart className="h-5 w-5 fill-current" />
                </div>
                <div className="absolute bottom-4 left-4 bg-[#7FE0F4] text-[#0B5C73] px-3 py-1 rounded-full text-[11px] font-bold shadow-sm">
                  {dest.location}
                </div>
              </div>
              <div className="p-5 flex-1 flex flex-col">
                <div className="flex items-start justify-between gap-2 mb-2">
                  <h3 className="text-[17px] font-bold text-[#112F43] leading-tight">{dest.title}</h3>
                  <div className="flex items-center gap-1 text-[13px] font-bold text-[#112F43] shrink-0">
                    <Star className="h-3.5 w-3.5 fill-current text-[#FBBF24]" />
                    {dest.rating}
                  </div>
                </div>
                <p className="text-[13px] text-slate-500 leading-relaxed mb-6 flex-1">
                  {dest.description}
                </p>
                <div className="space-y-2 mt-auto">
                  <button 
                    onClick={() => {
                      addDestination({ id: dest.id, title: dest.title });
                      showToast(`${dest.title} ditambahkan ke perjalanan!`, 'success');
                    }}
                    className="w-full bg-[#00526E] text-white font-bold text-[13px] py-3 rounded-xl transition-colors hover:bg-[#00415C]"
                  >
                    Tambahkan ke Perjalanan
                  </button>
                  <button className="w-full bg-white text-[#00526E] border border-[#00526E] font-bold text-[13px] py-3 rounded-xl transition-colors hover:bg-slate-50">
                    Lihat Detail
                  </button>
                </div>
              </div>
            </article>
          ))}
        </div>
      )}

      {activeTab === 'Penginapan' && (
        <div className="flex flex-col items-center justify-center py-20 px-4 bg-white rounded-2xl border border-slate-200 shadow-sm text-center">
          <div className="h-16 w-16 bg-[#EAF6FC] rounded-full flex items-center justify-center text-[#0E75BC] mb-4">
            <Building className="h-8 w-8" />
          </div>
          <h3 className="text-[18px] font-bold text-[#112F43] mb-2">Belum Ada Penginapan Tersimpan</h3>
          <p className="text-slate-500 mb-6 max-w-sm">Temukan penginapan terbaik untuk perjalananmu dan simpan di sini agar mudah diakses nanti.</p>
          <Link href="/planner/penginapan" className="inline-flex items-center gap-2 bg-[#00526E] text-white px-6 py-2.5 rounded-full font-bold text-sm transition-colors hover:bg-[#00415C]">
            <PlusCircle className="h-4 w-4" /> Cari Penginapan
          </Link>
        </div>
      )}

      {activeTab === 'Itinerary' && (
        <div className="flex flex-col items-center justify-center py-20 px-4 bg-white rounded-2xl border border-slate-200 shadow-sm text-center">
          <div className="h-16 w-16 bg-[#EAF6FC] rounded-full flex items-center justify-center text-[#0E75BC] mb-4">
            <Map className="h-8 w-8" />
          </div>
          <h3 className="text-[18px] font-bold text-[#112F43] mb-2">Belum Ada Itinerary</h3>
          <p className="text-slate-500 mb-6 max-w-sm">Gunakan bantuan AI kami untuk merencanakan perjalanan yang sempurna di Bandung.</p>
          <Link href="/planner/itinerary" className="inline-flex items-center gap-2 bg-[#00526E] text-white px-6 py-2.5 rounded-full font-bold text-sm transition-colors hover:bg-[#00415C]">
            <PlusCircle className="h-4 w-4" /> Buat Itinerary Baru
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
