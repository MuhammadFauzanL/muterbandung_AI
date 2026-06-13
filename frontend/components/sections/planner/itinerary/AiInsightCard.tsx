import { Sparkles } from 'lucide-react';

export function AiInsightCard() {
  return (
    <section className="relative rounded-[24px] border border-[#CFE5F2] bg-[#F2FAFE] p-6 shadow-sm overflow-hidden">
      {/* Decorative Sparkles Top Right */}
      <div className="absolute top-2 right-2 opacity-50">
        <Sparkles className="h-12 w-12 text-[#CFE5F2]" />
      </div>

      <div className="flex gap-2 mb-3 text-[#0E75BC] items-center relative z-10">
        <Sparkles className="h-5 w-5" />
        <h3 className="font-bold text-lg">Insight dari Cepot AI</h3>
      </div>
      
      <p className="text-sm leading-relaxed text-[#557083] relative z-10">
        Itinerary ini disusun untuk meminimalkan waktu perjalanan, mengoptimalkan budget, dan memberikan pengalaman wisata yang lebih nyaman. Penginapan dipilih berdasarkan kedekatan dengan destinasi utama agar waktu perjalanan lebih efisien.
      </p>
    </section>
  );
}
