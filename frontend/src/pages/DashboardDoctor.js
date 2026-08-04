import { state } from '../state.js';
import { initEmbedded3DCanvas } from '../services/three3d.js';

export function renderDashboardDoctor() {
  const user = state.currentUser || { full_name: 'Dr. Rajesh Kumar', is_approved: true };
  const isApproved = user.is_approved !== false;

  setTimeout(() => initEmbedded3DCanvas('doc-3d-organ', 'heart'), 120);

  return `
    <div style="animation: fadeInUp 0.4s ease;">

      <!-- Header -->
      <div class="dash-header" style="margin-bottom:2rem; display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:1rem;">
        <div>
          <div class="section-badge">
            <i class="fa-solid fa-user-doctor"></i> TRANSPLANT SURGEON PORTAL
          </div>
          <h1 class="dash-title" style="margin-top:6px;">Surgeon Clinical Command Center</h1>
          <p class="dash-subtitle">Attending Surgeon: <strong style="color:#f4f4f4;">${user.full_name}</strong> &nbsp;·&nbsp; Dept. of Cardiothoracic &amp; Organ Allocation</p>
        </div>
        <a href="#" data-tab="matching" class="btn-hero-primary" style="font-size:13px; padding:10px 18px; text-decoration:none;">
          <i class="fa-solid fa-atom"></i> Run Grover Quantum Match
        </a>
      </div>

      ${!isApproved ? `
        <div class="problem-card red" style="margin-bottom:2rem; display:flex; gap:1rem; align-items:center;">
          <i class="fa-solid fa-clock-rotate-left" style="font-size:2.2rem; color:#ff8389;"></i>
          <div>
            <h3 style="color:#ff8389; margin:0 0 4px 0;">Account Verification Pending Approval</h3>
            <p style="color:#c6c6c6; font-size:13px; margin:0;">Your medical license and biometric photo have been sent for review to the Lead Organizer.</p>
          </div>
        </div>
      ` : ''}

      <!-- KPI Row -->
      <div class="kpi-grid" style="margin-bottom:2rem;">
        <div class="kpi-card purple">
          <div class="kpi-card-label"><i class="fa-solid fa-heart-pulse" style="color:#be95ff;"></i> Registered Organs</div>
          <div class="kpi-card-value" style="color:#be95ff;">14</div>
          <div class="kpi-card-sub">Validated for Matching</div>
        </div>
        <div class="kpi-card green">
          <div class="kpi-card-label"><i class="fa-solid fa-clipboard-check" style="color:#42be65;"></i> Surgeries Completed</div>
          <div class="kpi-card-value" style="color:#42be65;">128</div>
          <div class="kpi-card-sub">100% 1-Year Survival</div>
        </div>
        <div class="kpi-card blue">
          <div class="kpi-card-label"><i class="fa-solid fa-atom" style="color:#78a9ff;"></i> Match Accuracy</div>
          <div class="kpi-card-value" style="color:#78a9ff;">99.98%</div>
          <div class="kpi-card-sub">HLA &amp; Blood Compatibility</div>
        </div>
        <div class="kpi-card red">
          <div class="kpi-card-label"><i class="fa-solid fa-snowflake" style="color:#ff8389;"></i> Ischemia Viability</div>
          <div class="kpi-card-value" style="color:#ff8389;">98.4%</div>
          <div class="kpi-card-sub">Cold-Box Temp: 4.2°C</div>
        </div>
      </div>

      <!-- Two-column: Queue Table  +  3D Organ Canvas Card -->
      <div style="display:grid; grid-template-columns: 7fr 5fr; gap:1.5rem; margin-bottom:2rem;">

        <!-- Left: Surgical Queue -->
        <div class="ultra-table-wrap">
          <div class="ultra-table-header">
            <div class="ultra-table-title">
              <i class="fa-solid fa-list-check" style="color:#0f62fe; margin-right:8px;"></i> Active Surgical Dispatch &amp; Allocation Queue
            </div>
            <span style="font-size:11px; color:#42be65; font-weight:700;"><i class="fa-solid fa-circle-dot"></i> LIVE SYNC</span>
          </div>
          <table class="utbl">
            <thead>
              <tr>
                <th>Patient ID</th><th>Organ</th><th>Blood / HLA</th><th>Hospital</th><th>Risk</th><th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>PT-2026-8812</strong></td>
                <td><span style="color:#ff8389; font-weight:700;">Heart</span></td>
                <td style="font-family:'IBM Plex Mono'; font-size:12px;">O+ / A2,B7,DR4</td>
                <td>Apollo Specialty</td>
                <td><span class="ticker-badge badge-critical">CRITICAL 3.2h</span></td>
                <td>
                  <button class="btn-call" style="padding:5px 12px; font-size:11px; background:#da1e28; color:#fff; border:none; border-radius:4px; cursor:pointer;">
                    <i class="fa-solid fa-truck-medical"></i> Dispatch
                  </button>
                </td>
              </tr>
              <tr>
                <td><strong>PT-2026-9041</strong></td>
                <td><span style="color:#78a9ff; font-weight:700;">Kidney</span></td>
                <td style="font-family:'IBM Plex Mono'; font-size:12px;">A+ / A1,B8,DR3</td>
                <td>Fortis Bengaluru</td>
                <td><span class="ticker-badge" style="background:#393939; color:#c6c6c6;">MEDIUM 12h</span></td>
                <td>
                  <button class="btn-call" style="padding:5px 12px; font-size:11px;">
                    <i class="fa-solid fa-dna"></i> Match
                  </button>
                </td>
              </tr>
              <tr>
                <td><strong>PT-2026-7734</strong></td>
                <td><span style="color:#be95ff; font-weight:700;">Liver</span></td>
                <td style="font-family:'IBM Plex Mono'; font-size:12px;">B+ / A3,B35,DR1</td>
                <td>AIIMS Transplant</td>
                <td><span class="ticker-badge badge-matched">MATCHED</span></td>
                <td>
                  <button class="btn-call" style="padding:5px 12px; font-size:11px; background:#198038; border-color:#198038;">
                    <i class="fa-solid fa-check-double"></i> Ready
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Right: 3D Organ Canvas + Register Form -->
        <div style="display:flex; flex-direction:column; gap:1.5rem;">

          <!-- 3D Organ Telemetry Card -->
          <div class="problem-card blue" style="margin:0; padding:1.25rem; text-align:center;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
              <span style="font-size:13px; font-weight:700; color:#78a9ff;"><i class="fa-solid fa-heart-pulse"></i> 3D Organ Perfusion Telemetry</span>
              <span class="ticker-badge badge-matched" style="font-size:10px;">4.2°C STABLE</span>
            </div>
            <canvas id="doc-3d-organ" width="400" height="170" style="width:100%; height:170px; background:rgba(0,0,0,0.4); border-radius:8px; display:block;"></canvas>
            <p style="font-size:10px; color:#8d8d8d; margin:6px 0 0 0;">
              <i class="fa-solid fa-atom" style="color:#0f62fe;"></i> Live 3D Organ Wireframe Mesh — Pulsating at 60 BPM Perfusion
            </p>
          </div>

          <!-- Add Organ Form -->
          <div class="problem-card" style="margin:0;">
            <h3 style="font-size:13px; font-weight:700; color:#f4f4f4; margin:0 0 1rem 0;">
              <i class="fa-solid fa-plus-circle" style="color:#be95ff;"></i> Register Donor Organ into Network
            </h3>
            <form id="form-doctor-add-organ">
              <div class="organ-form-grid" style="margin-bottom:10px;">
                <div class="form-group">
                  <label>Organ Type</label>
                  <select id="doc-organ-type">
                    <option value="Heart">Heart</option>
                    <option value="Kidney">Kidney</option>
                    <option value="Liver">Liver</option>
                    <option value="Lung">Lung</option>
                  </select>
                </div>
                <div class="form-group">
                  <label>Blood Type</label>
                  <select id="doc-blood-type">
                    <option value="O+">O+</option><option value="A+">A+</option><option value="B+">B+</option><option value="AB+">AB+</option>
                  </select>
                </div>
              </div>
              <div class="form-group" style="margin-bottom:12px;">
                <label>HLA Markers (6 Loci)</label>
                <input type="text" id="doc-hla-type" value="A2,B7,DR4" />
              </div>
              <button type="submit" class="btn-hero-primary" style="width:100%; justify-content:center; padding:10px; margin:0;">
                <i class="fa-solid fa-microchip"></i> Add Organ to Quantum Matrix
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  `;
}
