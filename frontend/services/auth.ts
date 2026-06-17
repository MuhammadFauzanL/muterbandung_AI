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

export const authService = {
  /**
   * Register a new user
   */
  async register(name: string, email: string, password: string): Promise<any> {
    return apiFetch('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ name, email, password }),
    });
  },

  /**
   * Login user and get access token
   */
  async login(email: string, password: string): Promise<AuthResponse> {
    const res = await apiFetch<any>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    return res.data || res;
  },

  /**
   * Get current authenticated user profile
   */
  async getMe(): Promise<User> {
    const res = await apiFetch<any>('/auth/me', {
      method: 'GET',
      requireAuth: true,
    });
    return res.data || res;
  },
};
