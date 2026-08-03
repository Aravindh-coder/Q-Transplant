import { state } from '../state.js';
import { renderQRBadge } from '../components/QRBadge.js';

export function renderDashboardDonor() {
  const user = state.currentUser || { full_name: 'David Miller' };

  return `
    <div style="padding:0 0.5rem;">
      <!-- Header -->
      <div class="dash-header" style="margin-bottom:2rem; display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:1rem;">
        <div>
          <div class="section-badge" style="background:rgba(25,128,56,0.15); border-color:rgba(25,128,56,0.4); color:#42be65;">
            <i class="fa-solid fa-hand-holding-heart"></i> VERIFIED ORGAN DONOR PORTAL
          </div>
          <h1 class="dash-title" style="margin-top:6px;">Digital Organ Life Passport &amp; Donor Pledge</h1>
          <p class="dash-subtitle">Registered Life Donor: <strong style="color:#f4f4f4;">${user.full_name}</strong> &nbsp;·&nbsp; NOTTO Donor ID: #DNR-2026-9041</p>
        </div>
      </div>

      <!-- Donor Pledge Summary + QR Passport -->
      <div style="display:grid; grid-template-columns: 8fr 4fr; gap:1.5rem; margin-bottom:2rem;">
        <div class="problem-card green" style="margin:0;">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1.5rem;">
            <h3 style="color:#42be65; margin:0; font-size:16px;"><i class="fa-solid fa-id-card"></i> Official Pledged Organ Donor Pass</h3>
            <span class="ticker-badge badge-matched"><i class="fa-solid fa-circle-check"></i> VERIFIED & ACTIVE</span>
          </div>

          <div style="display:flex; flex-direction:column; gap:12px; font-size:13px;">
            <div style="display:flex; justify-content:space-between; border-bottom:1px solid #393939; padding-bottom:8px;">
              <span style="color:#8d8d8d;">PLEDGED DONOR NAME</span>
              <strong style="color:#f4f4f4;">${user.full_name}</strong>
            </div>
            <div style="display:flex; justify-content:space-between; border-bottom:1px solid #393939; padding-bottom:8px;">
              <span style="color:#8d8d8d;">BLOOD TYPE</span>
              <span class="ticker-badge badge-critical" style="background:#da1e28; color:#fff;">O POSITIVE (O+)</span>
            </div>
            <div style="display:flex; justify-content:space-between; border-bottom:1px solid #393939; padding-bottom:8px;">
              <span style="color:#8d8d8d;">HLA GENETIC MARKERS</span>
              <span style="font-family:'IBM Plex Mono'; color:#be95ff; font-weight:700;">A2, B7, DR4</span>
            </div>
            <div style="display:flex; justify-content:space-between; border-bottom:1px solid #393939; padding-bottom:8px;">
              <span style="color:#8d8d8d;">PLEDGED ORGANS FOR DONATION</span>
              <span style="color:#42be65; font-weight:600;">Heart, Kidney, Cornea, Liver</span>
            </div>
            <div style="display:flex; justify-content:space-between;">
              <span style="color:#8d8d8d;">QUANTUM ALLOCATION MATRIX STATUS</span>
              <span style="color:#78a9ff; font-weight:600;"><i class="fa-solid fa-atom"></i> READY FOR GROVER SEARCH</span>
            </div>
          </div>
        </div>

        <div>
          ${renderQRBadge('QR-DONOR-O-PLUS-001', user.full_name)}
        </div>
      </div>

      <!-- Register Donated Organ Form -->
      <div class="problem-card blue" style="margin:0; padding:2rem;">
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:1.25rem;">
          <i class="fa-solid fa-hand-holding-medical" style="font-size:2rem; color:#78a9ff;"></i>
          <div>
            <h3 style="font-size:16px; font-weight:700; color:#f4f4f4; margin:0;">Register Organ Availability into Quantum Network</h3>
            <p style="font-size:12px; color:#8d8d8d; margin:2px 0 0 0;">Submitting an available organ triggers Grover's Quantum algorithm to find the ideal matched patient in seconds.</p>
          </div>
        </div>

        <form id="form-donor-register-organ">
          <div class="organ-form-grid" style="margin-bottom:1rem;">
            <div class="form-group">
              <label style="color:#8d8d8d;">Organ Type</label>
              <select id="donor-organ-type" required style="width:100%; background:#262626; color:#fff; border:1px solid #393939; padding:10px; border-radius:6px; font-size:13px;">
                <option value="Heart">Heart (Cardiac)</option>
                <option value="Kidney">Kidney (Renal)</option>
                <option value="Liver">Liver (Hepatic)</option>
                <option value="Lung">Lung (Pulmonary)</option>
                <option value="Pancreas">Pancreas</option>
              </select>
            </div>

            <div class="form-group">
              <label style="color:#8d8d8d;">Blood Group</label>
              <select id="donor-blood-type" required style="width:100%; background:#262626; color:#fff; border:1px solid #393939; padding:10px; border-radius:6px; font-size:13px;">
                <option value="O+">O Positive (O+)</option>
                <option value="A+">A Positive (A+)</option>
                <option value="B+">B Positive (B+)</option>
                <option value="AB+">AB Positive (AB+)</option>
                <option value="O-">O Negative (O-)</option>
              </select>
            </div>

            <div class="form-group">
              <label style="color:#8d8d8d;">HLA Antigen Markers</label>
              <input type="text" id="donor-hla-type" value="A2,B7,DR4" required style="width:100%; background:#262626; color:#fff; border:1px solid #393939; padding:10px; border-radius:6px; font-size:13px;" />
            </div>

            <div class="form-group">
              <label style="color:#8d8d8d;">Max Cold Ischemia Hours</label>
              <input type="number" id="donor-ischemia-hours" value="4.0" step="0.5" min="1" max="24" required style="width:100%; background:#262626; color:#fff; border:1px solid #393939; padding:10px; border-radius:6px; font-size:13px;" />
            </div>
          </div>

          <button type="submit" class="btn-register-organ" id="btn-submit-donor-organ" style="margin:0;">
            <i class="fa-solid fa-heart-pulse"></i>
            REGISTER ORGAN INTO GROVER QUANTUM MATCH DATABASE
          </button>
        </form>
      </div>
    </div>
  `;
}
