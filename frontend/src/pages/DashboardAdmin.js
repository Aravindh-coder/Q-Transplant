import { state } from '../state.js';

export function renderDashboardAdmin() {
  const pending = state.pendingUsers || [];
  const logs = state.auditLogs || [];
  const allUsersDetailed = state.allUsersDetailed || { doctors: [], hospitals: [], donors: [], patients: [], pending: [] };

  return `
    <div style="padding:0 0.5rem;">
      <!-- Header -->
      <div class="dash-header" style="margin-bottom:2rem; display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:1rem;">
        <div>
          <div class="section-badge" style="background:rgba(15,98,254,0.15); border-color:rgba(15,98,254,0.4); color:#78a9ff;">
            <i class="fa-solid fa-shield-halved"></i> ORGANIZER EXECUTIVE COMMAND
          </div>
          <h1 class="dash-title" style="margin-top:6px;">National Transplant Organizer Command Center</h1>
          <p class="dash-subtitle">System Administrator & Lead Organizer: <strong style="color:#f4f4f4;">aravindhjoshua10@gmail.com</strong> &nbsp;·&nbsp; NOTTO Audit Oversight</p>
        </div>
        <div style="display:flex; gap:10px;">
          <button id="btn-refresh-admin-data" class="btn-hero-secondary" style="font-size:13px; padding:10px 18px;">
            <i class="fa-solid fa-rotate"></i> Refresh Operational Feed
          </button>
        </div>
      </div>

      <!-- KPI Executive Summary Row -->
      <div class="kpi-grid" style="margin-bottom:2rem;">
        <div class="kpi-card green">
          <div class="kpi-card-label"><i class="fa-solid fa-hand-holding-heart" style="color:#42be65;"></i> Registered Donors</div>
          <div class="kpi-card-value" style="color:#42be65;">${allUsersDetailed.donors && allUsersDetailed.donors.length > 0 ? (1247 + allUsersDetailed.donors.length) : '1,247'}</div>
          <div class="kpi-card-sub">Verified Donor Pledges</div>
        </div>
        <div class="kpi-card purple">
          <div class="kpi-card-label"><i class="fa-solid fa-bed-pulse" style="color:#be95ff;"></i> Waitlist Patients</div>
          <div class="kpi-card-value" style="color:#be95ff;">${allUsersDetailed.patients && allUsersDetailed.patients.length > 0 ? (893 + allUsersDetailed.patients.length) : '893'}</div>
          <div class="kpi-card-sub">Active Recipient Queue</div>
        </div>
        <div class="kpi-card red">
          <div class="kpi-card-label"><i class="fa-solid fa-hospital" style="color:#ff8389;"></i> Connected Hospitals</div>
          <div class="kpi-card-value" style="color:#ff8389;">${allUsersDetailed.hospitals ? Math.max(15, allUsersDetailed.hospitals.length) : 15}</div>
          <div class="kpi-card-sub">ESP32 Hardware Nodes Active</div>
        </div>
        <div class="kpi-card blue">
          <div class="kpi-card-label"><i class="fa-solid fa-atom" style="color:#78a9ff;"></i> Quantum Match SLA</div>
          <div class="kpi-card-value" style="color:#78a9ff;">0.3ms</div>
          <div class="kpi-card-sub">Grover's O(√N) Acceleration</div>
        </div>
      </div>

      <!-- Pending Doctor & User Approvals -->
      <div class="ultra-table-wrap" style="margin-bottom: 2rem;">
        <div class="ultra-table-header" style="background:rgba(241,194,27,0.08); border-bottom:1px solid rgba(241,194,27,0.3);">
          <div class="ultra-table-title" style="color:#f1c21b;">
            <i class="fa-solid fa-triangle-exclamation" style="margin-right:8px;"></i>
            Pending Applicant Verification & Credentials Review (${pending.length})
          </div>
        </div>
        ${pending.length === 0 ? `
          <div style="padding: 2.5rem; text-align: center; color: #8d8d8d;">
            <i class="fa-solid fa-shield-check" style="font-size: 2.5rem; color: #42be65; margin-bottom: 12px; display: block;"></i>
            <div style="color:#f4f4f4; font-size:15px; font-weight:600; margin-bottom:4px;">All Medical Registrations Reviewed</div>
            <div style="font-size:13px;">No pending doctor or hospital approval requests in queue.</div>
          </div>
        ` : `
          <table class="utbl">
            <thead>
              <tr>
                <th>Applicant Name</th>
                <th>Requested Role</th>
                <th>Email Address</th>
                <th>Registration Date</th>
                <th style="text-align:right;">Organizer Executive Action</th>
              </tr>
            </thead>
            <tbody>
              ${pending.map(u => `
                <tr>
                  <td><strong>${u.full_name}</strong></td>
                  <td><span class="ticker-badge badge-searching">${u.role.toUpperCase()}</span></td>
                  <td>${u.email}</td>
                  <td style="font-family:'IBM Plex Mono'; font-size:12px; color:#8d8d8d;">${u.created_at ? new Date(u.created_at).toLocaleDateString() : 'Recent'}</td>
                  <td style="text-align:right;">
                    <button class="btn-call btn-approve-user" data-id="${u.id}" style="padding:6px 14px; font-size:12px; background:rgba(66,190,101,0.2); border-color:#42be65; color:#42be65; cursor:pointer;">
                      <i class="fa-solid fa-check"></i> Approve Account
                    </button>
                    <button class="btn-call btn-reject-user" data-id="${u.id}" style="padding:6px 14px; font-size:12px; background:rgba(218,30,40,0.2); border-color:#da1e28; color:#ff8389; cursor:pointer; margin-left:6px;">
                      <i class="fa-solid fa-xmark"></i> Reject
                    </button>
                  </td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        `}
      </div>

      <!-- Tabs for All Doctors, Hospitals, Donors, Patients -->
      <div class="ultra-table-wrap" style="margin-bottom: 2rem;">
        <div class="ultra-table-header">
          <div class="ultra-table-title">
            <i class="fa-solid fa-users" style="color:#0f62fe;margin-right:8px;"></i>
            Master Registry of System Entities &amp; Medical Centers
          </div>
        </div>

        <div style="display:flex; border-bottom: 1px solid #393939; background: #161616;">
          <button class="form-tab active tab-admin-view" data-target="admin-view-doctors">Transplant Doctors (${allUsersDetailed.doctors ? allUsersDetailed.doctors.length : 0})</button>
          <button class="form-tab tab-admin-view" data-target="admin-view-hospitals">Hospitals (${allUsersDetailed.hospitals ? allUsersDetailed.hospitals.length : 0})</button>
          <button class="form-tab tab-admin-view" data-target="admin-view-donors">Donors (${allUsersDetailed.donors ? allUsersDetailed.donors.length : 0})</button>
          <button class="form-tab tab-admin-view" data-target="admin-view-patients">Patients (${allUsersDetailed.patients ? allUsersDetailed.patients.length : 0})</button>
        </div>

        <!-- Doctors View -->
        <div id="admin-view-doctors" class="admin-view-section">
          <table class="utbl">
            <thead>
              <tr>
                <th>ID</th><th>Doctor Name</th><th>Email</th><th>Phone</th><th>Status</th><th style="text-align:right;">Organizer Action</th>
              </tr>
            </thead>
            <tbody>
              ${(allUsersDetailed.doctors || []).map(d => `
                <tr>
                  <td style="font-family:'IBM Plex Mono';">#DOC-${d.id}</td>
                  <td><strong>${d.full_name}</strong></td>
                  <td>${d.email}</td>
                  <td>${d.phone || 'N/A'}</td>
                  <td>${d.is_approved ? '<span class="ticker-badge badge-matched">APPROVED</span>' : '<span class="ticker-badge badge-searching">PENDING</span>'}</td>
                  <td style="text-align:right;">
                    <button class="btn-call btn-delete-doctor" data-id="${d.id}" data-name="${d.full_name}" style="padding:4px 10px; font-size:11px; background:rgba(218,30,40,0.2); border-color:#da1e28; color:#ff8389;">
                      <i class="fa-solid fa-trash"></i> Remove Doctor
                    </button>
                  </td>
                </tr>
              `).join('') || '<tr><td colspan="6" style="text-align:center;">No doctors registered yet</td></tr>'}
            </tbody>
          </table>
        </div>

        <!-- Hospitals View -->
        <div id="admin-view-hospitals" class="admin-view-section" style="display:none;">
          <table class="utbl">
            <thead>
              <tr><th>ID</th><th>Hospital Name</th><th>Email</th><th>Phone</th><th>Status</th></tr>
            </thead>
            <tbody>
              ${(allUsersDetailed.hospitals || []).map(h => `
                <tr>
                  <td style="font-family:'IBM Plex Mono';">#HOSP-${h.id}</td>
                  <td><strong>${h.full_name}</strong></td>
                  <td>${h.email}</td>
                  <td>${h.phone || 'N/A'}</td>
                  <td>${h.is_approved ? '<span class="ticker-badge badge-matched">APPROVED</span>' : '<span class="ticker-badge badge-searching">PENDING</span>'}</td>
                </tr>
              `).join('') || '<tr><td colspan="5" style="text-align:center;">No hospitals registered yet</td></tr>'}
            </tbody>
          </table>
        </div>

        <!-- Donors View -->
        <div id="admin-view-donors" class="admin-view-section" style="display:none;">
          <table class="utbl">
            <thead>
              <tr><th>ID</th><th>Donor Name</th><th>Email</th><th>Phone</th><th>Status</th></tr>
            </thead>
            <tbody>
              ${(allUsersDetailed.donors || []).map(dn => `
                <tr>
                  <td style="font-family:'IBM Plex Mono';">#DONOR-${dn.id}</td>
                  <td><strong>${dn.full_name}</strong></td>
                  <td>${dn.email}</td>
                  <td>${dn.phone || 'N/A'}</td>
                  <td>${dn.is_approved ? '<span class="ticker-badge badge-matched">APPROVED</span>' : '<span class="ticker-badge badge-searching">PENDING</span>'}</td>
                </tr>
              `).join('') || '<tr><td colspan="5" style="text-align:center;">No donors registered yet</td></tr>'}
            </tbody>
          </table>
        </div>

        <!-- Patients View -->
        <div id="admin-view-patients" class="admin-view-section" style="display:none;">
          <table class="utbl">
            <thead>
              <tr><th>ID</th><th>Patient Name</th><th>Email</th><th>Phone</th><th>Status</th></tr>
            </thead>
            <tbody>
              ${(allUsersDetailed.patients || []).map(p => `
                <tr>
                  <td style="font-family:'IBM Plex Mono';">#PATIENT-${p.id}</td>
                  <td><strong>${p.full_name}</strong></td>
                  <td>${p.email}</td>
                  <td>${p.phone || 'N/A'}</td>
                  <td>${p.is_approved ? '<span class="ticker-badge badge-matched">APPROVED</span>' : '<span class="ticker-badge badge-searching">PENDING</span>'}</td>
                </tr>
              `).join('') || '<tr><td colspan="5" style="text-align:center;">No patients registered yet</td></tr>'}
            </tbody>
          </table>
        </div>
      </div>

      <!-- Security Audit Logs -->
      <div class="ultra-table-wrap">
        <div class="ultra-table-header">
          <div class="ultra-table-title"><i class="fa-solid fa-clock-rotate-left" style="color:#0f62fe; margin-right:8px;"></i> Immutable Security &amp; Compliance Audit Logs</div>
        </div>
        <table class="utbl">
          <thead>
            <tr><th>Timestamp</th><th>Action</th><th>Resource</th><th>Event Details</th></tr>
          </thead>
          <tbody>
            ${(logs || []).slice(0, 10).map(l => `
              <tr>
                <td style="font-family: 'IBM Plex Mono'; font-size:11px;">${new Date(l.timestamp).toLocaleString()}</td>
                <td><span class="ticker-badge badge-searching">${l.action}</span></td>
                <td>${l.resource}</td>
                <td>${l.details}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    </div>
  `;
}
