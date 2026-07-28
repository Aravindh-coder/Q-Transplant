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

function checkHashForResetToken() {
  const hash = window.location.hash;
  if (hash.includes('reset-token=')) {
    const token = hash.split('reset-token=')[1].split('&')[0];
    const resetModal = document.getElementById('reset-pwd-modal');
    const tokenInput = document.getElementById('reset-token-input');
    if (resetModal && tokenInput) {
      tokenInput.value = token;
      resetModal.style.display = 'flex';
    }
  }
}

function renderApp() {
  const root = document.getElementById('app');
  if (!root) return;

  if (!state.currentUser) {
    root.innerHTML = renderLoginView();
    attachAuthEvents();
    checkHashForResetToken();
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

  const linkForgot = document.getElementById('link-forgot-pwd');
  const forgotModal = document.getElementById('forgot-pwd-modal');
  const closeForgotBtn = document.getElementById('btn-close-forgot-modal');
  const formForgot = document.getElementById('form-forgot-password');

  const resetModal = document.getElementById('reset-pwd-modal');
  const closeResetBtn = document.getElementById('btn-close-reset-modal');
  const formReset = document.getElementById('form-reset-password');

  if (linkForgot && forgotModal) {
    linkForgot.onclick = () => { forgotModal.style.display = 'flex'; };
  }
  if (closeForgotBtn && forgotModal) {
    closeForgotBtn.onclick = () => { forgotModal.style.display = 'none'; };
  }

  if (formForgot) {
    formForgot.onsubmit = async (e) => {
      e.preventDefault();
      const email = document.getElementById('forgot-email').value;
      try {
        const formData = new FormData();
        formData.append('email', email);
        const res = await fetch('/api/v1/auth/forgot-password', { method: 'POST', body: formData });
        const data = await res.json();
        ToastManager.show(data.message || 'Reset token link dispatched to email.', 'info');
        forgotModal.style.display = 'none';
        if (data.token) {
          window.location.hash = `#reset-token=${data.token}`;
          checkHashForResetToken();
        }
      } catch (err) {
        ToastManager.show('Error requesting reset: ' + err.message, 'error');
      }
    };
  }

  if (closeResetBtn && resetModal) {
    closeResetBtn.onclick = () => { resetModal.style.display = 'none'; };
  }

  if (formReset) {
    formReset.onsubmit = async (e) => {
      e.preventDefault();
      const token = document.getElementById('reset-token-input').value;
      const newPassword = document.getElementById('reset-new-password').value;
      try {
        const formData = new FormData();
        formData.append('token', token);
        formData.append('new_password', newPassword);
        const res = await fetch('/api/v1/auth/reset-password', { method: 'POST', body: formData });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Reset failed');
        ToastManager.show(data.message || 'Password successfully updated!', 'success');
        resetModal.style.display = 'none';
        window.location.hash = '';
      } catch (err) {
        ToastManager.show('Password reset error: ' + err.message, 'error');
      }
    };
  }

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
        ToastManager.show('Live camera photo captured successfully!', 'success');
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
      if (errBox) errBox.style.display = 'none';
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
        await loadSystemData();
      } catch (err) {
        if (errBox) {
          errBox.textContent = err.message || 'Authentication credentials invalid.';
          errBox.style.display = 'block';
        }
        ToastManager.show('Login failed: ' + (err.message || 'Invalid credentials'), 'error');
      }
    };
  }

  if (formReg) {
    formReg.onsubmit = async (e) => {
      e.preventDefault();
      if (errBox) errBox.style.display = 'none';
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
          formData.append('department', 'Cardiothoracic');
          formData.append('camera_image_base64', cameraInput.value);

          const res = await fetch('/api/v1/auth/register-doctor-camera', { method: 'POST', body: formData });
          if (!res.ok) {
            const data = await res.json();
            throw new Error(data.detail || 'Doctor camera registration failed');
          }
        } else {
          await ApiService.register({ email, password: pwd, full_name: name, role });
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

  // Admin User Approvals (Approve Button)
  document.querySelectorAll('.btn-approve-user').forEach(btn => {
    btn.onclick = async () => {
      const id = parseInt(btn.getAttribute('data-id'));
      try {
        await ApiService.approveUser(id, true, 'Approved by Organizer from Dashboard');
        ToastManager.show('User approved successfully! Approval email dispatched.', 'success');
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

window.addEventListener('hashchange', checkHashForResetToken);

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
