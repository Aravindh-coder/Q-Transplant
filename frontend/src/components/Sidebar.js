import { state } from '../state.js';

export function renderSidebar() {
  if (!state.currentUser) return '';
  const active = state.activeTab;
  const role = state.currentUser.role;
  return `
    <nav class="bx--side-nav">
      <ul class="bx--side-nav__items">
        <li><a href="#" data-tab="dashboard" class="bx--side-nav__link ${active === 'dashboard' ? 'active' : ''}"><i class="fa-solid fa-chart-line"></i><span>Dashboard</span></a></li>
        ${role === 'organizer' ? `
          <li><a href="#" data-tab="command-center" class="bx--side-nav__link ${active === 'command-center' ? 'active' : ''}"><i class="fa-solid fa-tower-broadcast"></i><span>Command Center</span></a></li>
          <li><a href="#" data-tab="quantum-lab" class="bx--side-nav__link ${active === 'quantum-lab' ? 'active' : ''}"><i class="fa-solid fa-atom"></i><span>Grover Path Lab</span></a></li>
          <li><a href="#" data-tab="approvals" class="bx--side-nav__link ${active === 'approvals' ? 'active' : ''}"><i class="fa-solid fa-user-check"></i><span>User Approvals</span></a></li>
          <li><a href="#" data-tab="audit" class="bx--side-nav__link ${active === 'audit' ? 'active' : ''}"><i class="fa-solid fa-shield-halved"></i><span>Audit Logs</span></a></li>
        ` : ''}
        ${['organizer', 'doctor', 'hospital'].includes(role) ? `
          <li><a href="#" data-tab="organs" class="bx--side-nav__link ${active === 'organs' ? 'active' : ''}"><i class="fa-solid fa-boxes-packing"></i><span>Organ Registry</span></a></li>
          <li><a href="#" data-tab="matching" class="bx--side-nav__link ${active === 'matching' ? 'active' : ''}"><i class="fa-solid fa-dna"></i><span>Compatibility Matching</span></a></li>
          <li><a href="#" data-tab="donor-search" class="bx--side-nav__link ${active === 'donor-search' ? 'active' : ''}"><i class="fa-solid fa-magnifying-glass"></i><span>Search for Donor</span></a></li>
        ` : ''}
        <li><a href="#" data-tab="telemetry" class="bx--side-nav__link ${active === 'telemetry' ? 'active' : ''}"><i class="fa-solid fa-microchip"></i><span>Cold-Box Telemetry</span></a></li>
        <li><a href="#" data-tab="live-tracking" class="bx--side-nav__link ${active === 'live-tracking' ? 'active' : ''}"><i class="fa-solid fa-route"></i><span>Live Transport Tracking</span></a></li>
      </ul>
    </nav>
  `;
}
