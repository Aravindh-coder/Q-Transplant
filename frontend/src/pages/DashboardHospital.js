import { state } from '../state.js';

export function renderDashboardHospital() {
  const user = state.currentUser || { full_name: 'Apollo Specialty Hospital' };
  const organs = state.organs || [];
  const matches = state.matches || [];

  return `
    <div>
      <div class="dash-header">
        <div>
          <h1 class="dash-title"><i class="fa-solid fa-hospital" style="color:#da1e28;margin-right:8px;"></i>Hospital Emergency & Organ Coordination Center</h1>
          <p class="dash-subtitle">${user.full_name} · Node Unit #KA-2026-9041</p>
        </div>
      </div>

      <!-- Emergency Organ Alert Panel -->
      <div class="emergency-panel">
        <div class="emergency-panel-header">
          <div class="live-dot"></div>
          <h3><i class="fa-solid fa-triangle-exclamation"></i> POST EMERGENCY ORGAN REQUEST (GROVER'S SEARCH PIPELINE)</h3>
        </div>
        <p style="font-size:13px; color:#c6c6c6; margin-bottom: 1.25rem;">
          Submitting an emergency search broadcasts an alert to all 15 connected hospital ESP32 hardware units (Buzzer + Red LED).
          Grover's algorithm automatically runs across all registered donor databases to find a perfect match.
        </p>

        <form id="form-emergency-request">
          <div class="emergency-form-grid">
            <div class="form-group">
              <label style="color:#ff8389;">Hospital Name</label>
              <input type="text" id="emg-hosp-name" value="${user.full_name}" required />
            </div>
            <div class="form-group">
              <label style="color:#ff8389;">Hospital City</label>
              <input type="text" id="emg-hosp-city" value="Bengaluru" required />
            </div>
            <div class="form-group">
              <label style="color:#ff8389;">Contact Emergency Phone</label>
              <input type="tel" id="emg-phone" value="080-4444-1111" required />
            </div>
            <div class="form-group">
              <label style="color:#ff8389;">Organ Required</label>
              <select id="emg-organ" required>
                <option value="Heart">Heart</option>
                <option value="Kidney">Kidney</option>
                <option value="Liver">Liver</option>
                <option value="Lung">Lung</option>
                <option value="Pancreas">Pancreas</option>
              </select>
            </div>
            <div class="form-group">
              <label style="color:#ff8389;">Blood Type Needed</label>
              <select id="emg-blood" required>
                <option value="O+">O+</option>
                <option value="A+">A+</option>
                <option value="B+">B+</option>
                <option value="AB+">AB+</option>
                <option value="O-">O-</option>
              </select>
            </div>
            <div class="form-group">
              <label style="color:#ff8389;">HLA Antigen Markers</label>
              <input type="text" id="emg-hla" value="A2,B7,DR4" required />
            </div>
            <div class="form-group">
              <label style="color:#ff8389;">Urgency Level</label>
              <select id="emg-urgency">
                <option value="CRITICAL">CRITICAL (Immediate Imminent Danger)</option>
                <option value="HIGH">HIGH (Within 12 Hours)</option>
                <option value="MEDIUM">MEDIUM (Within 24 Hours)</option>
              </select>
            </div>
            <div class="form-group">
              <label style="color:#ff8389;">Patient Age</label>
              <input type="number" id="emg-age" value="38" min="1" max="100" required />
            </div>
          </div>

          <button type="submit" class="btn-emergency-submit" id="btn-submit-emergency">
            <i class="fa-solid fa-bolt"></i>
            BROADCAST EMERGENCY ALERT & RUN GROVER'S SEARCH
          </button>
        </form>

        <!-- Quantum Match Live Output Container -->
        <div id="quantum-match-output-container"></div>
      </div>

      <!-- ICU Occupancy & Available Organs -->
      <div class="kpi-grid">
        <div class="kpi-card red">
          <div class="kpi-card-label">ICU Beds Total</div>
          <div class="kpi-card-value">20</div>
          <div class="kpi-card-sub">14 Occupied · 6 Available</div>
        </div>
        <div class="kpi-card blue">
          <div class="kpi-card-label">Ventilators</div>
          <div class="kpi-card-value">6</div>
          <div class="kpi-card-sub">Ready for Surgery</div>
        </div>
        <div class="kpi-card green">
          <div class="kpi-card-label">Available Organs</div>
          <div class="kpi-card-value">${organs.length}</div>
          <div class="kpi-card-sub">Registered in Network</div>
        </div>
        <div class="kpi-card purple">
          <div class="kpi-card-label">Grover Matches</div>
          <div class="kpi-card-value">${matches.length}</div>
          <div class="kpi-card-sub">Quantum Executed</div>
        </div>
      </div>

      <!-- Network Organs Table -->
      <div class="ultra-table-wrap">
        <div class="ultra-table-header">
          <div class="ultra-table-title"><i class="fa-solid fa-dna" style="color:#0f62fe;margin-right:8px;"></i> Registered Donated Organs Network</div>
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
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            ${organs.map(o => `
              <tr>
                <td style="font-family:var(--cds-mono-font);">${o.cold_box_id}</td>
                <td><strong>${o.organ_type}</strong></td>
                <td><span class="bx--tag bx--tag--red">${o.blood_type}</span></td>
                <td>${o.hla_type}</td>
                <td>${o.max_ischemia_hours} Hours</td>
                <td><span class="bx--tag bx--tag--green">${o.status.toUpperCase()}</span></td>
                <td>
                  <button class="bx--btn bx--btn--primary btn-compute-quantum-match" data-id="${o.id}" style="padding:6px 12px; font-size:12px; border-radius:4px;">
                    <i class="fa-solid fa-atom"></i> Run Grover Search
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
