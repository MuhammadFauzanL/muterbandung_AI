export interface Accommodation {
  id: string;
  slug?: string;
  name: string;
  type?: string;
  category?: string;
  image: string;
  rating: string;
  reviewCount: string;
  price: string;
  location: string;
  latitude?: number;
  longitude?: number;
  distanceKm?: number;
  distance: string;
  facilities: readonly string[];
  mapsUrl?: string;
  bookingUrl?: string;
  score?: number;
  scoreReason?: string;
  highlights: readonly string[];
}

export interface AccommodationMeta {
  page: number;
  limit: number;
  total: number;
  totalPages: number;
}

export interface AccommodationResponse {
  data: Accommodation[];
  meta: AccommodationMeta;
}

export interface AccommodationFilterOption {
  label: string;
  value: string;
  count: number;
}

export interface AccommodationFilterMetadata {
  types: AccommodationFilterOption[];
  priceOptions: string[];
  ratingOptions: number[];
  facilityOptions: string[];
  sortOptions: string[];
}
