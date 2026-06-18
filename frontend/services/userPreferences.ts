import { apiFetch } from './api';
import type { UserPreference, UserPreferencePayload } from '@/types';

interface ApiResponse<T> {
  data?: T;
}

export const userPreferencesService = {
  async getMine(): Promise<UserPreference | null> {
    const res = await apiFetch<ApiResponse<UserPreference | null>>('/me/preferences', {
      method: 'GET',
      requireAuth: true,
    });
    return res.data || null;
  },

  async saveMine(payload: UserPreferencePayload): Promise<UserPreference> {
    const res = await apiFetch<ApiResponse<UserPreference>>('/me/preferences', {
      method: 'PUT',
      requireAuth: true,
      body: JSON.stringify(payload),
    });
    if (!res.data) {
      throw new Error('Preferensi gagal disimpan.');
    }
    return res.data;
  },
};
