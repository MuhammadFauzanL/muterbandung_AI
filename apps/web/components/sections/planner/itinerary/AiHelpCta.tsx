import Image from 'next/image';

export function AiHelpCta() {
  return (
    <div className="flex items-end justify-end gap-3 mt-10 lg:pr-4">
      <div className="rounded-[10px] bg-white px-4 py-3 text-[12px] leading-5 text-[#6A7E8E] shadow-[0_12px_30px_rgba(17,73,112,0.14)] relative">
        <p>Butuh bantuan untuk menyesuaikan ulang?</p>
        <button
          type="button"
          onClick={() => window.dispatchEvent(new Event('open-chat'))}
          className="mt-1 font-semibold text-[#0E75BC] hover:text-[#095f99]"
        >
          Tanya Cepot AI
        </button>
      </div>
      <div className="relative h-12 w-12 overflow-hidden rounded-full bg-[#DDF3F8] shadow-[0_10px_24px_rgba(17,73,112,0.18)] shrink-0">
        <Image
          src="/images/welcome-cepot.png"
          alt="Cepot AI"
          fill
          sizes="48px"
          className="object-cover object-top"
        />
      </div>
    </div>
  );
}
