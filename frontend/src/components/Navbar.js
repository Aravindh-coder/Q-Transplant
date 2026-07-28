import { state, setTheme } from '../state.js';

export function renderNavbar() {
  const isDark = state.theme === 'dark';
  const roleName = state.currentUser ? state.currentUser.role.toUpperCase() : 'GUEST';

  return `
    <header class="bx--header">
      <a href="#" class="bx--header__name">
        <i class="fa-solid fa-heart-pulse" style="color: var(--cds-interactive-01);"></i>
        Q-TRANSPLANT <span>| Enterprise Coordination</span>
      </a>
      <div class="bx--header__global">
        ${state.currentUser ? `
          <span class="bx--tag bx--tag--blue"><i class="fa-solid fa-user-shield" style="margin-right:4px;"></i> ${roleName}</span>
          <span style="color: var(--cds-text-02); font-size: 13px;">${state.currentUser.full_name}</span>
        ` : ''}
        <button id="btn-toggle-theme" class="bx--btn bx--btn--ghost" title="Toggle Light/Dark Theme">
          <i class="fa-solid ${isDark ? 'fa-sun' : 'fa-moon'}"></i>
        </button>
        ${state.currentUser ? `
          <button id="btn-logout" class="bx--btn bx--btn--ghost" style="color: var(--cds-support-error);" title="Sign Out">
            <i class="fa-solid fa-right-from-bracket"></i>
          </button>
        ` : ''}
      </div>
    </header>
  `;
}
