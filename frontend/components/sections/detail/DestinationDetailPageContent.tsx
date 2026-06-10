import Image from 'next/image';
import Link from 'next/link';
import { LocationIcon } from '@/components/ui/icons';
import type { DestinationDetail, DetailMetric } from '@/types';

function BackIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      className="h-4 w-4"
      fill="none"
      aria-hidden="true"
    >
      <path
        d="M15 18 9 12l6-6"
        stroke="currentColor"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth="2"
      />
    </svg>
  );
}

function CalendarIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      className="h-4 w-4"
      fill="none"
      aria-hidden="true"
    >
      <path
        d="M7 3v4M17 3v4M4.5 9h15M6 5h12a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2Z"
        stroke="currentColor"
        strokeLinecap="round"
        strokeWidth="1.8"
      />
    </svg>
  );
}

function StarIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      className="h-4 w-4"
      fill="currentColor"
      aria-hidden="true"
    >
      <path d="m12 3.7 2.42 4.9 5.4.79-3.91 3.81.92 5.38L12 16.04l-4.83 2.54.92-5.38-3.91-3.81 5.4-.79L12 3.7Z" />
    </svg>
  );
}

function CheckIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      className="h-4 w-4"
      fill="none"
      aria-hidden="true"
    >
      <path
        d="m5 12.5 4.2 4.2L19 7"
        stroke="currentColor"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth="2"
      />
    </svg>
  );
}

function metricIcon(tone: DetailMetric['tone']) {
  if (tone === 'price') {
    return <span className="text-[18px] font-bold leading-none">Rp</span>;
  }

  if (tone === 'rating') {
    return <StarIcon />;
  }

  return <CalendarIcon />;
}

function DetailHero({ destination }: { destination: DestinationDetail }) {
  return (
    <section className="relative overflow-hidden rounded-[18px] bg-slate-900">
      <div className="relative h-[360px] sm:h-[430px]">
        <Image
          src={destination.heroImage}
          alt={destination.title}
          fill
          preload
          sizes="(min-width: 1180px) 1180px, 100vw"
          className="object-cover object-[center_58%] sm:object-center"
        />
        <div className="absolute inset-0 bg-[linear-gradient(180deg,rgba(15,23,42,0.06)_0%,rgba(15,23,42,0.2)_42%,rgba(15,23,42,0.78)_100%)]" />
      </div>

      <div className="absolute inset-x-0 bottom-0 px-5 pb-20 text-white sm:px-8">
        <Link
          href="/explore"
          className="mb-7 inline-flex items-center gap-2 rounded-full bg-white/92 px-4 py-2 text-sm font-semibold text-[#0E75BC] shadow-sm transition-colors hover:bg-white"
        >
          <BackIcon />
          Kembali
        </Link>
        <p className="text-sm font-semibold uppercase tracking-[0.22em] text-[#D8EFFB]">
          {destination.category}
        </p>
        <h1 className="mt-3 max-w-[620px] text-[40px] font-semibold leading-[1.05] sm:text-[54px]">
          {destination.title}
        </h1>
        <div className="mt-4 flex items-center gap-2 text-sm font-medium text-white/88">
          <LocationIcon className="h-4 w-4 text-white" />
          <span>{destination.location}</span>
        </div>
      </div>
    </section>
  );
}

function MetricBar({ metrics }: { metrics: DestinationDetail['metrics'] }) {
  return (
    <section className="relative z-10 mx-4 -mt-12 grid gap-3 rounded-2xl border border-[#D9E8F3] bg-white p-3 shadow-[0_18px_40px_rgba(15,23,42,0.14)] sm:mx-8 sm:grid-cols-3">
      {metrics.map((metric) => (
        <div
          key={metric.label}
          className="flex items-center gap-3 rounded-xl bg-[#F8FBFE] px-4 py-3"
        >
          <div className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-[#EAF6FC] text-[#0E75BC]">
            {metricIcon(metric.tone)}
          </div>
          <div>
            <p className="text-xs font-medium uppercase text-slate-500">
              {metric.label}
            </p>
            <p className="mt-1 text-sm font-semibold text-slate-950">
              {metric.value}
            </p>
          </div>
        </div>
      ))}
    </section>
  );
}

function AiReason({ destination }: { destination: DestinationDetail }) {
  return (
    <section className="rounded-2xl border border-[#CFE5F2] bg-[#EAF6FC] p-5">
      <p className="text-sm font-semibold text-[#0E75BC]">
        Kenapa Cepot AI Merekomendasikan Ini?
      </p>
      <p className="mt-2 text-sm leading-7 text-[#426F87]">
        {destination.aiReason}
      </p>
    </section>
  );
}

function DestinationStory({ destination }: { destination: DestinationDetail }) {
  return (
    <section className="rounded-2xl border border-[#D9E8F3] bg-white p-5 shadow-[0_12px_28px_rgba(15,23,42,0.05)]">
      <h2 className="text-[22px] font-semibold text-slate-950">
        Tentang Destinasi
      </h2>
      <p className="mt-3 text-sm leading-7 text-slate-600">
        {destination.description}
      </p>
    </section>
  );
}

function Gallery({ images }: { images: DestinationDetail['gallery'] }) {
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

function Facilities({ facilities }: { facilities: DestinationDetail['facilities'] }) {
  return (
    <section className="rounded-2xl border border-[#D9E8F3] bg-white p-5 shadow-[0_12px_28px_rgba(15,23,42,0.05)]">
      <h2 className="text-[22px] font-semibold text-slate-950">Fasilitas</h2>
      <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {facilities.map((facility) => (
          <div
            key={facility}
            className="flex items-center gap-3 rounded-xl border border-[#E1EEF6] bg-[#F8FBFE] px-4 py-3 text-sm font-semibold text-slate-700"
          >
            <span className="inline-flex h-7 w-7 items-center justify-center rounded-full bg-[#EAF6FC] text-[#0E75BC]">
              <CheckIcon />
            </span>
            {facility}
          </div>
        ))}
      </div>
    </section>
  );
}

function Reviews({ reviews }: { reviews: DestinationDetail['reviews'] }) {
  return (
    <section className="rounded-2xl border border-[#D9E8F3] bg-white p-5 shadow-[0_12px_28px_rgba(15,23,42,0.05)]">
      <div className="flex items-center justify-between gap-4">
        <h2 className="text-[22px] font-semibold text-slate-950">
          Ulasan Pengunjung
        </h2>
        <a
          href="#reviews"
          className="text-sm font-semibold text-[#0E75BC] hover:text-[#095f99]"
        >
          Lihat Semua
        </a>
      </div>
      <div id="reviews" className="mt-4 grid gap-3 md:grid-cols-3">
        {reviews.map((review) => (
          <article
            key={review.name}
            className="rounded-2xl border border-[#E1EEF6] bg-[#F8FBFE] p-4"
          >
            <div className="flex items-center justify-between gap-3">
              <div>
                <h3 className="text-sm font-semibold text-slate-950">
                  {review.name}
                </h3>
                <p className="text-xs text-slate-500">{review.role}</p>
              </div>
              <span className="inline-flex items-center gap-1 rounded-full bg-[#FFF3E2] px-2.5 py-1 text-xs font-semibold text-[#A96916]">
                <StarIcon />
                {review.rating}
              </span>
            </div>
            <p className="mt-3 text-sm leading-6 text-slate-600">
              {review.comment}
            </p>
          </article>
        ))}
      </div>
    </section>
  );
}

function WeatherCard({ destination }: { destination: DestinationDetail }) {
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

function NearbyStays({ destination }: { destination: DestinationDetail }) {
  return (
    <section className="rounded-2xl border border-[#D9E8F3] bg-white p-5 shadow-[0_12px_28px_rgba(15,23,42,0.06)]">
      <div className="flex items-center justify-between gap-3">
        <h2 className="text-lg font-semibold text-slate-950">
          Penginapan Terdekat
        </h2>
        <a
          href="#hotels"
          className="text-sm font-semibold text-[#0E75BC] hover:text-[#095f99]"
        >
          Lihat
        </a>
      </div>
      <div id="hotels" className="mt-4 space-y-3">
        {destination.nearbyStays.map((stay) => (
          <article
            key={stay.name}
            className="grid grid-cols-[86px_minmax(0,1fr)] gap-3 rounded-2xl border border-[#E1EEF6] bg-[#F8FBFE] p-2.5"
          >
            <div className="relative h-20 overflow-hidden rounded-xl">
              <Image
                src={stay.image}
                alt={stay.name}
                fill
                sizes="86px"
                className="object-cover"
              />
            </div>
            <div className="min-w-0 py-1">
              <h3 className="truncate text-sm font-semibold text-slate-950">
                {stay.name}
              </h3>
              <p className="mt-1 text-xs text-slate-500">{stay.location}</p>
              <p className="mt-2 text-xs font-semibold text-[#E54545]">
                {stay.price}
              </p>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

function PlanCard({ destination }: { destination: DestinationDetail }) {
  return (
    <section className="rounded-2xl border border-[#CFE5F2] bg-[#EAF6FC] p-5">
      <h2 className="text-lg font-semibold text-slate-950">
        Rencana Cepat Cepot AI
      </h2>
      <ol className="mt-4 space-y-3 text-sm text-slate-600">
        <li className="rounded-xl bg-white px-4 py-3">
          08.00 - Berangkat menuju {destination.location}
        </li>
        <li className="rounded-xl bg-white px-4 py-3">
          10.00 - Eksplor area utama dan galeri foto
        </li>
        <li className="rounded-xl bg-white px-4 py-3">
          12.30 - Istirahat dan lanjut ke destinasi sekitar
        </li>
      </ol>
    </section>
  );
}

function BottomActions({ destination }: { destination: DestinationDetail }) {
  return (
    <section className="mt-8 rounded-2xl border border-[#D9E8F3] bg-white p-3 shadow-[0_18px_40px_rgba(15,23,42,0.12)]">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-end sm:pr-16">
        <button
          type="button"
          className="inline-flex items-center justify-center rounded-xl border border-[#0E75BC] px-5 py-3 text-sm font-semibold text-[#0E75BC] transition-colors hover:bg-[#EEF7FD]"
        >
          Tambahkan ke Perjalanan
        </button>
        <button
          type="button"
          className="inline-flex items-center justify-center rounded-xl bg-[#E54545] px-5 py-3 text-sm font-semibold text-white transition-colors hover:bg-[#CF3B3B]"
        >
          Pesan {destination.title}
        </button>
      </div>
    </section>
  );
}

export function DestinationDetailPageContent({
  destination,
}: {
  destination: DestinationDetail;
}) {
  return (
    <main className="mx-auto max-w-[1180px] px-4 py-6 sm:px-8">
      <DetailHero destination={destination} />
      <MetricBar metrics={destination.metrics} />

      <div className="mt-6 grid gap-6 lg:grid-cols-[minmax(0,1fr)_320px]">
        <div className="space-y-6">
          <AiReason destination={destination} />
          <DestinationStory destination={destination} />
          <Gallery images={destination.gallery} />
          <Facilities facilities={destination.facilities} />
          <Reviews reviews={destination.reviews} />
        </div>

        <aside className="space-y-6 lg:sticky lg:top-6 lg:self-start">
          <WeatherCard destination={destination} />
          <NearbyStays destination={destination} />
          <PlanCard destination={destination} />
        </aside>
      </div>

      <BottomActions destination={destination} />
    </main>
  );
}
