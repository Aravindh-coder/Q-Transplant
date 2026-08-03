import { state } from '../state.js';
import { initEmbedded3DCanvas } from '../services/three3d.js';

export function renderDashboardHospital() {
  const user = state.currentUser || { full_name: 'Apollo Specialty Hospital' };
  const organs = state.organs || [];
  const matches = state.matches || [];

  setTimeout(() => initEmbedded3DCanvas('hsp-3d-coldbox', 'coldbox'), 120);

  return `
    <div style="animation: fadeInUp 0.4s ease;">

      <!-- Header -->
      <div class="dash-header" style="margin-bottom:2rem; display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:1rem;">
        <div>
          <div class="section-badge" style="background:rgba(218,30,40,0.15); border-color:rgba(218,30,40,0.4); color:#ff8389;">
            <i class="fa-solid fa-hospital"></i> HOSPITAL EMERGENCY COMMAND &amp; DISPATCH
          </div>
          <h1 class="dash-title" style="margin-top:6px;">Hospital Emergency Operations Center</h1>
          <p class="dash-subtitle">Medical Center: <strong style="color:#f4f4f4;">${user.full_name}</strong> &nbsp;·&nbsp; ESP32 Hardware Node #HSP-001 <span style="color:#42be65; font-weight:700;">● Connected</span></p>
        </div>
        <button id="btn-run-grover-all" class="btn-hero-primary" style="font-size:13px; padding:10px 18px;">
          <i class="fa-solid fa-atom"></i> Run Quantum Match All
        </button>
      </div>

      <!-- KPI Row -->
      <div class="kpi-grid" style="margin-bottom:2rem;">
        <div class="kpi-card red">
          <div class="kpi-card-label"><i class="fa-solid fa-bed" style="color:#ff8389;"></i> ICU Bed Capacity</div>
          <div class="kpi-card-value" style="color:#ff8389;">20</div>
          <div class="kpi-card-sub">14 Occupied · 6 Available</div>
        </div>
        <div class="kpi-card blue">
          <div class="kpi-card-label"><i class="fa-solid fa-fan" style="color:#78a9ff;"></i> Ventilators Ready</div>
          <div class="kpi-card-value" style="color:#78a9ff;">6</div>
          <div class="kpi-card-sub">Surgical Team on Standby</div>
        </div>
        <div class="kpi-card green">
          <div class="kpi-card-label"><i class="fa-solid fa-boxes-packing" style="color:#42be65;"></i> Network Organs Available</div>
          <div class="kpi-card-value" style="color:#42be65;">${organs.length}</div>
          <div class="kpi-card-sub">Validated in Quantum Network</div>
        </div>
        <div class="kpi-card purple">
          <div class="kpi-card-label"><i class="fa-solid fa-atom" style="color:#be95ff;"></i> Quantum Grover Matches</div>
          <div class="kpi-card-value" style="color:#be95ff;">${matches.length}</div>
          <div class="kpi-card-sub">Executed Allocations</div>
        </div>
      </div>

      <!-- Two-column: Emergency Form  +  3D Cold Box Node -->
      <div style="display:grid; grid-template-columns: 7fr 5fr; gap:1.5rem; margin-bottom:2rem;">

        <!-- Left: Emergency Alert Dispatch -->
        <div class="problem-card red" style="margin:0; border-color:#da1e28; padding:2rem;">
          <div style="display:flex; align-items:center; gap:10px; margin-bottom:1.25rem;">
            <div class="ticker-dot" style="width:12px; height:12px; background:#da1e28; animation: pulse-glow 1.5s infinite;"></div>
            <h3 style="color:#ff8389; margin:0; font-size:14px; font-weight:700;">
              DISPATCH EMERGENCY ORGAN REQUEST TO 15 ESP32 HARDWARE NODES
            </h3>
          </div>
          <p style="font-size:12px; color:#c6c6c6; margin-bottom:1.5rem; line-height:1.6;">
            Submitting triggers red LED alarms across all 15 connected hospital ESP32 cold box units while running Grover's Quantum Search across the national donor database.
          </p>

          <form id="form-emergency-request">
            <div class="organ-form-grid" style="margin-bottom:1rem;">
              <div class="form-group">
                <label>Hospital Name</label>
                <input type="text" id="emg-hosp-name" value="${user.full_name}" required />
              </div>
              <div class="form-group">
                <label>City / District</label>
                <input type="text" id="emg-hosp-city" value="Bengaluru" required />
              </div>
              <div class="form-group">
                <label>Emergency Phone</label>
                <input type="tel" id="emg-phone" value="080-4444-1111" required />
              </div>
              <div class="form-group">
                <label>Organ Required</label>
                <select id="emg-organ" required>
                  <option value="Heart">Heart</option>
                  <option value="Kidney">Kidney</option>
                  <option value="Liver">Liver</option>
                  <option value="Lung">Lung</option>
                </select>
              </div>
              <div class="form-group">
                <label>Blood Type Needed</label>
                <select id="emg-blood" required>
                  <option value="O+">O+</option><option value="A+">A+</option><option value="B+">B+</option><option value="AB+">AB+</option><option value="O-">O-</option>
                </select>
              </div>
              <div class="form-group">
                <label>HLA Antigen Profile</label>
                <input type="text" id="emg-hla" value="A2,B7,DR4" required />
              </div>
              <div class="form-group">
                <label>Urgency Level</label>
                <select id="emg-urgency">
                  <option value="CRITICAL">CRITICAL (Immediate)</option>
                  <option value="HIGH">HIGH (Within 12h)</option>
                  <option value="MEDIUM">MEDIUM (Within 24h)</option>
                </select>
              </div>
              <div class="form-group">
                <label>Patient Age</label>
                <input type="number" id="emg-age" value="38" min="1" max="100" required />
              </div>
            </div>

            <button type="submit" id="btn-submit-emergency" class="btn-emergency-submit" style="margin:0; width:100%; justify-content:center; animation: pulse-glow 2s infinite;">
              <i class="fa-solid fa-bolt"></i>
              BROADCAST EMERGENCY ALERT TO ALL 15 ESP32 HARDWARE NODES
            </button>
          </form>

          <div id="quantum-match-output-container" style="margin-top:1rem;"></div>
        </div>

        <!-- Right: 3D Cold Box ESP32 Node + Telemetry HUD -->
        <div style="display:flex; flex-direction:column; gap:1.5rem;">

          <!-- 3D ESP32 Node Canvas -->
          <div class="problem-card" style="margin:0; padding:1.25rem; text-align:center;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
              <span style="font-size:13px; font-weight:700; color:#78a9ff;"><i class="fa-solid fa-microchip"></i> ESP32 Cold Box IoT Node</span>
              <span class="ticker-badge badge-matched" style="font-size:10px;">● LIVE TELEMETRY</span>
            </div>
            <canvas id="hsp-3d-coldbox" style="width:100%; height:160px; background:rgba(0,0,0,0.5); border-radius:8px; display:block;"></canvas>
            <p style="font-size:10px; color:#6f6f6f; margin:6px 0 0 0; font-family:'IBM Plex Mono';">3D ESP32 Cold Box Transport Node — IoT Mesh Network</p>
          </div>

          <!-- Cold Box Telemetry HUD -->
          <div class="problem-card blue" style="margin:0;">
            <h3 style="font-size:13px; font-weight:700; color:#f4f4f4; margin:0 0 12px 0;">
              <i class="fa-solid fa-temperature-low" style="color:#78a9ff;"></i> Cold Box Real-Time Telemetry
            </h3>
            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px;">
              <div style="background:#262626; border-radius:8px; padding:12px; text-align:center;">
                <div style="font-size:10px; color:#8d8d8d; font-weight:700; margin-bottom:4px; text-transform:uppercase;">Temperature</div>
                <div style="font-size:1.5rem; font-weight:800; color:#78a9ff; font-family:'IBM Plex Mono';">4.2°C</div>
                <div style="font-size:10px; color:#42be65;">✓ Optimal</div>
              </div>
              <div style="background:#262626; border-radius:8px; padding:12px; text-align:center;">
                <div style="font-size:10px; color:#8d8d8d; font-weight:700; margin-bottom:4px; text-transform:uppercase;">Humidity</div>
                <div style="font-size:1.5rem; font-weight:800; color:#be95ff; font-family:'IBM Plex Mono';">88%</div>
                <div style="font-size:10px; color:#42be65;">✓ Optimal</div>
              </div>
              <div style="background:#262626; border-radius:8px; padding:12px; text-align:center;">
                <div style="font-size:10px; color:#8d8d8d; font-weight:700; margin-bottom:4px; text-transform:uppercase;">Vibration</div>
                <div style="font-size:1.5rem; font-weight:800; color:#ff8389; font-family:'IBM Plex Mono';">0.01G</div>
                <div style="font-size:10px; color:#42be65;">✓ Stable</div>
              </div>
              <div style="background:#262626; border-radius:8px; padding:12px; text-align:center;">
                <div style="font-size:10px; color:#8d8d8d; font-weight:700; margin-bottom:4px; text-transform:uppercase;">Battery</div>
                <div style="font-size:1.5rem; font-weight:800; color:#42be65; font-family:'IBM Plex Mono';">94%</div>
                <div style="font-size:10px; color:#42be65;">✓ Charged</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Network Organs Table -->
      <div class="ultra-table-wrap">
        <div class="ultra-table-header">
          <div class="ultra-table-title">
            <i class="fa-solid fa-dna" style="color:#0f62fe;margin-right:8px;"></i> Registered Organ Donor Inventory — National Quantum Network
          </div>
          <span style="font-size:11px; color:#8d8d8d;">${organs.length} organs registered</span>
        </div>
        <table class="utbl">
          <thead>
            <tr>
              <th>Cold Box ID</th><th>Organ Type</th><th>Blood Group</th><th>HLA Markers</th><th>Max Ischemia</th><th>Status</th><th style="text-align:right;">Quantum Action</th>
            </tr>
          </thead>
          <tbody>
            ${organs.length === 0 ? `
              <tr><td colspan="7" style="text-align:center; color:#6f6f6f; padding:2.5rem;">No organs currently registered in the quantum network.</td></tr>
            ` : organs.map(o => `
              <tr>
                <td style="font-family:'IBM Plex Mono'; font-size:12px;">${o.cold_box_id}</td>
                <td><strong>${o.organ_type}</strong></td>
                <td><span class="ticker-badge badge-critical">${o.blood_type}</span></td>
                <td style="font-family:'IBM Plex Mono'; font-size:12px; color:#be95ff;">${o.hla_type}</td>
                <td>${o.max_ischemia_hours}h</td>
                <td><span class="ticker-badge badge-matched">${o.status.toUpperCase()}</span></td>
                <td style="text-align:right;">
                  <button class="btn-compute-quantum-match" data-id="${o.id}" class="btn-call" style="padding:5px 12px; font-size:11px; background:#0f62fe; color:#fff; border:none; border-radius:4px; cursor:pointer;">
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
