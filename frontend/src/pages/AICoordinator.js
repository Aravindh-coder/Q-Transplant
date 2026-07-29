/**
 * AI Autonomous Coordinator Module
 * Trigger autonomous 9-step decision workflow for organ matching, ICU booking,
 * ambulance dispatch, risk evaluation, and stakeholder notifications.
 */

export function renderAICoordinatorView() {
  return `
    <div>
      <div class="dash-header">
        <div>
          <h1 class="dash-title"><i class="fa-solid fa-robot" style="color:#ff6b35;margin-right:8px;"></i>Autonomous AI Coordinator Engine</h1>
          <p class="dash-subtitle">Self-Driving Organ Matching, Resource Booking & Transport Dispatch Pipeline</p>
        </div>
      </div>

      <!-- Trigger Section -->
      <div class="ultra-table-wrap" style="margin-bottom: 2rem; background: rgba(38,38,38,0.6); padding: 1.5rem; border-radius: 12px;">
        <h4 style="font-size:14px; font-weight:600; color:#f4f4f4; margin-bottom:1rem;"><i class="fa-solid fa-bolt" style="color:#f1c21b;"></i> Trigger Autonomous Transplant Pipeline</h4>
        <p style="font-size:13px; color:#8d8d8d; margin-bottom:1.25rem;">
          Select a donor organ to launch the 9-step autonomous AI agent workflow. The system will independently execute Grover's search, select the recipient, book an ICU bed, assign an ambulance, compute survival risks, and alert doctors & organizers.
        </p>

        <div style="display:flex; gap:1rem; align-items:center; max-width:600px;">
          <select id="coord-organ-select" class="form-control" style="flex:1; background:#161616; color:#f4f4f4; border:1px solid #393939; padding:10px; border-radius:6px; font-size:13px;">
            <option value="1">Organ #1: Heart (O+) — Cold Box BOX-ESP32-001 (Available)</option>
            <option value="2">Organ #2: Kidney (A+) — Cold Box BOX-ESP32-002 (Available)</option>
            <option value="3">Organ #3: Liver (B+) — Cold Box BOX-ESP32-003 (Available)</option>
          </select>
          <button id="btn-trigger-coordinator" class="btn-hero-primary" style="padding:12px 24px; font-size:13px; white-space:nowrap;">
            <i class="fa-solid fa-play"></i> LAUNCH AI COORDINATOR
          </button>
        </div>
      </div>

      <!-- Execution Pipeline Output -->
      <div id="coordinator-output-panel" style="display:none;">
        <div style="background:#0f0f0f; border:1px solid #ff6b35; border-radius:12px; padding:1.5rem; margin-bottom:1.5rem; box-shadow:0 0 25px rgba(255,107,53,0.15);">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1.25rem;">
            <h3 style="font-size:16px; font-weight:700; color:#ff6b35; margin:0;"><i class="fa-solid fa-diagram-next"></i> AUTONOMOUS DECISION TRAIL</h3>
            <span class="bx--tag bx--tag--green" id="coord-status-badge">EXECUTING PIPELINE...</span>
          </div>

          <div id="coordinator-steps-timeline" style="display:flex; flex-direction:column; gap:12px;">
            <!-- Dynamic steps rendered here -->
          </div>
        </div>

        <!-- Recommendation Card -->
        <div id="coordinator-recommendation-card" style="display:none; background:rgba(66,190,101,0.08); border:1px solid #42be65; border-radius:12px; padding:1.5rem;">
          <h4 style="color:#42be65; font-size:15px; margin-bottom:1rem;"><i class="fa-solid fa-square-check"></i> FINAL AI TRANSPLANT RECOMMENDATION REPORT</h4>
          <div id="coord-rec-body" style="font-size:13px; color:#f4f4f4; line-height:1.6;"></div>
        </div>
      </div>
    </div>
  `;
}

export function attachAICoordinatorEvents() {
  const btnTrigger = document.getElementById('btn-trigger-coordinator');
  if (btnTrigger) {
    btnTrigger.onclick = async () => {
      const organId = document.getElementById('coord-organ-select')?.value || 1;
      await runAICoordinator(organId);
    };
  }
}

async function runAICoordinator(organId) {
  const outputPanel = document.getElementById('coordinator-output-panel');
  const stepsContainer = document.getElementById('coordinator-steps-timeline');
  const recCard = document.getElementById('coordinator-recommendation-card');
  const badge = document.getElementById('coord-status-badge');

  if (outputPanel) outputPanel.style.display = 'block';
  if (stepsContainer) stepsContainer.innerHTML = `<div style="color:#8d8d8d; font-size:12px;">Initializing autonomous agents...</div>`;
  if (recCard) recCard.style.display = 'none';

  try {
    const token = localStorage.getItem('token');
    const res = await fetch(`/api/v1/coordinator/trigger/${organId}`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (!res.ok) throw new Error('Failed to run coordinator');
    const data = await res.json();

    if (badge) badge.textContent = 'WORKFLOW COMPLETED';

    // Animate step rendering
    stepsContainer.innerHTML = '';
    data.steps.forEach((s, idx) => {
      setTimeout(() => {
        const stepEl = document.createElement('div');
        stepEl.style.cssText = `
          background:#161616; border:1px solid ${s.status === 'warning' ? '#f1c21b' : '#393939'};
          border-left:4px solid ${s.status === 'warning' ? '#f1c21b' : '#ff6b35'};
          border-radius:6px; padding:12px; font-size:12px; color:#c6c6c6; animation: fadeIn 0.3s ease;
        `;
        stepEl.innerHTML = `
          <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
            <strong style="color:#ff6b35;">Step ${idx+1}: [${s.agent}] — ${s.action}</strong>
            <span style="font-size:10px; color:#8d8d8d;">${new Date(s.timestamp).toLocaleTimeString()}</span>
          </div>
          <div>${s.detail}</div>
        `;
        stepsContainer.appendChild(stepEl);
      }, idx * 250);
    });

    // Render recommendation after all steps
    setTimeout(() => {
      if (recCard) recCard.style.display = 'block';
      const rec = data.recommendation;
      document.getElementById('coord-rec-body').innerHTML = `
        <div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:1rem; margin-bottom:1rem; background:#161616; padding:1rem; border-radius:8px;">
          <div><span style="color:#8d8d8d; font-size:11px;">Recipient</span><br/><strong style="color:#be95ff;">${rec.best_patient}</strong></div>
          <div><span style="color:#8d8d8d; font-size:11px;">Hospital</span><br/><strong style="color:#78a9ff;">${rec.best_hospital}</strong></div>
          <div><span style="color:#8d8d8d; font-size:11px;">Transport</span><br/><strong style="color:#42be65;">${rec.ambulance} (ETA ${rec.eta_minutes}m)</strong></div>
          <div><span style="color:#8d8d8d; font-size:11px;">1-Yr Survival</span><br/><strong style="color:#f1c21b;">${rec.one_year_survival}%</strong></div>
        </div>
        <div style="font-size:13px; color:#42be65; font-weight:600;">
          💡 AI DECISION: ${rec.recommendation}
        </div>
        <div style="font-size:10px; color:#8d8d8d; margin-top:8px;">
          Workflow executed in ${rec.coordinator_duration_ms}ms · Audit log saved.
        </div>
      `;
    }, data.steps.length * 250 + 200);

  } catch (err) {
    console.error('Error running AI coordinator:', err);
    if (stepsContainer) stepsContainer.innerHTML = `<div style="color:#da1e28;">Error executing AI coordinator: ${err.message}</div>`;
  }
}
