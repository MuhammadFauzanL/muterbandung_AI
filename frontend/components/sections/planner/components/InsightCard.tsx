import Image from 'next/image';

export function InsightCard() {
  return (
    <section className="relative overflow-hidden rounded-[16px] sm:rounded-[18px] border border-[#BFE8F0] bg-[#EAF8FB] px-3 py-3 sm:px-5 sm:py-4 shadow-sm">
      <div className="relative z-10 flex items-start gap-2.5 sm:gap-4">
        <div className="relative h-8 w-8 sm:h-12 sm:w-12 shrink-0 overflow-hidden rounded-full bg-[#D8F0F6] ring-1 ring-white">
          <Image
            src="/images/welcome-cepot.png"
            alt="Cepot AI"
            fill
            sizes="48px"
            className="object-cover object-top"
          />
        </div>
        <div>
          <p className="text-[9px] sm:text-[11px] font-bold uppercase tracking-normal text-[#137CA6]">
            Cepot AI Insight
          </p>
          <p className="mt-0.5 sm:mt-1.5 max-w-[640px] text-[10px] leading-relaxed sm:text-[14px] sm:leading-6 text-[#26485C]">
            Insight dari Cepot AI: Wisatawan yang mengunjungi Kawah Putih
            biasanya juga mengunjungi Situ Patenggang dan Ranca Upas karena
            berada dalam satu kawasan wisata yang berdekatan.
          </p>
        </div>
      </div>
      <div className="absolute -right-8 bottom-0 h-20 w-20 sm:h-28 sm:w-28 rounded-full bg-white/35" />
      <div className="absolute bottom-4 right-6 sm:bottom-7 sm:right-8 h-8 w-8 sm:h-11 sm:w-11 rotate-45 rounded-[6px] sm:rounded-[8px] border border-[#B8DDE7] bg-[#D9F0F6]" />
    </section>
  );
}
