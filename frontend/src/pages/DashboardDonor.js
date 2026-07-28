import { state } from '../state.js';
import { renderQRBadge } from '../components/QRBadge.js';

export function renderDashboardDonor() {
  const user = state.currentUser || { full_name: 'David Miller' };

  return `
    <div>
      <div style="margin-bottom: 1.5rem;">
        <h1 style="font-size: 1.75rem; font-weight: 300;">Organ Donor Portal</h1>
        <p style="color: var(--cds-text-02); font-size: 13px;">Donation Pledge Verification & Digital Health Passport</p>
      </div>

      <div class="bx--grid" style="grid-template-columns: repeat(12, 1fr); margin-bottom: 1.5rem;">
        <div class="bx--tile" style="grid-column: span 8;">
          <div class="bx--tile__heading"><i class="fa-solid fa-hand-holding-heart"></i> DONOR PLEDGE PROFILE</div>
          <div style="margin-top: 1rem; display: flex; flex-direction: column; gap: 12px;">
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid var(--cds-border-subtle); padding-bottom: 8px;">
              <span style="color: var(--cds-text-02);">DONOR NAME</span>
              <strong>${user.full_name}</strong>
            </div>
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid var(--cds-border-subtle); padding-bottom: 8px;">
              <span style="color: var(--cds-text-02);">BLOOD TYPE</span>
              <span class="bx--tag bx--tag--red">O POSITIVE</span>
            </div>
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid var(--cds-border-subtle); padding-bottom: 8px;">
              <span style="color: var(--cds-text-02);">HLA ANTIMATCH MARKERS</span>
              <span style="font-family: var(--cds-mono-font);">A2, B7, DR4</span>
            </div>
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid var(--cds-border-subtle); padding-bottom: 8px;">
              <span style="color: var(--cds-text-02);">PLEDGE STATUS</span>
              <span class="bx--tag bx--tag--green">VERIFIED & ACTIVE</span>
            </div>
          </div>
        </div>

        <div style="grid-column: span 4;">
          ${renderQRBadge('QR-DONOR-O-PLUS-001', user.full_name)}
        </div>
      </div>
    </div>
  `;
}
