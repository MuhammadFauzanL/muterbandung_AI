/**
 * Landing Page Constants
 *
 * Static data for the landing/splash page sections.
 */
import type { Destination, Category } from '@/types';

export const POPULAR_DESTINATIONS: readonly Destination[] = [
  {
    title: 'Kawah Putih Ciwidey',
    location: 'Lembang',
    price: '',
    rating: '4.8',
    image: 'https://images.unsplash.com/photo-1588668214407-6ea9a6d8c272?q=80&w=800&auto=format&fit=crop',
  },
  {
    title: 'Jalan Braga Heritage',
    location: 'Kota Bandung',
    price: '',
    rating: '4.6',
    image: 'https://images.unsplash.com/photo-1555881400-74d7acaacd8b?q=80&w=800&auto=format&fit=crop',
  },
  {
    title: 'Cukul Tea Sunrise',
    location: 'Pangalengan',
    price: '',
    rating: '4.7',
    image: 'https://images.unsplash.com/photo-1523987355523-c7b5b0dd90a7?q=80&w=800&auto=format&fit=crop',
  },
  {
    title: 'Masjid Al-Jabbar',
    location: 'Gedebage',
    price: '',
    rating: '5.0',
    image: 'https://images.unsplash.com/photo-1599940824399-b87987ceb72a?q=80&w=800&auto=format&fit=crop',
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
    title: 'Instragramable',
    description: '',
    image: 'https://images.unsplash.com/photo-1554118811-1e0d58224f24?q=80&w=800&auto=format&fit=crop',
  },
  {
    title: 'Caffe',
    description: '',
    image: 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?q=80&w=800&auto=format&fit=crop',
  },
  {
    title: 'Wisata Sejarah',
    description: '',
    image: 'https://images.unsplash.com/photo-1599940824399-b87987ceb72a?q=80&w=800&auto=format&fit=crop',
  },
] as const;
