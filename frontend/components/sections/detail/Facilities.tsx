import { CheckIcon } from '@/components/ui/icons';
import type { DestinationDetail } from '@/types';

export function Facilities({ facilities }: { facilities: DestinationDetail['facilities'] }) {
  return (
    <section className="rounded-2xl border border-[#D9E8F3] bg-white p-5 shadow-[0_12px_28px_rgba(15,23,42,0.05)]">
      <h2 className="text-[22px] font-semibold text-slate-950">Fasilitas</h2>
      <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {facilities.map((facility) => (
          <div
            key={facility}
            className="flex items-center gap-3 rounded-xl border border-[#E1EEF6] bg-[#F8FBFE] px-4 py-3 text-sm font-semibold text-slate-700"
          >
            <span className="inline-flex h-7 w-7 items-center justify-center rounded-full bg-[#EAF6FC] text-[#0E75BC]">
              <CheckIcon />
            </span>
            {facility}
          </div>
        ))}
      </div>
    </section>
  );
}
