"use client";

import Image from 'next/image';
import Link from 'next/link';
import { Building as BuildingIcon } from 'lucide-react';

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
    image: 'https://lh3.googleusercontent.com/gps-proxy/ALd4DhFQNQ81Dicl74zu40V7aXYY50dw0TH-lPCwm_rFUokItvPcAB2TR0TclWJS-39WNWfCJ_04IFMGsytAfz0mjmiv_2ft5DRYmyE0tyFhO6Q8WM81wJqxKvqNiKtB-0VBqYxss31T3exO_FUzUlc3d9J0f-idvXZvvVAfRhO6qZKDrOa9ali32Kou7Q=w455-h240-k-no',
  },
  {
    name: 'Patuha Resort Ciwidey',
    type: 'Resort Keluarga',
    distance: '4.8 km dari Kawah Putih',
    price: 'Rp680.000',
    rating: '4.7',
    image: 'https://lh3.googleusercontent.com/gps-cs-s/APNQkAEINPwRItiBa-w5a0baJmuuVumrV1ITN9jwyT2p_96DgsCe35Dr2WyED9858FVbmDDGeJUrv6XUoVepQsIyDRLiAvtNCd4UAVn0xPqFRYuSGP18ysRAcxChgCiuIN1WNCALULfvPQ=w416-h240-k-no',
  },
] as const;

export function NearbyHotels() {
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
