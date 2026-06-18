/**
 * User Favorites API Service
 *
 * Handles CRUD operations for user favorites.
 */

import { apiFetch } from './api';
import {
  type ApiDestinationCard,
  type ApiResponse,
  mapExploreDestination,
} from './destinations';
import type { ExploreDestination, ExploreMeta } from '@/types';

export interface FavoriteListResponse {
  data: ExploreDestination[];
  meta: ExploreMeta;
}

export const userFavoritesService = {
  /** Get paginated list of user's favorited destinations */
  async getFavorites(
    page: number = 1,
    limit: number = 12,
  ): Promise<FavoriteListResponse> {
    const query = new URLSearchParams();
    query.set('page', String(page));
    query.set('limit', String(limit));

    const res = await apiFetch<ApiResponse<ApiDestinationCard[]>>(
      `/me/favorites?${query.toString()}`,
      { method: 'GET', requireAuth: true },
    );

    return {
      data: (res.data || []).map((item) => ({
        ...mapExploreDestination(item),
        isFavorite: true, // everything in favorites list is favorited
      })),
      meta: res.meta || { page: 1, limit: 12, total: 0, totalPages: 0 },
    };
  },

  /** Add a destination to favorites (idempotent) */
  async addFavorite(destinationId: string): Promise<void> {
    await apiFetch(`/me/favorites/${destinationId}`, {
      method: 'POST',
      requireAuth: true,
    });
  },

  /** Remove a destination from favorites */
  async removeFavorite(destinationId: string): Promise<void> {
    await apiFetch(`/me/favorites/${destinationId}`, {
      method: 'DELETE',
      requireAuth: true,
    });
  },

  /** Get list of favorited destination IDs (for quick lookup) */
  async getFavoriteIds(): Promise<Set<string>> {
    // Fetch all favorites (up to 200 for ID lookup)
    const res = await apiFetch<ApiResponse<ApiDestinationCard[]>>(
      '/me/favorites?limit=200',
      { method: 'GET', requireAuth: true },
    );
    return new Set((res.data || []).map((item) => item.id).filter((id): id is string => !!id));
  },
};
