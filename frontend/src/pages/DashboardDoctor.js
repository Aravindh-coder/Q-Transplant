import { state } from '../state.js';
import { initEmbedded3DCanvas } from '../services/three3d.js';

export function renderDashboardDoctor() {
  const user = state.currentUser || { full_name: 'Dr. Rajesh Kumar', is_approved: true };
  const isApproved = user.is_approved !== false;

  // Trigger embedded 3D organ canvas after rendering
  setTimeout(() => initEmbedded3DCanvas('doc-3d-canvas', 'heart'), 100);

  return `
    <div class="clinical-dash-wrap">
      <!-- Header Bar -->
      <div style="margin-bottom: 2rem; display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1rem;">
        <div>
          <div style="display:inline-flex; align-items:center; gap:6px; background:#f1f5f9; border:1px solid #cbd5e1; border-radius:20px; padding:4px 12px; font-size:11px; font-weight:700; color:#475569; letter-spacing:1px; margin-bottom:8px;">
            <i class="fa-solid fa-user-doctor" style="color:#0f62fe;"></i> SURGEON CLINICAL PORTAL
          </div>
          <h1 style="font-size:1.8rem; font-weight:700; color:#0f172a; margin:0;">Transplant Surgeon Command Center</h1>
          <p style="font-size:13px; color:#64748b; margin-top:4px;">Attending Surgeon: <strong style="color:#0f172a;">${user.full_name}</strong> &nbsp;·&nbsp; Department of Cardiothoracic & Organ Allocation</p>
        </div>
        <div>
          <a href="#" data-tab="matching" class="btn-hero-primary" style="font-size: 13px; padding: 10px 18px; text-decoration: none;">
            <i class="fa-solid fa-atom"></i> Run Grover Quantum Match
          </a>
        </div>
      </div>

      ${!isApproved ? `
        <div class="clinical-card red-accent" style="margin-bottom: 2rem; background:#fff5f5; border-color:#fecaca;">
          <div style="display: flex; gap: 1rem; align-items: center;">
            <i class="fa-solid fa-clock-rotate-left" style="font-size: 2.2rem; color: #dc2626;"></i>
            <div>
              <h3 style="color: #dc2626; margin: 0 0 4px 0; font-size:15px; font-weight:700;">Account Verification Pending Approval</h3>
              <p style="color: #475569; font-size: 13px; margin: 0;">
                Your medical license credentials, live biometric photo, and surgical certifications have been securely uploaded to the Lead Organizer (<strong>aravindhjoshua10@gmail.com</strong>).
              </p>
            </div>
          </div>
        </div>
      ` : ''}

      <!-- Doctor Clinical KPIs -->
      <div class="clinical-kpi-grid" style="margin-bottom: 1.5rem;">
        <div class="clinical-kpi-card purple">
          <div class="clinical-kpi-label"><i class="fa-solid fa-heart-pulse" style="color:#8a3ffc;"></i> Registered Organs</div>
          <div class="clinical-kpi-val" style="color:#8a3ffc;">14</div>
          <div class="clinical-kpi-sub">Validated for Matching</div>
        </div>
        <div class="clinical-kpi-card green">
          <div class="clinical-kpi-label"><i class="fa-solid fa-clipboard-check" style="color:#198038;"></i> Surgeries Completed</div>
          <div class="clinical-kpi-val" style="color:#198038;">128</div>
          <div class="clinical-kpi-sub">100% 1-Year Patient Survival</div>
        </div>
        <div class="clinical-kpi-card blue">
          <div class="clinical-kpi-label"><i class="fa-solid fa-atom" style="color:#0f62fe;"></i> Match Accuracy</div>
          <div class="clinical-kpi-val" style="color:#0f62fe;">99.98%</div>
          <div class="clinical-kpi-sub">HLA & Blood Compatibility</div>
        </div>
        <div class="clinical-kpi-card red">
          <div class="clinical-kpi-label"><i class="fa-solid fa-snowflake" style="color:#da1e28;"></i> Ischemia Viability Avg</div>
          <div class="clinical-kpi-val" style="color:#da1e28;">98.4%</div>
          <div class="clinical-kpi-sub">Cold-Box Temp: 4.2°C</div>
        </div>
      </div>

      <!-- Grid Layout: Left Queue Table, Right Embedded 3D Component -->
      <div style="display: grid; grid-template-columns: 7fr 5fr; gap: 1.5rem; margin-bottom: 2rem;">
        <!-- Left: Active Surgical Dispatch Queue Table -->
        <div class="clinical-table-wrap">
          <div style="padding:1.25rem 1.5rem; background:#f8fafc; border-bottom:1px solid #e2e8f0; display:flex; justify-content:space-between; align-items:center;">
            <div style="font-size:14px; font-weight:700; color:#0f172a;">
              <i class="fa-solid fa-list-check" style="color:#0f62fe; margin-right:8px;"></i> Active Surgical Dispatch &amp; Allocation Queue
            </div>
            <span style="font-size:11px; color:#16a34a; font-weight:700;"><i class="fa-solid fa-circle-dot"></i> LIVE SYNC</span>
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
                <td><span style="color:#dc2626; font-weight:700;">Heart</span></td>
                <td>O+ / A2,B7,DR4</td>
                <td>Apollo Specialty</td>
                <td><span style="background:#fee2e2; color:#dc2626; border:1px solid #fca5a5; padding:2px 8px; border-radius:12px; font-size:10px; font-weight:700;">CRITICAL (3.2h)</span></td>
                <td>
                  <button style="background:#0f62fe; color:#fff; border:none; padding:5px 12px; border-radius:4px; font-size:11px; font-weight:600; cursor:pointer;" onclick="alert('Dispatching Surgical Transport Team...')">
                    <i class="fa-solid fa-truck-medical"></i> Dispatch
                  </button>
                </td>
              </tr>
              <tr>
                <td><strong>PT-2026-9041</strong></td>
                <td><span style="color:#0284c7; font-weight:700;">Kidney</span></td>
                <td>A+ / A1,B8,DR3</td>
                <td>Fortis Bengaluru</td>
                <td><span style="background:#fef3c7; color:#d97706; border:1px solid #fcd34d; padding:2px 8px; border-radius:12px; font-size:10px; font-weight:700;">MEDIUM (12h)</span></td>
                <td>
                  <button style="background:#f1f5f9; color:#0f172a; border:1px solid #cbd5e1; padding:5px 12px; border-radius:4px; font-size:11px; font-weight:600; cursor:pointer;" onclick="alert('Preparing Donor Allocation Match...')">
                    <i class="fa-solid fa-dna"></i> Match
                  </button>
                </td>
              </tr>
              <tr>
                <td><strong>PT-2026-7734</strong></td>
                <td><span style="color:#9333ea; font-weight:700;">Liver</span></td>
                <td>B+ / A3,B35,DR1</td>
                <td>AIIMS Transplant</td>
                <td><span style="background:#dcfce7; color:#16a34a; border:1px solid #86efac; padding:2px 8px; border-radius:12px; font-size:10px; font-weight:700;">MATCHED</span></td>
                <td>
                  <button style="background:#dcfce7; color:#15803d; border:1px solid #86efac; padding:5px 12px; border-radius:4px; font-size:11px; font-weight:600; cursor:pointer;" onclick="alert('Surgical Team Confirmed.')">
                    <i class="fa-solid fa-check-double"></i> Ready
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Right: Embedded 3D Organ Canvas Component + Verified Badge -->
        <div style="display:flex; flex-direction:column; gap:1.5rem;">
          <!-- 3D Component Tile -->
          <div class="clinical-card blue-accent" style="padding:1.5rem; text-align:center;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
              <h3 style="font-size:14px; font-weight:700; color:#0f172a; margin:0;"><i class="fa-solid fa-heart-pulse" style="color:#dc2626;"></i> Real-Time 3D Organ Perfusion Telemetry</h3>
              <span style="font-size:10px; background:#dcfce7; color:#15803d; padding:2px 8px; border-radius:12px; font-weight:700;">4.2°C STABLE</span>
            </div>
            <!-- Embedded 3D Canvas -->
            <canvas id="doc-3d-canvas" style="width:100%; height:180px; background:#0f172a; border-radius:8px; display:block;"></canvas>
            <div style="font-size:11px; color:#64748b; margin-top:8px;">
              <i class="fa-solid fa-atom" style="color:#0f62fe;"></i> Interactive 3D Wireframe Organ Mesh — Pulsating at 60 BPM Perfusion Frequency
            </div>
          </div>

          <!-- Doctor Organ Registration Card -->
          <div class="clinical-card purple-accent">
            <h3 style="font-size:14px; font-weight:700; color:#0f172a; margin:0 0 1rem 0;"><i class="fa-solid fa-plus-circle" style="color:#8a3ffc;"></i> Register Donor Organ into Network</h3>
            <form id="form-doctor-add-organ">
              <div class="organ-form-grid" style="margin-bottom:10px;">
                <div>
                  <label style="font-size:11px; color:#64748b; font-weight:700; display:block; margin-bottom:4px;">Organ Type</label>
                  <select id="doc-organ-type" style="width:100%; background:#f8fafc; color:#0f172a; border:1px solid #cbd5e1; padding:8px; border-radius:6px; font-size:12px;">
                    <option value="Heart">Heart</option>
                    <option value="Kidney">Kidney</option>
                    <option value="Liver">Liver</option>
                    <option value="Lung">Lung</option>
                  </select>
                </div>
                <div>
                  <label style="font-size:11px; color:#64748b; font-weight:700; display:block; margin-bottom:4px;">Blood Type</label>
                  <select id="doc-blood-type" style="width:100%; background:#f8fafc; color:#0f172a; border:1px solid #cbd5e1; padding:8px; border-radius:6px; font-size:12px;">
                    <option value="O+">O+</option><option value="A+">A+</option><option value="B+">B+</option><option value="AB+">AB+</option>
                  </select>
                </div>
              </div>
              <div style="margin-bottom:12px;">
                <label style="font-size:11px; color:#64748b; font-weight:700; display:block; margin-bottom:4px;">HLA Markers (6 Loci)</label>
                <input type="text" id="doc-hla-type" value="A2,B7,DR4" style="width:100%; background:#f8fafc; color:#0f172a; border:1px solid #cbd5e1; padding:8px; border-radius:6px; font-size:12px;" />
              </div>
              <button type="submit" class="btn-hero-primary" style="width:100%; justify-content:center; padding:10px; font-size:13px; margin:0;">
                <i class="fa-solid fa-microchip"></i> Add Organ to Quantum Matrix
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  `;
}
