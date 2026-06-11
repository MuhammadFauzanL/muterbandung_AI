import Image from 'next/image';
import { CloseIcon } from '@/components/ui/icons';

export function SuccessBanner() {
  return (
    <section className="relative overflow-hidden rounded-[10px] border border-[#DCEBF3] bg-white px-5 py-4 shadow-[0_10px_24px_rgba(17,73,112,0.05)]">
      <div className="absolute left-0 top-4 h-12 w-1 rounded-r-full bg-[#129ED0]" />
      <div className="flex items-start gap-3 pr-8">
        <div className="relative mt-0.5 h-8 w-8 overflow-hidden rounded-full bg-[#EAF6FC]">
          <Image
            src="/destinations/kawah-putih.svg"
            alt=""
            fill
            loading="eager"
            sizes="32px"
            className="object-cover"
          />
        </div>
        <div>
          <h1 className="text-[14px] font-semibold leading-5 text-[#202B37]">
            Kawah Putih berhasil ditambahkan ke perjalananmu.
          </h1>
          <p className="mt-0.5 text-[12px] leading-5 text-[#6E7F8E]">
            Cepot AI menambahkan destinasi lain yang sering dikunjungi dalam
            satu perjalanan.
          </p>
        </div>
      </div>
      <button
        type="button"
        aria-label="Tutup notifikasi"
        className="absolute right-4 top-4 text-[#8C9BA8] transition-colors hover:text-[#445463]"
      >
        <CloseIcon />
      </button>
    </section>
  );
}
