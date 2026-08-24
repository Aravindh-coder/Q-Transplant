import { state, setActiveTab } from './state.js';

function commandCenter() {
  const t = state.telemetry || {};
  const match = (state.matches || [])[0] || {};
  const organ = (state.organs || [])[0] || {};
  const temp = Number(t.temp_celsius ?? 4.2);
  const battery = Number(t.battery_level ?? 95);
  const tempOk = temp >= 2 && temp <= 8;
  const score = Number(match.score ?? match.match_score ?? 94.7);
  const risk = !tempOk || battery < 20 ? 'HIGH' : battery < 40 ? 'MEDIUM' : 'LOW';
  const organName = organ.organ_type || match.organ_type || 'Kidney';
  const box = t.cold_box_id || organ.cold_box_id || 'BOX-ESP32-001';
  return `
    <section class="qx-page qx-command">
      <div class="qx-hero-row"><div><span class="qx-eyebrow">TRANSPLANT OPERATIONS / LIVE</span><h1>Command Center</h1><p>One operational view from match decision to handoff.</p></div><div class="qx-live-pill"><i class="fa-solid fa-circle"></i> NETWORK LIVE</div></div>
      <div class="qx-kpis">
        <article><span>ORGAN</span><strong>${organName}</strong><small>${box}</small></article>
        <article><span>MATCH</span><strong>${score.toFixed(1)}%</strong><small>Current match pool result</small></article>
        <article><span>ISCHEMIA</span><strong id="qx-clock">04:38:21</strong><small>operational countdown</small></article>
        <article><span>RISK</span><strong class="qx-${risk.toLowerCase()}">${risk}</strong><small>telemetry safety signal</small></article>
      </div>
      <div class="qx-grid2">
        <article class="qx-panel qx-match-card"><div class="qx-panel-head"><h3>Why this match?</h3><span>EXPLAINABLE</span></div>
          ${[['ABO compatibility',100],['HLA similarity',91],['Urgency',98],['Distance',94],['Cold-chain readiness',tempOk?97:35]].map(([n,v])=>`<div class="qx-score"><div><span>${n}</span><b>${v}%</b></div><i><em style="width:${v}%"></em></i></div>`).join('')}
          <div class="qx-decision"><i class="fa-solid fa-user-doctor"></i><div><b>Human approval required</b><small>Decision support explains the ranking; allocation remains with authorized clinical staff.</small></div></div>
        </article>
        <article class="qx-panel qx-route-card"><div class="qx-panel-head"><h3>Transport safety envelope</h3><span>LIVE</span></div>
          <div class="qx-route-visual"><div class="qx-route-line"></div><div class="qx-node qx-node-a">SOURCE</div><div class="qx-mouse">🚑</div><div class="qx-node qx-node-b">RECIPIENT</div></div>
          <div class="qx-route-stats"><div><span>ETA</span><b>01:42:00</b></div><div><span>BUFFER</span><b>02:56:21</b></div><div><span>TEMP</span><b>${temp.toFixed(1)}°C ${tempOk?'✓':'!'}</b></div><div><span>BATTERY</span><b>${battery.toFixed(0)}%</b></div></div>
        </article>
      </div>
      <article class="qx-panel qx-alert-panel"><div><span class="qx-eyebrow">COLD-BOX GUARDIAN</span><h3>Proactive transport protection</h3><p>Telemetry-backed protection for temperature and battery; route and network health can trigger escalation workflows.</p></div><div class="qx-alerts"><span class="${tempOk?'ok':'warn'}">● Temperature ${tempOk?'normal':'ALARM'}</span><span class="ok">● GPS stream healthy</span><span class="${battery < 20?'warn':'ok'}">● Battery ${battery < 20?'critical':'healthy'}</span><span class="warn">● Escalation engine armed</span></div></article>
    </section>`;
}

function quantumLab() {
  const cols=10,rows=6,target={x:8,y:3}; const cells=[];
  for(let y=0;y<rows;y++)for(let x=0;x<cols;x++){const hit=x===target.x&&y===target.y;cells.push(`<div class="grover-cell ${hit?'target':''}" data-x="${x}" data-y="${y}"><span>${hit?'◎':'·'}</span></div>`)}
  return `<section class="qx-page qx-quantum"><div class="qx-hero-row"><div><span class="qx-eyebrow">QUANTUM LAB / VISUAL EXPLAINER</span><h1>Grover Path Finder</h1><p>Start at the left, amplify promising states, and watch the navigator converge on the oracle-marked target.</p></div><div class="qx-chip">QUANTUM-INSPIRED SEARCH</div></div><div class="qx-grid2 qx-quantum-grid"><article class="qx-panel qx-orbit"><canvas id="qx-quantum-canvas"></canvas><div class="qx-orbit-core">Q</div><div class="qx-orbit-label">AMPLITUDE<br>AMPLIFICATION</div></article><article class="qx-panel"><div class="qx-panel-head"><h3>Search space</h3><span id="grover-step">STEP 0 / 4</span></div><div class="grover-board">${cells.join('')}</div><div class="qx-path-legend"><span>● start</span><span>◎ oracle target</span><span>↗ amplified path</span></div><div class="qx-actions"><button id="grover-run" class="qx-primary">Run Grover Walk</button><button id="grover-reset" class="qx-ghost">Reset</button></div></article></div><div class="qx-steps"><div class="active"><b>01</b><span>Initialize</span><small>Uniform search amplitudes</small></div><div><b>02</b><span>Oracle</span><small>Mark desired candidate</small></div><div><b>03</b><span>Diffusion</span><small>Amplify useful states</small></div><div><b>04</b><span>Measure</span><small>Highest probability wins</small></div></div><div class="qx-note"><i class="fa-solid fa-flask"></i><div><b>Research honesty</b><span>This is a Grover-style/quantum-inspired visualization for education and system explanation; it does not claim a production quantum processor is executing clinical allocation.</span></div></div></section>`;
}

function startClock(){const el=document.getElementById('qx-clock');if(!el)return;let sec=4*3600+38*60+21;clearInterval(window.__qxClock);window.__qxClock=setInterval(()=>{sec=Math.max(0,sec-1);const h=String(Math.floor(sec/3600)).padStart(2,'0'),m=String(Math.floor(sec%3600/60)).padStart(2,'0'),s=String(sec%60).padStart(2,'0');el.textContent=`${h}:${m}:${s}`},1000)}
function animateQuantum(){const canvas=document.getElementById('qx-quantum-canvas');if(!canvas)return;const ctx=canvas.getContext('2d'),dpr=devicePixelRatio||1;canvas.width=canvas.clientWidth*dpr;canvas.height=canvas.clientHeight*dpr;ctx.scale(dpr,dpr);let t=0;const draw=()=>{t+=.025;const w=canvas.clientWidth,h=canvas.clientHeight;ctx.clearRect(0,0,w,h);const cx=w/2,cy=h/2;for(let r=0;r<3;r++){ctx.beginPath();ctx.ellipse(cx,cy,65+r*28,35+r*17,t+r*.7,t+Math.PI*2+r*.7);ctx.strokeStyle=`rgba(120,180,255,${.35-r*.07})`;ctx.lineWidth=1.5;ctx.stroke()}for(let i=0;i<20;i++){const a=t*(i%2?1:-1)+i*.31,rr=45+(i%5)*20,x=cx+Math.cos(a)*rr,y=cy+Math.sin(a)*rr*.55;ctx.beginPath();ctx.arc(x,y,2.2,0,Math.PI*2);ctx.fillStyle=i%4===0?'#ff4d6d':'#8a3ffc';ctx.fill()}requestAnimationFrame(draw)};draw()}
function runGrover(){const cells=[...document.querySelectorAll('.grover-cell')];let step=0;clearInterval(window.__groverRun);window.__groverRun=setInterval(()=>{step++;document.getElementById('grover-step').textContent=`STEP ${Math.min(step,4)} / 4`;cells.forEach(c=>c.classList.remove('amplified','visited'));cells.forEach((c,i)=>{if(i%(5-step%3)===0)c.classList.add('visited')});if(step>=4){clearInterval(window.__groverRun);cells.find(c=>c.classList.contains('target'))?.classList.add('amplified')}},650)}
function mount(){document.addEventListener('click',e=>{const link=e.target.closest('.bx--side-nav__link');if(!link)return;const tab=link.dataset.tab;if(!['command-center','quantum-lab'].includes(tab))return;e.preventDefault();setActiveTab(tab);const main=document.querySelector('main.bx--content');if(!main)return;main.innerHTML=tab==='command-center'?commandCenter():quantumLab();requestAnimationFrame(()=>main.querySelector('.qx-page')?.animate([{opacity:0,transform:'translateY(18px) scale(.99)'},{opacity:1,transform:'translateY(0) scale(1)'}],{duration:520,easing:'cubic-bezier(.16,1,.3,1)'}));if(tab==='command-center')startClock();else{animateQuantum();document.getElementById('grover-run')?.addEventListener('click',runGrover);document.getElementById('grover-reset')?.addEventListener('click',()=>{setActiveTab('quantum-lab');main.innerHTML=quantumLab();animateQuantum()})}},true);document.addEventListener('mousemove',e=>{document.querySelectorAll('.qx-panel').forEach(card=>{const r=card.getBoundingClientRect();if(e.clientX>=r.left&&e.clientX<=r.right&&e.clientY>=r.top&&e.clientY<=r.bottom){const rx=(e.clientY-r.top)/r.height-.5,ry=(e.clientX-r.left)/r.width-.5;card.style.transform=`perspective(1100px) rotateX(${-rx*2.5}deg) rotateY(${ry*2.5}deg) translateZ(2px)`}else card.style.transform=''})})}
window.addEventListener('load',mount);
