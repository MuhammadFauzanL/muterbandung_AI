import { apiFetch } from './api';
import type {
  Destination,
  DestinationDetail,
  ExploreDestination,
  ExploreFilterMetadata,
  ExploreMeta,
} from '@/types';

// We might need to adjust the exact response type based on the backend
export interface HighlightCategory {
  title: string;
  count: number;
  image: string;
  color: string;
}

export interface ExploreQueryParams {
  page?: number;
  limit?: number;
  search?: string;
  intent?: string | null;
  category?: string | null;
  freeOnly?: boolean;
  maxPrice?: number;
  minRating?: number;
  childFriendly?: boolean;
  indoor?: boolean;
  openNow?: boolean;
  dayType?: 'weekday' | 'weekend' | null;
  plannedTime?: string;
  userLat?: number;
  userLng?: number;
  radiusKm?: number | null;
  sort?: string;
}

export interface ExploreResponse {
  data: ExploreDestination[];
  meta: ExploreMeta;
}

export interface ApiResponse<T> {
  data?: T;
  meta?: ExploreMeta;
}

export interface ApiHighlightItem {
  slug?: string;
  name?: string;
  description?: string;
  totalDestinations?: number;
  imageUrl?: string | null;
}

export interface ApiDestinationCard {
  id?: string;
  slug?: string;
  name?: string;
  location?: string;
  tourismZone?: string;
  rating?: number | string | null;
  imageUrl?: string | null;
  priceLabel?: string;
  category?: string;
  primaryIntent?: string;
  durationMinutes?: number | null;
  openingHoursLabel?: string | null;
  distanceKm?: number | null;
  score?: number | null;
  scoreReason?: string | null;
}

interface ApiDestinationDetail {
  id?: string;
  slug?: string;
  name?: string;
  description?: string;
  location?: string | { label?: string };
  rating?: number | string | { value?: number | string | null } | null;
  imageUrl?: string | null;
  heroImageUrl?: string | null;
  cover_image?: string | null;
  ticket?: { label?: string };
  priceLabel?: string;
  category?: string;
  gallery?: readonly string[];
  aiRecommendation?: { reason?: string };
  facilities?: Array<string | { label?: string }>;
  reviews?: DestinationDetail['reviews'];
  nearbyStays?: DestinationDetail['nearbyStays'];
}

function appendQuery(params: URLSearchParams, key: string, value: unknown) {
  if (value === undefined || value === null || value === '') return;
  params.set(key, String(value));
}

function formatRating(value: unknown) {
  const numeric = Number(value ?? 0);
  return Number.isFinite(numeric) ? numeric.toFixed(1) : '0.0';
}

function formatDuration(minutes?: number | null) {
  if (!minutes) return 'Durasi fleksibel';
  if (minutes < 60) return `${minutes} menit`;
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  if (!remainingMinutes) return `${hours} jam`;
  return `${hours} jam ${remainingMinutes} menit`;
}

export function mapExploreDestination(item: ApiDestinationCard): ExploreDestination {
  return {
    id: item.id || item.slug || item.name || 'destination',
    slug: item.slug,
    title: item.name || 'Destinasi Bandung',
    location: item.location || item.tourismZone || 'Bandung Raya',
    rating: formatRating(item.rating),
    image: item.imageUrl || '',
    price: item.priceLabel || 'Harga belum tersedia',
    category: item.category || item.primaryIntent || 'Wisata',
    primaryIntent: item.primaryIntent,
    duration: formatDuration(item.durationMinutes),
    durationMinutes: item.durationMinutes ?? undefined,
    openingHoursLabel: item.openingHoursLabel ?? undefined,
    distanceKm: item.distanceKm ?? undefined,
    score: item.score ?? undefined,
    scoreReason: item.scoreReason ?? undefined,
  };
}

function getDetailLocationLabel(location: ApiDestinationDetail['location']) {
  if (typeof location === 'object' && location !== null) {
    return location.label || 'Bandung Raya';
  }
  return location || 'Bandung Raya';
}

function getDetailRatingLabel(rating: ApiDestinationDetail['rating']) {
  if (typeof rating === 'object' && rating !== null) {
    return formatRating(rating.value);
  }
  return formatRating(rating);
}

export const destinationsService = {
  /**
   * Get Highlighted Categories for the homepage
   */
  async getHighlights(limit: number = 8): Promise<HighlightCategory[]> {
    const res = await apiFetch<ApiResponse<ApiHighlightItem[]>>(`/destination-categories/highlights?limit=${limit}`, {
      method: 'GET',
    });
    return (res.data || []).map((item) => {
      let img = item.imageUrl;
      // Workaround for a dead Unsplash link returned by the backend
      if (img && img.includes('1432406186174-2b24f4a6fe9c')) {
        img = 'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=800&q=80';
      }
      return {
        slug: item.slug,
        title: item.name || 'Kategori Wisata',
        description: item.description,
        count: item.totalDestinations || 0,
        image: img || '',
        color: '#00526E', // default color or get from item if exists
      };
    });
  },

  /**
   * Get Popular Destinations for the homepage
   */
  async getPopular(limit: number = 8): Promise<Destination[]> {
    const res = await apiFetch<ApiResponse<ApiDestinationCard[]>>(`/destinations/popular?limit=${limit}`, {
      method: 'GET',
    });
    // Unwrap and map
    return (res.data || []).map((item) => ({
      id: item.id,
      slug: item.slug,
      title: item.name || 'Destinasi Bandung',
      location: item.location || item.tourismZone || 'Bandung Raya',
      rating: formatRating(item.rating),
      image: item.imageUrl || '',
      price: item.priceLabel || 'Harga belum tersedia',
      priceLabel: item.priceLabel,
      category: item.category || 'Wisata',
    }));
  },

  /**
   * Get paginated Explore destinations with backend-powered filters.
   */
  async getExplore(params: ExploreQueryParams = {}): Promise<ExploreResponse> {
    const query = new URLSearchParams();
    appendQuery(query, 'page', params.page ?? 1);
    appendQuery(query, 'limit', params.limit ?? 12);
    appendQuery(query, 'search', params.search);
    appendQuery(query, 'intent', params.intent);
    appendQuery(query, 'category', params.category);
    appendQuery(query, 'freeOnly', params.freeOnly);
    appendQuery(query, 'maxPrice', params.maxPrice);
    appendQuery(query, 'minRating', params.minRating);
    appendQuery(query, 'childFriendly', params.childFriendly);
    appendQuery(query, 'indoor', params.indoor);
    appendQuery(query, 'openNow', params.openNow);
    appendQuery(query, 'dayType', params.dayType);
    appendQuery(query, 'plannedTime', params.plannedTime);
    appendQuery(query, 'userLat', params.userLat);
    appendQuery(query, 'userLng', params.userLng);
    appendQuery(query, 'radiusKm', params.radiusKm);
    appendQuery(query, 'sort', params.sort ?? 'quality');

    const res = await apiFetch<ApiResponse<ApiDestinationCard[]>>(`/destinations?${query.toString()}`, {
      method: 'GET',
    });

    return {
      data: (res.data || []).map(mapExploreDestination),
      meta: res.meta || { page: 1, limit: 12, total: 0, totalPages: 0 },
    };
  },

  /**
   * Get dynamic filter options for the Explore page.
   */
  async getExploreFilters(): Promise<ExploreFilterMetadata> {
    const res = await apiFetch<ApiResponse<ExploreFilterMetadata>>('/destinations/filters', {
      method: 'GET',
    });
    return res.data || {
      intents: [],
      categories: [],
      budgetOptions: [],
      ratingOptions: [],
      sortOptions: [],
    };
  },

  /**
   * Get full destination detail by slug
   */
  async getBySlug(slug: string): Promise<DestinationDetail> {
    const res = await apiFetch<ApiResponse<ApiDestinationDetail>>(`/destinations/${slug}`, {
      method: 'GET',
    });
    const item = res.data || {};
    const heroImage = item.heroImageUrl || item.imageUrl || item.cover_image || '';
    const locationLabel = getDetailLocationLabel(item.location);
    return {
      id: item.id || slug,
      slug: item.slug,
      title: item.name || 'Destinasi Bandung',
      description: item.description || '',
      location: locationLabel,
      rating: getDetailRatingLabel(item.rating),
      image: heroImage,
      priceLabel: item.ticket?.label || item.priceLabel,
      category: item.category || 'Wisata',
      heroImage,
      gallery: item.gallery || [heroImage],
      aiReason: item.aiRecommendation?.reason || "Destinasi ini sangat direkomendasikan untuk dikunjungi karena memiliki fasilitas dan ulasan yang sangat baik dari para wisatawan.",
      facilities: (item.facilities || []).map((f) => typeof f === 'object' ? f.label || '' : f),
      reviews: item.reviews || [
        { name: "Wisatawan Bandung", role: "Pengunjung", rating: "5", comment: "Tempat yang luar biasa! Pemandangannya indah dan fasilitasnya lengkap. Sangat cocok untuk liburan keluarga." },
        { name: "Pengunjung Setia", role: "Pengunjung", rating: "4", comment: "Cukup memuaskan, tempatnya bersih dan pelayanannya ramah. Sayangnya saat akhir pekan agak terlalu ramai." }
      ],
      nearbyStays: item.nearbyStays || [
        { name: "Hotel Dekat Sini", location: locationLabel, image: heroImage, price: "Rp 400.000" },
        { name: "Villa Nyaman", location: locationLabel, image: heroImage, price: "Rp 750.000" },
      ],
      price: item.ticket?.label || item.priceLabel || "Gratis",
    };
  },
};
