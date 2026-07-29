/**
 * National Organ Command Center — Interactive GIS Map & Enterprise Control Portal
 * Displays real-time map of all Hospitals, Ambulances, Donors, Patients, and Cold Boxes.
 * Filtering by State, District, Hospital, Organ, Blood Group, and Urgency.
 */

import { ApiService } from '../services/api.js';

let commandCenterMap = null;
let mapMarkers = [];

export function renderNationalCommandCenterView() {
  return `
    <div>
      <div class="dash-header">
        <div>
          <h1 class="dash-title"><i class="fa-solid fa-earth-asia" style="color:#0f62fe;margin-right:8px;"></i>National Organ Command Center (GIS)</h1>
          <p class="dash-subtitle">Real-Time GIS Tracking & Resource Allocation across National Transplant Network</p>
        </div>
        <div style="display:flex; gap:10px; align-items:center;">
          <span class="bx--tag bx--tag--green" id="gis-status-badge"><i class="fa-solid fa-signal"></i> GIS LIVE CONNECTED</span>
          <button id="btn-refresh-gis" class="btn-hero-primary" style="padding:8px 16px; font-size:12px;">
            <i class="fa-solid fa-arrows-rotate"></i> Refresh GIS Feed
          </button>
        </div>
      </div>

      <!-- KPI Overview Bar -->
      <div class="kpi-grid" style="grid-template-columns: repeat(6, 1fr); margin-bottom:1.5rem;" id="gis-kpi-bar">
        <div class="kpi-card blue" style="padding:1rem;">
          <div class="kpi-card-label">Hospitals</div>
          <div class="kpi-card-value" id="gis-kpi-hospitals">--</div>
        </div>
        <div class="kpi-card green" style="padding:1rem;">
          <div class="kpi-card-label">Available Organs</div>
          <div class="kpi-card-value" id="gis-kpi-organs">--</div>
        </div>
        <div class="kpi-card yellow" style="padding:1rem;">
          <div class="kpi-card-label">Active Transports</div>
          <div class="kpi-card-value" id="gis-kpi-transports">--</div>
        </div>
        <div class="kpi-card purple" style="padding:1rem;">
          <div class="kpi-card-label">Patients Waiting</div>
          <div class="kpi-card-value" id="gis-kpi-patients">--</div>
        </div>
        <div class="kpi-card teal" style="padding:1rem;">
          <div class="kpi-card-label">Available Ambulances</div>
          <div class="kpi-card-value" id="gis-kpi-ambulances">--</div>
        </div>
        <div class="kpi-card red" style="padding:1rem;">
          <div class="kpi-card-label">Pending Matches</div>
          <div class="kpi-card-value" id="gis-kpi-matches">--</div>
        </div>
      </div>

      <!-- Control Panel & Filters -->
      <div class="ultra-table-wrap" style="margin-bottom: 1.5rem; background: rgba(38,38,38,0.6); padding: 1.25rem; border-radius: 12px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
          <h4 style="font-size:14px; font-weight:600; color:#f4f4f4; margin:0;"><i class="fa-solid fa-filter" style="color:#78a9ff;"></i> GIS Multi-Filter Panel</h4>
          <span style="font-size:11px; color:#8d8d8d;">Showing all active assets on map</span>
        </div>
        <div style="display:grid; grid-template-columns: repeat(5, 1fr); gap:1rem;">
          <div>
            <label style="font-size:11px; color:#c6c6c6; display:block; margin-bottom:4px;">Organ Type</label>
            <select id="gis-filter-organ" class="form-control" style="width:100%; background:#161616; color:#f4f4f4; border:1px solid #393939; padding:6px; border-radius:4px; font-size:12px;">
              <option value="ALL">All Organs</option>
              <option value="Heart">Heart</option>
              <option value="Kidney">Kidney</option>
              <option value="Liver">Liver</option>
              <option value="Lung">Lung</option>
              <option value="Pancreas">Pancreas</option>
            </select>
          </div>
          <div>
            <label style="font-size:11px; color:#c6c6c6; display:block; margin-bottom:4px;">Blood Group</label>
            <select id="gis-filter-blood" class="form-control" style="width:100%; background:#161616; color:#f4f4f4; border:1px solid #393939; padding:6px; border-radius:4px; font-size:12px;">
              <option value="ALL">All Blood Types</option>
              <option value="O+">O+</option>
              <option value="A+">A+</option>
              <option value="B+">B+</option>
              <option value="AB+">AB+</option>
              <option value="O-">O-</option>
            </select>
          </div>
          <div>
            <label style="font-size:11px; color:#c6c6c6; display:block; margin-bottom:4px;">Entity Layers</label>
            <select id="gis-filter-layer" class="form-control" style="width:100%; background:#161616; color:#f4f4f4; border:1px solid #393939; padding:6px; border-radius:4px; font-size:12px;">
              <option value="ALL">All Layers (Hospitals + Ambulances + Patients)</option>
              <option value="HOSPITALS">Hospitals Only</option>
              <option value="AMBULANCES">Ambulances Only</option>
              <option value="PATIENTS">Waiting Patients Only</option>
            </select>
          </div>
          <div>
            <label style="font-size:11px; color:#c6c6c6; display:block; margin-bottom:4px;">ICU Availability Filter</label>
            <select id="gis-filter-icu" class="form-control" style="width:100%; background:#161616; color:#f4f4f4; border:1px solid #393939; padding:6px; border-radius:4px; font-size:12px;">
              <option value="ALL">Any ICU Status</option>
              <option value="AVAILABLE">ICU Beds Available Only</option>
            </select>
          </div>
          <div style="display:flex; align-items:flex-end;">
            <button id="btn-find-nearest-icu" class="btn-hero-primary" style="width:100%; padding:7px; font-size:11px; justify-content:center; background:#8a3ffc; border-color:#8a3ffc;">
              <i class="fa-solid fa-hospital-user"></i> Find Nearest ICU
            </button>
          </div>
        </div>
      </div>

      <!-- Main GIS Grid: Map + Side Panel -->
      <div style="display:grid; grid-template-columns: 2.5fr 1fr; gap:1.5rem;">
        <!-- Map Container -->
        <div style="background:#161616; border:1px solid #393939; border-radius:12px; overflow:hidden; position:relative;">
          <div id="command-center-leaflet-map" style="height:600px; width:100%;"></div>
          <!-- Floating Map Legend -->
          <div style="position:absolute; bottom:16px; left:16px; z-index:1000; background:rgba(22,22,22,0.9); border:1px solid #393939; padding:10px 14px; border-radius:8px; font-size:11px; color:#c6c6c6; backdrop-filter:blur(4px);">
            <div style="font-weight:700; color:#f4f4f4; margin-bottom:6px;">MAP LEGEND</div>
            <div style="display:flex; align-items:center; gap:6px; margin-bottom:4px;"><span style="display:inline-block; width:10px; height:10px; border-radius:50%; background:#0f62fe;"></span> Hospital Node</div>
            <div style="display:flex; align-items:center; gap:6px; margin-bottom:4px;"><span style="display:inline-block; width:10px; height:10px; border-radius:50%; background:#42be65;"></span> Available Ambulance</div>
            <div style="display:flex; align-items:center; gap:6px; margin-bottom:4px;"><span style="display:inline-block; width:10px; height:10px; border-radius:50%; background:#8a3ffc;"></span> Waiting Patient</div>
            <div style="display:flex; align-items:center; gap:6px;"><span style="display:inline-block; width:10px; height:10px; border-radius:50%; background:#da1e28;"></span> Organ Cold Box in Transit</div>
          </div>
        </div>

        <!-- Side Panel: Hospital Capacity & Live Feed -->
        <div style="display:flex; flex-direction:column; gap:1rem;">
          <div class="ultra-table-wrap" style="flex:1; background:rgba(22,22,22,0.8); border-radius:12px; padding:1.25rem;">
            <h4 style="font-size:14px; font-weight:600; color:#f4f4f4; margin-bottom:1rem;"><i class="fa-solid fa-hospital-wide" style="color:#0f62fe;"></i> Hospital Network Nodes</h4>
            <div id="gis-hospital-list" style="max-height:260px; overflow-y:auto; display:flex; flex-direction:column; gap:8px;">
              <div style="color:#8d8d8d; font-size:12px;">Loading hospitals...</div>
            </div>
          </div>

          <div class="ultra-table-wrap" style="flex:1; background:rgba(22,22,22,0.8); border-radius:12px; padding:1.25rem;">
            <h4 style="font-size:14px; font-weight:600; color:#f4f4f4; margin-bottom:1rem;"><i class="fa-solid fa-truck-medical" style="color:#42be65;"></i> Active Transport Units</h4>
            <div id="gis-transport-list" style="max-height:240px; overflow-y:auto; display:flex; flex-direction:column; gap:8px;">
              <div style="color:#8d8d8d; font-size:12px;">Loading transport units...</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `;
}

export async function attachNationalCommandCenterEvents() {
  const btnRefresh = document.getElementById('btn-refresh-gis');
  if (btnRefresh) {
    btnRefresh.onclick = () => loadGISData();
  }

  const btnNearestICU = document.getElementById('btn-find-nearest-icu');
  if (btnNearestICU) {
    btnNearestICU.onclick = async () => {
      try {
        const token = localStorage.getItem('token');
        const res = await fetch('/api/v1/gis/nearest-icu', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const icus = await res.json();
        if (icus && icus.length > 0) {
          const top = icus[0];
          alert(`🏥 Nearest Hospital with ICU Available:\n\n${top.name} (${top.city})\nDistance: ${top.distance_km} km\nAvailable ICU Beds: ${top.icu_available}`);
          if (commandCenterMap) {
            commandCenterMap.setView([top.lat, top.lng], 13);
          }
        } else {
          alert('No ICU beds currently available in the network.');
        }
      } catch (err) {
        console.error('Error fetching nearest ICU:', err);
      }
    };
  }

  // Filter change handlers
  ['gis-filter-organ', 'gis-filter-blood', 'gis-filter-layer', 'gis-filter-icu'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.onchange = () => applyGISFilters();
  });

  await loadGISData();
}

let currentGISData = null;

async function loadGISData() {
  try {
    const token = localStorage.getItem('token');
    const res = await fetch('/api/v1/gis/overview', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (!res.ok) return;
    const data = await res.json();
    currentGISData = data;

    // Update KPI bar
    document.getElementById('gis-kpi-hospitals').textContent = data.summary.total_hospitals;
    document.getElementById('gis-kpi-organs').textContent = data.summary.available_organs;
    document.getElementById('gis-kpi-transports').textContent = data.summary.active_transports;
    document.getElementById('gis-kpi-patients').textContent = data.summary.patients_waiting;
    document.getElementById('gis-kpi-ambulances').textContent = data.summary.available_ambulances;
    document.getElementById('gis-kpi-matches').textContent = data.summary.pending_matches;

    // Render side panels
    renderHospitalSideList(data.hospitals);
    renderTransportSideList(data.ambulances);

    // Initialize or refresh map
    initGISMap(data);
  } catch (err) {
    console.error('Error loading GIS data:', err);
  }
}

function initGISMap(data) {
  const container = document.getElementById('command-center-leaflet-map');
  if (!container) return;

  if (typeof L === 'undefined') {
    container.innerHTML = `<div style="padding:2rem; text-align:center; color:#8d8d8d;">Map library loading...</div>`;
    return;
  }

  if (!commandCenterMap) {
    commandCenterMap = L.map('command-center-leaflet-map').setView([12.9716, 77.5946], 11);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors',
      maxZoom: 18
    }).addTo(commandCenterMap);
  }

  // Clear existing markers
  mapMarkers.forEach(m => commandCenterMap.removeLayer(m));
  mapMarkers = [];

  // Plot Hospitals
  data.hospitals.forEach(h => {
    const icon = L.divIcon({
      className: 'custom-map-pin-hosp',
      html: `<div style="background:#0f62fe; width:16px; height:16px; border-radius:50%; border:2px solid #fff; box-shadow:0 0 10px #0f62fe;"></div>`,
      iconSize: [16, 16]
    });
    const marker = L.marker([h.lat, h.lng], { icon })
      .bindPopup(`
        <div style="font-family:sans-serif; padding:4px;">
          <strong style="color:#0f62fe; font-size:13px;">${h.name}</strong><br/>
          <span style="font-size:11px; color:#555;">${h.city}, ${h.state}</span><br/>
          <span style="font-size:11px;">🏥 ICU Capacity: <strong>${h.icu_available} / ${h.icu_total} beds free</strong></span><br/>
          <span style="font-size:11px;">📞 ${h.contact_phone}</span>
        </div>
      `)
      .addTo(commandCenterMap);
    mapMarkers.push(marker);
  });

  // Plot Ambulances
  data.ambulances.forEach(a => {
    const icon = L.divIcon({
      className: 'custom-map-pin-amb',
      html: `<div style="background:#42be65; width:14px; height:14px; border-radius:50%; border:2px solid #fff; box-shadow:0 0 8px #42be65;"></div>`,
      iconSize: [14, 14]
    });
    const marker = L.marker([a.lat, a.lng], { icon })
      .bindPopup(`
        <div style="font-family:sans-serif; padding:4px;">
          <strong style="color:#42be65; font-size:13px;">🚑 Ambulance ${a.vehicle_number}</strong><br/>
          <span style="font-size:11px;">Driver: ${a.driver_name} (${a.driver_phone})</span><br/>
          <span style="font-size:11px;">Status: <strong>${a.status.toUpperCase()}</strong></span>
        </div>
      `)
      .addTo(commandCenterMap);
    mapMarkers.push(marker);
  });

  // Plot Patients
  data.patients.forEach(p => {
    const icon = L.divIcon({
      className: 'custom-map-pin-pat',
      html: `<div style="background:#8a3ffc; width:12px; height:12px; border-radius:50%; border:2px solid #fff; box-shadow:0 0 6px #8a3ffc;"></div>`,
      iconSize: [12, 12]
    });
    const marker = L.marker([p.hospital_lat + (Math.random()-0.5)*0.02, p.hospital_lng + (Math.random()-0.5)*0.02], { icon })
      .bindPopup(`
        <div style="font-family:sans-serif; padding:4px;">
          <strong style="color:#8a3ffc; font-size:13px;">👤 Patient: ${p.name}</strong><br/>
          <span style="font-size:11px;">Organ Needed: <strong>${p.target_organ} (${p.blood_type})</strong></span><br/>
          <span style="font-size:11px;">Urgency Score: <strong>${p.urgency_score}/10</strong></span>
        </div>
      `)
      .addTo(commandCenterMap);
    mapMarkers.push(marker);
  });
}

function renderHospitalSideList(hospitals) {
  const container = document.getElementById('gis-hospital-list');
  if (!container) return;
  if (!hospitals || hospitals.length === 0) {
    container.innerHTML = `<div style="color:#8d8d8d; font-size:12px;">No hospitals registered.</div>`;
    return;
  }
  container.innerHTML = hospitals.map(h => `
    <div style="background:#161616; border:1px solid #393939; border-radius:6px; padding:10px; font-size:12px; display:flex; justify-content:space-between; align-items:center;">
      <div>
        <div style="font-weight:600; color:#f4f4f4;">${h.name}</div>
        <div style="font-size:10px; color:#8d8d8d;">${h.city} · 📞 ${h.contact_phone}</div>
      </div>
      <div style="text-align:right;">
        <span class="bx--tag ${h.icu_available > 0 ? 'bx--tag--green' : 'bx--tag--red'}" style="font-size:10px; padding:2px 6px;">
          ICU: ${h.icu_available} FREE
        </span>
      </div>
    </div>
  `).join('');
}

function renderTransportSideList(ambulances) {
  const container = document.getElementById('gis-transport-list');
  if (!container) return;
  if (!ambulances || ambulances.length === 0) {
    container.innerHTML = `<div style="color:#8d8d8d; font-size:12px;">No transport units active.</div>`;
    return;
  }
  container.innerHTML = ambulances.map(a => `
    <div style="background:#161616; border:1px solid #393939; border-radius:6px; padding:10px; font-size:12px; display:flex; justify-content:space-between; align-items:center;">
      <div>
        <div style="font-weight:600; color:#42be65;">🚑 ${a.vehicle_number}</div>
        <div style="font-size:10px; color:#8d8d8d;">Driver: ${a.driver_name}</div>
      </div>
      <span class="bx--tag ${a.is_available ? 'bx--tag--green' : 'bx--tag--yellow'}" style="font-size:10px; padding:2px 6px;">
        ${a.is_available ? 'AVAILABLE' : 'IN TRANSIT'}
      </span>
    </div>
  `).join('');
}

function applyGISFilters() {
  if (!currentGISData) return;
  const organFilter = document.getElementById('gis-filter-organ')?.value;
  const bloodFilter = document.getElementById('gis-filter-blood')?.value;
  const layerFilter = document.getElementById('gis-filter-layer')?.value;

  let filtered = { ...currentGISData };

  if (layerFilter === 'HOSPITALS') {
    filtered.ambulances = [];
    filtered.patients = [];
  } else if (layerFilter === 'AMBULANCES') {
    filtered.hospitals = [];
    filtered.patients = [];
  } else if (layerFilter === 'PATIENTS') {
    filtered.hospitals = [];
    filtered.ambulances = [];
  }

  if (organFilter && organFilter !== 'ALL') {
    filtered.patients = filtered.patients.filter(p => p.target_organ === organFilter);
  }
  if (bloodFilter && bloodFilter !== 'ALL') {
    filtered.patients = filtered.patients.filter(p => p.blood_type === bloodFilter);
  }

  initGISMap(filtered);
}
