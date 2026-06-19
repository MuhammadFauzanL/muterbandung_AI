import { apiFetch } from './api';
import type {
  Destination,
  DestinationDetail,
  ExploreDestination,
  ExploreFilterMetadata,
  ExploreMeta,
  ExploreScoreBreakdown,
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
  location?: string | { label?: string; latitude?: number | string | null; longitude?: number | string | null };
  tourismZone?: string;
  rating?: number | string | null;
  imageUrl?: string | null;
  priceLabel?: string;
  category?: string;
  primaryIntent?: string;
  durationMinutes?: number | null;
  openingHoursLabel?: string | null;
  distanceKm?: number | null;
  latitude?: number | string | null;
  longitude?: number | string | null;
  score?: number | null;
  scoreReason?: string | null;
  scoreBreakdown?: ExploreScoreBreakdown | null;
  score_breakdown?: ExploreScoreBreakdown | null;
}

interface ApiDestinationDetail {
  id?: string;
  slug?: string;
  name?: string;
  description?: string;
  location?: string | { label?: string; latitude?: number | string | null; longitude?: number | string | null };
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

function parseCoordinate(value: unknown): number | undefined {
  const numeric = typeof value === 'string' ? Number(value) : value;
  return typeof numeric === 'number' && Number.isFinite(numeric) ? numeric : undefined;
}

function getLocationObject(location: ApiDestinationCard['location'] | ApiDestinationDetail['location']) {
  return typeof location === 'object' && location !== null ? location : null;
}

export function mapExploreDestination(item: ApiDestinationCard): ExploreDestination {
  const locationObj = getLocationObject(item.location);
  const latitude = parseCoordinate(item.latitude ?? locationObj?.latitude);
  const longitude = parseCoordinate(item.longitude ?? locationObj?.longitude);

  return {
    id: item.id || item.slug || item.name || 'destination',
    slug: item.slug,
    title: item.name || 'Destinasi Bandung',
    location: locationObj?.label || (typeof item.location === 'string' ? item.location : undefined) || item.tourismZone || 'Bandung Raya',
    rating: formatRating(item.rating),
    image: item.imageUrl || '',
    price: item.priceLabel || 'Harga belum tersedia',
    category: item.category || item.primaryIntent || 'Wisata',
    primaryIntent: item.primaryIntent,
    duration: formatDuration(item.durationMinutes),
    durationMinutes: item.durationMinutes ?? undefined,
    openingHoursLabel: item.openingHoursLabel ?? undefined,
    distanceKm: item.distanceKm ?? undefined,
    latitude,
    longitude,
    score: item.score ?? undefined,
    scoreReason: item.scoreReason ?? undefined,
    scoreBreakdown: item.scoreBreakdown ?? item.score_breakdown ?? undefined,
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
      location: getLocationObject(item.location)?.label || (typeof item.location === 'string' ? item.location : undefined) || item.tourismZone || 'Bandung Raya',
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

    // Always send auth token so backend can identify the user for personal sort
    const res = await apiFetch<ApiResponse<ApiDestinationCard[]>>(`/destinations?${query.toString()}`, {
      method: 'GET',
      requireAuth: true,
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
    const locationObj = getLocationObject(item.location);
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
      nearbyStays: item.nearbyStays || [],
      price: item.ticket?.label || item.priceLabel || "Gratis",
      latitude: parseCoordinate(locationObj?.latitude),
      longitude: parseCoordinate(locationObj?.longitude),
    };
  },
};
