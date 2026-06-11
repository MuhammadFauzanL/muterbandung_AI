import Image from 'next/image';
import Link from 'next/link';

type PlannerDestination = {
  title: string;
  category: string;
  description: string;
  distance: string;
  duration: string;
  price: string;
  rating: string;
  image: string;
};

type SimilarDestination = {
  title: string;
  description: string;
  image: string;
};

const NEARBY_DESTINATIONS: readonly PlannerDestination[] = [
  {
    title: 'Situ Patenggang',
    category: 'Alam',
    description:
      'Danau legendaris dengan pemandangan kebun teh yang menyejukkan mata.',
    distance: '25m away',
    duration: '1-2 hours',
    price: 'Rp15.000',
    rating: '4.8',
    image:
      'https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?q=80&w=900&auto=format&fit=crop',
  },
  {
    title: 'Ranca Upas',
    category: 'Alam',
    description:
      'Area perkemahan rasa alam camping ground yang asri di tengah hutan pinus.',
    distance: '1.5km away',
    duration: '2-3 hours',
    price: 'Rp25.000',
    rating: '4.6',
    image: '/destinations/ranca-upas.svg',
  },
] as const;

const SIMILAR_DESTINATIONS: readonly SimilarDestination[] = [
  {
    title: 'Tangkuban Perahu',
    description: 'Kawah vulkanik ikonik di Bandung Utara.',
    image: '/destinations/kawah-putih.svg',
  },
  {
    title: 'Orchid Forest',
    description: 'Hutan pinus dengan koleksi anggrek langka.',
    image:
      'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?q=80&w=900&auto=format&fit=crop',
  },
] as const;

function PinIcon({ className = 'h-4 w-4' }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      className={className}
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

function ClockIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      className="h-3.5 w-3.5"
      fill="none"
      aria-hidden="true"
    >
      <circle cx="12" cy="12" r="8" stroke="currentColor" strokeWidth="1.8" />
      <path
        d="M12 7.8v4.7l3.2 1.9"
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
      className="h-3.5 w-3.5"
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

function BuildingIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      className="h-4 w-4"
      fill="none"
      aria-hidden="true"
    >
      <path
        d="M5 21V5.8C5 4.8 5.8 4 6.8 4h10.4c1 0 1.8.8 1.8 1.8V21M3.5 21h17"
        stroke="currentColor"
        strokeLinecap="round"
        strokeWidth="1.8"
      />
      <path
        d="M8.5 8h1.2M14.3 8h1.2M8.5 11.5h1.2M14.3 11.5h1.2M8.5 15h1.2M14.3 15h1.2"
        stroke="currentColor"
        strokeLinecap="round"
        strokeWidth="1.8"
      />
    </svg>
  );
}

function TravelIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      className="h-4 w-4"
      fill="none"
      aria-hidden="true"
    >
      <path
        d="M5.5 20h13M8 20l2.4-11.5M14 20l-2.4-11.5M7 8.5h10"
        stroke="currentColor"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth="1.8"
      />
      <path
        d="M8.5 8.5 12 4l3.5 4.5"
        stroke="currentColor"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth="1.8"
      />
    </svg>
  );
}

function CloseIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      className="h-4 w-4"
      fill="none"
      aria-hidden="true"
    >
      <path
        d="m7 7 10 10M17 7 7 17"
        stroke="currentColor"
        strokeLinecap="round"
        strokeWidth="1.8"
      />
    </svg>
  );
}

function SuccessBanner() {
  return (
    <section className="relative overflow-hidden rounded-[10px] border border-[#DCEBF3] bg-white px-5 py-4 shadow-[0_10px_24px_rgba(17,73,112,0.05)]">
      <div className="absolute left-0 top-4 h-12 w-1 rounded-r-full bg-[#129ED0]" />
      <div className="flex items-start gap-3 pr-8">
        <div className="relative mt-0.5 h-8 w-8 overflow-hidden rounded-full bg-[#EAF6FC]">
          <Image
            src="/destinations/kawah-putih.svg"
            alt=""
            fill
            loading="eager"
            sizes="32px"
            className="object-cover"
          />
        </div>
        <div>
          <h1 className="text-[14px] font-semibold leading-5 text-[#202B37]">
            Kawah Putih berhasil ditambahkan ke perjalananmu.
          </h1>
          <p className="mt-0.5 text-[12px] leading-5 text-[#6E7F8E]">
            Cepot AI menambahkan destinasi lain yang sering dikunjungi dalam
            satu perjalanan.
          </p>
        </div>
      </div>
      <button
        type="button"
        aria-label="Tutup notifikasi"
        className="absolute right-4 top-4 text-[#8C9BA8] transition-colors hover:text-[#445463]"
      >
        <CloseIcon />
      </button>
    </section>
  );
}

function InsightCard() {
  return (
    <section className="relative overflow-hidden rounded-[18px] border border-[#BFE8F0] bg-[#EAF8FB] px-6 py-5">
      <div className="relative z-10 flex items-start gap-4">
        <div className="relative h-12 w-12 shrink-0 overflow-hidden rounded-full bg-[#D8F0F6] ring-1 ring-white">
          <Image
            src="/images/welcome-cepot.png"
            alt="Cepot AI"
            fill
            sizes="48px"
            className="object-cover object-top"
          />
        </div>
        <div>
          <p className="text-[11px] font-bold uppercase tracking-normal text-[#137CA6]">
            Cepot AI Insight
          </p>
          <p className="mt-2 max-w-[640px] text-[15px] leading-7 text-[#26485C]">
            Insight dari Cepot AI: Wisatawan yang mengunjungi Kawah Putih
            biasanya juga mengunjungi Situ Patenggang dan Ranca Upas karena
            berada dalam satu kawasan wisata yang berdekatan.
          </p>
        </div>
      </div>
      <div className="absolute -right-8 bottom-0 h-28 w-28 rounded-full bg-white/35" />
      <div className="absolute bottom-7 right-8 h-11 w-11 rotate-45 rounded-[8px] border border-[#B8DDE7] bg-[#D9F0F6]" />
    </section>
  );
}

function DestinationRecommendationCard({
  destination,
}: {
  destination: PlannerDestination;
}) {
  return (
    <article className="grid overflow-hidden rounded-[12px] border border-[#DDEAF2] bg-white shadow-[0_8px_22px_rgba(17,73,112,0.05)] sm:grid-cols-[178px_minmax(0,1fr)]">
      <div className="relative min-h-[150px] sm:min-h-0">
        <Image
          src={destination.image}
          alt={destination.title}
          fill
          sizes="(min-width: 640px) 178px, 100vw"
          className="object-cover"
        />
        <span className="absolute left-3 top-3 rounded-full bg-white/92 px-2.5 py-1 text-[11px] font-semibold text-[#176E9E] shadow-sm">
          +{destination.rating}
        </span>
      </div>

      <div className="min-w-0 px-4 py-3.5">
        <div className="flex items-start justify-between gap-3">
          <div>
            <span className="rounded-full bg-[#EAF6FC] px-3 py-1 text-[11px] font-semibold text-[#2882A9]">
              {destination.category}
            </span>
            <h3 className="mt-2 text-[16px] font-semibold leading-6 text-[#202B37]">
              {destination.title}
            </h3>
          </div>
          <span className="shrink-0 text-right text-[11px] font-semibold text-[#0E75BC]">
            {destination.distance}
          </span>
        </div>

        <p className="mt-1.5 text-[12px] leading-5 text-[#6A7E8E]">
          {destination.description}
        </p>

        <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-[11px] text-[#80909D]">
            <span className="inline-flex items-center gap-1">
              <ClockIcon />
              {destination.duration}
            </span>
            <span className="inline-flex items-center gap-1">
              <WalletIcon />
              {destination.price}
            </span>
          </div>
          <button
            type="button"
            className="inline-flex h-8 items-center justify-center rounded-[8px] bg-[#0E75BC] px-4 text-[11px] font-semibold text-white transition-colors hover:bg-[#095f99]"
          >
            + Tambahkan ke Perjalanan
          </button>
        </div>
      </div>
    </article>
  );
}

function RecommendationList() {
  return (
    <section>
      <div className="mb-3 flex items-center gap-2 text-[#202B37]">
        <PinIcon className="h-4 w-4 text-[#0E75BC]" />
        <h2 className="text-[16px] font-semibold leading-6">
          Destinasi Sekitar yang Direkomendasikan
        </h2>
      </div>

      <div className="space-y-3">
        {NEARBY_DESTINATIONS.map((destination) => (
          <DestinationRecommendationCard
            key={destination.title}
            destination={destination}
          />
        ))}
      </div>
    </section>
  );
}

function SimilarDestinations() {
  return (
    <section>
      <div className="mb-3 flex items-center gap-2 text-[#202B37]">
        <span className="text-[#0E75BC]">
          <TravelIcon />
        </span>
        <h2 className="text-[16px] font-semibold leading-6">
          Wisata Serupa yang Mungkin Kamu Sukai
        </h2>
      </div>
      <div className="grid gap-4 sm:grid-cols-2">
        {SIMILAR_DESTINATIONS.map((destination, index) => (
          <article
            key={destination.title}
            className="overflow-hidden rounded-[12px] border border-[#DDEAF2] bg-white shadow-[0_8px_22px_rgba(17,73,112,0.05)]"
          >
            <div className="relative h-[154px]">
              <Image
                src={destination.image}
                alt={destination.title}
                fill
                loading={index === 0 ? 'eager' : 'lazy'}
                sizes="(min-width: 640px) 50vw, 100vw"
                className="object-cover"
              />
            </div>
            <div className="px-4 py-3">
              <h3 className="text-[14px] font-semibold text-[#202B37]">
                {destination.title}
              </h3>
              <p className="mt-1 text-[12px] leading-5 text-[#6A7E8E]">
                {destination.description}
              </p>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

function TripSummary() {
  return (
    <aside className="rounded-[16px] border border-[#DCEAF3] bg-white p-5 shadow-[0_10px_28px_rgba(17,73,112,0.07)]">
      <h2 className="text-[15px] font-semibold text-[#202B37]">
        Ringkasan Perjalanan
      </h2>

      <div className="mt-4 space-y-2.5">
        <div className="flex items-center gap-2 rounded-[10px] bg-[#EAF8FB] px-3 py-2.5 text-[12px] font-semibold text-[#246983]">
          <PinIcon className="h-4 w-4 text-[#0E75BC]" />
          Kawah Putih
        </div>
        <div className="flex items-center gap-2 rounded-[10px] border border-[#E3EEF4] bg-white px-3 py-2.5 text-[12px] text-[#97A5B1]">
          <PinIcon className="h-4 w-4" />
          Pilih destinasi selanjutnya...
        </div>
      </div>

      <dl className="mt-5 space-y-2.5 border-t border-[#EDF4F8] pt-4 text-[12px]">
        <div className="flex items-center justify-between gap-4">
          <dt className="text-[#7B8B99]">Destinasi Dipilih</dt>
          <dd className="font-semibold text-[#202B37]">1/5 Destinasi</dd>
        </div>
        <div className="flex items-center justify-between gap-4">
          <dt className="text-[#7B8B99]">Estimasi Durasi</dt>
          <dd className="font-semibold text-[#202B37]">2-3 Jam</dd>
        </div>
        <div className="flex items-center justify-between gap-4">
          <dt className="text-[#7B8B99]">Estimasi Biaya</dt>
          <dd className="font-semibold text-[#0E75BC]">Rp50.000</dd>
        </div>
      </dl>

      <div className="mt-5 space-y-3">
        <Link
          href="/planner/penginapan"
          className="inline-flex h-11 w-full items-center justify-center gap-2 rounded-[10px] bg-[#0E75BC] px-4 text-[13px] font-semibold text-white transition-colors hover:bg-[#095f99]"
        >
          <BuildingIcon />
          Lanjut Pilih Penginapan
        </Link>
        <Link
          href="/explore"
          className="inline-flex h-11 w-full items-center justify-center rounded-[10px] border border-[#0E75BC] bg-white px-4 text-[13px] font-semibold text-[#0E75BC] transition-colors hover:bg-[#F2FAFE]"
        >
          Cari Destinasi Lain
        </Link>
      </div>

      <div className="mt-5 flex gap-3 rounded-[12px] bg-[#F0F7FC] px-4 py-3">
        <div className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[#0E75BC] text-white">
          <PinIcon className="h-4 w-4" />
        </div>
        <p className="text-[12px] leading-5 text-[#557083]">
          Kamu bisa menghemat Rp25.000 jika mengunjungi destinasi yang
          searah.
        </p>
      </div>
    </aside>
  );
}

function PlannerChatPrompt() {
  return (
    <div className="hidden items-end justify-end gap-3 pr-8 lg:flex">
      <div className="rounded-[10px] bg-white px-4 py-3 text-[12px] leading-5 text-[#6A7E8E] shadow-[0_12px_30px_rgba(17,73,112,0.14)]">
        <p>Butuh bantuan menyusun Perjalanan?</p>
        <button
          type="button"
          className="mt-1 font-semibold text-[#0E75BC] hover:text-[#095f99]"
        >
          Tanya Cepot AI
        </button>
      </div>
      <div className="relative h-12 w-12 overflow-hidden rounded-full bg-[#DDF3F8] shadow-[0_10px_24px_rgba(17,73,112,0.18)]">
        <Image
          src="/images/welcome-cepot.png"
          alt="Cepot AI"
          fill
          sizes="48px"
          className="object-cover object-top"
        />
      </div>
    </div>
  );
}

export function PlannerPageContent() {
  return (
    <main className="mx-auto max-w-[1180px] px-4 py-6 sm:px-8">
      <SuccessBanner />

      <div className="mt-5 grid gap-5 lg:grid-cols-[minmax(0,1fr)_340px]">
        <div className="min-w-0 space-y-6">
          <InsightCard />
          <RecommendationList />
          <SimilarDestinations />
        </div>

        <div className="space-y-6">
          <TripSummary />
          <PlannerChatPrompt />
        </div>
      </div>
    </main>
  );
}
