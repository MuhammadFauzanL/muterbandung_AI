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
    image: 'https://lh3.googleusercontent.com/gps-cs-s/APNQkAFaFXwEw1U4JIxhDsJyjEZJ7dqvRVW5IsAh8vwhX9CJumOqs71mWd90VbeY4WWgvBh6nodCe9tVRNO4574wsSgJnHLeoZRcFa7oXmZYME4fvSDhQ6Vgmu9TRYT8z7sUSaSkjUk_vQ=w408-h306-k-no',
  },
  {
    title: 'Jalan Braga Heritage',
    location: 'Kota Bandung',
    price: '',
    rating: '4.6',
    image: 'https://lh3.googleusercontent.com/gps-cs-s/APNQkAHI21zGS9xyCZJeyKYA46sbK48R4C-qIP7PISWq899VnDPQjE0Ju6fVosMcdR22gL0V5ILEFW0M8vnRi4o_1fTgm7sKAwt9gb0qyXcloQXNrxGNtjj4080-pFj1xNKaiPNp-cdI=w408-h544-k-no',
  },
  {
    title: 'Cukul Tea Sunrise',
    location: 'Pangalengan',
    price: '',
    rating: '4.7',
    image: 'https://lh3.googleusercontent.com/gps-cs-s/APNQkAH4hnLrM3DpouTLj9y1e4yRzJ0YbExJ7GkwvB7F9jOuyFdYPMT4Z0bBwZy7Sjr0sNeVAHgwDUrnv2AjUETl2ua__0wF0mKcgXCsWM3MYIzJ0PNpBBVkBH_ah9P8rel5_qSv4kk=w427-h240-k-no',
  },
  {
    title: 'Masjid Al-Jabbar',
    location: 'Gedebage',
    price: '',
    rating: '5.0',
    image: 'https://lh3.googleusercontent.com/gps-cs-s/APNQkAEgOgolRnHXere0lPbPK8QF1-B2DOXm-uaMyAJrnN6-1yCvyU5AeLdXAz8inPl8VsyZQdTTeP07HCunAHDUtgFueVAIXhgTMWNHizB8reDjeEkbKuherL0TAML0KaNct_hZrMNJ2g=w408-h307-k-no',
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
