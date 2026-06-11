import Image from 'next/image';
import { SparkIcon } from '@/components/ui/icons';

export function CepotInsight() {
  return (
    <section className="relative overflow-hidden rounded-[18px] border border-[#BFE8F0] bg-[#EAF8FB] px-5 py-4">
      <div className="relative z-10 flex items-start gap-3">
        <div className="relative h-11 w-11 shrink-0 overflow-hidden rounded-full bg-[#D8F0F6] ring-1 ring-white">
          <Image
            src="/images/welcome-cepot.png"
            alt="Cepot AI"
            fill
            sizes="44px"
            className="object-cover object-top"
          />
        </div>
        <div>
          <p className="flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-normal text-[#137CA6]">
            <SparkIcon />
            Cepot AI Insight
          </p>
          <p className="mt-1.5 text-[13px] leading-6 text-[#26485C]">
            Untuk rute Kawah Putih dan Ranca Upas, menginap di area Ciwidey
            membuat perjalanan pagi lebih ringan dan menghemat waktu tempuh
            sekitar 35 menit.
          </p>
        </div>
      </div>
      <div className="absolute -right-8 bottom-0 h-24 w-24 rounded-full bg-white/35" />
    </section>
  );
}
