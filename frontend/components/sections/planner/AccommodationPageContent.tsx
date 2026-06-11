import Image from 'next/image';
import Link from 'next/link';

type AccommodationOption = {
  name: string;
  type: string;
  location: string;
  distance: string;
  price: string;
  rating: string;
  reviewCount: string;
  description: string;
  image: string;
  highlights: readonly string[];
};

const ACCOMMODATIONS: readonly AccommodationOption[] = [
  {
    name: 'Bobocabin Ranca Upas',
    type: 'Cabin Alam',
    location: 'Ranca Upas, Ciwidey',
    distance: '2.4 km dari Kawah Putih',
    price: 'Rp520.000',
    rating: '4.8',
    reviewCount: '1.284 ulasan',
    description:
      'Cabin ringkas di area hutan pinus dengan akses cepat ke Ranca Upas dan jalur wisata Ciwidey.',
    image:
      'https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?q=80&w=900&auto=format&fit=crop',
    highlights: ['Dekat rute', 'View alam', 'Cocok pasangan'],
  },
  {
    name: 'Patuha Resort Ciwidey',
    type: 'Resort Keluarga',
    location: 'Sugihmukti, Pasirjambu',
    distance: '4.8 km dari Kawah Putih',
    price: 'Rp680.000',
    rating: '4.7',
    reviewCount: '842 ulasan',
    description:
      'Resort tenang dengan kamar keluarga, sarapan, dan area terbuka untuk istirahat setelah itinerary.',
    image:
      'https://images.unsplash.com/photo-1566073771259-6a8506099945?q=80&w=900&auto=format&fit=crop',
    highlights: ['Sarapan', 'Kamar keluarga', 'Parkir luas'],
  },
  {
    name: 'Grand Sunshine Resort',
    type: 'Hotel Resort',
    location: 'Soreang, Bandung',
    distance: '18 km dari Kawah Putih',
    price: 'Rp850.000',
    rating: '4.9',
    reviewCount: '2.310 ulasan',
    description:
      'Pilihan paling nyaman untuk keluarga, dengan fasilitas lengkap dan akses balik ke Bandung yang mudah.',
    image:
      'https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?q=80&w=900&auto=format&fit=crop',
    highlights: ['Kolam renang', 'Restoran', 'Akses kota'],
  },
] as const;

const FILTERS = ['Semua', 'Dekat Kawah Putih', 'Family stay', 'Cabin', 'Budget hemat'];

function ArrowLeftIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      className="h-4 w-4"
      fill="none"
      aria-hidden="true"
    >
      <path
        d="M19 12H5M11 18l-6-6 6-6"
        stroke="currentColor"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth="1.8"
      />
    </svg>
  );
}

function SearchIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      className="h-4 w-4"
      fill="none"
      aria-hidden="true"
    >
      <path
        d="M10.8 18.2a7.4 7.4 0 1 0 0-14.8 7.4 7.4 0 0 0 0 14.8ZM16 16l4.5 4.5"
        stroke="currentColor"
        strokeLinecap="round"
        strokeWidth="1.8"
      />
    </svg>
  );
}

function MapPinIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      className="h-4 w-4"
      fill="none"
      aria-hidden="true"
    >
      <path
        d="M12 21s7-5.2 7-11a7 7 0 1 0-14 0c0 5.8 7 11 7 11Z"
        stroke="currentColor"
        strokeWidth="1.8"
      />
      <circle cx="12" cy="10" r="2.4" stroke="currentColor" strokeWidth="1.8" />
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
      <path d="m12 3.7 2.4 4.9 5.4.8-3.9 3.8.9 5.4-4.8-2.5-4.8 2.5.9-5.4-3.9-3.8 5.4-.8L12 3.7Z" />
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
        d="M7 3.5v3M17 3.5v3M4.5 9.5h15M6.8 5h10.4A2.8 2.8 0 0 1 20 7.8v9.4a2.8 2.8 0 0 1-2.8 2.8H6.8A2.8 2.8 0 0 1 4 17.2V7.8A2.8 2.8 0 0 1 6.8 5Z"
        stroke="currentColor"
        strokeLinecap="round"
        strokeWidth="1.8"
      />
    </svg>
  );
}

function UsersIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      className="h-4 w-4"
      fill="none"
      aria-hidden="true"
    >
      <path
        d="M9.5 11a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7ZM3.8 20a5.8 5.8 0 0 1 11.4 0M16 11.5a3 3 0 0 0 .4-5.9M18.2 20a5.2 5.2 0 0 0-3-4.7"
        stroke="currentColor"
        strokeLinecap="round"
        strokeWidth="1.8"
      />
    </svg>
  );
}

function WalletIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      className="h-4 w-4"
      fill="none"
      aria-hidden="true"
    >
      <path
        d="M4.5 7.5h13.8a2.2 2.2 0 0 1 2.2 2.2v6.8a2.2 2.2 0 0 1-2.2 2.2H5.8a2.3 2.3 0 0 1-2.3-2.3V7.2a2 2 0 0 1 2-2h11"
        stroke="currentColor"
        strokeWidth="1.8"
      />
      <path
        d="M16.5 13h4"
        stroke="currentColor"
        strokeLinecap="round"
        strokeWidth="1.8"
      />
    </svg>
  );
}

function SparkIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      className="h-4 w-4"
      fill="none"
      aria-hidden="true"
    >
      <path
        d="M12 3.5 13.9 9l5.6 2-5.6 2-1.9 5.5-1.9-5.5-5.6-2 5.6-2L12 3.5ZM19 3.8l.7 2 2 .7-2 .7-.7 2-.7-2-2-.7 2-.7.7-2Z"
        stroke="currentColor"
        strokeLinejoin="round"
        strokeWidth="1.6"
      />
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
        d="m5 12.5 4.2 4.2L19 6.8"
        stroke="currentColor"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth="2"
      />
    </svg>
  );
}

function PlannerProgress() {
  const steps = ['Destinasi', 'Penginapan', 'Transport'];

  return (
    <div className="grid gap-2 rounded-[14px] border border-[#DDEAF2] bg-white p-2 shadow-[0_10px_24px_rgba(17,73,112,0.05)] sm:grid-cols-3">
      {steps.map((step, index) => (
        <div
          key={step}
          className={`flex items-center gap-2 rounded-[10px] px-3 py-2.5 text-[12px] font-semibold ${
            index === 1
              ? 'bg-[#0E75BC] text-white'
              : index === 0
                ? 'bg-[#EAF8FB] text-[#246983]'
                : 'bg-[#F6FAFD] text-[#8A9AA7]'
          }`}
        >
          <span
            className={`inline-flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-[11px] ${
              index === 1
                ? 'bg-white text-[#0E75BC]'
                : index === 0
                  ? 'bg-[#0E75BC] text-white'
                  : 'bg-white text-[#8A9AA7]'
            }`}
          >
            {index === 0 ? <CheckIcon /> : index + 1}
          </span>
          {step}
        </div>
      ))}
    </div>
  );
}

function AccommodationFilters() {
  return (
    <section className="rounded-[16px] border border-[#DCEAF3] bg-white p-4 shadow-[0_10px_26px_rgba(17,73,112,0.06)]">
      <div className="grid gap-3 md:grid-cols-[minmax(0,1fr)_150px_132px_140px]">
        <label className="flex h-11 items-center gap-2 rounded-[10px] border border-[#DDEAF2] bg-[#F8FBFE] px-3 text-[#748694]">
          <SearchIcon />
          <span className="sr-only">Cari penginapan</span>
          <input
            type="search"
            placeholder="Cari area atau nama penginapan"
            className="min-w-0 flex-1 bg-transparent text-[13px] text-[#202B37] outline-none placeholder:text-[#96A5B0]"
          />
        </label>
        <button
          type="button"
          className="inline-flex h-11 items-center justify-center gap-2 rounded-[10px] border border-[#DDEAF2] bg-white px-3 text-[12px] font-semibold text-[#405A6D]"
        >
          <CalendarIcon />
          12 Jun
        </button>
        <button
          type="button"
          className="inline-flex h-11 items-center justify-center gap-2 rounded-[10px] border border-[#DDEAF2] bg-white px-3 text-[12px] font-semibold text-[#405A6D]"
        >
          <UsersIcon />
          2 Tamu
        </button>
        <button
          type="button"
          className="inline-flex h-11 items-center justify-center gap-2 rounded-[10px] bg-[#0E75BC] px-3 text-[12px] font-semibold text-white transition-colors hover:bg-[#095f99]"
        >
          Terapkan
        </button>
      </div>

      <div className="mt-3 flex flex-wrap gap-2">
        {FILTERS.map((filter, index) => (
          <button
            key={filter}
            type="button"
            className={`rounded-full border px-3.5 py-2 text-[12px] font-semibold transition-colors ${
              index === 0
                ? 'border-[#0E75BC] bg-[#EAF6FC] text-[#0E75BC]'
                : 'border-[#DDEAF2] bg-white text-[#6A7E8E] hover:border-[#0E75BC] hover:text-[#0E75BC]'
            }`}
          >
            {filter}
          </button>
        ))}
      </div>
    </section>
  );
}

function AccommodationCard({
  accommodation,
  eagerImage = false,
}: {
  accommodation: AccommodationOption;
  eagerImage?: boolean;
}) {
  return (
    <article className="grid overflow-hidden rounded-[14px] border border-[#DDEAF2] bg-white shadow-[0_10px_26px_rgba(17,73,112,0.06)] md:grid-cols-[220px_minmax(0,1fr)]">
      <div className="relative min-h-[190px]">
        <Image
          src={accommodation.image}
          alt={accommodation.name}
          fill
          loading={eagerImage ? 'eager' : 'lazy'}
          sizes="(min-width: 768px) 220px, 100vw"
          className="object-cover"
        />
        <span className="absolute left-3 top-3 rounded-full bg-white/92 px-3 py-1 text-[11px] font-semibold text-[#176E9E] shadow-sm">
          {accommodation.type}
        </span>
      </div>

      <div className="min-w-0 p-4">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
          <div className="min-w-0">
            <h2 className="text-[17px] font-semibold leading-6 text-[#202B37]">
              {accommodation.name}
            </h2>
            <div className="mt-1.5 flex flex-wrap items-center gap-x-3 gap-y-1 text-[12px] text-[#6A7E8E]">
              <span className="inline-flex items-center gap-1">
                <MapPinIcon />
                {accommodation.location}
              </span>
              <span>{accommodation.distance}</span>
            </div>
          </div>

          <div className="shrink-0 rounded-[10px] bg-[#FFF7E8] px-3 py-2 text-[#7C4F00]">
            <div className="flex items-center gap-1 text-[12px] font-bold">
              <StarIcon />
              {accommodation.rating}
            </div>
            <p className="mt-0.5 text-[10px] font-semibold text-[#9B7840]">
              {accommodation.reviewCount}
            </p>
          </div>
        </div>

        <p className="mt-3 text-[13px] leading-6 text-[#607382]">
          {accommodation.description}
        </p>

        <div className="mt-4 flex flex-wrap gap-2">
          {accommodation.highlights.map((highlight) => (
            <span
              key={highlight}
              className="rounded-full bg-[#EEF7FD] px-3 py-1.5 text-[11px] font-semibold text-[#23689A]"
            >
              {highlight}
            </span>
          ))}
        </div>

        <div className="mt-5 flex flex-col gap-3 border-t border-[#EDF4F8] pt-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-[11px] font-medium text-[#80909D]">Mulai dari</p>
            <p className="text-[18px] font-bold text-[#202B37]">
              {accommodation.price}
              <span className="text-[11px] font-semibold text-[#7B8B99]">
                {' '}
                / malam
              </span>
            </p>
          </div>
          <button
            type="button"
            className="inline-flex h-10 items-center justify-center rounded-[10px] bg-[#0E75BC] px-5 text-[12px] font-semibold text-white transition-colors hover:bg-[#095f99]"
          >
            Pilih Penginapan
          </button>
        </div>
      </div>
    </article>
  );
}

function CepotInsight() {
  return (
    <section className="relative overflow-hidden rounded-[18px] border border-[#BFE8F0] bg-[#EAF8FB] px-5 py-4">
      <div className="relative z-10 flex items-start gap-3">
        <div className="relative h-11 w-11 shrink-0 overflow-hidden rounded-full bg-[#D8F0F6] ring-1 ring-white">
          <Image
            src="/images/welcome-cepot.png"
            alt="Cepot AI"
            fill
            sizes="44px"
            className="object-cover object-top"
          />
        </div>
        <div>
          <p className="flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-normal text-[#137CA6]">
            <SparkIcon />
            Cepot AI Insight
          </p>
          <p className="mt-1.5 text-[13px] leading-6 text-[#26485C]">
            Untuk rute Kawah Putih dan Ranca Upas, menginap di area Ciwidey
            membuat perjalanan pagi lebih ringan dan menghemat waktu tempuh
            sekitar 35 menit.
          </p>
        </div>
      </div>
      <div className="absolute -right-8 bottom-0 h-24 w-24 rounded-full bg-white/35" />
    </section>
  );
}

function TripSidebar() {
  return (
    <aside className="rounded-[16px] border border-[#DCEAF3] bg-white p-5 shadow-[0_10px_28px_rgba(17,73,112,0.07)]">
      <h2 className="text-[15px] font-semibold text-[#202B37]">
        Ringkasan Perjalanan
      </h2>

      <div className="mt-4 space-y-2.5">
        <div className="flex items-center gap-2 rounded-[10px] bg-[#EAF8FB] px-3 py-2.5 text-[12px] font-semibold text-[#246983]">
          <MapPinIcon />
          Kawah Putih
        </div>
        <div className="flex items-center gap-2 rounded-[10px] bg-[#EAF8FB] px-3 py-2.5 text-[12px] font-semibold text-[#246983]">
          <MapPinIcon />
          Ranca Upas
        </div>
        <div className="flex items-center gap-2 rounded-[10px] border border-[#E3EEF4] bg-white px-3 py-2.5 text-[12px] text-[#97A5B1]">
          <WalletIcon />
          Pilih penginapan...
        </div>
      </div>

      <dl className="mt-5 space-y-2.5 border-t border-[#EDF4F8] pt-4 text-[12px]">
        <div className="flex items-center justify-between gap-4">
          <dt className="text-[#7B8B99]">Tanggal Check-in</dt>
          <dd className="font-semibold text-[#202B37]">12 Jun 2026</dd>
        </div>
        <div className="flex items-center justify-between gap-4">
          <dt className="text-[#7B8B99]">Durasi Menginap</dt>
          <dd className="font-semibold text-[#202B37]">1 Malam</dd>
        </div>
        <div className="flex items-center justify-between gap-4">
          <dt className="text-[#7B8B99]">Budget Penginapan</dt>
          <dd className="font-semibold text-[#0E75BC]">Rp500rb - Rp900rb</dd>
        </div>
      </dl>

      <div className="mt-5 rounded-[12px] bg-[#F7FBF5] px-4 py-3 text-[12px] leading-5 text-[#4F7044]">
        Opsi paling efisien saat ini adalah Bobocabin Ranca Upas karena dekat
        dengan destinasi lanjutan dan masuk rentang budget.
      </div>

      <div className="mt-5 space-y-3">
        <button
          type="button"
          className="inline-flex h-11 w-full items-center justify-center rounded-[10px] bg-[#0E75BC] px-4 text-[13px] font-semibold text-white transition-colors hover:bg-[#095f99]"
        >
          Simpan Pilihan
        </button>
        <Link
          href="/planner"
          className="inline-flex h-11 w-full items-center justify-center rounded-[10px] border border-[#0E75BC] bg-white px-4 text-[13px] font-semibold text-[#0E75BC] transition-colors hover:bg-[#F2FAFE]"
        >
          Kembali ke Planner
        </Link>
      </div>
    </aside>
  );
}

export function AccommodationPageContent() {
  return (
    <main className="mx-auto max-w-[1180px] px-4 py-6 sm:px-8">
      <div className="mb-5 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <Link
            href="/planner"
            className="inline-flex items-center gap-2 text-[13px] font-semibold text-[#0E75BC] hover:text-[#095f99]"
          >
            <ArrowLeftIcon />
            Kembali ke itinerary
          </Link>
          <h1 className="mt-4 text-[28px] font-semibold leading-tight text-[#202B37] sm:text-[34px]">
            Pilih Penginapan
          </h1>
          <p className="mt-2 max-w-2xl text-[14px] leading-6 text-[#657786]">
            Rekomendasi penginapan disusun dari jarak ke destinasi, budget,
            dan ritme perjalanan yang sudah kamu pilih.
          </p>
        </div>

        <div className="w-full lg:max-w-[460px]">
          <PlannerProgress />
        </div>
      </div>

      <div className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_340px]">
        <div className="min-w-0 space-y-5">
          <AccommodationFilters />
          <CepotInsight />

          <section>
            <div className="mb-3 flex flex-col gap-1 sm:flex-row sm:items-end sm:justify-between">
              <div>
                <h2 className="text-[17px] font-semibold text-[#202B37]">
                  Rekomendasi Terbaik
                </h2>
                <p className="text-[12px] leading-5 text-[#7B8B99]">
                  3 penginapan cocok untuk itinerary Ciwidey.
                </p>
              </div>
              <button
                type="button"
                className="self-start rounded-full border border-[#DDEAF2] bg-white px-3 py-1.5 text-[12px] font-semibold text-[#23689A] transition-colors hover:border-[#0E75BC] hover:text-[#0E75BC] sm:self-auto"
              >
                Urutkan: Rekomendasi AI
              </button>
            </div>

            <div className="space-y-3">
              {ACCOMMODATIONS.map((accommodation, index) => (
                <AccommodationCard
                  key={accommodation.name}
                  accommodation={accommodation}
                  eagerImage={index === 0}
                />
              ))}
            </div>
          </section>
        </div>

        <div className="lg:sticky lg:top-6 lg:self-start">
          <TripSidebar />
        </div>
      </div>
    </main>
  );
}
