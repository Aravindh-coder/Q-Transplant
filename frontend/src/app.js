import { state, subscribe, setTheme, setCurrentUser, setActiveTab } from './state.js';
import { ApiService } from './services/api.js';
import { renderNavbar } from './components/Navbar.js';
import { renderSidebar } from './components/Sidebar.js';
import { initLiveMap } from './components/LiveMap.js';
import { CameraModal } from './components/CameraModal.js';
import { attachAIAssistantEvents } from './components/AIAssistant.js';
import { ToastManager } from './components/Toast.js';
import { renderLoginView } from './pages/Login.js';
import { renderDashboardAdmin } from './pages/DashboardAdmin.js';
import { renderDashboardDoctor } from './pages/DashboardDoctor.js';
import { renderDashboardHospital } from './pages/DashboardHospital.js';
import { renderDashboardDonor } from './pages/DashboardDonor.js';
import { renderDashboardPatient } from './pages/DashboardPatient.js';

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

function renderApp() {
  const root = document.getElementById('app');
  if (!root) return;

  if (!state.currentUser) {
    root.innerHTML = renderLoginView();
    attachAuthEvents();
    return;
  }

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

  attachAIAssistantEvents();
}

function renderActiveTab() {
  const role = state.currentUser ? state.currentUser.role : 'organizer';

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

function attachAuthEvents() {
  const tabLogin = document.getElementById('tab-btn-login');
  const tabReg = document.getElementById('tab-btn-register');
  const formLogin = document.getElementById('form-login');
  const formReg = document.getElementById('form-register');
  const errBox = document.getElementById('auth-error-msg');
  const cameraBtn = document.getElementById('btn-start-camera');
  const cameraInput = document.getElementById('reg-camera-base64');
  const avatarThumb = document.getElementById('avatar-preview-thumbnail');
  const roleSelect = document.getElementById('reg-role');
  const cameraSec = document.getElementById('doctor-camera-section');

  if (roleSelect && cameraSec) {
    roleSelect.onchange = () => {
      cameraSec.style.display = roleSelect.value === 'doctor' ? 'block' : 'none';
    };
  }

  if (cameraBtn) {
    cameraBtn.onclick = () => {
      CameraModal.startCamera((base64) => {
        cameraInput.value = base64;
        avatarThumb.src = base64;
        ToastManager.show('Live camera snapshot captured!', 'success');
      });
    };
  }

  if (tabLogin && tabReg) {
    tabLogin.onclick = () => {
      formLogin.style.display = 'block';
      formReg.style.display = 'none';
      tabLogin.style.borderBottom = '2px solid var(--cds-interactive-01)';
      tabReg.style.borderBottom = 'none';
    };
    tabReg.onclick = () => {
      formLogin.style.display = 'none';
      formReg.style.display = 'block';
      tabReg.style.borderBottom = '2px solid var(--cds-interactive-01)';
      tabLogin.style.borderBottom = 'none';
    };
  }

  if (formLogin) {
    formLogin.onsubmit = async (e) => {
      e.preventDefault();
      errBox.style.display = 'none';
      const email = document.getElementById('login-email').value;
      const pwd = document.getElementById('login-password').value;

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
        ToastManager.show(`Welcome back, ${tokenData.full_name}!`, 'success');
        loadSystemData();
      } catch (err) {
        errBox.textContent = err.message || 'Authentication failed.';
        errBox.style.display = 'block';
      }
    };
  }

  if (formReg) {
    formReg.onsubmit = async (e) => {
      e.preventDefault();
      errBox.style.display = 'none';
      const role = document.getElementById('reg-role').value;
      const email = document.getElementById('reg-email').value;
      const pwd = document.getElementById('reg-password').value;
      const name = document.getElementById('reg-name').value;

      try {
        if (role === 'doctor' && cameraInput.value) {
          const formData = new FormData();
          formData.append('email', email);
          formData.append('password', pwd);
          formData.append('full_name', name);
          formData.append('phone', '080-555-0100');
          formData.append('license_number', `MED-${Date.now().toString().slice(-4)}`);
          formData.append('specialization', 'Transplant Surgery');
          formData.append('department', 'Surgery');
          formData.append('camera_image_base64', cameraInput.value);

          await fetch('/api/v1/auth/register-doctor-camera', { method: 'POST', body: formData });
        } else {
          await ApiService.register({ email, password: pwd, full_name: name, role });
        }

        ToastManager.show('Registration successful! Submitted for admin approval.', 'success');
        tabLogin.click();
      } catch (err) {
        errBox.textContent = err.message || 'Registration failed.';
        errBox.style.display = 'block';
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
      ToastManager.show('Signed out cleanly.', 'info');
    };
  }

  const refreshBtn = document.getElementById('btn-refresh-data');
  if (refreshBtn) {
    refreshBtn.onclick = () => loadSystemData();
  }

  document.querySelectorAll('.bx--side-nav__link').forEach(link => {
    link.onclick = (e) => {
      e.preventDefault();
      const tab = link.getAttribute('data-tab');
      setActiveTab(tab);
    };
  });

  document.querySelectorAll('.btn-approve-user').forEach(btn => {
    btn.onclick = async () => {
      const id = parseInt(btn.getAttribute('data-id'));
      await ApiService.approveUser(id, true);
      ToastManager.show('User approved successfully.', 'success');
      loadSystemData();
    };
  });

  // Quantum Match Trigger Button
  document.querySelectorAll('.btn-compute-quantum-match').forEach(btn => {
    btn.onclick = async () => {
      const organId = parseInt(btn.getAttribute('data-id'));
      try {
        const matches = await ApiService.computeMatches(organId);
        ToastManager.show(`Computed ${matches.length} Quantum Matches!`, 'success');
        loadSystemData();
      } catch (err) {
        ToastManager.show('Error computing matches: ' + err.message, 'error');
      }
    };
  });
}

async function loadSystemData() {
  try {
    if (state.currentUser && state.currentUser.role === 'organizer') {
      const pending = await ApiService.getPendingApprovals();
      state.pendingUsers = pending;
      const logs = await ApiService.getAuditLogs();
      state.auditLogs = logs;
    }
    const organs = await ApiService.getOrgans();
    state.organs = organs;

    const matches = await ApiService.getMatches();
    state.matches = matches;

    const telemetry = await ApiService.getLatestTelemetry('BOX-ESP32-001');
    if (telemetry) {
      state.telemetry = telemetry;
    }
  } catch (err) {
    console.error('Error fetching operational data:', err);
  }
  renderApp();
}

subscribe(renderApp);

document.addEventListener('DOMContentLoaded', async () => {
  initWebSocket();
  const token = localStorage.getItem('access_token');
  if (token) {
    try {
      const user = await ApiService.getMe();
      setCurrentUser(user);
      await loadSystemData();
    } catch (err) {
      localStorage.removeItem('access_token');
    }
  }
  renderApp();
});
