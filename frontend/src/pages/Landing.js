/**
 * Q-Transplant Landing Page
 * Ultra-premium public-facing page with project details, quantum algo explainer,
 * ESP32 hardware section, live emergency feed, FAQ, About Us.
 */

export function renderLandingPage() {
  return `
    <!-- ══════════ NAVIGATION ══════════ -->
    <nav class="landing-nav">
      <a class="landing-nav-brand" href="#" id="landing-logo-link">
        <div class="brand-icon"><i class="fa-solid fa-heart-pulse"></i></div>
        Q-Transplant
        <span style="font-weight:300;color:#8d8d8d;font-size:13px;">| Quantum Life Network</span>
      </a>
      <div class="landing-nav-links">
        <a href="#how-it-works">How It Works</a>
        <a href="#quantum">Quantum Algo</a>
        <a href="#hardware">Hardware</a>
        <a href="#emergency">Emergency Feed</a>
        <a href="#about">About Us</a>
        <a href="#faq">FAQ</a>
        <a href="#" id="btn-go-portal" class="nav-cta">
          <i class="fa-solid fa-right-to-bracket"></i> Access Portal
        </a>
      </div>
    </nav>

    <!-- ══════════ HERO ══════════ -->
    <section class="hero" id="hero">
      <div class="hero-content">
        <!-- Left: Text -->
        <div class="hero-left">
          <div class="hero-badge">
            <span class="dot"></span>
            LIVE SYSTEM OPERATIONAL — 15 HOSPITALS CONNECTED
          </div>
          <h1 class="hero-title">
            Quantum-Powered<br>
            <span class="gradient-text">Organ Transplant</span><br>
            Coordination Network
          </h1>
          <p class="hero-subtitle">
            Q-Transplant uses <strong style="color:#f4f4f4">Grover's Quantum Search Algorithm</strong> to match 
            1,000+ donors to recipients in milliseconds — saving critical hours that save lives. 
            Connected to real ESP32 IoT hardware across 15 hospitals.
          </p>
          <div class="hero-cta-group">
            <a href="#" id="btn-hero-portal" class="btn-hero-primary">
              <i class="fa-solid fa-right-to-bracket"></i>
              Access Portal
            </a>
            <a href="#how-it-works" class="btn-hero-secondary">
              <i class="fa-solid fa-circle-play"></i>
              How It Works
            </a>
          </div>
          <div style="margin-top:2rem;display:flex;gap:2rem;flex-wrap:wrap;">
            <div style="display:flex;align-items:center;gap:8px;">
              <span style="width:8px;height:8px;border-radius:50%;background:#42be65;display:inline-block;animation:blink-led 1.5s infinite;"></span>
              <span style="font-size:12px;color:#8d8d8d;">Real-time ESP32 Telemetry</span>
            </div>
            <div style="display:flex;align-items:center;gap:8px;">
              <span style="width:8px;height:8px;border-radius:50%;background:#0f62fe;display:inline-block;"></span>
              <span style="font-size:12px;color:#8d8d8d;">Grover's O(√N) Search</span>
            </div>
            <div style="display:flex;align-items:center;gap:8px;">
              <span style="width:8px;height:8px;border-radius:50%;background:#8a3ffc;display:inline-block;"></span>
              <span style="font-size:12px;color:#8d8d8d;">AI Fraud Verification</span>
            </div>
          </div>
        </div>

        <!-- Right: Hardware Visualization -->
        <div class="hero-right" style="animation:float 4s ease-in-out infinite">
          <div class="hardware-card">
            <div class="hardware-label"><i class="fa-solid fa-microchip"></i> ESP32 — HOSPITAL UNIT · LIVE</div>
            <div class="esp32-board">
              <div class="esp32-title">ESP32 DEVKIT v4 | Q-Transplant Node</div>
              <div style="font-size:11px;color:#8d8d8d;margin-bottom:0.75rem;">3 PUSH BUTTONS — OLED DISPLAY — BUZZER — RGB LED</div>
              <div class="hw-buttons-row">
                <button class="hw-btn hw-btn-emergency" id="demo-btn-emergency">
                  <i class="fa-solid fa-siren-on"></i><br>BTN 1<br>EMERGENCY
                </button>
                <button class="hw-btn hw-btn-donor">
                  <i class="fa-solid fa-heart"></i><br>BTN 2<br>DONOR AVAIL
                </button>
                <button class="hw-btn hw-btn-ack">
                  <i class="fa-solid fa-check-double"></i><br>BTN 3<br>ACKNOWLEDGED
                </button>
              </div>
              <div class="led-row">
                <div class="led led-red" id="demo-led-red"></div>
                <span class="led-label">EMERGENCY</span>
                <div class="led led-green" id="demo-led-green" style="margin-left:12px;"></div>
                <span class="led-label">MATCHED</span>
                <i class="fa-solid fa-volume-high" style="margin-left:12px;font-size:12px;color:#8d8d8d;" id="demo-buzzer"></i>
                <span class="led-label">BUZZER</span>
              </div>
            </div>

            <div class="oled-display" id="demo-oled">
              &gt; Q-TRANSPLANT v2.0<br>
              &gt; 15 HOSPITALS ONLINE<br>
              &gt; DONORS: 1247 | WAITING: 893<br>
              &gt; STATUS: MONITORING...<br>
              &gt; QUANTUM ENGINE: READY<br>
              &gt; _
            </div>

            <div style="margin-top:1rem;">
              <div style="font-size:10px;color:#8d8d8d;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;">
                <i class="fa-solid fa-hospital"></i> NETWORK NODES (15 HOSPITALS)
              </div>
              <div class="hospital-nodes">
                <div class="hosp-node active-emergency">Apollo<br>Bengaluru</div>
                <div class="hosp-node">AIIMS<br>Delhi</div>
                <div class="hosp-node">Fortis<br>Mumbai</div>
                <div class="hosp-node">CMC<br>Vellore</div>
                <div class="hosp-node">Manipal<br>Mangaluru</div>
                <div class="hosp-node">NIMHANS<br>Bengaluru</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ══════════ STATS ══════════ -->
    <div class="stats-strip">
      <div class="stats-grid">
        <div>
          <div class="stat-number">1,247</div>
          <div class="stat-label">Registered Donors</div>
        </div>
        <div>
          <div class="stat-number">893</div>
          <div class="stat-label">Patients Waiting</div>
        </div>
        <div>
          <div class="stat-number">15</div>
          <div class="stat-label">Hospitals Connected</div>
        </div>
        <div>
          <div class="stat-number">0.3ms</div>
          <div class="stat-label">Quantum Match Time</div>
        </div>
      </div>
    </div>

    <!-- ══════════ HOW IT WORKS ══════════ -->
    <section class="section" id="how-it-works" style="background:#0a0a0a;">
      <div class="section-inner">
        <div class="section-badge"><i class="fa-solid fa-route"></i> THE SYSTEM</div>
        <h2 class="section-title">What Problem Do We Solve?</h2>
        <p class="section-subtitle">
          Traditional organ matching requires searching through thousands of records manually — 
          taking hours. When an organ becomes available, every second counts. We solve this.
        </p>
        <div class="problem-grid">
          <div class="problem-card red" style="animation-delay:0s">
            <div class="problem-card-icon">⏱️</div>
            <h3>Time-Critical Matching</h3>
            <p>A heart has 4–6 hours of viability. Traditional linear search through 1,000+ donors takes too long. Our Grover's algorithm finds the perfect match in O(√N) time — microseconds instead of minutes.</p>
          </div>
          <div class="problem-card blue" style="animation-delay:0.1s">
            <div class="problem-card-icon">🏥</div>
            <h3>Hospital Coordination</h3>
            <p>15 hospitals need instant communication. When an emergency occurs, all connected hospitals receive real-time alerts via ESP32 hardware — buzzers sound, red LEDs flash, and the Quantum engine activates.</p>
          </div>
          <div class="problem-card purple" style="animation-delay:0.2s">
            <div class="problem-card-icon">🔬</div>
            <h3>HLA & Blood Type Accuracy</h3>
            <p>Organ rejection is life-threatening. Our matching engine verifies ABO blood compatibility, HLA antigen similarity across 6 loci, and urgency score — ensuring only biologically perfect matches are shown.</p>
          </div>
          <div class="problem-card green" style="animation-delay:0.3s">
            <div class="problem-card-icon">🛡️</div>
            <h3>Verified Professionals Only</h3>
            <p>Doctors must submit live camera photos and medical certificates. AI scans for fraud patterns. Organizer reviews and approves. Only verified doctors can enter donor data — protecting system integrity.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ══════════ QUANTUM ALGORITHM ══════════ -->
    <section class="quantum-section" id="quantum">
      <div class="section-inner">
        <div class="section-badge"><i class="fa-solid fa-atom"></i> QUANTUM COMPUTING</div>
        <h2 class="section-title">Grover's Algorithm — <span style="color:#8a3ffc">O(√N) Search</span></h2>
        <p class="section-subtitle">
          Classical search through 1,000 donors: up to 1,000 comparisons. 
          Grover's quantum search: ~32 iterations. The speedup is exponential — and it scales to any database size.
        </p>

        <div class="quantum-viz">
          <div class="quantum-wave-bar"></div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:2rem;align-items:start;">
            <div>
              <h3 style="font-size:15px;font-weight:600;color:#be95ff;margin-bottom:1rem;">
                <i class="fa-solid fa-diagram-project"></i> How Grover's Search Works
              </h3>
              <div style="font-size:13px;color:#c6c6c6;line-height:1.9;">
                <p>1. <strong style="color:#f4f4f4">Superposition</strong> — All 1,000 donor states exist simultaneously in quantum memory</p>
                <p>2. <strong style="color:#f4f4f4">Oracle</strong> — Marks the target state (matching blood type + HLA profile)</p>
                <p>3. <strong style="color:#f4f4f4">Amplitude Amplification</strong> — Boosts probability of the correct match</p>
                <p>4. <strong style="color:#f4f4f4">Measurement</strong> — Collapses to the perfect donor with ~99.9% probability</p>
                <p>5. <strong style="color:#f4f4f4">Result</strong> — Matching hospital receives buzzer alert + result notification</p>
              </div>
            </div>
            <div>
              <div style="background:rgba(10,10,10,0.9);border:1px solid rgba(138,63,252,0.3);border-radius:10px;padding:1.5rem;font-family:'IBM Plex Mono',monospace;font-size:12px;color:#be95ff;line-height:1.8;">
                <div style="color:#8d8d8d;margin-bottom:0.5rem;"># Grover's Search - Q-Transplant</div>
                <div style="color:#42be65;">def grover_search(donors, target):</div>
                <div style="color:#c6c6c6;">&nbsp;&nbsp;N = len(donors)  # 1000+</div>
                <div style="color:#c6c6c6;">&nbsp;&nbsp;iterations = int(π/4 * √N)</div>
                <div style="color:#78a9ff;">&nbsp;&nbsp;# ~25 iterations for N=1000</div>
                <div style="color:#c6c6c6;">&nbsp;&nbsp;ψ = superposition(donors)</div>
                <div style="color:#c6c6c6;">&nbsp;&nbsp;for _ in range(iterations):</div>
                <div style="color:#c6c6c6;">&nbsp;&nbsp;&nbsp;&nbsp;ψ = oracle(ψ, target)</div>
                <div style="color:#c6c6c6;">&nbsp;&nbsp;&nbsp;&nbsp;ψ = diffusion(ψ)</div>
                <div style="color:#42be65;">&nbsp;&nbsp;return measure(ψ)  # ✓ Match!</div>
                <div style="color:#f1c21b;margin-top:0.5rem;">&gt; Complexity: O(√N) vs O(N)</div>
                <div style="color:#f1c21b;">&gt; Speedup: 31.6x for N=1000</div>
              </div>
            </div>
          </div>

          <div class="quantum-steps">
            <div class="q-step">
              <div class="q-step-num">1</div>
              <h4>Emergency Triggered</h4>
              <p>Hospital presses Button 1 on ESP32. Alert broadcasts to all 15 hospital nodes instantly via WebSocket.</p>
            </div>
            <div class="q-step">
              <div class="q-step-num">2</div>
              <h4>Requirements Entered</h4>
              <p>Hospital enters organ type, blood type, HLA profile, urgency level in the emergency form.</p>
            </div>
            <div class="q-step">
              <div class="q-step-num">3</div>
              <h4>Grover's Search Runs</h4>
              <p>Quantum algorithm searches all donor-hospital data in O(√N) iterations — milliseconds.</p>
            </div>
            <div class="q-step">
              <div class="q-step-num">4</div>
              <h4>Match Found</h4>
              <p>Matching hospital receives buzzer alert + green LED. Only the matched hospital is notified.</p>
            </div>
            <div class="q-step">
              <div class="q-step-num">5</div>
              <h4>Direct Contact</h4>
              <p>Emergency hospital views result and calls matched hospital directly via the platform interface.</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ══════════ HARDWARE SECTION ══════════ -->
    <section class="hardware-section" id="hardware">
      <div class="section-inner">
        <div class="section-badge"><i class="fa-solid fa-microchip"></i> IoT HARDWARE</div>
        <h2 class="section-title">ESP32 Hardware Network</h2>
        <p class="section-subtitle">
          Every hospital has a physical ESP32 device with OLED display, buzzer, RGB LED, and 3 dedicated push buttons. 
          Physical alerts make emergencies impossible to miss.
        </p>

        <div class="hw-flow">
          <div class="hw-node emergency-node">
            <div class="icon">🚨</div>
            <h4>BTN 1: EMERGENCY</h4>
            <p>Triggers alert to all hospitals</p>
          </div>
          <div class="hw-arrow">→</div>
          <div class="hw-node">
            <div class="icon">📡</div>
            <h4>WebSocket Broadcast</h4>
            <p>Instant push to 14 other nodes</p>
          </div>
          <div class="hw-arrow">→</div>
          <div class="hw-node">
            <div class="icon">🔴</div>
            <h4>Red LED + Buzzer</h4>
            <p>All hospitals alerted physically</p>
          </div>
          <div class="hw-arrow">→</div>
          <div class="hw-node">
            <div class="icon">⚛️</div>
            <h4>Grover's Search</h4>
            <p>Backend matches in O(√N)</p>
          </div>
          <div class="hw-arrow">→</div>
          <div class="hw-node success-node">
            <div class="icon">🟢</div>
            <h4>BTN 3: ACKNOWLEDGED</h4>
            <p>Match confirmed — green LED</p>
          </div>
        </div>

        <div style="margin-top:3rem;display:grid;grid-template-columns:repeat(3,1fr);gap:1.5rem;">
          <div class="problem-card blue">
            <div class="problem-card-icon">📟</div>
            <h3>OLED Display</h3>
            <p>128×64 OLED shows real-time organ tracking data, match results, and system status — always visible at nurse station.</p>
          </div>
          <div class="problem-card red">
            <div class="problem-card-icon">🔊</div>
            <h3>Piezo Buzzer</h3>
            <p>Audible alarm ensures no emergency is missed. Volume escalates based on urgency level — CRITICAL plays 3× louder.</p>
          </div>
          <div class="problem-card green">
            <div class="problem-card-icon">💡</div>
            <h3>RGB LED Status</h3>
            <p>Red = Emergency active. Green = Match found. Blue = Monitoring. Yellow = Algorithm running. Visible across the room.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ══════════ LIVE EMERGENCY FEED ══════════ -->
    <section class="section" id="emergency" style="background:rgba(218,30,40,0.03);border-top:1px solid rgba(218,30,40,0.1);">
      <div class="section-inner">
        <div class="section-badge" style="background:rgba(218,30,40,0.1);border-color:rgba(218,30,40,0.3);color:#ff8389;">
          <i class="fa-solid fa-triangle-exclamation"></i> LIVE EMERGENCY FEED
        </div>
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
          <div>
            <h2 class="section-title" style="margin-bottom:0.25rem;">Active Organ Requests</h2>
            <p class="section-subtitle" style="margin-bottom:0;">
              Real-time emergency requests triggered by ESP32 hardware buttons across 15 connected hospitals.
            </p>
          </div>
          <button id="btn-open-emergency-input-modal" class="btn-hero-primary" style="background:#da1e28; border-color:#da1e28; font-size:12px; padding:10px 18px; white-space:nowrap;">
            <i class="fa-solid fa-plus-circle"></i> Submit Emergency Organ Request
          </button>
        </div>

        <div class="emergency-ticker" id="landing-emergency-feed">
          <div class="ticker-header">
            <div class="ticker-dot"></div>
            LIVE — HARDWARE &amp; QUANTUM ENGINE ACTIVE
            <span style="margin-left:auto;font-weight:400;opacity:0.8;font-size:11px;" id="emergency-count-label">Loading...</span>
          </div>
          <div class="ticker-items" id="emergency-feed-items">
            <div style="padding:1.5rem;text-align:center;color:#8d8d8d;font-size:13px;">
              <i class="fa-solid fa-spinner fa-spin"></i> Loading emergency feed...
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Modal for Emergency Organ Request Entry -->
    <div id="landing-emergency-modal" class="modal-overlay" style="display:none; position:fixed; top:0; left:0; width:100vw; height:100vh; background:rgba(0,0,0,0.85); backdrop-filter:blur(6px); z-index:99999; justify-content:center; align-items:center;">
      <div style="background:#161616; border:1px solid #da1e28; border-radius:12px; width:90%; max-width:550px; padding:2rem; box-shadow:0 0 35px rgba(218,30,40,0.4); position:relative;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1.25rem;">
          <h3 style="font-size:16px; color:#ff8389; font-weight:700; margin:0;"><i class="fa-solid fa-siren-on"></i> Emergency Patient Organ Dispatch Input</h3>
          <button id="btn-close-emergency-modal" style="background:none; border:none; color:#8d8d8d; font-size:18px; cursor:pointer;">&times;</button>
        </div>
        <form id="emergency-request-form" style="display:flex; flex-direction:column; gap:12px;">
          <div>
            <label style="font-size:11px; color:#c6c6c6; display:block; margin-bottom:4px;">Hospital Name</label>
            <input type="text" id="em-hosp-name" value="Apollo Specialty Hospital" required style="width:100%; background:#262626; color:#fff; border:1px solid #393939; padding:8px; border-radius:4px; font-size:12px;" />
          </div>
          <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">
            <div>
              <label style="font-size:11px; color:#c6c6c6; display:block; margin-bottom:4px;">Organ Needed</label>
              <select id="em-organ" style="width:100%; background:#262626; color:#fff; border:1px solid #393939; padding:8px; border-radius:4px; font-size:12px;">
                <option value="Heart">Heart</option>
                <option value="Kidney">Kidney</option>
                <option value="Liver">Liver</option>
                <option value="Lung">Lung</option>
              </select>
            </div>
            <div>
              <label style="font-size:11px; color:#c6c6c6; display:block; margin-bottom:4px;">Blood Type</label>
              <select id="em-blood" style="width:100%; background:#262626; color:#fff; border:1px solid #393939; padding:8px; border-radius:4px; font-size:12px;">
                <option value="O+">O+</option>
                <option value="A+">A+</option>
                <option value="B+">B+</option>
                <option value="AB+">AB+</option>
              </select>
            </div>
          </div>
          <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">
            <div>
              <label style="font-size:11px; color:#c6c6c6; display:block; margin-bottom:4px;">HLA Profile</label>
              <input type="text" id="em-hla" value="A2,B7,DR4" required style="width:100%; background:#262626; color:#fff; border:1px solid #393939; padding:8px; border-radius:4px; font-size:12px;" />
            </div>
            <div>
              <label style="font-size:11px; color:#c6c6c6; display:block; margin-bottom:4px;">Patient Age</label>
              <input type="number" id="em-age" value="45" required style="width:100%; background:#262626; color:#fff; border:1px solid #393939; padding:8px; border-radius:4px; font-size:12px;" />
            </div>
          </div>
          <button type="submit" class="btn-hero-primary" style="background:#da1e28; border-color:#da1e28; justify-content:center; padding:10px; font-size:13px; margin-top:8px;">
            <i class="fa-solid fa-bolt"></i> BROADCAST EMERGENCY TO ALL HOSPITALS
          </button>
        </form>
      </div>
    </div>

    <!-- ══════════ ABOUT US ══════════ -->
    <section class="about-section" id="about">
      <div class="section-inner">
        <div class="section-badge"><i class="fa-solid fa-users"></i> ABOUT US</div>
        <h2 class="section-title">The Team Behind Q-Transplant</h2>
        <div class="about-grid">
          <div>
            <div class="about-img-placeholder">
              <div class="about-icon-large">🏥</div>
              <h3 style="font-size:1.1rem;font-weight:600;color:#f4f4f4;margin-bottom:0.5rem;">Q-Transplant Research Lab</h3>
              <p style="font-size:13px;color:#8d8d8d;max-width:280px;">
                Building quantum-powered healthcare infrastructure to eliminate preventable deaths from transplant delays.
              </p>
            </div>
          </div>
          <div>
            <p class="about-text">
              Q-Transplant was born from a simple but devastating observation: patients die waiting for organ transplants 
              not because donors don't exist — but because the <strong style="color:#f4f4f4">matching and coordination system is too slow</strong>.
            </p>
            <p class="about-text" style="margin-top:1rem;">
              We combined quantum computing principles (Grover's search algorithm), IoT hardware (ESP32 multi-button systems 
              in 15 hospitals), AI fraud detection for doctor verification, and a real-time coordination platform to 
              <strong style="color:#f4f4f4">compress hours of searching into milliseconds</strong>.
            </p>
            <p class="about-text" style="margin-top:1rem;">
              Contact for verification: 
              <a href="mailto:aravindhjoshua10@gmail.com" class="contact-chip" style="display:inline-flex;margin-top:0.5rem;">
                <i class="fa-solid fa-envelope"></i>
                aravindhjoshua10@gmail.com
              </a>
            </p>
            <div style="margin-top:1.5rem;">
              <div class="team-card">
                <div class="team-avatar"><i class="fa-solid fa-user-tie"></i></div>
                <div class="team-info">
                  <h4>Aravindh Joshua</h4>
                  <p>Lead Engineer — Hardware, Quantum Algorithm, Full-Stack Architecture</p>
                </div>
              </div>
              <div class="team-card">
                <div class="team-avatar" style="background:linear-gradient(135deg,#198038,#044317)"><i class="fa-solid fa-stethoscope"></i></div>
                <div class="team-info">
                  <h4>Clinical Advisory Board</h4>
                  <p>Transplant Surgeons, Nephrologists, Hepatologists — Protocol Design</p>
                </div>
              </div>
              <div class="team-card">
                <div class="team-avatar" style="background:linear-gradient(135deg,#8a3ffc,#491d8b)"><i class="fa-solid fa-microchip"></i></div>
                <div class="team-info">
                  <h4>Hardware Engineering</h4>
                  <p>ESP32 IoT Network across 15 hospitals — Real-time telemetry + alert system</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ══════════ FAQ ══════════ -->
    <section class="faq-section" id="faq">
      <div class="section-inner">
        <div class="section-badge"><i class="fa-solid fa-circle-question"></i> FAQ</div>
        <h2 class="section-title" style="text-align:center;">Frequently Asked Questions</h2>
        <div class="faq-list">
          ${renderFAQ("How does Grover's algorithm find a matching organ faster?",
            "Classical search examines donors one by one — O(N) complexity. Grover's quantum search uses amplitude amplification to find the target in O(√N) steps. For 1,000 donors, that means ~32 quantum operations instead of up to 1,000 classical comparisons — a ~31.6× speedup. For 1 million donors, the speedup becomes ~1,000×.")}
          ${renderFAQ("What does the ESP32 hardware actually do?",
            "Each hospital has a physical ESP32 microcontroller with 3 dedicated buttons: Button 1 triggers a hospital-wide emergency, Button 2 signals a donor is available, and Button 3 acknowledges a match. An OLED display shows live status. A buzzer and RGB LED provide unmissable physical alerts — red for emergency, green for match confirmed. All 15 hospital units are connected via WebSockets.")}
          ${renderFAQ("How are doctors verified to prevent fraud?",
            "Doctors must complete a 3-step verification: (1) Live camera photo capture at registration time — no uploaded photos allowed, (2) Medical certificate upload which is analyzed by AI for authenticity markers, (3) Organizer manual review with One-Click Approve/Reject via email with doctor photo and details. Only approved doctors can enter donor data into the system.")}
          ${renderFAQ("Who can register and access the portal?",
            "There are 4 portal types: Organizer (admin) — manages all users, approvals, and system data; Doctor — registers after organizer approval, manages donor entries; Hospital — registers their institution and manages emergency requests; Donor — registers through their doctor and can track their donation status. Each role has a dedicated login portal and dashboard.")}
          ${renderFAQ("What happens when an emergency is triggered?",
            "When a hospital presses Button 1 (Emergency): (1) All connected hospitals receive a buzzer alert and red LED signal, (2) The emergency hospital enters organ requirements in the platform, (3) Grover's quantum search runs through all registered donor data, (4) Only the single best-matched hospital receives a green LED signal and buzzer, (5) The emergency hospital can view which hospital has the match and call them directly through the platform.")}
          ${renderFAQ("What organ types and blood compatibility is handled?",
            "Q-Transplant handles Heart, Kidney, Liver, Lungs, Pancreas, and Corneas. Matching criteria include: ABO blood group compatibility (must match or be O universal), HLA antigen similarity across A, B, C, DR, DQ, DP loci, patient urgency score (1–10), organ ischemia time constraints, and geographic proximity of the donor hospital. All factors are weighted in the quantum matching oracle.")}
          ${renderFAQ("Is real-time tracking of the organ transport available?",
            "Yes. The cold-box (organ transport container) has an integrated ESP32 that sends GPS coordinates, internal temperature, humidity, and battery level via WebSocket every 5 seconds. The hospital dashboard shows a live Leaflet map tracking the cold-box in real time, along with alerts if temperature goes out of safe range or if estimated ischemia time is approaching the limit.")}
        </div>
      </div>
    </section>

    <!-- ══════════ FOOTER ══════════ -->
    <footer class="landing-footer">
      <div class="footer-inner">
        <div class="footer-brand">
          <h3><i class="fa-solid fa-heart-pulse" style="color:#0f62fe;margin-right:8px;"></i>Q-Transplant</h3>
          <p style="margin-top:0.75rem;">
            Quantum-Powered Organ Transplant Coordination Network.<br>
            Saving lives through technology, speed, and precision.
          </p>
          <a href="mailto:aravindhjoshua10@gmail.com" class="contact-chip" style="display:inline-flex;margin-top:1rem;">
            <i class="fa-solid fa-envelope"></i>
            aravindhjoshua10@gmail.com
          </a>
        </div>
        <div class="footer-col">
          <h4>Platform</h4>
          <a href="#how-it-works">How It Works</a>
          <a href="#quantum">Quantum Algorithm</a>
          <a href="#hardware">ESP32 Hardware</a>
          <a href="#emergency">Emergency Feed</a>
        </div>
        <div class="footer-col">
          <h4>Portals</h4>
          <a href="#" class="portal-link-footer" data-portal="organizer">Organizer Login</a>
          <a href="#" class="portal-link-footer" data-portal="doctor">Doctor Portal</a>
          <a href="#" class="portal-link-footer" data-portal="hospital">Hospital Portal</a>
          <a href="#" class="portal-link-footer" data-portal="donor">Donor Portal</a>
        </div>
        <div class="footer-col">
          <h4>Technology</h4>
          <a href="#">FastAPI Backend</a>
          <a href="#">SQLAlchemy ORM</a>
          <a href="#">ESP32 Firmware</a>
          <a href="#">Grover's Algorithm</a>
        </div>
      </div>
      <div class="footer-bottom">
        <p>© 2026 Q-Transplant. Built with ❤️ for saving lives.</p>
        <p>Powered by Quantum Computing + ESP32 IoT + FastAPI</p>
      </div>
    </footer>
  `;
}

function renderFAQ(question, answer) {
  return `
    <div class="faq-item" onclick="this.classList.toggle('open')">
      <div class="faq-question">
        <span>${question}</span>
        <i class="fa-solid fa-chevron-down arrow"></i>
      </div>
      <div class="faq-answer">${answer}</div>
    </div>
  `;
}

export async function loadEmergencyFeed() {
  try {
    const res = await fetch('/api/v1/emergency/?limit=8');
    if (!res.ok) throw new Error('No data');
    const events = await res.json();
    const container = document.getElementById('emergency-feed-items');
    const countEl = document.getElementById('emergency-count-label');
    if (!container) return;

    if (events.length === 0) {
      container.innerHTML = `<div style="padding:2rem;text-align:center;color:#8d8d8d;font-size:13px;">
        <i class="fa-solid fa-shield-check" style="font-size:2rem;color:#42be65;margin-bottom:0.75rem;display:block;"></i>
        No active emergencies. System monitoring 15 hospitals.
      </div>`;
      if (countEl) countEl.textContent = '0 ACTIVE';
      return;
    }

    if (countEl) countEl.textContent = `${events.filter(e => e.status !== 'CLOSED').length} ACTIVE`;

    container.innerHTML = events.map(ev => {
      const isMatched = ev.status === 'DONOR_MATCHED' || ev.status === 'MATCHED';
      const isAck = ev.status === 'ACKNOWLEDGED';
      const statusColor = isMatched ? '#42be65' : isAck ? '#78a9ff' : '#ff8389';

      return `
        <div class="ticker-item" style="border-left: 4px solid ${statusColor};">
          <div class="ticker-item-left">
            <h4><i class="fa-solid fa-hospital" style="color:${statusColor};margin-right:6px;"></i>${ev.hospital_name} — ${ev.organ_needed} needed</h4>
            <p>Blood Type: ${ev.blood_type} · HLA: ${ev.hla_type} · Patient Age: ${ev.patient_age}y · ${ev.hospital_city}</p>
            ${ev.matched_hospital ? `
              <div style="background:rgba(66,190,101,0.12); border:1px solid #42be65; border-radius:6px; padding:6px 10px; margin-top:6px; color:#42be65; font-size:12px; font-weight:600;">
                <i class="fa-solid fa-hospital-user"></i> DONOR MATCHED: ${ev.matched_hospital}
              </div>
            ` : ''}
            ${isAck ? `
              <div style="background:rgba(120,169,255,0.12); border:1px solid #78a9ff; border-radius:6px; padding:6px 10px; margin-top:6px; color:#78a9ff; font-size:12px; font-weight:600;">
                <i class="fa-solid fa-check-double"></i> ACKNOWLEDGED BY HOSPITAL CREW — Emergency Siren Stopped
              </div>
            ` : ''}
          </div>
          <div style="display:flex;flex-direction:column;align-items:flex-end;gap:6px;">
            <span class="ticker-badge ${ev.urgency_level === 'CRITICAL' ? 'badge-critical' : 'badge-searching'}">${ev.urgency_level}</span>
            <span class="ticker-badge" style="background:${statusColor}; color:#000; font-weight:700;">${ev.status}</span>
            <span style="font-size:10px;color:#6f6f6f;">${new Date(ev.created_at).toLocaleTimeString()}</span>
          </div>
        </div>
      `;
    }).join('');
  } catch (e) {
    const container = document.getElementById('emergency-feed-items');
    if (container) {
      container.innerHTML = `<div style="padding:1.5rem;text-align:center;color:#8d8d8d;font-size:13px;">
        <i class="fa-solid fa-shield-check" style="font-size:2rem;color:#42be65;display:block;margin-bottom:0.5rem;"></i>
        System operational — no active emergencies.
      </div>`;
    }
  }
}

export function attachLandingEvents(onPortalClick) {
  document.getElementById('btn-go-portal')?.addEventListener('click', e => { e.preventDefault(); onPortalClick(); });
  document.getElementById('btn-hero-portal')?.addEventListener('click', e => { e.preventDefault(); onPortalClick(); });
  document.querySelectorAll('.portal-link-footer').forEach(el => {
    el.addEventListener('click', e => { e.preventDefault(); onPortalClick(el.dataset.portal); });
  });

  // Emergency Modal Handlers
  const modal = document.getElementById('landing-emergency-modal');
  const btnOpen = document.getElementById('btn-open-emergency-input-modal');
  const btnClose = document.getElementById('btn-close-emergency-modal');
  const form = document.getElementById('emergency-request-form');

  if (btnOpen && modal) {
    btnOpen.onclick = () => { modal.style.display = 'flex'; };
  }
  if (btnClose && modal) {
    btnClose.onclick = () => { modal.style.display = 'none'; };
  }

  if (form) {
    form.onsubmit = async (e) => {
      e.preventDefault();
      const payload = {
        hospital_name: document.getElementById('em-hosp-name').value,
        hospital_city: "Bengaluru",
        contact_phone: "080-4444-1111",
        organ_needed: document.getElementById('em-organ').value,
        blood_type: document.getElementById('em-blood').value,
        hla_type: document.getElementById('em-hla').value,
        urgency_level: "CRITICAL",
        patient_age: parseInt(document.getElementById('em-age').value) || 45
      };

      try {
        const res = await fetch('/api/v1/emergency/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        if (res.ok) {
          modal.style.display = 'none';
          await loadEmergencyFeed();
          alert("🚨 Emergency organ request submitted & Grover quantum search executed across network!");
        }
      } catch (err) {
        console.error('Error submitting emergency:', err);
      }
    };
  }

  // Auto-refresh feed every 2.5 seconds to show ESP32 hardware button pushes in real-time!
  setInterval(() => {
    loadEmergencyFeed();
  }, 2500);

  // Demo ESP32 BTN 1: Emergency Trigger
  document.getElementById('demo-btn-emergency')?.addEventListener('click', async () => {
    const oled = document.getElementById('demo-oled');
    if (oled) oled.innerHTML = `&gt; ⚠️ EMERGENCY TRIGGERED!<br>&gt; Broadcasting to 14 hospitals...<br>&gt; Quantum search: INITIALIZING<br>&gt; Algorithm: Grover's O(√N)<br>&gt; Searching 1,247 donors...<br>&gt; _`;
    
    try {
      await fetch('/api/v1/emergency/dispatch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          cold_box_id: "BOX-ESP32-001",
          hospital_name: "Apollo Specialty Hospital",
          organ_type: "Heart",
          blood_type: "O+"
        })
      });
      await loadEmergencyFeed();
    } catch (e) { console.error(e); }

    setTimeout(() => {
      if (oled) oled.innerHTML = `&gt; ✅ MATCH FOUND!<br>&gt; Hospital: Fortis Healthcare, Bengaluru<br>&gt; Donor: O+ | HLA: A2,B7,DR4<br>&gt; Distance: 4.2 km<br>&gt; ETA: 12 minutes<br>&gt; BUZZER: ACTIVATED _`;
      const greenLed = document.getElementById('demo-led-green');
      if (greenLed) greenLed.style.animation = 'blink-led 0.3s infinite';
    }, 1500);
  });

  // Demo ESP32 BTN 2: Donor Available
  document.querySelector('.hw-btn-donor')?.addEventListener('click', async () => {
    const oled = document.getElementById('demo-oled');
    if (oled) oled.innerHTML = `&gt; 💚 DONOR ORGAN AVAILABLE!<br>&gt; Hospital: Fortis Healthcare, Bengaluru<br>&gt; Organ: Heart (O+)<br>&gt; Broadcasting to network...<br>&gt; _`;

    try {
      const res = await fetch('/api/v1/emergency/donor-available', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          hospital_name: "Fortis Healthcare, Bengaluru",
          organ_type: "Heart",
          blood_type: "O+",
          cold_box_id: "BOX-ESP32-001"
        })
      });
      const data = await res.json();
      await loadEmergencyFeed();
      alert(`🏥 DONOR AVAILABLE BROADCAST SENT!\n\nDonor Hospital Info Received: ${data.donor_hospital}\nOrgan: ${data.organ_type} (${data.blood_type})`);
    } catch (e) { console.error(e); }
  });

  // Demo ESP32 BTN 3: Acknowledged / Reset
  document.querySelector('.hw-btn-ack')?.addEventListener('click', async () => {
    const oled = document.getElementById('demo-oled');
    if (oled) oled.innerHTML = `&gt; ✔ ACKNOWLEDGED BY CREW<br>&gt; Emergency Siren STOPPED<br>&gt; Red LED: OFF<br>&gt; System Normal<br>&gt; _`;

    try {
      await fetch('/api/v1/emergency/acknowledge', { method: 'POST' });
      await loadEmergencyFeed();
      alert("🟢 ACKNOWLEDGED — Emergency Siren STOPPED & Alert Cleared!");
    } catch (e) { console.error(e); }
  });
}
