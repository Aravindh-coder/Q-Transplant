import { state } from '../state.js';
import { renderTelemetryGauge } from '../components/TelemetryGauge.js';

export function renderDashboardAdmin() {
  return `
    <div>
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
        <div>
          <h1 style="font-size: 1.75rem; font-weight: 300;">Organizer Executive Dashboard</h1>
          <p style="color: var(--cds-text-02); font-size: 13px;">System Governance & Real-Time Cold-Chain Telemetry</p>
        </div>
        <div>
          <button id="btn-refresh-data" class="bx--btn bx--btn--ghost">
            <i class="fa-solid fa-rotate-right"></i> Refresh System State
          </button>
        </div>
      </div>

      <!-- Overview Metric Cards -->
      <div class="bx--grid" style="grid-template-columns: repeat(4, 1fr); margin-bottom: 1.5rem;">
        <div class="bx--tile">
          <div class="bx--tile__heading"><i class="fa-solid fa-heart"></i> AVAILABLE ORGANS</div>
          <div class="bx--tile__value">${state.organs.length || 1}</div>
        </div>
        <div class="bx--tile">
          <div class="bx--tile__heading"><i class="fa-solid fa-user-clock"></i> PENDING APPROVALS</div>
          <div class="bx--tile__value" style="color: var(--cds-support-warning);">${state.pendingUsers.length || 0}</div>
        </div>
        <div class="bx--tile">
          <div class="bx--tile__heading"><i class="fa-solid fa-truck-medical"></i> DISPATCHED AMBULANCES</div>
          <div class="bx--tile__value">1</div>
        </div>
        <div class="bx--tile">
          <div class="bx--tile__heading"><i class="fa-solid fa-temperature-three-quarters"></i> ACTIVE COLD-BOXES</div>
          <div class="bx--tile__value" style="color: var(--cds-teal-40);">1</div>
        </div>
      </div>

      <!-- Cold-Box Telemetry Gauge Component -->
      <div style="margin-bottom: 1.5rem;">
        ${renderTelemetryGauge(state.telemetry)}
      </div>

      <div class="bx--grid" style="grid-template-columns: repeat(12, 1fr); margin-bottom: 1.5rem;">
        <!-- Live GPS Map Tracking -->
        <div class="bx--tile" style="grid-column: span 8;">
          <div class="bx--tile__heading"><i class="fa-solid fa-map-location-dot"></i> REAL-TIME GPS TRANSPORT TRACKER</div>
          <div id="leaflet-map" style="margin-top: 8px;"></div>
        </div>

        <!-- Pending Approvals Widget -->
        <div class="bx--tile" style="grid-column: span 4;">
          <div class="bx--tile__heading"><i class="fa-solid fa-user-shield"></i> PENDING USER REGISTRATIONS</div>
          <div id="pending-users-list" style="margin-top: 8px; max-height: 350px; overflow-y: auto;">
            ${state.pendingUsers.length === 0 ? `
              <div style="padding: 1rem; color: var(--cds-text-03); text-align: center;">No pending account requests</div>
            ` : state.pendingUsers.map(u => `
              <div style="padding: 10px; background: var(--cds-layer-02); border-bottom: 1px solid var(--cds-border-subtle); margin-bottom: 6px;">
                <div style="font-weight: 600; color: var(--cds-text-01);">${u.full_name}</div>
                <div style="font-size: 11px; color: var(--cds-text-02);">${u.email} | <span style="text-transform: uppercase;">${u.role}</span></div>
                <div style="margin-top: 8px; display: flex; gap: 8px;">
                  <button class="bx--btn bx--btn--primary btn-approve-user" data-id="${u.id}" style="padding: 4px 8px; font-size: 11px;">Approve</button>
                  <button class="bx--btn bx--btn--ghost btn-reject-user" data-id="${u.id}" style="padding: 4px 8px; font-size: 11px; color: var(--cds-support-error);">Reject</button>
                </div>
              </div>
            `).join('')}
          </div>
        </div>
      </div>

      <!-- Audit Logs Table -->
      <div class="bx--tile">
        <div class="bx--tile__heading"><i class="fa-solid fa-list-check"></i> SYSTEM AUDIT TRAIL</div>
        <table class="bx--data-table" style="margin-top: 8px;">
          <thead>
            <tr>
              <th>ID</th>
              <th>TIMESTAMP</th>
              <th>ACTION</th>
              <th>RESOURCE</th>
              <th>DETAILS</th>
            </tr>
          </thead>
          <tbody>
            ${state.auditLogs.slice(0, 5).map(log => `
              <tr>
                <td style="font-family: var(--cds-mono-font);">${log.id}</td>
                <td style="font-size: 12px;">${new Date(log.timestamp).toLocaleTimeString()}</td>
                <td><span class="bx--tag bx--tag--blue">${log.action}</span></td>
                <td>${log.resource}</td>
                <td style="font-size: 12px;">${log.details || '-'}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    </div>
  `;
}
