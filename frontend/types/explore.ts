export interface ExploreDestination {
  id: string;
  slug?: string;
  title: string;
  location: string;
  price: string;
  priceLabel?: string;
  rating: string;
  category: string;
  primaryIntent?: string;
  duration?: string;
  durationMinutes?: number;
  image: string;
  openingHoursLabel?: string;
  distanceKm?: number;
  latitude?: number;
  longitude?: number;
  score?: number;
  scoreReason?: string;
  isFavorite?: boolean;
}

export interface ExploreFilters {
  search: string;
  intent: string | null;
  budget: 'free' | 'under_50000' | 'under_100000' | 'custom' | null;
  customMaxPrice: string;
  radiusKm: number | null;
  dayType: 'weekday' | 'weekend' | null;
  plannedTime: string;
  minRating: number | null;
  childFriendly: boolean;
  openNow: boolean;
  needsAccommodation: boolean;
  userLat?: number;
  userLng?: number;
  sort: 'quality' | 'popular' | 'rating' | 'reviews' | 'price_low' | 'price_high' | 'nearest' | 'personal';
}

export interface ExploreMeta {
  page: number;
  limit: number;
  total: number;
  totalPages: number;
}

export interface ExploreFilterOption {
  label: string;
  value: string;
  count: number;
}

export interface ExploreFilterMetadata {
  intents: ExploreFilterOption[];
  categories: ExploreFilterOption[];
  budgetOptions: string[];
  ratingOptions: number[];
  sortOptions: string[];
}

export interface DetailMetric {
  label: string;
  value: string;
  tone: 'price' | 'time' | 'rating';
}

export interface NearbyStay {
  name: string;
  location: string;
  price: string;
  image: string;
}

export interface DestinationDetail extends ExploreDestination {
  heroImage: string;
  aiReason: string;
  description: string;
  metrics?: readonly DetailMetric[];
  gallery: readonly string[];
  facilities: readonly string[];
  weather?: {
    condition: string;
    temperature: string;
    note: string;
  };
  nearbyStays: readonly NearbyStay[];
}
