import { Map } from 'lucide-react';

export function RouteVisualization() {
  return (
    <section className="mb-4 sm:mb-10">
      <div className="flex items-center gap-2 mb-3 sm:mb-4 text-[#112F43]">
        <Map className="h-4 w-4 sm:h-5 sm:w-5 text-[#0E75BC]" />
        <h3 className="font-bold text-[15px] sm:text-lg">Visualisasi Rute Perjalanan</h3>
      </div>
      
      {/* Real Maps Embed */}
      <div className="relative w-full h-[250px] sm:h-[400px] rounded-[16px] sm:rounded-[24px] bg-slate-100 overflow-hidden shadow-sm border border-[#CFE5F2]">
        <iframe 
          src="https://www.openstreetmap.org/export/embed.html?bbox=107.3500%2C-7.2000%2C107.5000%2C-7.1000&layer=mapnik&marker=-7.1662%2C107.4021" 
          width="100%" 
          height="100%" 
          style={{ border: 0 }} 
          allowFullScreen={false} 
          loading="lazy" 
          className="absolute inset-0 grayscale-[20%] contrast-125"
        />
        
        {/* Overlay Badge Optional */}
        <div className="absolute top-3 left-3 sm:top-4 sm:left-4 bg-white/90 backdrop-blur-md px-3 py-1.5 rounded-full shadow-md border border-slate-200 pointer-events-none">
          <p className="text-[10px] sm:text-xs font-bold text-[#112F43]">📍 Rute Optimal</p>
        </div>
      </div>
    </section>
  );
}
