/**
 * Base API Service
 * Menyediakan fungsi wrapper untuk native fetch
 * dengan injeksi token otomatis dan error handling dasar.
 */

// Gunakan URL backend langsung agar request AI tidak putus oleh proxy Next dev.
const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface FetchOptions extends RequestInit {
  requireAuth?: boolean;
}

interface ApiErrorBody {
  detail?: unknown;
  message?: unknown;
  errors?: Array<{
    message?: string;
    msg?: string;
  }>;
}

function extractApiErrorMessage(data: unknown, fallback: string): string {
  if (typeof data === 'string') {
    return data || fallback;
  }

  if (data && typeof data === 'object') {
    const errorBody = data as ApiErrorBody;
    let errorMessage = errorBody.detail || errorBody.message || fallback;

    if (errorBody.errors && errorBody.errors.length > 0) {
      const errorDetails = errorBody.errors
        .map((error) => error.message || error.msg || 'Validasi tidak valid')
        .join(', ');
      errorMessage = `${errorMessage}: ${errorDetails}`;
    }

    return typeof errorMessage === 'string' ? errorMessage : JSON.stringify(errorMessage);
  }

  return fallback;
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

  // Bypass Ngrok warning page (development only)
  if (process.env.NODE_ENV === 'development') {
    headers.set('ngrok-skip-browser-warning', 'true');
  }

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

    const contentType = response.headers.get('content-type') || '';
    const rawText = await response.text();
    let data: unknown = {};

    if (rawText) {
      if (contentType.includes('application/json')) {
        try {
          data = JSON.parse(rawText) as unknown;
        } catch {
          data = rawText;
        }
      } else {
        data = rawText;
      }
    }

    if (!response.ok) {
      const errorMessage = extractApiErrorMessage(
        data,
        response.statusText || 'Terjadi kesalahan pada server'
      );

      throw new Error(errorMessage);
    }

    return data as T;
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : String(error);
    
    // Gunakan console.warn untuk 401 agar tidak memicu error overlay merah di Next.js saat token expired
    if (message.includes('Invalid or expired token') || message.includes('Unauthorized') || message.includes('Not authenticated')) {
      console.warn(`API Warn [${options.method || 'GET'} ${endpoint}]:`, message);
    } else {
      console.error(`API Error [${options.method || 'GET'} ${endpoint}]:`, message);
    }
    
    throw error;
  }
}
