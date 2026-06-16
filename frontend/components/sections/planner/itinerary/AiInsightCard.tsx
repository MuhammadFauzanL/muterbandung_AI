import { Sparkles } from 'lucide-react';

export function AiInsightCard() {
  return (
    <section className="relative rounded-[16px] sm:rounded-[24px] border border-[#CFE5F2] bg-[#F2FAFE] p-4 sm:p-6 shadow-sm overflow-hidden">
      {/* Decorative Sparkles Top Right */}
      <div className="absolute top-2 right-2 opacity-50">
        <Sparkles className="h-10 w-10 sm:h-12 sm:w-12 text-[#CFE5F2]" />
      </div>

      <div className="flex gap-1.5 sm:gap-2 mb-2 sm:mb-3 text-[#0E75BC] items-center relative z-10">
        <Sparkles className="h-4 w-4 sm:h-5 sm:w-5" />
        <h3 className="font-bold text-[15px] sm:text-lg">Insight dari Cepot AI</h3>
      </div>
      
      <p className="text-[12px] sm:text-sm leading-relaxed text-[#557083] relative z-10">
        Itinerary ini disusun untuk meminimalkan waktu perjalanan, mengoptimalkan budget, dan memberikan pengalaman wisata yang lebih nyaman. Penginapan dipilih berdasarkan kedekatan dengan destinasi utama agar waktu perjalanan lebih efisien.
      </p>
    </section>
  );
}
