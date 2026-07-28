export class CameraModal {
  static stream = null;

  static render() {
    return `
      <div id="camera-modal" style="display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.85); z-index: 2000; align-items: center; justify-content: center;">
        <div style="background: var(--cds-layer-01); border: 1px solid var(--cds-border-strong); padding: 1.5rem; max-width: 500px; width: 90%; position: relative;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <h3 style="font-size: 1.1rem; font-weight: 600;"><i class="fa-solid fa-camera"></i> Live Verification Photo Capture</h3>
            <button id="btn-close-camera" class="bx--btn bx--btn--ghost" style="color: var(--cds-text-01);"><i class="fa-solid fa-xmark"></i></button>
          </div>

          <div style="position: relative; background: #000; height: 300px; display: flex; align-items: center; justify-content: center; overflow: hidden; border: 1px solid var(--cds-border-subtle);">
            <video id="camera-video" autoplay playsinline style="width: 100%; height: 100%; object-fit: cover;"></video>
            <canvas id="camera-canvas" style="display: none;"></canvas>
            <img id="camera-preview-img" style="display: none; width: 100%; height: 100%; object-fit: cover;" />
          </div>

          <div style="margin-top: 1rem; display: flex; gap: 12px; justify-content: flex-end;">
            <button id="btn-snap-photo" class="bx--btn bx--btn--primary" style="flex: 1; justify-content: center;">
              <i class="fa-solid fa-circle-dot"></i> CAPTURE SNAPSHOT
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
    const useBtn = document.getElementById('btn-use-photo');
    const closeBtn = document.getElementById('btn-close-camera');

    modal.style.display = 'flex';
    video.style.display = 'block';
    preview.style.display = 'none';
    snapBtn.style.display = 'flex';
    useBtn.style.display = 'none';

    try {
      this.stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 } });
      video.srcObject = this.stream;
    } catch (err) {
      alert('Camera permission denied or camera unhooked. Falling back to default avatar placeholder.');
      console.warn('WebRTC Camera Error:', err);
    }

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
      useBtn.style.display = 'flex';
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
