import type { DestinationDetail } from '@/types';

export function PlanCard({ destination }: { destination: DestinationDetail }) {
  return (
    <section className="rounded-2xl border border-[#CFE5F2] bg-[#EAF6FC] p-5">
      <h2 className="text-lg font-semibold text-slate-950">
        Rencana Cepat Cepot AI
      </h2>
      <ol className="mt-4 space-y-3 text-sm text-slate-600">
        <li className="rounded-xl bg-white px-4 py-3">
          08.00 - Berangkat menuju {destination.location}
        </li>
        <li className="rounded-xl bg-white px-4 py-3">
          10.00 - Eksplor area utama dan galeri foto
        </li>
        <li className="rounded-xl bg-white px-4 py-3">
          12.30 - Istirahat dan lanjut ke destinasi sekitar
        </li>
      </ol>
    </section>
  );
}
