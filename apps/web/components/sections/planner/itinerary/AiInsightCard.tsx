import { Sparkles } from 'lucide-react';

interface AiInsightCardProps {
  destinationsCount: number;
  accommodationsCount: number;
  durationString: string;
}

export function AiInsightCard({ destinationsCount, accommodationsCount, durationString }: AiInsightCardProps) {
  let insightText = "Mulai tambahkan destinasi ke Planner untuk mendapatkan insight perjalanan dari Cepot AI.";
  
  if (destinationsCount > 0 && accommodationsCount === 0) {
    insightText = `Kamu telah merencanakan ${destinationsCount} destinasi yang menarik! Cepot merekomendasikan untuk menambahkan penginapan agar perjalanan ${durationString} kamu lebih nyaman dan terstruktur.`;
  } else if (destinationsCount > 0 && accommodationsCount > 0) {
    insightText = `Itinerary ini disusun untuk meminimalkan waktu perjalanan, mengoptimalkan budget, dan memberikan pengalaman wisata yang nyaman selama ${durationString}. Penginapan telah dipilih agar dekat dengan lokasi utama.`;
  } else if (destinationsCount === 0 && accommodationsCount > 0) {
    insightText = `Penginapan sudah siap! Sekarang saatnya memilih destinasi wisata di sekitar penginapanmu agar waktu liburanmu maksimal.`;
  }

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
        {insightText}
      </p>
    </section>
  );
}
