/**
 * Category Types
 *
 * Type definitions for destination categories.
 */

export interface Category {
  title: string;
  description: string;
  image: string;
  className?: string;
}

export type CategoryList = readonly Category[];
