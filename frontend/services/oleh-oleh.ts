/**
 * Oleh-Oleh (Souvenirs) API Service
 *
 * Handles API calls for Bandung souvenir recommendations.
 * Endpoint: POST /api/oleh-oleh/recommend
 */
import { apiPost } from './api';
import type { OlehOlehRequest, OlehOlehResponse } from '@/types';

/**
 * Get Bandung souvenir recommendations
 *
 * @param request - Search query and filters
 * @returns Oleh-oleh products with LLM evidence pack
 */
export async function getOlehOlehRecommendations(
  request: OlehOlehRequest
): Promise<OlehOlehResponse> {
  return apiPost<OlehOlehResponse>('/api/oleh-oleh/recommend', request);
}

/**
 * Convenience function for simple souvenir search
 */
export async function searchOlehOleh(
  query: string
): Promise<OlehOlehResponse> {
  return getOlehOlehRecommendations({ query });
}
