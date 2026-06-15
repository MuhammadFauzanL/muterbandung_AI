"use client";

import Link from 'next/link';
import { usePlanner } from '@/context/PlannerContext';
import { MapPin as PinIcon, Building as BuildingIcon, X as CloseIcon } from 'lucide-react';

export function TripSummary() {
  const { destinations, accommodations, removeDestination, removeAccommodation } = usePlanner();

  // Hitung jumlah destinasi (maksimal per hari misal 5)
  const destCount = destinations.length;
  // Hitung estimasi harga
  const totalAccommodationCost = accommodations.reduce((sum, acc) => sum + acc.totalPrice, 0);
  const totalCost = (destCount * 25000) + totalAccommodationCost;

  return (
    <aside className="rounded-[16px] border border-[#DCEAF3] bg-white p-3 sm:p-5 shadow-[0_10px_28px_rgba(17,73,112,0.07)]">
      <h2 className="text-[14px] sm:text-[15px] font-semibold text-[#202B37]">
        Ringkasan Perjalanan
      </h2>

      <div className="mt-3 sm:mt-4 space-y-2 sm:space-y-2.5">
        {destinations.map((dest) => (
          <div key={dest.id} className="flex items-center gap-2 rounded-[8px] sm:rounded-[10px] bg-[#EAF8FB] px-2.5 py-2 sm:px-3 sm:py-2.5 text-[11px] sm:text-[12px] font-semibold text-[#246983]">
            <PinIcon className="h-3 w-3 sm:h-4 sm:w-4 text-[#0E75BC]" />
            <span className="flex-1">{dest.title}</span>
            <button onClick={() => removeDestination(dest.id)} className="text-red-400 hover:text-red-600">
              <CloseIcon className="h-3 w-3 sm:h-4 sm:w-4" />
            </button>
          </div>
        ))}
        {destinations.length === 0 && (
          <div className="flex items-center gap-2 rounded-[8px] sm:rounded-[10px] border border-[#E3EEF4] bg-white px-2.5 py-2 sm:px-3 sm:py-2.5 text-[11px] sm:text-[12px] text-[#97A5B1]">
            <PinIcon className="h-3 w-3 sm:h-4 sm:w-4" />
            <span className="flex-1">Pilih destinasi...</span>
          </div>
        )}

        {accommodations.length > 0 ? (
          accommodations.map((acc) => (
            <div key={acc.name} className="flex items-center gap-2 rounded-[8px] sm:rounded-[10px] bg-[#EAF8FB] px-2.5 py-2 sm:px-3 sm:py-2.5 text-[11px] sm:text-[12px] font-semibold text-[#246983]">
              <BuildingIcon className="h-3 w-3 sm:h-4 sm:w-4" />
              <span className="flex-1">{acc.name}</span>
              <button onClick={() => removeAccommodation(acc.name)} className="text-red-400 hover:text-red-600">
                <CloseIcon className="h-3 w-3 sm:h-4 sm:w-4" />
              </button>
            </div>
          ))
        ) : (
          <div className="flex items-center gap-2 rounded-[8px] sm:rounded-[10px] border border-[#E3EEF4] bg-white px-2.5 py-2 sm:px-3 sm:py-2.5 text-[11px] sm:text-[12px] text-[#97A5B1]">
            <BuildingIcon className="h-3 w-3 sm:h-4 sm:w-4" />
            <span className="flex-1">Pilih penginapan...</span>
          </div>
        )}
      </div>

      <dl className="mt-3 sm:mt-5 space-y-1.5 sm:space-y-2.5 border-t border-[#EDF4F8] pt-3 sm:pt-4 text-[11px] sm:text-[12px]">
        <div className="flex items-center justify-between gap-4">
          <dt className="text-[#7B8B99]">Destinasi Dipilih</dt>
          <dd className="font-semibold text-[#202B37]">{destCount}/5 Destinasi</dd>
        </div>
        {accommodations.length > 0 && (
          <div className="flex items-center justify-between gap-4">
            <dt className="text-[#7B8B99]">Penginapan Dipilih</dt>
            <dd className="font-semibold text-[#202B37]">{accommodations.length} Hotel</dd>
          </div>
        )}
        <div className="flex items-center justify-between gap-4">
          <dt className="text-[#7B8B99]">Estimasi Biaya</dt>
          <dd className="font-semibold text-[#0E75BC]">Rp{totalCost.toLocaleString('id-ID')}</dd>
        </div>
      </dl>

      <div className="mt-3 sm:mt-5 space-y-2 sm:space-y-3">
        {accommodations.length === 0 ? (
          <Link
            href="/planner/penginapan"
            className="inline-flex h-9 sm:h-11 w-full items-center justify-center gap-2 rounded-[8px] sm:rounded-[10px] bg-[#0E75BC] px-4 text-[12px] sm:text-[13px] font-semibold text-white transition-colors hover:bg-[#095f99]"
          >
            Lanjut Pilih Penginapan
          </Link>
        ) : (
          <Link
            href="/planner/penginapan"
            className="inline-flex h-9 sm:h-11 w-full items-center justify-center gap-2 rounded-[8px] sm:rounded-[10px] border border-[#0E75BC] bg-white px-4 text-[12px] sm:text-[13px] font-semibold text-[#0E75BC] transition-colors hover:bg-[#F2FAFE]"
          >
            Pilih Penginapan Lain
          </Link>
        )}
        <Link
          href="/explore"
          className="inline-flex h-9 sm:h-11 w-full items-center justify-center rounded-[8px] sm:rounded-[10px] border border-[#0E75BC] bg-white px-4 text-[12px] sm:text-[13px] font-semibold text-[#0E75BC] transition-colors hover:bg-[#F2FAFE]"
        >
          Cari Destinasi Lain
        </Link>
        {accommodations.length > 0 || destinations.length > 0 ? (
          <Link
            href="/planner/itinerary"
            className="inline-flex h-9 sm:h-11 w-full items-center justify-center gap-2 rounded-[8px] sm:rounded-[10px] bg-[#E54545] px-4 text-[12px] sm:text-[13px] font-semibold text-white transition-colors hover:bg-[#d43b3b] shadow-md"
          >
            Buat Itinerary Saya
          </Link>
        ) : (
          <button
            disabled
            type="button"
            className="inline-flex h-9 sm:h-11 w-full items-center justify-center gap-2 rounded-[8px] sm:rounded-[10px] bg-slate-200 px-4 text-[12px] sm:text-[13px] font-semibold text-slate-400 cursor-not-allowed"
          >
            Buat Itinerary Saya
          </button>
        )}
      </div>
    </aside>
  );
}
