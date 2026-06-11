import type {
  AccommodationOption,
  PlannerDestination,
  SimilarDestination,
} from '@/types';

export const NEARBY_DESTINATIONS: readonly PlannerDestination[] = [
  {
    title: 'Situ Patenggang',
    category: 'Alam',
    description:
      'Danau legendaris dengan pemandangan kebun teh yang menyejukkan mata.',
    distance: '25 m dari Kawah Putih',
    duration: '1-2 jam',
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
    distance: '1.5 km dari Kawah Putih',
    duration: '2-3 jam',
    price: 'Rp25.000',
    rating: '4.6',
    image: '/destinations/ranca-upas.svg',
  },
] as const;

export const SIMILAR_DESTINATIONS: readonly SimilarDestination[] = [
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

export const ACCOMMODATION_FILTERS: readonly string[] = [
  'Semua',
  'Dekat Kawah Putih',
  'Family stay',
  'Cabin',
  'Budget hemat',
] as const;

export const ACCOMMODATIONS: readonly AccommodationOption[] = [
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
