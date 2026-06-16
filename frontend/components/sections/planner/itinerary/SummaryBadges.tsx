import { MapPin, Building, Calendar, Users, Wallet } from 'lucide-react';

interface SummaryBadgesProps {
  destinationsCount: number;
  firstAccommodationName?: string;
  durationString: string;
  maxGuests: number;
  grandTotal: number;
}

export function SummaryBadges({
  destinationsCount,
  firstAccommodationName,
  durationString,
  maxGuests,
  grandTotal
}: SummaryBadgesProps) {
  return (
    <div className="rounded-[16px] sm:rounded-[24px] border border-slate-200 bg-white p-4 sm:p-6 shadow-sm">
      <div className="grid grid-cols-2 gap-2 sm:gap-3 mb-3 sm:mb-4">
        {/* Badge 1: Destinasi */}
        <div className="flex items-center justify-center gap-1.5 sm:gap-2 rounded-full bg-[#7FE0F4] px-3 py-1.5 sm:px-4 sm:py-2 text-[11px] sm:text-xs font-semibold text-[#0B5C73]">
          <MapPin className="h-3 w-3 shrink-0" />
          <span className="truncate">{destinationsCount} Destinasi</span>
        </div>

        {/* Badge 2: Penginapan */}
        {firstAccommodationName ? (
          <div className="flex items-center justify-center gap-1.5 sm:gap-2 rounded-full bg-[#7FE0F4] px-3 py-1.5 sm:px-4 sm:py-2 text-[11px] sm:text-xs font-semibold text-[#0B5C73]">
            <Building className="h-3 w-3 shrink-0" />
            <span className="truncate">{firstAccommodationName}</span>
          </div>
        ) : (
          <div className="flex items-center justify-center gap-1.5 sm:gap-2 rounded-full bg-[#7FE0F4] px-3 py-1.5 sm:px-4 sm:py-2 text-[11px] sm:text-xs font-semibold text-[#0B5C73]">
            <Building className="h-3 w-3 shrink-0" />
            <span className="truncate">0 Penginapan</span>
          </div>
        )}

        {/* Badge 3: Durasi */}
        <div className="flex items-center justify-center gap-1.5 sm:gap-2 rounded-full bg-[#7FE0F4] px-3 py-1.5 sm:px-4 sm:py-2 text-[11px] sm:text-xs font-semibold text-[#0B5C73]">
          <Calendar className="h-3 w-3 shrink-0" />
          <span className="truncate">{durationString}</span>
        </div>

        {/* Badge 4: Orang */}
        <div className="flex items-center justify-center gap-1.5 sm:gap-2 rounded-full bg-[#7FE0F4] px-3 py-1.5 sm:px-4 sm:py-2 text-[11px] sm:text-xs font-semibold text-[#0B5C73]">
          <Users className="h-3 w-3 shrink-0" />
          <span className="truncate">{maxGuests} Orang</span>
        </div>
      </div>

      {/* Badge 5: Total Harga */}
      <div className="flex w-full items-center justify-center gap-2 rounded-full bg-[#185B64] px-3 py-2 sm:px-4 sm:py-2.5 text-[13px] sm:text-sm font-bold text-white shadow-md">
        <Wallet className="h-3.5 w-3.5 sm:h-4 w-4 shrink-0" />
        <span className="truncate">Rp{grandTotal.toLocaleString('id-ID')}</span>
      </div>
    </div>
  );
}
