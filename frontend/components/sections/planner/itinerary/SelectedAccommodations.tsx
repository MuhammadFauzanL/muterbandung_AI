import Image from 'next/image';
import { Building, Star } from 'lucide-react';

interface Accommodation {
  name: string;
  nights: number;
  basePrice: number;
  totalPrice: number;
}

interface SelectedAccommodationsProps {
  accommodations: Accommodation[];
}

export function SelectedAccommodations({ accommodations }: SelectedAccommodationsProps) {
  if (accommodations.length === 0) return null;

  return (
    <>
      {accommodations.map((acc, index) => (
        <section key={index} className="rounded-[16px] sm:rounded-[24px] border border-slate-200 bg-white p-4 sm:p-5 shadow-sm">
          <h3 className="font-bold text-[15px] sm:text-base text-[#112F43] flex items-center gap-2 mb-3">
            <Building className="h-4 w-4 sm:h-5 sm:w-5 text-[#0E75BC]" /> Penginapan Terpilih
          </h3>
          
          <div className="space-y-3 sm:space-y-4">
            <div className="relative w-full h-32 sm:h-40 overflow-hidden rounded-xl bg-slate-200">
              <Image 
                src="https://lh3.googleusercontent.com/gps-proxy/ALd4DhFQNQ81Dicl74zu40V7aXYY50dw0TH-lPCwm_rFUokItvPcAB2TR0TclWJS-39WNWfCJ_04IFMGsytAfz0mjmiv_2ft5DRYmyE0tyFhO6Q8WM81wJqxKvqNiKtB-0VBqYxss31T3exO_FUzUlc3d9J0f-idvXZvvVAfRhO6qZKDrOa9ali32Kou7Q=w455-h240-k-no" 
                alt={acc.name} 
                fill 
                className="object-cover" 
              />
            </div>
            
            <div>
              <div className="flex items-start sm:items-center justify-between gap-2">
                <h4 className="font-bold text-[#112F43] text-[15px] sm:text-lg leading-tight">{acc.name}</h4>
                <span className="bg-[#FCD3D1] text-[#E94B35] px-1.5 sm:px-2 py-0.5 sm:py-1 rounded-md shadow-sm flex items-center gap-1 font-bold text-[10px] sm:text-xs shrink-0">
                  <Star className="h-2.5 w-2.5 sm:h-3 sm:w-3 fill-current" /> 4.8
                </span>
              </div>
              <div className="flex items-center gap-1 text-[11px] sm:text-xs text-slate-500 mt-1">
                <MapPinIcon className="h-3 w-3 shrink-0" />
                <span>0.5 km dari Kawah Putih</span>
              </div>
            </div>
              
            <div className="grid grid-cols-2 gap-2 sm:gap-3 text-[11px] sm:text-xs">
              <div className="bg-[#F2FAFE] p-2.5 sm:p-3 rounded-xl border border-[#CFE5F2]">
                <p className="text-[#557083] mb-0.5 sm:mb-1 text-[10px] sm:text-xs">Durasi</p>
                <p className="font-bold text-[#112F43] leading-tight">{acc.nights + 1} Hari {acc.nights} Malam</p>
              </div>
              <div className="bg-[#F2FAFE] p-2.5 sm:p-3 rounded-xl border border-[#CFE5F2]">
                <p className="text-[#557083] mb-0.5 sm:mb-1 text-[10px] sm:text-xs">Harga/Malam</p>
                <p className="font-bold text-[#112F43] leading-tight">Rp {acc.basePrice.toLocaleString('id-ID')}</p>
              </div>
            </div>
              
            <div className="pt-2 sm:pt-3 border-t border-slate-200 flex justify-between items-center text-[13px] sm:text-sm">
              <span className="text-[#557083] font-medium">Total Akomodasi</span>
              <span className="font-bold text-[#185B64] text-[15px] sm:text-lg">Rp {acc.totalPrice.toLocaleString('id-ID')}</span>
            </div>
          </div>
        </section>
      ))}
    </>
  );
}

function MapPinIcon({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" className={className} fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
      <circle cx="12" cy="10" r="3" />
    </svg>
  );
}
