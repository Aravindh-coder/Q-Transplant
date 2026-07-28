// Global Application State Manager
export const state = {
  currentUser: null,
  activeTab: 'dashboard',
  theme: localStorage.getItem('theme') || 'dark',
  telemetry: {
    cold_box_id: 'BOX-ESP32-001',
    temp_celsius: 4.2,
    humidity_percent: 82.0,
    battery_level: 95.0,
    lat: 12.9716,
    lng: 77.5946,
    status: 'Nominal'
  },
  organs: [],
  matches: [],
  pendingUsers: [],
  auditLogs: []
};

export const listeners = new Set();

export function subscribe(fn) {
  listeners.add(fn);
  return () => listeners.delete(fn);
}

export function notifyStateChange() {
  listeners.forEach(fn => fn(state));
}

export function setTheme(newTheme) {
  state.theme = newTheme;
  localStorage.setItem('theme', newTheme);
  document.documentElement.setAttribute('data-theme', newTheme);
  notifyStateChange();
}

export function setCurrentUser(user) {
  state.currentUser = user;
  notifyStateChange();
}

export function setActiveTab(tab) {
  state.activeTab = tab;
  notifyStateChange();
}
