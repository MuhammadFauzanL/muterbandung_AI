/**
 * Popular Destinations Section Component
 *
 * Displays a grid of popular tourist destinations in Bandung.
 * Uses DestinationCard for each destination item.
 */
import { POPULAR_DESTINATIONS } from '@/constants';
import { DestinationCard } from '@/components/ui/cards';

export function PopularDestinationsSection() {
  return (
    <section id="explore" className="bg-[#F8FBFE] py-14 sm:py-16">
      <div className="mx-auto max-w-[1180px] px-5 sm:px-8">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <h2 className="text-[28px] font-semibold tracking-normal text-slate-950">
              Destinasi Populer Bandung
            </h2>
            <p className="mt-1 text-[18px] text-slate-600">
              Tempat populer wisatawan yang sering dikunjungi.
            </p>
          </div>

          <a
            href="#"
            className="inline-flex items-center gap-2 self-start pt-1 text-[18px] font-medium text-[#0E75BC] hover:text-[#095f99]"
          >
            Lihat Semua
            <span className="text-xl leading-none">→</span>
          </a>
        </div>

        <div className="mt-8 grid gap-6 md:grid-cols-2 xl:grid-cols-3">
          {POPULAR_DESTINATIONS.map((destination) => (
            <DestinationCard key={destination.title} {...destination} />
          ))}
        </div>
      </div>
    </section>
  );
}
