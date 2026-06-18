import { apiFetch } from './api';

export interface User {
  id: string | number;
  name: string;
  email: string;
  avatar_url?: string;
  created_at?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user?: User;
}

type ApiEnvelope<T> = T | { data: T };

function unwrapData<T>(response: ApiEnvelope<T>): T {
  if (
    typeof response === 'object' &&
    response !== null &&
    'data' in response
  ) {
    return response.data;
  }

  return response;
}

export const authService = {
  /**
   * Register a new user
   */
  async register(name: string, email: string, password: string): Promise<AuthResponse> {
    const res = await apiFetch<ApiEnvelope<AuthResponse>>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ name, email, password }),
    });
    return unwrapData(res);
  },

  /**
   * Login user and get access token
   */
  async login(email: string, password: string): Promise<AuthResponse> {
    const res = await apiFetch<ApiEnvelope<AuthResponse>>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    return unwrapData(res);
  },

  /**
   * Get current authenticated user profile
   */
  async getMe(): Promise<User> {
    const res = await apiFetch<ApiEnvelope<User>>('/auth/me', {
      method: 'GET',
      requireAuth: true,
    });
    return unwrapData(res);
  },
};
