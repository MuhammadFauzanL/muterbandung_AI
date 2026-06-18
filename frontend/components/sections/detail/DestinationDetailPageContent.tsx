"use client";

import { SafeImage } from '@/components/ui/SafeImage';
import Link from 'next/link';
import { usePlanner } from '@/context/PlannerContext';
import { useToast } from '@/context/ToastContext';
import { useFavorite } from '@/context/FavoriteContext';
import { accommodationsService } from '@/services/accommodations';
import { trackViewDetail, trackPlannerAdd } from '@/services/userEvents';
import { ArrowLeft, MapPin, Ticket, Clock, Sparkles, Star, Car, Droplets, Book, Utensils, Camera, Accessibility, Heart, Share2, Building } from 'lucide-react';
import type { Accommodation, DestinationDetail } from '@/types';
import { useEffect, useState } from 'react';

export function DestinationDetailPageContent({ destination }: { destination: DestinationDetail }) {
  const { addDestination } = usePlanner();
  const { showToast } = useToast();
  const { isFavorite, toggleFavorite } = useFavorite();
  const favorited = isFavorite(destination.id);
  const [nearbyAccommodations, setNearbyAccommodations] = useState<Accommodation[]>([]);
  const [accommodationsLoading, setAccommodationsLoading] = useState(false);

  // Track view_detail event on mount
  useEffect(() => {
    trackViewDetail(destination.id);
  }, [destination.id]);

  useEffect(() => {
    if (!destination.slug) return;
    let active = true;
    const timeoutId = window.setTimeout(() => {
      setAccommodationsLoading(true);
      accommodationsService
        .getNearbyForDestination(destination.slug!, {
          limit: 3,
          radiusKm: 10,
          sort: 'recommended',
        })
        .then((result) => {
          if (active) setNearbyAccommodations(result.data);
        })
        .catch(() => {
          if (active) setNearbyAccommodations([]);
        })
        .finally(() => {
          if (active) setAccommodationsLoading(false);
        });
    }, 0);
    return () => {
      active = false;
      window.clearTimeout(timeoutId);
    };
  }, [destination.slug]);

  const handleAddTrip = () => {
    addDestination({ id: destination.id, title: destination.title });
    trackPlannerAdd(destination.id);
    showToast(`${destination.title} berhasil ditambahkan ke perjalanan!`, 'success');
  };

  return (
    <>
      <main className="mx-auto max-w-[1180px] px-4 py-4 sm:px-8 pb-6 sm:pb-12">
        {/* HERO SECTION */}
        <section className="relative overflow-hidden rounded-[20px] bg-slate-900 h-[260px] sm:h-[400px]">
          <SafeImage
            src={destination.heroImage}
            alt={destination.title}
            fill
            sizes="100vw"
            className="object-cover object-center opacity-90"
            priority
            category={destination.category}
          />
          {/* Gradient Overlay for Text Visibility */}
          <div className="absolute inset-0 bg-gradient-to-t from-slate-900/90 via-slate-900/20 to-transparent" />
          
          {/* Top Left Back Button */}
          <div className="absolute top-4 left-4 sm:top-6 sm:left-6 z-10">
            <Link
              href="/explore"
              className="inline-flex items-center gap-1.5 rounded-full bg-white/95 px-4 py-2 sm:px-5 sm:py-2.5 text-[12px] sm:text-[13px] font-bold text-[#0E75BC] shadow-sm transition-colors hover:bg-white"
            >
              <ArrowLeft className="h-3.5 w-3.5 sm:h-4 sm:w-4" />
              Kembali
            </Link>
          </div>

          {/* Bottom Left Content */}
          <div className="absolute bottom-6 left-4 sm:bottom-16 sm:left-10 z-10 text-white pr-4">
            <span className="inline-block rounded-full bg-[#0E75BC] px-2.5 py-0.5 sm:px-3 sm:py-1 text-[9px] sm:text-[11px] font-bold uppercase tracking-wider text-white shadow-sm mb-2 sm:mb-3">
              {destination.category}
            </span>
            <h1 className="text-[22px] sm:text-4xl font-black leading-tight drop-shadow-md">
              {destination.title}
            </h1>
          </div>
        </section>

        {/* METRIC BAR (Overlapping Hero) */}
        <section className="relative z-20 mx-4 sm:mx-10 -mt-6 sm:-mt-8 grid grid-cols-2 sm:flex sm:flex-wrap items-center justify-between rounded-[16px] bg-white px-4 py-3 sm:px-8 sm:py-5 shadow-[0_8px_16px_rgba(0,0,0,0.06)] border border-slate-100 gap-3 sm:gap-0">
          <div className="flex items-center gap-2.5 sm:gap-4 flex-1">
            <div className="flex h-7 w-7 sm:h-10 sm:w-10 items-center justify-center rounded-full bg-[#FFF4ED] text-[#F97316]">
              <Star className="h-3.5 w-3.5 sm:h-5 sm:w-5 fill-current" />
            </div>
            <div>
              <p className="text-[9px] sm:text-[11px] font-bold text-slate-400 uppercase tracking-wider">Rating</p>
              <p className="text-[12px] sm:text-[15px] font-bold text-slate-900 leading-tight">{destination.rating} / 5.0</p>
            </div>
          </div>
          
          <div className="hidden sm:block w-px h-10 bg-slate-200" />
          
          <div className="flex items-center gap-2.5 sm:gap-4 flex-1 sm:pl-8">
            <div className="flex h-7 w-7 sm:h-10 sm:w-10 items-center justify-center rounded-full bg-[#EAF6FC] text-[#0E75BC]">
              <MapPin className="h-3.5 w-3.5 sm:h-5 sm:w-5" />
            </div>
            <div>
              <p className="text-[9px] sm:text-[11px] font-bold text-slate-400 uppercase tracking-wider">Lokasi</p>
              <p className="text-[12px] sm:text-[15px] font-bold text-slate-900 leading-tight truncate max-w-[100px] sm:max-w-none">{destination.location.split(',')[0]}</p>
            </div>
          </div>

          <div className="hidden lg:block w-px h-10 bg-slate-200" />

          <div className="flex items-center gap-2.5 sm:gap-4 flex-1 lg:pl-8">
            <div className="flex h-7 w-7 sm:h-10 sm:w-10 items-center justify-center rounded-full bg-[#EAF6FC] text-[#10B981]">
              <Ticket className="h-3.5 w-3.5 sm:h-5 sm:w-5" />
            </div>
            <div>
              <p className="text-[9px] sm:text-[11px] font-bold text-slate-400 uppercase tracking-wider">Tiket</p>
              <p className="text-[12px] sm:text-[15px] font-bold text-slate-900 leading-tight">{destination.price}</p>
            </div>
          </div>

          <div className="hidden lg:block w-px h-10 bg-slate-200" />

          <div className="flex items-center gap-2.5 sm:gap-4 flex-1 lg:pl-8">
            <div className="flex h-7 w-7 sm:h-10 sm:w-10 items-center justify-center rounded-full bg-[#EAF6FC] text-[#6366F1]">
              <Clock className="h-3.5 w-3.5 sm:h-5 sm:w-5" />
            </div>
            <div>
              <p className="text-[9px] sm:text-[11px] font-bold text-slate-400 uppercase tracking-wider">Jam</p>
              <p className="text-[12px] sm:text-[15px] font-bold text-slate-900 leading-tight">07:00 - 17:00</p>
            </div>
          </div>
        </section>

        {/* MAIN LAYOUT (Left Content + Right Sidebar) */}
        <div className="mt-6 sm:mt-12 grid gap-6 sm:gap-10 lg:grid-cols-[1fr_360px] items-start">
          
          {/* KOLOM KIRI */}
          <div className="space-y-6 sm:space-y-12">
            
            {/* AI Insight */}
            <section className="relative overflow-hidden rounded-[16px] bg-[#EAF6FC] border border-[#CDE3F3] p-4 sm:p-6">
              <div className="flex items-start gap-3 sm:gap-4 relative z-10">
                <Sparkles className="h-4 w-4 sm:h-6 sm:w-6 text-[#0E75BC] shrink-0 mt-0.5" />
                <div>
                  <h3 className="text-[12px] sm:text-[14px] font-bold text-[#0E75BC] uppercase tracking-wide">Mengapa Cepot AI Merekomendasikan Ini?</h3>
                  <p className="mt-1 sm:mt-2 text-[12px] sm:text-[14px] leading-relaxed text-[#0A415C]">
                    {destination.aiReason}
                  </p>
                </div>
              </div>
            </section>

            {/* Tentang Destinasi */}
            <section>
              <h2 className="text-[16px] sm:text-xl font-bold text-slate-900 mb-2 sm:mb-4">Tentang Destinasi</h2>
              <div className="text-[12px] sm:text-[15px] leading-relaxed text-slate-600 space-y-3 sm:space-y-4 whitespace-pre-line">
                {destination.description}
              </div>
            </section>

            {/* Galeri Foto */}
            <section>
              <h2 className="text-[16px] sm:text-xl font-bold text-slate-900 mb-2 sm:mb-4">Galeri Foto</h2>
              <div className="grid grid-cols-2 gap-2 sm:gap-3 h-[200px] sm:h-[400px]">
                <div className="grid grid-rows-2 gap-2 sm:gap-3">
                  <div className="relative rounded-xl sm:rounded-2xl overflow-hidden bg-slate-100">
                    <SafeImage src={destination.gallery[0] || destination.heroImage} alt="Gallery 1" fill className="object-cover" />
                  </div>
                  <div className="relative rounded-xl sm:rounded-2xl overflow-hidden bg-slate-100">
                    <SafeImage src={destination.gallery[1] || destination.heroImage} alt="Gallery 2" fill className="object-cover" />
                  </div>
                </div>
                <div className="relative rounded-xl sm:rounded-2xl overflow-hidden bg-slate-100">
                  <div className="absolute inset-0 grid grid-rows-2 gap-2 sm:gap-3 p-0">
                     <div className="relative bg-slate-200 rounded-xl sm:rounded-2xl overflow-hidden"><SafeImage src={destination.gallery[2] || destination.heroImage} alt="Gallery 3" fill className="object-cover" /></div>
                     <div className="relative bg-slate-300 rounded-xl sm:rounded-2xl overflow-hidden"><SafeImage src={destination.gallery[3] || destination.heroImage} alt="Gallery 4" fill className="object-cover" /></div>
                  </div>
                </div>
              </div>
            </section>

            {/* Fasilitas */}
            <section>
              <h2 className="text-[16px] sm:text-xl font-bold text-slate-900 mb-2 sm:mb-4">Fasilitas</h2>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 sm:gap-4">
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
                    <div key={facility} className="flex items-center gap-2 sm:gap-3 bg-white border border-slate-200 rounded-lg sm:rounded-xl px-3 py-2 sm:px-4 sm:py-3 shadow-sm">
                      <Icon className="h-4 w-4 sm:h-5 sm:w-5 text-[#0E75BC]" />
                      <span className="text-[11px] sm:text-[13px] font-bold text-slate-700">{facility}</span>
                    </div>
                  );
                })}
              </div>
            </section>

          </div>

          {/* KOLOM KANAN (Sidebar) */}
          <div className="space-y-6 sm:space-y-8 lg:sticky lg:top-24">
            
            {/* Lokasi */}
            <section className="bg-white rounded-xl sm:rounded-2xl border border-slate-200 p-4 sm:p-5 shadow-sm">
              <h2 className="text-[14px] sm:text-[16px] font-bold text-slate-900 mb-3 sm:mb-4">Lokasi</h2>
              <div className="w-full h-[120px] sm:h-[180px] bg-slate-200 rounded-lg sm:rounded-xl overflow-hidden relative mb-3 sm:mb-4">
                {/* Mock Map Image */}
                <SafeImage src="/images/background.png" alt="Map Route" fill className="object-cover opacity-70" />
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="h-8 w-8 sm:h-10 sm:w-10 bg-white rounded-full flex items-center justify-center shadow-lg text-[#E94B35]">
                    <MapPin className="h-4 w-4 sm:h-6 w-6" />
                  </div>
                </div>
              </div>
              <p className="text-[12px] sm:text-[13px] text-slate-600 leading-relaxed mb-4 sm:mb-5">
                {destination.location}
              </p>
              <button className="w-full bg-[#EAF6FC] text-[#0E75BC] font-bold text-[12px] sm:text-[13px] py-2.5 sm:py-3 rounded-xl transition-colors hover:bg-[#d6eefb] flex items-center justify-center gap-2">
                <Share2 className="h-3.5 w-3.5 sm:h-4 sm:w-4" /> Lihat Rute
              </button>
            </section>

            {/* Penginapan Terdekat */}
            <section>
              <div className="mb-3 sm:mb-4 flex items-center justify-between gap-3">
                <h2 className="text-[14px] sm:text-[16px] font-bold text-slate-900 flex items-center gap-2">
                  <Building className="h-4 w-4 sm:h-5 sm:w-5 text-[#E94B35]" /> Penginapan Terdekat
                </h2>
                {destination.slug && (
                  <Link
                    href={`/planner/penginapan?destination=${destination.slug}`}
                    className="text-[11px] sm:text-[12px] font-bold text-[#0E75BC] hover:underline"
                  >
                    Lihat Semua
                  </Link>
                )}
              </div>
              <div className="space-y-2 sm:space-y-3">
                {accommodationsLoading && (
                  [...Array(3)].map((_, idx) => (
                    <div key={idx} className="h-[76px] animate-pulse rounded-xl border border-slate-100 bg-slate-100" />
                  ))
                )}
                {!accommodationsLoading && nearbyAccommodations.length === 0 && (
                  <div className="rounded-xl border border-dashed border-slate-200 bg-white p-3 text-[12px] leading-5 text-slate-500">
                    Belum ada data penginapan terdekat yang bisa ditampilkan untuk destinasi ini.
                  </div>
                )}
                {!accommodationsLoading && nearbyAccommodations.map((stay) => (
                  <a
                    key={stay.id}
                    href={stay.mapsUrl || stay.bookingUrl || '#'}
                    target={stay.mapsUrl || stay.bookingUrl ? '_blank' : undefined}
                    rel={stay.mapsUrl || stay.bookingUrl ? 'noreferrer' : undefined}
                    className="bg-white border border-slate-200 rounded-xl p-2.5 sm:p-3 flex gap-3 sm:gap-4 items-center shadow-sm hover:border-[#0E75BC] transition-colors"
                  >
                    <div className="relative h-12 w-12 sm:h-16 w-16 rounded-lg sm:rounded-xl overflow-hidden shrink-0">
                      <SafeImage src={stay.image} alt={stay.name} fill className="object-cover" />
                    </div>
                    <div className="min-w-0">
                      <h4 className="text-[12px] sm:text-[14px] font-bold text-slate-900">{stay.name}</h4>
                      <p className="text-[10px] sm:text-[11px] text-slate-500 mt-0.5">{stay.distance}</p>
                      <p className="text-[11px] sm:text-[13px] font-bold text-[#0E75BC] mt-0.5 sm:mt-1">{stay.price}</p>
                    </div>
                  </a>
                ))}
              </div>
            </section>

          </div>

        </div>

        {/* ACTION BAR (Above Apa Selanjutnya) */}
        <section className="mt-8 sm:mt-12 mb-2 sm:mb-4 bg-white border border-slate-200 shadow-sm rounded-xl sm:rounded-2xl px-4 py-3 sm:px-6 sm:py-5">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-3 sm:gap-4">
            <div className="flex items-center gap-3 sm:gap-5 self-start sm:self-auto w-full sm:w-auto">
              <div className="hidden sm:flex h-12 w-12 rounded-full bg-[#333333] items-center justify-center text-white font-bold text-xl">
                N
              </div>
              <div className="flex flex-col w-full sm:w-auto">
                <span className="text-[9px] sm:text-[10px] font-bold text-slate-400 uppercase tracking-widest">TIKET MASUK MULAI</span>
                <div className="flex items-end gap-1 mt-0.5">
                  <span className="text-lg sm:text-2xl font-black text-[#0B5C73] leading-none">{destination.price}</span>
                </div>
              </div>
            </div>
            <div className="flex w-full sm:w-auto items-center gap-2 sm:gap-3">
              <button 
                onClick={() => toggleFavorite(destination.id)}
                className={`flex-1 sm:flex-none flex items-center justify-center gap-1.5 px-3 py-2.5 sm:px-6 sm:py-3.5 rounded-lg sm:rounded-xl text-[12px] sm:text-[13px] font-bold transition-all border-2 ${
                  favorited 
                    ? 'bg-[#EAF6FC] border-[#0E75BC] text-[#0E75BC]' 
                    : 'bg-white border-slate-300 text-slate-600 hover:border-[#0E75BC] hover:text-[#0E75BC]'
                }`}
              >
                <Heart className={`h-4 w-4 ${favorited ? 'fill-current' : ''}`} />
                <span className="hidden sm:inline">Simpan Favorit</span>
              </button>
              <button 
                onClick={handleAddTrip}
                className="flex-[2] sm:flex-none px-4 py-2.5 sm:px-8 sm:py-3.5 rounded-lg sm:rounded-xl bg-[#E94B35] text-white text-[12px] sm:text-[13px] font-bold shadow-md transition-colors hover:bg-[#d6412e] text-center"
              >
                Tambah ke Perjalanan
              </button>
            </div>
          </div>
        </section>

        {/* APA SELANJUTNYA? Section */}
        <section className="mt-2 mb-2 sm:mb-4">
          <div className="text-center mb-3 sm:mb-5">
            <h2 className="text-[14px] sm:text-[18px] font-bold text-[#0E75BC]">Apa Selanjutnya?</h2>
          </div>
          <div className="grid grid-cols-4 gap-2 sm:gap-6 text-center max-w-[900px] mx-auto">
            <div className="flex flex-col items-center">
              <div className="h-8 w-8 sm:h-12 sm:w-12 bg-[#4F46E5] text-white rounded-full flex items-center justify-center mb-1.5 sm:mb-3 shadow-sm">
                <MapPin className="h-4 w-4 sm:h-5 sm:w-5" />
              </div>
              <h4 className="text-[9px] sm:text-[13px] font-bold text-slate-900 leading-tight">1. Tambahkan</h4>
              <p className="hidden sm:block text-[11px] text-slate-500 mt-1">Pilih destinasi lainnya.</p>
            </div>
            <div className="flex flex-col items-center">
              <div className="h-8 w-8 sm:h-12 sm:w-12 bg-[#10B981] text-white rounded-full flex items-center justify-center mb-1.5 sm:mb-3 shadow-sm">
                <Sparkles className="h-4 w-4 sm:h-5 sm:w-5" />
              </div>
              <h4 className="text-[9px] sm:text-[13px] font-bold text-slate-900 leading-tight">2. Rekomendasi AI</h4>
              <p className="hidden sm:block text-[11px] text-slate-500 mt-1">Saran dari Cepot AI.</p>
            </div>
            <div className="flex flex-col items-center">
              <div className="h-8 w-8 sm:h-12 sm:w-12 bg-[#F97316] text-white rounded-full flex items-center justify-center mb-1.5 sm:mb-3 shadow-sm">
                <Building className="h-4 w-4 sm:h-5 sm:w-5" />
              </div>
              <h4 className="text-[9px] sm:text-[13px] font-bold text-slate-900 leading-tight">3. Penginapan</h4>
              <p className="hidden sm:block text-[11px] text-slate-500 mt-1">Pilihan hotel terbaik.</p>
            </div>
            <div className="flex flex-col items-center">
              <div className="h-8 w-8 sm:h-12 sm:w-12 bg-[#0E75BC] text-white rounded-full flex items-center justify-center mb-1.5 sm:mb-3 shadow-sm">
                <Share2 className="h-4 w-4 sm:h-5 sm:w-5" />
              </div>
              <h4 className="text-[9px] sm:text-[13px] font-bold text-slate-900 leading-tight">4. Itinerary</h4>
              <p className="hidden sm:block text-[11px] text-slate-500 mt-1">Jadwal otomatis.</p>
            </div>
          </div>
        </section>

      </main>
    </>
  );
}
