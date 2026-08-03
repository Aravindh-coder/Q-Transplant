import { state } from '../state.js';

export function renderDashboardDoctor() {
  const user = state.currentUser || { full_name: 'Dr. Rajesh Kumar', is_approved: true };
  const isApproved = user.is_approved !== false;

  return `
    <div style="padding: 0 0.5rem;">
      <!-- Header -->
      <div class="dash-header" style="margin-bottom: 2rem; display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1rem;">
        <div>
          <div class="section-badge" style="background: rgba(138,63,252,0.15); border-color: rgba(138,63,252,0.4); color: #be95ff;">
            <i class="fa-solid fa-user-doctor"></i> SURGEON CLINICAL PORTAL
          </div>
          <h1 class="dash-title" style="margin-top: 6px;">Transplant Surgeon Command Center</h1>
          <p class="dash-subtitle">Attending Surgeon: <strong style="color:#f4f4f4;">${user.full_name}</strong> &nbsp;·&nbsp; Department of Cardiothoracic & Organ Allocation</p>
        </div>
        <div style="display: flex; gap: 10px;">
          <a href="#" data-tab="matching" class="btn-hero-primary" style="font-size: 13px; padding: 10px 18px; text-decoration: none;">
            <i class="fa-solid fa-atom"></i> Execute Grover Match
          </a>
        </div>
      </div>

      ${!isApproved ? `
        <!-- Doctor Registration Pending Notice -->
        <div class="problem-card red" style="margin-bottom: 2rem; border-color: #da1e28; background: rgba(218,30,40,0.08);">
          <div style="display: flex; gap: 1rem; align-items: center;">
            <i class="fa-solid fa-clock-rotate-left" style="font-size: 2.5rem; color: #ff8389;"></i>
            <div>
              <h3 style="color: #ff8389; margin-bottom: 4px;">Account Verification Pending Approval</h3>
              <p style="color: #c6c6c6; font-size: 13px; margin: 0;">
                Your medical license credentials, live biometric photo, and surgical certifications have been securely uploaded and dispatched to the Lead Organizer (<strong>aravindhjoshua10@gmail.com</strong>).
              </p>
            </div>
          </div>
        </div>
      ` : ''}

      <!-- Doctor Clinical KPIs -->
      <div class="kpi-grid" style="margin-bottom: 2rem;">
        <div class="kpi-card purple">
          <div class="kpi-card-label"><i class="fa-solid fa-heart-pulse" style="color:#be95ff;"></i> Active Organs Registered</div>
          <div class="kpi-card-value" style="color:#be95ff;">14</div>
          <div class="kpi-card-sub">Validated for Quantum Matching</div>
        </div>
        <div class="kpi-card green">
          <div class="kpi-card-label"><i class="fa-solid fa-clipboard-check" style="color:#42be65;"></i> Successful Surgeries</div>
          <div class="kpi-card-value" style="color:#42be65;">128</div>
          <div class="kpi-card-sub">100% 1-Year Patient Survival</div>
        </div>
        <div class="kpi-card blue">
          <div class="kpi-card-label"><i class="fa-solid fa-atom" style="color:#78a9ff;"></i> Grover Match Accuracy</div>
          <div class="kpi-card-value" style="color:#78a9ff;">99.98%</div>
          <div class="kpi-card-sub">HLA & Blood Compatibility</div>
        </div>
        <div class="kpi-card yellow">
          <div class="kpi-card-label"><i class="fa-solid fa-snowflake" style="color:#f1c21b;"></i> Ischemia Viability Avg</div>
          <div class="kpi-card-value" style="color:#f1c21b;">98.4%</div>
          <div class="kpi-card-sub">Cold-Box Temperature: 4.2°C</div>
        </div>
      </div>

      <!-- Main Portal Grid -->
      <div style="display: grid; grid-template-columns: 7fr 5fr; gap: 1.5rem; margin-bottom: 2rem;">
        <!-- Left: Active Clinical Organ Allocation Queue -->
        <div class="ultra-table-wrap">
          <div class="ultra-table-header">
            <div class="ultra-table-title"><i class="fa-solid fa-list-check" style="color:#0f62fe; margin-right:8px;"></i> Active Surgical Dispatch & Allocation Queue</div>
            <span style="font-size:11px; color:#42be65; font-weight:700;"><i class="fa-solid fa-circle-dot"></i> REAL-TIME SYNC</span>
          </div>
          <table class="utbl">
            <thead>
              <tr>
                <th>Patient ID</th>
                <th>Required Organ</th>
                <th>Blood / HLA</th>
                <th>Hospital</th>
                <th>Ischemia Risk</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>PT-2026-8812</strong></td>
                <td><span style="color:#ff8389; font-weight:700;">Heart</span></td>
                <td>O+ / A2,B7,DR4</td>
                <td>Apollo Specialty</td>
                <td><span class="ticker-badge badge-critical">CRITICAL (3.2h)</span></td>
                <td>
                  <button class="btn-call" style="padding:4px 10px; font-size:11px;" onclick="alert('Dispatching Surgical Transport Team for Patient PT-2026-8812...')">
                    <i class="fa-solid fa-truck-medical"></i> Dispatch
                  </button>
                </td>
              </tr>
              <tr>
                <td><strong>PT-2026-9041</strong></td>
                <td><span style="color:#78a9ff; font-weight:700;">Kidney</span></td>
                <td>A+ / A1,B8,DR3</td>
                <td>Fortis Bengaluru</td>
                <td><span class="ticker-badge badge-searching">MEDIUM (12h)</span></td>
                <td>
                  <button class="btn-call" style="padding:4px 10px; font-size:11px;" onclick="alert('Preparing Donor Allocation Match...')">
                    <i class="fa-solid fa-dna"></i> Match
                  </button>
                </td>
              </tr>
              <tr>
                <td><strong>PT-2026-7734</strong></td>
                <td><span style="color:#be95ff; font-weight:700;">Liver</span></td>
                <td>B+ / A3,B35,DR1</td>
                <td>AIIMS Transplant</td>
                <td><span class="ticker-badge badge-matched">MATCHED</span></td>
                <td>
                  <button class="btn-call" style="padding:4px 10px; font-size:11px; background:rgba(66,190,101,0.2); border-color:#42be65; color:#42be65;" onclick="alert('Surgical Team Confirmed.')">
                    <i class="fa-solid fa-check-double"></i> Ready
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Right: Surgeon Organ Registration Form & AI Biometric Card -->
        <div style="display: flex; flex-direction: column; gap: 1.5rem;">
          <!-- Credentials Card -->
          <div class="problem-card purple" style="margin:0;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
              <h3 style="margin:0; font-size:15px; color:#be95ff;"><i class="fa-solid fa-id-card"></i> Verified Surgeon Identity</h3>
              <span style="background:rgba(66,190,101,0.2); color:#42be65; border:1px solid #42be65; font-size:10px; font-weight:700; padding:2px 8px; border-radius:12px;">VERIFIED</span>
            </div>
            <div style="font-size:12px; color:#c6c6c6; display:flex; flex-direction:column; gap:8px;">
              <div style="display:flex; justify-content:space-between;">
                <span style="color:#8d8d8d;">License No:</span>
                <strong style="font-family:'IBM Plex Mono'; color:#f4f4f4;">MED-KA-2026-9081</strong>
              </div>
              <div style="display:flex; justify-content:space-between;">
                <span style="color:#8d8d8d;">Specialty:</span>
                <span style="color:#78a9ff; font-weight:600;">Cardiothoracic & Transplant</span>
              </div>
              <div style="display:flex; justify-content:space-between;">
                <span style="color:#8d8d8d;">AI Verification:</span>
                <span style="color:#42be65; font-weight:700;"><i class="fa-solid fa-robot"></i> Biometric 100% Authentic</span>
              </div>
            </div>
          </div>

          <!-- Register Organ Entry Form -->
          <div class="problem-card blue" style="margin:0;">
            <h3 style="margin:0; font-size:15px; color:#78a9ff; margin-bottom:0.75rem;"><i class="fa-solid fa-plus-circle"></i> Register Donor Organ into Network</h3>
            <form id="form-doctor-add-organ">
              <div class="organ-form-grid" style="margin-bottom:10px;">
                <div>
                  <label style="font-size:11px; color:#8d8d8d; display:block; margin-bottom:4px;">Organ Type</label>
                  <select id="doc-organ-type" style="width:100%; background:#262626; color:#fff; border:1px solid #393939; padding:8px; border-radius:4px; font-size:12px;">
                    <option value="Heart">Heart</option>
                    <option value="Kidney">Kidney</option>
                    <option value="Liver">Liver</option>
                    <option value="Lung">Lung</option>
                  </select>
                </div>
                <div>
                  <label style="font-size:11px; color:#8d8d8d; display:block; margin-bottom:4px;">Blood Type</label>
                  <select id="doc-blood-type" style="width:100%; background:#262626; color:#fff; border:1px solid #393939; padding:8px; border-radius:4px; font-size:12px;">
                    <option value="O+">O+</option><option value="A+">A+</option><option value="B+">B+</option><option value="AB+">AB+</option>
                  </select>
                </div>
              </div>
              <div style="margin-bottom:12px;">
                <label style="font-size:11px; color:#8d8d8d; display:block; margin-bottom:4px;">HLA Markers (6 Loci)</label>
                <input type="text" id="doc-hla-type" value="A2,B7,DR4" style="width:100%; background:#262626; color:#fff; border:1px solid #393939; padding:8px; border-radius:4px; font-size:12px;" />
              </div>
              <button type="submit" class="btn-register-organ" style="margin:0;">
                <i class="fa-solid fa-microchip"></i> Add Organ to Quantum Matrix
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  `;
}
