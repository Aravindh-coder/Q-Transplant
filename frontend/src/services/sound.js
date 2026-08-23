/**
 * ═══════════════════════════════════════════════════════════════════
 * Q-TRANSPLANT — WEB AUDIO API PROCEDURAL MEDICAL SOUND EFFECTS
 * Zero-dependency Web Audio API synthesizer for emergency sirens & chimes
 * ═══════════════════════════════════════════════════════════════════
 */

let audioCtx = null;

function getAudioContext() {
  if (!audioCtx) {
    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    if (AudioContextClass) {
      audioCtx = new AudioContextClass();
    }
  }
  if (audioCtx && audioCtx.state === 'suspended') {
    audioCtx.resume();
  }
  return audioCtx;
}

/**
 * 🚨 Emergency SOS Siren Sound — single short blip (kept for backward compat)
 */
export function playEmergencyAlertSound() {
  try {
    const ctx = getAudioContext();
    if (!ctx) return;

    const osc = ctx.createOscillator();
    const gain = ctx.createGain();

    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(880, ctx.currentTime); // A5 note
    osc.frequency.exponentialRampToValueAtTime(440, ctx.currentTime + 0.3); // A4 note

    gain.gain.setValueAtTime(0.15, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.35);

    osc.connect(gain);
    gain.connect(ctx.destination);

    osc.start();
    osc.stop(ctx.currentTime + 0.35);
  } catch (e) {
    // Ignore audio autoplay policy restrictions
  }
}

/**
 * 🚑 REAL AMBULANCE SIREN — continuous two-tone wail (Hi-Lo European style),
 * loops until stopAmbulanceSiren() is called. Uses a single sweeping
 * oscillator scheduled ahead of time so there are no audible gaps/clicks
 * between cycles.
 */
let _sirenOsc = null;
let _sirenGain = null;
let _sirenSchedulerId = null;
let _sirenRunning = false;

export function startAmbulanceSiren() {
  try {
    if (_sirenRunning) return; // already wailing
    const ctx = getAudioContext();
    if (!ctx) return;

    _sirenRunning = true;

    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'sine';
    gain.gain.value = 0.11;
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start();

    _sirenOsc = osc;
    _sirenGain = gain;

    const HI = 980;   // Hz
    const LO = 620;   // Hz
    const CYCLE = 0.85; // seconds per hi->lo->hi sweep (ambulance-like)

    // Schedule frequency ramps a little ahead of real time, in a loop,
    // for as long as the siren is running.
    let nextCycleAt = ctx.currentTime;
    const scheduleAhead = 2.5; // seconds of lookahead per tick

    function scheduleCycles() {
      if (!_sirenRunning || !_sirenOsc) return;
      const now = ctx.currentTime;
      while (nextCycleAt < now + scheduleAhead) {
        osc.frequency.setValueAtTime(HI, nextCycleAt);
        osc.frequency.linearRampToValueAtTime(LO, nextCycleAt + CYCLE / 2);
        osc.frequency.linearRampToValueAtTime(HI, nextCycleAt + CYCLE);
        nextCycleAt += CYCLE;
      }
      _sirenSchedulerId = setTimeout(scheduleCycles, 800);
    }
    scheduleCycles();
  } catch (e) {
    _sirenRunning = false;
  }
}

export function stopAmbulanceSiren() {
  try {
    _sirenRunning = false;
    if (_sirenSchedulerId) {
      clearTimeout(_sirenSchedulerId);
      _sirenSchedulerId = null;
    }
    if (_sirenGain && audioCtx) {
      // Quick fade-out to avoid a hard click
      _sirenGain.gain.setValueAtTime(_sirenGain.gain.value, audioCtx.currentTime);
      _sirenGain.gain.linearRampToValueAtTime(0.0001, audioCtx.currentTime + 0.15);
    }
    if (_sirenOsc) {
      const osc = _sirenOsc;
      setTimeout(() => { try { osc.stop(); } catch (e) {} }, 200);
      _sirenOsc = null;
    }
    _sirenGain = null;
  } catch (e) {
    // Ignore
  }
}

export function isSirenPlaying() {
  return _sirenRunning;
}

/**
 * 💚 Donor Organ Matched Chime — a full ~3 second "match found" cue:
 * rising arpeggio, then two confirming double-chimes, then a sustained pad.
 */
export function playDonorMatchSound() {
  try {
    const ctx = getAudioContext();
    if (!ctx) return;

    const now = ctx.currentTime;

    const tone = (freq, start, dur, type = 'sine', peak = 0.12) => {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = type;
      osc.frequency.setValueAtTime(freq, start);
      gain.gain.setValueAtTime(0.0001, start);
      gain.gain.exponentialRampToValueAtTime(peak, start + 0.04);
      gain.gain.exponentialRampToValueAtTime(0.0001, start + dur);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(start);
      osc.stop(start + dur + 0.02);
    };

    // 0.0s – 0.4s: rising arpeggio (C5, E5, G5, C6)
    [523.25, 659.25, 783.99, 1046.50].forEach((f, i) => tone(f, now + i * 0.09, 0.3));

    // 0.6s & 1.4s: two confident "ding-ding" confirmation chimes
    tone(1046.50, now + 0.65, 0.35, 'sine', 0.14);
    tone(1318.51, now + 0.78, 0.35, 'sine', 0.10);
    tone(1046.50, now + 1.45, 0.35, 'sine', 0.14);
    tone(1318.51, now + 1.58, 0.35, 'sine', 0.10);

    // 1.9s – 3.0s: sustained warm pad chord (C-E-G) to let the moment land
    [523.25, 659.25, 783.99].forEach((f) => tone(f, now + 1.9, 1.1, 'triangle', 0.06));
  } catch (e) {
    // Ignore
  }
}

/**
 * 🎉 Happy Resolution Jingle — plays once the emergency is fully acknowledged
 * and resolved. A short, upbeat major-key melody (distinct from the donor
 * match chime), to close the loop on a positive note.
 */
export function playHappyAckSound() {
  try {
    const ctx = getAudioContext();
    if (!ctx) return;
    const now = ctx.currentTime;

    const tone = (freq, start, dur, type = 'sine', peak = 0.13) => {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = type;
      osc.frequency.setValueAtTime(freq, start);
      gain.gain.setValueAtTime(0.0001, start);
      gain.gain.exponentialRampToValueAtTime(peak, start + 0.03);
      gain.gain.exponentialRampToValueAtTime(0.0001, start + dur);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(start);
      osc.stop(start + dur + 0.02);
    };

    // Cheerful little melody: G5, C6, E6, G6 (major triad run-up) + final flourish
    const melody = [
      { f: 783.99, t: 0.00, d: 0.16 },   // G5
      { f: 1046.50, t: 0.14, d: 0.16 },  // C6
      { f: 1318.51, t: 0.28, d: 0.16 },  // E6
      { f: 1567.98, t: 0.42, d: 0.45 },  // G6 (held)
    ];
    melody.forEach(n => tone(n.f, now + n.t, n.d, 'triangle', 0.14));

    // Bright resolving chord underneath
    [1046.50, 1318.51, 1567.98].forEach(f => tone(f, now + 0.42, 0.55, 'sine', 0.06));
  } catch (e) {
    // Ignore
  }
}

/**
 * ✔ Acknowledge Confirmation Click (Soft Tech Click)
 */
export function playAckSound() {
  try {
    const ctx = getAudioContext();
    if (!ctx) return;

    const osc = ctx.createOscillator();
    const gain = ctx.createGain();

    osc.type = 'sine';
    osc.frequency.setValueAtTime(600, ctx.currentTime);

    gain.gain.setValueAtTime(0.08, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.08);

    osc.connect(gain);
    gain.connect(ctx.destination);

    osc.start();
    osc.stop(ctx.currentTime + 0.08);
  } catch (e) {
    // Ignore
  }
}
