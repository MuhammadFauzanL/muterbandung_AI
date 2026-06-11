import { ACCOMMODATION_FILTERS } from '@/constants';
import { CalendarIcon, SearchIcon, UsersIcon } from '@/components/ui/icons';

export function AccommodationFilters() {
  return (
    <section className="rounded-[16px] border border-[#DCEAF3] bg-white p-4 shadow-[0_10px_26px_rgba(17,73,112,0.06)]">
      <div className="grid gap-3 md:grid-cols-[minmax(0,1fr)_150px_132px_140px]">
        <label className="flex h-11 items-center gap-2 rounded-[10px] border border-[#DDEAF2] bg-[#F8FBFE] px-3 text-[#748694]">
          <SearchIcon />
          <span className="sr-only">Cari penginapan</span>
          <input
            type="search"
            placeholder="Cari area atau nama penginapan"
            className="min-w-0 flex-1 bg-transparent text-[13px] text-[#202B37] outline-none placeholder:text-[#96A5B0]"
          />
        </label>
        <button
          type="button"
          className="inline-flex h-11 items-center justify-center gap-2 rounded-[10px] border border-[#DDEAF2] bg-white px-3 text-[12px] font-semibold text-[#405A6D]"
        >
          <CalendarIcon />
          12 Jun
        </button>
        <button
          type="button"
          className="inline-flex h-11 items-center justify-center gap-2 rounded-[10px] border border-[#DDEAF2] bg-white px-3 text-[12px] font-semibold text-[#405A6D]"
        >
          <UsersIcon />
          2 Tamu
        </button>
        <button
          type="button"
          className="inline-flex h-11 items-center justify-center gap-2 rounded-[10px] bg-[#0E75BC] px-3 text-[12px] font-semibold text-white transition-colors hover:bg-[#095f99]"
        >
          Terapkan
        </button>
      </div>

      <div className="mt-3 flex flex-wrap gap-2">
        {ACCOMMODATION_FILTERS.map((filter, index) => (
          <button
            key={filter}
            type="button"
            className={`rounded-full border px-3.5 py-2 text-[12px] font-semibold transition-colors ${
              index === 0
                ? 'border-[#0E75BC] bg-[#EAF6FC] text-[#0E75BC]'
                : 'border-[#DDEAF2] bg-white text-[#6A7E8E] hover:border-[#0E75BC] hover:text-[#0E75BC]'
            }`}
          >
            {filter}
          </button>
        ))}
      </div>
    </section>
  );
}
