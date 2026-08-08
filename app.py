import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Chrono Crisis: Tactical Enforcement",
    page_icon="🎯",
    layout="centered",
)

st.markdown(
    """
    <style>
        .block-container { padding-top: 2rem; padding-bottom: 1rem; max-width: 560px; }
        header[data-testid="stHeader"] { background: transparent; }
        h1 { text-align:center; letter-spacing:1px; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("<h1>🎯 CHRONO CRISIS<br><span style='font-size:0.5em;color:#ff6a3c;'>TACTICAL ENFORCEMENT</span></h1>", unsafe_allow_html=True)
st.caption("A 28-chapter tactical rail-shooter across 4 sectors. Original characters, locations and story — built from scratch for the browser.")

GAME_HTML = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
  * { margin:0; padding:0; box-sizing:border-box; -webkit-tap-highlight-color:transparent; -webkit-user-select:none; user-select:none; }
  html, body { background:#0a0a0d; overflow:hidden; touch-action:none; font-family:'Courier New', monospace; }
  #gameWrap {
    position:relative; width:100%; max-width:460px; margin:0 auto;
    aspect-ratio: 3 / 4; background:#000; border:3px solid #2a2a33; border-radius:10px;
    overflow:hidden; box-shadow:0 0 30px rgba(255,90,40,0.15), inset 0 0 40px rgba(0,0,0,0.6);
  }
  canvas { display:block; width:100%; height:100%; cursor:crosshair; }

  #reloadBtn {
    position:absolute; bottom:16px; right:16px; width:76px; height:76px; border-radius:50%;
    background:radial-gradient(circle at 35% 30%, #ff6a3c, #7a1a05);
    border:3px solid #ffd9b0; color:#fff; font-weight:bold; font-size:12px;
    display:flex; align-items:center; justify-content:center; text-align:center;
    box-shadow:0 0 18px rgba(255,90,40,0.75); z-index:6; line-height:1.1; letter-spacing:0.5px;
  }
  #reloadBtn.flash { animation:reloadFlash 0.4s ease 2; }
  @keyframes reloadFlash { 0%,100%{ box-shadow:0 0 18px rgba(255,90,40,0.75);} 50%{ box-shadow:0 0 34px 10px rgba(255,255,255,0.9);} }
  #reloadBtn:active { transform:scale(0.9); }

  .overlay {
    position:absolute; inset:0; z-index:10; display:flex; flex-direction:column;
    align-items:center; justify-content:center; text-align:center; padding:26px;
    background:radial-gradient(ellipse at center, rgba(20,10,10,0.92), rgba(0,0,0,0.97));
    color:#f2f2f2;
  }
  .overlay h1 { font-size:1.5em; color:#ff5a3c; text-shadow:0 0 12px rgba(255,90,60,0.8); letter-spacing:2px; margin-bottom:6px;}
  .overlay h2 { font-size:1.05em; color:#ffd9b0; margin-bottom:14px; letter-spacing:1px; }
  .overlay p { font-size:0.85em; color:#c9c9d2; line-height:1.5em; margin-bottom:10px; max-width:340px; }
  .btn {
    margin-top:14px; padding:12px 30px; background:linear-gradient(180deg,#ff6a3c,#c23a12);
    border:2px solid #ffd9b0; color:#fff; font-weight:bold; letter-spacing:2px; font-size:0.95em;
    border-radius:6px; cursor:pointer; box-shadow:0 0 16px rgba(255,90,40,0.55);
  }
  .btn:active { transform:scale(0.96); }
  .tag { font-size:0.7em; color:#8a8a93; letter-spacing:1px; margin-top:18px; }
  .sectorPill {
    display:inline-block; padding:4px 12px; border:1px solid #ff6a3c; border-radius:20px;
    color:#ff6a3c; font-size:0.7em; letter-spacing:1px; margin-bottom:10px;
  }
</style>
</head>
<body>
<div id="gameWrap">
  <canvas id="game"></canvas>
  <div id="reloadBtn">RELOAD</div>

  <div class="overlay" id="startOverlay">
    <div class="sectorPill">28 CHAPTERS · 4 SECTORS</div>
    <h1>CHRONO CRISIS</h1>
    <h2>TACTICAL ENFORCEMENT</h2>
    <p>Elite response unit "Vanguard-7" is deployed downtown. Tap or click hostiles before their
    Threat Ring hits zero. Watch your ammo — 6 rounds per clip. Protect your 5-point life gauge
    across all 4 sectors.</p>
    <p style="font-size:0.75em;color:#8a8a93;">PC: left-click to shoot, right-click to reload.<br>
    Mobile: tap to shoot, tap RELOAD to refresh your clip.</p>
    <div class="btn" id="startBtn">START MISSION</div>
    <div class="tag">VANGUARD-7 TACTICAL DIVISION</div>
  </div>

  <div class="overlay" id="chapterOverlay" style="display:none;">
    <div class="sectorPill" id="sectorLabel">SECTOR 1</div>
    <h1 id="chapterTitle" style="font-size:1.2em;">CHAPTER</h1>
    <h2 id="chapterObjective" style="font-size:0.85em;font-weight:normal;">Objective</h2>
    <div class="btn" id="beginBtn">BEGIN</div>
  </div>

  <div class="overlay" id="failOverlay" style="display:none;">
    <h1>MISSION FAILED</h1>
    <p id="failStats">Vanguard-7 unit down.</p>
    <div class="btn" id="retryBtn">RETRY CAMPAIGN</div>
  </div>

  <div class="overlay" id="winOverlay" style="display:none;">
    <h1>MISSION ACCOMPLISHED</h1>
    <h2>All 28 chapters cleared</h2>
    <p id="winStats">Final score: 0</p>
    <div class="btn" id="playAgainBtn">PLAY AGAIN</div>
  </div>
</div>

<script>
(function(){

/* =========================================================
   AUDIO ENGINE — fully synthesized, zero external files
========================================================= */
let actx = null;
function ensureAudio(){
  if(!actx){ actx = new (window.AudioContext || window.webkitAudioContext)(); }
  if(actx.state === 'suspended'){ actx.resume(); }
}

function playGunshot(){
  ensureAudio();
  const t = actx.currentTime;
  const bufSize = Math.floor(actx.sampleRate * 0.15);
  const buffer = actx.createBuffer(1, bufSize, actx.sampleRate);
  const data = buffer.getChannelData(0);
  for(let i=0;i<bufSize;i++){ data[i] = (Math.random()*2-1) * Math.pow(1-i/bufSize, 2); }
  const noise = actx.createBufferSource();
  noise.buffer = buffer;
  const noiseGain = actx.createGain();
  noiseGain.gain.setValueAtTime(0.9, t);
  noiseGain.gain.exponentialRampToValueAtTime(0.001, t+0.15);
  noise.connect(noiseGain).connect(actx.destination);
  noise.start(t); noise.stop(t+0.16);

  const osc = actx.createOscillator();
  osc.type = 'sawtooth';
  osc.frequency.setValueAtTime(900, t);
  osc.frequency.exponentialRampToValueAtTime(80, t+0.12);
  const oscGain = actx.createGain();
  oscGain.gain.setValueAtTime(0.7, t);
  oscGain.gain.exponentialRampToValueAtTime(0.001, t+0.13);
  osc.connect(oscGain).connect(actx.destination);
  osc.start(t); osc.stop(t+0.14);
}

function playReload(){
  ensureAudio();
  const t = actx.currentTime;
  [1200, 1850].forEach((f,i)=>{
    const osc = actx.createOscillator();
    osc.type = 'square';
    osc.frequency.setValueAtTime(f, t + i*0.08);
    const g = actx.createGain();
    g.gain.setValueAtTime(0.22, t + i*0.08);
    g.gain.exponentialRampToValueAtTime(0.001, t + i*0.08 + 0.09);
    osc.connect(g).connect(actx.destination);
    osc.start(t + i*0.08); osc.stop(t + i*0.08 + 0.1);
  });
}

function playWarningBleep(intensity){
  ensureAudio();
  const t = actx.currentTime;
  const osc = actx.createOscillator();
  osc.type = 'sine';
  osc.frequency.setValueAtTime(650 + intensity*550, t);
  const g = actx.createGain();
  g.gain.setValueAtTime(0.001, t);
  g.gain.linearRampToValueAtTime(0.16, t+0.02);
  g.gain.exponentialRampToValueAtTime(0.001, t+0.09);
  osc.connect(g).connect(actx.destination);
  osc.start(t); osc.stop(t+0.1);
}

function playEmptyClick(){
  ensureAudio();
  const t = actx.currentTime;
  const osc = actx.createOscillator();
  osc.type = 'square'; osc.frequency.setValueAtTime(190, t);
  const g = actx.createGain();
  g.gain.setValueAtTime(0.14, t); g.gain.exponentialRampToValueAtTime(0.001, t+0.05);
  osc.connect(g).connect(actx.destination); osc.start(t); osc.stop(t+0.06);
}

function playHeartLoss(){
  ensureAudio();
  const t = actx.currentTime;
  const osc = actx.createOscillator();
  osc.type = 'triangle';
  osc.frequency.setValueAtTime(220, t);
  osc.frequency.exponentialRampToValueAtTime(70, t+0.35);
  const g = actx.createGain();
  g.gain.setValueAtTime(0.3, t); g.gain.exponentialRampToValueAtTime(0.001, t+0.4);
  osc.connect(g).connect(actx.destination); osc.start(t); osc.stop(t+0.4);
}

let bgTimer = null, bgStep = 0;
function startBgBeat(){
  ensureAudio();
  if(bgTimer) return;
  bgTimer = setInterval(()=>{
    const t = actx.currentTime;
    if(bgStep % 2 === 0){
      const osc = actx.createOscillator();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(120, t);
      osc.frequency.exponentialRampToValueAtTime(38, t+0.15);
      const g = actx.createGain();
      g.gain.setValueAtTime(0.32, t); g.gain.exponentialRampToValueAtTime(0.001, t+0.16);
      osc.connect(g).connect(actx.destination); osc.start(t); osc.stop(t+0.17);
    }
    const bufSize = Math.floor(actx.sampleRate * 0.03);
    const buffer = actx.createBuffer(1, bufSize, actx.sampleRate);
    const data = buffer.getChannelData(0);
    for(let i=0;i<bufSize;i++){ data[i] = (Math.random()*2-1) * 0.18; }
    const src = actx.createBufferSource(); src.buffer = buffer;
    const hg = actx.createGain();
    hg.gain.setValueAtTime(0.1, t); hg.gain.exponentialRampToValueAtTime(0.001, t+0.03);
    src.connect(hg).connect(actx.destination); src.start(t);

    if(bgStep % 4 === 2){
      const notes = [55, 58, 49, 55];
      const osc = actx.createOscillator();
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(notes[Math.floor(bgStep/4) % notes.length], t);
      const filt = actx.createBiquadFilter();
      filt.type = 'lowpass'; filt.frequency.setValueAtTime(420, t);
      const g = actx.createGain();
      g.gain.setValueAtTime(0.001, t);
      g.gain.linearRampToValueAtTime(0.22, t+0.02);
      g.gain.exponentialRampToValueAtTime(0.001, t+0.35);
      osc.connect(filt).connect(g).connect(actx.destination);
      osc.start(t); osc.stop(t+0.36);
    }
    bgStep++;
  }, 240);
}
function stopBgBeat(){ if(bgTimer){ clearInterval(bgTimer); bgTimer = null; bgStep = 0; } }

/* =========================================================
   28-CHAPTER CAMPAIGN DATABASE
========================================================= */
const SECTOR_DEFS = [
  { name:"Downtown Bank Heist & Highway Pursuit", seed:"downtown", range:[1,7],
    subtitles:["Vault Breach","Lobby Standoff","Rooftop Exfil","Getaway Alley","Overpass Ambush","Tollbooth Blockade","Highway Convoy Strike"],
    objectives:[
      "Neutralize the heist crew before they crack the vault.",
      "Clear hostiles from the bank lobby without civilian casualties.",
      "Secure the rooftop extraction point.",
      "Pursue the getaway crew through the back alleys.",
      "Hold the overpass against incoming reinforcements.",
      "Break through the tollbooth blockade.",
      "Take down the armored convoy on the highway."
    ]},
  { name:"Industrial Subway Yards & Dockside Warehouses", seed:"industrial", range:[8,14],
    subtitles:["Yard Infiltration","Freight Car Sweep","Signal Tower Assault","Warehouse Breach","Container Maze","Crane Bay Firefight","Dock Perimeter Lockdown"],
    objectives:[
      "Infiltrate the abandoned subway yard.",
      "Sweep the freight cars for hidden gunmen.",
      "Take the signal tower and cut enemy comms.",
      "Breach the dockside warehouse.",
      "Clear the shipping container maze.",
      "Fight through the crane bay.",
      "Lock down the dock perimeter."
    ]},
  { name:"Corporate Penthouse Skyscraper Raid", seed:"skyscraper", range:[15,21],
    subtitles:["Lobby Checkpoint","Elevator Shaft Ambush","Executive Floor Sweep","Server Room Defense","Boardroom Standoff","Rooftop Helipad","Penthouse Showdown"],
    objectives:[
      "Push past the lobby checkpoint.",
      "Survive the elevator shaft ambush.",
      "Sweep the executive floor.",
      "Defend the server room from sabotage.",
      "Clear the boardroom of hostiles.",
      "Secure the rooftop helipad.",
      "Storm the penthouse suite."
    ]},
  { name:"Cyber-Command Control & Mastermind Bunkers", seed:"bunker", range:[22,28],
    subtitles:["Command Deck Breach","Reactor Corridor","Data Vault Sweep","Bunker Checkpoint","Inner Sanctum","Mastermind's Gauntlet","Final Countdown"],
    objectives:[
      "Breach the cyber-command deck.",
      "Push through the reactor corridor.",
      "Sweep the data vault for saboteurs.",
      "Clear the bunker checkpoint.",
      "Fight into the inner sanctum.",
      "Survive the mastermind's gauntlet.",
      "Stop the final countdown."
    ]}
];

function seededRandom(seed){
  let s = seed % 2147483647; if(s<=0) s += 2147483646;
  return function(){ s = (s*16807) % 2147483647; return (s-1)/2147483646; };
}

function buildChapters(){
  const chapters = [];
  SECTOR_DEFS.forEach(sector=>{
    for(let n=sector.range[0]; n<=sector.range[1]; n++){
      const localIdx = n - sector.range[0];
      const rand = seededRandom(n*97 + 13);
      const spawnCount = 5 + (n % 4);
      const spawns = [];
      const kinds = ["roof edge","behind a car","doorway","crate stack","support pillar"];
      for(let i=0;i<spawnCount;i++){
        spawns.push({
          x: 0.08 + rand()*0.84,
          y: 0.30 + rand()*0.48,
          kind: kinds[Math.floor(rand()*kinds.length)]
        });
      }
      chapters.push({
        num: n,
        sectorIdx: SECTOR_DEFS.indexOf(sector),
        sectorName: sector.name,
        title: "CHAPTER " + n + " — " + sector.subtitles[localIdx],
        objective: sector.objectives[localIdx],
        bg: "https://picsum.photos/seed/chronocrisis-" + sector.seed + "-" + n + "/900/1200",
        spawns: spawns,
        enemiesRequired: 6 + Math.floor(n/5)
      });
    }
  });
  return chapters;
}
const CHAPTERS = buildChapters();

/* =========================================================
   CANVAS / RENDER SETUP
========================================================= */
const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');
const wrap = document.getElementById('gameWrap');
let CW = 460, CH = 613;

function resize(){
  const rect = wrap.getBoundingClientRect();
  CW = rect.width; CH = rect.height;
  const dpr = window.devicePixelRatio || 1;
  canvas.width = Math.floor(CW * dpr);
  canvas.height = Math.floor(CH * dpr);
  canvas.style.width = CW + 'px';
  canvas.style.height = CH + 'px';
  ctx.setTransform(dpr,0,0,dpr,0,0);
}
window.addEventListener('resize', resize);
resize();

/* =========================================================
   GAME STATE
========================================================= */
const state = {
  screen: 'start',
  chapterIdx: 0,
  ammo: 6, maxAmmo: 6,
  hearts: 5, maxHearts: 5,
  score: 0,
  enemiesDefeated: 0,
  enemies: [],
  decals: [],
  flashTimer: 0,
  shakeTimer: 0,
  bgImage: null,
  bgLoaded: false,
  lastSpawn: 0,
  spawnInterval: 1500,
};

function loadChapterBg(){
  const ch = CHAPTERS[state.chapterIdx];
  const img = new Image();
  img.crossOrigin = 'anonymous';
  state.bgLoaded = false; state.bgImage = null;
  img.onload = ()=>{ state.bgImage = img; state.bgLoaded = true; };
  img.onerror = ()=>{ state.bgImage = null; state.bgLoaded = false; };
  img.src = ch.bg;
}

function startChapter(idx){
  state.chapterIdx = idx;
  state.enemies = [];
  state.decals = [];
  state.enemiesDefeated = 0;
  state.spawnInterval = Math.max(650, 1500 - idx*28);
  loadChapterBg();
  showChapterOverlay();
}

function showChapterOverlay(){
  const ch = CHAPTERS[state.chapterIdx];
  const sectorNum = ch.sectorIdx + 1;
  document.getElementById('sectorLabel').textContent = "SECTOR " + sectorNum + " OF 4";
  document.getElementById('chapterTitle').textContent = ch.title;
  document.getElementById('chapterObjective').textContent = ch.objective;
  state.screen = 'chapterIntro';
  document.getElementById('chapterOverlay').style.display = 'flex';
}

function beginChapterPlay(){
  document.getElementById('chapterOverlay').style.display = 'none';
  state.screen = 'playing';
  state.lastSpawn = performance.now() - state.spawnInterval + 300;
  startBgBeat();
}

function spawnEnemy(){
  const ch = CHAPTERS[state.chapterIdx];
  const point = ch.spawns[Math.floor(Math.random()*ch.spawns.length)];
  const baseThreat = Math.max(1600, 3400 - state.chapterIdx*35);
  state.enemies.push({
    id: Math.random().toString(36).slice(2),
    x: point.x * CW,
    y: point.y * CH,
    r: 24 + Math.random()*7,
    spawnTime: performance.now(),
    threatTime: baseThreat,
    lastBleep: 0,
    bob: Math.random()*Math.PI*2
  });
}

function spawnDecal(x, y, hit){
  state.decals.push({ x, y, hit, t: 0, life: hit ? 550 : 900 });
}

function triggerShake(){ state.shakeTimer = 260; }

function enemyBreach(){
  state.hearts--;
  state.flashTimer = 320;
  triggerShake();
  playHeartLoss();
  if(state.hearts <= 0){ missionFailed(); }
}

function checkChapterComplete(){
  const ch = CHAPTERS[state.chapterIdx];
  if(state.enemiesDefeated >= ch.enemiesRequired){
    if(state.chapterIdx + 1 < CHAPTERS.length){
      startChapter(state.chapterIdx + 1);
    } else {
      missionWin();
    }
  }
}

function missionFailed(){
  state.screen = 'failed';
  stopBgBeat();
  document.getElementById('failStats').textContent =
    "Cleared " + (state.chapterIdx+1) + " of 28 chapters · Score " + state.score;
  document.getElementById('failOverlay').style.display = 'flex';
}

function missionWin(){
  state.screen = 'win';
  stopBgBeat();
  document.getElementById('winStats').textContent = "Final score: " + state.score;
  document.getElementById('winOverlay').style.display = 'flex';
}

function resetCampaign(){
  state.ammo = state.maxAmmo;
  state.hearts = state.maxHearts;
  state.score = 0;
  document.getElementById('failOverlay').style.display = 'none';
  document.getElementById('winOverlay').style.display = 'none';
  startChapter(0);
}

/* =========================================================
   INPUT
========================================================= */
function flashReloadBtn(){
  const b = document.getElementById('reloadBtn');
  b.classList.remove('flash'); void b.offsetWidth; b.classList.add('flash');
}

function handleShot(cx, cy){
  if(state.screen !== 'playing') return;
  if(state.ammo <= 0){ playEmptyClick(); flashReloadBtn(); return; }
  state.ammo--;
  playGunshot();
  let hit = false;
  for(let i=state.enemies.length-1; i>=0; i--){
    const e = state.enemies[i];
    const dx = cx - e.x, dy = cy - e.y;
    if(Math.sqrt(dx*dx + dy*dy) <= e.r + 10){
      hit = true;
      state.score += 100;
      state.enemiesDefeated++;
      state.enemies.splice(i,1);
      spawnDecal(cx, cy, true);
      break;
    }
  }
  if(!hit){ spawnDecal(cx, cy, false); }
  checkChapterComplete();
}

function doReload(){
  if(state.screen !== 'playing') return;
  if(state.ammo === state.maxAmmo) return;
  playReload();
  state.ammo = state.maxAmmo;
}

canvas.addEventListener('contextmenu', (e)=>{ e.preventDefault(); doReload(); });

canvas.addEventListener('pointerdown', (e)=>{
  if(e.button === 2) return;
  ensureAudio();
  const rect = canvas.getBoundingClientRect();
  const cx = e.clientX - rect.left;
  const cy = e.clientY - rect.top;
  handleShot(cx, cy);
});

document.getElementById('reloadBtn').addEventListener('pointerdown', (e)=>{
  e.stopPropagation();
  ensureAudio();
  doReload();
});

document.getElementById('startBtn').addEventListener('pointerdown', ()=>{
  ensureAudio();
  document.getElementById('startOverlay').style.display = 'none';
  startChapter(0);
});
document.getElementById('beginBtn').addEventListener('pointerdown', ()=>{
  ensureAudio();
  beginChapterPlay();
});
document.getElementById('retryBtn').addEventListener('pointerdown', ()=>{
  ensureAudio();
  resetCampaign();
});
document.getElementById('playAgainBtn').addEventListener('pointerdown', ()=>{
  ensureAudio();
  resetCampaign();
});

/* =========================================================
   RENDER HELPERS
========================================================= */
function drawBackground(){
  if(state.bgLoaded && state.bgImage){
    const img = state.bgImage;
    const scale = Math.max(CW/img.width, CH/img.height);
    const dw = img.width*scale, dh = img.height*scale;
    const dx = (CW-dw)/2, dy = (CH-dh)/2;
    ctx.drawImage(img, dx, dy, dw, dh);
    ctx.fillStyle = 'rgba(5,5,10,0.35)';
    ctx.fillRect(0,0,CW,CH);
  } else {
    const g = ctx.createLinearGradient(0,0,0,CH);
    g.addColorStop(0, '#1a1c22');
    g.addColorStop(1, '#050507');
    ctx.fillStyle = g;
    ctx.fillRect(0,0,CW,CH);
  }
}

function ringColor(ratio){
  if(ratio > 0.55){
    const p = (ratio-0.55)/0.45;
    return "rgb(" + Math.floor(255-(255-40)*p) + "," + 220 + "," + Math.floor(60*p) + ")";
  } else if(ratio > 0.25){
    const p = (ratio-0.25)/0.30;
    return "rgb(255," + Math.floor(220*p + 30) + ",30)";
  } else {
    const flick = 0.5 + 0.5*Math.sin(performance.now()/70);
    return "rgb(255," + Math.floor(40*flick) + ",30)";
  }
}

function drawEnemy(e, now){
  const elapsed = now - e.spawnTime;
  const ratio = Math.max(0, 1 - elapsed/e.threatTime);
  const bob = Math.sin(now/220 + e.bob) * 2;
  const x = e.x, y = e.y + bob;

  if(ratio < 0.5){
    const interval = 180 + ratio*500;
    if(now - e.lastBleep > interval){ playWarningBleep(1-ratio); e.lastBleep = now; }
  }

  ctx.save();
  ctx.translate(x, y);

  ctx.fillStyle = 'rgba(10,10,14,0.92)';
  ctx.beginPath();
  ctx.arc(0, -e.r*0.55, e.r*0.42, 0, Math.PI*2);
  ctx.fill();
  ctx.beginPath();
  ctx.moveTo(-e.r*0.55, e.r*0.55);
  ctx.quadraticCurveTo(-e.r*0.65, -e.r*0.1, -e.r*0.28, -e.r*0.32);
  ctx.lineTo(e.r*0.28, -e.r*0.32);
  ctx.quadraticCurveTo(e.r*0.65, -e.r*0.1, e.r*0.55, e.r*0.55);
  ctx.closePath();
  ctx.fill();

  const glow = 0.6 + 0.4*Math.sin(now/150);
  ctx.shadowColor = 'rgba(255,40,40,0.9)';
  ctx.shadowBlur = 8*glow;
  ctx.fillStyle = 'rgba(255,30,30,' + (0.8+0.2*glow) + ')';
  ctx.beginPath(); ctx.ellipse(-e.r*0.18, -e.r*0.58, e.r*0.13, e.r*0.07, 0, 0, Math.PI*2); ctx.fill();
  ctx.beginPath(); ctx.ellipse(e.r*0.18, -e.r*0.58, e.r*0.13, e.r*0.07, 0, 0, Math.PI*2); ctx.fill();
  ctx.shadowBlur = 0;

  ctx.restore();

  ctx.save();
  ctx.translate(x, y);
  ctx.lineWidth = 3.5;
  ctx.strokeStyle = ringColor(ratio);
  ctx.beginPath();
  ctx.arc(0, 0, e.r + 12, -Math.PI/2, -Math.PI/2 + Math.PI*2*ratio);
  ctx.stroke();
  ctx.lineWidth = 1;
  ctx.strokeStyle = 'rgba(255,255,255,0.25)';
  ctx.beginPath(); ctx.arc(0,0,e.r+12,0,Math.PI*2); ctx.stroke();
  ctx.restore();

  if(ratio <= 0){ return true; }
  return false;
}

function drawDecals(dt){
  for(let i=state.decals.length-1; i>=0; i--){
    const d = state.decals[i];
    d.t += dt;
    const a = Math.max(0, 1 - d.t/d.life);
    if(a <= 0){ state.decals.splice(i,1); continue; }
    ctx.save();
    ctx.globalAlpha = a;
    if(d.hit){
      ctx.strokeStyle = '#ffdca0';
      ctx.lineWidth = 2;
      ctx.beginPath(); ctx.arc(d.x, d.y, 14, 0, Math.PI*2); ctx.stroke();
      for(let k=0;k<5;k++){
        const ang = k*(Math.PI*2/5) + d.t/200;
        ctx.beginPath();
        ctx.moveTo(d.x, d.y);
        ctx.lineTo(d.x + Math.cos(ang)*20, d.y + Math.sin(ang)*20);
        ctx.stroke();
      }
    } else {
      ctx.fillStyle = 'rgba(20,20,20,0.85)';
      ctx.beginPath(); ctx.arc(d.x, d.y, 4.5, 0, Math.PI*2); ctx.fill();
      ctx.strokeStyle = 'rgba(0,0,0,0.6)';
      ctx.lineWidth = 1.2;
      for(let k=0;k<4;k++){
        const ang = k*(Math.PI/2) + 0.4;
        ctx.beginPath();
        ctx.moveTo(d.x, d.y);
        ctx.lineTo(d.x + Math.cos(ang)*8, d.y + Math.sin(ang)*8);
        ctx.stroke();
      }
    }
    ctx.restore();
  }
}

function drawHUD(){
  const ch = CHAPTERS[state.chapterIdx];

  ctx.save();
  ctx.fillStyle = 'rgba(0,0,0,0.45)';
  ctx.fillRect(0,0,CW,46);
  ctx.font = '600 12px Courier New';
  ctx.fillStyle = '#ffd9b0';
  ctx.textBaseline = 'middle';
  ctx.fillText(ch.title, 10, 16);
  ctx.font = '10px Courier New';
  ctx.fillStyle = '#c9c9d2';
  ctx.fillText(ch.objective, 10, 34);
  ctx.restore();

  for(let i=0;i<state.maxHearts;i++){
    const x = 12 + i*20, y = CH - 26;
    ctx.beginPath();
    const filled = i < state.hearts;
    ctx.fillStyle = filled ? '#ff3b4e' : 'rgba(255,255,255,0.15)';
    drawHeartPath(x, y, 8);
    ctx.fill();
  }

  const ammoX = CW - 12;
  for(let i=0;i<state.maxAmmo;i++){
    const x = ammoX - i*14, y = CH - 26;
    ctx.fillStyle = i < state.ammo ? '#ffd23f' : 'rgba(255,255,255,0.15)';
    ctx.fillRect(x-4, y-9, 6, 18);
  }

  ctx.save();
  ctx.font = '600 12px Courier New';
  ctx.fillStyle = '#f2f2f2';
  ctx.textAlign = 'center';
  ctx.fillText('SCORE ' + state.score, CW/2, CH - 24);
  ctx.restore();
}

function drawHeartPath(x, y, s){
  ctx.beginPath();
  ctx.moveTo(x, y+s*0.3);
  ctx.bezierCurveTo(x, y, x-s, y, x-s, y+s*0.3);
  ctx.bezierCurveTo(x-s, y+s*0.7, x, y+s*0.9, x, y+s*1.2);
  ctx.bezierCurveTo(x, y+s*0.9, x+s, y+s*0.7, x+s, y+s*0.3);
  ctx.bezierCurveTo(x+s, y, x, y, x, y+s*0.3);
  ctx.closePath();
}

/* =========================================================
   MAIN LOOP
========================================================= */
let lastTs = performance.now();
function loop(ts){
  const dt = ts - lastTs;
  lastTs = ts;

  let shakeX = 0, shakeY = 0;
  if(state.shakeTimer > 0){
    state.shakeTimer -= dt;
    const p = Math.max(0, state.shakeTimer/260);
    shakeX = (Math.random()*2-1) * 6 * p;
    shakeY = (Math.random()*2-1) * 6 * p;
  }

  ctx.save();
  ctx.clearRect(0,0,CW,CH);
  ctx.translate(shakeX, shakeY);

  drawBackground();

  if(state.screen === 'playing'){
    if(ts - state.lastSpawn > state.spawnInterval && state.enemies.length < 6){
      spawnEnemy();
      state.lastSpawn = ts;
    }
    for(let i=state.enemies.length-1; i>=0; i--){
      const breached = drawEnemy(state.enemies[i], ts);
      if(breached){
        state.enemies.splice(i,1);
        enemyBreach();
      }
    }
  } else if(state.enemies.length){
    for(let i=0;i<state.enemies.length;i++){ drawEnemy(state.enemies[i], ts); }
  }

  drawDecals(dt);

  if(state.screen === 'playing' || state.screen === 'failed'){
    drawHUD();
  }

  if(state.flashTimer > 0){
    state.flashTimer -= dt;
    const a = Math.max(0, state.flashTimer/320);
    ctx.fillStyle = 'rgba(255,255,255,' + (a*0.55) + ')';
    ctx.fillRect(0,0,CW,CH);
    ctx.strokeStyle = 'rgba(255,20,20,' + (a*0.9) + ')';
    ctx.lineWidth = 18;
    ctx.strokeRect(0,0,CW,CH);
  }

  ctx.restore();
  requestAnimationFrame(loop);
}
requestAnimationFrame(loop);

})();
</script>
</body>
</html>
"""

components.html(GAME_HTML, height=760, scrolling=False)

with st.expander("Mission Briefing & Controls"):
    st.markdown(
        """
- **PC:** Left-click hostiles to shoot. Right-click anywhere on the screen to reload.
- **Mobile:** Tap hostiles to shoot. Tap the **RELOAD** button to refresh your clip.
- Every hostile spawns with a **Threat Ring** — it shrinks and shifts from green to yellow to
  flashing red. If it empties before you drop them, you take 1 HP of damage.
- You carry a 6-round tactical magazine and a 5-point life gauge.
- Clear all **28 chapters** across **4 sectors** — Downtown, Industrial Docks, Skyscraper Raid,
  and the Cyber-Command Bunkers — to complete the campaign.
- All audio is generated live in your browser with the Web Audio API — no sound files required.
        """
    )
