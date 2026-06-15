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
    image: 'https://lh3.googleusercontent.com/gps-cs-s/APNQkAFaFXwEw1U4JIxhDsJyjEZJ7dqvRVW5IsAh8vwhX9CJumOqs71mWd90VbeY4WWgvBh6nodCe9tVRNO4574wsSgJnHLeoZRcFa7oXmZYME4fvSDhQ6Vgmu9TRYT8z7sUSaSkjUk_vQ=w408-h306-k-no',
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
      'https://lh3.googleusercontent.com/gps-cs-s/APNQkAGag0VLevHCsTHhDlK95tp5oz82x5jCeIof-xVau_rViiNgCFEcFPKsH1LZ5CM1HkFmRhMH1tTXEWkANtLa8sCda9DP7Whkcphpp9YjHym9mU77UzkIf7osXRG1f_BK9UTJd0x50Q=w408-h272-k-no',
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
      'https://lh3.googleusercontent.com/gps-cs-s/APNQkAGB5A_jnvgXbWCpyJ1fPpXz6_5EEDTyyiBslNudJ3VsDF5UUyWXwiNRgNzLn5hpbZMg8jz8ci8hmMDS1v5Sp7RR5lmO1Sx_yChtHboP8vwpHWr8uu0qMSsAS5njXYDOyIl-rV1OVvAUpmZF=w408-h612-k-no',
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
      'https://lh3.googleusercontent.com/gps-cs-s/APNQkAEOwm4L-_oDg37hoOpkgGYAx4r2e55VUnu2yhFM-9YPBlvrm_r9W7NqYazeiLvd8nNhOzOX8OYrS58ijbdXASjgOgftE210IJiO4q2Q15pYZP83QIyl6eSb-cgDTY3xXk_7TRPqFQ=w408-h306-k-no',
  },
] as const;

export const DESTINATION_DETAILS: readonly DestinationDetail[] = [
  {
    ...EXPLORE_DESTINATIONS[0],
    heroImage: 'https://lh3.googleusercontent.com/gps-cs-s/APNQkAFaFXwEw1U4JIxhDsJyjEZJ7dqvRVW5IsAh8vwhX9CJumOqs71mWd90VbeY4WWgvBh6nodCe9tVRNO4574wsSgJnHLeoZRcFa7oXmZYME4fvSDhQ6Vgmu9TRYT8z7sUSaSkjUk_vQ=w408-h306-k-no',
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
      'https://lh3.googleusercontent.com/gps-cs-s/APNQkAFaFXwEw1U4JIxhDsJyjEZJ7dqvRVW5IsAh8vwhX9CJumOqs71mWd90VbeY4WWgvBh6nodCe9tVRNO4574wsSgJnHLeoZRcFa7oXmZYME4fvSDhQ6Vgmu9TRYT8z7sUSaSkjUk_vQ=w408-h306-k-no',
      'https://lh3.googleusercontent.com/gps-cs-s/APNQkAHVY6eUFC9uWt0H1O4Ya4jvM86cHKdTJtCz9_6P3sD-U-dJC9IJuT_WOBfCT26Uo7-4DPoEjyByYBfYv_8aFDBlLkTMRT9lslSj_IJ0uPDD--XPYjdxFnc-kpi6PpQOxGvctl5w=w224-h398-k-no',
      'https://lh3.googleusercontent.com/gps-cs-s/APNQkAEw9YulVVbWWgZoIjoftnRLbPC3nGW0VlDQGW9tP3ERkOwD9OlLSm-SA83BVC-yol8jtG3O3-CXkLIlb7ONJLWn5oVDy2k_hgeBNijzl8vN-VBn40NLktdStaHvy-Qt-n-8zvM3SA=w529-h298-k-no',
      'https://lh3.googleusercontent.com/gps-cs-s/APNQkAFsAsjcB4KkTK263DcaFlX5HHIc8ixC7CexyD4rOZ-ZY0y4Lm8WdgjRGQ0Q8scKifr6myvS9RJZQEHkWMlOdKVR37GBA68-Mv7dSy8VeUR7IkkL9WK5xBfVRSdY02-ZqfF9K7NqxINIUzg=w224-h398-k-no',
      'https://lh3.googleusercontent.com/gps-cs-s/APNQkAFaFXwEw1U4JIxhDsJyjEZJ7dqvRVW5IsAh8vwhX9CJumOqs71mWd90VbeY4WWgvBh6nodCe9tVRNO4574wsSgJnHLeoZRcFa7oXmZYME4fvSDhQ6Vgmu9TRYT8z7sUSaSkjUk_vQ=w408-h306-k-no',
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
          'https://lh3.googleusercontent.com/gps-proxy/ALd4DhFQNQ81Dicl74zu40V7aXYY50dw0TH-lPCwm_rFUokItvPcAB2TR0TclWJS-39WNWfCJ_04IFMGsytAfz0mjmiv_2ft5DRYmyE0tyFhO6Q8WM81wJqxKvqNiKtB-0VBqYxss31T3exO_FUzUlc3d9J0f-idvXZvvVAfRhO6qZKDrOa9ali32Kou7Q=w455-h240-k-no',
      },
      {
        name: 'Glamping Lakeside',
        location: 'Situ Patenggang',
        price: 'Mulai Rp 780.000',
        image:
          'https://lh3.googleusercontent.com/gps-proxy/ALd4DhG4zvnpyhSwhsxDH6NhAELLszGnGdWxJq98Cm8xHBLL0dy-s-QcYoPq6c2ftf-GSGlzCQc80Vgidf5Km37Vyc2c427nSsuKAPDpPlBzzNHIrxYvvIDq55T25lMdbmnmG4Pk25Fl4CcR_ckRnGlJed_-_B5mtTecgra5UITD2iE1lsB7y3Tqm2-Zmw=w408-h300-k-no',
      },
      {
        name: 'Villa Patuha Resort',
        location: 'Rancabali',
        price: 'Mulai Rp 520.000',
        image:
          'https://lh3.googleusercontent.com/gps-cs-s/APNQkAEINPwRItiBa-w5a0baJmuuVumrV1ITN9jwyT2p_96DgsCe35Dr2WyED9858FVbmDDGeJUrv6XUoVepQsIyDRLiAvtNCd4UAVn0xPqFRYuSGP18ysRAcxChgCiuIN1WNCALULfvPQ=w416-h240-k-no',
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
          'https://lh3.googleusercontent.com/gps-proxy/ALd4DhGX8w9qk9j5Y_2xAGRr7S328EAuKfdOny3WGXiOhgMKLiL1rKwJillorzX3Zhwnss-PlbgBDu-wSkO4dJC3rj6Lx_7gVYfwgJectjQVvB3VVqc0pZMkZGDwn5yELBRYTM17e8Frtx4Kz2jGV13GeRZRajShfk8LT4iTWpmPkaJPex90ATaeLQwI=w408-h272-k-no',
      },
      {
        name: 'Puteri Gunung Hotel',
        location: 'Lembang',
        price: 'Mulai Rp 700.000',
        image:
          'https://lh3.googleusercontent.com/gps-proxy/ALd4DhFmom7fwHALFdyh_mmOrATQaeNj3S7riiTmj54xTIuplAUWfhF75VTGHJNnYp0IEn7GgM4_M8LOk0WezJWjT5y8RIEFGxfFwhZgRQd6Pm2I9P302gtf5PW6P9t7LC_c2-x2HLHhdHV1U9F05yadXcHBqKdOor6b8lY8s17EVXbramT1EdzdpYoIyg=w472-h240-k-no',
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
