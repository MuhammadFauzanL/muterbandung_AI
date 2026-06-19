import { Map, Navigation } from 'lucide-react';
import dynamic from 'next/dynamic';

// Dynamically import MapComponent to disable SSR since Leaflet uses window object
const DynamicMap = dynamic(() => import('./MapComponent'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full bg-gradient-to-br from-[#EAF6FC] to-[#F8F9FA] animate-pulse flex flex-col items-center justify-center text-slate-400 gap-2">
      <div className="w-8 h-8 border-2 border-[#0E75BC] border-t-transparent rounded-full animate-spin" />
      <span className="text-xs font-medium">Memuat Peta...</span>
    </div>
  )
});

interface Location {
  latitude?: number;
  longitude?: number;
  title?: string;
  name?: string;
}

interface RouteVisualizationProps {
  destinations: Location[];
  accommodations?: Location[];
}

export function RouteVisualization({ destinations, accommodations = [] }: RouteVisualizationProps) {
  // Construct points array for MapComponent
  const points: { name: string, lat: number, lng: number, type: 'destination' | 'accommodation', index?: number }[] = [];
  
  let destIndex = 1;
  destinations.forEach(d => {
    if (d.latitude && d.longitude) {
      points.push({
        name: d.title || 'Destinasi',
        lat: d.latitude,
        lng: d.longitude,
        type: 'destination',
        index: destIndex++
      });
    }
  });

  accommodations.forEach(a => {
    if (a.latitude && a.longitude) {
      points.push({
        name: a.name || 'Penginapan',
        lat: a.latitude,
        lng: a.longitude,
        type: 'accommodation'
      });
    }
  });

  return (
    <section className="mb-4 sm:mb-10">
      <div className="flex items-center gap-2 mb-3 sm:mb-4 text-[#112F43]">
        <div className="h-7 w-7 sm:h-8 sm:w-8 bg-[#EAF6FC] rounded-lg flex items-center justify-center">
          <Navigation className="h-3.5 w-3.5 sm:h-4 sm:w-4 text-[#0E75BC]" />
        </div>
        <div>
          <h3 className="font-bold text-[15px] sm:text-lg leading-tight">Visualisasi Rute Perjalanan</h3>
          {points.length >= 2 && (
            <p className="text-[10px] sm:text-xs text-slate-500 leading-tight">Rute jalan ditampilkan berdasarkan data OpenStreetMap</p>
          )}
        </div>
      </div>
      
      {/* Map Container */}
      <div className="relative w-full h-[280px] sm:h-[420px] rounded-[16px] sm:rounded-[24px] bg-slate-100 overflow-hidden shadow-sm border border-[#CFE5F2]">
        <DynamicMap points={points} />
        
        {/* Top Left Badge */}
        <div className="absolute top-3 left-3 sm:top-4 sm:left-4 bg-white/90 backdrop-blur-md px-3 py-1.5 rounded-full shadow-md border border-slate-200 pointer-events-none z-20 flex items-center gap-1.5">
          <div className="w-2 h-2 rounded-full bg-[#10B981] animate-pulse" />
          <p className="text-[10px] sm:text-xs font-bold text-[#112F43] flex items-center gap-1">
            <svg className="w-3 h-3 text-[#E94B35]" viewBox="0 0 24 24" fill="currentColor" stroke="none"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>
            {points.length >= 2 ? 'Rute Jalan Nyata' : 'Rute Perjalanan'}
          </p>
        </div>

        {/* Legend */}
        {points.length >= 2 && (
          <div className="absolute top-3 right-3 sm:top-4 sm:right-4 bg-white/90 backdrop-blur-md px-2.5 py-2 rounded-xl shadow-md border border-slate-200 pointer-events-none z-20">
            <div className="space-y-1.5">
              <div className="flex items-center gap-1.5">
                <div className="w-3 h-3 rounded-full bg-gradient-to-br from-[#10B981] to-[#059669] border border-white shadow-sm" />
                <span className="text-[8px] sm:text-[10px] text-slate-600 font-medium">Start</span>
              </div>
              <div className="flex items-center gap-1.5">
                <div className="w-3 h-3 rounded-full bg-gradient-to-br from-[#0E75BC] to-[#0B5C73] border border-white shadow-sm" />
                <span className="text-[8px] sm:text-[10px] text-slate-600 font-medium">Destinasi</span>
              </div>
              {accommodations.some(a => a.latitude && a.longitude) && (
                <div className="flex items-center gap-1.5">
                  <div className="w-3 h-3 rounded-full bg-gradient-to-br from-[#E94B35] to-[#C93A28] border border-white shadow-sm" />
                  <span className="text-[8px] sm:text-[10px] text-slate-600 font-medium">Hotel</span>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
