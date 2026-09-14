import Cookies from 'js-cookie';

const API_BASE = '/api/v1';

export function getAuthToken(): string | undefined {
  return Cookies.get('token') || localStorage.getItem('token') || undefined;
}

export function setAuthToken(token: string) {
  Cookies.set('token', token, { expires: 7 });
  localStorage.setItem('token', token);
}

export function clearAuthToken() {
  Cookies.remove('token');
  localStorage.removeItem('token');
}

export async function apiFetch<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = getAuthToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    let errorMsg = `HTTP Error ${res.status}`;
    try {
      const data = await res.json();
      errorMsg = data.error?.message || data.detail || errorMsg;
    } catch (_) {}
    throw new Error(errorMsg);
  }

  return res.json();
}
