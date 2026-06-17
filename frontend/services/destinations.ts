import { apiFetch } from './api';
import type { Destination } from '@/types';

// We might need to adjust the exact response type based on the backend
export interface HighlightCategory {
  title: string;
  count: number;
  image: string;
  color: string;
}

export const destinationsService = {
  /**
   * Get Highlighted Categories for the homepage
   */
  async getHighlights(limit: number = 8): Promise<HighlightCategory[]> {
    const res = await apiFetch<any>(`/destination-categories/highlights?limit=${limit}`, {
      method: 'GET',
    });
    return (res.data || []).map((item: any) => {
      let img = item.imageUrl;
      // Workaround for a dead Unsplash link returned by the backend
      if (img && img.includes('1432406186174-2b24f4a6fe9c')) {
        img = 'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=800&q=80';
      }
      return {
        slug: item.slug,
        title: item.name,
        description: item.description,
        count: item.totalDestinations || 0,
        image: img,
        color: '#00526E', // default color or get from item if exists
      };
    });
  },

  /**
   * Get Popular Destinations for the homepage
   */
  async getPopular(limit: number = 8): Promise<Destination[]> {
    const res = await apiFetch<any>(`/destinations/popular?limit=${limit}`, {
      method: 'GET',
    });
    // Unwrap and map
    return (res.data || []).map((item: any) => ({
      id: item.id,
      slug: item.slug,
      title: item.name,
      location: item.location,
      rating: parseFloat(item.rating).toFixed(1),
      image: item.imageUrl,
      priceLabel: item.priceLabel,
      category: item.category,
    }));
  },

  /**
   * Get full destination detail by slug
   */
  async getBySlug(slug: string): Promise<Destination> {
    const res = await apiFetch<any>(`/destinations/${slug}`, {
      method: 'GET',
    });
    const item = res.data || res; // depending on if detail is wrapped
    return {
      id: item.id,
      slug: item.slug,
      title: item.name,
      description: item.description,
      location: typeof item.location === 'object' ? item.location?.label || 'Bandung Raya' : item.location,
      rating: typeof item.rating === 'object' ? parseFloat(item.rating.value).toFixed(1) : (item.rating ? parseFloat(item.rating).toFixed(1) : "0.0"),
      image: item.imageUrl || item.heroImageUrl || item.cover_image,
      priceLabel: item.ticket?.label || item.priceLabel,
      category: item.category,
      heroImage: item.heroImageUrl || item.imageUrl || item.cover_image,
      gallery: item.gallery || [item.heroImageUrl || item.imageUrl || item.cover_image],
      aiReason: item.aiRecommendation?.reason || "Destinasi ini sangat direkomendasikan untuk dikunjungi karena memiliki fasilitas dan ulasan yang sangat baik dari para wisatawan.",
      facilities: (item.facilities || []).map((f: any) => typeof f === 'object' ? f.label : f),
      reviews: item.reviews || [
        { name: "Wisatawan Bandung", rating: 5, comment: "Tempat yang luar biasa! Pemandangannya indah dan fasilitasnya lengkap. Sangat cocok untuk liburan keluarga." },
        { name: "Pengunjung Setia", rating: 4, comment: "Cukup memuaskan, tempatnya bersih dan pelayanannya ramah. Sayangnya saat akhir pekan agak terlalu ramai." }
      ],
      nearbyStays: item.nearbyStays || [
        { name: "Hotel Dekat Sini", location: typeof item.location === 'object' ? item.location?.label : item.location, image: item.heroImageUrl || item.imageUrl, price: "Rp 400.000" },
        { name: "Villa Nyaman", location: typeof item.location === 'object' ? item.location?.label : item.location, image: item.heroImageUrl || item.imageUrl, price: "Rp 750.000" },
      ],
      price: item.ticket?.label || item.priceLabel || "Gratis",
    } as any;
  },
};
