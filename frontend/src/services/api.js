// API Client Service for Q-Transplant Backend
const API_BASE = '/api/v1';

export class ApiService {
  static getAuthHeaders() {
    const token = localStorage.getItem('access_token');
    return token ? { 'Authorization': `Bearer ${token}` } : {};
  }

  static async request(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...this.getAuthHeaders(),
      ...options.headers
    };

    try {
      const response = await fetch(url, { ...options, headers });
      if (response.status === 401) {
        // Handle token expiration or unauthenticated state
        localStorage.removeItem('access_token');
      }
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'API request failed');
      }
      return data;
    } catch (err) {
      console.error(`API Error [${endpoint}]:`, err);
      throw err;
    }
  }

  // Auth Endpoints
  static async login(email, password) {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
  }

  static async register(userData) {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData)
    });
  }

  static async getMe() {
    return this.request('/auth/me');
  }

  // Admin User Approvals
  static async getPendingApprovals() {
    return this.request('/users/pending-approvals');
  }

  static async approveUser(userId, approve = true, reason = '') {
    return this.request('/users/approve', {
      method: 'POST',
      body: JSON.stringify({ user_id: userId, approve, reason })
    });
  }

  static async getAllUsersDetailed() {
    return this.request('/users/all-detailed');
  }

  static async postEmergencyAlert(payload) {
    return this.request('/emergency/', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  // Organs & Matching
  static async getOrgans() {
    return this.request('/organs/');
  }

  static async registerOrgan(organData) {
    return this.request('/organs/', {
      method: 'POST',
      body: JSON.stringify(organData)
    });
  }

  static async computeMatches(organId) {
    return this.request(`/matches/compute/${organId}`, {
      method: 'POST'
    });
  }

  static async getMatches() {
    return this.request('/matches/');
  }

  static async approveMatch(matchId) {
    return this.request(`/matches/${matchId}/approve`, {
      method: 'POST'
    });
  }

  // Telemetry
  static async getLatestTelemetry(boxId) {
    return this.request(`/telemetry/${boxId}/latest`);
  }

  static async pushTelemetry(telemetryData) {
    return this.request('/telemetry/push', {
      method: 'POST',
      body: JSON.stringify(telemetryData)
    });
  }

  // Audit Logs
  static async getAuditLogs() {
    return this.request('/audit/logs');
  }
}
