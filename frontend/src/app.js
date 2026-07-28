import { state, subscribe, setTheme, setCurrentUser, setActiveTab } from './state.js';
import { ApiService } from './services/api.js';
import { renderNavbar } from './components/Navbar.js';
import { renderSidebar } from './components/Sidebar.js';
import { initLiveMap } from './components/LiveMap.js';
import { renderLoginView } from './pages/Login.js';
import { renderDashboardAdmin } from './pages/DashboardAdmin.js';

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

  if (state.activeTab === 'dashboard') {
    initLiveMap(state.telemetry.lat, state.telemetry.lng);
  }
}

function renderActiveTab() {
  switch (state.activeTab) {
    case 'dashboard':
      return renderDashboardAdmin();
    case 'approvals':
      return renderDashboardAdmin();
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
      const payload = {
        email: document.getElementById('reg-email').value,
        password: document.getElementById('reg-password').value,
        full_name: document.getElementById('reg-name').value,
        role: document.getElementById('reg-role').value
      };

      try {
        await ApiService.register(payload);
        alert('Registration successful! Log in to your portal.');
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
    };
  }

  const refreshBtn = document.getElementById('btn-refresh-data');
  if (refreshBtn) {
    refreshBtn.onclick = () => loadSystemData();
  }

  // Sidebar Tab Navigation
  document.querySelectorAll('.bx--side-nav__link').forEach(link => {
    link.onclick = (e) => {
      e.preventDefault();
      const tab = link.getAttribute('data-tab');
      setActiveTab(tab);
    };
  });

  // Approval Buttons
  document.querySelectorAll('.btn-approve-user').forEach(btn => {
    btn.onclick = async () => {
      const id = parseInt(btn.getAttribute('data-id'));
      await ApiService.approveUser(id, true);
      loadSystemData();
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

    const telemetry = await ApiService.getLatestTelemetry('BOX-ESP32-001');
    if (telemetry) {
      state.telemetry = telemetry;
    }
  } catch (err) {
    console.error('Error fetching operational data:', err);
  }
  renderApp();
}

// Initial App Boot
subscribe(renderApp);

document.addEventListener('DOMContentLoaded', async () => {
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
