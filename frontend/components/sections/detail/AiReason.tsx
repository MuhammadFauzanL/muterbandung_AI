import type { DestinationDetail } from '@/types';

export function AiReason({ destination }: { destination: DestinationDetail }) {
  return (
    <section className="rounded-2xl border border-[#CFE5F2] bg-[#EAF6FC] p-5">
      <p className="text-sm font-semibold text-[#0E75BC]">
        Kenapa Cepot AI Merekomendasikan Ini?
      </p>
      <p className="mt-2 text-sm leading-7 text-[#426F87]">
        {destination.aiReason}
      </p>
    </section>
  );
}
