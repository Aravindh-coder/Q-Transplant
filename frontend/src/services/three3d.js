/**
 * ═══════════════════════════════════════════════════════════════════
 * Q-TRANSPLANT — ADVANCED 3D PROJECT-SPECIFIC MOTION GRAPHICS ENGINE
 * 
 * Includes 4 Project-Specific 3D Models in WebGL Background:
 *  1. 🧬 3D DNA Double Helix (HLA Donor-Recipient Genetic Matching)
 *  2. 🫀 3D Pulsating Organ Wireframe Mesh (Perfusion & Cold Box Telemetry)
 *  3. ⚛️ 3D Grover Qubit Bloch Sphere & Quantum Orbit Rings
 *  4. 🏥 3D Hospital Network Constellation & Laser Transport Routes
 * ═══════════════════════════════════════════════════════════════════
 */

import * as THREE from 'three';

let bgScene, bgCamera, bgRenderer;
let dnaGroup, heartMesh, heartCoreMesh, quantumBlochGroup, hospitalNodesGroup;
let mouseX = 0, mouseY = 0;
let is3DInitialized = false;
let pulseTime = 0;

export function init3DBackground() {
  const canvas = document.getElementById('q-3d-background-canvas');
  if (!canvas || is3DInitialized || typeof THREE === 'undefined') return;

  try {
    bgScene = new THREE.Scene();
    bgCamera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 1, 3000);
    bgCamera.position.z = 900;

    bgRenderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
    bgRenderer.setSize(window.innerWidth, window.innerHeight);
    bgRenderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    // ── 1. 🧬 3D DNA DOUBLE HELIX (HLA Matching) ───────────────────────────
    dnaGroup = new THREE.Group();
    const strandLength = 40;
    const radius = 60;
    const strandGeo = new THREE.SphereGeometry(2.5, 8, 8);
    const matBlue   = new THREE.MeshBasicMaterial({ color: 0x0f62fe, transparent: true, opacity: 0.85 });
    const matPurple = new THREE.MeshBasicMaterial({ color: 0x8a3ffc, transparent: true, opacity: 0.85 });
    const lineMat   = new THREE.MeshBasicMaterial({ color: 0x42be65, transparent: true, opacity: 0.45 });

    for (let i = 0; i < strandLength; i++) {
      const angle = i * 0.35;
      const y = (i - strandLength / 2) * 18;

      // Base A
      const x1 = Math.cos(angle) * radius;
      const z1 = Math.sin(angle) * radius;
      const sphere1 = new THREE.Mesh(strandGeo, matBlue);
      sphere1.position.set(x1, y, z1);
      dnaGroup.add(sphere1);

      // Base B
      const x2 = Math.cos(angle + Math.PI) * radius;
      const z2 = Math.sin(angle + Math.PI) * radius;
      const sphere2 = new THREE.Mesh(strandGeo, matPurple);
      sphere2.position.set(x2, y, z2);
      dnaGroup.add(sphere2);

      // Connecting Hydrogen Bond
      const rungDist = Math.sqrt((x2 - x1) ** 2 + (z2 - z1) ** 2);
      const rungGeo = new THREE.CylinderGeometry(0.8, 0.8, rungDist, 4);
      const rung = new THREE.Mesh(rungGeo, lineMat);
      rung.position.set((x1 + x2) / 2, y, (z1 + z2) / 2);
      rung.rotation.z = Math.PI / 2;
      rung.rotation.y = -angle;
      dnaGroup.add(rung);
    }
    dnaGroup.position.set(-420, 50, -200);
    dnaGroup.rotation.z = Math.PI / 6;
    bgScene.add(dnaGroup);

    // ── 2. 🫀 3D PULSATING ORGAN WIREFRAME MESH (Cold Box Telemetry) ────────
    const heartGroup = new THREE.Group();
    const heartGeo = new THREE.IcosahedronGeometry(75, 2);
    const heartMat = new THREE.MeshBasicMaterial({
      color: 0xda1e28,
      wireframe: true,
      transparent: true,
      opacity: 0.65
    });
    heartMesh = new THREE.Mesh(heartGeo, heartMat);

    const coreGeo = new THREE.IcosahedronGeometry(45, 1);
    const coreMat = new THREE.MeshBasicMaterial({
      color: 0xff8389,
      transparent: true,
      opacity: 0.3,
      blending: THREE.AdditiveBlending
    });
    heartCoreMesh = new THREE.Mesh(coreGeo, coreMat);

    // Telemetry Sensor HUD Orbit Ring around organ
    const sensorRingGeo = new THREE.TorusGeometry(105, 1, 16, 100);
    const sensorRingMat = new THREE.MeshBasicMaterial({ color: 0x42be65, wireframe: true, transparent: true, opacity: 0.5 });
    const sensorRing = new THREE.Mesh(sensorRingGeo, sensorRingMat);
    sensorRing.rotation.x = Math.PI / 3;

    heartGroup.add(heartMesh);
    heartGroup.add(heartCoreMesh);
    heartGroup.add(sensorRing);
    heartGroup.position.set(450, -80, -150);
    bgScene.add(heartGroup);

    // ── 3. ⚛️ 3D GROVER QUBIT BLOCH SPHERE (Quantum Matching Engine) ──────────
    quantumBlochGroup = new THREE.Group();
    const blochSphereGeo = new THREE.SphereGeometry(90, 16, 16);
    const blochSphereMat = new THREE.MeshBasicMaterial({
      color: 0x8a3ffc,
      wireframe: true,
      transparent: true,
      opacity: 0.25
    });
    const blochMesh = new THREE.Mesh(blochSphereGeo, blochSphereMat);
    quantumBlochGroup.add(blochMesh);

    // Qubit Orbiting Electron Particles
    const electronCount = 8;
    for (let i = 0; i < electronCount; i++) {
      const eGeo = new THREE.SphereGeometry(3.5, 8, 8);
      const eMat = new THREE.MeshBasicMaterial({ color: 0x00f0ff, transparent: true, opacity: 0.9 });
      const electron = new THREE.Mesh(eGeo, eMat);
      const orbitRingGeo = new THREE.TorusGeometry(90 + i * 10, 0.8, 8, 64);
      const orbitRingMat = new THREE.MeshBasicMaterial({ color: 0x0f62fe, transparent: true, opacity: 0.2 });
      const ring = new THREE.Mesh(orbitRingGeo, orbitRingMat);
      ring.rotation.x = (i * Math.PI) / electronCount;
      ring.rotation.y = (i * Math.PI) / (electronCount * 1.5);
      quantumBlochGroup.add(ring);
      quantumBlochGroup.add(electron);
    }
    quantumBlochGroup.position.set(0, 180, -350);
    bgScene.add(quantumBlochGroup);

    // ── 4. 🏥 3D HOSPITAL NETWORK CONSTELLATION NODES ───────────────────────
    hospitalNodesGroup = new THREE.Group();
    const nodeCount = 15;
    const nodeCoords = [];
    for (let i = 0; i < nodeCount; i++) {
      const nx = (Math.random() - 0.5) * 1400;
      const ny = (Math.random() - 0.5) * 800;
      const nz = (Math.random() - 0.5) * 600 - 100;
      nodeCoords.push(new THREE.Vector3(nx, ny, nz));

      const nodeGeo = new THREE.OctahedronGeometry(6, 0);
      const nodeMat = new THREE.MeshBasicMaterial({ color: i === 0 ? 0xda1e28 : 0x42be65, transparent: true, opacity: 0.85 });
      const nodeMesh = new THREE.Mesh(nodeGeo, nodeMat);
      nodeMesh.position.set(nx, ny, nz);
      hospitalNodesGroup.add(nodeMesh);
    }

    // Connect nodes with laser lines
    const lineGeometry = new THREE.BufferGeometry();
    const linePositions = [];
    for (let i = 0; i < nodeCount; i++) {
      for (let j = i + 1; j < nodeCount; j++) {
        if (nodeCoords[i].distanceTo(nodeCoords[j]) < 450) {
          linePositions.push(nodeCoords[i].x, nodeCoords[i].y, nodeCoords[i].z);
          linePositions.push(nodeCoords[j].x, nodeCoords[j].y, nodeCoords[j].z);
        }
      }
    }
    lineGeometry.setAttribute('position', new THREE.Float32BufferAttribute(linePositions, 3));
    const constLineMat = new THREE.LineBasicMaterial({ color: 0x0f62fe, transparent: true, opacity: 0.25 });
    const networkLines = new THREE.LineSegments(lineGeometry, constLineMat);
    hospitalNodesGroup.add(networkLines);
    bgScene.add(hospitalNodesGroup);

    // ── Ambient Background Floating Particle Field ─────────────────────────
    const particleCount = 600;
    const particleGeo = new THREE.BufferGeometry();
    const pPositions = new Float32Array(particleCount * 3);
    for (let i = 0; i < particleCount; i++) {
      pPositions[i * 3]     = (Math.random() - 0.5) * 2200;
      pPositions[i * 3 + 1] = (Math.random() - 0.5) * 1600;
      pPositions[i * 3 + 2] = (Math.random() - 0.5) * 1200;
    }
    particleGeo.setAttribute('position', new THREE.BufferAttribute(pPositions, 3));
    const pMat = new THREE.PointsMaterial({ size: 3, color: 0x78a9ff, transparent: true, opacity: 0.6, blending: THREE.AdditiveBlending });
    const ambientParticles = new THREE.Points(particleGeo, pMat);
    bgScene.add(ambientParticles);

    // Event Listeners
    window.addEventListener('mousemove', (e) => {
      mouseX = (e.clientX - window.innerWidth / 2) * 0.35;
      mouseY = (e.clientY - window.innerHeight / 2) * 0.35;
    });

    window.addEventListener('resize', () => {
      bgCamera.aspect = window.innerWidth / window.innerHeight;
      bgCamera.updateProjectionMatrix();
      bgRenderer.setSize(window.innerWidth, window.innerHeight);
    });

    // ── Animation Loop ──────────────────────────────────────────────────────
    function animate() {
      requestAnimationFrame(animate);
      pulseTime += 0.04;

      // Smooth Camera Inertia
      bgCamera.position.x += (mouseX - bgCamera.position.x) * 0.025;
      bgCamera.position.y += (-mouseY - bgCamera.position.y) * 0.025;
      bgCamera.lookAt(bgScene.position);

      // 🧬 DNA Spin
      if (dnaGroup) dnaGroup.rotation.y += 0.008;

      // 🫀 Heart Pulsate Simulation (60 BPM pulse contraction)
      if (heartMesh && heartCoreMesh) {
        const pulseScale = 1 + Math.sin(pulseTime) * 0.08;
        heartMesh.scale.set(pulseScale, pulseScale, pulseScale);
        heartMesh.rotation.y += 0.005;
        heartCoreMesh.scale.set(pulseScale * 0.95, pulseScale * 0.95, pulseScale * 0.95);
      }

      // ⚛️ Quantum Qubit Bloch Sphere Spin
      if (quantumBlochGroup) {
        quantumBlochGroup.rotation.y += 0.006;
        quantumBlochGroup.rotation.x += 0.003;
      }

      // 🏥 Hospital Network Slow Motion Drift
      if (hospitalNodesGroup) {
        hospitalNodesGroup.rotation.y += 0.0005;
      }

      ambientParticles.rotation.y += 0.0003;

      bgRenderer.render(bgScene, bgCamera);
    }

    animate();
    is3DInitialized = true;
  } catch (err) {
    console.warn('3D Project Background Init Failed:', err);
  }
}

// Track active animation frame IDs to prevent duplicate render loops
const activeAnimationFrames = {};

/**
 * Render interactive 3D WebGL Component Models inside portal dashboard cards.
 * Includes automatic 2D Canvas mathematical 3D vector fallback if WebGL fails.
 * @param {string} canvasId - Element ID of target <canvas>
 * @param {string} type - 'heart' | 'bloch' | 'dna' | 'coldbox'
 */
export function initEmbedded3DCanvas(canvasId, type) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;

  // Cancel any existing animation frame loop for this canvas ID
  if (activeAnimationFrames[canvasId]) {
    cancelAnimationFrame(activeAnimationFrames[canvasId]);
    delete activeAnimationFrames[canvasId];
  }

  // Determine actual rendered or attribute dimensions
  const parent = canvas.parentElement;
  const W = (parent && parent.clientWidth > 0) ? parent.clientWidth : (canvas.width || 400);
  const H = (canvas.height > 0) ? canvas.height : 140;

  canvas.width = W;
  canvas.height = H;

  // Attempt WebGL rendering with local Three.js
  let webglSuccess = false;
  if (typeof THREE !== 'undefined') {
    try {
      const scene = new THREE.Scene();
      const camera = new THREE.PerspectiveCamera(45, W / H, 0.1, 1000);
      camera.position.z = 180;

      const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true, preserveDrawingBuffer: true });
      renderer.setSize(W, H, false);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

      let mainMesh;

      if (type === 'heart') {
        mainMesh = new THREE.Mesh(
          new THREE.IcosahedronGeometry(42, 2),
          new THREE.MeshBasicMaterial({ color: 0xda1e28, wireframe: true })
        );
        const ring = new THREE.Mesh(
          new THREE.TorusGeometry(60, 1, 16, 64),
          new THREE.MeshBasicMaterial({ color: 0x42be65, wireframe: true, transparent: true, opacity: 0.7 })
        );
        ring.rotation.x = Math.PI / 3;
        mainMesh.add(ring);

      } else if (type === 'bloch') {
        mainMesh = new THREE.Group();
        // Wireframe sphere
        const sphere = new THREE.Mesh(
          new THREE.SphereGeometry(45, 16, 16),
          new THREE.MeshBasicMaterial({ color: 0x8a3ffc, wireframe: true })
        );
        mainMesh.add(sphere);
        // Equatorial orbit ring
        const r1 = new THREE.Mesh(
          new THREE.TorusGeometry(60, 1.2, 12, 64),
          new THREE.MeshBasicMaterial({ color: 0x0f62fe, transparent: true, opacity: 0.85 })
        );
        r1.rotation.x = Math.PI / 4;
        mainMesh.add(r1);
        // Polar orbit ring
        const r2 = new THREE.Mesh(
          new THREE.TorusGeometry(60, 1.2, 12, 64),
          new THREE.MeshBasicMaterial({ color: 0xbe95ff, transparent: true, opacity: 0.6 })
        );
        r2.rotation.y = Math.PI / 2;
        mainMesh.add(r2);
        // State vector arrow (cyan rod with top sphere)
        const arrow = new THREE.Mesh(
          new THREE.CylinderGeometry(2, 2, 80, 8),
          new THREE.MeshBasicMaterial({ color: 0x00f0ff })
        );
        arrow.rotation.z = Math.PI / 5;
        const tip = new THREE.Mesh(
          new THREE.SphereGeometry(5, 8, 8),
          new THREE.MeshBasicMaterial({ color: 0x00f0ff })
        );
        tip.position.y = 40;
        arrow.add(tip);
        mainMesh.add(arrow);

      } else if (type === 'dna') {
        mainMesh = new THREE.Group();
        for (let i = 0; i < 22; i++) {
          const angle = i * 0.38;
          const y = (i - 11) * 6;
          const s1 = new THREE.Mesh(new THREE.SphereGeometry(3, 8, 8), new THREE.MeshBasicMaterial({ color: 0x0f62fe }));
          s1.position.set(Math.cos(angle) * 32, y, Math.sin(angle) * 32);
          const s2 = new THREE.Mesh(new THREE.SphereGeometry(3, 8, 8), new THREE.MeshBasicMaterial({ color: 0x8a3ffc }));
          s2.position.set(Math.cos(angle + Math.PI) * 32, y, Math.sin(angle + Math.PI) * 32);
          mainMesh.add(s1, s2);
          if (i % 3 === 0) {
            const rung = new THREE.Mesh(
              new THREE.CylinderGeometry(0.8, 0.8, 64, 4),
              new THREE.MeshBasicMaterial({ color: 0x42be65, transparent: true, opacity: 0.6 })
            );
            rung.position.set(0, y, 0);
            rung.rotation.z = Math.PI / 2;
            rung.rotation.y = angle;
            mainMesh.add(rung);
          }
        }

      } else if (type === 'coldbox') {
        mainMesh = new THREE.Group();
        mainMesh.add(new THREE.Mesh(
          new THREE.BoxGeometry(50, 50, 50),
          new THREE.MeshBasicMaterial({ color: 0x0f62fe, wireframe: true })
        ));
        mainMesh.add(new THREE.Mesh(
          new THREE.SphereGeometry(18, 10, 10),
          new THREE.MeshBasicMaterial({ color: 0x42be65, transparent: true, opacity: 0.85 })
        ));
        const ant = new THREE.Mesh(
          new THREE.CylinderGeometry(1, 1, 40, 6),
          new THREE.MeshBasicMaterial({ color: 0xf1c21b })
        );
        ant.position.y = 40;
        mainMesh.add(ant);
      }

      if (mainMesh) scene.add(mainMesh);

      let pTime = 0;
      function animateWebGL() {
        if (!document.getElementById(canvasId)) return;
        activeAnimationFrames[canvasId] = requestAnimationFrame(animateWebGL);
        pTime += 0.04;
        if (mainMesh) {
          mainMesh.rotation.y += 0.015;
          mainMesh.rotation.x += 0.006;
          if (type === 'heart') {
            const s = 1 + Math.sin(pTime) * 0.08;
            mainMesh.scale.set(s, s, s);
          }
        }
        renderer.render(scene, camera);
      }
      animateWebGL();
      webglSuccess = true;
    } catch (err) {
      console.warn('[3D] WebGL render attempt failed, switching to 2D vector fallback:', err);
    }
  }

  // ── 2D Canvas Mathematical 3D Vector Projection Fallback Engine ──────────
  if (!webglSuccess) {
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let angleY = 0;
    let angleX = 0.3;

    function render2DFallback() {
      if (!document.getElementById(canvasId)) return;
      activeAnimationFrames[canvasId] = requestAnimationFrame(render2DFallback);
      angleY += 0.02;
      ctx.clearRect(0, 0, W, H);

      const cx = W / 2;
      const cy = H / 2;

      ctx.save();

      if (type === 'bloch' || type === 'heart') {
        // Draw glowing 3D wireframe sphere with orbit ring and state vector
        const radius = Math.min(W, H) * 0.32;

        // Outer glow circle
        ctx.beginPath();
        ctx.arc(cx, cy, radius, 0, Math.PI * 2);
        ctx.strokeStyle = (type === 'bloch') ? '#8a3ffc' : '#da1e28';
        ctx.lineWidth = 1.5;
        ctx.stroke();

        // Equatorial ellipse
        ctx.beginPath();
        ctx.ellipse(cx, cy, radius, radius * 0.35, angleY, 0, Math.PI * 2);
        ctx.strokeStyle = '#0f62fe';
        ctx.lineWidth = 1;
        ctx.stroke();

        // Polar ellipse
        ctx.beginPath();
        ctx.ellipse(cx, cy, radius * 0.35, radius, angleY * 0.7, 0, Math.PI * 2);
        ctx.strokeStyle = '#be95ff';
        ctx.lineWidth = 1;
        ctx.stroke();

        // Vector arrow line
        const vx = cx + Math.cos(angleY) * radius * 0.8;
        const vy = cy + Math.sin(angleY * 0.5) * radius * 0.6;
        ctx.beginPath();
        ctx.moveTo(cx, cy);
        ctx.lineTo(vx, vy);
        ctx.strokeStyle = '#00f0ff';
        ctx.lineWidth = 2.5;
        ctx.stroke();

        // Vector tip dot
        ctx.beginPath();
        ctx.arc(vx, vy, 4, 0, Math.PI * 2);
        ctx.fillStyle = '#00f0ff';
        ctx.fill();

      } else if (type === 'dna') {
        // Draw 3D DNA strand
        const r = 25;
        for (let i = 0; i < 18; i++) {
          const a = angleY + i * 0.4;
          const y = cy + (i - 9) * 6;
          const x1 = cx + Math.cos(a) * r;
          const x2 = cx + Math.cos(a + Math.PI) * r;

          ctx.beginPath();
          ctx.arc(x1, y, 3, 0, Math.PI * 2);
          ctx.fillStyle = '#0f62fe';
          ctx.fill();

          ctx.beginPath();
          ctx.arc(x2, y, 3, 0, Math.PI * 2);
          ctx.fillStyle = '#8a3ffc';
          ctx.fill();

          if (i % 3 === 0) {
            ctx.beginPath();
            ctx.moveTo(x1, y);
            ctx.lineTo(x2, y);
            ctx.strokeStyle = 'rgba(66, 190, 101, 0.6)';
            ctx.stroke();
          }
        }
      } else {
        // Coldbox wireframe cube
        const s = 30;
        ctx.strokeStyle = '#0f62fe';
        ctx.lineWidth = 1.5;
        ctx.strokeRect(cx - s, cy - s, s * 2, s * 2);
        ctx.strokeRect(cx - s + 8, cy - s - 8, s * 2, s * 2);

        ctx.beginPath();
        ctx.arc(cx, cy, 12, 0, Math.PI * 2);
        ctx.fillStyle = '#42be65';
        ctx.fill();
      }

      ctx.restore();
    }
    render2DFallback();
  }
}



/**
 * Attach 3D Motion Depth Mouse-Tilt effect to card elements across every page.
 * Includes both dark portal cards and new clinical white cards.
 */
export function attach3DTiltEffects() {
  const cards = document.querySelectorAll(
    '.problem-card, .portal-card, .kpi-card, .hardware-card, .q-step, .team-card, ' +
    '.match-result-card, .ultra-table-wrap, .clinical-card, .clinical-kpi-card'
  );

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

      const rotateX = ((y - centerY) / centerY) * -8;
      const rotateY = ((x - centerX) / centerX) * 8;

      card.style.transform = `perspective(1200px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.015, 1.015, 1.015)`;
    });

    card.addEventListener('mouseleave', () => {
      card.style.transform = 'perspective(1200px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)';
    });
  });
}
