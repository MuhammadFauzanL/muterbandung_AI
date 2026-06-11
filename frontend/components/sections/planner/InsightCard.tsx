import Image from 'next/image';

export function InsightCard() {
  return (
    <section className="relative overflow-hidden rounded-[18px] border border-[#BFE8F0] bg-[#EAF8FB] px-6 py-5">
      <div className="relative z-10 flex items-start gap-4">
        <div className="relative h-12 w-12 shrink-0 overflow-hidden rounded-full bg-[#D8F0F6] ring-1 ring-white">
          <Image
            src="/images/welcome-cepot.png"
            alt="Cepot AI"
            fill
            sizes="48px"
            className="object-cover object-top"
          />
        </div>
        <div>
          <p className="text-[11px] font-bold uppercase tracking-normal text-[#137CA6]">
            Cepot AI Insight
          </p>
          <p className="mt-2 max-w-[640px] text-[15px] leading-7 text-[#26485C]">
            Insight dari Cepot AI: Wisatawan yang mengunjungi Kawah Putih
            biasanya juga mengunjungi Situ Patenggang dan Ranca Upas karena
            berada dalam satu kawasan wisata yang berdekatan.
          </p>
        </div>
      </div>
      <div className="absolute -right-8 bottom-0 h-28 w-28 rounded-full bg-white/35" />
      <div className="absolute bottom-7 right-8 h-11 w-11 rotate-45 rounded-[8px] border border-[#B8DDE7] bg-[#D9F0F6]" />
    </section>
  );
}
