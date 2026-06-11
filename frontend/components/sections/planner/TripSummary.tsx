import Link from 'next/link';
import {
  HotelIcon as BuildingIcon,
  MapPinIcon as PinIcon,
} from '@/components/ui/icons';

export function TripSummary() {
  return (
    <aside className="rounded-[16px] border border-[#DCEAF3] bg-white p-5 shadow-[0_10px_28px_rgba(17,73,112,0.07)]">
      <h2 className="text-[15px] font-semibold text-[#202B37]">
        Ringkasan Perjalanan
      </h2>

      <div className="mt-4 space-y-2.5">
        <div className="flex items-center gap-2 rounded-[10px] bg-[#EAF8FB] px-3 py-2.5 text-[12px] font-semibold text-[#246983]">
          <PinIcon className="h-4 w-4 text-[#0E75BC]" />
          Kawah Putih
        </div>
        <div className="flex items-center gap-2 rounded-[10px] border border-[#E3EEF4] bg-white px-3 py-2.5 text-[12px] text-[#97A5B1]">
          <PinIcon className="h-4 w-4" />
          Pilih destinasi selanjutnya...
        </div>
      </div>

      <dl className="mt-5 space-y-2.5 border-t border-[#EDF4F8] pt-4 text-[12px]">
        <div className="flex items-center justify-between gap-4">
          <dt className="text-[#7B8B99]">Destinasi Dipilih</dt>
          <dd className="font-semibold text-[#202B37]">1/5 Destinasi</dd>
        </div>
        <div className="flex items-center justify-between gap-4">
          <dt className="text-[#7B8B99]">Estimasi Durasi</dt>
          <dd className="font-semibold text-[#202B37]">2-3 Jam</dd>
        </div>
        <div className="flex items-center justify-between gap-4">
          <dt className="text-[#7B8B99]">Estimasi Biaya</dt>
          <dd className="font-semibold text-[#0E75BC]">Rp50.000</dd>
        </div>
      </dl>

      <div className="mt-5 space-y-3">
        <Link
          href="/planner/penginapan"
          className="inline-flex h-11 w-full items-center justify-center gap-2 rounded-[10px] bg-[#0E75BC] px-4 text-[13px] font-semibold text-white transition-colors hover:bg-[#095f99]"
        >
          <BuildingIcon />
          Lanjut Pilih Penginapan
        </Link>
        <Link
          href="/explore"
          className="inline-flex h-11 w-full items-center justify-center rounded-[10px] border border-[#0E75BC] bg-white px-4 text-[13px] font-semibold text-[#0E75BC] transition-colors hover:bg-[#F2FAFE]"
        >
          Cari Destinasi Lain
        </Link>
      </div>

      <div className="mt-5 flex gap-3 rounded-[12px] bg-[#F0F7FC] px-4 py-3">
        <div className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[#0E75BC] text-white">
          <PinIcon className="h-4 w-4" />
        </div>
        <p className="text-[12px] leading-5 text-[#557083]">
          Kamu bisa menghemat Rp25.000 jika mengunjungi destinasi yang
          searah.
        </p>
      </div>
    </aside>
  );
}
