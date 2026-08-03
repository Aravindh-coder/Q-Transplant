import { state } from '../state.js';

export function renderDashboardHospital() {
  const user = state.currentUser || { full_name: 'Apollo Specialty Hospital' };
  const organs = state.organs || [];
  const matches = state.matches || [];

  return `
    <div style="padding:0 0.5rem;">
      <!-- Header -->
      <div class="dash-header" style="margin-bottom:2rem; display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:1rem;">
        <div>
          <div class="section-badge" style="background:rgba(218,30,40,0.15); border-color:rgba(218,30,40,0.4); color:#ff8389;">
            <i class="fa-solid fa-hospital"></i> HOSPITAL EMERGENCY COMMAND &amp; DISPATCH
          </div>
          <h1 class="dash-title" style="margin-top:6px;">Hospital Emergency Operations Center</h1>
          <p class="dash-subtitle">Medical Center: <strong style="color:#f4f4f4;">${user.full_name}</strong> &nbsp;·&nbsp; ESP32 Hardware Node #HSP-001 Connected</p>
        </div>
      </div>

      <!-- Emergency Alert Dispatch Panel -->
      <div class="problem-card red" style="margin-bottom:2rem; border-color:#da1e28; background:rgba(218,30,40,0.06); padding:2rem;">
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:1.25rem;">
          <div class="ticker-dot" style="width:12px; height:12px; background:#da1e28;"></div>
          <h3 style="color:#ff8389; margin:0; font-size:16px; font-weight:700;">
            <i class="fa-solid fa-triangle-exclamation"></i> DISPATCH EMERGENCY ORGAN REQUEST TO 15 HOSPITAL ESP32 HARDWARE NODES
          </h3>
        </div>
        <p style="font-size:13px; color:#c6c6c6; margin-bottom:1.5rem; line-height:1.6;">
          Submitting an emergency request instantly triggers red LED alarms and sirens across all 15 connected hospital ESP32 cold box units while running Grover's $O(\sqrt{N})$ Quantum Search across the national donor database.
        </p>

        <form id="form-emergency-request">
          <div class="organ-form-grid" style="margin-bottom:1rem;">
            <div class="form-group">
              <label style="color:#ff8389;">Hospital Name</label>
              <input type="text" id="emg-hosp-name" value="${user.full_name}" required style="width:100%; background:#262626; color:#fff; border:1px solid #393939; padding:10px; border-radius:6px; font-size:13px;" />
            </div>
            <div class="form-group">
              <label style="color:#ff8389;">City / District</label>
              <input type="text" id="emg-hosp-city" value="Bengaluru" required style="width:100%; background:#262626; color:#fff; border:1px solid #393939; padding:10px; border-radius:6px; font-size:13px;" />
            </div>
            <div class="form-group">
              <label style="color:#ff8389;">Emergency Phone Line</label>
              <input type="tel" id="emg-phone" value="080-4444-1111" required style="width:100%; background:#262626; color:#fff; border:1px solid #393939; padding:10px; border-radius:6px; font-size:13px;" />
            </div>
            <div class="form-group">
              <label style="color:#ff8389;">Organ Required</label>
              <select id="emg-organ" required style="width:100%; background:#262626; color:#fff; border:1px solid #393939; padding:10px; border-radius:6px; font-size:13px;">
                <option value="Heart">Heart</option>
                <option value="Kidney">Kidney</option>
                <option value="Liver">Liver</option>
                <option value="Lung">Lung</option>
              </select>
            </div>
            <div class="form-group">
              <label style="color:#ff8389;">Blood Type Needed</label>
              <select id="emg-blood" required style="width:100%; background:#262626; color:#fff; border:1px solid #393939; padding:10px; border-radius:6px; font-size:13px;">
                <option value="O+">O+</option><option value="A+">A+</option><option value="B+">B+</option><option value="AB+">AB+</option><option value="O-">O-</option>
              </select>
            </div>
            <div class="form-group">
              <label style="color:#ff8389;">HLA Antigen Profile</label>
              <input type="text" id="emg-hla" value="A2,B7,DR4" required style="width:100%; background:#262626; color:#fff; border:1px solid #393939; padding:10px; border-radius:6px; font-size:13px;" />
            </div>
            <div class="form-group">
              <label style="color:#ff8389;">Urgency Level</label>
              <select id="emg-urgency" style="width:100%; background:#262626; color:#fff; border:1px solid #393939; padding:10px; border-radius:6px; font-size:13px;">
                <option value="CRITICAL">CRITICAL (Immediate Action)</option>
                <option value="HIGH">HIGH (Within 12 Hours)</option>
                <option value="MEDIUM">MEDIUM (Within 24 Hours)</option>
              </select>
            </div>
            <div class="form-group">
              <label style="color:#ff8389;">Patient Age</label>
              <input type="number" id="emg-age" value="38" min="1" max="100" required style="width:100%; background:#262626; color:#fff; border:1px solid #393939; padding:10px; border-radius:6px; font-size:13px;" />
            </div>
          </div>

          <button type="submit" class="btn-emergency-submit" id="btn-submit-emergency" style="margin:0; font-size:14px; font-weight:700;">
            <i class="fa-solid fa-bolt"></i>
            BROADCAST EMERGENCY ALERT TO ALL 15 ESP32 HARDWARE NODES
          </button>
        </form>

        <div id="quantum-match-output-container"></div>
      </div>

      <!-- Hospital Clinical Capacity KPIs -->
      <div class="kpi-grid" style="margin-bottom:2rem;">
        <div class="kpi-card red">
          <div class="kpi-card-label"><i class="fa-solid fa-bed" style="color:#ff8389;"></i> ICU Beds Capacity</div>
          <div class="kpi-card-value" style="color:#ff8389;">20 Total</div>
          <div class="kpi-card-sub">14 Occupied · 6 Available</div>
        </div>
        <div class="kpi-card blue">
          <div class="kpi-card-label"><i class="fa-solid fa-fan" style="color:#78a9ff;"></i> Ventilators Ready</div>
          <div class="kpi-card-value" style="color:#78a9ff;">6 Ready</div>
          <div class="kpi-card-sub">Surgical Team Standby</div>
        </div>
        <div class="kpi-card green">
          <div class="kpi-card-label"><i class="fa-solid fa-boxes-packing" style="color:#42be65;"></i> Registered Organs</div>
          <div class="kpi-card-value" style="color:#42be65;">${organs.length}</div>
          <div class="kpi-card-sub">Validated in Network</div>
        </div>
        <div class="kpi-card purple">
          <div class="kpi-card-label"><i class="fa-solid fa-atom" style="color:#be95ff;"></i> Grover Matches</div>
          <div class="kpi-card-value" style="color:#be95ff;">${matches.length}</div>
          <div class="kpi-card-sub">Quantum Executed</div>
        </div>
      </div>

      <!-- Network Organs Table -->
      <div class="ultra-table-wrap">
        <div class="ultra-table-header">
          <div class="ultra-table-title"><i class="fa-solid fa-dna" style="color:#0f62fe;margin-right:8px;"></i> Registered Organ Donor Inventory</div>
        </div>
        <table class="utbl">
          <thead>
            <tr>
              <th>Cold Box ID</th><th>Organ Type</th><th>Blood Group</th><th>HLA Markers</th><th>Max Ischemia</th><th>Status</th><th>Grover Action</th>
            </tr>
          </thead>
          <tbody>
            ${organs.map(o => `
              <tr>
                <td style="font-family:'IBM Plex Mono';">${o.cold_box_id}</td>
                <td><strong>${o.organ_type}</strong></td>
                <td><span class="ticker-badge badge-critical" style="background:#da1e28; color:#fff;">${o.blood_type}</span></td>
                <td>${o.hla_type}</td>
                <td>${o.max_ischemia_hours} Hours</td>
                <td><span class="ticker-badge badge-matched">${o.status.toUpperCase()}</span></td>
                <td>
                  <button class="btn-call btn-compute-quantum-match" data-id="${o.id}" style="padding:5px 12px; font-size:11px;">
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
