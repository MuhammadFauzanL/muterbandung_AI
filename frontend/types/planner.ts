export interface PlannerDestination {
  title: string;
  category: string;
  description: string;
  distance: string;
  duration: string;
  price: string;
  rating: string;
  image: string;
}

export interface SimilarDestination {
  title: string;
  description: string;
  image: string;
}

export interface AccommodationOption {
  name: string;
  type: string;
  location: string;
  distance: string;
  price: string;
  rating: string;
  reviewCount: string;
  description: string;
  image: string;
  highlights: readonly string[];
}
