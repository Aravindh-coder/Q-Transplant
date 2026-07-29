/**
 * Digital Twin Transport Dashboard (Mission 2)
 * Real-Time GPS Simulation, Cold Ischemia Countdown, ETA Prediction vs Actual
 */
export function renderDigitalTwinView() {
  return `
    <div style="padding:0 1rem;">
      <div class="dash-title-row" style="margin-bottom:1.5rem;">
        <h1 class="dash-title">
          <i class="fa-solid fa-satellite-dish" style="color:#00b0ff;margin-right:10px;"></i>
          Digital Twin — Live Organ Transport
        </h1>
        <div style="display:flex;gap:8px;">
          <button id="btn-twin-ambulance" class="bx--btn bx--btn--primary" style="font-size:11px;padding:6px 14px;">
            <i class="fa-solid fa-truck-medical"></i> Ambulance Mode
          </button>
          <button id="btn-twin-drone" class="bx--btn bx--btn--secondary" style="font-size:11px;padding:6px 14px;">
            <i class="fa-solid fa-helicopter"></i> Drone Mode
          </button>
          <button id="btn-twin-replay" class="bx--btn bx--btn--ghost" style="font-size:11px;padding:6px 14px;">
            <i class="fa-solid fa-rotate-left"></i> Replay History
          </button>
        </div>
      </div>

      <div id="digital-twin-state">
        <div class="glass-card" style="padding:2rem;text-align:center;">
          <i class="fa-solid fa-satellite-dish" style="font-size:2.5rem;color:#00b0ff;margin-bottom:1rem;display:block;animation:pulse 2s ease-in-out infinite;"></i>
          <p style="color:#8d8d8d;">Click <strong style="color:#00b0ff;">Ambulance Mode</strong> or <strong style="color:#8a3ffc;">Drone Mode</strong> to launch simulation.</p>
        </div>
      </div>

      <div class="glass-card" style="margin-top:1.5rem;padding:1.5rem;">
        <h3 style="color:#00b0ff;margin-bottom:1rem;font-size:14px;font-weight:700;">
          <i class="fa-solid fa-route"></i> Transport Corridor — Bengaluru Medical Nodes
        </h3>
        <div id="twin-leaflet-map" style="height:350px;border-radius:8px;background:#1a1a2e;border:1px solid rgba(0,176,255,0.2);display:flex;align-items:center;justify-content:center;">
          <p style="color:#525252;font-size:12px;">Map initializes when simulation is running</p>
        </div>
      </div>

      <div class="glass-card" style="margin-top:1.5rem;padding:1.5rem;">
        <h3 style="color:#8d8d8d;font-size:14px;margin-bottom:1rem;"><i class="fa-solid fa-rotate-left"></i> Historical Replay Frames</h3>
        <div id="digital-twin-replay" style="font-size:11px;color:#8d8d8d;text-align:center;">Run simulation first to record replay frames.</div>
      </div>
    </div>
  `;
}

export function attachDigitalTwinEvents() {
  let simInterval = null;
  let currentMode = 'ambulance';

  function renderTwinState(data) {
    const el = document.getElementById('digital-twin-state');
    if (!el) return;
    const ischemiaColor = data.ischemia_remaining_minutes > 240 ? '#42be65' :
                          data.ischemia_remaining_minutes > 120 ? '#f1c21b' : '#da1e28';
    const tempColor = data.temperature_celsius <= 6 ? '#42be65' :
                      data.temperature_celsius <= 8 ? '#f1c21b' : '#da1e28';

    el.innerHTML = `
      <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin-bottom:1.5rem;">
        ${[
          ['Location', data.current_location?.name || 'En Route', '#00b0ff', 'fa-location-dot'],
          ['Progress', data.progress_percent + '%', '#42be65', 'fa-route'],
          ['Speed', data.speed_kmh + ' km/h', '#8a3ffc', 'fa-gauge-high'],
          ['Mode', data.mode, '#f1c21b', 'fa-truck-medical']
        ].map(([label, val, color, icon]) => `
          <div class="glass-card" style="padding:1rem;text-align:center;">
            <i class="fa-solid ${icon}" style="color:${color};font-size:1.2rem;margin-bottom:0.5rem;display:block;"></i>
            <div style="font-size:16px;font-weight:800;color:${color};">${val}</div>
            <div style="font-size:10px;color:#8d8d8d;">${label}</div>
          </div>
        `).join('')}
      </div>

      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:1rem;">
        <div class="glass-card" style="padding:1rem;border-color:rgba(218,30,40,0.3);">
          <div style="font-size:10px;color:#8d8d8d;font-weight:700;margin-bottom:0.5rem;">❄️ COLD ISCHEMIA REMAINING</div>
          <div style="font-size:24px;font-weight:900;color:${ischemiaColor};">${data.ischemia_formatted}</div>
          <div style="height:6px;background:#393939;border-radius:3px;margin-top:8px;">
            <div style="width:${(data.ischemia_remaining_minutes/360)*100}%;height:100%;background:${ischemiaColor};border-radius:3px;transition:width 0.5s;"></div>
          </div>
        </div>
        <div class="glass-card" style="padding:1rem;border-color:rgba(0,176,255,0.3);">
          <div style="font-size:10px;color:#8d8d8d;font-weight:700;margin-bottom:0.5rem;">🎯 ETA PREDICTION</div>
          <div style="font-size:24px;font-weight:900;color:#00b0ff;">${data.predicted_eta_minutes} min</div>
          <div style="font-size:11px;color:#525252;">Actual: ${data.actual_eta_minutes} min · Δ ${data.eta_variance_minutes} min</div>
        </div>
        <div class="glass-card" style="padding:1rem;border-color:rgba(66,190,101,0.3);">
          <div style="font-size:10px;color:#8d8d8d;font-weight:700;margin-bottom:0.5rem;">🌡️ TEMPERATURE</div>
          <div style="font-size:24px;font-weight:900;color:${tempColor};">${data.temperature_celsius}°C</div>
          <div style="font-size:11px;color:#525252;">Battery: ${data.battery_percent}%</div>
        </div>
      </div>
    `;
  }

  function startSim(mode) {
    currentMode = mode;
    if (simInterval) clearInterval(simInterval);
    simInterval = setInterval(async () => {
      try {
        const r = await fetch(`/api/v1/ai/digital-twin/live?mode=${mode}`);
        const data = await r.json();
        renderTwinState(data);
      } catch (err) {}
    }, 2000);
    fetch(`/api/v1/ai/digital-twin/live?mode=${mode}`).then(r=>r.json()).then(renderTwinState).catch(()=>{});
  }

  document.getElementById('btn-twin-ambulance')?.addEventListener('click', () => startSim('ambulance'));
  document.getElementById('btn-twin-drone')?.addEventListener('click', () => startSim('drone'));
  document.getElementById('btn-twin-replay')?.addEventListener('click', async () => {
    try {
      const r = await fetch('/api/v1/ai/digital-twin/replay');
      const frames = await r.json();
      const el = document.getElementById('digital-twin-replay');
      if (!el) return;
      el.innerHTML = `
        <div style="max-height:200px;overflow-y:auto;">
          <table class="utbl" style="font-size:11px;">
            <thead><tr><th>Time</th><th>Location</th><th>Progress</th><th>Temp</th><th>Ischemia Left</th><th>ETA</th></tr></thead>
            <tbody>
              ${frames.slice().reverse().map(f => `
                <tr>
                  <td style="font-family:monospace;">${f.timestamp}</td>
                  <td>${f.current_location?.name || '-'}</td>
                  <td><span style="color:#42be65;">${f.progress_percent}%</span></td>
                  <td style="color:#00b0ff;">${f.temperature_celsius}°C</td>
                  <td style="color:#f1c21b;">${f.ischemia_formatted}</td>
                  <td>${f.predicted_eta_minutes} min</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      `;
    } catch (err) {}
  });
}
