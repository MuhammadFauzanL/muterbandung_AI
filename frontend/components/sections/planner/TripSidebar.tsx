import Link from 'next/link';
import { MapPinIcon, WalletIcon } from '@/components/ui/icons';

export function TripSidebar() {
  return (
    <aside className="rounded-[16px] border border-[#DCEAF3] bg-white p-5 shadow-[0_10px_28px_rgba(17,73,112,0.07)]">
      <h2 className="text-[15px] font-semibold text-[#202B37]">
        Ringkasan Perjalanan
      </h2>

      <div className="mt-4 space-y-2.5">
        <div className="flex items-center gap-2 rounded-[10px] bg-[#EAF8FB] px-3 py-2.5 text-[12px] font-semibold text-[#246983]">
          <MapPinIcon />
          Kawah Putih
        </div>
        <div className="flex items-center gap-2 rounded-[10px] bg-[#EAF8FB] px-3 py-2.5 text-[12px] font-semibold text-[#246983]">
          <MapPinIcon />
          Ranca Upas
        </div>
        <div className="flex items-center gap-2 rounded-[10px] border border-[#E3EEF4] bg-white px-3 py-2.5 text-[12px] text-[#97A5B1]">
          <WalletIcon />
          Pilih penginapan...
        </div>
      </div>

      <dl className="mt-5 space-y-2.5 border-t border-[#EDF4F8] pt-4 text-[12px]">
        <div className="flex items-center justify-between gap-4">
          <dt className="text-[#7B8B99]">Tanggal Check-in</dt>
          <dd className="font-semibold text-[#202B37]">12 Jun 2026</dd>
        </div>
        <div className="flex items-center justify-between gap-4">
          <dt className="text-[#7B8B99]">Durasi Menginap</dt>
          <dd className="font-semibold text-[#202B37]">1 Malam</dd>
        </div>
        <div className="flex items-center justify-between gap-4">
          <dt className="text-[#7B8B99]">Budget Penginapan</dt>
          <dd className="font-semibold text-[#0E75BC]">Rp500rb - Rp900rb</dd>
        </div>
      </dl>

      <div className="mt-5 rounded-[12px] bg-[#F7FBF5] px-4 py-3 text-[12px] leading-5 text-[#4F7044]">
        Opsi paling efisien saat ini adalah Bobocabin Ranca Upas karena dekat
        dengan destinasi lanjutan dan masuk rentang budget.
      </div>

      <div className="mt-5 space-y-3">
        <button
          type="button"
          className="inline-flex h-11 w-full items-center justify-center rounded-[10px] bg-[#0E75BC] px-4 text-[13px] font-semibold text-white transition-colors hover:bg-[#095f99]"
        >
          Simpan Pilihan
        </button>
        <Link
          href="/planner"
          className="inline-flex h-11 w-full items-center justify-center rounded-[10px] border border-[#0E75BC] bg-white px-4 text-[13px] font-semibold text-[#0E75BC] transition-colors hover:bg-[#F2FAFE]"
        >
          Kembali ke Planner
        </Link>
      </div>
    </aside>
  );
}
