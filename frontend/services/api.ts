/**
 * API Client Configuration
 *
 * Base API client setup for communicating with the Flask/FastAPI backend.
 * All API calls should go through this centralized client.
 *
 * Environment variables:
 * - NEXT_PUBLIC_API_BASE_URL: Backend API base URL (default: http://localhost:8000)
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export interface APIClientConfig {
  baseURL: string;
  timeout: number;
  headers: Record<string, string>;
}

export const defaultConfig: APIClientConfig = {
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
};

/**
 * Generic API request handler with error handling
 */
export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${defaultConfig.baseURL}${endpoint}`;

  const config: RequestInit = {
    ...options,
    headers: {
      ...defaultConfig.headers,
      ...options.headers,
    },
  };

  try {
    const response = await fetch(url, config);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({
        error: 'Unknown error',
        message: response.statusText,
        statusCode: response.status,
      }));

      throw new APIError(
        errorData.message || 'Request failed',
        response.status,
        errorData
      );
    }

    return await response.json();
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }

    // Network or parsing errors
    throw new APIError(
      error instanceof Error ? error.message : 'Network request failed',
      0,
      { error: 'NetworkError' }
    );
  }
}

/**
 * Custom API Error class
 */
export class APIError extends Error {
  constructor(
    message: string,
    public statusCode: number,
    public data?: unknown
  ) {
    super(message);
    this.name = 'APIError';
  }
}

/**
 * Helper for GET requests
 */
export async function apiGet<T>(endpoint: string): Promise<T> {
  return apiRequest<T>(endpoint, { method: 'GET' });
}

/**
 * Helper for POST requests
 */
export async function apiPost<T>(
  endpoint: string,
  body: unknown
): Promise<T> {
  return apiRequest<T>(endpoint, {
    method: 'POST',
    body: JSON.stringify(body),
  });
}

/**
 * Helper for PUT requests
 */
export async function apiPut<T>(
  endpoint: string,
  body: unknown
): Promise<T> {
  return apiRequest<T>(endpoint, {
    method: 'PUT',
    body: JSON.stringify(body),
  });
}

/**
 * Helper for DELETE requests
 */
export async function apiDelete<T>(endpoint: string): Promise<T> {
  return apiRequest<T>(endpoint, { method: 'DELETE' });
}
