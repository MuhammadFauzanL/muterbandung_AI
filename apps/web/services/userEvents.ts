/**
 * User Event Tracking Service
 *
 * Fire-and-forget event recording for behavioral profiling.
 * All functions silently catch errors — event tracking should
 * never interrupt the user experience.
 */

import { apiFetch } from './api';

export type EventType =
  | 'search'
  | 'filter_apply'
  | 'view_detail'
  | 'favorite_add'
  | 'favorite_remove'
  | 'planner_add';

interface TrackEventPayload {
  event_type: EventType;
  destination_id?: string | null;
  metadata?: Record<string, unknown> | null;
}

/** Core event tracking — fire-and-forget */
async function sendEvent(payload: TrackEventPayload): Promise<void> {
  try {
    await apiFetch('/me/events', {
      method: 'POST',
      requireAuth: true,
      body: JSON.stringify(payload),
    });
  } catch {
    // Silently fail — event tracking should never block UX
  }
}

/** Check if user is logged in (has a token) */
function hasToken(): boolean {
  if (typeof window === 'undefined') return false;
  return !!localStorage.getItem('muterbandung_token');
}

// ── Convenience helpers ──────────────────────────────────

/** Track a search query */
export function trackSearch(query: string): void {
  if (!hasToken() || !query.trim()) return;
  void sendEvent({
    event_type: 'search',
    metadata: { query: query.trim() },
  });
}

/** Track filter application */
export function trackFilterApply(
  filters: Record<string, unknown>,
): void {
  if (!hasToken()) return;
  void sendEvent({
    event_type: 'filter_apply',
    metadata: filters,
  });
}

/** Track detail page view */
export function trackViewDetail(destinationId: string): void {
  if (!hasToken() || !destinationId) return;
  void sendEvent({
    event_type: 'view_detail',
    destination_id: destinationId,
  });
}

/** Track planner add */
export function trackPlannerAdd(destinationId: string): void {
  if (!hasToken() || !destinationId) return;
  void sendEvent({
    event_type: 'planner_add',
    destination_id: destinationId,
  });
}

/** Track favorite add (called internally by FavoriteContext) */
export function trackFavoriteAdd(destinationId: string): void {
  if (!hasToken() || !destinationId) return;
  void sendEvent({
    event_type: 'favorite_add',
    destination_id: destinationId,
  });
}

/** Track favorite remove (called internally by FavoriteContext) */
export function trackFavoriteRemove(destinationId: string): void {
  if (!hasToken() || !destinationId) return;
  void sendEvent({
    event_type: 'favorite_remove',
    destination_id: destinationId,
  });
}
