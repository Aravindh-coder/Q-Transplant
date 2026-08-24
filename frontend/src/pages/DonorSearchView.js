/**
 * Search for Donor — doctors upload donor pool CSVs (thousands of donors),
 * then search by a single patient's medical profile. The search is shown as
 * a live Grover's-algorithm-style amplitude-amplification animation across
 * the donor pool before the ranked top matches are revealed.
 */
import { ToastManager } from '../components/Toast.js';

let _lastSearchResult = null;
let _poolStats = { pool_size: 0, by_organ: {}, by_blood_type: {} };

export function renderDonorSearchView() {
  return `
    <div>
      <div class="dash-header">
        <div>
          <h1 class="dash-title"><i class="fa-solid fa-magnifying-glass" style="color:#8a3ffc;margin-right:8px;"></i>Search for Donor</h1>
          <p class="dash-subtitle">Search thousands of doctor-registered donors for a single patient — visualized as a live Grover's quantum search</p>
        </div>
      </div>

      <!-- ── Donor Pool Panel ─────────────────────────────────────────── -->
      <div class="ultra-table-wrap" style="margin-bottom:1.5rem;background:rgba(38,38,38,0.6);border-radius:12px;padding:1.5rem;">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1rem;">
          <div>
            <h4 style="color:#f4f4f4;font-size:14px;margin-bottom:4px;"><i class="fa-solid fa-database" style="color:#42be65;"></i> Donor Pool</h4>
            <div id="ds-pool-badge" style="color:#8d8d8d;font-size:12px;">Loading pool stats…</div>
          </div>
          <div style="display:flex;gap:0.6rem;flex-wrap:wrap;">
            <label class="bx--btn bx--btn--secondary" style="padding:8px 16px;font-size:12px;border-radius:6px;cursor:pointer;">
              <i class="fa-solid fa-file-csv"></i> Upload Donor CSV
              <input type="file" id="ds-csv-input" accept=".csv" style="display:none;" />
            </label>
            <button id="ds-seed-demo-btn" class="bx--btn bx--btn--secondary" style="padding:8px 16px;font-size:12px;border-radius:6px;">
              <i class="fa-solid fa-dice"></i> Seed 1,000 Random Donors
            </button>
            <button id="ds-load-sample-btn" class="bx--btn bx--btn--primary" style="padding:8px 16px;font-size:12px;border-radius:6px;">
              <i class="fa-solid fa-stethoscope"></i> Load Realistic 1,000-Donor Dataset
            </button>
            <button id="ds-clear-pool-btn" class="bx--btn bx--btn--secondary" style="padding:8px 16px;font-size:12px;border-radius:6px;background:#da1e28;">
              <i class="fa-solid fa-trash"></i> Clear Pool
            </button>
          </div>
        </div>
        <div style="margin-top:10px;font-size:11px;color:#6f6f6f;">
          CSV columns supported: donor_name, hospital, city, organ_type, blood_type, hla_type, age, max_ischemia_hours, lat, lng, registered_by
        </div>
      </div>

      <!-- ── Patient Search Form ──────────────────────────────────────── -->
      <div class="ultra-table-wrap" style="margin-bottom:1.5rem;background:rgba(38,38,38,0.6);border-radius:12px;padding:1.5rem;">
        <h4 style="color:#be95ff;font-size:14px;margin-bottom:1rem;"><i class="fa-solid fa-bed-pulse"></i> Patient Medical Information</h4>
        <form id="ds-search-form">
          <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;">
            <div class="form-group">
              <label>Patient Name</label>
              <input type="text" id="ds-p-name" value="Patient" />
            </div>
            <div class="form-group">
              <label>Organ Needed</label>
              <select id="ds-p-organ" required>
                <option value="Kidney">Kidney</option>
                <option value="Heart">Heart</option>
                <option value="Liver">Liver</option>
                <option value="Lung">Lung</option>
                <option value="Pancreas">Pancreas</option>
                <option value="Cornea">Cornea</option>
              </select>
            </div>
            <div class="form-group">
              <label>Blood Group</label>
              <select id="ds-p-blood" required>
                <option value="O+">O+</option>
                <option value="O-">O-</option>
                <option value="A+">A+</option>
                <option value="A-">A-</option>
                <option value="B+">B+</option>
                <option value="B-">B-</option>
                <option value="AB+">AB+</option>
                <option value="AB-">AB-</option>
              </select>
            </div>
            <div class="form-group">
              <label>Age</label>
              <input type="number" id="ds-p-age" value="45" min="0" max="110" />
            </div>
            <div class="form-group" style="grid-column: span 2;">
              <label>HLA Markers</label>
              <input type="text" id="ds-p-hla" value="A2,B7,DR4" />
            </div>
            <div class="form-group">
              <label>Urgency (1-10)</label>
              <input type="number" id="ds-p-urgency" value="8" min="1" max="10" />
            </div>
            <div class="form-group">
              <label>Patient Hospital Location</label>
              <select id="ds-p-location">
                <option value="12.9716,77.5946">Bengaluru (Apollo)</option>
                <option value="19.0760,72.8777">Mumbai</option>
                <option value="28.6139,77.2090">Delhi</option>
                <option value="13.0827,80.2707">Chennai</option>
                <option value="17.3850,78.4867">Hyderabad</option>
              </select>
            </div>
          </div>
          <button type="submit" id="ds-run-search-btn" class="bx--btn bx--btn--primary" style="margin-top:1.25rem;padding:10px 24px;border-radius:6px;font-size:13px;">
            <i class="fa-solid fa-atom"></i> Run Grover's Search Across Donor Pool
          </button>
        </form>
      </div>

      <!-- ── Live Grover's Algorithm Visualization ───────────────────── -->
      <div id="ds-grover-viz-wrap" style="display:none;margin-bottom:1.5rem;background:rgba(15,10,30,0.6);border:1px solid rgba(138,63,252,0.4);border-radius:12px;padding:1.5rem;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.75rem;">
          <h4 style="color:#be95ff;font-size:14px;margin:0;"><i class="fa-solid fa-atom fa-spin"></i> Grover's Amplitude Amplification — Live</h4>
          <div id="ds-grover-status" style="color:#8d8d8d;font-size:12px;"></div>
        </div>
        <div id="ds-grover-grid" style="display:grid;grid-template-columns:repeat(40,1fr);gap:2px;margin-bottom:0.75rem;"></div>
        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:0.75rem;font-size:11px;color:#a6a6a6;">
          <div>Pool size (N): <strong id="ds-g-n" style="color:#f4f4f4;">—</strong></div>
          <div>Classical O(N): <strong id="ds-g-classical" style="color:#ff8389;">—</strong> ops</div>
          <div>Grover O(√N): <strong id="ds-g-quantum" style="color:#42be65;">—</strong> ops</div>
          <div>Speedup: <strong id="ds-g-speedup" style="color:#be95ff;">—</strong>×</div>
        </div>
      </div>

      <!-- ── Ranked Results ───────────────────────────────────────────── -->
      <div id="ds-results-wrap" style="display:none;" class="ultra-table-wrap">
        <div class="ultra-table-header">
          <div class="ultra-table-title">Top Matches — Ranked by Compatibility Score</div>
        </div>
        <table class="utbl">
          <thead>
            <tr>
              <th>Rank</th><th>Donor</th><th>Hospital</th><th>Organ</th><th>Blood</th>
              <th>HLA Match</th><th>Distance</th><th>ETA</th><th>Match Score</th>
            </tr>
          </thead>
          <tbody id="ds-results-tbody"></tbody>
        </table>
      </div>
    </div>
  `;
}

async function refreshPoolStats() {
  try {
    const res = await fetch('/api/v1/donor-search/pool-stats');
    _poolStats = await res.json();
  } catch (e) {
    _poolStats = { pool_size: 0, by_organ: {}, by_blood_type: {} };
  }
  const badge = document.getElementById('ds-pool-badge');
  if (badge) {
    const organBreakdown = Object.entries(_poolStats.by_organ || {})
      .map(([k, v]) => `${k}: ${v}`).join(' · ');
    badge.innerHTML = _poolStats.pool_size > 0
      ? `<strong style="color:#42be65;">${_poolStats.pool_size.toLocaleString()} donors</strong> registered &nbsp;·&nbsp; ${organBreakdown || 'No breakdown'}`
      : `<span style="color:#ff8389;">Pool is empty</span> — upload a CSV or seed demo donors to begin searching`;
  }
}

function buildGroverGrid(n) {
  const grid = document.getElementById('ds-grover-grid');
  if (!grid) return;
  const cellCount = Math.min(400, Math.max(40, n)); // visualize up to 400 cells representing the pool
  grid.innerHTML = '';
  for (let i = 0; i < cellCount; i++) {
    const cell = document.createElement('div');
    cell.className = 'grover-cell';
    cell.style.cssText = 'width:100%;aspect-ratio:1;background:#2a2a3a;border-radius:2px;transition:background 0.12s;';
    grid.appendChild(cell);
  }
}

/**
 * Animates amplitude amplification: random cells "light up" (amplitude
 * probing) across grover_iterations rounds, converging on brighter and
 * brighter purple as iterations progress — then the winning cells (top
 * matches) lock in bright green at the end.
 */
function runGroverAnimation(iterations, winnersCount, onComplete) {
  const grid = document.getElementById('ds-grover-grid');
  const statusEl = document.getElementById('ds-grover-status');
  if (!grid) { onComplete(); return; }

  const cells = Array.from(grid.children);
  const winnerIdx = new Set();
  while (winnerIdx.size < Math.min(winnersCount, cells.length)) {
    winnerIdx.add(Math.floor(Math.random() * cells.length));
  }

  const totalRounds = Math.min(24, Math.max(6, iterations)); // cap animation length regardless of true iteration count
  let round = 0;

  function tick() {
    round++;
    const intensity = round / totalRounds;
    if (statusEl) statusEl.textContent = `Amplitude amplification round ${round}/${totalRounds}…`;

    cells.forEach((cell, i) => {
      if (winnerIdx.has(i)) {
        // Winning states gradually amplify toward bright green
        const g = Math.round(60 + intensity * 150);
        cell.style.background = `rgb(20,${g},80)`;
      } else if (Math.random() < 0.35) {
        // Random probing flicker on non-winning states (fading purple)
        const p = Math.round(80 + Math.random() * 100 * (1 - intensity));
        cell.style.background = `rgb(${p},${Math.round(p * 0.5)},${Math.round(p * 1.3)})`;
      } else {
        cell.style.background = '#2a2a3a';
      }
    });

    if (round < totalRounds) {
      setTimeout(tick, 90);
    } else {
      // Lock winners in bright green, dim everything else
      cells.forEach((cell, i) => {
        cell.style.background = winnerIdx.has(i) ? '#42be65' : '#1c1c1c';
      });
      if (statusEl) statusEl.textContent = `✔ Converged — ${winnersCount} top candidates isolated.`;
      onComplete();
    }
  }
  tick();
}

function renderResultsTable(results) {
  const tbody = document.getElementById('ds-results-tbody');
  if (!tbody) return;
  tbody.innerHTML = results.map((r, idx) => `
    <tr>
      <td><span class="bx--tag ${idx === 0 ? 'bx--tag--green' : 'bx--tag--blue'}">#${idx + 1}</span></td>
      <td><strong>${r.donor_name}</strong><div style="font-size:10px;color:#8d8d8d;">${r.registered_by || ''}</div></td>
      <td>${r.hospital}<div style="font-size:10px;color:#8d8d8d;">${r.city || ''}</div></td>
      <td>${r.organ_type}</td>
      <td><span class="bx--tag bx--tag--red">${r.blood_type}</span></td>
      <td>${r.hla_score}%</td>
      <td>${r.distance_km} km</td>
      <td>${r.eta_minutes} min</td>
      <td>
        <div style="display:flex;align-items:center;gap:8px;">
          <div style="width:60px;height:6px;background:#262626;border-radius:3px;overflow:hidden;">
            <div style="width:${r.match_score}%;height:100%;background:${r.match_score >= 70 ? '#42be65' : r.match_score >= 40 ? '#f1c21b' : '#da1e28'};"></div>
          </div>
          <strong style="color:${r.match_score >= 70 ? '#42be65' : r.match_score >= 40 ? '#f1c21b' : '#da1e28'};">${r.match_score}%</strong>
        </div>
      </td>
    </tr>
  `).join('');
}

export function attachDonorSearchEvents() {
  refreshPoolStats();

  document.getElementById('ds-csv-input')?.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);
    try {
      const res = await fetch('/api/v1/donor-search/upload-csv', { method: 'POST', body: formData });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Upload failed');
      ToastManager.show(`✅ ${data.rows_added} donors added from CSV (pool: ${data.pool_size})`, 'success');
      refreshPoolStats();
    } catch (err) {
      ToastManager.show(`Upload failed: ${err.message}`, 'error');
    }
    e.target.value = '';
  });

  document.getElementById('ds-seed-demo-btn')?.addEventListener('click', async () => {
    try {
      const res = await fetch('/api/v1/donor-search/seed-demo?count=1000&append=true', { method: 'POST' });
      const data = await res.json();
      ToastManager.show(`✅ Seeded — pool now has ${data.pool_size.toLocaleString()} donors`, 'success');
      refreshPoolStats();
    } catch (err) {
      ToastManager.show('Failed to seed demo donors', 'error');
    }
  });

  document.getElementById('ds-load-sample-btn')?.addEventListener('click', async () => {
    try {
      const res = await fetch('/api/v1/donor-search/load-sample-dataset', { method: 'POST' });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed to load sample dataset');
      ToastManager.show(`✅ Loaded realistic dataset — ${data.rows_added} donors with medical records ready`, 'success');
      refreshPoolStats();
    } catch (err) {
      ToastManager.show(err.message, 'error');
    }
  });

  document.getElementById('ds-clear-pool-btn')?.addEventListener('click', async () => {
    try {
      await fetch('/api/v1/donor-search/pool', { method: 'DELETE' });
      ToastManager.show('Donor pool cleared', 'info');
      refreshPoolStats();
    } catch (err) {
      ToastManager.show('Failed to clear pool', 'error');
    }
  });

  document.getElementById('ds-search-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const [lat, lng] = document.getElementById('ds-p-location').value.split(',').map(Number);
    const payload = {
      patient_name: document.getElementById('ds-p-name').value || 'Patient',
      target_organ: document.getElementById('ds-p-organ').value,
      blood_type: document.getElementById('ds-p-blood').value,
      hla_type: document.getElementById('ds-p-hla').value,
      urgency_score: parseInt(document.getElementById('ds-p-urgency').value) || 5,
      age: parseInt(document.getElementById('ds-p-age').value) || null,
      patient_lat: lat,
      patient_lng: lng,
      top_n: 10
    };

    const btn = document.getElementById('ds-run-search-btn');
    const vizWrap = document.getElementById('ds-grover-viz-wrap');
    const resultsWrap = document.getElementById('ds-results-wrap');
    if (btn) { btn.disabled = true; btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Searching…'; }
    if (resultsWrap) resultsWrap.style.display = 'none';

    try {
      const res = await fetch('/api/v1/donor-search/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Search failed');
      _lastSearchResult = data;

      // Show + build the live Grover visualization
      if (vizWrap) vizWrap.style.display = 'block';
      buildGroverGrid(data.pool_size);
      document.getElementById('ds-g-n').textContent = data.pool_size.toLocaleString();
      document.getElementById('ds-g-classical').textContent = data.classical_ops.toLocaleString();
      document.getElementById('ds-g-quantum').textContent = data.quantum_ops.toLocaleString();
      document.getElementById('ds-g-speedup').textContent = data.speedup_factor.toLocaleString();

      runGroverAnimation(data.grover_iterations, data.results.length, () => {
        if (btn) { btn.disabled = false; btn.innerHTML = '<i class="fa-solid fa-atom"></i> Run Grover\'s Search Across Donor Pool'; }
        if (resultsWrap) resultsWrap.style.display = 'block';
        renderResultsTable(data.results);
        ToastManager.show(`✔ Found ${data.results.length} ranked matches out of ${data.candidates_matching_organ} organ-compatible donors`, 'success');
      });
    } catch (err) {
      if (btn) { btn.disabled = false; btn.innerHTML = '<i class="fa-solid fa-atom"></i> Run Grover\'s Search Across Donor Pool'; }
      ToastManager.show(err.message, 'error');
    }
  });
}
