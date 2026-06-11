import {
  EXPLORE_FILTER_GROUPS,
  EXPLORE_STATS,
} from '@/constants';
import { SlidersIcon } from '@/components/ui/icons';

export function ResultsSummary() {
  return (
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
          className="w-full rounded-xl border border-[#D6E6F0] px-4 py-3 text-sm font-semibold text-[#23689A] transition-colors hover:border-[#0E75BC]"
        >
          Reset Pilihan
        </button>
      </div>
    </aside>
  );
}
