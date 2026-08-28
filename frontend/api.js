// Frontend transport layer. Business/medical decisions stay in the backend.
export const API_BASE = (localStorage.getItem('qt_api') || 'http://localhost:9900').replace(/\/$/, '');

export async function api(path, options = {}) {
  const headers = { ...(options.body instanceof FormData ? {} : { 'Content-Type': 'application/json' }), ...(options.headers || {}) };
  const token = localStorage.getItem('qt_token');
  if (token) headers.Authorization = `Bearer ${token}`;
  const response = await fetch(`${API_BASE}${path}`, { ...options, headers });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || data.message || 'Request failed');
  return data;
}

export const auth = {
  login: (email, password) => api('/api/v1/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) }),
  register: (payload) => api('/api/v1/auth/register', { method: 'POST', body: JSON.stringify(payload) }),
  logout: () => api('/api/v1/auth/logout', { method: 'POST' }),
  forgotPassword: (email) => api('/api/v1/auth/forgot-password', { method: 'POST', body: JSON.stringify({ email }) }),
  resetPassword: (payload) => api('/api/v1/auth/reset-password', { method: 'POST', body: JSON.stringify(payload) }),
  verifyEmail: (payload) => api('/api/v1/auth/verify-email', { method: 'POST', body: JSON.stringify(payload) }),
};
