import { apiFetch } from './api';
import type {
  Accommodation,
  AccommodationFilterMetadata,
  AccommodationMeta,
  AccommodationResponse,
} from '@/types';

export interface AccommodationQueryParams {
  page?: number;
  limit?: number;
  search?: string;
  type?: string | null;
  maxPrice?: number;
  minRating?: number;
  facilities?: readonly string[];
  userLat?: number;
  userLng?: number;
  radiusKm?: number | null;
  sort?: 'recommended' | 'nearest' | 'rating' | 'reviews' | 'price_low' | 'price_high';
}

interface ApiResponse<T> {
  data?: T;
  meta?: AccommodationMeta;
}

interface ApiAccommodationCard {
  id?: string;
  slug?: string;
  name?: string;
  type?: string | null;
  category?: string | null;
  imageUrl?: string | null;
  rating?: number | string | null;
  reviewCount?: number | string | null;
  priceLabel?: string;
  location?: string;
  latitude?: number | string | null;
  longitude?: number | string | null;
  distanceKm?: number | null;
  facilities?: string[];
  mapsUrl?: string | null;
  bookingUrl?: string | null;
  score?: number | null;
  scoreReason?: string | null;
}

function appendQuery(params: URLSearchParams, key: string, value: unknown) {
  if (value === undefined || value === null || value === '') return;
  params.set(key, String(value));
}

function formatRating(value: unknown) {
  const numeric = Number(value ?? 0);
  return Number.isFinite(numeric) && numeric > 0 ? numeric.toFixed(1) : 'Baru';
}

function formatReviewCount(value: unknown) {
  const numeric = Number(value ?? 0);
  if (!Number.isFinite(numeric) || numeric <= 0) return 'Belum ada ulasan';
  return `${numeric.toLocaleString('id-ID')} ulasan`;
}

function formatDistance(value?: number | null) {
  if (value === undefined || value === null) return 'Jarak belum tersedia';
  return `${value.toFixed(value < 10 ? 1 : 0)} km dari destinasi`;
}

function parseCoordinate(value: unknown): number | undefined {
  const numeric = typeof value === 'string' ? Number(value) : value;
  return typeof numeric === 'number' && Number.isFinite(numeric) ? numeric : undefined;
}

function buildHighlights(item: ApiAccommodationCard) {
  const facilities = item.facilities || [];
  const values = [
    item.distanceKm !== null && item.distanceKm !== undefined
      ? `${item.distanceKm.toFixed(item.distanceKm < 10 ? 1 : 0)} km`
      : undefined,
    item.type || undefined,
    ...facilities.slice(0, 2),
  ].filter(Boolean) as string[];
  return values.length > 0 ? values : ['Data aktif', 'Akomodasi'];
}

export function mapAccommodation(item: ApiAccommodationCard): Accommodation {
  return {
    id: item.id || item.slug || item.name || 'accommodation',
    slug: item.slug,
    name: item.name || 'Penginapan Bandung',
    type: item.type || undefined,
    category: item.category || undefined,
    image: item.imageUrl || '',
    rating: formatRating(item.rating),
    reviewCount: formatReviewCount(item.reviewCount),
    price: item.priceLabel || 'Harga belum tersedia',
    location: item.location || 'Bandung Raya',
    latitude: parseCoordinate(item.latitude),
    longitude: parseCoordinate(item.longitude),
    distanceKm: item.distanceKm ?? undefined,
    distance: formatDistance(item.distanceKm),
    facilities: item.facilities || [],
    mapsUrl: item.mapsUrl || undefined,
    bookingUrl: item.bookingUrl || undefined,
    score: item.score ?? undefined,
    scoreReason: item.scoreReason || undefined,
    highlights: buildHighlights(item),
  };
}

function buildQuery(params: AccommodationQueryParams = {}) {
  const query = new URLSearchParams();
  appendQuery(query, 'page', params.page ?? 1);
  appendQuery(query, 'limit', params.limit ?? 12);
  appendQuery(query, 'search', params.search);
  appendQuery(query, 'type', params.type);
  appendQuery(query, 'maxPrice', params.maxPrice);
  appendQuery(query, 'minRating', params.minRating);
  appendQuery(query, 'userLat', params.userLat);
  appendQuery(query, 'userLng', params.userLng);
  appendQuery(query, 'radiusKm', params.radiusKm);
  appendQuery(query, 'sort', params.sort ?? 'recommended');
  if (params.facilities && params.facilities.length > 0) {
    appendQuery(query, 'facilities', params.facilities.join(','));
  }
  return query;
}

export const accommodationsService = {
  async getAll(params: AccommodationQueryParams = {}): Promise<AccommodationResponse> {
    const query = buildQuery(params);
    const res = await apiFetch<ApiResponse<ApiAccommodationCard[]>>(
      `/accommodations?${query.toString()}`,
      { method: 'GET' },
    );

    return {
      data: (res.data || []).map(mapAccommodation),
      meta: res.meta || { page: 1, limit: params.limit ?? 12, total: 0, totalPages: 0 },
    };
  },

  async getNearbyForDestination(
    destinationSlug: string,
    params: AccommodationQueryParams = {},
  ): Promise<AccommodationResponse> {
    const query = buildQuery({
      ...params,
      limit: params.limit ?? 5,
      radiusKm: params.radiusKm ?? 10,
      sort: params.sort ?? 'recommended',
    });
    const res = await apiFetch<ApiResponse<ApiAccommodationCard[]>>(
      `/destinations/${destinationSlug}/nearby-accommodations?${query.toString()}`,
      { method: 'GET' },
    );

    return {
      data: (res.data || []).map(mapAccommodation),
      meta: res.meta || { page: 1, limit: params.limit ?? 5, total: 0, totalPages: 0 },
    };
  },

  async getFilters(): Promise<AccommodationFilterMetadata> {
    const res = await apiFetch<ApiResponse<AccommodationFilterMetadata>>(
      '/accommodations/filters',
      { method: 'GET' },
    );

    return res.data || {
      types: [],
      priceOptions: [],
      ratingOptions: [],
      facilityOptions: [],
      sortOptions: [],
    };
  },
};
