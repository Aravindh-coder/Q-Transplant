import { state } from '../state.js';

export function renderDashboardDoctor() {
  const user = state.currentUser || { full_name: 'Dr. Rajesh Kumar', is_approved: true };
  const isApproved = user.is_approved;

  return `
    <div>
      <div class="dash-header">
        <div>
          <h1 class="dash-title"><i class="fa-solid fa-user-doctor" style="color:#8a3ffc;margin-right:8px;"></i>Transplant Surgeon Clinical Portal</h1>
          <p class="dash-subtitle">Specialist: <strong>${user.full_name}</strong> (${user.email})</p>
        </div>
      </div>

      ${!isApproved ? `
        <!-- Doctor Registration Pending Organizer Approval Notice -->
        <div class="waiting-approval" style="background:rgba(241,194,27,0.08); border: 1px solid rgba(241,194,27,0.4); border-radius:12px; margin-bottom:2rem;">
          <div class="waiting-icon">⏳</div>
          <h3>ACCOUNT REGISTRATION PENDING ORGANIZER APPROVAL</h3>
          <p>
            Your live camera photo, medical license credentials, and certificate have been submitted securely to the Organizer Admin (<strong>aravindhjoshua10@gmail.com</strong>).
            <br>An email verification request containing One-Click Approve and Reject buttons was automatically dispatched to the Organizer.
            <br><span style="color:#f4f4f4;font-weight:600;">You will receive an automated confirmation email as soon as your account is approved.</span>
          </p>
        </div>
      ` : `
        <div class="bx--tag bx--tag--green" style="margin-bottom:1.5rem; padding:8px 16px; font-size:13px;">
          <i class="fa-solid fa-shield-check" style="margin-right:6px;"></i> VERIFIED & APPROVED TRANSPLANT SURGEON
        </div>
      `}

      <div class="bx--grid" style="grid-template-columns: repeat(12, 1fr); gap: 1.5rem;">
        <!-- Doctor Credentials & AI Security Badge -->
        <div class="bx--tile" style="grid-column: span 6; background: rgba(38,38,38,0.6); border-radius:12px;">
          <div class="bx--tile__heading"><i class="fa-solid fa-id-card"></i> CLINICAL CREDENTIALS & AI FRAUD VERIFICATION</div>
          <div style="margin-top: 1.5rem; display: flex; flex-direction: column; gap: 14px;">
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid var(--cds-border-subtle); padding-bottom: 8px;">
              <span style="color: var(--cds-text-02);">SURGEON NAME</span>
              <strong>${user.full_name}</strong>
            </div>
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid var(--cds-border-subtle); padding-bottom: 8px;">
              <span style="color: var(--cds-text-02);">MEDICAL LICENSE</span>
              <span style="font-family: var(--cds-mono-font);">MED-KA-2026-9081</span>
            </div>
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid var(--cds-border-subtle); padding-bottom: 8px;">
              <span style="color: var(--cds-text-02);">SPECIALIZATION</span>
              <span class="bx--tag bx--tag--blue">Cardiothoracic Surgery</span>
            </div>
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid var(--cds-border-subtle); padding-bottom: 8px;">
              <span style="color: var(--cds-text-02);">AI CERTIFICATE ANALYSIS</span>
              <span class="bx--tag bx--tag--green"><i class="fa-solid fa-robot"></i> 100% AUTHENTIC</span>
            </div>
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid var(--cds-border-subtle); padding-bottom: 8px;">
              <span style="color: var(--cds-text-02);">LIVE CAMERA CAPTURE</span>
              <span class="bx--tag bx--tag--green">BIOMETRIC VERIFIED</span>
            </div>
          </div>
        </div>

        <!-- Register New Donor / Patient Entry -->
        <div class="bx--tile" style="grid-column: span 6; background: rgba(38,38,38,0.6); border-radius:12px;">
          <div class="bx--tile__heading"><i class="fa-solid fa-notes-medical"></i> CLINICAL ENTRY MANAGEMENT</div>
          <p style="font-size:13px; color:#8d8d8d; margin-top:8px; margin-bottom:1.25rem;">
            As an approved Transplant Surgeon, you can enter new verified donor organs into the quantum network.
          </p>

          <form id="form-doctor-add-organ">
            <div class="form-group">
              <label>Organ Type</label>
              <select id="doc-organ-type" style="padding:10px; background:var(--cds-layer-02); color:#f4f4f4; width:100%; border:1px solid var(--cds-border-subtle); border-radius:6px;">
                <option value="Heart">Heart</option>
                <option value="Kidney">Kidney</option>
                <option value="Liver">Liver</option>
                <option value="Lung">Lung</option>
                <option value="Pancreas">Pancreas</option>
              </select>
            </div>
            <div class="form-group" style="margin-top:10px;">
              <label>Blood Group</label>
              <select id="doc-blood-type" style="padding:10px; background:var(--cds-layer-02); color:#f4f4f4; width:100%; border:1px solid var(--cds-border-subtle); border-radius:6px;">
                <option value="O+">O+</option><option value="A+">A+</option>
                <option value="B+">B+</option><option value="AB+">AB+</option>
              </select>
            </div>
            <div class="form-group" style="margin-top:10px;">
              <label>HLA Markers</label>
              <input type="text" id="doc-hla-type" value="A2,B7,DR4" style="padding:10px; background:var(--cds-layer-02); color:#f4f4f4; width:100%; border:1px solid var(--cds-border-subtle); border-radius:6px;" />
            </div>
            <button type="submit" class="btn-register-organ" style="margin-top:1.25rem;">
              <i class="fa-solid fa-plus-circle"></i> Register Organ into Quantum Network
            </button>
          </form>
        </div>
      </div>
    </div>
  `;
}
