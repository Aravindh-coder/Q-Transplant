export class ToastManager {
  static show(message, type = 'info') {
    let container = document.getElementById('toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toast-container';
      container.style.cssText = 'position: fixed; bottom: 20px; right: 20px; z-index: 3000; display: flex; flex-direction: column; gap: 10px;';
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    const color = type === 'error' ? 'var(--cds-support-error)' : type === 'success' ? 'var(--cds-support-success)' : 'var(--cds-interactive-01)';
    toast.style.cssText = `background: var(--cds-layer-01); color: var(--cds-text-01); border-left: 4px solid ${color}; border-top: 1px solid var(--cds-border-subtle); border-right: 1px solid var(--cds-border-subtle); border-bottom: 1px solid var(--cds-border-subtle); padding: 12px 16px; font-size: 13px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); display: flex; align-items: center; gap: 10px; min-width: 280px;`;
    
    toast.innerHTML = `
      <i class="fa-solid ${type === 'error' ? 'fa-circle-xmark' : type === 'success' ? 'fa-circle-check' : 'fa-circle-info'}" style="color: ${color}; font-size: 1.1rem;"></i>
      <span style="flex: 1;">${message}</span>
    `;

    container.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
  }
}
