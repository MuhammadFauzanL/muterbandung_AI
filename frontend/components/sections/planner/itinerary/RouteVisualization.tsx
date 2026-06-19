import { Map } from 'lucide-react';
import dynamic from 'next/dynamic';

// Dynamically import MapComponent to disable SSR since Leaflet uses window object
const DynamicMap = dynamic(() => import('./MapComponent'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full bg-slate-100 animate-pulse flex items-center justify-center text-slate-400">
      Memuat Peta...
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
        <Map className="h-4 w-4 sm:h-5 sm:w-5 text-[#0E75BC]" />
        <h3 className="font-bold text-[15px] sm:text-lg">Visualisasi Rute Perjalanan</h3>
      </div>
      
      {/* Real Maps Embed */}
      <div className="relative w-full h-[250px] sm:h-[400px] rounded-[16px] sm:rounded-[24px] bg-slate-100 overflow-hidden shadow-sm border border-[#CFE5F2]">
        <DynamicMap points={points} />
        
        {/* Overlay Badge Optional */}
        <div className="absolute top-3 left-3 sm:top-4 sm:left-4 bg-white/90 backdrop-blur-md px-3 py-1.5 rounded-full shadow-md border border-slate-200 pointer-events-none z-20">
          <p className="text-[10px] sm:text-xs font-bold text-[#112F43]">📍 Rute Optimal</p>
        </div>
      </div>
    </section>
  );
}
