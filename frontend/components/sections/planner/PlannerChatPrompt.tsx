import Image from 'next/image';

export function PlannerChatPrompt() {
  return (
    <div className="hidden items-end justify-end gap-3 pr-8 lg:flex">
      <div className="rounded-[10px] bg-white px-4 py-3 text-[12px] leading-5 text-[#6A7E8E] shadow-[0_12px_30px_rgba(17,73,112,0.14)]">
        <p>Butuh bantuan menyusun Perjalanan?</p>
        <button
          type="button"
          className="mt-1 font-semibold text-[#0E75BC] hover:text-[#095f99]"
        >
          Tanya Cepot AI
        </button>
      </div>
      <div className="relative h-12 w-12 overflow-hidden rounded-full bg-[#DDF3F8] shadow-[0_10px_24px_rgba(17,73,112,0.18)]">
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
