import Image from 'next/image';
import type { DestinationDetail } from '@/types';

export function WeatherCard({ destination }: { destination: DestinationDetail }) {
  return (
    <section className="overflow-hidden rounded-2xl border border-[#D9E8F3] bg-white shadow-[0_12px_28px_rgba(15,23,42,0.06)]">
      <div className="relative h-36">
        <Image
          src={destination.gallery[1] ?? destination.image}
          alt="Cuaca destinasi"
          fill
          sizes="320px"
          className="object-cover"
        />
        <div className="absolute inset-0 bg-[linear-gradient(180deg,rgba(13,93,145,0.12)_0%,rgba(13,93,145,0.76)_100%)]" />
        <div className="absolute inset-x-0 bottom-0 p-4 text-white">
          <p className="text-sm font-semibold">Cuaca</p>
          <div className="mt-1 flex items-end justify-between">
            <p className="text-[36px] font-semibold leading-none">
              {destination.weather.temperature}
            </p>
            <p className="text-sm font-medium">{destination.weather.condition}</p>
          </div>
        </div>
      </div>
      <p className="p-4 text-sm leading-6 text-slate-600">
        {destination.weather.note}
      </p>
    </section>
  );
}
