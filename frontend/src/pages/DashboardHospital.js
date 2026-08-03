import { state } from '../state.js';
import { initEmbedded3DCanvas } from '../services/three3d.js';

export function renderDashboardHospital() {
  const user = state.currentUser || { full_name: 'Apollo Specialty Hospital' };
  const organs = state.organs || [];
  const matches = state.matches || [];

  // Trigger embedded 3D Cold Box ESP32 Cube component after render
  setTimeout(() => initEmbedded3DCanvas('hsp-3d-canvas', 'coldbox'), 100);

  return `
    <div class="clinical-dash-wrap">
      <!-- Header Bar -->
      <div style="margin-bottom: 2rem; display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1rem;">
        <div>
          <div style="display:inline-flex; align-items:center; gap:6px; background:#fff1f2; border:1px solid #fecaca; border-radius:20px; padding:4px 12px; font-size:11px; font-weight:700; color:#dc2626; letter-spacing:1px; margin-bottom:8px;">
            <i class="fa-solid fa-hospital"></i> HOSPITAL EMERGENCY COMMAND &amp; DISPATCH
          </div>
          <h1 style="font-size:1.8rem; font-weight:700; color:#0f172a; margin:0;">Hospital Emergency Operations Center</h1>
          <p style="font-size:13px; color:#64748b; margin-top:4px;">Medical Center: <strong style="color:#0f172a;">${user.full_name}</strong> &nbsp;·&nbsp; ESP32 Hardware Node #HSP-001 <span style="color:#16a34a; font-weight:700;">● Connected</span></p>
        </div>
        <div style="display:flex; gap:10px;">
          <button id="btn-refresh-hospital" style="background:#ffffff; color:#0f172a; border:1px solid #cbd5e1; padding:9px 16px; border-radius:6px; font-size:13px; font-weight:600; cursor:pointer; box-shadow:0 2px 5px rgba(0,0,0,0.05);">
            <i class="fa-solid fa-rotate"></i> Refresh Organ Feed
          </button>
          <button id="btn-run-grover-all" style="background:#0f62fe; color:#fff; border:none; padding:9px 16px; border-radius:6px; font-size:13px; font-weight:600; cursor:pointer;">
            <i class="fa-solid fa-atom"></i> Run Quantum Match All
          </button>
        </div>
      </div>

      <!-- Hospital ICU Capacity KPIs -->
      <div class="clinical-kpi-grid" style="margin-bottom: 1.5rem;">
        <div class="clinical-kpi-card red">
          <div class="clinical-kpi-label"><i class="fa-solid fa-bed" style="color:#da1e28;"></i> ICU Bed Capacity</div>
          <div class="clinical-kpi-val" style="color:#da1e28;">20</div>
          <div class="clinical-kpi-sub">14 Occupied · 6 Available</div>
        </div>
        <div class="clinical-kpi-card blue">
          <div class="clinical-kpi-label"><i class="fa-solid fa-fan" style="color:#0f62fe;"></i> Ventilators Ready</div>
          <div class="clinical-kpi-val" style="color:#0f62fe;">6</div>
          <div class="clinical-kpi-sub">Surgical Team on Standby</div>
        </div>
        <div class="clinical-kpi-card green">
          <div class="clinical-kpi-label"><i class="fa-solid fa-boxes-packing" style="color:#198038;"></i> Network Organs Available</div>
          <div class="clinical-kpi-val" style="color:#198038;">${organs.length}</div>
          <div class="clinical-kpi-sub">Validated in Quantum Network</div>
        </div>
        <div class="clinical-kpi-card purple">
          <div class="clinical-kpi-label"><i class="fa-solid fa-atom" style="color:#8a3ffc;"></i> Quantum Grover Matches</div>
          <div class="clinical-kpi-val" style="color:#8a3ffc;">${matches.length}</div>
          <div class="clinical-kpi-sub">Executed Allocations</div>
        </div>
      </div>

      <!-- Main Grid: Left Emergency Panel, Right 3D Cold Box Node -->
      <div style="display:grid; grid-template-columns: 7fr 5fr; gap:1.5rem; margin-bottom:2rem;">
        <!-- Left: Emergency Alert Dispatch Form -->
        <div class="clinical-card red-accent" style="padding:2rem;">
          <div style="display:flex; align-items:center; gap:10px; margin-bottom:1.25rem;">
            <div style="width:10px; height:10px; background:#dc2626; border-radius:50%; animation: pulse-glow 1.5s infinite;"></div>
            <h3 style="color:#dc2626; margin:0; font-size:15px; font-weight:700;">
              DISPATCH EMERGENCY ORGAN REQUEST TO 15 ESP32 HARDWARE NODES
            </h3>
          </div>
          <p style="font-size:12px; color:#64748b; margin-bottom:1.5rem; line-height:1.6;">
            Submitting an emergency request instantly triggers red LED alarms across all 15 connected hospital ESP32 cold box units while running Grover's Quantum Search across the national donor database.
          </p>

          <form id="form-emergency-request">
            <div class="organ-form-grid" style="margin-bottom:1rem;">
              <div class="form-group">
                <label style="color:#475569; font-weight:700; font-size:11px;">Hospital Name</label>
                <input type="text" id="emg-hosp-name" value="${user.full_name}" required style="width:100%; background:#f8fafc; color:#0f172a; border:1px solid #cbd5e1; padding:8px; border-radius:6px; font-size:12px;" />
              </div>
              <div class="form-group">
                <label style="color:#475569; font-weight:700; font-size:11px;">City / District</label>
                <input type="text" id="emg-hosp-city" value="Bengaluru" required style="width:100%; background:#f8fafc; color:#0f172a; border:1px solid #cbd5e1; padding:8px; border-radius:6px; font-size:12px;" />
              </div>
              <div class="form-group">
                <label style="color:#475569; font-weight:700; font-size:11px;">Emergency Phone Line</label>
                <input type="tel" id="emg-phone" value="080-4444-1111" required style="width:100%; background:#f8fafc; color:#0f172a; border:1px solid #cbd5e1; padding:8px; border-radius:6px; font-size:12px;" />
              </div>
              <div class="form-group">
                <label style="color:#475569; font-weight:700; font-size:11px;">Organ Required</label>
                <select id="emg-organ" required style="width:100%; background:#f8fafc; color:#0f172a; border:1px solid #cbd5e1; padding:8px; border-radius:6px; font-size:12px;">
                  <option value="Heart">Heart</option>
                  <option value="Kidney">Kidney</option>
                  <option value="Liver">Liver</option>
                  <option value="Lung">Lung</option>
                </select>
              </div>
              <div class="form-group">
                <label style="color:#475569; font-weight:700; font-size:11px;">Blood Type Needed</label>
                <select id="emg-blood" required style="width:100%; background:#f8fafc; color:#0f172a; border:1px solid #cbd5e1; padding:8px; border-radius:6px; font-size:12px;">
                  <option value="O+">O+</option><option value="A+">A+</option><option value="B+">B+</option><option value="AB+">AB+</option><option value="O-">O-</option>
                </select>
              </div>
              <div class="form-group">
                <label style="color:#475569; font-weight:700; font-size:11px;">HLA Antigen Profile</label>
                <input type="text" id="emg-hla" value="A2,B7,DR4" required style="width:100%; background:#f8fafc; color:#0f172a; border:1px solid #cbd5e1; padding:8px; border-radius:6px; font-size:12px;" />
              </div>
              <div class="form-group">
                <label style="color:#475569; font-weight:700; font-size:11px;">Urgency Level</label>
                <select id="emg-urgency" style="width:100%; background:#f8fafc; color:#0f172a; border:1px solid #cbd5e1; padding:8px; border-radius:6px; font-size:12px;">
                  <option value="CRITICAL">CRITICAL (Immediate)</option>
                  <option value="HIGH">HIGH (Within 12 Hours)</option>
                  <option value="MEDIUM">MEDIUM (Within 24 Hours)</option>
                </select>
              </div>
              <div class="form-group">
                <label style="color:#475569; font-weight:700; font-size:11px;">Patient Age</label>
                <input type="number" id="emg-age" value="38" min="1" max="100" required style="width:100%; background:#f8fafc; color:#0f172a; border:1px solid #cbd5e1; padding:8px; border-radius:6px; font-size:12px;" />
              </div>
            </div>

            <button type="submit" id="btn-submit-emergency" style="width:100%; background:#dc2626; color:#fff; border:none; padding:14px; border-radius:8px; font-size:14px; font-weight:700; cursor:pointer; display:flex; align-items:center; justify-content:center; gap:8px; animation: pulse-glow 2s infinite;">
              <i class="fa-solid fa-bolt"></i>
              BROADCAST EMERGENCY ALERT TO ALL 15 ESP32 HARDWARE NODES
            </button>
          </form>

          <div id="quantum-match-output-container" style="margin-top: 1rem;"></div>
        </div>

        <!-- Right: Embedded 3D Cold Box ESP32 Node Model + Status HUD -->
        <div style="display:flex; flex-direction:column; gap:1.5rem;">
          <!-- 3D ESP32 Node Canvas Card -->
          <div class="clinical-card" style="background:#0f172a; padding:1.5rem; text-align:center;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
              <h3 style="font-size:13px; font-weight:700; color:#f1f5f9; margin:0;"><i class="fa-solid fa-microchip" style="color:#0f62fe;"></i> ESP32 Cold Box IoT Node</h3>
              <span style="font-size:10px; background:#052e16; color:#4ade80; border:1px solid #16a34a; padding:2px 8px; border-radius:12px; font-weight:700;">● LIVE TELEMETRY</span>
            </div>
            <canvas id="hsp-3d-canvas" style="width:100%; height:180px; display:block;"></canvas>
            <div style="font-size:10px; color:#94a3b8; margin-top:6px; font-family:'IBM Plex Mono';">3D ESP32 Cold Box Transport Node &mdash; IoT Mesh Network</div>
          </div>

          <!-- Cold Box Telemetry HUD -->
          <div class="clinical-card blue-accent">
            <h3 style="font-size:13px; font-weight:700; color:#0f172a; margin:0 0 12px 0;"><i class="fa-solid fa-temperature-low" style="color:#0f62fe;"></i> Cold Box Real-Time Telemetry</h3>
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:12px;">
              <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:12px; text-align:center;">
                <div style="font-size:10px; color:#64748b; font-weight:700; margin-bottom:4px;">TEMPERATURE</div>
                <div style="font-size:1.6rem; font-weight:800; color:#0f62fe; font-family:'IBM Plex Mono';">4.2°C</div>
                <div style="font-size:10px; color:#16a34a;">✓ Optimal</div>
              </div>
              <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:12px; text-align:center;">
                <div style="font-size:10px; color:#64748b; font-weight:700; margin-bottom:4px;">HUMIDITY</div>
                <div style="font-size:1.6rem; font-weight:800; color:#8a3ffc; font-family:'IBM Plex Mono';">88%</div>
                <div style="font-size:10px; color:#16a34a;">✓ Optimal</div>
              </div>
              <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:12px; text-align:center;">
                <div style="font-size:10px; color:#64748b; font-weight:700; margin-bottom:4px;">VIBRATION</div>
                <div style="font-size:1.6rem; font-weight:800; color:#da1e28; font-family:'IBM Plex Mono';">0.01G</div>
                <div style="font-size:10px; color:#16a34a;">✓ Stable</div>
              </div>
              <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:12px; text-align:center;">
                <div style="font-size:10px; color:#64748b; font-weight:700; margin-bottom:4px;">BATTERY</div>
                <div style="font-size:1.6rem; font-weight:800; color:#198038; font-family:'IBM Plex Mono';">94%</div>
                <div style="font-size:10px; color:#16a34a;">✓ Charged</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Network Organs Donor Inventory Table -->
      <div class="clinical-table-wrap">
        <div style="padding:1.25rem 1.5rem; background:#f8fafc; border-bottom:1px solid #e2e8f0; display:flex; justify-content:space-between; align-items:center;">
          <div style="font-size:14px; font-weight:700; color:#0f172a;">
            <i class="fa-solid fa-dna" style="color:#0f62fe;margin-right:8px;"></i> Registered Organ Donor Inventory — National Quantum Network
          </div>
          <span style="font-size:11px; color:#64748b;">${organs.length} organs registered</span>
        </div>
        <table class="utbl">
          <thead>
            <tr>
              <th>Cold Box ID</th>
              <th>Organ Type</th>
              <th>Blood Group</th>
              <th>HLA Markers</th>
              <th>Max Ischemia</th>
              <th>Status</th>
              <th style="text-align:right;">Quantum Action</th>
            </tr>
          </thead>
          <tbody>
            ${organs.length === 0 ? `
              <tr><td colspan="7" style="text-align:center; color:#94a3b8; padding: 2rem;">No organs currently registered in the quantum network.</td></tr>
            ` : organs.map(o => `
              <tr>
                <td style="font-family:'IBM Plex Mono'; font-size:12px;">${o.cold_box_id}</td>
                <td><strong style="color:#0f172a;">${o.organ_type}</strong></td>
                <td><span style="background:#fee2e2; color:#dc2626; border:1px solid #fca5a5; padding:2px 8px; border-radius:4px; font-size:10px; font-weight:700;">${o.blood_type}</span></td>
                <td style="font-family:'IBM Plex Mono'; font-size:12px; color:#7e22ce;">${o.hla_type}</td>
                <td>${o.max_ischemia_hours}h</td>
                <td><span style="background:#dcfce7; color:#15803d; border:1px solid #86efac; padding:2px 8px; border-radius:4px; font-size:10px; font-weight:700;">${o.status.toUpperCase()}</span></td>
                <td style="text-align:right;">
                  <button class="btn-compute-quantum-match" data-id="${o.id}" style="background:#0f62fe; color:#fff; border:none; padding:5px 12px; border-radius:4px; font-size:11px; font-weight:600; cursor:pointer;">
                    <i class="fa-solid fa-atom"></i> Run Grover Match
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
