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
    <section className="rounded-[24px] bg-[#E8F3FB] p-6 shadow-sm">
      <h3 className="font-bold text-lg text-[#112F43] mb-5">Estimasi Anggaran</h3>
      
      <div className="space-y-4 text-sm font-medium">
        {/* Tiket Wisata */}
        <div className="flex justify-between items-center">
          <span className="text-[#557083]">Tiket Wisata</span>
          <span className="font-bold text-[#112F43]">Rp {totalDestinationCost.toLocaleString('id-ID')}</span>
        </div>
        
        {/* Akomodasi */}
        <div>
          <div className="flex justify-between items-center">
            <span className="text-[#557083] flex items-center gap-2">Akomodasi</span>
            <span className="font-bold text-[#112F43]">Rp {totalAccommodationCost.toLocaleString('id-ID')}</span>
          </div>
          {accommodations.map((acc, index) => (
            <div key={index} className="text-[10px] font-normal text-[#0E75BC] mt-0.5">
              {acc.name} ({acc.nights} malam @ Rp{(acc.totalPrice / acc.nights).toLocaleString('id-ID')})
            </div>
          ))}
        </div>
      </div>
      
      <div className="mt-6 pt-5 border-t border-[#CFE5F2] flex justify-between items-center">
        <span className="text-lg font-bold text-[#112F43] leading-tight">Total<br/>Estimasi</span>
        <span className="text-2xl font-bold text-[#0B5C73]">Rp<br/>{grandTotal.toLocaleString('id-ID')}</span>
      </div>
    </section>
  );
}
