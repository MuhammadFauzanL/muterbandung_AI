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

export interface AiPlannerRequest {
  query?: string;
  filters?: Record<string, unknown>;
  persona_context?: Record<string, unknown>;
  persona_payload?: Record<string, unknown>;
  behaviour_context?: Record<string, unknown>;
  behaviour_payload?: Record<string, unknown>;
  top_k?: number;
  limit?: number;
}

interface ApiPlannerRecommendation extends ApiDestinationCard {
  destination_id?: string | number;
  nama?: string;
  lokasi?: string;
  kategori?: string;
  gambar_url?: string | null;
  harga?: string;
  final_score?: number | null;
  alasan?: string | null;
  media?: { image_url?: string | null };
  info_praktis?: { harga?: string };
}

interface RecommendationApiResponse extends ApiResponse<ApiPlannerRecommendation[]> {
  recommendations?: ApiPlannerRecommendation[];
}

interface AiPlannerApiResponse {
  data?: {
    recommendations?: ApiPlannerRecommendation[];
    meta?: ExploreMeta;
  };
  recommendations?: ApiPlannerRecommendation[];
  meta?: ExploreMeta;
}

function normalizeRecommendationItem(item: ApiPlannerRecommendation): ApiDestinationCard {
  return {
    id: item.id || (item.destination_id !== undefined ? String(item.destination_id) : undefined),
    slug: item.slug,
    name: item.name || item.nama,
    location: item.location || item.lokasi,
    rating: item.rating,
    imageUrl: item.imageUrl || item.gambar_url || item.media?.image_url || null,
    priceLabel: item.priceLabel || item.harga || item.info_praktis?.harga,
    category: item.category || item.kategori,
    primaryIntent: item.primaryIntent,
    durationMinutes: item.durationMinutes,
    openingHoursLabel: item.openingHoursLabel,
    distanceKm: item.distanceKm,
    score: item.score ?? item.final_score,
    scoreReason: item.scoreReason ?? item.alasan,
    scoreBreakdown: item.scoreBreakdown ?? item.score_breakdown,
    score_breakdown: item.score_breakdown ?? item.scoreBreakdown,
  };
}

export const recommendationsService = {
  async getDestinations(
    params: RecommendationQueryParams = {},
  ): Promise<RecommendationResponse> {
    const query = new URLSearchParams();
    query.set('page', String(params.page ?? 1));
    query.set('limit', String(params.limit ?? 12));

    const res = await apiFetch<RecommendationApiResponse>(
      `/recommendations/destinations?${query.toString()}`,
      {
        method: 'GET',
        requireAuth: params.requireAuth ?? false,
      },
    );

    const apiItems = Array.isArray(res.data)
      ? res.data
      : Array.isArray(res.recommendations)
        ? res.recommendations
        : [];

    return {
      data: apiItems.map((item) => mapExploreDestination(normalizeRecommendationItem(item))),
      meta: res.meta || { page: 1, limit: 12, total: 0, totalPages: 0 },
    };
  },

  async getAiPlanner(payload: AiPlannerRequest = {}): Promise<RecommendationResponse> {
    const res = await apiFetch<AiPlannerApiResponse>('/recommendations/ai-planner', {
      method: 'POST',
      body: JSON.stringify(payload),
    });

    const plannerPayload = res.data || res;
    const apiItems = Array.isArray(plannerPayload.recommendations)
      ? plannerPayload.recommendations
      : [];
    const limit = payload.limit ?? payload.top_k ?? apiItems.length;

    return {
      data: apiItems.map((item) => mapExploreDestination(normalizeRecommendationItem(item))),
      meta: plannerPayload.meta || {
        page: 1,
        limit,
        total: apiItems.length,
        totalPages: 1,
      },
    };
  },
};
