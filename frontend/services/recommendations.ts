/**
 * Recommendations API Service
 *
 * Handles API calls for destination and package recommendations.
 * Endpoint: POST /api/recommend
 */
import { apiPost } from './api';
import type {
  RecommendationRequest,
  RecommendationResponse,
} from '@/types';

/**
 * Get personalized destination and package recommendations
 *
 * @param request - User preferences and query
 * @returns Recommendations with LLM evidence pack for validation
 */
export async function getRecommendations(
  request: RecommendationRequest
): Promise<RecommendationResponse> {
  return apiPost<RecommendationResponse>('/api/recommend', request);
}

/**
 * Convenience function for quick recommendations without preferences
 */
export async function getQuickRecommendations(
  query: string
): Promise<RecommendationResponse> {
  return getRecommendations({ query });
}
