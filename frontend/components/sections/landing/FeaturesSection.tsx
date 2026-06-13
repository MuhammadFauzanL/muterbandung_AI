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
    <section className="bg-white py-16">
      <div className="mx-auto max-w-[1180px] px-5 sm:px-8">
        <div className="text-center max-w-2xl mx-auto mb-10">
          <h2 className="text-[28px] font-bold text-[#14528E] mb-2">Kenapa MuterBandung?</h2>
          <p className="text-[15px] text-slate-500">Solusi cerdas untuk liburan yang tak terlupakan.</p>
        </div>

        <div className="grid gap-6 md:grid-cols-3">
          {features.map((feature, idx) => (
            <div key={idx} className="rounded-2xl border border-[#D9E8F3] bg-white p-6 shadow-sm hover:shadow-md transition-shadow">
              <div className="flex gap-4">
                <div className={`h-12 w-12 rounded-xl flex items-center justify-center shrink-0 ${feature.iconBg}`}>
                  {feature.icon}
                </div>
                <div>
                  <h3 className="text-[16px] font-bold text-[#14528E] mb-2">{feature.title}</h3>
                  <p className="text-[13px] text-slate-600 leading-relaxed">{feature.description}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
