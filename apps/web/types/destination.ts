/**
 * Destination Types
 *
 * Type definitions for tourist destinations in Bandung.
 */

export interface Destination {
  id?: string | number;
  slug?: string;
  title: string;
  description?: string;
  location: string;
  price: string;
  priceLabel?: string;
  rating: string;
  image: string;
  category?: string;
  heroImage?: string;
  gallery?: string[];
  aiReason?: string;
  facilities?: string[];
  nearbyStays?: Array<{
    name: string;
    location: string;
    image: string;
    price: string;
  }>;
}

export type DestinationList = readonly Destination[];
