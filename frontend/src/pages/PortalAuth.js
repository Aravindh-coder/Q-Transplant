/**
 * Portal Selector — rendered between landing page and auth forms.
 * Shows Doctor / Hospital / Donor / Organizer portal cards.
 */
import { CameraModal } from '../components/CameraModal.js';

export function renderPortalSelector() {
  return `
    <div class="portal-page" id="portal-selector-page">
      <div class="portal-wrapper">
        <div class="portal-header">
          <div class="portal-logo"><i class="fa-solid fa-heart-pulse"></i></div>
          <h1 class="portal-title">Q-Transplant Portal</h1>
          <p class="portal-subtitle">Select your access portal to continue</p>
        </div>

        <div class="portal-grid">
          <div class="portal-card organizer" id="portal-card-organizer" data-portal="organizer" style="cursor:pointer;">
            <div class="portal-card-icon"><i class="fa-solid fa-shield-halved"></i></div>
            <div>
              <h3>Organizer Dashboard</h3>
              <p>Full system access — manage doctors, hospitals, donors, patients, approvals, and audit logs.</p>
            </div>
            <div class="portal-card-arrow"><i class="fa-solid fa-arrow-right"></i></div>
          </div>

          <div class="portal-card doctor" id="portal-card-doctor" data-portal="doctor" style="cursor:pointer;">
            <div class="portal-card-icon"><i class="fa-solid fa-user-doctor"></i></div>
            <div>
              <h3>Doctor Portal</h3>
              <p>Register with live camera + medical certificate. Manage donor registrations and patient matching.</p>
            </div>
            <div class="portal-card-arrow"><i class="fa-solid fa-arrow-right"></i></div>
          </div>

          <div class="portal-card hospital" id="portal-card-hospital" data-portal="hospital" style="cursor:pointer;">
            <div class="portal-card-icon"><i class="fa-solid fa-hospital"></i></div>
            <div>
              <h3>Hospital Portal</h3>
              <p>Emergency organ request system, Grover's match results, ICU status, and inter-hospital coordination.</p>
            </div>
            <div class="portal-card-arrow"><i class="fa-solid fa-arrow-right"></i></div>
          </div>

          <div class="portal-card donor" id="portal-card-donor" data-portal="donor" style="cursor:pointer;">
            <div class="portal-card-icon"><i class="fa-solid fa-hand-holding-heart"></i></div>
            <div>
              <h3>Donor Portal</h3>
              <p>Register your organ pledge, view verification status, and track your potential life-saving contribution.</p>
            </div>
            <div class="portal-card-arrow"><i class="fa-solid fa-arrow-right"></i></div>
          </div>
        </div>

        <div style="text-align:center;">
          <button id="btn-back-to-landing" style="background:none;border:none;color:#8d8d8d;font-size:13px;cursor:pointer;transition:color 0.2s;" onmouseover="this.style.color='#f4f4f4'" onmouseout="this.style.color='#8d8d8d'">
            <i class="fa-solid fa-arrow-left"></i> Back to Home
          </button>
        </div>
      </div>
    </div>
  `;
}


export function renderAuthForm(portal) {
  const config = {
    organizer: {
      color: '#0f62fe', bg: 'rgba(15,98,254,0.1)', border: 'rgba(15,98,254,0.3)',
      icon: 'fa-shield-halved', label: 'Organizer — Executive Admin', title: 'Organizer Sign In',
      subtitle: 'Manage all system users, approvals, and operational data.',
      showRegister: false
    },
    doctor: {
      color: '#8a3ffc', bg: 'rgba(138,63,252,0.1)', border: 'rgba(138,63,252,0.3)',
      icon: 'fa-user-doctor', label: 'Doctor Portal', title: 'Doctor Access',
      subtitle: 'Sign in or register as a verified transplant specialist.',
      showRegister: true
    },
    hospital: {
      color: '#da1e28', bg: 'rgba(218,30,40,0.1)', border: 'rgba(218,30,40,0.3)',
      icon: 'fa-hospital', label: 'Hospital Authority', title: 'Hospital Portal',
      subtitle: 'Sign in or register your hospital to access the emergency coordination system.',
      showRegister: true
    },
    donor: {
      color: '#198038', bg: 'rgba(25,128,56,0.1)', border: 'rgba(25,128,56,0.3)',
      icon: 'fa-hand-holding-heart', label: 'Organ Donor', title: 'Donor Portal',
      subtitle: 'Sign in or register your organ donation pledge.',
      showRegister: true
    }
  };

  const c = config[portal] || config.organizer;

  return `
    <div class="auth-form-page">
      <div class="auth-form-card">
        <button class="back-link" id="btn-back-to-portals">
          <i class="fa-solid fa-arrow-left"></i> All Portals
        </button>

        <div class="auth-portal-badge" style="background:${c.bg};border:1px solid ${c.border};color:${c.color};">
          <i class="fa-solid ${c.icon}"></i>
          ${c.label}
        </div>

        <h2 class="auth-form-title">${c.title}</h2>
        <p class="auth-form-subtitle">${c.subtitle}</p>

        ${c.showRegister ? `
          <div class="form-tabs">
            <button class="form-tab active" id="tab-login">Sign In</button>
            <button class="form-tab" id="tab-register">Register</button>
          </div>
        ` : ''}

        <div id="auth-error-box" class="auth-error-box"></div>
        <div id="auth-success-box" class="auth-success-box"></div>

        <!-- Login Form -->
        <form id="form-portal-login">
          <div class="form-group">
            <label>Email Address</label>
            <input type="email" id="portal-login-email" required placeholder="your@hospital.org"
              value="${portal === 'organizer' ? 'aravindhjoshua10@gmail.com' : ''}" />
          </div>
          <div class="form-group">
            <label>
              Password
              <button type="button" id="link-forgot-pwd" style="float:right;background:none;border:none;font-size:11px;color:${c.color};cursor:pointer;text-transform:none;letter-spacing:0;font-weight:400;">
                Forgot password?
              </button>
            </label>
            <input type="password" id="portal-login-password" required placeholder="••••••••"
              value="${portal === 'organizer' ? 'AdminPass123!' : ''}" />
          </div>
          <button type="submit" class="btn-submit-auth" id="btn-portal-login-submit"
            style="background:linear-gradient(135deg,${c.color},${c.color}cc);">
            <i class="fa-solid fa-right-to-bracket"></i>
            Sign In to ${c.label}
          </button>
        </form>

        ${c.showRegister ? `
          <!-- Register Form -->
          <form id="form-portal-register" style="display:none;">
            <div class="form-group">
              <label>Full Name</label>
              <input type="text" id="portal-reg-name" required
                placeholder="${portal === 'doctor' ? 'Dr. Jane Doe' : portal === 'hospital' ? 'Apollo Specialty Hospital' : 'Your Full Name'}" />
            </div>
            <div class="form-group">
              <label>Email Address</label>
              <input type="email" id="portal-reg-email" required placeholder="email@example.com" />
            </div>
            <div class="form-group">
              <label>Phone Number</label>
              <input type="tel" id="portal-reg-phone" required placeholder="080-555-0100" />
            </div>

            ${portal === 'doctor' ? renderDoctorRegFields() : ''}
            ${portal === 'hospital' ? renderHospitalRegFields() : ''}
            ${portal === 'donor' ? renderDonorRegFields() : ''}

            <div class="form-group">
              <label>Password</label>
              <input type="password" id="portal-reg-password" required placeholder="Min. 8 characters" />
            </div>

            <button type="submit" class="btn-submit-auth"
              style="background:linear-gradient(135deg,${c.color},${c.color}cc);">
              <i class="fa-solid fa-user-plus"></i>
              Create Account & Request Approval
            </button>
          </form>
        ` : ''}

        <!-- Forgot Password Modal -->
        <div id="forgot-pwd-modal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,0.85);z-index:3000;align-items:center;justify-content:center;">
          <div style="background:#262626;border:1px solid #393939;border-radius:12px;padding:2rem;max-width:420px;width:90%;margin:0 auto;">
            <h3 style="color:#f4f4f4;margin-bottom:1rem;"><i class="fa-solid fa-key" style="color:${c.color};margin-right:8px;"></i>Reset Password</h3>
            <p style="font-size:13px;color:#8d8d8d;margin-bottom:1.5rem;">Enter your registered email to receive a 15-minute secure reset link.</p>
            <form id="form-forgot-password">
              <div class="form-group">
                <label>Email Address</label>
                <input type="email" id="forgot-email" required placeholder="your@email.com" />
              </div>
              <div style="display:flex;gap:1rem;">
                <button type="submit" class="btn-submit-auth" style="background:${c.color};">Send Reset Link</button>
                <button type="button" id="btn-close-forgot-modal" style="flex:1;padding:12px;background:transparent;border:1px solid #393939;border-radius:8px;color:#8d8d8d;cursor:pointer;">Cancel</button>
              </div>
            </form>
          </div>
        </div>

        <!-- Reset Password Modal -->
        <div id="reset-pwd-modal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,0.85);z-index:3100;align-items:center;justify-content:center;">
          <div style="background:#262626;border:1px solid #393939;border-radius:12px;padding:2rem;max-width:420px;width:90%;margin:0 auto;">
            <h3 style="color:#f4f4f4;margin-bottom:1rem;"><i class="fa-solid fa-lock" style="color:#42be65;margin-right:8px;"></i>Set New Password</h3>
            <form id="form-reset-password">
              <input type="hidden" id="reset-token-input" />
              <div class="form-group">
                <label>New Password</label>
                <input type="password" id="reset-new-password" required placeholder="••••••••" />
              </div>
              <button type="submit" class="btn-submit-auth" style="background:#198038;">
                <i class="fa-solid fa-check"></i> Update Password
              </button>
            </form>
          </div>
        </div>

        ${CameraModal.render()}
      </div>
    </div>
  `;
}

function renderDoctorRegFields() {
  return `
    <div class="form-group">
      <label>Medical License Number</label>
      <input type="text" id="portal-reg-license" required placeholder="MED-KA-2026-XXXX" />
    </div>
    <div class="form-group">
      <label>Specialization</label>
      <select id="portal-reg-spec">
        <option value="Cardiothoracic Surgery">Cardiothoracic Surgery</option>
        <option value="Transplant Surgery">Transplant Surgery</option>
        <option value="Nephrology">Nephrology</option>
        <option value="Hepatology">Hepatology</option>
        <option value="Pulmonology">Pulmonology</option>
        <option value="General Surgery">General Surgery</option>
      </select>
    </div>
    <div class="form-group">
      <label>Department</label>
      <input type="text" id="portal-reg-dept" required placeholder="Organ Transplantation Unit" />
    </div>

    <!-- Donor Data File Upload -->
    <div class="form-group">
      <label>Donor Data File <span style="color:#0f62fe;font-size:10px;font-weight:600;">(OPTIONAL / BATCH)</span></label>
      <div class="cert-upload-zone" id="donor-upload-zone" onclick="document.getElementById('donor-data-file-input').click()">
        <div class="icon"><i class="fa-solid fa-hand-holding-medical" style="color:#0f62fe;"></i></div>
        <h4 style="font-size:13px;">Upload Donor Dataset</h4>
        <p>CSV, JSON, XLSX — Max 10MB</p>
      </div>
      <input type="file" id="donor-data-file-input" accept=".csv,.json,.xlsx,.xls" style="display:none;" />
      <div id="donor-data-file-name" style="font-size:11px;color:#8d8d8d;margin-top:4px;"></div>
    </div>

    <!-- Recipient Data File Upload -->
    <div class="form-group">
      <label>Recipient / Patient Data File <span style="color:#8a3ffc;font-size:10px;font-weight:600;">(OPTIONAL / BATCH)</span></label>
      <div class="cert-upload-zone" id="recipient-upload-zone" onclick="document.getElementById('recipient-data-file-input').click()">
        <div class="icon"><i class="fa-solid fa-user-injured" style="color:#8a3ffc;"></i></div>
        <h4 style="font-size:13px;">Upload Recipient Dataset</h4>
        <p>CSV, JSON, XLSX — Max 10MB</p>
      </div>
      <input type="file" id="recipient-data-file-input" accept=".csv,.json,.xlsx,.xls" style="display:none;" />
      <div id="recipient-data-file-name" style="font-size:11px;color:#8d8d8d;margin-top:4px;"></div>
    </div>

    <!-- Medical Certificate Upload + AI Verification -->
    <div class="form-group">
      <label>Medical Certificate <span style="color:#8a3ffc;font-size:10px;font-weight:600;">(AI VERIFIED)</span></label>
      <div class="cert-upload-zone" id="cert-upload-zone" onclick="document.getElementById('cert-file-input').click()">
        <div class="icon"><i class="fa-solid fa-file-medical"></i></div>
        <h4>Upload Medical Certificate</h4>
        <p>PDF, JPG, PNG — Max 5MB</p>
        <div class="ai-verify-badge"><i class="fa-solid fa-robot"></i> AI Fraud Detection Active</div>
      </div>
      <input type="file" id="cert-file-input" accept=".pdf,.jpg,.jpeg,.png" style="display:none;" />
      <div id="cert-file-name" style="font-size:11px;color:#8d8d8d;margin-top:6px;"></div>
    </div>

    <!-- Live Camera Capture -->
    <div class="form-group">
      <label>Live Camera Photo <span style="color:#da1e28;font-size:10px;font-weight:600;">(MANDATORY)</span></label>
      <div class="camera-capture-zone">
        <img id="camera-preview-img" class="camera-preview"
          src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 60 60'%3E%3Ccircle cx='30' cy='30' r='30' fill='%23393939'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' font-size='24' fill='%238d8d8d'%3E👤%3C/text%3E%3C/svg%3E"
          alt="Camera Preview" />
        <button type="button" id="btn-start-camera" class="btn-capture">
          <i class="fa-solid fa-camera"></i> Capture Live Photo
        </button>
        <p style="font-size:11px;color:#8d8d8d;margin-top:8px;">No uploaded photos — live capture only</p>
      </div>
      <input type="hidden" id="reg-camera-base64" />
    </div>
  `;
}

function renderHospitalRegFields() {
  return `
    <div class="form-group">
      <label>Hospital License Number</label>
      <input type="text" id="portal-reg-license" required placeholder="LIC-KA-2026-XXXX" />
    </div>
    <div class="form-group">
      <label>City</label>
      <input type="text" id="portal-reg-city" required placeholder="Bengaluru" />
    </div>
    <div class="form-group">
      <label>State</label>
      <input type="text" id="portal-reg-state" required placeholder="Karnataka" />
    </div>
    <div class="form-group">
      <label>Full Address</label>
      <input type="text" id="portal-reg-address" required placeholder="123 Medical Avenue" />
    </div>
  `;
}

function renderDonorRegFields() {
  return `
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">
      <div class="form-group">
        <label>Blood Type</label>
        <select id="portal-reg-blood">
          <option value="A+">A+</option><option value="A-">A-</option>
          <option value="B+">B+</option><option value="B-">B-</option>
          <option value="AB+">AB+</option><option value="AB-">AB-</option>
          <option value="O+">O+</option><option value="O-">O-</option>
        </select>
      </div>
      <div class="form-group">
        <label>Age</label>
        <input type="number" id="portal-reg-age" min="18" max="70" placeholder="30" />
      </div>
    </div>
    <div class="form-group">
      <label>HLA Type</label>
      <input type="text" id="portal-reg-hla" placeholder="A2,B7,DR4" />
    </div>
    <div class="form-group">
      <label>Gender</label>
      <select id="portal-reg-gender">
        <option value="Male">Male</option>
        <option value="Female">Female</option>
        <option value="Other">Other</option>
      </select>
    </div>
  `;
}
