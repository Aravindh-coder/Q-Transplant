/**
 * Blockchain Explorer Dashboard (Mission 3)
 * Cryptographic SHA-256 Block Chain Viewer, Tamper Detector, Chain Export
 */
export function renderBlockchainView() {
  return `
    <div style="padding:0 1rem;">
      <div class="dash-title-row" style="margin-bottom:1.5rem;">
        <h1 class="dash-title">
          <i class="fa-solid fa-link" style="color:#f1c21b;margin-right:10px;"></i>
          Blockchain Audit Ledger
        </h1>
        <div style="display:flex;gap:8px;">
          <button id="btn-bc-verify" class="bx--btn bx--btn--primary" style="font-size:11px;padding:6px 14px;">
            <i class="fa-solid fa-shield-check"></i> Verify Integrity
          </button>
          <button id="btn-bc-add" class="bx--btn bx--btn--secondary" style="font-size:11px;padding:6px 14px;">
            <i class="fa-solid fa-plus"></i> Add Test Block
          </button>
          <a href="/api/v1/ai/blockchain/export" class="bx--btn bx--btn--ghost" style="font-size:11px;padding:6px 14px;text-decoration:none;">
            <i class="fa-solid fa-download"></i> Export Chain
          </a>
        </div>
      </div>

      <div id="bc-integrity-result"></div>

      <div class="glass-card" style="padding:1.5rem;margin-bottom:1.5rem;">
        <h3 style="color:#f1c21b;margin-bottom:1rem;font-size:14px;font-weight:700;">
          <i class="fa-solid fa-cubes"></i> Immutable Block Chain Explorer
        </h3>
        <div id="blockchain-chain-list">
          <div style="text-align:center;color:#525252;padding:1.5rem;font-size:13px;">Loading blockchain...</div>
        </div>
      </div>
    </div>
  `;
}

export function attachBlockchainEvents() {
  function loadChain() {
    fetch('/api/v1/ai/blockchain/chain').then(r => r.json()).then(blocks => {
      const el = document.getElementById('blockchain-chain-list');
      if (!el) return;
      if (!blocks.length) {
        el.innerHTML = `<div style="text-align:center;color:#525252;padding:1.5rem;font-size:13px;">No blocks yet. Add a test block to initialize the chain.</div>`;
        return;
      }
      el.innerHTML = `
        <div style="display:flex;flex-direction:column;gap:0.75rem;">
          ${blocks.slice().reverse().map((b, i) => `
            <div style="background:#0d0d18;border:1px solid rgba(241,194,27,0.2);border-radius:8px;padding:1rem;">
              <div style="display:flex;align-items:center;gap:1rem;margin-bottom:0.75rem;">
                <div style="background:rgba(241,194,27,0.15);border:1px solid rgba(241,194,27,0.4);border-radius:50%;width:40px;height:40px;display:flex;align-items:center;justify-content:center;flex-shrink:0;">
                  <span style="color:#f1c21b;font-weight:900;font-size:14px;">#${b.index}</span>
                </div>
                <div style="flex:1;">
                  <div style="font-size:12px;font-weight:700;color:#f4f4f4;">${b.action}</div>
                  <div style="font-size:11px;color:#8d8d8d;">${b.actor} · ${b.hospital}</div>
                </div>
                <div style="text-align:right;">
                  <div style="font-size:10px;color:#525252;font-family:monospace;">${new Date(b.timestamp).toLocaleString()}</div>
                </div>
              </div>
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.5rem;">
                <div style="background:#161616;border-radius:4px;padding:0.5rem;">
                  <div style="font-size:9px;color:#8d8d8d;font-weight:700;margin-bottom:2px;">BLOCK HASH</div>
                  <div style="font-family:monospace;font-size:9px;color:#42be65;word-break:break-all;">${b.hash}</div>
                </div>
                <div style="background:#161616;border-radius:4px;padding:0.5rem;">
                  <div style="font-size:9px;color:#8d8d8d;font-weight:700;margin-bottom:2px;">PREV HASH</div>
                  <div style="font-family:monospace;font-size:9px;color:#525252;word-break:break-all;">${b.prev_hash}</div>
                </div>
              </div>
              ${b.details ? `<div style="margin-top:0.5rem;font-size:11px;color:#8d8d8d;">${b.details}</div>` : ''}
            </div>
          `).join('')}
        </div>
      `;
    }).catch(() => {});
  }

  loadChain();

  document.getElementById('btn-bc-verify')?.addEventListener('click', async () => {
    const res = await fetch('/api/v1/ai/blockchain/verify').then(r => r.json());
    const el = document.getElementById('bc-integrity-result');
    if (!el) return;
    const color = res.valid ? '#42be65' : '#da1e28';
    const icon = res.valid ? 'fa-shield-check' : 'fa-triangle-exclamation';
    el.innerHTML = `
      <div style="background:${res.valid ? 'rgba(66,190,101,0.1)' : 'rgba(218,30,40,0.1)'};border:1px solid ${color};border-radius:8px;padding:1rem;margin-bottom:1rem;display:flex;align-items:center;gap:1rem;">
        <i class="fa-solid ${icon}" style="color:${color};font-size:1.5rem;"></i>
        <div>
          <div style="font-weight:700;color:${color};">${res.valid ? 'CHAIN INTEGRITY VERIFIED' : 'TAMPERING DETECTED'}</div>
          <div style="font-size:12px;color:#8d8d8d;">${res.message}</div>
        </div>
      </div>
    `;
  });

  document.getElementById('btn-bc-add')?.addEventListener('click', async () => {
    await fetch('/api/v1/ai/blockchain/add-block', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        actor: 'Organizer Admin',
        hospital: 'Apollo Specialty Hospital',
        action: 'TEST_BLOCK',
        details: 'Manual test block created from Blockchain Explorer dashboard'
      })
    });
    loadChain();
  });
}

/**
 * Federated Learning Dashboard (Mission 4)
 */
export function renderFederatedLearningView() {
  return `
    <div style="padding:0 1rem;">
      <div class="dash-title-row" style="margin-bottom:1.5rem;">
        <h1 class="dash-title">
          <i class="fa-solid fa-network-wired" style="color:#42be65;margin-right:10px;"></i>
          Federated Learning Framework
        </h1>
        <div style="display:flex;gap:8px;">
          <button id="btn-fed-run-round" class="bx--btn bx--btn--primary" style="font-size:11px;padding:6px 14px;">
            <i class="fa-solid fa-play"></i> Run Federated Round
          </button>
          <button id="btn-fed-load-history" class="bx--btn bx--btn--ghost" style="font-size:11px;padding:6px 14px;">
            <i class="fa-solid fa-history"></i> Load History
          </button>
        </div>
      </div>

      <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin-bottom:1.5rem;">
        ${[
          {name:'Apollo Specialty Hospital',id:'H001',color:'#0f62fe'},
          {name:'Fortis Bangalore',id:'H002',color:'#42be65'},
          {name:'Manipal Hospital',id:'H003',color:'#f1c21b'},
          {name:'Narayana Hrudayalaya',id:'H004',color:'#da1e28'}
        ].map(h => `
          <div class="glass-card" style="padding:1rem;border-color:rgba(255,255,255,0.1);">
            <div style="width:10px;height:10px;border-radius:50%;background:${h.color};margin-bottom:0.5rem;"></div>
            <div style="font-size:11px;font-weight:700;color:#f4f4f4;">${h.name}</div>
            <div style="font-size:10px;color:#8d8d8d;margin-top:2px;">${h.id} · Privacy Preserved</div>
            <div id="fed-node-${h.id}" style="font-size:10px;color:#525252;margin-top:6px;">Idle</div>
          </div>
        `).join('')}
      </div>

      <div id="fed-round-result">
        <div class="glass-card" style="padding:2rem;text-align:center;">
          <i class="fa-solid fa-network-wired" style="font-size:2.5rem;color:#42be65;margin-bottom:1rem;display:block;"></i>
          <p style="color:#8d8d8d;font-size:13px;">No hospital data is shared. Only gradients are sent.<br>Click <strong style="color:#42be65;">Run Federated Round</strong> to start.</p>
        </div>
      </div>

      <div class="glass-card" style="margin-top:1.5rem;padding:1.5rem;">
        <h3 style="color:#42be65;font-size:14px;font-weight:700;margin-bottom:1rem;"><i class="fa-solid fa-chart-line"></i> Session History</h3>
        <div id="fed-history"></div>
      </div>
    </div>
  `;
}

export function attachFederatedLearningEvents() {
  function loadHistory() {
    fetch('/api/v1/ai/federated/history').then(r => r.json()).then(sessions => {
      const el = document.getElementById('fed-history');
      if (!el) return;
      if (!sessions.length) {
        el.innerHTML = '<div style="text-align:center;color:#525252;font-size:12px;padding:1rem;">No rounds completed yet.</div>';
        return;
      }
      el.innerHTML = `
        <table class="utbl" style="font-size:12px;">
          <thead><tr><th>Round</th><th>Global Accuracy</th><th>Global Loss</th><th>Hospitals</th><th>Timestamp</th></tr></thead>
          <tbody>
            ${sessions.map(s => `
              <tr>
                <td><strong>#${s.round}</strong></td>
                <td style="color:#42be65;font-weight:700;">${(s.global_accuracy * 100).toFixed(2)}%</td>
                <td style="color:#f1c21b;">${s.global_loss.toFixed(4)}</td>
                <td>${s.hospitals} nodes</td>
                <td style="font-size:10px;color:#8d8d8d;">${new Date(s.created_at).toLocaleString()}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      `;
    }).catch(() => {});
  }

  document.getElementById('btn-fed-run-round')?.addEventListener('click', async () => {
    const el = document.getElementById('fed-round-result');
    if (el) el.innerHTML = `<div class="glass-card" style="padding:1.5rem;text-align:center;"><div style="width:32px;height:32px;border:3px solid #42be65;border-top-color:transparent;border-radius:50%;animation:spin 0.8s linear infinite;margin:0 auto 1rem;"></div><p style="color:#42be65;font-size:13px;">Running Federated Round (FedAvg across 4 hospitals)...</p></div>`;

    try {
      const r = await fetch('/api/v1/ai/federated/run-round', { method: 'POST' });
      const data = await r.json();

      data.node_results?.forEach(node => {
        const nodeEl = document.getElementById(`fed-node-${node.node_id}`);
        if (nodeEl) nodeEl.innerHTML = `Acc: <span style="color:#42be65;">${(node.local_accuracy*100).toFixed(1)}%</span> · Loss: <span style="color:#f1c21b;">${node.local_loss.toFixed(3)}</span> · ${node.local_records} records`;
      });

      if (el) el.innerHTML = `
        <div class="glass-card" style="padding:1.5rem;border-color:rgba(66,190,101,0.3);">
          <h4 style="color:#42be65;margin-bottom:1rem;"><i class="fa-solid fa-check-circle"></i> Round #${data.round} Complete — FedAvg Results</h4>
          <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:1rem;">
            <div style="text-align:center;"><div style="font-size:24px;font-weight:900;color:#42be65;">${(data.federated.global_accuracy*100).toFixed(2)}%</div><div style="font-size:10px;color:#8d8d8d;">Federated Accuracy</div></div>
            <div style="text-align:center;"><div style="font-size:24px;font-weight:900;color:#0f62fe;">${(data.centralized_baseline.accuracy*100).toFixed(2)}%</div><div style="font-size:10px;color:#8d8d8d;">Centralized Baseline</div></div>
            <div style="text-align:center;"><div style="font-size:24px;font-weight:900;color:#f1c21b;">${data.accuracy_gap_percent}%</div><div style="font-size:10px;color:#8d8d8d;">Accuracy Gap</div></div>
          </div>
          <div style="margin-top:1rem;font-size:11px;color:#8d8d8d;text-align:center;">🔒 ${data.federated_advantage} · ${data.federated.total_records_used} total records used</div>
        </div>
      `;
      loadHistory();
    } catch (err) {}
  });

  document.getElementById('btn-fed-load-history')?.addEventListener('click', loadHistory);
  loadHistory();
}

/**
 * Multi-Agent System Dashboard (Mission 5)
 */
export function renderMultiAgentView() {
  return `
    <div style="padding:0 1rem;">
      <div class="dash-title-row" style="margin-bottom:1.5rem;">
        <h1 class="dash-title">
          <i class="fa-solid fa-robot" style="color:#ff6b35;margin-right:10px;"></i>
          Autonomous Multi-Agent Coordination
        </h1>
        <button id="btn-agents-run" class="bx--btn bx--btn--primary" style="font-size:11px;padding:6px 14px;">
          <i class="fa-solid fa-play"></i> Run Agent Cycle
        </button>
      </div>

      <div style="display:grid;grid-template-columns:repeat(7,1fr);gap:0.5rem;margin-bottom:1.5rem;">
        ${[
          {id:'coordinator',name:'Coordinator',icon:'fa-sitemap',color:'#0f62fe'},
          {id:'doctor',name:'Doctor',icon:'fa-user-doctor',color:'#8a3ffc'},
          {id:'hospital',name:'Hospital',icon:'fa-hospital',color:'#da1e28'},
          {id:'donor',name:'Donor',icon:'fa-hand-holding-heart',color:'#198038'},
          {id:'patient',name:'Patient',icon:'fa-bed-pulse',color:'#f1c21b'},
          {id:'transport',name:'Transport',icon:'fa-truck-medical',color:'#00b0ff'},
          {id:'risk',name:'Risk',icon:'fa-shield-halved',color:'#ff6b35'}
        ].map(a => `
          <div class="glass-card agent-node" id="agent-${a.id}" style="padding:0.75rem;text-align:center;border-color:rgba(255,255,255,0.1);transition:all 0.3s;">
            <i class="fa-solid ${a.icon}" style="color:${a.color};font-size:1.2rem;margin-bottom:4px;display:block;"></i>
            <div style="font-size:9px;font-weight:700;color:#f4f4f4;">${a.name}</div>
            <div class="agent-status-${a.id}" style="font-size:8px;color:#525252;margin-top:2px;">Idle</div>
          </div>
        `).join('')}
      </div>

      <div class="glass-card" style="padding:1.5rem;">
        <h3 style="color:#ff6b35;font-size:14px;font-weight:700;margin-bottom:1rem;"><i class="fa-solid fa-comments"></i> Agent Communication Graph</h3>
        <div id="agent-message-log">
          <div style="text-align:center;color:#525252;padding:1.5rem;font-size:13px;">Run a cycle to see agent coordination messages.</div>
        </div>
      </div>
    </div>
  `;
}

export function attachMultiAgentEvents() {
  const AGENT_COLORS = {
    coordinator:'#0f62fe', doctor:'#8a3ffc', hospital:'#da1e28',
    donor:'#198038', patient:'#f1c21b', transport:'#00b0ff', risk:'#ff6b35'
  };

  document.getElementById('btn-agents-run')?.addEventListener('click', async () => {
    const logEl = document.getElementById('agent-message-log');
    if (logEl) logEl.innerHTML = `<div style="text-align:center;color:#ff6b35;padding:1rem;"><div style="width:28px;height:28px;border:2px solid #ff6b35;border-top-color:transparent;border-radius:50%;animation:spin 0.8s linear infinite;margin:0 auto 0.5rem;"></div>Agents coordinating...</div>`;

    try {
      const r = await fetch('/api/v1/ai/agents/run-cycle', { method: 'POST' });
      const data = await r.json();

      // Flash active agent nodes
      data.messages?.forEach((msg, i) => {
        setTimeout(() => {
          document.querySelectorAll('.agent-node').forEach(n => n.style.boxShadow = '');
          const senderEl = document.getElementById(`agent-${msg.sender_id}`);
          if (senderEl) senderEl.style.boxShadow = `0 0 12px ${msg.sender_color}`;
          const statusEl = document.querySelector(`.agent-status-${msg.sender_id}`);
          if (statusEl) statusEl.textContent = msg.action;
        }, i * 500);
      });

      if (logEl) logEl.innerHTML = `
        <div style="margin-bottom:0.5rem;font-size:11px;color:#8d8d8d;">Trigger: <strong style="color:#f4f4f4;">${data.trigger}</strong> · ${data.total_messages} messages · ${data.coordination_latency_ms}ms</div>
        <div style="display:flex;flex-direction:column;gap:0.5rem;max-height:400px;overflow-y:auto;">
          ${data.messages.map(msg => `
            <div style="display:flex;align-items:flex-start;gap:0.75rem;background:#1a1a2e;border-radius:6px;padding:0.75rem;">
              <div style="flex-shrink:0;width:8px;height:8px;border-radius:50%;background:${msg.sender_color};margin-top:4px;"></div>
              <div style="flex:1;">
                <div style="font-size:11px;font-weight:700;">
                  <span style="color:${msg.sender_color};">${msg.sender_name}</span>
                  <span style="color:#525252;margin:0 4px;">→</span>
                  <span style="color:${msg.recipient_color};">${msg.recipient_name}</span>
                  <span class="bx--tag" style="margin-left:8px;background:rgba(255,255,255,0.05);color:#8d8d8d;font-size:9px;padding:1px 6px;">${msg.action}</span>
                </div>
                <div style="font-size:12px;color:#c6c6c6;margin-top:3px;">${msg.message}</div>
              </div>
              <div style="font-size:9px;color:#525252;flex-shrink:0;">${msg.timestamp}</div>
            </div>
          `).join('')}
        </div>
      `;
    } catch (err) {}
  });
}

/**
 * Research Analytics Dashboard (Mission 9)
 */
export function renderResearchAnalyticsView() {
  return `
    <div style="padding:0 1rem;">
      <div class="dash-title-row" style="margin-bottom:1.5rem;">
        <h1 class="dash-title">
          <i class="fa-solid fa-chart-mixed" style="color:#be95ff;margin-right:10px;"></i>
          Research Analytics Platform
        </h1>
        <button id="btn-analytics-load" class="bx--btn bx--btn--primary" style="font-size:11px;padding:6px 14px;">
          <i class="fa-solid fa-sync"></i> Refresh Analytics
        </button>
      </div>
      <div id="analytics-content">
        <div style="text-align:center;color:#525252;padding:2rem;font-size:13px;">Loading analytics...</div>
      </div>
    </div>
  `;
}

export function attachResearchAnalyticsEvents() {
  function loadAnalytics() {
    fetch('/api/v1/ai/analytics').then(r => r.json()).then(data => {
      const el = document.getElementById('analytics-content');
      if (!el) return;

      const pa = data.prediction_accuracy || {};
      const wt = data.waiting_time || {};
      const hu = data.hospital_utilization || {};
      const qm = data.quantum_matching || {};
      const tl = data.timeline || {};

      el.innerHTML = `
        <!-- Model Accuracy Comparison -->
        <div class="glass-card" style="padding:1.5rem;margin-bottom:1.5rem;">
          <h3 style="color:#be95ff;font-size:14px;font-weight:700;margin-bottom:1rem;"><i class="fa-solid fa-trophy"></i> Model Accuracy Benchmark</h3>
          <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:0.75rem;">
            ${Object.entries(pa).map(([model, metrics]) => `
              <div style="text-align:center;background:#1a1a2e;border-radius:8px;padding:1rem;">
                <div style="font-size:24px;font-weight:900;color:${model==='ensemble'?'#42be65':'#0f62fe'};">${metrics.accuracy}%</div>
                <div style="font-size:9px;color:#8d8d8d;margin-top:2px;text-transform:uppercase;">${model}</div>
                <div style="height:3px;background:#393939;border-radius:2px;margin-top:8px;">
                  <div style="width:${metrics.accuracy}%;height:100%;background:${model==='ensemble'?'#42be65':'#0f62fe'};border-radius:2px;"></div>
                </div>
              </div>
            `).join('')}
          </div>
        </div>

        <!-- Quantum Matching vs Classical -->
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:1rem;margin-bottom:1.5rem;">
          <div class="glass-card" style="padding:1.25rem;text-align:center;">
            <i class="fa-solid fa-atom" style="color:#8a3ffc;font-size:1.5rem;margin-bottom:0.5rem;display:block;"></i>
            <div style="font-size:22px;font-weight:900;color:#8a3ffc;">${qm.avg_compatibility_score}%</div>
            <div style="font-size:10px;color:#8d8d8d;">Quantum Match Score</div>
            <div style="font-size:10px;color:#42be65;margin-top:4px;">+${qm.quantum_advantage_percent}% vs Classical</div>
          </div>
          <div class="glass-card" style="padding:1.25rem;text-align:center;">
            <i class="fa-solid fa-clock" style="color:#f1c21b;font-size:1.5rem;margin-bottom:0.5rem;display:block;"></i>
            <div style="font-size:22px;font-weight:900;color:#f1c21b;">${wt.avg_waiting_days} days</div>
            <div style="font-size:10px;color:#8d8d8d;">Avg Waiting Time</div>
            <div style="font-size:10px;color:#8d8d8d;margin-top:4px;">Median: ${wt.median_waiting_days} days</div>
          </div>
          <div class="glass-card" style="padding:1.25rem;text-align:center;">
            <i class="fa-solid fa-hospital" style="color:#00b0ff;font-size:1.5rem;margin-bottom:0.5rem;display:block;"></i>
            <div style="font-size:22px;font-weight:900;color:#00b0ff;">${hu.avg_icu_utilization}%</div>
            <div style="font-size:10px;color:#8d8d8d;">Avg ICU Utilization</div>
            <div style="font-size:10px;color:#8d8d8d;margin-top:4px;">${hu.hospitals_connected} hospitals</div>
          </div>
        </div>

        <!-- Hospital Rankings -->
        <div class="glass-card" style="padding:1.5rem;margin-bottom:1.5rem;">
          <h3 style="color:#00b0ff;font-size:14px;font-weight:700;margin-bottom:1rem;"><i class="fa-solid fa-ranking-star"></i> Hospital Transplant Rankings</h3>
          <table class="utbl">
            <thead><tr><th>Rank</th><th>Hospital</th><th>Transplants</th><th>Success Rate</th></tr></thead>
            <tbody>
              ${(hu.rankings || []).map((h, i) => `
                <tr>
                  <td><strong style="color:#f1c21b;">#${i+1}</strong></td>
                  <td>${h.name}</td>
                  <td>${h.transplants}</td>
                  <td>
                    <div style="display:flex;align-items:center;gap:8px;">
                      <div style="flex:1;height:5px;background:#393939;border-radius:3px;">
                        <div style="width:${h.success_rate}%;height:100%;background:#42be65;border-radius:3px;"></div>
                      </div>
                      <span style="font-weight:700;color:#42be65;">${h.success_rate}%</span>
                    </div>
                  </td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>

        <!-- Trend Chart (text-based) -->
        <div class="glass-card" style="padding:1.5rem;">
          <h3 style="color:#be95ff;font-size:14px;font-weight:700;margin-bottom:1rem;"><i class="fa-solid fa-chart-line"></i> Prediction Accuracy Trend (12 Months)</h3>
          <div style="display:flex;align-items:flex-end;gap:4px;height:80px;padding:0 0.5rem;">
            ${(tl.prediction_accuracy_trend || []).map((val, i) => `
              <div style="flex:1;display:flex;flex-direction:column;align-items:center;gap:3px;">
                <div style="width:100%;background:linear-gradient(to top,#8a3ffc,#0f62fe);border-radius:2px 2px 0 0;height:${(val/100)*70}px;min-height:4px;"></div>
                <div style="font-size:8px;color:#525252;">${(tl.months||[])[i]||''}</div>
              </div>
            `).join('')}
          </div>
        </div>
      `;
    }).catch(() => {});
  }

  loadAnalytics();
  document.getElementById('btn-analytics-load')?.addEventListener('click', loadAnalytics);
}

/**
 * Synthetic Data Generation Dashboard (Mission 10)
 */
export function renderSyntheticDataView() {
  return `
    <div style="padding:0 1rem;">
      <div class="dash-title-row" style="margin-bottom:1.5rem;">
        <h1 class="dash-title">
          <i class="fa-solid fa-database" style="color:#42be65;margin-right:10px;"></i>
          Synthetic Data Generation Lab
        </h1>
      </div>

      <div class="glass-card" style="padding:1.5rem;margin-bottom:1.5rem;">
        <h3 style="color:#42be65;font-size:14px;font-weight:700;margin-bottom:1rem;"><i class="fa-solid fa-sliders"></i> Dataset Configuration</h3>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">
          <div class="form-group">
            <label>Record Count</label>
            <select id="synth-count">
              <option value="100">100 Records</option>
              <option value="1000" selected>1,000 Records</option>
              <option value="10000">10,000 Records</option>
              <option value="50000">50,000 Records</option>
              <option value="100000">100,000 Records</option>
            </select>
          </div>
          <div class="form-group">
            <label>Export Format</label>
            <select id="synth-format">
              <option value="json">JSON</option>
              <option value="csv">CSV</option>
              <option value="sql">SQL INSERT Statements</option>
            </select>
          </div>
        </div>
        <div style="display:flex;gap:0.75rem;margin-top:1rem;flex-wrap:wrap;">
          <button id="btn-synth-stats" class="bx--btn bx--btn--primary" style="font-size:12px;padding:8px 16px;">
            <i class="fa-solid fa-chart-bar"></i> Generate & Show Stats
          </button>
          <button id="btn-synth-export" class="bx--btn bx--btn--secondary" style="font-size:12px;padding:8px 16px;">
            <i class="fa-solid fa-download"></i> Download Dataset
          </button>
        </div>
      </div>

      <div id="synth-stats-result">
        <div class="glass-card" style="padding:2rem;text-align:center;">
          <i class="fa-solid fa-database" style="font-size:2rem;color:#393939;display:block;margin-bottom:0.75rem;"></i>
          <p style="color:#525252;font-size:13px;">Configure dataset parameters above and click <strong style="color:#42be65;">Generate & Show Stats</strong>.</p>
        </div>
      </div>
    </div>
  `;
}

export function attachSyntheticDataEvents() {
  document.getElementById('btn-synth-stats')?.addEventListener('click', async () => {
    const count = document.getElementById('synth-count').value;
    const el = document.getElementById('synth-stats-result');
    if (el) el.innerHTML = `<div class="glass-card" style="padding:1.5rem;text-align:center;"><div style="width:28px;height:28px;border:2px solid #42be65;border-top-color:transparent;border-radius:50%;animation:spin 0.8s linear infinite;margin:0 auto 0.75rem;"></div><p style="color:#42be65;font-size:12px;">Generating ${parseInt(count).toLocaleString()} synthetic records...</p></div>`;

    try {
      const data = await fetch(`/api/v1/ai/synthetic/stats?count=${count}`).then(r => r.json());
      const bloodColors = {'O+':'#42be65','O-':'#198038','A+':'#0f62fe','A-':'#0043ce','B+':'#f1c21b','B-':'#b45309','AB+':'#8a3ffc','AB-':'#6929c4'};

      if (el) el.innerHTML = `
        <div class="glass-card" style="padding:1.5rem;">
          <h3 style="color:#42be65;font-size:14px;margin-bottom:1rem;"><i class="fa-solid fa-chart-bar"></i> Dataset Benchmark Statistics</h3>
          <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin-bottom:1.5rem;">
            ${[
              ['Total Records', data.total_records?.toLocaleString(),'#f4f4f4','fa-database'],
              ['Successful Transplants', data.successful_transplants?.toLocaleString(),'#42be65','fa-check-circle'],
              ['Success Rate', data.success_rate + '%', '#0f62fe', 'fa-percent'],
              ['Avg 1-Yr Survival', data.avg_one_year_survival + '%', '#be95ff', 'fa-heart-pulse'],
              ['Avg Waiting Days', data.avg_waiting_days?.toLocaleString(), '#f1c21b', 'fa-clock'],
              ['Avg Cold Ischemia', data.avg_cold_ischemia_hours + ' hrs', '#00b0ff', 'fa-snowflake']
            ].map(([label, val, color, icon]) => `
              <div style="background:#1a1a2e;border-radius:8px;padding:1rem;text-align:center;">
                <i class="fa-solid ${icon}" style="color:${color};margin-bottom:6px;display:block;"></i>
                <div style="font-size:20px;font-weight:800;color:${color};">${val}</div>
                <div style="font-size:10px;color:#8d8d8d;">${label}</div>
              </div>
            `).join('')}
          </div>

          <div>
            <div style="font-size:11px;font-weight:700;color:#8d8d8d;margin-bottom:0.75rem;">BLOOD GROUP DISTRIBUTION</div>
            <div style="display:flex;flex-wrap:wrap;gap:0.5rem;">
              ${Object.entries(data.blood_group_distribution || {}).sort((a,b)=>b[1]-a[1]).map(([bg, cnt]) => `
                <div style="background:rgba(255,255,255,0.05);border:1px solid #393939;border-radius:6px;padding:6px 12px;text-align:center;">
                  <div style="font-weight:700;color:${bloodColors[bg]||'#ccc'};font-size:14px;">${bg}</div>
                  <div style="font-size:10px;color:#8d8d8d;">${cnt}</div>
                </div>
              `).join('')}
            </div>
          </div>
        </div>
      `;
    } catch (err) {}
  });

  document.getElementById('btn-synth-export')?.addEventListener('click', () => {
    const count = document.getElementById('synth-count').value;
    const format = document.getElementById('synth-format').value;
    window.location.href = `/api/v1/ai/synthetic/generate?count=${count}&format=${format}`;
  });
}
