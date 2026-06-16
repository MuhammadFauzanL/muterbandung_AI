interface Accommodation {
  name: string;
  nights: number;
  totalPrice: number;
}

interface BudgetSummaryProps {
  totalDestinationCost: number;
  totalAccommodationCost: number;
  accommodations: Accommodation[];
  grandTotal: number;
}

export function BudgetSummary({
  totalDestinationCost,
  totalAccommodationCost,
  accommodations,
  grandTotal
}: BudgetSummaryProps) {
  return (
    <section className="rounded-[16px] sm:rounded-[24px] bg-[#E8F3FB] px-4 py-3 sm:p-6 shadow-sm">
      <h3 className="font-bold text-[14px] sm:text-lg text-[#112F43] mb-2 sm:mb-5">Estimasi Anggaran</h3>
      
      <div className="space-y-1.5 sm:space-y-4 text-[12px] sm:text-sm font-medium">
        {/* Tiket Wisata */}
        <div className="flex justify-between items-center gap-2">
          <span className="text-[#557083]">Tiket Wisata</span>
          <span className="font-bold text-[#112F43] text-right">Rp {totalDestinationCost.toLocaleString('id-ID')}</span>
        </div>
        
        {/* Akomodasi */}
        <div>
          <div className="flex justify-between items-center gap-2">
            <span className="text-[#557083] flex items-center gap-2">Akomodasi</span>
            <span className="font-bold text-[#112F43] text-right">Rp {totalAccommodationCost.toLocaleString('id-ID')}</span>
          </div>
          {accommodations.map((acc, index) => (
            <div key={index} className="text-[10px] font-normal text-[#0E75BC]">
              {acc.name} ({acc.nights} malam @ Rp{(acc.totalPrice / acc.nights).toLocaleString('id-ID')})
            </div>
          ))}
        </div>
      </div>
      
      <div className="mt-2.5 sm:mt-6 pt-2.5 sm:pt-5 border-t border-[#CFE5F2] flex justify-between items-center gap-2">
        <span className="text-[14px] sm:text-lg font-bold text-[#112F43]">Total Estimasi</span>
        <span className="text-[16px] sm:text-2xl font-bold text-[#0B5C73] text-right">Rp {grandTotal.toLocaleString('id-ID')}</span>
      </div>
    </section>
  );
}
