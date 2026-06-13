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
        <section key={index} className="rounded-[24px] border border-slate-200 bg-white p-5 shadow-sm">
          <h3 className="font-bold text-base text-[#112F43] flex items-center gap-2 mb-3">
            <Building className="h-5 w-5 text-[#0E75BC]" /> Penginapan Terpilih
          </h3>
          
          <div className="space-y-4">
            <div className="relative w-full h-40 overflow-hidden rounded-xl bg-slate-200">
              <Image 
                src="/images/background.png" 
                alt={acc.name} 
                fill 
                className="object-cover" 
              />
            </div>
            
            <div>
              <div className="flex items-center justify-between">
                <h4 className="font-bold text-[#112F43] text-lg">{acc.name}</h4>
                <span className="bg-[#FCD3D1] text-[#E94B35] px-2 py-1 rounded-md shadow-sm flex items-center gap-1 font-bold text-xs">
                  <Star className="h-3 w-3 fill-current" /> 4.8
                </span>
              </div>
              <div className="flex items-center gap-1 text-xs text-slate-500 mt-1">
                <MapPinIcon className="h-3 w-3" />
                <span>0.5 km dari Kawah Putih</span>
              </div>
            </div>
              
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="bg-[#F2FAFE] p-3 rounded-xl border border-[#CFE5F2]">
                <p className="text-[#557083] mb-1">Durasi</p>
                <p className="font-bold text-[#112F43]">{acc.nights + 1} Hari {acc.nights} Malam</p>
              </div>
              <div className="bg-[#F2FAFE] p-3 rounded-xl border border-[#CFE5F2]">
                <p className="text-[#557083] mb-1">Harga/Malam</p>
                <p className="font-bold text-[#112F43]">Rp {acc.basePrice.toLocaleString('id-ID')}</p>
              </div>
            </div>
              
            <div className="pt-3 border-t border-slate-200 flex justify-between items-center text-sm">
              <span className="text-[#557083] font-medium">Total Akomodasi</span>
              <span className="font-bold text-[#185B64] text-lg">Rp {acc.totalPrice.toLocaleString('id-ID')}</span>
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
