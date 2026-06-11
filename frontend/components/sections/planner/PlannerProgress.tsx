import { CheckIcon } from '@/components/ui/icons';

export function PlannerProgress() {
  const steps = ['Destinasi', 'Penginapan', 'Transport'];

  return (
    <div className="grid gap-2 rounded-[14px] border border-[#DDEAF2] bg-white p-2 shadow-[0_10px_24px_rgba(17,73,112,0.05)] sm:grid-cols-3">
      {steps.map((step, index) => (
        <div
          key={step}
          className={`flex items-center gap-2 rounded-[10px] px-3 py-2.5 text-[12px] font-semibold ${
            index === 1
              ? 'bg-[#0E75BC] text-white'
              : index === 0
                ? 'bg-[#EAF8FB] text-[#246983]'
                : 'bg-[#F6FAFD] text-[#8A9AA7]'
          }`}
        >
          <span
            className={`inline-flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-[11px] ${
              index === 1
                ? 'bg-white text-[#0E75BC]'
                : index === 0
                  ? 'bg-[#0E75BC] text-white'
                  : 'bg-white text-[#8A9AA7]'
            }`}
          >
            {index === 0 ? <CheckIcon /> : index + 1}
          </span>
          {step}
        </div>
      ))}
    </div>
  );
}
