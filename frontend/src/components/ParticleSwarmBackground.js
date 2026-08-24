// Lightweight connected-particle swarm background.
// Used only on the Donor and Hospital dashboards (per product decision to
// visually distinguish those two portals). Doctor/Organizer views keep the
// existing shared 3D ambient background untouched.

let rafId = null;
let canvasEl = null;
let resizeHandler = null;

const CONFIG = {
  donor:    { color: '66, 190, 101',  particleCount: 55, linkDistance: 130, speed: 0.25 }, // green — life/health
  hospital: { color: '255, 131, 137', particleCount: 55, linkDistance: 130, speed: 0.3 },  // red — emergency/clinical
};

export function initParticleSwarmBackground(variant) {
  stopParticleSwarmBackground();

  const cfg = CONFIG[variant];
  if (!cfg) return;

  canvasEl = document.createElement('canvas');
  canvasEl.id = 'particle-swarm-bg';
  canvasEl.style.cssText = `
    position: fixed;
    inset: 0;
    width: 100vw;
    height: 100vh;
    pointer-events: none;
    z-index: 0;
    opacity: 0.55;
  `;
  document.body.prepend(canvasEl);

  const ctx = canvasEl.getContext('2d');
  let w, h, particles;

  function size() {
    w = canvasEl.width = window.innerWidth;
    h = canvasEl.height = window.innerHeight;
  }

  function makeParticles() {
    particles = Array.from({ length: cfg.particleCount }, () => ({
      x: Math.random() * w,
      y: Math.random() * h,
      vx: (Math.random() - 0.5) * cfg.speed,
      vy: (Math.random() - 0.5) * cfg.speed,
      r: Math.random() * 1.6 + 0.6,
    }));
  }

  function tick() {
    ctx.clearRect(0, 0, w, h);

    for (const p of particles) {
      p.x += p.vx;
      p.y += p.vy;
      if (p.x < 0 || p.x > w) p.vx *= -1;
      if (p.y < 0 || p.y > h) p.vy *= -1;

      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${cfg.color}, 0.85)`;
      ctx.fill();
    }

    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < cfg.linkDistance) {
          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.strokeStyle = `rgba(${cfg.color}, ${0.18 * (1 - dist / cfg.linkDistance)})`;
          ctx.lineWidth = 1;
          ctx.stroke();
        }
      }
    }

    rafId = requestAnimationFrame(tick);
  }

  size();
  makeParticles();
  tick();

  resizeHandler = () => { size(); makeParticles(); };
  window.addEventListener('resize', resizeHandler);
}

export function stopParticleSwarmBackground() {
  if (rafId) cancelAnimationFrame(rafId);
  rafId = null;
  if (resizeHandler) window.removeEventListener('resize', resizeHandler);
  resizeHandler = null;
  if (canvasEl && canvasEl.parentNode) canvasEl.parentNode.removeChild(canvasEl);
  canvasEl = null;
}
