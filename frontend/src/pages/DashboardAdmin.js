import { state } from '../state.js';
import { initEmbedded3DCanvas } from '../services/three3d.js';

export function renderDashboardAdmin() {
  const pending = state.pendingUsers || [];
  const allUsersDetailed = state.allUsersDetailed || { doctors: [], hospitals: [], donors: [], patients: [] };

  setTimeout(() => initEmbedded3DCanvas('org-3d-bloch', 'bloch'), 120);

  return `
    <div style="animation: fadeInUp 0.4s ease;">

      <!-- Header -->
      <div class="dash-header" style="margin-bottom:2rem; display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:1rem;">
        <div>
          <div class="section-badge">
            <i class="fa-solid fa-shield-halved"></i> ORGANIZER EXECUTIVE COMMAND
          </div>
          <h1 class="dash-title" style="margin-top:6px;">National Organ Allocation Command Center</h1>
          <p class="dash-subtitle">Lead Organizer: <strong style="color:#f4f4f4;">aravindhjoshua10@gmail.com</strong> &nbsp;·&nbsp; NOTTO Audit &amp; System Governance</p>
        </div>
        <button id="btn-refresh-admin-data" class="btn-call" style="padding:10px 16px; font-size:13px;">
          <i class="fa-solid fa-rotate"></i> Refresh Operational Feed
        </button>
      </div>

      <!-- KPI Row -->
      <div class="kpi-grid" style="margin-bottom:2rem;">
        <div class="kpi-card green">
          <div class="kpi-card-label"><i class="fa-solid fa-hand-holding-heart" style="color:#42be65;"></i> Registered Donors</div>
          <div class="kpi-card-value" style="color:#42be65;">1,247</div>
          <div class="kpi-card-sub">Verified Donor Pledges</div>
        </div>
        <div class="kpi-card purple">
          <div class="kpi-card-label"><i class="fa-solid fa-bed-pulse" style="color:#be95ff;"></i> Waitlist Patients</div>
          <div class="kpi-card-value" style="color:#be95ff;">893</div>
          <div class="kpi-card-sub">Active Recipient Queue</div>
        </div>
        <div class="kpi-card red">
          <div class="kpi-card-label"><i class="fa-solid fa-hospital" style="color:#ff8389;"></i> Connected Hospitals</div>
          <div class="kpi-card-value" style="color:#ff8389;">15</div>
          <div class="kpi-card-sub">ESP32 IoT Nodes Active</div>
        </div>
        <div class="kpi-card blue">
          <div class="kpi-card-label"><i class="fa-solid fa-atom" style="color:#78a9ff;"></i> Quantum Search SLA</div>
          <div class="kpi-card-value" style="color:#78a9ff;">0.3ms</div>
          <div class="kpi-card-sub">Grover's O(√N) Acceleration</div>
        </div>
      </div>

      <!-- Two-column: Bloch Sphere Banner + Quantum Description -->
      <div class="problem-card blue" style="margin-bottom:2rem; display:grid; grid-template-columns: 7fr 5fr; gap:1.5rem; align-items:center;">
        <div>
          <div class="section-badge" style="margin-bottom:8px;"><i class="fa-solid fa-atom"></i> Grover's Quantum Match Engine — Live State Model</div>
          <h3 style="font-size:1.1rem; font-weight:700; color:#f4f4f4; margin:0 0 8px 0;">Organ Allocation Quantum Superposition State</h3>
          <p style="font-size:13px; color:#c6c6c6; line-height:1.7; margin:0;">
            Grover's algorithm processes 1,000,000+ donor-recipient permutations simultaneously in 
            <span style="color:#be95ff; font-family:'IBM Plex Mono'; font-weight:700;">O(√N)</span> iterations.
            The live 3D Bloch sphere tracks the qubit state vector during active dispatches across all 15 ESP32 hospital nodes.
          </p>
        </div>
        <div style="background:#161616; border-radius:10px; padding:12px; text-align:center;">
          <canvas id="org-3d-bloch" width="400" height="140" style="width:100%; height:140px; display:block;"></canvas>
          <div style="font-size:10px; color:#6f6f6f; margin-top:6px; font-family:'IBM Plex Mono';">3D Grover Qubit Bloch Sphere — Live Vector</div>
        </div>
      </div>

      <!-- Pending Approvals Table -->
      <div class="ultra-table-wrap" style="margin-bottom:2rem;">
        <div class="ultra-table-header">
          <div class="ultra-table-title">
            <i class="fa-solid fa-triangle-exclamation" style="color:#f1c21b; margin-right:8px;"></i>
            Pending Applicant Credentials Review (${pending.length})
          </div>
        </div>

        ${pending.length === 0 ? `
          <div style="padding:2.5rem; text-align:center; color:#6f6f6f;">
            <i class="fa-solid fa-shield-check" style="font-size:2.5rem; color:#42be65; display:block; margin-bottom:8px;"></i>
            <div style="color:#c6c6c6; font-size:14px; font-weight:600;">All Medical Registrations Reviewed</div>
            <div style="font-size:12px; margin-top:4px;">No pending approval requests.</div>
          </div>
        ` : `
          <table class="utbl">
            <thead>
              <tr>
                <th>Applicant Name</th><th>Role</th><th>Email</th><th>Date</th><th style="text-align:right;">Action</th>
              </tr>
            </thead>
            <tbody>
              ${pending.map(u => `
                <tr>
                  <td><strong>${u.full_name}</strong></td>
                  <td><span class="ticker-badge" style="background:#393939;">${u.role.toUpperCase()}</span></td>
                  <td>${u.email}</td>
                  <td style="font-family:'IBM Plex Mono'; font-size:12px; color:#8d8d8d;">${u.created_at ? new Date(u.created_at).toLocaleDateString() : 'Recent'}</td>
                  <td style="text-align:right;">
                    <button class="btn-approve-user" data-id="${u.id}" style="background:#198038; color:#fff; border:none; padding:5px 12px; border-radius:4px; font-size:11px; font-weight:600; cursor:pointer;">
                      <i class="fa-solid fa-check"></i> Approve
                    </button>
                    <button class="btn-reject-user" data-id="${u.id}" style="background:#da1e28; color:#fff; border:none; padding:5px 12px; border-radius:4px; font-size:11px; font-weight:600; cursor:pointer; margin-left:6px;">
                      <i class="fa-solid fa-xmark"></i> Reject
                    </button>
                  </td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        `}
      </div>

      <!-- Master Registry -->
      <div class="ultra-table-wrap">
        <div class="ultra-table-header">
          <div class="ultra-table-title"><i class="fa-solid fa-users" style="color:#0f62fe;margin-right:8px;"></i> Master Registry of Medical Centers &amp; System Profiles</div>
        </div>
        <div style="display:flex; border-bottom:1px solid #393939;">
          <button class="form-tab active tab-admin-view" data-target="admin-view-doctors" style="padding:10px 18px; font-size:13px; font-weight:600; color:#8d8d8d; background:transparent; border:none; cursor:pointer; border-bottom:2px solid transparent;">Doctors (${allUsersDetailed.doctors ? allUsersDetailed.doctors.length : 0})</button>
          <button class="form-tab tab-admin-view" data-target="admin-view-hospitals" style="padding:10px 18px; font-size:13px; font-weight:600; color:#8d8d8d; background:transparent; border:none; cursor:pointer; border-bottom:2px solid transparent;">Hospitals (${allUsersDetailed.hospitals ? allUsersDetailed.hospitals.length : 0})</button>
          <button class="form-tab tab-admin-view" data-target="admin-view-donors" style="padding:10px 18px; font-size:13px; font-weight:600; color:#8d8d8d; background:transparent; border:none; cursor:pointer; border-bottom:2px solid transparent;">Donors (${allUsersDetailed.donors ? allUsersDetailed.donors.length : 0})</button>
          <button class="form-tab tab-admin-view" data-target="admin-view-patients" style="padding:10px 18px; font-size:13px; font-weight:600; color:#8d8d8d; background:transparent; border:none; cursor:pointer; border-bottom:2px solid transparent;">Patients (${allUsersDetailed.patients ? allUsersDetailed.patients.length : 0})</button>
        </div>
        <div id="admin-view-doctors" class="admin-view-section" style="display:block;">
          <table class="utbl">
            <thead><tr><th>ID</th><th>Doctor Name</th><th>Email</th><th>Phone</th><th>Status</th><th style="text-align:right;">Action</th></tr></thead>
            <tbody>
              ${(allUsersDetailed.doctors || []).map(d => `
                <tr>
                  <td style="font-family:'IBM Plex Mono'; font-size:12px;">#DOC-${d.id}</td>
                  <td><strong>${d.full_name}</strong></td>
                  <td>${d.email}</td>
                  <td>${d.phone || 'N/A'}</td>
                  <td>${d.is_approved ? '<span class="ticker-badge badge-matched">APPROVED</span>' : '<span class="ticker-badge badge-critical">PENDING</span>'}</td>
                  <td style="text-align:right;">
                    <button class="btn-delete-doctor" data-id="${d.id}" data-name="${d.full_name}" style="background:#da1e28; color:#fff; border:none; padding:4px 10px; font-size:11px; border-radius:4px; cursor:pointer;">
                      <i class="fa-solid fa-trash"></i> Remove
                    </button>
                  </td>
                </tr>
              `).join('') || '<tr><td colspan="6" style="text-align:center; color:#6f6f6f; padding:2rem;">No doctors registered yet</td></tr>'}
            </tbody>
          </table>
        </div>
        <div id="admin-view-hospitals" class="admin-view-section" style="display:none;">
          <table class="utbl">
            <thead><tr><th>ID</th><th>Hospital Name</th><th>Email</th><th>City</th><th>Status</th></tr></thead>
            <tbody>
              ${(allUsersDetailed.hospitals || []).map(h => `
                <tr>
                  <td style="font-family:'IBM Plex Mono'; font-size:12px;">#HSP-${h.id}</td>
                  <td><strong>${h.full_name}</strong></td>
                  <td>${h.email}</td>
                  <td>${h.city || 'N/A'}</td>
                  <td>${h.is_approved ? '<span class="ticker-badge badge-matched">APPROVED</span>' : '<span class="ticker-badge badge-critical">PENDING</span>'}</td>
                </tr>
              `).join('') || '<tr><td colspan="5" style="text-align:center; color:#6f6f6f; padding:2rem;">No hospitals registered yet</td></tr>'}
            </tbody>
          </table>
        </div>
        <div id="admin-view-donors" class="admin-view-section" style="display:none;">
          <table class="utbl">
            <thead><tr><th>ID</th><th>Donor Name</th><th>Email</th><th>Blood Type</th><th>Status</th></tr></thead>
            <tbody>
              ${(allUsersDetailed.donors || []).map(d => `
                <tr>
                  <td style="font-family:'IBM Plex Mono'; font-size:12px;">#DNR-${d.id}</td>
                  <td><strong>${d.full_name}</strong></td>
                  <td>${d.email}</td>
                  <td><span class="ticker-badge badge-critical">${d.blood_type || 'N/A'}</span></td>
                  <td>${d.is_approved ? '<span class="ticker-badge badge-matched">APPROVED</span>' : '<span class="ticker-badge badge-critical">PENDING</span>'}</td>
                </tr>
              `).join('') || '<tr><td colspan="5" style="text-align:center; color:#6f6f6f; padding:2rem;">No donors registered yet</td></tr>'}
            </tbody>
          </table>
        </div>
        <div id="admin-view-patients" class="admin-view-section" style="display:none;">
          <table class="utbl">
            <thead><tr><th>ID</th><th>Patient Name</th><th>Email</th><th>Organ Needed</th><th>Status</th></tr></thead>
            <tbody>
              ${(allUsersDetailed.patients || []).map(p => `
                <tr>
                  <td style="font-family:'IBM Plex Mono'; font-size:12px;">#PT-${p.id}</td>
                  <td><strong>${p.full_name}</strong></td>
                  <td>${p.email}</td>
                  <td>${p.organ_needed || 'N/A'}</td>
                  <td><span class="ticker-badge badge-matched">WAITLISTED</span></td>
                </tr>
              `).join('') || '<tr><td colspan="5" style="text-align:center; color:#6f6f6f; padding:2rem;">No patients registered yet</td></tr>'}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  `;
}
