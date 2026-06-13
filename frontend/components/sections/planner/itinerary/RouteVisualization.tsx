import Image from 'next/image';
import { Map } from 'lucide-react';

export function RouteVisualization() {
  return (
    <section className="mb-10">
      <div className="flex items-center gap-2 mb-4 text-[#112F43]">
        <Map className="h-5 w-5 text-[#0E75BC]" />
        <h3 className="font-bold text-lg">Visualisasi Rute Perjalanan</h3>
      </div>
      
      {/* Wide Map Box */}
      <div className="relative w-full h-[320px] rounded-[24px] bg-[#424A4D] overflow-hidden shadow-inner flex border border-slate-200">
        <Image 
          src="/images/background.png" 
          alt="Map Background" 
          fill 
          className="object-cover opacity-30 mix-blend-overlay" 
        />
        
        {/* Mock UI: Floating List on Left */}
        <div className="absolute top-8 bottom-8 left-8 w-[240px] bg-[#F2F4F5] rounded-3xl p-6 shadow-xl flex flex-col justify-center">
          <div className="relative border-l border-dashed border-slate-400 ml-3 space-y-8">
            <div className="relative pl-6">
              <span className="absolute -left-[6px] top-1/2 -translate-y-1/2 h-3 w-3 rounded-full bg-[#112F43]" />
              <p className="text-xs font-bold text-[#112F43]">Patuha Resort</p>
            </div>
            <div className="relative pl-6">
              <span className="absolute -left-[6px] top-1/2 -translate-y-1/2 h-3 w-3 rounded-full bg-[#0E75BC]" />
              <p className="text-xs font-bold text-[#112F43]">Kawah Putih Area</p>
            </div>
            <div className="relative pl-6">
              <span className="absolute -left-[6px] top-1/2 -translate-y-1/2 h-3 w-3 rounded-full bg-[#E94B35]" />
              <p className="text-xs font-bold text-[#112F43]">Lembang (Opsional)</p>
            </div>
          </div>
        </div>
        
        {/* Mobile Mockup Frame overlapping map */}
        <div className="absolute left-1/2 top-4 bottom-[-40px] w-[300px] -translate-x-1/2 rounded-[2rem] border-[4px] border-[#556064] bg-[#556064] overflow-hidden shadow-2xl">
          <div className="relative w-full h-full bg-[#3D474A]">
             <Image 
                src="/images/background.png" 
                alt="Map Background" 
                fill 
                className="object-cover opacity-40 mix-blend-overlay" 
              />
              <svg className="absolute inset-0 w-full h-full" viewBox="0 0 300 500" style={{ pointerEvents: 'none' }}>
                <path d="M 120 150 Q 180 250 150 350" fill="none" stroke="#7FE0F4" strokeWidth="3" />
                <circle cx="120" cy="150" r="5" fill="#7FE0F4" stroke="white" strokeWidth="2"/>
                <circle cx="180" cy="250" r="5" fill="#7FE0F4" stroke="white" strokeWidth="2"/>
                <circle cx="150" cy="350" r="5" fill="#7FE0F4" stroke="white" strokeWidth="2"/>
              </svg>
          </div>
        </div>
      </div>
    </section>
  );
}
