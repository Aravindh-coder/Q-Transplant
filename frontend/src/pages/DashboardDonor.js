import { state } from '../state.js';
import { renderQRBadge } from '../components/QRBadge.js';
import { initEmbedded3DCanvas } from '../services/three3d.js';

export function renderDashboardDonor() {
  const user = state.currentUser || { full_name: 'David Miller' };

  // Trigger embedded 3D DNA strand component after render
  setTimeout(() => initEmbedded3DCanvas('dnr-3d-canvas', 'dna'), 100);

  return `
    <div class="clinical-dash-wrap">
      <!-- Header Bar -->
      <div style="margin-bottom: 2rem; display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1rem;">
        <div>
          <div style="display:inline-flex; align-items:center; gap:6px; background:#f1f5f9; border:1px solid #cbd5e1; border-radius:20px; padding:4px 12px; font-size:11px; font-weight:700; color:#475569; letter-spacing:1px; margin-bottom:8px;">
            <i class="fa-solid fa-hand-holding-heart" style="color:#198038;"></i> VERIFIED ORGAN DONOR PORTAL
          </div>
          <h1 style="font-size:1.8rem; font-weight:700; color:#0f172a; margin:0;">Digital Organ Life Passport &amp; Donor Pledge</h1>
          <p style="font-size:13px; color:#64748b; margin-top:4px;">Registered Life Donor: <strong style="color:#0f172a;">${user.full_name}</strong> &nbsp;·&nbsp; NOTTO Donor ID: #DNR-2026-9041</p>
        </div>
      </div>

      <!-- Main Layout: Left Passport + 3D DNA Canvas, Right QR Badge -->
      <div style="display:grid; grid-template-columns: 8fr 4fr; gap:1.5rem; margin-bottom:2rem;">
        <!-- Left: Clinical Donor Pass Card -->
        <div class="clinical-card green-accent">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1.5rem;">
            <h3 style="color:#15803d; margin:0; font-size:16px; font-weight:700;"><i class="fa-solid fa-id-card"></i> Official Pledged Organ Donor Pass</h3>
            <span style="background:#dcfce7; color:#15803d; border:1px solid #86efac; font-size:10px; font-weight:700; padding:3px 10px; border-radius:12px;"><i class="fa-solid fa-circle-check"></i> VERIFIED &amp; ACTIVE</span>
          </div>

          <div style="display:grid; grid-template-columns: 1fr 1fr; gap:1.5rem; align-items:center;">
            <div style="display:flex; flex-direction:column; gap:12px; font-size:13px;">
              <div style="display:flex; justify-content:space-between; border-bottom:1px solid #e2e8f0; padding-bottom:8px;">
                <span style="color:#64748b;">PLEDGED DONOR NAME</span>
                <strong style="color:#0f172a;">${user.full_name}</strong>
              </div>
              <div style="display:flex; justify-content:space-between; border-bottom:1px solid #e2e8f0; padding-bottom:8px;">
                <span style="color:#64748b;">BLOOD TYPE</span>
                <span style="background:#fee2e2; color:#dc2626; border:1px solid #fca5a5; font-size:11px; font-weight:700; padding:2px 8px; border-radius:4px;">O POSITIVE (O+)</span>
              </div>
              <div style="display:flex; justify-content:space-between; border-bottom:1px solid #e2e8f0; padding-bottom:8px;">
                <span style="color:#64748b;">HLA GENETIC MARKERS</span>
                <span style="font-family:'IBM Plex Mono'; color:#7e22ce; font-weight:700;">A2, B7, DR4</span>
              </div>
              <div style="display:flex; justify-content:space-between;">
                <span style="color:#64748b;">PLEDGED ORGANS FOR DONATION</span>
                <span style="color:#16a34a; font-weight:700;">Heart, Kidney, Cornea, Liver</span>
              </div>
            </div>

            <!-- Embedded 3D DNA Model Canvas -->
            <div style="background:#0f172a; border-radius:10px; padding:10px; text-align:center;">
              <canvas id="dnr-3d-canvas" style="width:100%; height:130px; display:block;"></canvas>
              <div style="font-size:10px; color:#94a3b8; margin-top:4px;">3D HLA DNA Compatibility Model</div>
            </div>
          </div>
        </div>

        <div>
          ${renderQRBadge('QR-DONOR-O-PLUS-001', user.full_name)}
        </div>
      </div>

      <!-- Register Donated Organ Form Card -->
      <div class="clinical-card blue-accent" style="padding:2rem;">
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:1.25rem;">
          <i class="fa-solid fa-hand-holding-medical" style="font-size:2rem; color:#0f62fe;"></i>
          <div>
            <h3 style="font-size:16px; font-weight:700; color:#0f172a; margin:0;">Register Organ Availability into Quantum Network</h3>
            <p style="font-size:12px; color:#64748b; margin:2px 0 0 0;">Submitting an available organ triggers Grover's Quantum algorithm to find the ideal matched patient in seconds.</p>
          </div>
        </div>

        <form id="form-donor-register-organ">
          <div class="organ-form-grid" style="margin-bottom:1rem;">
            <div class="form-group">
              <label style="color:#475569; font-weight:700;">Organ Type</label>
              <select id="donor-organ-type" required style="width:100%; background:#f8fafc; color:#0f172a; border:1px solid #cbd5e1; padding:10px; border-radius:6px; font-size:13px;">
                <option value="Heart">Heart (Cardiac)</option>
                <option value="Kidney">Kidney (Renal)</option>
                <option value="Liver">Liver (Hepatic)</option>
                <option value="Lung">Lung (Pulmonary)</option>
              </select>
            </div>

            <div class="form-group">
              <label style="color:#475569; font-weight:700;">Blood Group</label>
              <select id="donor-blood-type" required style="width:100%; background:#f8fafc; color:#0f172a; border:1px solid #cbd5e1; padding:10px; border-radius:6px; font-size:13px;">
                <option value="O+">O Positive (O+)</option>
                <option value="A+">A Positive (A+)</option>
                <option value="B+">B Positive (B+)</option>
                <option value="AB+">AB Positive (AB+)</option>
                <option value="O-">O Negative (O-)</option>
              </select>
            </div>

            <div class="form-group">
              <label style="color:#475569; font-weight:700;">HLA Antigen Markers</label>
              <input type="text" id="donor-hla-type" value="A2,B7,DR4" required style="width:100%; background:#f8fafc; color:#0f172a; border:1px solid #cbd5e1; padding:10px; border-radius:6px; font-size:13px;" />
            </div>

            <div class="form-group">
              <label style="color:#475569; font-weight:700;">Max Cold Ischemia Hours</label>
              <input type="number" id="donor-ischemia-hours" value="4.0" step="0.5" min="1" max="24" required style="width:100%; background:#f8fafc; color:#0f172a; border:1px solid #cbd5e1; padding:10px; border-radius:6px; font-size:13px;" />
            </div>
          </div>

          <button type="submit" class="btn-hero-primary" id="btn-submit-donor-organ" style="width:100%; justify-content:center; padding:12px; font-size:14px; margin:0;">
            <i class="fa-solid fa-heart-pulse"></i>
            REGISTER ORGAN INTO GROVER QUANTUM MATCH DATABASE
          </button>
        </form>
      </div>
    </div>
  `;
}
