import { state } from '../state.js';
import { renderAIAssistant } from '../components/AIAssistant.js';

export function renderDashboardDoctor() {
  return `
    <div>
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
        <div>
          <h1 style="font-size: 1.75rem; font-weight: 300;">Doctor Transplant Portal</h1>
          <p style="color: var(--cds-text-02); font-size: 13px;">Transplant Surgery Unit & Recipient Compatibility</p>
        </div>
        <div>
          <button id="btn-register-organ-modal" class="bx--btn bx--btn--primary">
            <i class="fa-solid fa-plus"></i> Register Donated Organ
          </button>
        </div>
      </div>

      <!-- Overview Cards -->
      <div class="bx--grid" style="grid-template-columns: repeat(4, 1fr); margin-bottom: 1.5rem;">
        <div class="bx--tile">
          <div class="bx--tile__heading"><i class="fa-solid fa-hospital-user"></i> ASSIGNED PATIENTS</div>
          <div class="bx--tile__value">1</div>
        </div>
        <div class="bx--tile">
          <div class="bx--tile__heading"><i class="fa-solid fa-heart-pulse"></i> AVAILABLE ORGANS</div>
          <div class="bx--tile__value" style="color: var(--cds-support-success);">${state.organs.length || 1}</div>
        </div>
        <div class="bx--tile">
          <div class="bx--tile__heading"><i class="fa-solid fa-dna"></i> MATCH COMPUTATIONS</div>
          <div class="bx--tile__value">${state.matches.length || 1}</div>
        </div>
        <div class="bx--tile">
          <div class="bx--tile__heading"><i class="fa-solid fa-clock-rotate-left"></i> ACTIVE TRANSPLANTS</div>
          <div class="bx--tile__value" style="color: var(--cds-teal-40);">1</div>
        </div>
      </div>

      <!-- Integrated AI Assistant Widget -->
      <div style="margin-bottom: 1.5rem;">
        ${renderAIAssistant()}
      </div>

      <!-- Organ Registry & Match Execution Table -->
      <div class="bx--tile" style="margin-bottom: 1.5rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
          <span class="bx--tile__heading"><i class="fa-solid fa-boxes-packing"></i> DONATED ORGAN REGISTRY</span>
          <a href="/api/v1/reports/export/organs" target="_blank" class="bx--btn bx--btn--ghost" style="font-size: 11px;">
            <i class="fa-solid fa-file-csv"></i> Export CSV Report
          </a>
        </div>
        <table class="bx--data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>ORGAN TYPE</th>
              <th>BLOOD TYPE</th>
              <th>HLA ANTIMATCH</th>
              <th>COLD-BOX SENSOR ID</th>
              <th>STATUS</th>
              <th>QUANTUM MATCH ACTION</th>
            </tr>
          </thead>
          <tbody>
            ${state.organs.length === 0 ? `
              <tr><td colspan="7" style="text-align: center; color: var(--cds-text-03);">No organs registered</td></tr>
            ` : state.organs.map(o => `
              <tr>
                <td style="font-family: var(--cds-mono-font);">${o.id}</td>
                <td><strong>${o.organ_type.toUpperCase()}</strong></td>
                <td><span class="bx--tag bx--tag--red">${o.blood_type}</span></td>
                <td style="font-family: var(--cds-mono-font);">${o.hla_type}</td>
                <td style="font-family: var(--cds-mono-font);">${o.cold_box_id}</td>
                <td><span class="bx--tag bx--tag--green">${o.status.toUpperCase()}</span></td>
                <td>
                  <button class="bx--btn bx--btn--primary btn-compute-quantum-match" data-id="${o.id}" style="padding: 4px 10px; font-size: 11px;">
                    <i class="fa-solid fa-wand-magic-sparkles"></i> Compute Quantum Matches
                  </button>
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    </div>
  `;
}
