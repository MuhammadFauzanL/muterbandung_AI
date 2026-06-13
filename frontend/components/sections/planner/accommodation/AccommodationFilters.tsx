import { Search, Calendar, Users } from 'lucide-react';

const FILTERS = ['Semua', 'Dekat Kawah Putih', 'Family stay', 'Cabin', 'Budget hemat'];

export function AccommodationFilters() {
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
