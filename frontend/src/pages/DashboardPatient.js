import { state } from '../state.js';

export function renderDashboardPatient() {
  const user = state.currentUser || { full_name: 'Sarah Jenkins' };

  return `
    <div>
      <div style="margin-bottom: 1.5rem;">
        <h1 style="font-size: 1.75rem; font-weight: 300;">Patient Transplant Portal</h1>
        <p style="color: var(--cds-text-02); font-size: 13px;">Waiting List Position & Compatibility Tracking</p>
      </div>

      <div class="bx--grid" style="grid-template-columns: repeat(4, 1fr); margin-bottom: 1.5rem;">
        <div class="bx--tile">
          <div class="bx--tile__heading"><i class="fa-solid fa-list-ol"></i> WAITING LIST POSITION</div>
          <div class="bx--tile__value" style="color: var(--cds-interactive-01);">#1 Priority</div>
        </div>
        <div class="bx--tile">
          <div class="bx--tile__heading"><i class="fa-solid fa-heart"></i> TARGET ORGAN</div>
          <div class="bx--tile__value">Heart</div>
        </div>
        <div class="bx--tile">
          <div class="bx--tile__heading"><i class="fa-solid fa-gauge-high"></i> URGENCY SCORE</div>
          <div class="bx--tile__value" style="color: var(--cds-support-error);">9 / 10</div>
        </div>
        <div class="bx--tile">
          <div class="bx--tile__heading"><i class="fa-solid fa-square-check"></i> COMPATIBILITY STATUS</div>
          <div class="bx--tile__value" style="color: var(--cds-support-success);">94.5%</div>
        </div>
      </div>

      <div class="bx--tile">
        <div class="bx--tile__heading"><i class="fa-solid fa-user-doctor"></i> ATTENDING SURGICAL TEAM</div>
        <div style="margin-top: 10px; display: flex; align-items: center; gap: 15px; background: var(--cds-layer-02); padding: 1rem;">
          <i class="fa-solid fa-user-doctor" style="font-size: 2.5rem; color: var(--cds-interactive-01);"></i>
          <div>
            <div style="font-weight: 600; font-size: 1rem;">Dr. Rajesh Kumar (Chief Transplant Surgeon)</div>
            <div style="font-size: 12px; color: var(--cds-text-02);">Apollo Specialty Hospital | Department of Cardiothoracic Surgery</div>
            <div style="margin-top: 6px; font-size: 12px; color: var(--cds-support-success);">
              <i class="fa-solid fa-circle" style="font-size: 8px;"></i> On-Call for Emergency Dispatch
            </div>
          </div>
        </div>
      </div>
    </div>
  `;
}
