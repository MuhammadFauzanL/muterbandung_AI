import type { DestinationDetail } from '@/types';

export function DestinationStory({ destination }: { destination: DestinationDetail }) {
  return (
    <section className="rounded-2xl border border-[#D9E8F3] bg-white p-5 shadow-[0_12px_28px_rgba(15,23,42,0.05)]">
      <h2 className="text-[22px] font-semibold text-slate-950">
        Tentang Destinasi
      </h2>
      <p className="mt-3 text-sm leading-7 text-slate-600">
        {destination.description}
      </p>
    </section>
  );
}
