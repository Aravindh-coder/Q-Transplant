export function renderTelemetryGauge(telemetry) {
  const isOptimal = telemetry.temp_celsius >= 2.0 && telemetry.temp_celsius <= 8.0;
  const statusClass = isOptimal ? 'bx--tag--green' : 'bx--tag--red';
  const statusText = isOptimal ? 'NOMINAL' : 'TEMPERATURE ALARM';

  return `
    <div class="bx--tile">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
        <span class="bx--tile__heading"><i class="fa-solid fa-temperature-arrow-down"></i> COLD-BOX TELEMETRY [ESP32]</span>
        <span class="bx--tag ${statusClass}">${statusText}</span>
      </div>

      <div class="bx--grid" style="grid-template-columns: repeat(4, 1fr); gap: 12px;">
        <div style="background-color: var(--cds-layer-02); padding: 12px; border-left: 3px solid var(--cds-interactive-01);">
          <div style="font-size: 11px; color: var(--cds-text-02);">TEMPERATURE</div>
          <div style="font-size: 1.5rem; font-family: var(--cds-mono-font); font-weight: 600;">${telemetry.temp_celsius.toFixed(1)} °C</div>
          <div style="font-size: 10px; color: var(--cds-text-03);">Target: 2.0°C - 8.0°C</div>
        </div>

        <div style="background-color: var(--cds-layer-02); padding: 12px; border-left: 3px solid var(--cds-teal-40);">
          <div style="font-size: 11px; color: var(--cds-text-02);">HUMIDITY</div>
          <div style="font-size: 1.5rem; font-family: var(--cds-mono-font); font-weight: 600;">${telemetry.humidity_percent.toFixed(1)} %</div>
          <div style="font-size: 10px; color: var(--cds-text-03);">Sensor DHT22</div>
        </div>

        <div style="background-color: var(--cds-layer-02); padding: 12px; border-left: 3px solid var(--cds-support-success);">
          <div style="font-size: 11px; color: var(--cds-text-02);">BATTERY LEVEL</div>
          <div style="font-size: 1.5rem; font-family: var(--cds-mono-font); font-weight: 600;">${telemetry.battery_level.toFixed(0)} %</div>
          <div style="font-size: 10px; color: var(--cds-text-03);">LiPo Cell Backup</div>
        </div>

        <div style="background-color: var(--cds-layer-02); padding: 12px; border-left: 3px solid var(--cds-cyan-30);">
          <div style="font-size: 11px; color: var(--cds-text-02);">ISCHEMIA WINDOW</div>
          <div style="font-size: 1.5rem; font-family: var(--cds-mono-font); font-weight: 600;">03:42:15</div>
          <div style="font-size: 10px; color: var(--cds-text-03);">Max 06:00:00</div>
        </div>
      </div>
    </div>
  `;
}
