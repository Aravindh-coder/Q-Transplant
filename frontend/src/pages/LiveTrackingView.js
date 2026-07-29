/**
 * Live Transport Tracking Dashboard
 * Real-time map, telemetry gauges, speed, ETA countdown, and transport logs.
 */

export function renderLiveTrackingView() {
  return `
    <div>
      <div class="dash-header">
        <div>
          <h1 class="dash-title"><i class="fa-solid fa-route" style="color:#00f0ff;margin-right:8px;"></i>Live Organ Transport Tracking & Telemetry</h1>
          <p class="dash-subtitle">Sub-Second GPS Tracking, Speed, Battery, & Cold-Box Temperature Monitoring</p>
        </div>
        <span class="bx--tag bx--tag--green" id="tracking-live-tag">● LIVE STREAM ACTIVE</span>
      </div>

      <!-- Live Stats Panel -->
      <div class="kpi-grid" style="grid-template-columns: repeat(5, 1fr); margin-bottom:1.5rem;">
        <div class="kpi-card blue" style="padding:1rem;">
          <div class="kpi-card-label">Active Transport</div>
          <div class="kpi-card-value" style="font-size:1.2rem;" id="lt-id">TR-2026-901</div>
        </div>
        <div class="kpi-card green" style="padding:1rem;">
          <div class="kpi-card-label">Cold Box Temperature</div>
          <div class="kpi-card-value" style="font-size:1.2rem; color:#42be65;" id="lt-temp">4.2 °C</div>
        </div>
        <div class="kpi-card yellow" style="padding:1rem;">
          <div class="kpi-card-label">Vehicle Speed</div>
          <div class="kpi-card-value" style="font-size:1.2rem; color:#f1c21b;" id="lt-speed">78 km/h</div>
        </div>
        <div class="kpi-card purple" style="padding:1rem;">
          <div class="kpi-card-label">Estimated Arrival (ETA)</div>
          <div class="kpi-card-value" style="font-size:1.2rem; color:#be95ff;" id="lt-eta">28 mins</div>
        </div>
        <div class="kpi-card red" style="padding:1rem;">
          <div class="kpi-card-label">Battery Level</div>
          <div class="kpi-card-value" style="font-size:1.2rem; color:#42be65;" id="lt-battery">96%</div>
        </div>
      </div>

      <!-- Main Tracking Area -->
      <div style="display:grid; grid-template-columns: 2fr 1fr; gap:1.5rem;">
        <!-- Live Leaflet Map Container -->
        <div style="background:#161616; border:1px solid #393939; border-radius:12px; overflow:hidden;">
          <div id="live-tracking-leaflet-map" style="height:520px; width:100%;"></div>
        </div>

        <!-- Telemetry & Logs Sidebar -->
        <div style="display:flex; flex-direction:column; gap:1rem;">
          <div class="ultra-table-wrap" style="background:rgba(22,22,22,0.8); border-radius:12px; padding:1.25rem;">
            <h4 style="font-size:14px; font-weight:600; color:#f4f4f4; margin-bottom:1rem;"><i class="fa-solid fa-box-archive" style="color:#00f0ff;"></i> Organ Package Details</h4>
            <div style="font-size:12px; color:#c6c6c6; display:flex; flex-direction:column; gap:8px;">
              <div><strong>Organ:</strong> Heart (O+)</div>
              <div><strong>Container:</strong> ESP32-BOX-001 (Smart Cold Box)</div>
              <div><strong>Origin:</strong> Apollo Specialty Hospital, Bengaluru</div>
              <div><strong>Destination:</strong> Fortis Healthcare, Richmond Road</div>
              <div><strong>Max Viability:</strong> 4.0 Hours (Remaining: 3.1h)</div>
              <div><strong>Surgeon:</strong> Dr. Rajesh Kumar</div>
            </div>
          </div>

          <div class="ultra-table-wrap" style="flex:1; background:rgba(22,22,22,0.8); border-radius:12px; padding:1.25rem;">
            <h4 style="font-size:14px; font-weight:600; color:#f4f4f4; margin-bottom:1rem;"><i class="fa-solid fa-list-check" style="color:#42be65;"></i> Telemetry Event Stream</h4>
            <div id="lt-event-log" style="max-height:220px; overflow-y:auto; font-size:11px; font-family:monospace; display:flex; flex-direction:column; gap:6px; color:#8d8d8d;">
              <div>[22:30:12] GPS PING: 12.9716, 77.5946 · Speed 78km/h · Temp 4.2°C</div>
              <div>[22:30:02] GPS PING: 12.9690, 77.5920 · Speed 75km/h · Temp 4.1°C</div>
              <div>[22:29:52] Cold Box Lid Lock Verified: SEALED</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `;
}

let trackingMap = null;
let trackingMarker = null;

export function attachLiveTrackingEvents() {
  const container = document.getElementById('live-tracking-leaflet-map');
  if (!container || typeof L === 'undefined') return;

  if (!trackingMap) {
    trackingMap = L.map('live-tracking-leaflet-map').setView([12.9716, 77.5946], 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(trackingMap);

    const ambIcon = L.divIcon({
      className: 'custom-map-pin-tracking',
      html: `<div style="background:#00f0ff; width:20px; height:20px; border-radius:50%; border:3px solid #fff; box-shadow:0 0 15px #00f0ff;"></div>`,
      iconSize: [20, 20]
    });

    trackingMarker = L.marker([12.9716, 77.5946], { icon: ambIcon })
      .bindPopup(`<strong>🚑 Organ Transport Ambulance</strong><br/>Temp: 4.2°C | Speed: 78 km/h`)
      .addTo(trackingMap);
  }

  // Simulate movement
  let lat = 12.9716;
  let lng = 77.5946;
  setInterval(() => {
    lat += (Math.random() - 0.5) * 0.002;
    lng += (Math.random() - 0.5) * 0.002;
    if (trackingMarker) trackingMarker.setLatLng([lat, lng]);

    const temp = (4.0 + Math.random() * 0.4).toFixed(1);
    const speed = Math.floor(70 + Math.random() * 15);
    const tempEl = document.getElementById('lt-temp');
    const speedEl = document.getElementById('lt-speed');
    if (tempEl) tempEl.textContent = `${temp} °C`;
    if (speedEl) speedEl.textContent = `${speed} km/h`;
  }, 3000);
}
