"use client";

import Image from 'next/image';
import Link from 'next/link';
import { usePlanner } from '@/context/PlannerContext';
import { useToast } from '@/context/ToastContext';
import { MapPin as PinIcon, Clock as ClockIcon, Wallet as WalletIcon, Building as BuildingIcon, Compass as TravelIcon, X as CloseIcon } from 'lucide-react';

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

type NearbyHotel = {
  name: string;
  type: string;
  distance: string;
  price: string;
  rating: string;
  image: string;
};

const NEARBY_HOTELS: readonly NearbyHotel[] = [
  {
    name: 'Bobocabin Ranca Upas',
    type: 'Cabin Alam',
    distance: '2.4 km dari Kawah Putih',
    price: 'Rp520.000',
    rating: '4.8',
    image: 'https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?q=80&w=900&auto=format&fit=crop',
  },
  {
    name: 'Patuha Resort Ciwidey',
    type: 'Resort Keluarga',
    distance: '4.8 km dari Kawah Putih',
    price: 'Rp680.000',
    rating: '4.7',
    image: 'https://images.unsplash.com/photo-1566073771259-6a8506099945?q=80&w=900&auto=format&fit=crop',
  },
] as const;



function NearbyHotels() {
  return (
    <section>
      <div className="mb-3 flex items-center gap-2 text-[#202B37]">
        <span className="text-[#0E75BC]">
          <BuildingIcon />
        </span>
        <h2 className="text-[16px] font-semibold leading-6">
          Penginapan Terdekat
        </h2>
      </div>
      <div className="space-y-3">
        {NEARBY_HOTELS.map((hotel) => (
          <article key={hotel.name} className="flex gap-4 rounded-[12px] border border-[#DDEAF2] bg-white p-3 shadow-[0_8px_22px_rgba(17,73,112,0.05)]">
            <div className="relative h-[100px] w-[140px] shrink-0 overflow-hidden rounded-[8px]">
              <Image src={hotel.image} alt={hotel.name} fill className="object-cover" sizes="140px" />
            </div>
            <div className="flex min-w-0 flex-1 flex-col justify-between py-1">
              <div>
                <h3 className="text-[14px] font-semibold text-[#202B37] truncate">{hotel.name}</h3>
                <p className="text-[12px] text-[#6A7E8E]">{hotel.distance}</p>
              </div>
              <div className="flex items-center justify-between mt-2">
                <div>
                  <p className="text-[10px] text-[#80909D]">Mulai dari</p>
                  <p className="text-[14px] font-bold text-[#0E75BC]">{hotel.price}</p>
                </div>
                <Link
                  href="/planner/penginapan"
                  className="rounded-[8px] bg-[#EAF6FC] px-3 py-1.5 text-[11px] font-semibold text-[#0E75BC] transition-colors hover:bg-[#DDEAF2]"
                >
                  Lihat Detail
                </Link>
              </div>
            </div>
          </article>
        ))}
      </div>
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
  const { addDestination } = usePlanner();
  const { showToast } = useToast();

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
            onClick={() => {
              addDestination({ id: destination.title, title: destination.title });
              showToast(`${destination.title} berhasil ditambahkan ke perjalanan!`, 'success');
            }}
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
  const { destinations, accommodations, removeDestination, removeAccommodation } = usePlanner();

  // Hitung jumlah destinasi (maksimal per hari misal 5)
  const destCount = destinations.length;
  // Hitung estimasi harga
  const totalAccommodationCost = accommodations.reduce((sum, acc) => sum + acc.totalPrice, 0);
  const totalCost = (destCount * 25000) + totalAccommodationCost;

  return (
    <aside className="rounded-[16px] border border-[#DCEAF3] bg-white p-5 shadow-[0_10px_28px_rgba(17,73,112,0.07)]">
      <h2 className="text-[15px] font-semibold text-[#202B37]">
        Ringkasan Perjalanan
      </h2>

      <div className="mt-4 space-y-2.5">
        {destinations.map((dest) => (
          <div key={dest.id} className="flex items-center gap-2 rounded-[10px] bg-[#EAF8FB] px-3 py-2.5 text-[12px] font-semibold text-[#246983]">
            <PinIcon className="h-4 w-4 text-[#0E75BC]" />
            <span className="flex-1">{dest.title}</span>
            <button onClick={() => removeDestination(dest.id)} className="text-red-400 hover:text-red-600">
              <CloseIcon />
            </button>
          </div>
        ))}
        {destinations.length === 0 && (
          <div className="flex items-center gap-2 rounded-[10px] border border-[#E3EEF4] bg-white px-3 py-2.5 text-[12px] text-[#97A5B1]">
            <PinIcon className="h-4 w-4" />
            <span className="flex-1">Pilih destinasi...</span>
          </div>
        )}

        {accommodations.length > 0 ? (
          accommodations.map((acc) => (
            <div key={acc.name} className="flex items-center gap-2 rounded-[10px] bg-[#EAF8FB] px-3 py-2.5 text-[12px] font-semibold text-[#246983]">
              <BuildingIcon />
              <span className="flex-1">{acc.name}</span>
              <button onClick={() => removeAccommodation(acc.name)} className="text-red-400 hover:text-red-600">
                <CloseIcon />
              </button>
            </div>
          ))
        ) : (
          <div className="flex items-center gap-2 rounded-[10px] border border-[#E3EEF4] bg-white px-3 py-2.5 text-[12px] text-[#97A5B1]">
            <BuildingIcon />
            <span className="flex-1">Pilih penginapan...</span>
          </div>
        )}
      </div>

      <dl className="mt-5 space-y-2.5 border-t border-[#EDF4F8] pt-4 text-[12px]">
        <div className="flex items-center justify-between gap-4">
          <dt className="text-[#7B8B99]">Destinasi Dipilih</dt>
          <dd className="font-semibold text-[#202B37]">{destCount}/5 Destinasi</dd>
        </div>
        {accommodations.length > 0 && (
          <div className="flex items-center justify-between gap-4">
            <dt className="text-[#7B8B99]">Penginapan Dipilih</dt>
            <dd className="font-semibold text-[#202B37]">{accommodations.length} Hotel</dd>
          </div>
        )}
        <div className="flex items-center justify-between gap-4">
          <dt className="text-[#7B8B99]">Estimasi Biaya</dt>
          <dd className="font-semibold text-[#0E75BC]">Rp{totalCost.toLocaleString('id-ID')}</dd>
        </div>
      </dl>

      <div className="mt-5 space-y-3">
        {accommodations.length === 0 ? (
          <Link
            href="/planner/penginapan"
            className="inline-flex h-11 w-full items-center justify-center gap-2 rounded-[10px] bg-[#0E75BC] px-4 text-[13px] font-semibold text-white transition-colors hover:bg-[#095f99]"
          >
            Lanjut Pilih Penginapan
          </Link>
        ) : (
          <Link
            href="/planner/penginapan"
            className="inline-flex h-11 w-full items-center justify-center gap-2 rounded-[10px] border border-[#0E75BC] bg-white px-4 text-[13px] font-semibold text-[#0E75BC] transition-colors hover:bg-[#F2FAFE]"
          >
            Pilih Penginapan Lain
          </Link>
        )}
        <Link
          href="/explore"
          className="inline-flex h-11 w-full items-center justify-center rounded-[10px] border border-[#0E75BC] bg-white px-4 text-[13px] font-semibold text-[#0E75BC] transition-colors hover:bg-[#F2FAFE]"
        >
          Cari Destinasi Lain
        </Link>
        {accommodations.length > 0 || destinations.length > 0 ? (
          <Link
            href="/planner/itinerary"
            className="inline-flex h-11 w-full items-center justify-center gap-2 rounded-[10px] bg-[#E54545] px-4 text-[13px] font-semibold text-white transition-colors hover:bg-[#d43b3b] shadow-md"
          >
            Buat Itinerary Saya
          </Link>
        ) : (
          <button
            disabled
            type="button"
            className="inline-flex h-11 w-full items-center justify-center gap-2 rounded-[10px] bg-slate-200 px-4 text-[13px] font-semibold text-slate-400 cursor-not-allowed"
          >
            Buat Itinerary Saya
          </button>
        )}
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
          onClick={() => window.dispatchEvent(new Event('open-chat'))}
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
      <div className="mt-5 grid gap-5 lg:grid-cols-[minmax(0,1fr)_340px]">
        <div className="min-w-0 space-y-6">
          <InsightCard />
          <RecommendationList />
          <NearbyHotels />
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
