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

interface ApiErrorBody {
  detail?: unknown;
  message?: unknown;
  errors?: Array<{
    message?: string;
    msg?: string;
  }>;
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

    const data: unknown = await response.json();

    if (!response.ok) {
      const errorBody = data as ApiErrorBody;
      // Backend FastAPI biasanya mengembalikan error di `detail`
      let errorMessage = errorBody.detail || errorBody.message || 'Terjadi kesalahan pada server';
      
      // Jika ada array errors (contoh: validasi FastAPI Pydantic)
      if (errorBody.errors && errorBody.errors.length > 0) {
        const errorDetails = errorBody.errors
          .map((error) => error.message || error.msg || 'Validasi tidak valid')
          .join(', ');
        errorMessage = `${errorMessage}: ${errorDetails}`;
      }

      throw new Error(typeof errorMessage === 'string' ? errorMessage : JSON.stringify(errorMessage));
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
