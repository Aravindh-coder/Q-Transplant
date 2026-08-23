import { state } from '../state.js';

export function renderSidebar() {
  if (!state.currentUser) return '';

  const active = state.activeTab;
  const role = state.currentUser.role;

  return `
    <nav class="bx--side-nav">
      <ul class="bx--side-nav__items">
        <li>
          <a href="#" data-tab="dashboard" class="bx--side-nav__link ${active === 'dashboard' ? 'active' : ''}">
            <i class="fa-solid fa-chart-line"></i>
            <span>Dashboard</span>
          </a>
        </li>

        <li style="margin-top:10px;padding:4px 12px;font-size:10px;font-weight:700;color:#8d8d8d;letter-spacing:1px;">COMMAND &amp; AI SUITE</li>

        <li>
          <a href="#" data-tab="gis-command" class="bx--side-nav__link ${active === 'gis-command' ? 'active' : ''}">
            <i class="fa-solid fa-earth-asia" style="color:#0f62fe;"></i>
            <span>GIS Command Center</span>
          </a>
        </li>
        <li>
          <a href="#" data-tab="ai-coordinator" class="bx--side-nav__link ${active === 'ai-coordinator' ? 'active' : ''}">
            <i class="fa-solid fa-robot" style="color:#ff6b35;"></i>
            <span>Autonomous AI Coordinator</span>
          </a>
        </li>
        <li>
          <a href="#" data-tab="live-tracking" class="bx--side-nav__link ${active === 'live-tracking' ? 'active' : ''}">
            <i class="fa-solid fa-route" style="color:#00f0ff;"></i>
            <span>Live Transport Tracking</span>
          </a>
        </li>
        <li>
          <a href="#" data-tab="ai-predict" class="bx--side-nav__link ${active === 'ai-predict' ? 'active' : ''}">
            <i class="fa-solid fa-brain" style="color:#8a3ffc;"></i>
            <span>AI Risk Prediction</span>
          </a>
        </li>
        <li>
          <a href="#" data-tab="digital-twin" class="bx--side-nav__link ${active === 'digital-twin' ? 'active' : ''}">
            <i class="fa-solid fa-satellite-dish" style="color:#00b0ff;"></i>
            <span>Digital Twin Transport</span>
          </a>
        </li>
        <li>
          <a href="#" data-tab="blockchain" class="bx--side-nav__link ${active === 'blockchain' ? 'active' : ''}">
            <i class="fa-solid fa-link" style="color:#f1c21b;"></i>
            <span>Blockchain Audit</span>
          </a>
        </li>
        <li>
          <a href="#" data-tab="federated" class="bx--side-nav__link ${active === 'federated' ? 'active' : ''}">
            <i class="fa-solid fa-network-wired" style="color:#42be65;"></i>
            <span>Federated Learning</span>
          </a>
        </li>
        <li>
          <a href="#" data-tab="multi-agent" class="bx--side-nav__link ${active === 'multi-agent' ? 'active' : ''}">
            <i class="fa-solid fa-people-arrows" style="color:#ff7eb6;"></i>
            <span>Multi-Agent System</span>
          </a>
        </li>
        <li>
          <a href="#" data-tab="analytics" class="bx--side-nav__link ${active === 'analytics' ? 'active' : ''}">
            <i class="fa-solid fa-chart-pie" style="color:#be95ff;"></i>
            <span>Research Analytics</span>
          </a>
        </li>
        <li>
          <a href="#" data-tab="slime-mould" class="bx--side-nav__link ${active === 'slime-mould' ? 'active' : ''}">
            <i class="fa-solid fa-bacteria" style="color:#f1c21b;"></i>
            <span>Slime Mould vs Q-SMA</span>
          </a>
        </li>

        <li>
          <a href="#" data-tab="synthetic" class="bx--side-nav__link ${active === 'synthetic' ? 'active' : ''}">
            <i class="fa-solid fa-database" style="color:#42be65;"></i>
            <span>Synthetic Data Lab</span>
          </a>
        </li>
        <li>
          <a href="#" data-tab="documentation" class="bx--side-nav__link ${active === 'documentation' ? 'active' : ''}">
            <i class="fa-solid fa-file-pdf" style="color:#0f62fe;"></i>
            <span>Research &amp; Docs Export</span>
          </a>
        </li>

        <li style="margin-top:10px;padding:4px 12px;font-size:10px;font-weight:700;color:#8d8d8d;letter-spacing:1px;">CORE SERVICES</li>

        ${role === 'organizer' ? `
          <li>
            <a href="#" data-tab="approvals" class="bx--side-nav__link ${active === 'approvals' ? 'active' : ''}">
              <i class="fa-solid fa-user-check"></i>
              <span>User Approvals</span>
            </a>
          </li>
          <li>
            <a href="#" data-tab="audit" class="bx--side-nav__link ${active === 'audit' ? 'active' : ''}">
              <i class="fa-solid fa-shield-halved"></i>
              <span>Audit Logs</span>
            </a>
          </li>
        ` : ''}
        ${['organizer', 'doctor', 'hospital'].includes(role) ? `
          <li>
            <a href="#" data-tab="organs" class="bx--side-nav__link ${active === 'organs' ? 'active' : ''}">
              <i class="fa-solid fa-boxes-packing"></i>
              <span>Organ Registry</span>
            </a>
          </li>
          <li>
            <a href="#" data-tab="matching" class="bx--side-nav__link ${active === 'matching' ? 'active' : ''}">
              <i class="fa-solid fa-dna"></i>
              <span>Grover Match Engine</span>
            </a>
          </li>
          <li>
            <a href="#" data-tab="donor-search" class="bx--side-nav__link ${active === 'donor-search' ? 'active' : ''}">
              <i class="fa-solid fa-magnifying-glass" style="color:#be95ff;"></i>
              <span>Search for Donor</span>
            </a>
          </li>
        ` : ''}
        <li>
          <a href="#" data-tab="telemetry" class="bx--side-nav__link ${active === 'telemetry' ? 'active' : ''}">
            <i class="fa-solid fa-microchip"></i>
            <span>Cold-Box Telemetry</span>
          </a>
        </li>
      </ul>
    </nav>
  `;
}
