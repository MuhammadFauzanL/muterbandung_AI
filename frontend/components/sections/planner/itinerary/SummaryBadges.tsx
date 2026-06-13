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
    <div className="rounded-[24px] border border-slate-200 bg-white p-6 shadow-sm">
      <div className="grid grid-cols-2 gap-3 mb-3">
        {/* Badge 1: Destinasi */}
        <div className="flex items-center justify-center gap-2 rounded-full bg-[#7FE0F4] px-4 py-2 text-xs font-semibold text-[#0B5C73]">
          <MapPin className="h-3 w-3" />
          {destinationsCount} Destinasi
        </div>

        {/* Badge 2: Penginapan */}
        {firstAccommodationName ? (
          <div className="flex items-center justify-center gap-2 rounded-full bg-[#7FE0F4] px-4 py-2 text-xs font-semibold text-[#0B5C73]">
            <Building className="h-3 w-3" />
            <span className="truncate">{firstAccommodationName}</span>
          </div>
        ) : (
          <div className="flex items-center justify-center gap-2 rounded-full bg-[#7FE0F4] px-4 py-2 text-xs font-semibold text-[#0B5C73]">
            <Building className="h-3 w-3" />
            0 Penginapan
          </div>
        )}

        {/* Badge 3: Durasi */}
        <div className="flex items-center justify-center gap-2 rounded-full bg-[#7FE0F4] px-4 py-2 text-xs font-semibold text-[#0B5C73]">
          <Calendar className="h-3 w-3" />
          {durationString}
        </div>

        {/* Badge 4: Orang */}
        <div className="flex items-center justify-center gap-2 rounded-full bg-[#7FE0F4] px-4 py-2 text-xs font-semibold text-[#0B5C73]">
          <Users className="h-3 w-3" />
          {maxGuests} Orang
        </div>
      </div>

      {/* Badge 5: Total Harga */}
      <div className="flex w-full items-center justify-center gap-2 rounded-full bg-[#185B64] px-4 py-2.5 text-sm font-bold text-white shadow-md">
        <Wallet className="h-4 w-4" />
        Rp{grandTotal.toLocaleString('id-ID')}
      </div>
    </div>
  );
}
