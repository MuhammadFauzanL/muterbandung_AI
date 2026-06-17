export interface ExploreDestination {
  id: string;
  title: string;
  location: string;
  price: string;
  rating: string;
  category: string;
  duration?: string;
  image: string;
}

export interface DetailMetric {
  label: string;
  value: string;
  tone: 'price' | 'time' | 'rating';
}

export interface DestinationReview {
  name: string;
  role: string;
  rating: string;
  comment: string;
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
  reviews: readonly DestinationReview[];
}

export interface ExploreFilterGroup {
  title: string;
  options: readonly string[];
}

export interface ExploreStat {
  label: string;
  value: string;
}
