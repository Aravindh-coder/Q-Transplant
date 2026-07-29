/**
 * AI Transplant Prediction Dashboard (Mission 1)
 * XGBoost + LightGBM + Random Forest Ensemble
 * SHAP Explainability • PDF Export • Prediction History
 */
export function renderAIPredictionView() {
  return `
    <div style="padding:0 1rem;">
      <div class="dash-title-row" style="margin-bottom:1.5rem;">
        <h1 class="dash-title">
          <i class="fa-solid fa-brain" style="color:#8a3ffc;margin-right:10px;"></i>
          AI Transplant Prediction Engine
        </h1>
        <div style="display:flex;gap:8px;align-items:center;">
          <span class="bx--tag" style="background:rgba(138,63,252,0.15);color:#be95ff;border:1px solid rgba(138,63,252,0.3);font-size:11px;">
            <i class="fa-solid fa-atom"></i> XGBoost + LightGBM + Random Forest Ensemble
          </span>
          <span class="bx--tag" style="background:rgba(0,176,255,0.15);color:#82cfff;border:1px solid rgba(0,176,255,0.3);font-size:11px;">
            <i class="fa-solid fa-chart-bar"></i> SHAP Explainability
          </span>
        </div>
      </div>

      <div style="display:grid;grid-template-columns:1fr 1fr;gap:1.5rem;">
        <!-- Input Form -->
        <div class="glass-card" style="padding:1.5rem;">
          <h3 style="color:#be95ff;margin-bottom:1.2rem;font-size:14px;font-weight:700;">
            <i class="fa-solid fa-sliders"></i> Patient & Organ Parameters
          </h3>
          <form id="form-ai-predict">
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.75rem;">
              <div class="form-group">
                <label>Organ Type</label>
                <select id="ai-organ-type">
                  <option value="Kidney">Kidney</option>
                  <option value="Heart">Heart</option>
                  <option value="Liver">Liver</option>
                  <option value="Lung">Lung</option>
                  <option value="Pancreas">Pancreas</option>
                  <option value="Cornea">Cornea</option>
                </select>
              </div>
              <div class="form-group">
                <label>Patient Age</label>
                <input type="number" id="ai-age" value="45" min="18" max="80" />
              </div>
              <div class="form-group">
                <label>Blood Type</label>
                <select id="ai-blood">
                  <option value="O+">O+</option><option value="O-">O-</option>
                  <option value="A+">A+</option><option value="A-">A-</option>
                  <option value="B+">B+</option><option value="B-">B-</option>
                  <option value="AB+">AB+</option><option value="AB-">AB-</option>
                </select>
              </div>
              <div class="form-group">
                <label>HLA Type</label>
                <input type="text" id="ai-hla" value="A2,B7,DR4" />
              </div>
              <div class="form-group">
                <label>Creatinine (mg/dL)</label>
                <input type="number" id="ai-creatinine" value="1.1" step="0.1" min="0.5" max="12" />
              </div>
              <div class="form-group">
                <label>Cold Ischemia (hrs)</label>
                <input type="number" id="ai-ischemia" value="4.0" step="0.5" min="0.5" max="12" />
              </div>
              <div class="form-group">
                <label>Distance (km)</label>
                <input type="number" id="ai-distance" value="15" min="1" max="500" />
              </div>
              <div class="form-group">
                <label>BMI</label>
                <input type="number" id="ai-bmi" value="24.5" step="0.5" min="15" max="45" />
              </div>
              <div class="form-group">
                <label>Comorbidities Count</label>
                <input type="number" id="ai-comorbidities" value="0" min="0" max="6" />
              </div>
              <div class="form-group">
                <label>ICU Available</label>
                <select id="ai-icu">
                  <option value="true">Yes — ICU Ready</option>
                  <option value="false">No — ICU Full</option>
                </select>
              </div>
            </div>
            <div style="display:flex;gap:0.75rem;margin-top:1rem;">
              <button type="submit" class="btn-submit-auth" style="background:linear-gradient(135deg,#8a3ffc,#6929c4);">
                <i class="fa-solid fa-brain"></i> Run AI Prediction
              </button>
              <button type="button" id="btn-download-pdf" class="btn-submit-auth"
                style="background:linear-gradient(135deg,#da1e28,#a21c24);display:none;">
                <i class="fa-solid fa-file-pdf"></i> Export PDF
              </button>
            </div>
          </form>
        </div>

        <!-- Results Panel -->
        <div id="ai-results-panel">
          <div class="glass-card" style="padding:1.5rem;text-align:center;color:#525252;">
            <i class="fa-solid fa-brain" style="font-size:3rem;color:#393939;margin-bottom:1rem;display:block;"></i>
            <p style="font-size:13px;">Enter patient parameters and click<br><strong style="color:#be95ff;">Run AI Prediction</strong> to get results.</p>
          </div>
        </div>
      </div>

      <!-- Prediction History -->
      <div class="glass-card" style="margin-top:1.5rem;padding:1.5rem;">
        <h3 style="color:#be95ff;margin-bottom:1rem;font-size:14px;font-weight:700;">
          <i class="fa-solid fa-history"></i> Prediction History
        </h3>
        <div id="ai-prediction-history">
          <div style="text-align:center;color:#525252;padding:1.5rem;font-size:13px;">Loading prediction history...</div>
        </div>
      </div>
    </div>
  `;
}

export function attachAIPredictionEvents() {
  const form = document.getElementById('form-ai-predict');
  const resultsPanel = document.getElementById('ai-results-panel');
  const downloadBtn = document.getElementById('btn-download-pdf');
  let lastPrediction = null;

  // Load prediction history
  fetch('/api/v1/ai/predictions/history')
    .then(r => r.json())
    .then(records => {
      const histEl = document.getElementById('ai-prediction-history');
      if (!histEl) return;
      if (!records.length) {
        histEl.innerHTML = '<div style="text-align:center;color:#525252;padding:1rem;font-size:12px;">No predictions stored yet. Run your first prediction above.</div>';
        return;
      }
      histEl.innerHTML = `
        <table class="utbl">
          <thead><tr><th>Organ</th><th>Age</th><th>Blood</th><th>1-Yr Survival</th><th>5-Yr Survival</th><th>Rejection Risk</th><th>Success %</th><th>Date</th></tr></thead>
          <tbody>
            ${records.map(r => `
              <tr>
                <td><strong>${r.organ_type}</strong></td>
                <td>${r.patient_age}</td>
                <td><span class="bx--tag bx--tag--red">${r.blood_type}</span></td>
                <td style="color:#42be65;font-weight:700;">${r.one_year_survival}%</td>
                <td style="color:#0f62fe;">${r.five_year_survival}%</td>
                <td style="color:#f1c21b;">${r.rejection_probability}%</td>
                <td>
                  <div style="display:flex;align-items:center;gap:8px;">
                    <div style="flex:1;height:6px;background:#393939;border-radius:3px;">
                      <div style="width:${r.overall_success}%;height:100%;background:linear-gradient(90deg,#42be65,#0f62fe);border-radius:3px;"></div>
                    </div>
                    <span style="font-weight:700;color:#f4f4f4;">${r.overall_success}%</span>
                  </div>
                </td>
                <td style="font-size:11px;color:#8d8d8d;">${new Date(r.created_at).toLocaleString()}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      `;
    }).catch(() => {});

  if (!form) return;

  form.onsubmit = async (e) => {
    e.preventDefault();
    if (resultsPanel) resultsPanel.innerHTML = `
      <div class="glass-card" style="padding:2rem;text-align:center;">
        <div style="width:40px;height:40px;border:3px solid #8a3ffc;border-top-color:transparent;border-radius:50%;animation:spin 0.8s linear infinite;margin:0 auto 1rem;"></div>
        <p style="color:#be95ff;font-size:13px;">Running XGBoost + LightGBM + Random Forest Ensemble...</p>
      </div>
    `;

    const payload = {
      organ_type: document.getElementById('ai-organ-type').value,
      age: parseFloat(document.getElementById('ai-age').value),
      blood_type: document.getElementById('ai-blood').value,
      hla_type: document.getElementById('ai-hla').value,
      creatinine: parseFloat(document.getElementById('ai-creatinine').value),
      cold_ischemia_hours: parseFloat(document.getElementById('ai-ischemia').value),
      distance_km: parseFloat(document.getElementById('ai-distance').value),
      icu_available: document.getElementById('ai-icu').value === 'true',
      bmi: parseFloat(document.getElementById('ai-bmi').value),
      comorbidities_count: parseInt(document.getElementById('ai-comorbidities').value)
    };

    try {
      const res = await fetch('/api/v1/ai/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      lastPrediction = data;

      const successColor = data.overall_success > 75 ? '#42be65' : data.overall_success > 55 ? '#f1c21b' : '#da1e28';
      const successLabel = data.overall_success > 75 ? 'HIGH VIABILITY' : data.overall_success > 55 ? 'MODERATE RISK' : 'HIGH RISK';

      if (resultsPanel) resultsPanel.innerHTML = `
        <div class="glass-card" style="padding:1.5rem;">
          <div style="text-align:center;margin-bottom:1.5rem;">
            <div style="width:110px;height:110px;border-radius:50%;background:conic-gradient(${successColor} ${data.overall_success * 3.6}deg, #262626 0);display:inline-flex;align-items:center;justify-content:center;margin-bottom:0.5rem;">
              <div style="width:82px;height:82px;border-radius:50%;background:#161616;display:flex;align-items:center;justify-content:center;flex-direction:column;">
                <span style="font-size:20px;font-weight:900;color:${successColor};">${data.overall_success}%</span>
                <span style="font-size:8px;color:#8d8d8d;">SUCCESS</span>
              </div>
            </div>
            <div style="font-size:11px;font-weight:700;color:${successColor};letter-spacing:1px;">${successLabel}</div>
          </div>

          <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.75rem;margin-bottom:1rem;">
            ${[
              ['1-Year Graft Survival', data.one_year_survival + '%', '#42be65'],
              ['5-Year Graft Survival', data.five_year_survival + '%', '#0f62fe'],
              ['Rejection Risk', data.rejection_probability + '%', '#f1c21b'],
              ['Mortality Risk', data.mortality_risk + '%', '#da1e28'],
              ['Confidence', data.confidence_score + '%', '#be95ff'],
              ['Ensemble Models', '3 Models', '#8d8d8d']
            ].map(([label, val, color]) => `
              <div style="background:#262626;border:1px solid #393939;border-radius:8px;padding:0.75rem;text-align:center;">
                <div style="font-size:18px;font-weight:800;color:${color};">${val}</div>
                <div style="font-size:10px;color:#8d8d8d;margin-top:2px;">${label}</div>
              </div>
            `).join('')}
          </div>

          <div style="background:#0a0a14;border:1px solid rgba(138,63,252,0.3);border-radius:8px;padding:1rem;margin-bottom:1rem;">
            <div style="font-size:11px;font-weight:700;color:#be95ff;margin-bottom:0.75rem;">
              <i class="fa-solid fa-chart-bar"></i> SHAP Feature Importance
            </div>
            ${(data.shap_explanation || []).map(f => `
              <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
                <span style="font-size:11px;color:#c6c6c6;width:160px;flex-shrink:0;">${f.feature}</span>
                <div style="flex:1;height:5px;background:#393939;border-radius:3px;">
                  <div style="width:${Math.min(100, Math.abs(f.impact) * 5)}%;height:100%;background:${f.impact < 0 ? '#da1e28' : '#42be65'};border-radius:3px;"></div>
                </div>
                <span style="font-size:10px;color:${f.impact < 0 ? '#fa4d56' : '#42be65'};width:45px;text-align:right;">
                  ${f.impact > 0 ? '+' : ''}${f.impact}
                </span>
                <span style="font-size:10px;color:#525252;">${f.unit}</span>
              </div>
            `).join('')}
          </div>

          <div style="background:#0a1a0a;border:1px solid rgba(66,190,101,0.3);border-radius:8px;padding:0.75rem;margin-bottom:1rem;">
            <div style="font-size:10px;font-weight:700;color:#42be65;margin-bottom:0.5rem;">MODEL COMPARISON</div>
            <div style="display:flex;gap:8px;flex-wrap:wrap;">
              ${Object.entries(data.model_comparison || {}).map(([model, score]) => `
                <span style="background:#161616;border:1px solid #393939;border-radius:4px;padding:3px 8px;font-size:11px;">
                  <span style="color:#8d8d8d;">${model}:</span> <span style="color:#f4f4f4;font-weight:700;">${score}%</span>
                </span>
              `).join('')}
            </div>
          </div>

          <p style="font-size:11px;color:#8d8d8d;border-top:1px solid #393939;padding-top:0.75rem;">
            ${data.explanation_summary}
          </p>
        </div>
      `;

      if (downloadBtn) downloadBtn.style.display = 'block';
    } catch (err) {
      if (resultsPanel) resultsPanel.innerHTML = `
        <div class="glass-card" style="padding:1.5rem;border-color:rgba(218,30,40,0.3);">
          <p style="color:#da1e28;font-size:13px;"><i class="fa-solid fa-triangle-exclamation"></i> Prediction failed: ${err.message}</p>
        </div>
      `;
    }
  };

  if (downloadBtn) {
    downloadBtn.onclick = async () => {
      if (!lastPrediction) return;
      const payload = lastPrediction.inputs || {};
      const res = await fetch('/api/v1/ai/predict/pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url; a.download = 'qtransplant_ai_report.pdf'; a.click();
    };
  }
}
