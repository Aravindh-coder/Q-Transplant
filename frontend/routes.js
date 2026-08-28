// Route contract for the Q-Transplant SPA. Components should call the backend
// API rather than implementing medical compatibility/ranking locally.
export const ROUTES = Object.freeze({
  public: ['/', '/login', '/register/doctor', '/register/donor', '/register/hospital'],
  doctor: ['/doctor', '/doctor/profile', '/doctor/patients', '/doctor/donors', '/doctor/matching', '/doctor/emergency'],
  donor: ['/donor', '/donor/profile', '/donor/status'],
  hospital: ['/hospital', '/hospital/profile', '/hospital/doctors', '/hospital/patients', '/hospital/matching', '/hospital/emergency'],
  organizer: ['/organizer', '/organizer/users', '/organizer/doctors', '/organizer/approvals', '/organizer/hospitals', '/organizer/donors', '/organizer/patients', '/organizer/matches', '/organizer/emergency', '/organizer/devices', '/organizer/audit'],
});

export function canAccess(role, route) {
  if (ROUTES.public.includes(route)) return true;
  return Object.prototype.hasOwnProperty.call(ROUTES, role) && ROUTES[role].includes(route);
}
