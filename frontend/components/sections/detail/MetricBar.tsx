import { CalendarIcon, StarIcon } from '@/components/ui/icons';
import type { DestinationDetail, DetailMetric } from '@/types';

function metricIcon(tone: DetailMetric['tone']) {
  if (tone === 'price') {
    return <span className="text-[18px] font-bold leading-none">Rp</span>;
  }

  if (tone === 'rating') {
    return <StarIcon className="h-4 w-4" size={16} />;
  }

  return <CalendarIcon />;
}

export function MetricBar({ metrics }: { metrics: DestinationDetail['metrics'] }) {
  return (
    <section className="relative z-10 mx-4 -mt-12 grid gap-3 rounded-2xl border border-[#D9E8F3] bg-white p-3 shadow-[0_18px_40px_rgba(15,23,42,0.14)] sm:mx-8 sm:grid-cols-3">
      {metrics.map((metric) => (
        <div
          key={metric.label}
          className="flex items-center gap-3 rounded-xl bg-[#F8FBFE] px-4 py-3"
        >
          <div className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-[#EAF6FC] text-[#0E75BC]">
            {metricIcon(metric.tone)}
          </div>
          <div>
            <p className="text-xs font-medium uppercase text-slate-500">
              {metric.label}
            </p>
            <p className="mt-1 text-sm font-semibold text-slate-950">
              {metric.value}
            </p>
          </div>
        </div>
      ))}
    </section>
  );
}
