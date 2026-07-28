import { CameraModal } from '../components/CameraModal.js';

export function renderLoginView() {
  return `
    <div style="max-width: 480px; margin: 60px auto; background-color: var(--cds-layer-01); border: 1px solid var(--cds-border-subtle); padding: 2.5rem; box-shadow: 0 4px 20px rgba(0,0,0,0.5);">
      <div style="text-align: center; margin-bottom: 2rem;">
        <i class="fa-solid fa-heart-pulse" style="font-size: 3rem; color: var(--cds-interactive-01); margin-bottom: 1rem;"></i>
        <h2 style="font-weight: 600; font-size: 1.5rem; color: var(--cds-text-01);">Q-Transplant</h2>
        <p style="color: var(--cds-text-02); font-size: 13px; margin-top: 4px;">Enterprise Organ Coordination Platform</p>
      </div>

      <!-- Auth Toggle Tabs -->
      <div style="display: flex; margin-bottom: 1.5rem; border-bottom: 1px solid var(--cds-border-subtle);">
        <button id="tab-btn-login" class="bx--btn bx--btn--ghost" style="flex:1; border-bottom: 2px solid var(--cds-interactive-01);">Sign In</button>
        <button id="tab-btn-register" class="bx--btn bx--btn--ghost" style="flex:1; color: var(--cds-text-03);">Register Account</button>
      </div>

      <!-- Login Form -->
      <form id="form-login">
        <div style="margin-bottom: 1.25rem;">
          <label style="display: block; font-size: 12px; color: var(--cds-text-02); margin-bottom: 6px;">EMAIL ADDRESS</label>
          <input type="email" id="login-email" required value="admin@qtransplant.org" style="width: 100%; padding: 10px; background: var(--cds-layer-02); border: 1px solid var(--cds-border-subtle); color: var(--cds-text-01);" />
        </div>

        <div style="margin-bottom: 1rem;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
            <label style="font-size: 12px; color: var(--cds-text-02);">PASSWORD</label>
            <a href="#" id="link-forgot-pwd" style="font-size: 11px; color: var(--cds-interactive-01); text-decoration: none;">Forgot password?</a>
          </div>
          <input type="password" id="login-password" required value="AdminPass123!" style="width: 100%; padding: 10px; background: var(--cds-layer-02); border: 1px solid var(--cds-border-subtle); color: var(--cds-text-01);" />
        </div>

        <button type="submit" class="bx--btn bx--btn--primary" style="width: 100%; justify-content: center; margin-top: 1rem;">
          <span>SIGN IN TO PORTAL</span>
          <i class="fa-solid fa-arrow-right"></i>
        </button>
      </form>

      <!-- Register Form -->
      <form id="form-register" style="display: none;">
        <div style="margin-bottom: 1rem;">
          <label style="display: block; font-size: 12px; color: var(--cds-text-02); margin-bottom: 4px;">FULL NAME</label>
          <input type="text" id="reg-name" required placeholder="Dr. Jane Doe" style="width: 100%; padding: 8px; background: var(--cds-layer-02); border: 1px solid var(--cds-border-subtle); color: var(--cds-text-01);" />
        </div>

        <div style="margin-bottom: 1rem;">
          <label style="display: block; font-size: 12px; color: var(--cds-text-02); margin-bottom: 4px;">EMAIL ADDRESS</label>
          <input type="email" id="reg-email" required placeholder="jane@hospital.org" style="width: 100%; padding: 8px; background: var(--cds-layer-02); border: 1px solid var(--cds-border-subtle); color: var(--cds-text-01);" />
        </div>

        <div style="margin-bottom: 1rem;">
          <label style="display: block; font-size: 12px; color: var(--cds-text-02); margin-bottom: 4px;">ROLE</label>
          <select id="reg-role" style="width: 100%; padding: 8px; background: var(--cds-layer-02); border: 1px solid var(--cds-border-subtle); color: var(--cds-text-01);">
            <option value="doctor">Doctor / Surgeon</option>
            <option value="hospital">Hospital Authority</option>
            <option value="donor">Organ Donor</option>
            <option value="patient">Transplant Patient</option>
            <option value="organizer">Organizer (Admin)</option>
          </select>
        </div>

        <!-- Doctor Mandatory Camera Capture Section -->
        <div id="doctor-camera-section" style="margin-bottom: 1rem; padding: 10px; background: var(--cds-layer-02); border: 1px dashed var(--cds-border-strong);">
          <label style="display: block; font-size: 11px; color: var(--cds-text-02); margin-bottom: 6px;">MANDATORY LIVE CAMERA VERIFICATION</label>
          <div style="display: flex; align-items: center; gap: 10px;">
            <img id="avatar-preview-thumbnail" src="https://via.placeholder.com/60?text=Photo" style="width: 50px; height: 50px; object-fit: cover; border: 1px solid var(--cds-border-subtle);" />
            <button type="button" id="btn-start-camera" class="bx--btn bx--btn--secondary" style="padding: 6px 12px; font-size: 12px;">
              <i class="fa-solid fa-camera"></i> CAPTURE LIVE PHOTO
            </button>
          </div>
          <input type="hidden" id="reg-camera-base64" />
        </div>

        <div style="margin-bottom: 1.25rem;">
          <label style="display: block; font-size: 12px; color: var(--cds-text-02); margin-bottom: 4px;">PASSWORD</label>
          <input type="password" id="reg-password" required placeholder="••••••••" style="width: 100%; padding: 8px; background: var(--cds-layer-02); border: 1px solid var(--cds-border-subtle); color: var(--cds-text-01);" />
        </div>

        <button type="submit" class="bx--btn bx--btn--primary" style="width: 100%; justify-content: center;">
          <span>CREATE ACCOUNT</span>
          <i class="fa-solid fa-user-plus"></i>
        </button>
      </form>

      <div id="auth-error-msg" style="margin-top: 1rem; color: var(--cds-support-error); font-size: 12px; display: none;"></div>
    </div>

    ${CameraModal.render()}
  `;
}
