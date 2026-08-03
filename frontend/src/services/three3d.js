/**
 * ═══════════════════════════════════════════════════════════════════
 * Q-TRANSPLANT — THREE.JS 3D MOTION ENGINE & TILT CONTROLLER
 * Dynamic 3D Quantum Particle Wavefield + 3D Tilt Card Effects
 * ═══════════════════════════════════════════════════════════════════
 */

let bgScene, bgCamera, bgRenderer, bgParticles, particlePositions;
let mouseX = 0, mouseY = 0;
let is3DInitialized = false;

/**
 * Initialize global 3D quantum motion particle canvas
 */
export function init3DBackground() {
  const canvas = document.getElementById('q-3d-background-canvas');
  if (!canvas || is3DInitialized || typeof THREE === 'undefined') return;

  try {
    bgScene = new THREE.Scene();
    bgCamera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 1, 2000);
    bgCamera.position.z = 1000;

    bgRenderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
    bgRenderer.setSize(window.innerWidth, window.innerHeight);
    bgRenderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    // Particle Field (1200 Glowing Quantum Nodes)
    const particleCount = 1200;
    const geometry = new THREE.BufferGeometry();
    particlePositions = new Float32Array(particleCount * 3);
    const particleColors = new Float32Array(particleCount * 3);

    const colors = [
      new THREE.Color(0x0f62fe), // IBM Blue
      new THREE.Color(0x8a3ffc), // Purple
      new THREE.Color(0x42be65), // Green
      new THREE.Color(0xda1e28)  // Red
    ];

    for (let i = 0; i < particleCount; i++) {
      const x = (Math.random() - 0.5) * 2000;
      const y = (Math.random() - 0.5) * 2000;
      const z = (Math.random() - 0.5) * 2000;

      particlePositions[i * 3]     = x;
      particlePositions[i * 3 + 1] = y;
      particlePositions[i * 3 + 2] = z;

      const color = colors[Math.floor(Math.random() * colors.length)];
      particleColors[i * 3]     = color.r;
      particleColors[i * 3 + 1] = color.g;
      particleColors[i * 3 + 2] = color.b;
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(particlePositions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(particleColors, 3));

    // Custom Particle Material with Bloom Glow
    const particleMaterial = new THREE.PointsMaterial({
      size: 4.5,
      vertexColors: true,
      transparent: true,
      opacity: 0.8,
      blending: THREE.AdditiveBlending
    });

    bgParticles = new THREE.Points(geometry, particleMaterial);
    bgScene.add(bgParticles);

    // Add glowing Quantum Wireframe Ring
    const ringGeo = new THREE.TorusGeometry(320, 1.2, 16, 100);
    const ringMat = new THREE.MeshBasicMaterial({ color: 0x8a3ffc, wireframe: true, transparent: true, opacity: 0.35 });
    const quantumRing = new THREE.Mesh(ringGeo, ringMat);
    quantumRing.rotation.x = Math.PI / 3;
    bgScene.add(quantumRing);

    const ringGeo2 = new THREE.TorusGeometry(450, 1.5, 16, 100);
    const ringMat2 = new THREE.MeshBasicMaterial({ color: 0x0f62fe, wireframe: true, transparent: true, opacity: 0.25 });
    const quantumRing2 = new THREE.Mesh(ringGeo2, ringMat2);
    quantumRing2.rotation.y = Math.PI / 4;
    bgScene.add(quantumRing2);

    // Mouse Listeners
    window.addEventListener('mousemove', (e) => {
      mouseX = (e.clientX - window.innerWidth / 2) * 0.4;
      mouseY = (e.clientY - window.innerHeight / 2) * 0.4;
    });

    window.addEventListener('resize', () => {
      bgCamera.aspect = window.innerWidth / window.innerHeight;
      bgCamera.updateProjectionMatrix();
      bgRenderer.setSize(window.innerWidth, window.innerHeight);
    });

    // Animation Loop
    function animate() {
      requestAnimationFrame(animate);

      // Smooth Camera Inertia
      bgCamera.position.x += (mouseX - bgCamera.position.x) * 0.03;
      bgCamera.position.y += (-mouseY - bgCamera.position.y) * 0.03;
      bgCamera.lookAt(bgScene.position);

      // Rotation & Wave Motion
      bgParticles.rotation.y += 0.0008;
      bgParticles.rotation.x += 0.0004;

      quantumRing.rotation.z += 0.002;
      quantumRing2.rotation.z -= 0.0015;

      bgRenderer.render(bgScene, bgCamera);
    }

    animate();
    is3DInitialized = true;
  } catch (err) {
    console.warn('3D Background Init Failed:', err);
  }
}

/**
 * Attach 3D Motion Depth Mouse-Tilt effect to card elements across every page
 */
export function attach3DTiltEffects() {
  const cards = document.querySelectorAll('.problem-card, .portal-card, .kpi-card, .hardware-card, .q-step, .team-card, .match-result-card, .ultra-table-wrap');

  cards.forEach(card => {
    if (card.dataset.hasTilt) return;
    card.dataset.hasTilt = 'true';

    card.style.transformStyle = 'preserve-3d';
    card.style.transition = 'transform 0.15s ease-out, border-color 0.3s, box-shadow 0.3s';

    card.addEventListener('mousemove', (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      const centerX = rect.width / 2;
      const centerY = rect.height / 2;

      const rotateX = ((y - centerY) / centerY) * -10; // Rotate up/down max 10 deg
      const rotateY = ((x - centerX) / centerX) * 10;  // Rotate left/right max 10 deg

      card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`;
    });

    card.addEventListener('mouseleave', () => {
      card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)';
    });
  });
}
