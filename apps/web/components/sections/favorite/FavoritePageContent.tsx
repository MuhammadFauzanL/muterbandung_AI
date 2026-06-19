"use client";

import { useEffect, useState, useCallback } from 'react';
import { MapPin, Map, Building, Heart, PlusCircle, Star, Loader2, Calendar, Users, Wallet, Trash2 } from 'lucide-react';
import { usePlanner } from '@/context/PlannerContext';
import { useToast } from '@/context/ToastContext';
import { useAuth } from '@/context/AuthContext';
import { useFavorite } from '@/context/FavoriteContext';
import { SafeImage } from '@/components/ui/SafeImage';
import { userFavoritesService } from '@/services/userFavorites';
import { trackPlannerAdd } from '@/services/userEvents';
import { getSavedItineraries, deleteItinerary, getItineraryCount } from '@/services/savedItineraries';
import type { SavedItinerary } from '@/services/savedItineraries';
import Link from 'next/link';
import type { ExploreDestination } from '@/types';

type TabType = 'Destinasi' | 'Penginapan' | 'Itinerary';

function ItineraryTabContent() {
  const [itineraries, setItineraries] = useState<SavedItinerary[]>(() => getSavedItineraries());
  const { showToast } = useToast();

  const handleDelete = (id: string, title: string) => {
    deleteItinerary(id);
    setItineraries((prev) => prev.filter((i) => i.id !== id));
    showToast(`"${title}" dihapus`, 'success');
  };

  if (itineraries.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 sm:py-20 px-4 bg-white rounded-xl sm:rounded-2xl border border-slate-200 shadow-sm text-center">
        <div className="h-12 w-12 sm:h-16 sm:w-16 bg-[#EAF6FC] rounded-full flex items-center justify-center text-[#0E75BC] mb-3 sm:mb-4">
          <Map className="h-6 w-6 sm:h-8 sm:w-8" />
        </div>
        <h3 className="text-[15px] sm:text-[18px] font-bold text-[#112F43] mb-1.5 sm:mb-2">Belum Ada Itinerary</h3>
        <p className="text-xs sm:text-sm text-slate-500 mb-4 sm:mb-6 max-w-sm">Gunakan bantuan AI kami untuk merencanakan perjalanan, lalu simpan itinerary-mu di sini.</p>
        <Link href="/planner" className="inline-flex items-center gap-1.5 sm:gap-2 bg-[#00526E] text-white px-5 py-2 sm:px-6 sm:py-2.5 rounded-full font-bold text-[11px] sm:text-sm transition-colors hover:bg-[#00415C]">
          <PlusCircle className="h-3.5 w-3.5 sm:h-4 sm:w-4" /> Buat Itinerary Baru
        </Link>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-6">
      {itineraries.map((itn) => {
        const savedDate = new Date(itn.savedAt).toLocaleDateString('id-ID', { day: 'numeric', month: 'short', year: 'numeric' });
        const firstImage = itn.destinations[0]?.image;
        
        return (
          <article key={itn.id} className="overflow-hidden rounded-xl sm:rounded-2xl border border-slate-200 bg-white shadow-sm flex flex-col group">
            {/* Image Header */}
            <div className="relative h-[120px] sm:h-[160px] w-full bg-gradient-to-br from-[#0E75BC] to-[#0B5C73] overflow-hidden">
              {firstImage ? (
                <SafeImage src={firstImage} alt={itn.title} fill className="object-cover opacity-60" />
              ) : null}
              {/* Gradient overlay */}
              <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />
              {/* Title on image */}
              <div className="absolute bottom-3 left-3 sm:bottom-4 sm:left-4 right-3 sm:right-4">
                <h3 className="text-[13px] sm:text-[16px] font-bold text-white leading-tight line-clamp-2 drop-shadow-md">{itn.title}</h3>
                <p className="text-[9px] sm:text-[11px] text-white/70 mt-0.5">Disimpan {savedDate}</p>
              </div>
              {/* Delete button */}
              <button
                onClick={() => handleDelete(itn.id, itn.title)}
                className="absolute top-2 right-2 sm:top-3 sm:right-3 h-7 w-7 sm:h-8 sm:w-8 bg-white/90 backdrop-blur-sm rounded-full flex items-center justify-center text-red-500 hover:bg-red-50 transition-colors shadow-sm opacity-0 group-hover:opacity-100"
                title="Hapus Itinerary"
              >
                <Trash2 className="h-3.5 w-3.5 sm:h-4 sm:w-4" />
              </button>
            </div>
            {/* Content */}
            <div className="p-3 sm:p-5 flex-1 flex flex-col">
              {/* Destination pills */}
              <div className="flex flex-wrap gap-1 sm:gap-1.5 mb-3">
                {itn.destinations.slice(0, 3).map((dest) => (
                  <span key={dest.id} className="inline-flex items-center gap-1 bg-[#EAF6FC] text-[#0B5C73] px-2 py-0.5 rounded-full text-[8px] sm:text-[10px] font-medium">
                    <MapPin className="h-2.5 w-2.5" />
                    {dest.title}
                  </span>
                ))}
                {itn.destinations.length > 3 && (
                  <span className="inline-flex items-center bg-slate-100 text-slate-500 px-2 py-0.5 rounded-full text-[8px] sm:text-[10px] font-medium">
                    +{itn.destinations.length - 3} lagi
                  </span>
                )}
              </div>
              {/* Meta info */}
              <div className="grid grid-cols-3 gap-2 text-center mt-auto">
                <div className="flex flex-col items-center gap-0.5">
                  <Calendar className="h-3.5 w-3.5 text-[#0E75BC]" />
                  <span className="text-[9px] sm:text-[11px] text-slate-500 font-medium">
                    {itn.durationNights > 0 ? `${itn.durationDays}H ${itn.durationNights}M` : '1 Hari'}
                  </span>
                </div>
                <div className="flex flex-col items-center gap-0.5">
                  <Users className="h-3.5 w-3.5 text-[#0E75BC]" />
                  <span className="text-[9px] sm:text-[11px] text-slate-500 font-medium">{itn.guestCount} Org</span>
                </div>
                <div className="flex flex-col items-center gap-0.5">
                  <Wallet className="h-3.5 w-3.5 text-[#0E75BC]" />
                  <span className="text-[9px] sm:text-[11px] text-slate-500 font-medium">Rp{(itn.totalBudget / 1000).toFixed(0)}k</span>
                </div>
              </div>
            </div>
          </article>
        );
      })}
    </div>
  );
}


export function FavoritePageContent() {
  const [activeTab, setActiveTab] = useState<TabType>('Destinasi');
  const { addDestination } = usePlanner();
  const { showToast } = useToast();
  const { isLoggedIn, isLoading: authLoading } = useAuth();
  const { toggleFavorite, isFavorite: isFav } = useFavorite();

  const [destinations, setDestinations] = useState<ExploreDestination[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [itineraryCount, setItineraryCount] = useState(() => getItineraryCount());
  const page = 1;

  const fetchFavorites = useCallback(async () => {
    if (!isLoggedIn) {
      setDestinations([]);
      setTotal(0);
      setIsLoading(false);
      return;
    }
    setIsLoading(true);
    try {
      const res = await userFavoritesService.getFavorites(page, 12);
      setDestinations(res.data);
      setTotal(res.meta.total);
    } catch {
      setDestinations([]);
      setTotal(0);
    } finally {
      setIsLoading(false);
    }
  }, [isLoggedIn, page]);

  useEffect(() => {
    if (authLoading) return;

    const timeoutId = window.setTimeout(() => {
      void fetchFavorites();
    }, 0);

    return () => {
      window.clearTimeout(timeoutId);
    };
  }, [authLoading, fetchFavorites]);

  // Refresh when returning to this page (favorite state may have changed)
  useEffect(() => {
    const handleVisibility = () => {
      if (document.visibilityState === 'visible' && isLoggedIn) {
        fetchFavorites();
      }
    };
    document.addEventListener('visibilitychange', handleVisibility);
    return () => document.removeEventListener('visibilitychange', handleVisibility);
  }, [isLoggedIn, fetchFavorites]);

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
            <p className="text-base sm:text-[32px] font-black text-[#0B5C73] leading-none mt-0.5 sm:mt-1">{total}</p>
          </div>
        </div>
        <div className="bg-white rounded-xl sm:rounded-2xl border border-slate-200 p-2.5 sm:p-6 flex flex-col sm:flex-row items-center sm:gap-6 shadow-sm text-center sm:text-left">
          <div className="h-8 w-8 sm:h-14 sm:w-14 rounded-lg sm:rounded-xl bg-[#EAF6FC] flex items-center justify-center text-[#0E75BC] shrink-0 mb-1.5 sm:mb-0">
            <Building className="h-4 w-4 sm:h-6 sm:w-6" />
          </div>
          <div>
            <p className="text-[7px] sm:text-[11px] font-bold text-slate-500 uppercase tracking-widest line-clamp-1">Penginapan</p>
            <p className="text-base sm:text-[32px] font-black text-[#0B5C73] leading-none mt-0.5 sm:mt-1">0</p>
          </div>
        </div>
        <div className="bg-white rounded-xl sm:rounded-2xl border border-slate-200 p-2.5 sm:p-6 flex flex-col sm:flex-row items-center sm:gap-6 shadow-sm text-center sm:text-left">
          <div className="h-8 w-8 sm:h-14 sm:w-14 rounded-lg sm:rounded-xl bg-[#FCD3D1] flex items-center justify-center text-[#E94B35] shrink-0 mb-1.5 sm:mb-0">
            <Map className="h-4 w-4 sm:h-6 sm:w-6" />
          </div>
          <div>
            <p className="text-[7px] sm:text-[11px] font-bold text-slate-500 uppercase tracking-widest line-clamp-1">Itinerary</p>
            <p className="text-base sm:text-[32px] font-black text-[#112F43] leading-none mt-0.5 sm:mt-1">{itineraryCount}</p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex w-full sm:w-auto items-center gap-1 sm:gap-2 mb-6 sm:mb-8 bg-[#EAF6FC] p-1.5 rounded-xl sm:rounded-full">
        {(['Destinasi', 'Penginapan', 'Itinerary'] as TabType[]).map((tab) => (
          <button
            key={tab}
            onClick={() => {
              setActiveTab(tab);
              if (tab === 'Itinerary') {
                setItineraryCount(getItineraryCount());
              }
            }}
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
        <>
          {!isLoggedIn && !authLoading && (
            <div className="flex flex-col items-center justify-center py-12 sm:py-20 px-4 bg-white rounded-xl sm:rounded-2xl border border-slate-200 shadow-sm text-center">
              <div className="h-12 w-12 sm:h-16 sm:w-16 bg-[#EAF6FC] rounded-full flex items-center justify-center text-[#0E75BC] mb-3 sm:mb-4">
                <Heart className="h-6 w-6 sm:h-8 sm:w-8" />
              </div>
              <h3 className="text-[15px] sm:text-[18px] font-bold text-[#112F43] mb-1.5 sm:mb-2">Silakan Login</h3>
              <p className="text-xs sm:text-sm text-slate-500 mb-4 sm:mb-6 max-w-sm">Login terlebih dahulu untuk melihat destinasi favoritmu.</p>
              <Link href="/login" className="inline-flex items-center gap-1.5 sm:gap-2 bg-[#00526E] text-white px-5 py-2 sm:px-6 sm:py-2.5 rounded-full font-bold text-[11px] sm:text-sm transition-colors hover:bg-[#00415C]">
                Login Sekarang
              </Link>
            </div>
          )}

          {isLoggedIn && isLoading && (
            <div className="flex items-center justify-center py-20">
              <Loader2 className="h-8 w-8 animate-spin text-[#0E75BC]" />
            </div>
          )}

          {isLoggedIn && !isLoading && destinations.length === 0 && (
            <div className="flex flex-col items-center justify-center py-12 sm:py-20 px-4 bg-white rounded-xl sm:rounded-2xl border border-slate-200 shadow-sm text-center">
              <div className="h-12 w-12 sm:h-16 sm:w-16 bg-[#EAF6FC] rounded-full flex items-center justify-center text-[#0E75BC] mb-3 sm:mb-4">
                <Heart className="h-6 w-6 sm:h-8 sm:w-8" />
              </div>
              <h3 className="text-[15px] sm:text-[18px] font-bold text-[#112F43] mb-1.5 sm:mb-2">Belum Ada Favorit</h3>
              <p className="text-xs sm:text-sm text-slate-500 mb-4 sm:mb-6 max-w-sm">Jelajahi destinasi di Bandung dan tekan ❤️ untuk menyimpannya di sini.</p>
              <Link href="/explore" className="inline-flex items-center gap-1.5 sm:gap-2 bg-[#00526E] text-white px-5 py-2 sm:px-6 sm:py-2.5 rounded-full font-bold text-[11px] sm:text-sm transition-colors hover:bg-[#00415C]">
                <PlusCircle className="h-3.5 w-3.5 sm:h-4 sm:w-4" /> Jelajahi Destinasi
              </Link>
            </div>
          )}

          {isLoggedIn && !isLoading && destinations.length > 0 && (
            <div className="grid grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-6">
              {destinations.map((dest) => {
                const favorited = isFav(dest.id);
                return (
                  <article key={dest.id} className="overflow-hidden rounded-xl sm:rounded-2xl border border-slate-200 bg-white shadow-sm flex flex-col">
                    <div className="relative h-[120px] sm:h-[200px] w-full bg-slate-100">
                      <SafeImage 
                        src={dest.image} 
                        alt={dest.title} 
                        fill 
                        className="object-cover" 
                        category={dest.category}
                      />
                      <button
                        type="button"
                        onClick={() => toggleFavorite(dest.id)}
                        className={`absolute top-2 right-2 sm:top-4 sm:right-4 h-6 w-6 sm:h-9 sm:w-9 bg-white rounded-full flex items-center justify-center shadow-sm transition-colors ${favorited ? 'text-[#E94B35]' : 'text-slate-400 hover:text-[#E94B35]'}`}
                      >
                        <Heart className={`h-3 w-3 sm:h-5 sm:w-5 ${favorited ? 'fill-current' : ''}`} />
                      </button>
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
                        {dest.price}
                      </p>
                      <div className="space-y-1.5 sm:space-y-2 mt-auto">
                        <button 
                          onClick={() => {
                            addDestination({
                              id: dest.id,
                              title: dest.title,
                              slug: dest.slug,
                              category: dest.category,
                              primaryIntent: dest.primaryIntent,
                              image: dest.image,
                              latitude: dest.latitude,
                              longitude: dest.longitude,
                            });
                            trackPlannerAdd(dest.id);
                            showToast(`${dest.title} ditambahkan ke perjalanan!`, 'success');
                          }}
                          className="w-full bg-[#00526E] text-white font-bold text-[9px] sm:text-[13px] py-1.5 sm:py-3 rounded-md sm:rounded-xl transition-colors hover:bg-[#00415C]"
                        >
                          Tambah
                        </button>
                        <Link
                          href={`/explore/${dest.slug || dest.id}`}
                          className="block w-full bg-white text-[#00526E] border border-[#00526E] font-bold text-[9px] sm:text-[13px] py-1.5 sm:py-3 rounded-md sm:rounded-xl transition-colors hover:bg-slate-50 text-center"
                        >
                          Detail
                        </Link>
                      </div>
                    </div>
                  </article>
                );
              })}
            </div>
          )}
        </>
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
        <ItineraryTabContent />
      )}

    </main>
  );
}
