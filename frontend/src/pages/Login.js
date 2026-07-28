import { CameraModal } from '../components/CameraModal.js';

export function renderLoginView() {
  return `
    <div style="max-width: 480px; margin: 50px auto; background-color: var(--cds-layer-01); border: 1px solid var(--cds-border-subtle); padding: 2.5rem; box-shadow: 0 8px 30px rgba(0,0,0,0.6);">
      <div style="text-align: center; margin-bottom: 2rem;">
        <i class="fa-solid fa-heart-pulse" style="font-size: 3rem; color: var(--cds-interactive-01); margin-bottom: 1rem;"></i>
        <h2 style="font-weight: 600; font-size: 1.5rem; color: var(--cds-text-01); font-family: var(--cds-sans-font);">Q-Transplant</h2>
        <p style="color: var(--cds-text-02); font-size: 13px; margin-top: 4px;">Enterprise Organ Transplant Coordination Network</p>
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
            <button type="button" id="link-forgot-pwd" style="background: none; border: none; font-size: 11px; color: var(--cds-interactive-01); cursor: pointer; padding: 0;">Forgot password?</button>
          </div>
          <input type="password" id="login-password" required value="AdminPass123!" style="width: 100%; padding: 10px; background: var(--cds-layer-02); border: 1px solid var(--cds-border-subtle); color: var(--cds-text-01);" />
        </div>

        <button type="submit" id="btn-submit-login" class="bx--btn bx--btn--primary" style="width: 100%; justify-content: center; margin-top: 1rem;">
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
          <label style="display: block; font-size: 12px; color: var(--cds-text-02); margin-bottom: 4px;">ACCOUNT ROLE</label>
          <select id="reg-role" style="width: 100%; padding: 8px; background: var(--cds-layer-02); border: 1px solid var(--cds-border-subtle); color: var(--cds-text-01);">
            <option value="doctor">Doctor / Transplant Surgeon</option>
            <option value="hospital">Hospital Authority</option>
            <option value="donor">Organ Donor</option>
            <option value="patient">Transplant Patient</option>
            <option value="organizer">Organizer (Executive Admin)</option>
          </select>
        </div>

        <!-- Doctor Mandatory Camera Capture Section -->
        <div id="doctor-camera-section" style="margin-bottom: 1rem; padding: 12px; background: var(--cds-layer-02); border: 1px dashed var(--cds-border-strong);">
          <label style="display: block; font-size: 11px; color: var(--cds-interactive-01); font-weight: bold; margin-bottom: 6px;">
            <i class="fa-solid fa-camera"></i> MANDATORY LIVE CAMERA VERIFICATION
          </label>
          <div style="display: flex; align-items: center; gap: 12px;">
            <img id="avatar-preview-thumbnail" src="https://via.placeholder.com/60?text=Photo" style="width: 50px; height: 50px; object-fit: cover; border: 1px solid var(--cds-border-subtle);" />
            <button type="button" id="btn-start-camera" class="bx--btn bx--btn--secondary" style="padding: 6px 12px; font-size: 12px;">
              <i class="fa-solid fa-camera"></i> CAPTURE LIVE SNAPSHOT
            </button>
          </div>
          <input type="hidden" id="reg-camera-base64" />
        </div>

        <div style="margin-bottom: 1.25rem;">
          <label style="display: block; font-size: 12px; color: var(--cds-text-02); margin-bottom: 4px;">PASSWORD</label>
          <input type="password" id="reg-password" required placeholder="••••••••" style="width: 100%; padding: 8px; background: var(--cds-layer-02); border: 1px solid var(--cds-border-subtle); color: var(--cds-text-01);" />
        </div>

        <button type="submit" class="bx--btn bx--btn--primary" style="width: 100%; justify-content: center;">
          <span>CREATE ACCOUNT & REQUEST APPROVAL</span>
          <i class="fa-solid fa-user-plus"></i>
        </button>
      </form>

      <div id="auth-error-msg" style="margin-top: 1rem; color: var(--cds-support-error); font-size: 12px; display: none;"></div>
    </div>

    <!-- Forgot Password Modal -->
    <div id="forgot-pwd-modal" style="display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.85); z-index: 2500; align-items: center; justify-content: center;">
      <div style="background: var(--cds-layer-01); border: 1px solid var(--cds-border-strong); padding: 2rem; max-width: 440px; width: 90%;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
          <h3 style="font-size: 1.1rem; font-weight: 600;"><i class="fa-solid fa-key"></i> Request Password Reset</h3>
          <button type="button" id="btn-close-forgot-modal" class="bx--btn bx--btn--ghost"><i class="fa-solid fa-xmark"></i></button>
        </div>
        <p style="font-size: 13px; color: var(--cds-text-02); margin-bottom: 1rem;">Enter your registered account email address to receive a 15-minute secure reset token link.</p>
        <form id="form-forgot-password">
          <div style="margin-bottom: 1rem;">
            <label style="display: block; font-size: 12px; color: var(--cds-text-02); margin-bottom: 4px;">EMAIL ADDRESS</label>
            <input type="email" id="forgot-email" required placeholder="user@qtransplant.org" style="width: 100%; padding: 10px; background: var(--cds-layer-02); border: 1px solid var(--cds-border-subtle); color: var(--cds-text-01);" />
          </div>
          <button type="submit" class="bx--btn bx--btn--primary" style="width: 100%; justify-content: center;">
            <span>DISPATCH RESET EMAIL</span>
            <i class="fa-solid fa-paper-plane"></i>
          </button>
        </form>
      </div>
    </div>

    <!-- Reset Password Token Modal -->
    <div id="reset-pwd-modal" style="display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.85); z-index: 2600; align-items: center; justify-content: center;">
      <div style="background: var(--cds-layer-01); border: 1px solid var(--cds-border-strong); padding: 2rem; max-width: 440px; width: 90%;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
          <h3 style="font-size: 1.1rem; font-weight: 600;"><i class="fa-solid fa-shield-halved"></i> Set New Password</h3>
          <button type="button" id="btn-close-reset-modal" class="bx--btn bx--btn--ghost"><i class="fa-solid fa-xmark"></i></button>
        </div>
        <form id="form-reset-password">
          <input type="hidden" id="reset-token-input" />
          <div style="margin-bottom: 1rem;">
            <label style="display: block; font-size: 12px; color: var(--cds-text-02); margin-bottom: 4px;">NEW PASSWORD</label>
            <input type="password" id="reset-new-password" required placeholder="••••••••" style="width: 100%; padding: 10px; background: var(--cds-layer-02); border: 1px solid var(--cds-border-subtle); color: var(--cds-text-01);" />
          </div>
          <button type="submit" class="bx--btn bx--btn--primary" style="width: 100%; justify-content: center;">
            <span>UPDATE PASSWORD</span>
            <i class="fa-solid fa-check"></i>
          </button>
        </form>
      </div>
    </div>

    ${CameraModal.render()}
  `;
}
