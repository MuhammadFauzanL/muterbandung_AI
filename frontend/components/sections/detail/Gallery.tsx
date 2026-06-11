import Image from 'next/image';
import type { DestinationDetail } from '@/types';

export function Gallery({ images }: { images: DestinationDetail['gallery'] }) {
  return (
    <section className="rounded-2xl border border-[#D9E8F3] bg-white p-5 shadow-[0_12px_28px_rgba(15,23,42,0.05)]">
      <h2 className="text-[22px] font-semibold text-slate-950">Galeri Foto</h2>
      <div className="mt-4 grid h-[360px] gap-3 sm:grid-cols-[1.1fr_0.9fr_0.9fr] sm:grid-rows-2">
        {images.map((image, index) => (
          <div
            key={image}
            className={`relative overflow-hidden rounded-2xl ${
              index === 0 ? 'sm:row-span-2' : ''
            }`}
          >
            <Image
              src={image}
              alt={`Galeri destinasi ${index + 1}`}
              fill
              sizes="(min-width: 768px) 360px, 100vw"
              className="object-cover"
            />
          </div>
        ))}
      </div>
    </section>
  );
}
