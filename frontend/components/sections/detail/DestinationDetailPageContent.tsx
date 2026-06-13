"use client";

import Image from 'next/image';
import Link from 'next/link';
import { usePlanner } from '@/context/PlannerContext';
import { useToast } from '@/context/ToastContext';
import { ArrowLeft, MapPin, Ticket, Clock, Sparkles, Star, Car, Droplets, Book, Utensils, Camera, Accessibility, Heart, Share2, Building } from 'lucide-react';
import type { DestinationDetail } from '@/types';
import { useState } from 'react';

export function DestinationDetailPageContent({ destination }: { destination: DestinationDetail }) {
  const { addDestination } = usePlanner();
  const { showToast } = useToast();
  const [isFavorite, setIsFavorite] = useState(false);

  const handleAddTrip = () => {
    addDestination({ id: destination.id, title: destination.title });
    showToast(`${destination.title} berhasil ditambahkan ke perjalanan!`, 'success');
  };

  return (
    <>
      <main className="mx-auto max-w-[1180px] px-4 py-6 sm:px-8 pb-32">
        {/* HERO SECTION */}
        <section className="relative overflow-hidden rounded-[24px] bg-slate-900 h-[450px]">
          <Image
            src={destination.heroImage}
            alt={destination.title}
            fill
            sizes="100vw"
            className="object-cover object-center opacity-90"
            priority
          />
          {/* Gradient Overlay for Text Visibility */}
          <div className="absolute inset-0 bg-gradient-to-t from-slate-900/90 via-slate-900/20 to-transparent" />
          
          {/* Top Left Back Button */}
          <div className="absolute top-6 left-6 z-10">
            <Link
              href="/explore"
              className="inline-flex items-center gap-2 rounded-full bg-white/95 px-5 py-2.5 text-[13px] font-bold text-[#0E75BC] shadow-sm transition-colors hover:bg-white"
            >
              <ArrowLeft className="h-4 w-4" />
              Kembali ke Explore
            </Link>
          </div>

          {/* Bottom Left Content */}
          <div className="absolute bottom-16 left-6 sm:left-10 z-10 text-white">
            <span className="inline-block rounded-full bg-[#0E75BC] px-3 py-1 text-[11px] font-bold uppercase tracking-wider text-white shadow-sm mb-3">
              {destination.category}
            </span>
            <h1 className="text-4xl sm:text-5xl font-black leading-tight drop-shadow-md">
              {destination.title}
            </h1>
          </div>
        </section>

        {/* METRIC BAR (Overlapping Hero) */}
        <section className="relative z-20 mx-4 sm:mx-10 -mt-8 flex flex-wrap items-center justify-between rounded-[20px] bg-white px-8 py-5 shadow-[0_12px_24px_rgba(0,0,0,0.06)] border border-slate-100">
          <div className="flex items-center gap-4 py-2 flex-1 min-w-[200px]">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#FFF4ED] text-[#F97316]">
              <Star className="h-5 w-5 fill-current" />
            </div>
            <div>
              <p className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Rating</p>
              <p className="text-[15px] font-bold text-slate-900">{destination.rating} / 5.0</p>
            </div>
          </div>
          
          <div className="hidden sm:block w-px h-10 bg-slate-200" />
          
          <div className="flex items-center gap-4 py-2 flex-1 min-w-[200px] sm:pl-8">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#EAF6FC] text-[#0E75BC]">
              <MapPin className="h-5 w-5" />
            </div>
            <div>
              <p className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Lokasi</p>
              <p className="text-[15px] font-bold text-slate-900">{destination.location}</p>
            </div>
          </div>

          <div className="hidden lg:block w-px h-10 bg-slate-200" />

          <div className="flex items-center gap-4 py-2 flex-1 min-w-[200px] lg:pl-8">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#EAF6FC] text-[#10B981]">
              <Ticket className="h-5 w-5" />
            </div>
            <div>
              <p className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Tiket</p>
              <p className="text-[15px] font-bold text-slate-900">{destination.price}</p>
            </div>
          </div>

          <div className="hidden lg:block w-px h-10 bg-slate-200" />

          <div className="flex items-center gap-4 py-2 flex-1 min-w-[200px] lg:pl-8">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#EAF6FC] text-[#6366F1]">
              <Clock className="h-5 w-5" />
            </div>
            <div>
              <p className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Jam Buka</p>
              <p className="text-[15px] font-bold text-slate-900">07:00 - 17:00</p>
            </div>
          </div>
        </section>

        {/* MAIN LAYOUT (Left Content + Right Sidebar) */}
        <div className="mt-12 grid gap-10 lg:grid-cols-[1fr_360px] items-start">
          
          {/* KOLOM KIRI */}
          <div className="space-y-12">
            
            {/* AI Insight */}
            <section className="relative overflow-hidden rounded-[20px] bg-[#EAF6FC] border border-[#CDE3F3] p-6">
              <div className="flex items-start gap-4 relative z-10">
                <Sparkles className="h-6 w-6 text-[#0E75BC] shrink-0 mt-0.5" />
                <div>
                  <h3 className="text-[14px] font-bold text-[#0E75BC] uppercase tracking-wide">Mengapa Cepot AI Merekomendasikan Ini?</h3>
                  <p className="mt-2 text-[14px] leading-relaxed text-[#0A415C]">
                    {destination.aiReason}
                  </p>
                </div>
              </div>
            </section>

            {/* Tentang Destinasi */}
            <section>
              <h2 className="text-2xl font-bold text-slate-900 mb-4">Tentang Destinasi</h2>
              <div className="text-[15px] leading-relaxed text-slate-600 space-y-4 whitespace-pre-line">
                {destination.description}
              </div>
            </section>

            {/* Galeri Foto */}
            <section>
              <h2 className="text-2xl font-bold text-slate-900 mb-4">Galeri Foto</h2>
              <div className="grid grid-cols-2 gap-3 h-[400px]">
                <div className="grid grid-rows-2 gap-3">
                  <div className="relative rounded-2xl overflow-hidden bg-slate-100">
                    <Image src={destination.gallery[0] || destination.heroImage} alt="Gallery 1" fill className="object-cover" />
                  </div>
                  <div className="relative rounded-2xl overflow-hidden bg-slate-100">
                    <Image src={destination.gallery[1] || destination.heroImage} alt="Gallery 2" fill className="object-cover" />
                  </div>
                </div>
                <div className="relative rounded-2xl overflow-hidden bg-slate-100">
                  <div className="absolute inset-0 grid grid-rows-2 gap-3 p-0">
                     <div className="relative bg-slate-200 rounded-2xl overflow-hidden"><Image src={destination.gallery[2] || destination.heroImage} alt="Gallery 3" fill className="object-cover" /></div>
                     <div className="relative bg-slate-300 rounded-2xl overflow-hidden"><Image src={destination.gallery[3] || destination.heroImage} alt="Gallery 4" fill className="object-cover" /></div>
                  </div>
                </div>
              </div>
            </section>

            {/* Fasilitas */}
            <section>
              <h2 className="text-2xl font-bold text-slate-900 mb-4">Fasilitas</h2>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                {destination.facilities.map((facility) => {
                  let Icon = Book; // fallback
                  if (facility.toLowerCase().includes('parkir')) Icon = Car;
                  else if (facility.toLowerCase().includes('toilet')) Icon = Droplets;
                  else if (facility.toLowerCase().includes('mushola')) Icon = Book;
                  else if (facility.toLowerCase().includes('makan') || facility.toLowerCase().includes('cafe') || facility.toLowerCase().includes('resto') || facility.toLowerCase().includes('warung')) Icon = Utensils;
                  else if (facility.toLowerCase().includes('foto')) Icon = Camera;
                  else if (facility.toLowerCase().includes('difabel')) Icon = Accessibility;
                  else Icon = Star;

                  return (
                    <div key={facility} className="flex items-center gap-3 bg-white border border-slate-200 rounded-xl px-4 py-3 shadow-sm">
                      <Icon className="h-5 w-5 text-[#0E75BC]" />
                      <span className="text-[13px] font-bold text-slate-700">{facility}</span>
                    </div>
                  );
                })}
              </div>
            </section>

            {/* Ulasan Pengunjung */}
            <section>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-2xl font-bold text-slate-900">Ulasan Pengunjung</h2>
                <button className="text-[13px] font-bold text-[#0E75BC] hover:underline">Lihat Semua &gt;</button>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                {destination.reviews.slice(0, 3).map((rev, i) => (
                  <div key={i} className="bg-[#F8FAFC] border border-slate-200 rounded-2xl p-5">
                    <div className="flex items-center gap-3 mb-3">
                      <div className="h-10 w-10 rounded-full bg-slate-300 overflow-hidden bg-gradient-to-br from-blue-200 to-orange-200" />
                      <div>
                        <p className="text-[13px] font-bold text-slate-900">{rev.name}</p>
                        <div className="flex items-center text-[#F97316]">
                          {[...Array(5)].map((_, j) => (
                            <Star key={j} className={`h-3 w-3 ${j < Number(rev.rating) ? 'fill-current' : 'text-slate-300'}`} />
                          ))}
                        </div>
                      </div>
                    </div>
                    <p className="text-[13px] text-slate-600 leading-relaxed italic">&quot;{rev.comment}&quot;</p>
                  </div>
                ))}
              </div>
            </section>

          </div>

          {/* KOLOM KANAN (Sidebar) */}
          <div className="space-y-8 lg:sticky lg:top-24">
            
            {/* Lokasi */}
            <section className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm">
              <h2 className="text-[16px] font-bold text-slate-900 mb-4">Lokasi</h2>
              <div className="w-full h-[180px] bg-slate-200 rounded-xl overflow-hidden relative mb-4">
                {/* Mock Map Image */}
                <Image src="/images/background.png" alt="Map Route" fill className="object-cover opacity-70" />
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="h-10 w-10 bg-white rounded-full flex items-center justify-center shadow-lg text-[#E94B35]">
                    <MapPin className="h-6 w-6" />
                  </div>
                </div>
              </div>
              <p className="text-[13px] text-slate-600 leading-relaxed mb-5">
                {destination.location}
              </p>
              <button className="w-full bg-[#EAF6FC] text-[#0E75BC] font-bold text-[13px] py-3 rounded-xl transition-colors hover:bg-[#d6eefb] flex items-center justify-center gap-2">
                <Share2 className="h-4 w-4" /> Lihat Rute
              </button>
            </section>

            {/* Penginapan Terdekat */}
            <section>
              <h2 className="text-[16px] font-bold text-slate-900 mb-4 flex items-center gap-2">
                <Building className="h-5 w-5 text-[#E94B35]" /> Penginapan Terdekat
              </h2>
              <div className="space-y-3">
                {destination.nearbyStays.slice(0, 3).map((stay, idx) => (
                  <div key={idx} className="bg-white border border-slate-200 rounded-2xl p-3 flex gap-4 items-center shadow-sm hover:border-[#0E75BC] transition-colors cursor-pointer">
                    <div className="relative h-16 w-16 rounded-xl overflow-hidden shrink-0">
                      <Image src={stay.image} alt={stay.name} fill className="object-cover" />
                    </div>
                    <div>
                      <h4 className="text-[14px] font-bold text-slate-900">{stay.name}</h4>
                      <p className="text-[11px] text-slate-500 mt-0.5">{stay.location}</p>
                      <p className="text-[13px] font-bold text-[#0E75BC] mt-1">{stay.price}</p>
                    </div>
                  </div>
                ))}
              </div>
            </section>

          </div>

        </div>

        {/* ACTION BAR (Above Apa Selanjutnya) */}
        <section className="mt-12 mb-8 bg-white border border-slate-200 shadow-sm rounded-2xl px-6 py-5">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-5">
              <div className="hidden sm:flex h-12 w-12 rounded-full bg-[#333333] items-center justify-center text-white font-bold text-xl">
                N
              </div>
              <div className="flex flex-col">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">TIKET MASUK MULAI</span>
                <div className="flex items-end gap-1">
                  <span className="text-xl sm:text-2xl font-black text-[#0B5C73] leading-none">{destination.price}</span>
                </div>
              </div>
            </div>
            <div className="flex w-full sm:w-auto items-center gap-3">
              <button 
                onClick={() => setIsFavorite(!isFavorite)}
                className={`flex-1 sm:flex-none flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl text-[13px] font-bold transition-all border-2 ${
                  isFavorite 
                    ? 'bg-[#EAF6FC] border-[#0E75BC] text-[#0E75BC]' 
                    : 'bg-white border-slate-300 text-slate-600 hover:border-[#0E75BC] hover:text-[#0E75BC]'
                }`}
              >
                <Heart className={`h-4 w-4 ${isFavorite ? 'fill-current' : ''}`} />
                Simpan ke Favorit
              </button>
              <button 
                onClick={handleAddTrip}
                className="flex-1 sm:flex-none px-8 py-3.5 rounded-xl bg-[#E94B35] text-white text-[13px] font-bold shadow-md transition-colors hover:bg-[#d6412e]"
              >
                Tambah ke Perjalanan
              </button>
            </div>
          </div>
        </section>

        {/* APA SELANJUTNYA? Section */}
        <section className="mt-8 border-t border-slate-200 pt-16 mb-10">
          <div className="text-center mb-10">
            <h2 className="text-2xl font-bold text-[#0E75BC]">Apa Selanjutnya?</h2>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center max-w-[900px] mx-auto">
            <div className="flex flex-col items-center">
              <div className="h-16 w-16 bg-[#4F46E5] text-white rounded-full flex items-center justify-center mb-4 shadow-lg shadow-indigo-200">
                <MapPin className="h-7 w-7" />
              </div>
              <h4 className="text-[14px] font-bold text-slate-900">1. Tambahkan ke perjalanan</h4>
              <p className="text-[12px] text-slate-500 mt-1">Pilih destinasi lainnya untuk mulai menyusun rencana.</p>
            </div>
            <div className="flex flex-col items-center">
              <div className="h-16 w-16 bg-[#10B981] text-white rounded-full flex items-center justify-center mb-4 shadow-lg shadow-emerald-200">
                <Sparkles className="h-7 w-7" />
              </div>
              <h4 className="text-[14px] font-bold text-slate-900">2. Rekomendasi AI</h4>
              <p className="text-[12px] text-slate-500 mt-1">Cepot AI menyarankan tempat menarik dari di sekitar.</p>
            </div>
            <div className="flex flex-col items-center">
              <div className="h-16 w-16 bg-[#F97316] text-white rounded-full flex items-center justify-center mb-4 shadow-lg shadow-orange-200">
                <Building className="h-7 w-7" />
              </div>
              <h4 className="text-[14px] font-bold text-slate-900">3. Pilih Penginapan</h4>
              <p className="text-[12px] text-slate-500 mt-1">Dapatkan pilihan hotel dan villa terbaik sesuai budget.</p>
            </div>
            <div className="flex flex-col items-center">
              <div className="h-16 w-16 bg-[#0E75BC] text-white rounded-full flex items-center justify-center mb-4 shadow-lg shadow-blue-200">
                <Share2 className="h-7 w-7" />
              </div>
              <h4 className="text-[14px] font-bold text-slate-900">4. Itinerary Personal</h4>
              <p className="text-[12px] text-slate-500 mt-1">Jadwal perjalanan lengkap dibuat otomatis untukmu.</p>
            </div>
          </div>
        </section>

      </main>
    </>
  );
}
