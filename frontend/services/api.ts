/**
 * Base API Service
 * Menyediakan fungsi wrapper untuk native fetch
 * dengan injeksi token otomatis dan error handling dasar.
 */

// Gunakan URL absolut di sisi server (Server Components), dan /api di client (Client Components)
const BASE_URL = typeof window === 'undefined' 
  ? (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000') 
  : '/api';

interface FetchOptions extends RequestInit {
  requireAuth?: boolean;
}

export async function apiFetch<T>(
  endpoint: string,
  options: FetchOptions = {}
): Promise<T> {
  const { requireAuth = false, headers: customHeaders, ...customOptions } = options;
  
  const headers = new Headers(customHeaders);
  
  // Default content type is JSON if not provided and it's not a FormData
  if (!headers.has('Content-Type') && !(customOptions.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }

  // Bypass Ngrok warning page
  headers.set('ngrok-skip-browser-warning', 'true');

  // Inject token if required
  if (requireAuth) {
    const token = typeof window !== 'undefined' ? localStorage.getItem('muterbandung_token') : null;
    if (token) {
      headers.set('Authorization', `Bearer ${token}`);
    }
  }

  const url = `${BASE_URL}${endpoint}`;

  try {
    const response = await fetch(url, {
      ...customOptions,
      headers,
    });

    // Jika response 204 No Content
    if (response.status === 204) {
      return {} as T;
    }

    const data = await response.json();

    if (!response.ok) {
      // Backend FastAPI biasanya mengembalikan error di `detail`
      const errorMessage = data.detail || data.message || 'Terjadi kesalahan pada server';
      throw new Error(typeof errorMessage === 'string' ? errorMessage : JSON.stringify(errorMessage));
    }

    return data as T;
  } catch (error: any) {
    console.error(`API Error [${options.method || 'GET'} ${endpoint}]:`, error.message);
    throw error;
  }
}
