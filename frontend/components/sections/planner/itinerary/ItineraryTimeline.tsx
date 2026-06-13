import Image from 'next/image';
import { Trash2, Calendar } from 'lucide-react';

interface TimelineItem {
  time: string;
  title: string;
  type: 'destination' | 'accommodation';
  name: string;
  id?: string;
}

interface ItineraryTimelineProps {
  timelineItems: TimelineItem[];
  onRemoveDestination: (id: string, title: string) => void;
  onRemoveAccommodation: (name: string) => void;
}

export function ItineraryTimeline({
  timelineItems,
  onRemoveDestination,
  onRemoveAccommodation
}: ItineraryTimelineProps) {
  return (
    <div className="relative border-l border-dashed border-slate-300 ml-[25px] space-y-6 py-2">
      {timelineItems.length === 0 ? (
        <p className="pl-12 text-slate-500">Keranjang kosong. Yuk cari destinasi dulu!</p>
      ) : (
        timelineItems.map((item, index) => (
          <div key={index} className="relative pl-12 pr-2">
            {/* Timeline Hollow Dot */}
            <span 
              className={`absolute -left-[9px] top-1/2 -translate-y-1/2 flex h-[18px] w-[18px] items-center justify-center rounded-full border-[3px] bg-white shadow-sm ${item.type === 'destination' ? 'border-[#0E75BC]' : 'border-[#E94B35]'}`}
            />
            
            {/* Activity Card */}
            <div className="group relative overflow-hidden rounded-[20px] border border-slate-200 bg-white shadow-sm transition-all flex flex-col sm:flex-row p-4 gap-4">
              {/* Image Thumbnail */}
              <div className="relative h-40 sm:h-[130px] sm:w-[180px] rounded-xl overflow-hidden shrink-0">
                <Image 
                  src={item.type === 'destination' 
                    ? `/destinations/${item.id || 'kawah-putih'}.svg`
                    : 'https://images.unsplash.com/photo-1566073771259-6a8506099945?q=80&w=400&auto=format&fit=crop'} 
                  alt={item.title} 
                  fill 
                  className="object-cover" 
                />
              </div>
              
              <div className="flex-1 flex flex-col justify-between">
                <div>
                  <div className="flex items-start justify-between mb-2">
                    <span className={`font-bold text-sm ${item.type === 'destination' ? 'text-[#0E75BC]' : 'text-[#E94B35]'}`}>{item.time}</span>
                    <span className={`text-[10px] font-semibold px-3 py-1 rounded-full ${item.type === 'destination' ? 'bg-[#F2FAFE] text-[#557083]' : 'bg-[#E94B35] text-white'}`}>
                      {item.type === 'destination' ? '2 Jam • Alam' : 'Check-In • Hotel'}
                    </span>
                  </div>
                  <h3 className="text-base font-bold text-slate-900 mb-1">{item.title}</h3>
                  {item.type === 'destination' ? (
                    <p className="text-[12px] text-slate-600 leading-relaxed max-w-[90%]">
                      Menikmati pemandangan kawah vulkanik yang ikonik dengan suasana pegunungan yang sejuk.
                    </p>
                  ) : (
                    <div className="text-[10px] text-slate-600 mb-2">
                      <p>★ 4.8 • Jl. Raya Ciwidey - Patengan</p>
                      <div className="flex gap-4 mt-2">
                        <span className="flex items-center gap-1 font-semibold"><Calendar className="w-3 h-3 text-[#E94B35]" /> Check-in: 24 Mei 2024</span>
                        <span className="flex items-center gap-1 font-semibold"><Calendar className="w-3 h-3 text-[#E94B35]" /> Check-out: 25 Mei 2024</span>
                      </div>
                      <p className="mt-2">Waktu istirahat dan menikmati fasilitas hotel.</p>
                    </div>
                  )}
                </div>

                {/* Delete Button (Bottom Right) */}
                <div className="flex justify-end mt-4 sm:mt-0">
                  <button 
                    onClick={() => {
                      if (item.type === 'destination' && item.id) {
                        onRemoveDestination(item.id, item.title);
                      } else {
                        onRemoveAccommodation(item.name);
                      }
                    }}
                    className="flex items-center gap-2 rounded-full border border-red-200 bg-white px-4 py-1.5 text-xs font-semibold text-red-500 shadow-sm transition-all hover:bg-red-50"
                  >
                    <Trash2 className="h-3 w-3" />
                    Hapus Perjalanan
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))
      )}
    </div>
  );
}
