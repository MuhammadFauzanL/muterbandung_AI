'use client';

import { useState, FormEvent } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import {
  EXPLORE_CATEGORY_FILTERS,
  EXPLORE_DESTINATIONS,
  EXPLORE_FILTER_GROUPS,
  EXPLORE_STATS,
} from '@/constants';
import { HeartIcon, LocationIcon } from '@/components/ui/icons';
import type { ExploreDestination } from '@/types';

// --- Dynamic result type from backend ---
interface BackendPlace {
  location_name: string;
  category: string;
  subcategory?: string;
  explanation?: string;
  score_breakdown: {
    similarity: number;
    sentiment_score: number;
  };
}

function SearchIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" aria-hidden="true">
      <path
        d="M10.75 18.5a7.75 7.75 0 1 0 0-15.5 7.75 7.75 0 0 0 0 15.5ZM16.5 16.5 21 21"
        stroke="currentColor"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth="2"
      />
    </svg>
  );
}

function SlidersIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" aria-hidden="true">
      <path
        d="M4 7h9M17 7h3M4 17h3M11 17h9M13 7a2 2 0 1 0 4 0 2 2 0 0 0-4 0ZM7 17a2 2 0 1 0 4 0 2 2 0 0 0-4 0Z"
        stroke="currentColor"
        strokeLinecap="round"
        strokeWidth="1.8"
      />
    </svg>
  );
}

function GridIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" aria-hidden="true">
      <path
        d="M4 4h7v7H4V4ZM13 4h7v7h-7V4ZM4 13h7v7H4v-7ZM13 13h7v7h-7v-7Z"
        stroke="currentColor"
        strokeLinejoin="round"
        strokeWidth="1.8"
      />
    </svg>
  );
}

function ListIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" aria-hidden="true">
      <path
        d="M8 6h12M8 12h12M8 18h12M4 6h.01M4 12h.01M4 18h.01"
        stroke="currentColor"
        strokeLinecap="round"
        strokeWidth="2"
      />
    </svg>
  );
}

function SpinnerIcon() {
  return (
    <svg className="h-5 w-5 animate-spin text-white" viewBox="0 0 24 24" fill="none">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
    </svg>
  );
}

// --- AI Result Card (from backend) ---
function AIResultCard({ place }: { place: BackendPlace }) {
  const similarity = (place.score_breakdown.similarity * 100).toFixed(1);
  return (
    <article className="overflow-hidden rounded-2xl border border-[#D9E8F3] bg-white shadow-[0_12px_28px_rgba(15,23,42,0.07)]">
      <div className="relative h-[80px] bg-gradient-to-r from-[#0E75BC] to-[#4B82BD] flex items-center px-5">
        <div className="absolute right-4 top-3 rounded-full bg-white/92 px-3 py-1 text-xs font-semibold text-[#0E75BC] shadow-sm">
          {similarity}% Match
        </div>
        <div className="text-white">
          <span className="text-xs font-medium opacity-80">{place.category} • {place.subcategory || 'Umum'}</span>
        </div>
      </div>
      <div className="p-4">
        <h3 className="text-[19px] font-semibold leading-tight text-slate-900">
          {place.location_name}
        </h3>
        <div className="mt-2 flex items-center gap-2 text-xs text-slate-500">
          <span>⭐ Sentimen: {place.score_breakdown.sentiment_score.toFixed(2)}</span>
        </div>
        <p className="mt-3 text-sm leading-6 text-slate-600">
          {place.explanation || 'Rekomendasi terbaik berdasarkan pencarian Anda.'}
        </p>
      </div>
    </article>
  );
}

// --- Static Destination Card (from mock) ---
function DestinationCard({
  destination,
  eagerImage = false,
}: {
  destination: ExploreDestination;
  eagerImage?: boolean;
}) {
  return (
    <article className="overflow-hidden rounded-2xl border border-[#D9E8F3] bg-white shadow-[0_12px_28px_rgba(15,23,42,0.07)]">
      <div className="relative h-[184px] overflow-hidden">
        <Image
          src={destination.image}
          alt={destination.title}
          fill
          loading={eagerImage ? 'eager' : 'lazy'}
          sizes="(min-width: 1024px) 390px, (min-width: 640px) 50vw, 100vw"
          className="object-cover"
        />
        <div className="absolute left-3 top-3 rounded-full bg-white/92 px-3 py-1 text-xs font-semibold text-[#0E75BC] shadow-sm">
          {destination.category}
        </div>
        <button
          type="button"
          aria-label={`Simpan ${destination.title}`}
          className="absolute right-3 top-3 inline-flex h-9 w-9 items-center justify-center rounded-full bg-white/92 text-slate-500 shadow-sm transition-colors hover:text-[#E54545]"
        >
          <HeartIcon className="h-5 w-5" />
        </button>
      </div>

      <div className="p-4">
        <div className="flex items-center gap-1.5 text-xs font-medium text-[#0E75BC]">
          <LocationIcon className="h-3.5 w-3.5" />
          <span>{destination.location}</span>
        </div>

        <h3 className="mt-2 text-[19px] font-semibold leading-tight text-slate-900">
          {destination.title}
        </h3>

        <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-500">
          <span>{destination.duration}</span>
          <span>{destination.price}</span>
          <span className="font-semibold text-[#E54545]">
            +{destination.rating}
          </span>
        </div>

        <div className="mt-4 flex items-center justify-between">
          <Link
            href={`/explore/${destination.id}`}
            className="text-sm font-semibold text-[#0E75BC] hover:text-[#095f99]"
          >
            Lihat Detail
          </Link>
          <button
            type="button"
            className="rounded-full bg-[#FFEDEE] px-4 py-2 text-xs font-semibold text-[#E54545] transition-colors hover:bg-[#FFDCDD]"
          >
            Pilih Rencana
          </button>
        </div>
      </div>
    </article>
  );
}

export function ExplorePageContent() {
  const [query, setQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [aiResults, setAiResults] = useState<BackendPlace[] | null>(null);
  const [searchError, setSearchError] = useState<string | null>(null);
  const [activeCategory, setActiveCategory] = useState(0);

  async function handleSearch(e: FormEvent) {
    e.preventDefault();
    if (!query.trim()) return;

    setIsSearching(true);
    setSearchError(null);
    setAiResults(null);

    try {
      const res = await fetch(`/api/recommend`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: query.trim(), top_k: 5 }),
      });

      if (!res.ok) throw new Error(`Server error: ${res.status}`);
      const data = await res.json();
      setAiResults(data.recommendations || []);
    } catch (err) {
      setSearchError(err instanceof Error ? err.message : 'Gagal menghubungi server AI');
    } finally {
      setIsSearching(false);
    }
  }

  function handleQuickSearch(text: string) {
    setQuery(text);
    // Trigger search programmatically
    setIsSearching(true);
    setSearchError(null);
    setAiResults(null);

    fetch(`/api/recommend`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: text, top_k: 5 }),
    })
      .then((res) => {
        if (!res.ok) throw new Error(`Server error: ${res.status}`);
        return res.json();
      })
      .then((data) => setAiResults(data.recommendations || []))
      .catch((err) => setSearchError(err instanceof Error ? err.message : 'Gagal'))
      .finally(() => setIsSearching(false));
  }

  function handleCategoryClick(index: number, filter: string) {
    setActiveCategory(index);
    if (index > 0) {
      // Map category filter ke query
      handleQuickSearch(filter.toLowerCase());
    } else {
      // "Semua Rekomendasi" = reset ke mock
      setAiResults(null);
      setSearchError(null);
    }
  }

  const showingAI = aiResults !== null;

  return (
    <main id="planner" className="mx-auto max-w-[1180px] px-4 py-6 sm:px-8">
      {/* Hero Search Bar */}
      <section className="rounded-[18px] bg-[linear-gradient(135deg,#4B82BD_0%,#6FA9E0_100%)] px-5 py-7 text-white shadow-[0_18px_36px_rgba(31,90,145,0.18)] sm:px-8">
        <div className="max-w-3xl">
          <h1 className="text-[28px] font-semibold leading-tight sm:text-[34px]">
            Rencana Seru di Bandung
          </h1>
          <form onSubmit={handleSearch} className="mt-5 flex max-w-2xl items-center rounded-xl bg-white p-1.5 shadow-[0_10px_24px_rgba(15,23,42,0.16)]">
            <label className="sr-only" htmlFor="planner-search">
              Cari rencana perjalanan
            </label>
            <div className="flex flex-1 items-center gap-2 px-3 text-slate-500">
              <SearchIcon />
              <input
                id="planner-search"
                name="query"
                type="search"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Mau kemana hari ini?"
                className="h-9 min-w-0 flex-1 bg-transparent text-sm text-slate-900 outline-none placeholder:text-slate-400"
              />
            </div>
            <button
              type="submit"
              disabled={isSearching}
              className="inline-flex h-9 items-center justify-center gap-2 rounded-lg bg-[#0D5D91] px-5 text-sm font-semibold text-white transition-colors hover:bg-[#0A4F7C] disabled:opacity-60"
            >
              {isSearching ? <SpinnerIcon /> : 'Cari'}
            </button>
          </form>
          <div className="mt-3 flex flex-wrap gap-2 text-xs text-white/78">
            <span>Coba:</span>
            <button type="button" onClick={() => handleQuickSearch('tempat teduh anak')} className="hover:text-white underline-offset-2 hover:underline">
              tempat teduh anak
            </button>
            <span>/</span>
            <button type="button" onClick={() => handleQuickSearch('kafe wifi kencang')} className="hover:text-white underline-offset-2 hover:underline">
              kafe wifi kencang
            </button>
            <span>/</span>
            <button type="button" onClick={() => handleQuickSearch('wisata dekat Lembang')} className="hover:text-white underline-offset-2 hover:underline">
              wisata dekat Lembang
            </button>
          </div>
        </div>
      </section>

      {/* Category Chips */}
      <div className="mt-5 space-y-4">
        <div className="flex flex-wrap gap-2">
          {EXPLORE_CATEGORY_FILTERS.map((filter, index) => (
            <button
              key={filter}
              type="button"
              onClick={() => handleCategoryClick(index, filter)}
              className={`rounded-full border px-4 py-2 text-sm font-medium transition-colors ${
                index === activeCategory
                  ? 'border-[#0E75BC] bg-[#0E75BC] text-white shadow-sm'
                  : 'border-[#D5E6F2] bg-white text-[#23689A] hover:border-[#0E75BC] hover:text-[#0E75BC]'
              }`}
            >
              {filter}
            </button>
          ))}
        </div>

        {/* AI Recommendation Banner */}
        <section className="rounded-2xl border border-[#CFE5F2] bg-[#EAF6FC] px-5 py-4 text-[#1D5F88]">
          <p className="text-sm font-semibold">
            {showingAI ? '🧠 Hasil Pencarian Cepot AI (Semantic Search)' : 'Kenapa Cepot AI Merekomendasikan Ini?'}
          </p>
          <p className="mt-1 text-sm leading-6 text-[#45738F]">
            {showingAI
              ? `Menampilkan ${aiResults.length} hasil terbaik untuk "${query}" menggunakan kecerdasan bahasa MiniLM.`
              : 'Destinasi ini cocok untuk keluarga dengan budget di bawah Rp100.000, memiliki akses nyaman, dan berkaitan hangat dengan suasana Bandung.'}
          </p>
        </section>
      </div>

      {/* Error Banner */}
      {searchError && (
        <div className="mt-4 rounded-xl border border-red-200 bg-red-50 px-5 py-3 text-sm text-red-700">
          ⚠️ {searchError} — Pastikan backend berjalan di <code className="font-mono">{API_BASE}</code>
        </div>
      )}

      {/* Main Content */}
      <div className="mt-6 grid gap-6 lg:grid-cols-[280px_minmax(0,1fr)]">
        {/* Sidebar Filters */}
        <aside className="rounded-2xl border border-[#D9E8F3] bg-white p-5 shadow-[0_12px_28px_rgba(15,23,42,0.06)]">
          <div className="flex items-center gap-2 text-[#0E75BC]">
            <SlidersIcon />
            <h2 className="text-base font-semibold text-slate-900">
              Sesuaikan Hasil
            </h2>
          </div>

          <div className="mt-5 grid grid-cols-3 gap-2">
            {EXPLORE_STATS.map((stat) => (
              <div
                key={stat.label}
                className="rounded-xl border border-[#E1EEF6] bg-[#F8FBFE] px-3 py-3 text-center"
              >
                <p className="text-[11px] font-medium uppercase text-slate-500">
                  {stat.label}
                </p>
                <p className="mt-1 text-sm font-semibold text-slate-900">
                  {stat.value}
                </p>
              </div>
            ))}
          </div>

          <div className="mt-5 space-y-5">
            {EXPLORE_FILTER_GROUPS.map((group) => (
              <div key={group.title}>
                <h3 className="text-sm font-semibold text-slate-900">
                  {group.title}
                </h3>
                <div className="mt-2 flex flex-wrap gap-2">
                  {group.options.map((option, index) => (
                    <button
                      key={option}
                      type="button"
                      className={`rounded-full border px-3 py-1.5 text-xs font-medium transition-colors ${
                        index === 0
                          ? 'border-[#0E75BC] bg-[#EEF7FD] text-[#0E75BC]'
                          : 'border-[#DDEAF2] text-slate-600 hover:border-[#0E75BC] hover:text-[#0E75BC]'
                      }`}
                    >
                      {option}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>

          <div className="mt-6 space-y-3">
            <button
              type="button"
              className="w-full rounded-xl bg-[#0E75BC] px-4 py-3 text-sm font-semibold text-white transition-colors hover:bg-[#095f99]"
            >
              Update Filter
            </button>
            <button
              type="button"
              onClick={() => { setAiResults(null); setSearchError(null); setActiveCategory(0); setQuery(''); }}
              className="w-full rounded-xl border border-[#D6E6F0] px-4 py-3 text-sm font-semibold text-[#23689A] transition-colors hover:border-[#0E75BC]"
            >
              Reset Pilihan
            </button>
          </div>
        </aside>

        {/* Destination Grid */}
        <section id="destinations" className="min-w-0">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <p className="text-sm font-semibold text-[#0E75BC]">
                {showingAI
                  ? `Ditemukan ${aiResults.length} hasil dari AI`
                  : `Ditemukan ${EXPLORE_DESTINATIONS.length} tempat sesuai hasil rekomendasi`}
              </p>
              <h2 className="mt-1 text-[28px] font-semibold tracking-normal text-slate-950">
                {showingAI ? 'Hasil Pencarian AI' : 'Destinasi Untukmu'}
              </h2>
            </div>
            <div className="flex items-center gap-2">
              <button
                type="button"
                aria-label="Tampilan grid"
                className="inline-flex h-10 w-10 items-center justify-center rounded-xl bg-[#0E75BC] text-white"
              >
                <GridIcon />
              </button>
              <button
                type="button"
                aria-label="Tampilan daftar"
                className="inline-flex h-10 w-10 items-center justify-center rounded-xl border border-[#D7E8F2] bg-white text-[#23689A] transition-colors hover:border-[#0E75BC]"
              >
                <ListIcon />
              </button>
            </div>
          </div>

          {/* Loading State */}
          {isSearching && (
            <div className="mt-8 flex flex-col items-center gap-3 py-12 text-slate-500">
              <div className="h-10 w-10 animate-spin rounded-full border-4 border-slate-200 border-t-[#0E75BC]" />
              <p className="text-sm font-medium">Cepot AI sedang mencari...</p>
            </div>
          )}

          {/* AI Results */}
          {!isSearching && showingAI && (
            <div className="mt-5 grid gap-5 md:grid-cols-2">
              {aiResults.map((place) => (
                <AIResultCard key={place.location_name} place={place} />
              ))}
              {aiResults.length === 0 && (
                <p className="col-span-2 py-8 text-center text-sm text-slate-500">
                  Tidak ada hasil untuk pencarian ini. Coba kata kunci lain.
                </p>
              )}
            </div>
          )}

          {/* Static Mock Results (default) */}
          {!isSearching && !showingAI && (
            <>
              <div className="mt-5 grid gap-5 md:grid-cols-2">
                {EXPLORE_DESTINATIONS.map((destination, index) => (
                  <DestinationCard
                    key={destination.id}
                    destination={destination}
                    eagerImage={index === 0}
                  />
                ))}
              </div>

              <div className="mt-7 flex items-center justify-center gap-2">
                {[1, 2, 3].map((page) => (
                  <button
                    key={page}
                    type="button"
                    className={`h-9 min-w-9 rounded-full text-sm font-semibold ${
                      page === 1
                        ? 'bg-[#0E75BC] text-white'
                        : 'border border-[#D9E8F3] bg-white text-[#23689A]'
                    }`}
                  >
                    {page}
                  </button>
                ))}
              </div>
            </>
          )}
        </section>
      </div>
    </main>
  );
}
