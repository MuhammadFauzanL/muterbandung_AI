import type { DestinationDetail } from '@/types';

export function BottomActions({ destination }: { destination: DestinationDetail }) {
  return (
    <section className="mt-8 rounded-2xl border border-[#D9E8F3] bg-white p-3 shadow-[0_18px_40px_rgba(15,23,42,0.12)]">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-end sm:pr-16">
        <button
          type="button"
          className="inline-flex items-center justify-center rounded-xl border border-[#0E75BC] px-5 py-3 text-sm font-semibold text-[#0E75BC] transition-colors hover:bg-[#EEF7FD]"
        >
          Tambahkan ke Perjalanan
        </button>
        <button
          type="button"
          className="inline-flex items-center justify-center rounded-xl bg-[#E54545] px-5 py-3 text-sm font-semibold text-white transition-colors hover:bg-[#CF3B3B]"
        >
          Pesan {destination.title}
        </button>
      </div>
    </section>
  );
}
