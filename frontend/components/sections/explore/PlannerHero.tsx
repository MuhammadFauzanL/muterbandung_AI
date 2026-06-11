import { SearchIcon } from '@/components/ui/icons';

export function PlannerHero() {
  return (
    <section className="rounded-[18px] bg-[linear-gradient(135deg,#4B82BD_0%,#6FA9E0_100%)] px-5 py-7 text-white shadow-[0_18px_36px_rgba(31,90,145,0.18)] sm:px-8">
      <div className="max-w-3xl">
        <h1 className="text-[28px] font-semibold leading-tight sm:text-[34px]">
          Rencana Seru di Bandung
        </h1>
        <form className="mt-5 flex max-w-2xl items-center rounded-xl bg-white p-1.5 shadow-[0_10px_24px_rgba(15,23,42,0.16)]">
          <label className="sr-only" htmlFor="planner-search">
            Cari rencana perjalanan
          </label>
          <div className="flex flex-1 items-center gap-2 px-3 text-slate-500">
            <SearchIcon />
            <input
              id="planner-search"
              name="query"
              type="search"
              placeholder="Mau kemana hari ini?"
              className="h-9 min-w-0 flex-1 bg-transparent text-sm text-slate-900 outline-none placeholder:text-slate-400"
            />
          </div>
          <button
            type="submit"
            className="inline-flex h-9 items-center justify-center rounded-lg bg-[#0D5D91] px-5 text-sm font-semibold text-white transition-colors hover:bg-[#0A4F7C]"
          >
            Cari
          </button>
        </form>
        <div className="mt-3 flex flex-wrap gap-2 text-xs text-white/78">
          <span>Coba:</span>
          <a href="#destinations" className="hover:text-white">
            tempat teduh anak
          </a>
          <span>/</span>
          <a href="#destinations" className="hover:text-white">
            itinerary satu hari
          </a>
          <span>/</span>
          <a href="#destinations" className="hover:text-white">
            wisata dekat Lembang
          </a>
        </div>
      </div>
    </section>
  );
}
