import { BrainCircuit, Map, CalendarRange } from 'lucide-react';

export function FeaturesSection() {
  const features = [
    {
      title: 'AI Planner Cerdas',
      description: 'Algoritma AI kami menganalisis ribuan data untuk memberikan rekomendasi yang benar-benar personal sesuai minat Anda.',
      icon: <BrainCircuit className="h-5 w-5 text-[#0E75BC]" />,
      iconBg: 'bg-[#EAF6FC]',
    },
    {
      title: 'Kearifan Lokal',
      description: 'Bukan sekadar destinasi wisata biasa. Temukan hidden gems Bandung yang hanya diketahui oleh warga lokal.',
      icon: <Map className="h-5 w-5 text-[#0E75BC]" />,
      iconBg: 'bg-[#EAF6FC]',
    },
    {
      title: 'Itinerary Instan',
      description: 'Lupakan berjam-jam riset. Dapatkan rencana perjalanan lengkap dari pagi hingga malam dalam hitungan detik.',
      icon: <CalendarRange className="h-5 w-5 text-[#E54545]" />,
      iconBg: 'bg-[#FEECEB]',
    },
  ];

  return (
    <section className="bg-white py-6 sm:py-10">
      <div className="mx-auto max-w-[1180px] px-4 sm:px-8">
        <div className="text-center max-w-2xl mx-auto mb-4 sm:mb-8">
          <h2 className="text-[22px] sm:text-[28px] font-bold text-[#14528E] mb-1 sm:mb-2">Kenapa MuterBandung?</h2>
          <p className="text-[13px] sm:text-[15px] text-slate-500">Solusi cerdas untuk liburan yang tak terlupakan.</p>
        </div>

        {/* Container for cards - Horizontal scroll on mobile, Grid on desktop */}
        <div className="flex overflow-x-auto snap-x scroll-smooth gap-4 pb-4 md:grid md:grid-cols-3 md:gap-6 hide-scrollbar -mx-4 px-4 sm:mx-0 sm:px-0">
          {features.map((feature, idx) => (
            <div 
              key={idx} 
              className="snap-center shrink-0 w-[85vw] sm:w-[320px] md:w-auto rounded-xl sm:rounded-2xl border border-[#D9E8F3] bg-white p-4 sm:p-6 shadow-sm hover:shadow-md transition-shadow"
            >
              <div className="flex gap-3 sm:gap-4 flex-row items-center text-left">
                <div className={`h-10 w-10 sm:h-12 sm:w-12 rounded-full sm:rounded-xl flex items-center justify-center shrink-0 ${feature.iconBg}`}>
                  {feature.icon}
                </div>
                <div>
                  <h3 className="text-[15px] sm:text-[16px] font-bold text-[#14528E] mb-1">{feature.title}</h3>
                  <p className="text-[13px] text-slate-600 leading-relaxed line-clamp-3 sm:line-clamp-none">{feature.description}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
