export class CameraModal {
  static stream = null;

  static render() {
    return `
      <div id="camera-modal" style="display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.85); z-index: 2000; align-items: center; justify-content: center;">
        <div style="background: var(--cds-layer-01); border: 1px solid var(--cds-border-strong); padding: 1.5rem; max-width: 520px; width: 92%; position: relative; box-shadow: 0 8px 30px rgba(0,0,0,0.7);">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; border-bottom: 1px solid var(--cds-border-subtle); padding-bottom: 10px;">
            <h3 style="font-size: 1.1rem; font-weight: 600; color: var(--cds-text-01); font-family: var(--cds-sans-font);">
              <i class="fa-solid fa-camera" style="color: var(--cds-interactive-01); margin-right: 8px;"></i> Mandatory Doctor Verification Photo
            </h3>
            <button id="btn-close-camera" class="bx--btn bx--btn--ghost" style="color: var(--cds-text-01);"><i class="fa-solid fa-xmark"></i></button>
          </div>

          <div style="position: relative; background: #000; height: 320px; display: flex; align-items: center; justify-content: center; overflow: hidden; border: 1px solid var(--cds-border-subtle);">
            <video id="camera-video" autoplay playsinline style="width: 100%; height: 100%; object-fit: cover;"></video>
            <canvas id="camera-canvas" style="display: none;"></canvas>
            <img id="camera-preview-img" style="display: none; width: 100%; height: 100%; object-fit: cover;" />
            <div id="camera-loading-notice" style="position: absolute; color: #fff; font-size: 13px; display: none;">
              <i class="fa-solid fa-spinner fa-spin"></i> Initializing Camera Hardware...
            </div>
          </div>

          <div style="margin-top: 1rem; display: flex; gap: 10px; justify-content: flex-end;">
            <button id="btn-snap-photo" class="bx--btn bx--btn--primary" style="flex: 1; justify-content: center;">
              <i class="fa-solid fa-circle-dot"></i> CAPTURE SNAPSHOT
            </button>
            <button id="btn-retake-photo" class="bx--btn bx--btn--secondary" style="flex: 1; justify-content: center; display: none;">
              <i class="fa-solid fa-rotate-left"></i> RETAKE PHOTO
            </button>
            <button id="btn-use-photo" class="bx--btn bx--btn--primary" style="flex: 1; justify-content: center; display: none; background-color: var(--cds-support-success);">
              <i class="fa-solid fa-check"></i> USE THIS PHOTO
            </button>
          </div>
        </div>
      </div>
    `;
  }

  static async startCamera(onCapturedCallback) {
    const modal = document.getElementById('camera-modal');
    const video = document.getElementById('camera-video');
    const canvas = document.getElementById('camera-canvas');
    const preview = document.getElementById('camera-preview-img');
    const snapBtn = document.getElementById('btn-snap-photo');
    const retakeBtn = document.getElementById('btn-retake-photo');
    const useBtn = document.getElementById('btn-use-photo');
    const closeBtn = document.getElementById('btn-close-camera');
    const notice = document.getElementById('camera-loading-notice');

    modal.style.display = 'flex';
    video.style.display = 'block';
    preview.style.display = 'none';
    snapBtn.style.display = 'flex';
    retakeBtn.style.display = 'none';
    useBtn.style.display = 'none';
    if (notice) notice.style.display = 'block';

    const startStream = async () => {
      try {
        this.stopCamera();
        this.stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: 'user', width: { ideal: 640 }, height: { ideal: 480 } }
        });
        video.srcObject = this.stream;
        if (notice) notice.style.display = 'none';
      } catch (err) {
        console.warn('Primary getUserMedia constraints failed, attempting fallback:', err);
        try {
          this.stream = await navigator.mediaDevices.getUserMedia({ video: true });
          video.srcObject = this.stream;
          if (notice) notice.style.display = 'none';
        } catch (fallbackErr) {
          if (notice) notice.style.display = 'none';
          alert('Camera permission denied or camera unhooked. Falling back to default avatar.');
          console.error('WebRTC Camera Fatal Error:', fallbackErr);
        }
      }
    };

    await startStream();

    let capturedBase64 = '';

    snapBtn.onclick = () => {
      canvas.width = video.videoWidth || 640;
      canvas.height = video.videoHeight || 480;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      capturedBase64 = canvas.toDataURL('image/jpeg');

      preview.src = capturedBase64;
      preview.style.display = 'block';
      video.style.display = 'none';

      snapBtn.style.display = 'none';
      retakeBtn.style.display = 'flex';
      useBtn.style.display = 'flex';
    };

    retakeBtn.onclick = async () => {
      preview.style.display = 'none';
      video.style.display = 'block';
      snapBtn.style.display = 'flex';
      retakeBtn.style.display = 'none';
      useBtn.style.display = 'none';
      await startStream();
    };

    useBtn.onclick = () => {
      if (onCapturedCallback) onCapturedCallback(capturedBase64);
      this.stopCamera();
      modal.style.display = 'none';
    };

    closeBtn.onclick = () => {
      this.stopCamera();
      modal.style.display = 'none';
    };
  }

  static stopCamera() {
    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop());
      this.stream = null;
    }
  }
}
