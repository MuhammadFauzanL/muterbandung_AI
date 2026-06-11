import type { Destination, Category } from '@/types';

export const POPULAR_DESTINATIONS: readonly Destination[] = [
  {
    title: 'Kawah Putih',
    location: 'Ciwidey, Bandung',
    price: 'Rp 28.000',
    rating: '4.8',
    image: 'https://images.unsplash.com/photo-1588668214407-6ea9a6d8c272?q=80&w=800&auto=format&fit=crop',
  },
  {
    title: 'Farmhouse Lembang',
    location: 'Lembang, Bandung',
    price: 'Rp 35.000',
    rating: '4.5',
    image: 'https://images.unsplash.com/photo-1518780664697-55e3ad937233?q=80&w=800&auto=format&fit=crop',
  },
  {
    title: 'Jalan Braga',
    location: 'Sumur Bandung, Bandung',
    price: 'Gratis',
    rating: '4.9',
    image: 'https://images.unsplash.com/photo-1555881400-74d7acaacd8b?q=80&w=800&auto=format&fit=crop',
  },
  {
    title: 'Trans Studio',
    location: 'Buah Batu, Bandung',
    price: 'Rp 28.000',
    rating: '4.5',
    image: 'https://images.unsplash.com/photo-1513889961551-628c1e5e2ee9?q=80&w=800&auto=format&fit=crop',
  },
  {
    title: 'Lembang Park Zoo',
    location: 'Lembang, Kab Bandung Barat',
    price: 'Rp 28.000',
    rating: '4.5',
    image: 'https://images.unsplash.com/photo-1534567153574-2b12153a87f0?q=80&w=800&auto=format&fit=crop',
  },
  {
    title: 'Ranca Upas',
    location: 'Ciwidey, Bandung',
    price: 'Rp 28.000',
    rating: '4.5',
    image: 'https://images.unsplash.com/photo-1523987355523-c7b5b0dd90a7?q=80&w=800&auto=format&fit=crop',
  },
] as const;

export const CATEGORY_HIGHLIGHTS: readonly Category[] = [
  {
    title: 'Wisata Alam',
    description:
      'Temukan ketenangan di tengah rimbunnya hutan pinus dan kawah vulkanik.',
    image: 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?q=80&w=800&auto=format&fit=crop',
  },
  {
    title: 'Instagramable',
    description: 'Sudut nongkrong nyaman untuk santai dan mengabadikan momen.',
    image: 'https://images.unsplash.com/photo-1554118811-1e0d58224f24?q=80&w=800&auto=format&fit=crop',
  },
  {
    title: 'Cafe',
    description: '',
    image: 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?q=80&w=800&auto=format&fit=crop',
  },
  {
    title: 'Wisata Sejarah',
    description: '',
    image: 'https://images.unsplash.com/photo-1599940824399-b87987ceb72a?q=80&w=800&auto=format&fit=crop',
  },
] as const;
