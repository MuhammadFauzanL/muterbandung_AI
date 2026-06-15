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
    <div className="relative border-l border-dashed border-slate-300 ml-[25px] space-y-5 sm:space-y-6 py-2">
      {timelineItems.length === 0 ? (
        <p className="pl-12 text-slate-500">Keranjang kosong. Yuk cari destinasi dulu!</p>
      ) : (
        timelineItems.map((item, index) => (
          <div key={index} className="relative pl-10 sm:pl-12 pr-2">
            {/* Timeline Hollow Dot */}
            <span 
              className={`absolute -left-[9px] top-1/2 -translate-y-1/2 flex h-[18px] w-[18px] items-center justify-center rounded-full border-[3px] bg-white shadow-sm ${item.type === 'destination' ? 'border-[#0E75BC]' : 'border-[#E94B35]'}`}
            />
            
            {/* Activity Card */}
            <div className="group relative overflow-hidden rounded-[16px] sm:rounded-[20px] border border-slate-200 bg-white shadow-sm transition-all flex flex-col sm:flex-row p-3 sm:p-4 gap-3 sm:gap-4">
              {/* Image Thumbnail */}
              <div className="relative h-32 sm:h-[130px] sm:w-[180px] rounded-xl overflow-hidden shrink-0">
                <Image 
                  src={item.type === 'destination' 
                    ? `https://lh3.googleusercontent.com/gps-cs-s/APNQkAFaFXwEw1U4JIxhDsJyjEZJ7dqvRVW5IsAh8vwhX9CJumOqs71mWd90VbeY4WWgvBh6nodCe9tVRNO4574wsSgJnHLeoZRcFa7oXmZYME4fvSDhQ6Vgmu9TRYT8z7sUSaSkjUk_vQ=w408-h306-k-no`
                    : 'https://lh3.googleusercontent.com/gps-proxy/ALd4DhFQNQ81Dicl74zu40V7aXYY50dw0TH-lPCwm_rFUokItvPcAB2TR0TclWJS-39WNWfCJ_04IFMGsytAfz0mjmiv_2ft5DRYmyE0tyFhO6Q8WM81wJqxKvqNiKtB-0VBqYxss31T3exO_FUzUlc3d9J0f-idvXZvvVAfRhO6qZKDrOa9ali32Kou7Q=w455-h240-k-no'} 
                  alt={item.title} 
                  fill 
                  className="object-cover" 
                />
              </div>
              
              <div className="flex-1 flex flex-col justify-between">
                <div>
                  <div className="flex items-start justify-between mb-1.5 sm:mb-2">
                    <span className={`font-bold text-[13px] sm:text-sm ${item.type === 'destination' ? 'text-[#0E75BC]' : 'text-[#E94B35]'}`}>{item.time}</span>
                    <span className={`text-[9px] sm:text-[10px] font-semibold px-2 sm:px-3 py-0.5 sm:py-1 rounded-full ${item.type === 'destination' ? 'bg-[#F2FAFE] text-[#557083]' : 'bg-[#E94B35] text-white'}`}>
                      {item.type === 'destination' ? '2 Jam • Alam' : 'Check-In • Hotel'}
                    </span>
                  </div>
                  <h3 className="text-[15px] sm:text-base font-bold text-slate-900 mb-1 leading-tight">{item.title}</h3>
                  {item.type === 'destination' ? (
                    <div className="flex items-end justify-between gap-2 mt-1">
                      <p className="text-[11px] sm:text-[12px] text-slate-600 leading-relaxed flex-1">
                        Menikmati pemandangan kawah vulkanik yang ikonik dengan suasana pegunungan yang sejuk.
                      </p>
                      <button 
                        onClick={() => {
                          if (item.id) onRemoveDestination(item.id, item.title);
                        }}
                        className="flex items-center gap-1.5 sm:gap-2 rounded-full border border-red-200 bg-white px-3 sm:px-4 py-1.5 text-[11px] sm:text-xs font-semibold text-red-500 shadow-sm transition-all hover:bg-red-50 shrink-0"
                      >
                        <Trash2 className="h-3 w-3" />
                        Hapus
                      </button>
                    </div>
                  ) : (
                    <div className="text-[10px] text-slate-600 mb-2">
                      <p>★ 4.8 • Jl. Raya Ciwidey - Patengan</p>
                      <div className="flex flex-wrap gap-2 sm:gap-4 mt-1.5 sm:mt-2">
                        <span className="flex items-center gap-1 font-semibold"><Calendar className="w-3 h-3 text-[#E94B35]" /> Check-in: 24 Mei 2024</span>
                        <span className="flex items-center gap-1 font-semibold"><Calendar className="w-3 h-3 text-[#E94B35]" /> Check-out: 25 Mei 2024</span>
                      </div>
                      <div className="flex items-end justify-between gap-2 mt-1.5 sm:mt-2">
                        <p className="flex-1">Waktu istirahat dan menikmati fasilitas hotel.</p>
                        
                        {/* Delete Button (Bottom Right) for Accommodation */}
                        <button 
                          onClick={() => onRemoveAccommodation(item.name)}
                          className="flex items-center gap-1.5 sm:gap-2 rounded-full border border-red-200 bg-white px-3 sm:px-4 py-1.5 text-[11px] sm:text-xs font-semibold text-red-500 shadow-sm transition-all hover:bg-red-50 shrink-0"
                        >
                          <Trash2 className="h-3 w-3" />
                          Hapus
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))
      )}
    </div>
  );
}
