import { state } from '../state.js';
import { renderQRBadge } from '../components/QRBadge.js';

export function renderDashboardDonor() {
  const user = state.currentUser || { full_name: 'David Miller' };

  return `
    <div>
      <div class="dash-header">
        <div>
          <h1 class="dash-title"><i class="fa-solid fa-hand-holding-heart" style="color:#198038;margin-right:8px;"></i>Organ Donor Pledge Portal</h1>
          <p class="dash-subtitle">Donation Verification & Digital Life Passport · Donor: <strong>${user.full_name}</strong></p>
        </div>
      </div>

      <!-- Donor Pledge Summary + QR Passport -->
      <div class="bx--grid" style="grid-template-columns: repeat(12, 1fr); gap:1.5rem; margin-bottom: 2rem;">
        <div class="bx--tile" style="grid-column: span 8; background: rgba(38,38,38,0.6); border-radius:12px;">
          <div class="bx--tile__heading"><i class="fa-solid fa-id-card"></i> PLEDGED DONOR PROFILE DETAILS</div>
          <div style="margin-top: 1.5rem; display: flex; flex-direction: column; gap: 14px;">
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid var(--cds-border-subtle); padding-bottom: 8px;">
              <span style="color: var(--cds-text-02);">DONOR NAME</span>
              <strong>${user.full_name}</strong>
            </div>
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid var(--cds-border-subtle); padding-bottom: 8px;">
              <span style="color: var(--cds-text-02);">REGISTERED BLOOD GROUP</span>
              <span class="bx--tag bx--tag--red">O POSITIVE</span>
            </div>
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid var(--cds-border-subtle); padding-bottom: 8px;">
              <span style="color: var(--cds-text-02);">HLA ANTIMATCH MARKERS</span>
              <span style="font-family: var(--cds-mono-font);">A2, B7, DR4</span>
            </div>
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid var(--cds-border-subtle); padding-bottom: 8px;">
              <span style="color: var(--cds-text-02);">PLEDGE VERIFICATION</span>
              <span class="bx--tag bx--tag--green">VERIFIED & ACTIVE</span>
            </div>
          </div>
        </div>

        <div style="grid-column: span 4;">
          ${renderQRBadge('QR-DONOR-O-PLUS-001', user.full_name)}
        </div>
      </div>

      <!-- REGISTER DONATED ORGAN FORM (FIXED FUNCTIONALITY) -->
      <div class="ultra-table-wrap" style="padding: 2rem; background: rgba(38,38,38,0.6); border-radius: 12px;">
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:1rem;">
          <i class="fa-solid fa-plus-circle" style="font-size:1.5rem; color:#42be65;"></i>
          <div>
            <h3 style="font-size:16px; font-weight:600; color:#f4f4f4;">Register Donated Organ Pledge</h3>
            <p style="font-size:12px; color:#8d8d8d;">Submit an available donated organ record to enter into Grover's Quantum Matching search.</p>
          </div>
        </div>

        <form id="form-donor-register-organ">
          <div class="organ-form-grid">
            <div class="form-group">
              <label>Organ Type</label>
              <select id="donor-organ-type" required>
                <option value="Heart">Heart (Cardiac)</option>
                <option value="Kidney">Kidney (Renal)</option>
                <option value="Liver">Liver (Hepatic)</option>
                <option value="Lung">Lung (Pulmonary)</option>
                <option value="Pancreas">Pancreas</option>
              </select>
            </div>

            <div class="form-group">
              <label>Blood Group</label>
              <select id="donor-blood-type" required>
                <option value="O+">O Positive</option>
                <option value="A+">A Positive</option>
                <option value="B+">B Positive</option>
                <option value="AB+">AB Positive</option>
                <option value="O-">O Negative</option>
              </select>
            </div>

            <div class="form-group">
              <label>HLA Markers</label>
              <input type="text" id="donor-hla-type" value="A2,B7,DR4" required />
            </div>

            <div class="form-group">
              <label>Max Ischemia Viability Hours</label>
              <input type="number" id="donor-ischemia-hours" value="4.0" step="0.5" min="1" max="24" required />
            </div>
          </div>

          <button type="submit" class="btn-register-organ" id="btn-submit-donor-organ">
            <i class="fa-solid fa-hand-holding-heart"></i>
            REGISTER DONATED ORGAN INTO QUANTUM DATABASE
          </button>
        </form>
      </div>
    </div>
  `;
}
