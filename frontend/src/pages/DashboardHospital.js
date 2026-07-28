export function renderDashboardHospital() {
  return `
    <div>
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
        <div>
          <h1 style="font-size: 1.75rem; font-weight: 300;">Hospital Operational Control Center</h1>
          <p style="color: var(--cds-text-02); font-size: 13px;">ICU Bed Occupancy, Operation Theatres & Blood Reserve Logistics</p>
        </div>
      </div>

      <!-- Hospital Metrics -->
      <div class="bx--grid" style="grid-template-columns: repeat(4, 1fr); margin-bottom: 1.5rem;">
        <div class="bx--tile">
          <div class="bx--tile__heading"><i class="fa-solid fa-bed-pulse"></i> ICU BED OCCUPANCY</div>
          <div class="bx--tile__value">14 / 20</div>
          <div style="font-size: 11px; color: var(--cds-support-warning); margin-top: 4px;">70.0% Capacity Occupied</div>
        </div>
        <div class="bx--tile">
          <div class="bx--tile__heading"><i class="fa-solid fa-square-virus"></i> VENTILATORS AVAILABLE</div>
          <div class="bx--tile__value" style="color: var(--cds-support-success);">6</div>
        </div>
        <div class="bx--tile">
          <div class="bx--tile__heading"><i class="fa-solid fa-droplet"></i> BLOOD INVENTORY</div>
          <div class="bx--tile__value">51 Units</div>
        </div>
        <div class="bx--tile">
          <div class="bx--tile__heading"><i class="fa-solid fa-truck-medical"></i> AMBULANCE FLEET</div>
          <div class="bx--tile__value" style="color: var(--cds-interactive-01);">1 Active</div>
        </div>
      </div>

      <div class="bx--grid" style="grid-template-columns: repeat(12, 1fr);">
        <!-- Blood Reserve Grid -->
        <div class="bx--tile" style="grid-column: span 6;">
          <div class="bx--tile__heading"><i class="fa-solid fa-vial"></i> BLOOD TYPE INVENTORY</div>
          <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-top: 10px;">
            <div style="background: var(--cds-layer-02); padding: 10px; text-align: center; border: 1px solid var(--cds-border-subtle);">
              <div style="font-size: 12px; color: var(--cds-text-02);">O Negative</div>
              <div style="font-size: 1.25rem; font-family: var(--cds-mono-font); font-weight: 600; color: var(--cds-support-error);">8 Units</div>
            </div>
            <div style="background: var(--cds-layer-02); padding: 10px; text-align: center; border: 1px solid var(--cds-border-subtle);">
              <div style="font-size: 12px; color: var(--cds-text-02);">O Positive</div>
              <div style="font-size: 1.25rem; font-family: var(--cds-mono-font); font-weight: 600;">15 Units</div>
            </div>
            <div style="background: var(--cds-layer-02); padding: 10px; text-align: center; border: 1px solid var(--cds-border-subtle);">
              <div style="font-size: 12px; color: var(--cds-text-02);">A Positive</div>
              <div style="font-size: 1.25rem; font-family: var(--cds-mono-font); font-weight: 600;">12 Units</div>
            </div>
          </div>
        </div>

        <!-- Operation Theatre Status -->
        <div class="bx--tile" style="grid-column: span 6;">
          <div class="bx--tile__heading"><i class="fa-solid fa-hospital"></i> OPERATION THEATRE SUITES</div>
          <div style="margin-top: 10px;">
            <div style="padding: 10px; background: var(--cds-layer-02); border-left: 3px solid var(--cds-support-success); margin-bottom: 8px;">
              <div style="font-weight: 600;">OT Suite 1 (Cardiothoracic)</div>
              <div style="font-size: 11px; color: var(--cds-text-02);">Status: Available for Emergency Transplant</div>
            </div>
            <div style="padding: 10px; background: var(--cds-layer-02); border-left: 3px solid var(--cds-support-warning);">
              <div style="font-weight: 600;">OT Suite 2 (Renal Surgery)</div>
              <div style="font-size: 11px; color: var(--cds-text-02);">Status: Procedure in Progress (Est. 45m left)</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `;
}
