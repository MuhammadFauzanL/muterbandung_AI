/**
 * Destination Types
 *
 * Type definitions for tourist destinations in Bandung.
 */

export interface Destination {
  title: string;
  location: string;
  price: string;
  rating: string;
  image: string;
}

export type DestinationList = readonly Destination[];
