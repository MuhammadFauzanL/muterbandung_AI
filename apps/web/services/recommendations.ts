import { apiFetch } from './api';
import {
  type ApiDestinationCard,
  type ApiResponse,
  mapExploreDestination,
} from './destinations';
import type { ExploreDestination, ExploreMeta } from '@/types';

export interface RecommendationQueryParams {
  page?: number;
  limit?: number;
  requireAuth?: boolean;
}

export interface RecommendationResponse {
  data: ExploreDestination[];
  meta: ExploreMeta;
}

export const recommendationsService = {
  async getDestinations(
    params: RecommendationQueryParams = {},
  ): Promise<RecommendationResponse> {
    const query = new URLSearchParams();
    query.set('page', String(params.page ?? 1));
    query.set('limit', String(params.limit ?? 12));

    const res = await apiFetch<ApiResponse<ApiDestinationCard[]>>(
      `/recommendations/destinations?${query.toString()}`,
      {
        method: 'GET',
        requireAuth: params.requireAuth ?? false,
      },
    );

    return {
      data: (res.data || []).map(mapExploreDestination),
      meta: res.meta || { page: 1, limit: 12, total: 0, totalPages: 0 },
    };
  },
};
