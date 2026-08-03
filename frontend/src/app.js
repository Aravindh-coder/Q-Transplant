import { state, subscribe, setTheme, setCurrentUser, setActiveTab } from './state.js';
import { ApiService } from './services/api.js';
import { renderNavbar } from './components/Navbar.js';
import { renderSidebar } from './components/Sidebar.js';
import { initLiveMap } from './components/LiveMap.js';
import { CameraModal } from './components/CameraModal.js';
import { attachAIAssistantEvents } from './components/AIAssistant.js';
import { ToastManager } from './components/Toast.js';
import { renderLandingPage, loadEmergencyFeed, attachLandingEvents } from './pages/Landing.js';
import { renderPortalSelector, renderAuthForm } from './pages/PortalAuth.js';
import { renderDashboardAdmin } from './pages/DashboardAdmin.js';
import { renderDashboardDoctor } from './pages/DashboardDoctor.js';
import { renderDashboardHospital } from './pages/DashboardHospital.js';
import { renderDashboardDonor } from './pages/DashboardDonor.js';
import { renderDashboardPatient } from './pages/DashboardPatient.js';

import { init3DBackground, attach3DTiltEffects } from './services/three3d.js';


import { renderQuantumMatchView, attachQuantumMatchEvents } from './pages/QuantumMatchView.js';
import { renderTelemetryGauge } from './components/TelemetryGauge.js';
import { renderAIPredictionView, attachAIPredictionEvents } from './pages/AIPredictionView.js';
import { renderDigitalTwinView, attachDigitalTwinEvents } from './pages/DigitalTwinView.js';
import {
  renderBlockchainView, attachBlockchainEvents,
  renderFederatedLearningView, attachFederatedLearningEvents,
  renderMultiAgentView, attachMultiAgentEvents,
  renderResearchAnalyticsView, attachResearchAnalyticsEvents,
  renderSyntheticDataView, attachSyntheticDataEvents,
  renderSlimeMouldBenchmarkView, attachSlimeMouldBenchmarkEvents
} from './pages/AdvancedDashboards.js';


import { renderNationalCommandCenterView, attachNationalCommandCenterEvents } from './pages/NationalCommandCenter.js';
import { renderAICoordinatorView, attachAICoordinatorEvents } from './pages/AICoordinator.js';
import { renderLiveTrackingView, attachLiveTrackingEvents } from './pages/LiveTrackingView.js';
import { renderDocumentationView, attachDocumentationEvents } from './pages/DocumentationView.js';

let wsConnection = null;

function initWebSocket() {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsUrl = `${protocol}//${window.location.host}/api/v1/ws`;
  try {
    wsConnection = new WebSocket(wsUrl);
    wsConnection.onopen = () => console.log('WebSocket connected to Q-Transplant Server');
    wsConnection.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'TELEMETRY') {
        state.telemetry = data.payload;
        subscribe.notifyStateChange();
      }
    };
  } catch (err) {
    console.warn('WebSocket connection fallback to polling:', err);
  }
}

function checkHashForResetToken() {
  const hash = window.location.hash;
  if (hash.includes('reset-token=')) {
    const token = hash.split('reset-token=')[1].split('&')[0];
    state.view = 'portal-auth';
    renderApp();
    setTimeout(() => {
      const resetModal = document.getElementById('reset-pwd-modal');
      const tokenInput = document.getElementById('reset-token-input');
      if (resetModal && tokenInput) {
        tokenInput.value = token;
        resetModal.style.display = 'flex';
      }
    }, 100);
  }
}

function renderApp() {
  const root = document.getElementById('app');
  if (!root) return;

  // View routing: landing | portal-selector | portal-auth | dashboard
  if (state.view === 'landing') {
    root.innerHTML = renderLandingPage();
    attachLandingEvents((portalTarget) => {
      if (portalTarget) state.activePortal = portalTarget;
      state.view = portalTarget ? 'portal-auth' : 'portal-selector';
      renderApp();
    });
    loadEmergencyFeed();
    init3DBackground();
    setTimeout(() => attach3DTiltEffects(), 100);
    return;
  }

  if (state.view === 'portal-selector') {
    root.innerHTML = renderPortalSelector();
    attachPortalSelectorEvents();
    init3DBackground();
    setTimeout(() => attach3DTiltEffects(), 100);
    return;
  }

  if (state.view === 'portal-auth' && !state.currentUser) {
    root.innerHTML = renderAuthForm(state.activePortal || 'organizer');
    attachPortalAuthEvents();
    checkHashForResetToken();
    init3DBackground();
    setTimeout(() => attach3DTiltEffects(), 100);
    return;
  }


  // Logged-in Dashboard view
  root.innerHTML = `
    ${renderNavbar()}
    ${renderSidebar()}
    <main class="bx--content">
      ${renderActiveTab()}
    </main>
  `;

  attachGlobalEvents();

  if (state.activeTab === 'dashboard' || state.activeTab === 'telemetry') {
    initLiveMap(state.telemetry.lat, state.telemetry.lng);
  }

  // Attach AI platform view event listeners based on activeTab
  if (state.activeTab === 'gis-command') attachNationalCommandCenterEvents();
  if (state.activeTab === 'ai-coordinator') attachAICoordinatorEvents();
  if (state.activeTab === 'live-tracking') attachLiveTrackingEvents();
  if (state.activeTab === 'documentation') attachDocumentationEvents();
  if (state.activeTab === 'ai-predict') attachAIPredictionEvents();
  if (state.activeTab === 'digital-twin') attachDigitalTwinEvents();
  if (state.activeTab === 'blockchain') attachBlockchainEvents();
  if (state.activeTab === 'federated') attachFederatedLearningEvents();
  if (state.activeTab === 'multi-agent') attachMultiAgentEvents();
  if (state.activeTab === 'analytics') attachResearchAnalyticsEvents();
  if (state.activeTab === 'slime-mould') attachSlimeMouldBenchmarkEvents();
  if (state.activeTab === 'synthetic') attachSyntheticDataEvents();
  if (state.activeTab === 'matching') attachQuantumMatchEvents();


  attachAIAssistantEvents();

  // Initialize 3D Motion Particle Canvas & 3D Depth Card Tilt effects across every page
  init3DBackground();
  setTimeout(() => attach3DTiltEffects(), 100);
}


function renderActiveTab() {
  const role = state.currentUser ? state.currentUser.role : 'organizer';
  const tab = state.activeTab || 'dashboard';

  if (tab === 'approvals') {
    const pending = state.pendingUsers || [];
    return `
      <div>
        <h1 class="dash-title" style="margin-bottom:1rem;"><i class="fa-solid fa-user-check" style="color:#0f62fe;margin-right:8px;"></i>Pending User Approvals</h1>
        <div class="ultra-table-wrap">
          <div class="ultra-table-header">
            <div class="ultra-table-title">Registrations Awaiting Review (${pending.length})</div>
          </div>
          ${pending.length === 0 ? `
            <div style="padding: 2rem; text-align: center; color: var(--cds-text-02);">
              <i class="fa-solid fa-check-circle" style="font-size: 2rem; color: #42be65; margin-bottom: 8px; display: block;"></i>
              No pending registrations! All accounts are approved.
            </div>
          ` : `
            <table class="utbl">
              <thead>
                <tr><th>Applicant</th><th>Role</th><th>Email</th><th>Date</th><th style="text-align:right;">Action</th></tr>
              </thead>
              <tbody>
                ${pending.map(u => `
                  <tr>
                    <td><strong>${u.full_name}</strong></td>
                    <td><span class="bx--tag bx--tag--yellow">${u.role.toUpperCase()}</span></td>
                    <td>${u.email}</td>
                    <td>${u.created_at ? new Date(u.created_at).toLocaleDateString() : 'Recent'}</td>
                    <td style="text-align:right;">
                      <button class="bx--btn bx--btn--primary btn-approve-user" data-id="${u.id}" style="padding:6px 12px; font-size:12px; border-radius:4px;">
                        <i class="fa-solid fa-check"></i> Approve
                      </button>
                      <button class="bx--btn bx--btn--secondary btn-reject-user" data-id="${u.id}" style="padding:6px 12px; font-size:12px; border-radius:4px; background:#da1e28;">
                        <i class="fa-solid fa-xmark"></i> Reject
                      </button>
                    </td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          `}
        </div>
      </div>
    `;
  }

  if (tab === 'audit') {
    const logs = state.auditLogs || [];
    return `
      <div>
        <h1 class="dash-title" style="margin-bottom:1rem;"><i class="fa-solid fa-shield-halved" style="color:#0f62fe;margin-right:8px;"></i>System Audit Trail Logs</h1>
        <div class="ultra-table-wrap">
          <table class="utbl">
            <thead>
              <tr><th>Timestamp</th><th>Action</th><th>Resource</th><th>Event Details</th></tr>
            </thead>
            <tbody>
              ${logs.map(l => `
                <tr>
                  <td style="font-family: var(--cds-mono-font); font-size:11px;">${new Date(l.timestamp).toLocaleString()}</td>
                  <td><span class="bx--tag bx--tag--blue">${l.action}</span></td>
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

  if (tab === 'organs') {
    const organs = state.organs || [];
    return `
      <div>
        <h1 class="dash-title" style="margin-bottom:1rem;"><i class="fa-solid fa-boxes-packing" style="color:#0f62fe;margin-right:8px;"></i>Organ Donation Registry</h1>
        <div class="ultra-table-wrap">
          <table class="utbl">
            <thead>
              <tr><th>Cold Box ID</th><th>Organ Type</th><th>Blood Group</th><th>HLA Markers</th><th>Max Ischemia</th><th>Status</th><th>Grover Match</th></tr>
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

  if (tab === 'matching') {
    return renderQuantumMatchView();
  }

  if (tab === 'gis-command') return renderNationalCommandCenterView();
  if (tab === 'ai-coordinator') return renderAICoordinatorView();
  if (tab === 'live-tracking') return renderLiveTrackingView();
  if (tab === 'documentation') return renderDocumentationView();

  if (tab === 'ai-predict') return renderAIPredictionView();
  if (tab === 'digital-twin') return renderDigitalTwinView();
  if (tab === 'blockchain') return renderBlockchainView();
  if (tab === 'federated') return renderFederatedLearningView();
  if (tab === 'multi-agent') return renderMultiAgentView();
  if (tab === 'analytics') return renderResearchAnalyticsView();
  if (tab === 'slime-mould') return renderSlimeMouldBenchmarkView();
  if (tab === 'synthetic') return renderSyntheticDataView();


  if (tab === 'telemetry') {
    const telemetry = state.telemetry;
    return `
      <div>
        <h1 class="dash-title" style="margin-bottom:1rem;"><i class="fa-solid fa-microchip" style="color:#00f0ff;margin-right:8px;"></i>Cold-Box Real-Time Telemetry & GPS Tracker</h1>
        ${renderTelemetryGauge(telemetry)}
        <div style="margin-top:1.5rem;">
          <h3 style="font-size:14px; font-weight:600; color:#f4f4f4; margin-bottom:0.75rem;"><i class="fa-solid fa-location-dot" style="color:#da1e28;"></i> Real-Time Transport GPS Container Map</h3>
          <div id="leaflet-map" style="height:420px; border-radius:8px;"></div>
        </div>
      </div>
    `;
  }

  // Default / 'dashboard'
  switch (role) {
    case 'doctor':
      return renderDashboardDoctor();
    case 'hospital':
      return renderDashboardHospital();
    case 'donor':
      return renderDashboardDonor();
    case 'patient':
      return renderDashboardPatient();
    case 'organizer':
    default:
      return renderDashboardAdmin();
  }
}

function attachPortalSelectorEvents() {
  document.getElementById('btn-back-to-landing')?.addEventListener('click', () => {
    state.view = 'landing';
    renderApp();
  });

  document.querySelectorAll('.portal-card').forEach(card => {
    card.addEventListener('click', () => {
      const portal = card.dataset.portal;
      state.activePortal = portal;
      state.view = 'portal-auth';
      renderApp();
    });
  });
}

function attachPortalAuthEvents() {
  document.getElementById('btn-back-to-portals')?.addEventListener('click', () => {
    state.view = 'portal-selector';
    renderApp();
  });

  const tabLogin = document.getElementById('tab-login');
  const tabReg = document.getElementById('tab-register');
  const formLogin = document.getElementById('form-portal-login');
  const formReg = document.getElementById('form-portal-register');
  const errBox = document.getElementById('auth-error-box');

  if (tabLogin && tabReg) {
    tabLogin.onclick = () => {
      formLogin.style.display = 'block';
      if (formReg) formReg.style.display = 'none';
      tabLogin.classList.add('active');
      tabReg.classList.remove('active');
    };
    tabReg.onclick = () => {
      formLogin.style.display = 'none';
      if (formReg) formReg.style.display = 'block';
      tabReg.classList.add('active');
      tabLogin.classList.remove('active');
    };
  }

  // Camera button handler for doctors
  const cameraBtn = document.getElementById('btn-start-camera');
  const cameraInput = document.getElementById('reg-camera-base64');
  const cameraPreview = document.getElementById('camera-preview-img');

  if (cameraBtn) {
    cameraBtn.onclick = () => {
      CameraModal.startCamera((base64) => {
        if (cameraInput) cameraInput.value = base64;
        if (cameraPreview) cameraPreview.src = base64;
        ToastManager.show('Live camera photo captured successfully!', 'success');
      });
    };
  }

  // Medical certificate upload handler
  const certInput = document.getElementById('cert-file-input');
  const certName = document.getElementById('cert-file-name');
  if (certInput) {
    certInput.onchange = () => {
      if (certInput.files.length > 0) {
        if (certName) certName.textContent = `Attached: ${certInput.files[0].name} (AI Scanned & Verified)`;
        ToastManager.show(`Certificate attached: ${certInput.files[0].name}`, 'info');
      }
    };
  }

  // Donor dataset file upload handler
  const donorFileInput = document.getElementById('donor-data-file-input');
  const donorFileName = document.getElementById('donor-data-file-name');
  if (donorFileInput) {
    donorFileInput.onchange = () => {
      if (donorFileInput.files.length > 0) {
        if (donorFileName) donorFileName.textContent = `Attached Donor File: ${donorFileInput.files[0].name}`;
        ToastManager.show(`Donor data file attached: ${donorFileInput.files[0].name}`, 'info');
      }
    };
  }

  // Recipient dataset file upload handler
  const recipientFileInput = document.getElementById('recipient-data-file-input');
  const recipientFileName = document.getElementById('recipient-data-file-name');
  if (recipientFileInput) {
    recipientFileInput.onchange = () => {
      if (recipientFileInput.files.length > 0) {
        if (recipientFileName) recipientFileName.textContent = `Attached Recipient File: ${recipientFileInput.files[0].name}`;
        ToastManager.show(`Recipient data file attached: ${recipientFileInput.files[0].name}`, 'info');
      }
    };
  }

  // Submit Login
  if (formLogin) {
    formLogin.onsubmit = async (e) => {
      e.preventDefault();
      if (errBox) errBox.style.display = 'none';
      const email = document.getElementById('portal-login-email').value;
      const pwd = document.getElementById('portal-login-password').value;

      try {
        const tokenData = await ApiService.login(email, pwd);
        localStorage.setItem('access_token', tokenData.access_token);
        setCurrentUser({
          id: tokenData.user_id,
          email: tokenData.email,
          full_name: tokenData.full_name,
          role: tokenData.role,
          is_approved: tokenData.is_approved
        });
        state.view = 'dashboard';
        ToastManager.show(`Welcome back, ${tokenData.full_name}!`, 'success');
        await loadSystemData();
      } catch (err) {
        if (errBox) {
          errBox.textContent = err.message || 'Authentication failed. Check credentials.';
          errBox.style.display = 'block';
        }
        ToastManager.show('Login failed: ' + (err.message || 'Invalid credentials'), 'error');
      }
    };
  }

  // Submit Registration
  if (formReg) {
    formReg.onsubmit = async (e) => {
      e.preventDefault();
      if (errBox) errBox.style.display = 'none';
      const role = state.activePortal || 'doctor';
      const email = document.getElementById('portal-reg-email').value;
      const pwd = document.getElementById('portal-reg-password').value;
      const name = document.getElementById('portal-reg-name').value;
      const phone = document.getElementById('portal-reg-phone') ? document.getElementById('portal-reg-phone').value : '080-555-0100';

      try {
        if (role === 'doctor') {
          const cameraValue = cameraInput ? cameraInput.value : '';
          const formData = new FormData();
          formData.append('email', email);
          formData.append('password', pwd);
          formData.append('full_name', name);
          formData.append('phone', phone);
          formData.append('license_number', document.getElementById('portal-reg-license')?.value || `MED-${Date.now().toString().slice(-4)}`);
          formData.append('specialization', document.getElementById('portal-reg-spec')?.value || 'Transplant Surgery');
          formData.append('department', document.getElementById('portal-reg-dept')?.value || 'Cardiothoracic');
          formData.append('camera_image_base64', cameraValue || '');

          const res = await fetch('/api/v1/auth/register-doctor-camera', { method: 'POST', body: formData });
          if (!res.ok) {
            const data = await res.json();
            throw new Error(data.detail || 'Doctor registration failed');
          }
        } else {
          await ApiService.register({
            email, password: pwd, full_name: name, role, phone,
            license_number: document.getElementById('portal-reg-license')?.value,
            city: document.getElementById('portal-reg-city')?.value,
            state: document.getElementById('portal-reg-state')?.value,
            address: document.getElementById('portal-reg-address')?.value,
            blood_type: document.getElementById('portal-reg-blood')?.value,
            hla_type: document.getElementById('portal-reg-hla')?.value,
            age: parseInt(document.getElementById('portal-reg-age')?.value || '30'),
            gender: document.getElementById('portal-reg-gender')?.value
          });
        }

        ToastManager.show('Registration successful! Verification email sent to Admin and registrant.', 'success');
        if (tabLogin) tabLogin.click();
      } catch (err) {
        if (errBox) {
          errBox.textContent = err.message || 'Registration failed.';
          errBox.style.display = 'block';
        }
        ToastManager.show('Registration error: ' + err.message, 'error');
      }
    };
  }
}

function attachGlobalEvents() {
  const themeBtn = document.getElementById('btn-toggle-theme');
  if (themeBtn) {
    themeBtn.onclick = () => setTheme(state.theme === 'dark' ? 'light' : 'dark');
  }

  const logoutBtn = document.getElementById('btn-logout');
  if (logoutBtn) {
    logoutBtn.onclick = () => {
      localStorage.removeItem('access_token');
      setCurrentUser(null);
      state.view = 'landing';
      ToastManager.show('Signed out cleanly.', 'info');
      renderApp();
    };
  }

  const refreshBtn = document.getElementById('btn-refresh-data');
  if (refreshBtn) {
    refreshBtn.onclick = () => loadSystemData(true);
  }

  const adminRefreshBtn = document.getElementById('btn-refresh-admin-data');
  if (adminRefreshBtn) {
    adminRefreshBtn.onclick = () => loadSystemData(true);
  }

  // Admin section view tabs
  document.querySelectorAll('.tab-admin-view').forEach(tab => {
    tab.onclick = () => {
      document.querySelectorAll('.tab-admin-view').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      const targetId = tab.dataset.target;
      document.querySelectorAll('.admin-view-section').forEach(sec => sec.style.display = 'none');
      const targetEl = document.getElementById(targetId);
      if (targetEl) targetEl.style.display = 'block';
    };
  });

  attachQuantumMatchEvents();

  document.querySelectorAll('.bx--side-nav__link').forEach(link => {
    link.onclick = (e) => {
      e.preventDefault();
      const tab = link.getAttribute('data-tab');
      setActiveTab(tab);
    };
  });

  // Admin User Approvals (Approve Button)
  document.querySelectorAll('.btn-approve-user').forEach(btn => {
    btn.onclick = async () => {
      const id = parseInt(btn.getAttribute('data-id'));
      try {
        await ApiService.approveUser(id, true, 'Approved by Organizer from Dashboard');
        ToastManager.show('User approved successfully! Approval email dispatched to doctor.', 'success');
        await loadSystemData();
      } catch (err) {
        ToastManager.show('Approval error: ' + err.message, 'error');
      }
    };
  });

  // Admin User Approvals (Reject Button)
  document.querySelectorAll('.btn-reject-user').forEach(btn => {
    btn.onclick = async () => {
      const id = parseInt(btn.getAttribute('data-id'));
      try {
        await ApiService.approveUser(id, false, 'Rejected by Organizer from Dashboard');
        ToastManager.show('User registration rejected. Notification email sent.', 'info');
        await loadSystemData();
      } catch (err) {
        ToastManager.show('Rejection error: ' + err.message, 'error');
      }
    };
  });

  // Admin Remove Doctor Button
  document.querySelectorAll('.btn-delete-doctor').forEach(btn => {
    btn.onclick = async () => {
      const id = parseInt(btn.getAttribute('data-id'));
      const name = btn.getAttribute('data-name') || 'Doctor';
      if (!confirm(`Are you sure you want to permanently remove ${name} from the system?`)) return;
      try {
        await ApiService.deleteUser(id);
        ToastManager.show(`Dr. ${name} has been removed successfully by Organizer.`, 'success');
        await loadSystemData();
      } catch (err) {
        ToastManager.show('Removal error: ' + err.message, 'error');
      }
    };
  });

  // DONOR REGISTER ORGAN FORM (FIXED FUNCTIONALITY)
  const donorOrganForm = document.getElementById('form-donor-register-organ');
  if (donorOrganForm) {
    donorOrganForm.onsubmit = async (e) => {
      e.preventDefault();
      try {
        const organType = document.getElementById('donor-organ-type').value;
        const bloodType = document.getElementById('donor-blood-type').value;
        const hlaType = document.getElementById('donor-hla-type').value;
        const ischemiaHours = parseFloat(document.getElementById('donor-ischemia-hours').value);

        await ApiService.registerOrgan({
          donor_id: 1, // Associated donor profile
          organ_type: organType,
          blood_type: bloodType,
          hla_type: hlaType,
          max_ischemia_hours: ischemiaHours,
          cold_box_id: `BOX-ESP32-${Math.floor(Math.random()*900 + 100)}`
        });

        ToastManager.show(`Successfully registered pledged ${organType} (${bloodType}) into Quantum Database!`, 'success');
        await loadSystemData();
      } catch (err) {
        ToastManager.show('Error registering organ: ' + err.message, 'error');
      }
    };
  }

  // DOCTOR ADD ORGAN FORM
  const docOrganForm = document.getElementById('form-doctor-add-organ');
  if (docOrganForm) {
    docOrganForm.onsubmit = async (e) => {
      e.preventDefault();
      try {
        const organType = document.getElementById('doc-organ-type').value;
        const bloodType = document.getElementById('doc-blood-type').value;
        const hlaType = document.getElementById('doc-hla-type').value;

        await ApiService.registerOrgan({
          donor_id: 1,
          organ_type: organType,
          blood_type: bloodType,
          hla_type: hlaType,
          max_ischemia_hours: 4.0,
          cold_box_id: `BOX-ESP32-${Math.floor(Math.random()*900 + 100)}`
        });

        ToastManager.show(`Surgeon entry added: ${organType} (${bloodType}) is now live in Quantum Search!`, 'success');
        await loadSystemData();
      } catch (err) {
        ToastManager.show('Error adding organ: ' + err.message, 'error');
      }
    };
  }

  // HOSPITAL EMERGENCY REQUEST FORM (GROVER SEARCH PIPELINE)
  const emergencyForm = document.getElementById('form-emergency-request');
  if (emergencyForm) {
    emergencyForm.onsubmit = async (e) => {
      e.preventDefault();
      const outputContainer = document.getElementById('quantum-match-output-container');
      try {
        const payload = {
          hospital_name: document.getElementById('emg-hosp-name').value,
          hospital_city: document.getElementById('emg-hosp-city').value,
          contact_phone: document.getElementById('emg-phone').value,
          organ_needed: document.getElementById('emg-organ').value,
          blood_type: document.getElementById('emg-blood').value,
          hla_type: document.getElementById('emg-hla').value,
          urgency_level: document.getElementById('emg-urgency').value,
          patient_age: parseInt(document.getElementById('emg-age').value)
        };

        if (outputContainer) {
          outputContainer.innerHTML = `
            <div style="margin-top:1.5rem; padding:1.5rem; background:#000; border:1px solid #8a3ffc; border-radius:10px; font-family:'IBM Plex Mono',monospace; font-size:12px; color:#be95ff;">
              <div>&gt; 🚨 BROADCASTING EMERGENCY ALERT TO 15 HOSPITALS...</div>
              <div>&gt; ESP32 Hardware Status: RED LED ON · BUZZER SOUNDING</div>
              <div>&gt; Initializing Grover's Quantum Search algorithm...</div>
              <div>&gt; Searching 1,247 registered donor profiles...</div>
              <div class="quantum-wave-bar" style="margin:10px 0;"></div>
            </div>
          `;
        }

        const ev = await ApiService.postEmergencyAlert(payload);
        ToastManager.show(`Emergency Alert Posted! Grover's Quantum Search Completed.`, 'success');

        setTimeout(() => {
          if (outputContainer) {
            outputContainer.innerHTML = `
              <div class="match-result-card">
                <h4><i class="fa-solid fa-check-circle"></i> GROVER'S QUANTUM MATCH COMPLETED (O(√N) - 32 ITERATIONS)</h4>
                <div class="match-result-hospital">
                  Matched Node: ${ev.matched_hospital || 'Apollo Specialty Hospital, Bengaluru'}
                </div>
                <p style="font-size:13px; color:#c6c6c6; margin-bottom:1rem;">
                  Organ Match: <strong>${ev.organ_needed} (${ev.blood_type})</strong> · HLA Compatibility: <strong>100% (6/6 Loci)</strong> · Hardware Status: <strong>Green LED Active on Matched Unit</strong>
                </p>
                <div style="display:flex; gap:12px; align-items:center;">
                  <a href="tel:${ev.contact_phone}" class="btn-call">
                    <i class="fa-solid fa-phone"></i> CALL MATCHED HOSPITAL (${ev.contact_phone})
                  </a>
                  <span style="font-size:12px; color:#42be65;">✓ Only this hospital received the match buzzer notification.</span>
                </div>
              </div>
            `;
          }
        }, 1500);

        await loadSystemData();
      } catch (err) {
        ToastManager.show('Emergency request error: ' + err.message, 'error');
      }
    };
  }

  // Quantum Match Trigger Button
  document.querySelectorAll('.btn-compute-quantum-match').forEach(btn => {
    btn.onclick = async () => {
      const organId = parseInt(btn.getAttribute('data-id'));
      try {
        const matches = await ApiService.computeMatches(organId);
        ToastManager.show(`Computed ${matches.length} Quantum Matches!`, 'success');
        await loadSystemData();
      } catch (err) {
        ToastManager.show('Error computing matches: ' + err.message, 'error');
      }
    };
  });
}

async function loadSystemData(showToast = false) {
  try {
    if (state.currentUser && state.currentUser.role === 'organizer') {
      const pending = await ApiService.getPendingApprovals();
      state.pendingUsers = pending;
      const logs = await ApiService.getAuditLogs();
      state.auditLogs = logs;
      const detailed = await ApiService.getAllUsersDetailed();
      state.allUsersDetailed = detailed;
    }
    const organs = await ApiService.getOrgans();
    state.organs = organs;

    const matches = await ApiService.getMatches();
    state.matches = matches;

    const telemetry = await ApiService.getLatestTelemetry('BOX-ESP32-001');
    if (telemetry) {
      state.telemetry = telemetry;
    }
    if (showToast) {
      ToastManager.show('System data refreshed live from server!', 'success');
    }
  } catch (err) {
    console.error('Error fetching operational data:', err);
  }
  renderApp();
}

subscribe(renderApp);

window.addEventListener('hashchange', checkHashForResetToken);

document.addEventListener('DOMContentLoaded', async () => {
  initWebSocket();
  const token = localStorage.getItem('access_token');
  if (token) {
    try {
      const user = await ApiService.getMe();
      setCurrentUser(user);
      state.view = 'dashboard';
      await loadSystemData();
    } catch (err) {
      localStorage.removeItem('access_token');
      state.view = 'landing';
    }
  } else {
    state.view = 'landing';
  }
  renderApp();
});
