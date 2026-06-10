import type {
  DestinationDetail,
  ExploreDestination,
  ExploreFilterGroup,
  ExploreStat,
} from '@/types';

export const EXPLORE_CATEGORY_FILTERS: readonly string[] = [
  'Semua Rekomendasi',
  'Alam',
  'Keluarga',
  'Kuliner',
  'Hiking',
  'Edukasi',
  'Malam',
  'Dekat Saya',
] as const;

export const EXPLORE_STATS: readonly ExploreStat[] = [
  { label: 'Cocok untuk', value: 'Alam' },
  { label: 'Budget', value: '<100k' },
  { label: 'Waktu', value: '2-3 jam' },
] as const;

export const EXPLORE_FILTER_GROUPS: readonly ExploreFilterGroup[] = [
  {
    title: 'Budget',
    options: ['Gratis', '<50k', '50k-100k'],
  },
  {
    title: 'Kategori',
    options: ['Wisata alam', 'Kuliner lokal', 'Sejarah', 'Keluarga'],
  },
  {
    title: 'Jarak',
    options: ['0-5 km', '5-15 km', '15+ km'],
  },
] as const;

export const EXPLORE_DESTINATIONS: readonly ExploreDestination[] = [
  {
    id: 'kawah-putih',
    title: 'Kawah Putih Ciwidey',
    location: 'Ciwidey, Kab. Bandung',
    price: 'Rp 28.000',
    rating: '4.8',
    category: 'Alam',
    duration: '2-3 jam',
    image: '/destinations/kawah-putih.svg',
  },
  {
    id: 'the-lodge-maribaya',
    title: 'The Lodge Maribaya',
    location: 'Lembang, Bandung Barat',
    price: 'Rp 50.000',
    rating: '4.6',
    category: 'Keluarga',
    duration: '3-4 jam',
    image:
      'https://images.unsplash.com/photo-1449158743715-0a90ebb6d2d8?q=80&w=900&auto=format&fit=crop',
  },
  {
    id: 'sudut-pandang',
    title: 'Sudut Pandang',
    location: 'Ciumbuleuit, Bandung',
    price: 'Rp 50.000',
    rating: '4.9',
    category: 'Kuliner',
    duration: '1-2 jam',
    image:
      'https://images.unsplash.com/photo-1554118811-1e0d58224f24?q=80&w=900&auto=format&fit=crop',
  },
  {
    id: 'farmhouse-lembang',
    title: 'Farmhouse Lembang',
    location: 'Lembang, Bandung Barat',
    price: 'Rp 35.000',
    rating: '4.5',
    category: 'Edukasi',
    duration: '2-3 jam',
    image:
      'https://images.unsplash.com/photo-1518780664697-55e3ad937233?q=80&w=900&auto=format&fit=crop',
  },
] as const;

export const DESTINATION_DETAILS: readonly DestinationDetail[] = [
  {
    ...EXPLORE_DESTINATIONS[0],
    heroImage: '/destinations/kawah-putih.svg',
    aiReason:
      'Kawah Putih cocok untuk itinerary alam setengah hari, punya spot foto ikonik, dan masih aman untuk rencana keluarga dengan budget terkontrol.',
    description:
      'Kawah Putih Ciwidey adalah danau vulkanik dengan warna air kehijauan yang berubah mengikuti cuaca. Udara sejuk, lanskap kabut, dan akses yang relatif mudah membuat tempat ini cocok untuk wisata santai, fotografi, maupun perjalanan singkat dari Bandung.',
    metrics: [
      { label: 'Harga Tiket', value: 'Rp 28.000', tone: 'price' },
      { label: 'Waktu Ideal', value: '2-3 jam', tone: 'time' },
      { label: 'Rating', value: '4.8/5', tone: 'rating' },
    ],
    gallery: [
      '/destinations/kawah-putih.svg',
      'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?q=80&w=800&auto=format&fit=crop',
      'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?q=80&w=800&auto=format&fit=crop',
      'https://images.unsplash.com/photo-1506744038136-46273834b3fb?q=80&w=800&auto=format&fit=crop',
      'https://images.unsplash.com/photo-1501785888041-af3ef285b470?q=80&w=800&auto=format&fit=crop',
    ],
    facilities: [
      'Parkir luas',
      'Toilet',
      'Mushola',
      'Area foto',
      'Warung',
      'Shuttle',
    ],
    weather: {
      condition: 'Cerah berawan',
      temperature: '23°C',
      note: 'Bawa jaket tipis karena angin kawah bisa terasa dingin.',
    },
    nearbyStays: [
      {
        name: 'Bobocabin Ranca Upas',
        location: 'Ciwidey',
        price: 'Mulai Rp 650.000',
        image:
          'https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?q=80&w=500&auto=format&fit=crop',
      },
      {
        name: 'Glamping Lakeside',
        location: 'Situ Patenggang',
        price: 'Mulai Rp 780.000',
        image:
          'https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?q=80&w=500&auto=format&fit=crop',
      },
      {
        name: 'Villa Patuha Resort',
        location: 'Rancabali',
        price: 'Mulai Rp 520.000',
        image:
          'https://images.unsplash.com/photo-1510798831971-661eb04b3739?q=80&w=500&auto=format&fit=crop',
      },
    ],
    reviews: [
      {
        name: 'Rani Putri',
        role: 'Family trip',
        rating: '4.9',
        comment:
          'Pemandangannya cantik dan aksesnya cukup mudah. Datang pagi lebih nyaman karena belum terlalu ramai.',
      },
      {
        name: 'Daffa Mahendra',
        role: 'Solo traveler',
        rating: '4.8',
        comment:
          'Spot foto banyak, udara segar, dan rekomendasi Cepot AI membantu susun rute lanjut ke Situ Patenggang.',
      },
      {
        name: 'Maya Sari',
        role: 'Weekend planner',
        rating: '4.7',
        comment:
          'Worth it untuk perjalanan pendek. Saran terbaiknya bawa masker kalau sensitif dengan aroma belerang.',
      },
    ],
  },
  {
    ...EXPLORE_DESTINATIONS[1],
    heroImage:
      'https://images.unsplash.com/photo-1449158743715-0a90ebb6d2d8?q=80&w=1600&auto=format&fit=crop',
    aiReason:
      'The Lodge Maribaya cocok untuk keluarga dan pasangan yang ingin spot foto alam dengan fasilitas rapi tanpa trekking berat.',
    description:
      'The Lodge Maribaya menawarkan suasana hutan pinus, area foto tematik, dan aktivitas ringan yang cocok untuk perjalanan santai di Lembang.',
    metrics: [
      { label: 'Harga Tiket', value: 'Rp 50.000', tone: 'price' },
      { label: 'Waktu Ideal', value: '3-4 jam', tone: 'time' },
      { label: 'Rating', value: '4.6/5', tone: 'rating' },
    ],
    gallery: [
      'https://images.unsplash.com/photo-1449158743715-0a90ebb6d2d8?q=80&w=800&auto=format&fit=crop',
      'https://images.unsplash.com/photo-1510798831971-661eb04b3739?q=80&w=800&auto=format&fit=crop',
      'https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?q=80&w=800&auto=format&fit=crop',
      'https://images.unsplash.com/photo-1470770841072-f978cf4d019e?q=80&w=800&auto=format&fit=crop',
      'https://images.unsplash.com/photo-1501785888041-af3ef285b470?q=80&w=800&auto=format&fit=crop',
    ],
    facilities: ['Parkir', 'Toilet', 'Mushola', 'Cafe', 'Spot foto', 'Shuttle'],
    weather: {
      condition: 'Sejuk',
      temperature: '22°C',
      note: 'Siapkan alas kaki nyaman untuk area kontur pinus.',
    },
    nearbyStays: [
      {
        name: 'Maribaya Glamping Tent',
        location: 'Lembang',
        price: 'Mulai Rp 720.000',
        image:
          'https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?q=80&w=500&auto=format&fit=crop',
      },
      {
        name: 'Lembang Asri Resort',
        location: 'Lembang',
        price: 'Mulai Rp 610.000',
        image:
          'https://images.unsplash.com/photo-1566073771259-6a8506099945?q=80&w=500&auto=format&fit=crop',
      },
    ],
    reviews: [
      {
        name: 'Ardi Nugraha',
        role: 'Couple trip',
        rating: '4.6',
        comment: 'Tempatnya rapi dan banyak spot foto. Paling enak datang sebelum siang.',
      },
      {
        name: 'Tika Lestari',
        role: 'Family trip',
        rating: '4.5',
        comment: 'Anak-anak suka area hutannya. Pilihan makan juga cukup dekat.',
      },
    ],
  },
  {
    ...EXPLORE_DESTINATIONS[2],
    heroImage:
      'https://images.unsplash.com/photo-1554118811-1e0d58224f24?q=80&w=1600&auto=format&fit=crop',
    aiReason:
      'Sudut Pandang cocok sebagai jeda kuliner karena mudah digabung dengan rute Dago dan punya suasana indoor-outdoor.',
    description:
      'Sudut Pandang adalah destinasi kuliner dan rekreasi visual di area Ciumbuleuit dengan pemandangan kota serta ruang santai yang nyaman.',
    metrics: [
      { label: 'Harga Tiket', value: 'Rp 50.000', tone: 'price' },
      { label: 'Waktu Ideal', value: '1-2 jam', tone: 'time' },
      { label: 'Rating', value: '4.9/5', tone: 'rating' },
    ],
    gallery: [
      'https://images.unsplash.com/photo-1554118811-1e0d58224f24?q=80&w=800&auto=format&fit=crop',
      'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?q=80&w=800&auto=format&fit=crop',
      'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?q=80&w=800&auto=format&fit=crop',
      'https://images.unsplash.com/photo-1509042239860-f550ce710b93?q=80&w=800&auto=format&fit=crop',
      'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?q=80&w=800&auto=format&fit=crop',
    ],
    facilities: ['Cafe', 'Toilet', 'Mushola', 'Wi-Fi', 'Area foto', 'Parkir'],
    weather: {
      condition: 'Nyaman',
      temperature: '25°C',
      note: 'Cocok untuk sore hari menjelang city light.',
    },
    nearbyStays: [
      {
        name: 'Art Deco Luxury Hotel',
        location: 'Ciumbuleuit',
        price: 'Mulai Rp 850.000',
        image:
          'https://images.unsplash.com/photo-1566073771259-6a8506099945?q=80&w=500&auto=format&fit=crop',
      },
      {
        name: 'Padma Hotel Bandung',
        location: 'Ciumbuleuit',
        price: 'Mulai Rp 1.800.000',
        image:
          'https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?q=80&w=500&auto=format&fit=crop',
      },
    ],
    reviews: [
      {
        name: 'Nadia Kirana',
        role: 'Food hunter',
        rating: '4.9',
        comment: 'Ambience bagus, cocok untuk ngobrol lama. View sore hari paling bagus.',
      },
      {
        name: 'Rizky Fajar',
        role: 'Remote worker',
        rating: '4.8',
        comment: 'Tempatnya nyaman dan mudah lanjut ke spot Dago lain.',
      },
    ],
  },
  {
    ...EXPLORE_DESTINATIONS[3],
    heroImage:
      'https://images.unsplash.com/photo-1518780664697-55e3ad937233?q=80&w=1600&auto=format&fit=crop',
    aiReason:
      'Farmhouse Lembang cocok untuk keluarga karena punya area tematik, edukasi ringan, dan alur kunjungan yang mudah.',
    description:
      'Farmhouse Lembang menghadirkan nuansa pedesaan Eropa, area foto, dan aktivitas keluarga yang ringan di jalur wisata Lembang.',
    metrics: [
      { label: 'Harga Tiket', value: 'Rp 35.000', tone: 'price' },
      { label: 'Waktu Ideal', value: '2-3 jam', tone: 'time' },
      { label: 'Rating', value: '4.5/5', tone: 'rating' },
    ],
    gallery: [
      'https://images.unsplash.com/photo-1518780664697-55e3ad937233?q=80&w=800&auto=format&fit=crop',
      'https://images.unsplash.com/photo-1510798831971-661eb04b3739?q=80&w=800&auto=format&fit=crop',
      'https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?q=80&w=800&auto=format&fit=crop',
      'https://images.unsplash.com/photo-1523987355523-c7b5b0dd90a7?q=80&w=800&auto=format&fit=crop',
      'https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?q=80&w=800&auto=format&fit=crop',
    ],
    facilities: ['Parkir', 'Toilet', 'Mushola', 'Restoran', 'Toko oleh-oleh', 'Foto kostum'],
    weather: {
      condition: 'Cerah',
      temperature: '24°C',
      note: 'Datang pagi untuk menghindari antrean foto.',
    },
    nearbyStays: [
      {
        name: 'Grand Paradise Hotel',
        location: 'Lembang',
        price: 'Mulai Rp 560.000',
        image:
          'https://images.unsplash.com/photo-1566073771259-6a8506099945?q=80&w=500&auto=format&fit=crop',
      },
      {
        name: 'Puteri Gunung Hotel',
        location: 'Lembang',
        price: 'Mulai Rp 700.000',
        image:
          'https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?q=80&w=500&auto=format&fit=crop',
      },
    ],
    reviews: [
      {
        name: 'Alya Permata',
        role: 'Family trip',
        rating: '4.5',
        comment: 'Anak-anak senang, spot fotonya banyak, dan lokasinya gampang dicari.',
      },
      {
        name: 'Bima Pratama',
        role: 'Weekend trip',
        rating: '4.4',
        comment: 'Cocok untuk mampir sebelum lanjut wisata Lembang lainnya.',
      },
    ],
  },
] as const;
