import streamlit as st
import streamlit.components.v1 as components
import random

st.set_page_config(page_title="Virtua Tactical: Hampi Jericho Ops", layout="centered")
st.title("Virtua Tactical: Hampi Jericho Chronicles")

# Base HTML layout initialization
game_html = '''
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
    body { margin: 0; padding: 0; font-family: 'Segoe UI', Arial, sans-serif; user-select: none; -webkit-user-select: none; background: #05070d; }

    #gameArea {
        position: relative; width: 420px; height: 520px;
        background: #05070d; border: 1px solid #1e293b; overflow: hidden;
        margin: auto; border-radius: 14px; touch-action: none;
        box-shadow: 0 30px 70px rgba(0,0,0,0.9), inset 0 0 120px rgba(0,0,0,0.6);
        cursor: crosshair;
    }
    /* subtle grain + vignette so the map does not look flat */
    #gameArea::after {
        content: ''; position: absolute; inset: 0; pointer-events: none; z-index: 28;
        background:
            radial-gradient(120% 100% at 50% 40%, transparent 55%, rgba(0,0,0,0.55) 100%),
            url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 120 120'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='3'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.05'/%3E%3C/svg%3E");
        background-size: cover, 180px 180px; transition: background-color 0.1s;
    }
    #gameArea.taking-damage::after { background-color: rgba(200, 20, 20, 0.28); box-shadow: inset 0 0 130px rgba(200,0,0,0.95); }
    #gameArea.critical-pulse::after { animation: lowHp 0.55s ease-in-out infinite alternate; }
    @keyframes lowHp {
        0% { box-shadow: inset 0 0 80px rgba(150,0,0,0.55); }
        100% { box-shadow: inset 0 0 150px rgba(255,0,0,0.9); }
    }

    canvas { position: absolute; top: 0; left: 0; width: 420px; height: 520px; z-index: 1; }

    /* ---------- REALISTIC PISTOL (bottom-right, first person) ---------- */
    #weapon {
        position: absolute; bottom: -8px; right: 4px; width: 210px; height: 250px;
        pointer-events: none; z-index: 25; display: none;
        transform-origin: 78% 100%; will-change: transform;
        filter: drop-shadow(-8px -6px 14px rgba(0,0,0,0.7));
    }
    .gun { position: absolute; }
    /* the hand / grip the player holds */
    .g-grip {
        bottom: 0; right: 8px; width: 78px; height: 150px;
        background: linear-gradient(105deg, #16181c 0%, #2b2f36 45%, #101216 100%);
        border-radius: 14px 30px 22px 30px;
        transform: rotate(18deg);
        box-shadow: inset 3px 3px 6px rgba(255,255,255,0.08), inset -4px -4px 8px rgba(0,0,0,0.7);
    }
    /* grip stippling / texture */
    .g-grip::before {
        content: ''; position: absolute; inset: 14px 12px 40px 14px; border-radius: 10px;
        background-image: radial-gradient(rgba(255,255,255,0.10) 1px, transparent 1.4px);
        background-size: 7px 7px; opacity: 0.6;
    }
    /* frame body */
    .g-frame {
        bottom: 118px; right: 26px; width: 150px; height: 46px;
        background: linear-gradient(180deg, #3a3f47 0%, #23262c 55%, #0e1013 100%);
        border-radius: 8px 6px 6px 10px; transform: rotate(-9deg);
        box-shadow: inset 0 2px 3px rgba(255,255,255,0.14), inset 0 -4px 6px rgba(0,0,0,0.7);
    }
    /* slide on top of frame with serrations */
    .g-slide {
        bottom: 150px; right: 22px; width: 168px; height: 40px;
        background: linear-gradient(180deg, #4a505a 0%, #2c3037 50%, #14161a 100%);
        border-radius: 7px 7px 4px 8px; transform: rotate(-9deg);
        box-shadow: inset 0 3px 4px rgba(255,255,255,0.20), 0 3px 6px rgba(0,0,0,0.6);
    }
    .g-slide::after {
        content: ''; position: absolute; top: 8px; left: 8px; width: 42px; height: 24px;
        background: repeating-linear-gradient(90deg, #0c0e11 0 3px, #2b2f36 3px 6px);
        border-radius: 2px; opacity: 0.9;
    }
    /* front + rear iron sights */
    .g-sight-front { bottom: 190px; right: 30px; width: 6px; height: 12px; background: #0a0b0d; border-radius: 2px; transform: rotate(-9deg); }
    .g-sight-rear  { bottom: 188px; right: 168px; width: 14px; height: 12px; background: #0a0b0d; border-radius: 2px 2px 0 0; transform: rotate(-9deg); }
    .g-dot { bottom: 191px; right: 33px; width: 3px; height: 3px; border-radius: 50%; background: #22e0a1; box-shadow: 0 0 5px #22e0a1; }
    /* trigger guard */
    .g-guard {
        bottom: 96px; right: 96px; width: 46px; height: 40px;
        border: 7px solid #1a1d22; border-top: none; border-radius: 0 0 22px 22px;
        transform: rotate(-9deg);
    }
    /* muzzle position marker (barrel end, upper-left of gun) */
    #muzzle { bottom: 176px; right: 176px; width: 10px; height: 10px; }

    #flash {
        position: absolute; width: 66px; height: 66px;
        background: radial-gradient(circle, #fffdf0 12%, #ffd257 34%, #ff7a18 60%, transparent 78%);
        border-radius: 50%; display: none; z-index: 26;
        filter: drop-shadow(0 0 16px #ff9d33); transform: translate(-50%,-50%);
    }
    #flash .spike { position:absolute; top:50%; left:50%; width:80px; height:6px; background:linear-gradient(90deg,transparent,#ffd257,transparent); transform:translate(-50%,-50%); }
    #flash .spike.v { transform:translate(-50%,-50%) rotate(90deg); }

    .target-ring {
        position: absolute; border: 2.5px dashed #ff2f5e; border-radius: 50%;
        pointer-events: none; z-index: 10; transform: translate(-50%, -50%);
        box-shadow: 0 0 12px #ff2f5e; opacity: 0; transition: opacity 0.12s ease;
    }
    #sight {
        position: absolute; width: 34px; height: 34px; pointer-events: none;
        transform: translate(-50%, -50%); z-index: 20; display: none;
    }
    #sight::before, #sight::after { content:''; position:absolute; background:#00f0ff; box-shadow:0 0 6px #00f0ff; }
    #sight::before { top:50%; left:0; width:100%; height:2px; transform:translateY(-50%); }
    #sight::after  { left:50%; top:0; height:100%; width:2px; transform:translateX(-50%); }
    #sight .ringc { position:absolute; inset:6px; border:2px solid #00f0ff; border-radius:50%; box-shadow:0 0 8px #00f0ff; }

    #scoreCounter { position: absolute; top: 12px; left: 12px; color: #ffea00; font-weight: bold; font-family: 'Courier New', monospace; font-size: 22px; z-index: 30; background: rgba(0,0,0,0.85); padding: 4px 14px; border-radius: 6px; border: 1px solid #3f3f46; text-shadow: 0 0 6px #ffea00; display: none; }
    #chapterTxt { position: absolute; top: 12px; right: 12px; color: #e2e8f0; font-weight: bold; font-size: 11px; z-index: 30; background: rgba(0,0,0,0.85); padding: 6px 12px; border-radius: 6px; border: 1px solid #3f3f46; letter-spacing: 1px; display: none; }
    #targetTracker { position: absolute; top: 52px; right: 12px; color: #ff3366; font-weight: bold; font-family: monospace; font-size: 12px; z-index: 30; background: rgba(0,0,0,0.85); padding: 3px 8px; border-radius: 4px; display: none; }
    #healthWrap { position:absolute; bottom:14px; left:12px; z-index:30; display:none; }
    #healthBarBg { width:150px; height:14px; background:rgba(0,0,0,0.85); border:1px solid #ef4444; border-radius:7px; overflow:hidden; }
    #healthBar { height:100%; width:100%; background:linear-gradient(90deg,#f87171,#dc2626); transition:width 0.2s; }
    #healthLabel { color:#fca5a5; font-family:'Courier New',monospace; font-size:11px; font-weight:bold; margin-bottom:3px; text-shadow:0 0 4px #000; }

    #overScreen, #winScreen { position: absolute; inset: 0; background: rgba(2, 6, 23, 0.94); z-index: 40; display: none; flex-direction: column; align-items: center; justify-content: center; }
    .retry-btn, .win-btn { margin-top: 20px; padding: 10px 24px; background: #ef4444; color: white; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 13px; }
    .win-btn { background: #eab308; color: #020617; }
    #chapterOverlay { position: absolute; inset: 0; background: #000000; z-index: 49; display: flex; flex-direction: column; align-items: center; justify-content: center; }
    @keyframes flashPulse { 0% { opacity: 0.6; } 100% { opacity: 1; } }
</style>
</head>
<body>
    <div id="gameArea">
        <div id="chapterOverlay">
            <div style="color:white; font-family:monospace; font-size:18px; font-weight:bold; letter-spacing:3px;">CHAPTER 1</div>
            <div style="color:#64748b; font-family:sans-serif; font-size:11px; margin-top:5px; letter-spacing:1px;">PORT TERMINAL SANITIZATION</div>
        </div>

        <div id="tutorialPopup" style="position: absolute; top: 40%; left: 50%; transform: translate(-50%, -50%); color: #ff2266; font-family: monospace; font-size: 15px; font-weight: bold; background: rgba(0,0,0,0.85); border: 2px solid #ff2266; padding: 10px 16px; border-radius: 8px; z-index: 35; text-align: center; box-shadow: 0 0 15px rgba(255, 34, 102, 0.4); animation: flashPulse 1s infinite alternate; pointer-events: none; display:none;">
            AIM &amp; CLICK THE ENEMY TO FIRE
        </div>

        <div id="scoreCounter">00200</div>
        <div id="chapterTxt">CH 1: CONTAINER PORT</div>
        <div id="targetTracker">SECTOR A: 0/3</div>
        <div id="healthWrap">
            <div id="healthLabel">HP</div>
            <div id="healthBarBg"><div id="healthBar"></div></div>
        </div>

        <canvas id="gameCanvas" width="420" height="520"></canvas>
        <div id="sight"><div class="ringc"></div></div>

        <div id="weapon">
            <div class="gun g-guard"></div>
            <div class="gun g-grip"></div>
            <div class="gun g-frame"></div>
            <div class="gun g-slide"></div>
            <div class="gun g-sight-rear"></div>
            <div class="gun g-sight-front"></div>
            <div class="gun g-dot"></div>
            <div class="gun" id="muzzle"></div>
        </div>
        <div id="flash"><div class="spike"></div><div class="spike v"></div></div>

        <div id="overScreen">
            <div style="color:#ef4444; font-size:32px; font-weight:bold; text-shadow:0 0 12px #000; font-family:monospace; letter-spacing:1px;">MISSION FAILURE</div>
            <div id="finalScore" style="color:white; font-size:16px; margin-top:10px;">Final Score Log: 200</div>
            <button class="retry-btn" onclick="window.resetArcadeEngine(true)">REDEPLOY OPERATIVE</button>
        </div>

        <div id="winScreen">
            <div style="color:#eab308; font-size:28px; font-weight:bold; text-shadow: 0 0 12px #eab308;">CAMPAIGN SECURED</div>
            <div style="color:white; font-size:14px; text-align:center; margin-top:15px; max-width:320px; line-height:1.5;">EXCELLENT WORK JERICHO!<br>All terminals cleared successfully.</div>
            <button class="win-btn" onclick="window.resetArcadeEngine(true)">REPLAY CAMPAIGN</button>
        </div>
    </div>
<script>
    const CW = 420, CH = 520, HORIZON = 250, CX0 = 210;
    let currentX = CX0, currentY = HORIZON, score = 200, isOver = false;
    let threatsList = []; let playerHp = 100;
    let spawnTimerId = null, runLoopTimerId = null, heartbeatIntervalId = null;
    let audioCtx = null;
    let bloodParticles = []; let smokeParticles = [];

    let currentSector = "A"; let sectorKills = 0; let sectorClearing = false;
    const sectorsList = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"];
    const sectorRequirements = { "A":3, "B":3, "C":3, "D":3, "E":4, "F":4, "G":4, "H":4, "I":4, "J":5 };
    let isMoving = false;

    const canvas = document.getElementById("gameCanvas"); const ctx = canvas.getContext("2d");
    let cameraZ = 0, targetCameraZ = 0; let cameraX = 0, targetCameraX = 0; let cycleTick = 0;

    const gameArea = document.getElementById("gameArea");
    const weapon = document.getElementById("weapon");
    const sight = document.getElementById("sight");
    const scoreCounter = document.getElementById("scoreCounter");
    const chapterTxt = document.getElementById("chapterTxt");
    const targetTracker = document.getElementById("targetTracker");
    const healthBar = document.getElementById("healthBar");
    const overScreen = document.getElementById("overScreen");
    const winScreen = document.getElementById("winScreen");
    const finalScore = document.getElementById("finalScore");
    const flash = document.getElementById("flash");

    // Shipping containers positioned along the port. side:1 => right face visible, -1 => left face.
    const static3DObstacles = [
        { id: "c1", x: -2.1, y: 0.9, z: 15, baseColor: "#0f766e", topColor:"#134e4a", side: 1,  stack:true,  label:"HJX" },
        { id: "c2", x:  2.2, y: 0.9, z: 27, baseColor: "#b91c1c", topColor:"#7f1d1d", side:-1,  stack:false, label:"MRK" },
        { id: "c3", x: -2.0, y: 0.9, z: 41, baseColor: "#1d4ed8", topColor:"#1e3a8a", side: 1,  stack:true,  label:"COS" },
        { id: "c4", x:  2.1, y: 0.9, z: 55, baseColor: "#a16207", topColor:"#713f12", side:-1,  stack:false, label:"EVR" },
        { id: "c5", x: -2.2, y: 0.9, z: 69, baseColor: "#475569", topColor:"#1e293b", side: 1,  stack:true,  label:"UNK" }
    ];

    function setupAudio() {
        if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        if (audioCtx.state === "suspended") audioCtx.resume();
    }

    // ---------------- SOUND DESIGN ----------------
    function makeNoise(dur, decay) {
        const len = Math.floor(audioCtx.sampleRate * dur);
        const buf = audioCtx.createBuffer(1, len, audioCtx.sampleRate);
        const d = buf.getChannelData(0);
        for (let i = 0; i < len; i++) { d[i] = (Math.random()*2-1) * Math.pow(1 - i/len, decay); }
        const src = audioCtx.createBufferSource(); src.buffer = buf; return src;
    }

    // realistic layered pistol shot: sharp crack + body thump + mechanical click
    function gunshot() {
        setupAudio(); if (!audioCtx) return;
        const t = audioCtx.currentTime;

        const noise = makeNoise(0.25, 2.2);
        const bp = audioCtx.createBiquadFilter(); bp.type = "bandpass"; bp.frequency.value = 1700; bp.Q.value = 0.8;
        const hp = audioCtx.createBiquadFilter(); hp.type = "highpass"; hp.frequency.value = 380;
        const ng = audioCtx.createGain(); ng.gain.setValueAtTime(0.95, t); ng.gain.exponentialRampToValueAtTime(0.001, t + 0.2);
        noise.connect(bp); bp.connect(hp); hp.connect(ng); ng.connect(audioCtx.destination);
        noise.start(t); noise.stop(t + 0.25);

        const thump = audioCtx.createOscillator(); thump.type = "triangle";
        thump.frequency.setValueAtTime(170, t); thump.frequency.exponentialRampToValueAtTime(48, t + 0.13);
        const tg = audioCtx.createGain(); tg.gain.setValueAtTime(0.8, t); tg.gain.exponentialRampToValueAtTime(0.001, t + 0.16);
        thump.connect(tg); tg.connect(audioCtx.destination); thump.start(t); thump.stop(t + 0.17);

        const click = audioCtx.createOscillator(); click.type = "square"; click.frequency.setValueAtTime(2600, t);
        const cg = audioCtx.createGain(); cg.gain.setValueAtTime(0.22, t); cg.gain.exponentialRampToValueAtTime(0.001, t + 0.03);
        click.connect(cg); cg.connect(audioCtx.destination); click.start(t); click.stop(t + 0.04);
    }

    // synthesized human pained death shout (pitch/length randomised so it varies)
    function deathShout() {
        setupAudio(); if (!audioCtx) return;
        const t = audioCtx.currentTime;
        const base = 150 + Math.random() * 110;
        const dur = 0.45 + Math.random() * 0.3;

        const voice = audioCtx.createOscillator(); voice.type = "sawtooth";
        voice.frequency.setValueAtTime(base * 1.15, t);
        voice.frequency.linearRampToValueAtTime(base, t + 0.1);
        voice.frequency.linearRampToValueAtTime(base * 0.55, t + dur);

        const vib = audioCtx.createOscillator(); vib.frequency.value = 16 + Math.random()*8;
        const vibg = audioCtx.createGain(); vibg.gain.value = 14;
        vib.connect(vibg); vibg.connect(voice.frequency); vib.start(t); vib.stop(t + dur);

        const fmt = audioCtx.createBiquadFilter(); fmt.type = "bandpass"; fmt.frequency.value = 950; fmt.Q.value = 5;
        const vg = audioCtx.createGain();
        vg.gain.setValueAtTime(0.001, t);
        vg.gain.linearRampToValueAtTime(0.55, t + 0.05);
        vg.gain.setValueAtTime(0.5, t + dur * 0.55);
        vg.gain.exponentialRampToValueAtTime(0.001, t + dur);
        voice.connect(fmt); fmt.connect(vg); vg.connect(audioCtx.destination);
        voice.start(t); voice.stop(t + dur);

        // breathy grit layer
        const br = makeNoise(dur, 1.4);
        const brf = audioCtx.createBiquadFilter(); brf.type = "bandpass"; brf.frequency.value = 1400; brf.Q.value = 1.2;
        const brg = audioCtx.createGain(); brg.gain.setValueAtTime(0.18, t); brg.gain.exponentialRampToValueAtTime(0.001, t + dur);
        br.connect(brf); brf.connect(brg); brg.connect(audioCtx.destination); br.start(t); br.stop(t + dur);
    }

    function sound(type) {
        setupAudio(); if (!audioCtx) return;
        if (type === "shot") { gunshot(); return; }
        if (type === "shout") { deathShout(); return; }
        let osc = audioCtx.createOscillator(), gain = audioCtx.createGain(); osc.connect(gain); gain.connect(audioCtx.destination);
        if (type === "ding") { osc.type = "sine"; osc.frequency.setValueAtTime(950, audioCtx.currentTime); osc.frequency.linearRampToValueAtTime(1350, audioCtx.currentTime + 0.08); gain.gain.setValueAtTime(0.12, audioCtx.currentTime); osc.start(); osc.stop(audioCtx.currentTime + 0.08); }
        else if (type === "level") { osc.type = "sine"; osc.frequency.setValueAtTime(523.25, audioCtx.currentTime); osc.frequency.setValueAtTime(659.25, audioCtx.currentTime + 0.1); osc.frequency.setValueAtTime(783.99, audioCtx.currentTime + 0.2); gain.gain.setValueAtTime(0.2, audioCtx.currentTime); osc.start(); osc.stop(audioCtx.currentTime + 0.4); }
        else if (type === "bullet_crack") { osc.type = "sawtooth"; osc.frequency.setValueAtTime(190, audioCtx.currentTime); osc.frequency.linearRampToValueAtTime(30, audioCtx.currentTime + 0.12); gain.gain.setValueAtTime(0.28, audioCtx.currentTime); osc.start(); osc.stop(audioCtx.currentTime + 0.12); }
        else if (type === "heartbeat") { osc.type = "sine"; osc.frequency.setValueAtTime(60, audioCtx.currentTime); osc.frequency.exponentialRampToValueAtTime(25, audioCtx.currentTime + 0.18); gain.gain.setValueAtTime(0.4, audioCtx.currentTime); osc.start(); osc.stop(audioCtx.currentTime + 0.18); }
    }

    function project3D(x, y, z) {
        let relativeX = x - cameraX; let activePerspectiveZ = z - cameraZ;
        if (activePerspectiveZ <= 0.1) return null;
        let fovScale = 400 / activePerspectiveZ;
        return { x: CX0 + (relativeX * fovScale), y: HORIZON - ((y - 1.6) * fovScale), size: fovScale };
    }

    function spawn3DThreatUnit() {
        if (isOver || sectorClearing || isMoving) return;
        if (threatsList.filter(t => !t.isDying).length >= 2) return;
        if (winScreen.style.display === "flex" || document.getElementById("chapterOverlay").style.display === "flex") return;
        let idx = sectorsList.indexOf(currentSector); let spawnZ = cameraZ + 12 + (idx * 0.5); let spawnX = cameraX + (Math.random() * 2.6) - 1.3;
        let ring = document.createElement("div"); ring.className = "target-ring"; gameArea.appendChild(ring);
        threatsList.push({ x: spawnX, y: 0.2, z: spawnZ, age: 0, loopTick: Math.floor(Math.random()*60), isDying: false, deathTick: 0, deathDir: Math.random() < 0.5 ? -1 : 1, isFlashing: false, ring: ring, currentScreenX: 0, currentScreenY: 0, currentRadius: 24 });
        sound("ding");
    }

    function aim(e) {
        if (isOver || document.getElementById("chapterOverlay").style.display === "flex") return;
        let targetPoint = e;
        if (e.touches && e.touches.length > 0) { targetPoint = e.touches[0]; }
        else if (e.changedTouches && e.changedTouches.length > 0) { targetPoint = e.changedTouches[0]; }
        let bounds = gameArea.getBoundingClientRect();
        currentX = (targetPoint.clientX - bounds.left) * (CW / bounds.width);
        currentY = (targetPoint.clientY - bounds.top) * (CH / bounds.height);

        let mappedThreatZ = 12; threatsList.forEach(t => { if(!t.isDying) mappedThreatZ = t.z - cameraZ; });
        let dynamicallyAdjustedSize = Math.max(20, Math.min(64, (400 / mappedThreatZ) * 0.95));
        sight.style.width = dynamicallyAdjustedSize + "px"; sight.style.height = dynamicallyAdjustedSize + "px";
        sight.style.display = "block"; sight.style.left = currentX + "px"; sight.style.top = currentY + "px";

        // gun recoil-idle: aim toward the reticle from the corner
        let swayX = (currentX - CX0) / 26; let swayY = (currentY - HORIZON) / 40;
        weapon.style.transform = "rotate(" + swayX + "deg) translate(" + (swayX*1.4) + "px," + swayY + "px)";
    }

    gameArea.addEventListener("mousemove", aim);
    gameArea.addEventListener("touchmove", (e) => { e.preventDefault(); aim(e); }, { passive: false });

    function triggerMouseCoordinateFire(e) {
        setupAudio(); let bounds = gameArea.getBoundingClientRect();
        currentX = (e.clientX - bounds.left) * (CW / bounds.width);
        currentY = (e.clientY - bounds.top) * (CH / bounds.height);
        triggerFire();
    }
    gameArea.addEventListener("mousedown", (e) => { if(e.target.tagName !== "BUTTON") triggerMouseCoordinateFire(e); });
    gameArea.addEventListener("touchstart", (e) => { if(e.target.tagName !== "BUTTON") { e.preventDefault(); setupAudio(); aim(e); triggerFire(); } }, { passive: false });

    function triggerSectorPathMovement() {
        if (isMoving) return; isMoving = true; sectorClearing = false;
        let idx = sectorsList.indexOf(currentSector);
        if (idx >= 0 && idx < sectorsList.length - 1) {
            currentSector = sectorsList[idx + 1]; sectorKills = 0; targetCameraZ = (idx + 1) * 16;
            let roll = Math.random();
            targetCameraX = roll < 0.33 ? -1.6 : (roll < 0.66 ? 1.6 : 0.0);
            chapterTxt.innerText = ["E","F","G","H","I","J"].includes(currentSector) ? "CH 1: CARGO WATERFRONT" : "CH 1: CONTAINER PORT";
            document.getElementById("tutorialPopup").style.display = "none";
        } else {
            clearInterval(spawnTimerId); clearInterval(runLoopTimerId); isOver = true;
            if(heartbeatIntervalId) { clearInterval(heartbeatIntervalId); heartbeatIntervalId = null; }
            winScreen.style.display = "flex"; return;
        }
        let needed = sectorRequirements[currentSector]; targetTracker.innerText = "SECTOR " + currentSector + ": " + sectorKills + "/" + needed;
        sound("level");
    }

    function triggerEnemyDamageStrike() {
        if (isOver || winScreen.style.display === "flex" || isMoving || document.getElementById("chapterOverlay").style.display === "flex") return;
        playerHp -= 12; if (playerHp < 0) playerHp = 0; healthBar.style.width = playerHp + "%"; sound("bullet_crack");
        gameArea.classList.add("taking-damage"); setTimeout(() => gameArea.classList.remove("taking-damage"), 130);
        if (playerHp <= 20 && !heartbeatIntervalId) { gameArea.classList.add("critical-pulse"); heartbeatIntervalId = setInterval(() => { sound("heartbeat"); }, 550); }
        if (playerHp <= 0) { isOver = true; sound("bullet_crack"); clearInterval(spawnTimerId); clearInterval(runLoopTimerId); if(heartbeatIntervalId) { clearInterval(heartbeatIntervalId); gameArea.classList.remove("critical-pulse"); heartbeatIntervalId = null; } finalScore.innerText = "Final Score Log: " + score; overScreen.style.display = "flex"; }
    }

    function muzzleFX() {
        // position the muzzle flash at the barrel tip in game space
        let m = document.getElementById("muzzle").getBoundingClientRect();
        let b = gameArea.getBoundingClientRect();
        let mx = (m.left + m.width/2 - b.left) * (CW / b.width);
        let my = (m.top + m.height/2 - b.top) * (CH / b.height);
        flash.style.left = mx + "px"; flash.style.top = my + "px";
        flash.style.display = "block"; setTimeout(() => { flash.style.display = "none"; }, 55);
        weapon.animate([{ transform: getComputedStyle(weapon).transform }, { transform: getComputedStyle(weapon).transform + " translateY(10px)" }, { transform: getComputedStyle(weapon).transform }], { duration: 90 });
        for (let i = 0; i < 6; i++) smokeParticles.push({ x: mx + (Math.random()*10-5), y: my, vx: (Math.random()*1.2-0.6), vy: -0.8 - Math.random()*0.8, life: 1, r: 4 + Math.random()*4 });
    }

    function triggerFire() {
        if (isOver || winScreen.style.display === "flex" || isMoving || document.getElementById("chapterOverlay").style.display === "flex") return;
        document.getElementById("tutorialPopup").style.display = "none";

        sound("shot"); muzzleFX();

        let hitTarget = null; let lowestDistance = Infinity;
        threatsList.forEach(t => {
            if (t.isDying) return;
            let d = Math.hypot(currentX - t.currentScreenX, currentY - t.currentScreenY);
            if (d < t.currentRadius && d < lowestDistance) { lowestDistance = d; hitTarget = t; }
        });
        if (hitTarget) {
            hitTarget.isDying = true; hitTarget.deathTick = 0;
            sound("shout"); // enemy shouts on death
            score += 100; scoreCounter.innerText = String(score).padStart(5, '0'); sectorKills += 1;
            let needed = sectorRequirements[currentSector]; targetTracker.innerText = "SECTOR " + currentSector + ": " + Math.min(sectorKills, needed) + "/" + needed;
            hitTarget.ring.style.opacity = "0";
            // blood spray
            for (let i = 0; i < 16; i++) bloodParticles.push({ x: hitTarget.currentScreenX, y: hitTarget.currentScreenY, vx: (Math.random()*6-3), vy: (Math.random()*-4-1), life: 1, r: 2 + Math.random()*2.5 });
            // Fix: begin sector clear only when the quota is met; the actual
            // advance waits until every enemy (dying included) has left the field.
            if (sectorKills >= needed) {
                sectorClearing = true;
                if (spawnTimerId) { clearInterval(spawnTimerId); spawnTimerId = null; }
            }
        }
    }

    // ---------------- DRAWING HELPERS ----------------
    function drawContainer(b) {
        let p = project3D(b.x, b.y, b.z); if (!p) return;
        let w = 2.6 * p.size, h = 2.4 * p.size;
        let fx = p.x - w/2, fy = p.y - h/2;
        let depth = 0.5 * p.size * b.side; // side face offset

        // side face (gives it 3D volume)
        ctx.fillStyle = b.topColor;
        ctx.beginPath();
        ctx.moveTo(fx + (b.side > 0 ? w : 0), fy);
        ctx.lineTo(fx + (b.side > 0 ? w : 0) + depth, fy - Math.abs(depth)*0.5);
        ctx.lineTo(fx + (b.side > 0 ? w : 0) + depth, fy + h - Math.abs(depth)*0.5);
        ctx.lineTo(fx + (b.side > 0 ? w : 0), fy + h);
        ctx.closePath(); ctx.fill();

        // top face
        ctx.fillStyle = shade(b.baseColor, 1.25);
        ctx.beginPath();
        ctx.moveTo(fx, fy); ctx.lineTo(fx + w, fy);
        ctx.lineTo(fx + w + depth, fy - Math.abs(depth)*0.5);
        ctx.lineTo(fx + depth, fy - Math.abs(depth)*0.5);
        ctx.closePath(); ctx.fill();

        // front face base
        ctx.fillStyle = b.baseColor; ctx.fillRect(fx, fy, w, h);
        // corrugation ribs
        let ribs = 10;
        for (let i = 0; i < ribs; i++) {
            ctx.fillStyle = (i % 2 === 0) ? "rgba(0,0,0,0.16)" : "rgba(255,255,255,0.06)";
            ctx.fillRect(fx + (i/ribs)*w, fy + h*0.08, (w/ribs)*0.55, h*0.84);
        }
        // top + bottom rails
        ctx.fillStyle = b.topColor; ctx.fillRect(fx, fy, w, h*0.09); ctx.fillRect(fx, fy + h*0.91, w, h*0.09);
        // corner castings
        ctx.fillStyle = "#0b0d10";
        ctx.fillRect(fx, fy, w*0.09, h*0.09); ctx.fillRect(fx + w*0.91, fy, w*0.09, h*0.09);
        ctx.fillRect(fx, fy + h*0.91, w*0.09, h*0.09); ctx.fillRect(fx + w*0.91, fy + h*0.91, w*0.09, h*0.09);
        // doors: two vertical locking rods
        ctx.strokeStyle = "rgba(0,0,0,0.5)"; ctx.lineWidth = Math.max(1, p.size*0.03);
        ctx.beginPath(); ctx.moveTo(fx + w*0.35, fy + h*0.1); ctx.lineTo(fx + w*0.35, fy + h*0.9);
        ctx.moveTo(fx + w*0.65, fy + h*0.1); ctx.lineTo(fx + w*0.65, fy + h*0.9); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(fx + w*0.5, fy + h*0.1); ctx.lineTo(fx + w*0.5, fy + h*0.9); ctx.stroke();
        // faded stencil label
        if (p.size > 26) {
            ctx.fillStyle = "rgba(255,255,255,0.55)"; ctx.font = "bold " + Math.floor(p.size*0.28) + "px monospace";
            ctx.textAlign = "center"; ctx.fillText(b.label, fx + w*0.5, fy + h*0.5);
        }
        ctx.strokeStyle = "rgba(0,0,0,0.55)"; ctx.lineWidth = Math.max(1.5, p.size*0.04); ctx.strokeRect(fx, fy, w, h);

        // stacked container on top
        if (b.stack) {
            let sy = fy - h*0.98;
            ctx.fillStyle = shade(b.baseColor, 0.8); ctx.fillRect(fx + w*0.05, sy, w*0.9, h*0.9);
            for (let i = 0; i < 9; i++) { ctx.fillStyle = (i%2===0)?"rgba(0,0,0,0.16)":"rgba(255,255,255,0.05)"; ctx.fillRect(fx + w*0.05 + (i/9)*w*0.9, sy + h*0.08, (w*0.9/9)*0.55, h*0.72); }
            ctx.strokeStyle = "rgba(0,0,0,0.55)"; ctx.strokeRect(fx + w*0.05, sy, w*0.9, h*0.9);
        }
    }

    function shade(hex, f) {
        let c = hex.replace('#',''); let r = parseInt(c.substr(0,2),16), g = parseInt(c.substr(2,2),16), b = parseInt(c.substr(4,2),16);
        r = Math.min(255, Math.floor(r*f)); g = Math.min(255, Math.floor(g*f)); b = Math.min(255, Math.floor(b*f));
        return "rgb(" + r + "," + g + "," + b + ")";
    }

    function drawSoldier(t) {
        let p = project3D(t.x, t.y, t.z); if (!p) return;
        let peek = (Math.sin(t.loopTick * 0.05) + 1) / 2; let isOut = peek > 0.45;
        let s = p.size * 0.5;
        let cx = p.x - (s * 1.7) + (s * 1.7 * peek);
        let feetY = p.y + s * 0.4;
        t.currentScreenX = cx; t.currentScreenY = feetY - s * 1.0; t.currentRadius = s * 1.25;

        if (!t.isDying) { if (isOut) { t.ring.style.opacity = "1"; t.age++; } else { t.ring.style.opacity = "0"; } }
        if (!t.isDying && t.age > 55 && t.age % 78 === 0 && !isMoving && isOut && !sectorClearing) {
            t.isFlashing = true; triggerEnemyDamageStrike(); setTimeout(() => { t.isFlashing = false; }, 90);
        }

        ctx.save();
        if (t.isDying) {
            let dp = Math.min(1, t.deathTick / 20);
            ctx.globalAlpha = 1 - dp * 0.95;
            ctx.translate(cx, feetY); ctx.rotate(dp * t.deathDir * 1.3); ctx.translate(-cx, -feetY);
        }

        // ground shadow
        ctx.fillStyle = "rgba(0,0,0,0.45)"; ctx.beginPath(); ctx.ellipse(cx, feetY + s*0.05, s*0.7, s*0.18, 0, 0, Math.PI*2); ctx.fill();

        // legs
        ctx.fillStyle = "#243027";
        ctx.fillRect(cx - s*0.34, feetY - s*0.55, s*0.28, s*0.6);
        ctx.fillRect(cx + s*0.06, feetY - s*0.55, s*0.28, s*0.6);
        // boots
        ctx.fillStyle = "#0c0e0b"; ctx.fillRect(cx - s*0.36, feetY - s*0.05, s*0.32, s*0.14); ctx.fillRect(cx + s*0.04, feetY - s*0.05, s*0.32, s*0.14);

        // torso / tactical vest
        ctx.fillStyle = "#2f3a2b"; ctx.fillRect(cx - s*0.42, feetY - s*1.35, s*0.84, s*0.85);
        ctx.fillStyle = "#1c241a"; ctx.fillRect(cx - s*0.42, feetY - s*1.35, s*0.84, s*0.85); // base
        ctx.fillStyle = "#3c4a35"; ctx.fillRect(cx - s*0.38, feetY - s*1.3, s*0.76, s*0.75); // vest plate
        // vest pouches + straps
        ctx.fillStyle = "#20281c";
        ctx.fillRect(cx - s*0.3, feetY - s*0.95, s*0.24, s*0.22);
        ctx.fillRect(cx + s*0.06, feetY - s*0.95, s*0.24, s*0.22);
        ctx.strokeStyle = "#12160f"; ctx.lineWidth = Math.max(1, s*0.05);
        ctx.beginPath(); ctx.moveTo(cx - s*0.2, feetY - s*1.3); ctx.lineTo(cx - s*0.2, feetY - s*0.55);
        ctx.moveTo(cx + s*0.2, feetY - s*1.3); ctx.lineTo(cx + s*0.2, feetY - s*0.55); ctx.stroke();

        // arms
        ctx.fillStyle = "#2f3a2b";
        ctx.fillRect(cx - s*0.55, feetY - s*1.25, s*0.2, s*0.6);
        ctx.fillRect(cx + s*0.35, feetY - s*1.25, s*0.2, s*0.55);

        // rifle pointed toward the player (down/front)
        ctx.save();
        ctx.translate(cx + s*0.1, feetY - s*0.95); ctx.rotate(0.55);
        ctx.fillStyle = "#111"; ctx.fillRect(-s*0.1, 0, s*1.15, s*0.14);      // barrel
        ctx.fillStyle = "#1b1b1b"; ctx.fillRect(-s*0.1, s*0.05, s*0.55, s*0.28); // body
        ctx.fillStyle = "#0a0a0a"; ctx.fillRect(-s*0.02, s*0.3, s*0.16, s*0.34); // magazine
        // muzzle flash when firing
        if (t.isFlashing && isOut && !t.isDying) {
            let g = ctx.createRadialGradient(s*1.1, s*0.07, 1, s*1.1, s*0.07, s*0.4);
            g.addColorStop(0, "#fffbe6"); g.addColorStop(0.5, "#ffb020"); g.addColorStop(1, "transparent");
            ctx.fillStyle = g; ctx.beginPath(); ctx.arc(s*1.1, s*0.07, s*0.4, 0, Math.PI*2); ctx.fill();
        }
        ctx.restore();

        // neck + head
        ctx.fillStyle = "#c79a6b"; ctx.fillRect(cx - s*0.1, feetY - s*1.45, s*0.2, s*0.16);
        ctx.fillStyle = "#d4b38a"; ctx.beginPath(); ctx.arc(cx, feetY - s*1.62, s*0.3, 0, Math.PI*2); ctx.fill();
        // helmet
        ctx.fillStyle = "#2a3325"; ctx.beginPath(); ctx.arc(cx, feetY - s*1.68, s*0.34, Math.PI, 0); ctx.fill();
        ctx.fillRect(cx - s*0.34, feetY - s*1.7, s*0.68, s*0.1);
        ctx.fillStyle = "#1a2016"; ctx.fillRect(cx + s*0.1, feetY - s*1.74, s*0.28, s*0.05); // helmet accessory rail
        // visor / eyes
        ctx.fillStyle = "#0b0d0a"; ctx.fillRect(cx - s*0.2, feetY - s*1.6, s*0.4, s*0.08);

        // hit flash overlay
        if (t.isFlashing && isOut && !t.isDying) {
            ctx.fillStyle = "rgba(255,90,60,0.25)"; ctx.fillRect(cx - s*0.5, feetY - s*1.8, s*1.0, s*1.8);
        }
        ctx.restore();

        // ring follows the head/upper body
        t.ring.style.left = cx + "px"; t.ring.style.top = (feetY - s*1.0) + "px";
        let dyn = Math.max(18, Math.min(120, 100 * (1.3 - (t.age / 40))));
        t.ring.style.width = dyn + "px"; t.ring.style.height = dyn + "px";
    }

    function drawParticles() {
        // blood
        for (let i = bloodParticles.length - 1; i >= 0; i--) {
            let pt = bloodParticles[i]; pt.x += pt.vx; pt.y += pt.vy; pt.vy += 0.35; pt.life -= 0.035;
            if (pt.life <= 0) { bloodParticles.splice(i, 1); continue; }
            ctx.fillStyle = "rgba(150,10,10," + Math.max(0, pt.life) + ")";
            ctx.beginPath(); ctx.arc(pt.x, pt.y, pt.r, 0, Math.PI*2); ctx.fill();
        }
        // muzzle smoke
        for (let i = smokeParticles.length - 1; i >= 0; i--) {
            let pt = smokeParticles[i]; pt.x += pt.vx; pt.y += pt.vy; pt.vy -= 0.02; pt.life -= 0.04; pt.r += 0.6;
            if (pt.life <= 0) { smokeParticles.splice(i, 1); continue; }
            ctx.fillStyle = "rgba(200,200,205," + Math.max(0, pt.life*0.4) + ")";
            ctx.beginPath(); ctx.arc(pt.x, pt.y, pt.r, 0, Math.PI*2); ctx.fill();
        }
    }

    function render3DSceneGrid() {
        if (document.getElementById("chapterOverlay").style.display === "flex") return;
        cycleTick += 0.05; cameraZ += (targetCameraZ - cameraZ) * 0.07; cameraX += (targetCameraX - cameraX) * 0.07;
        if (isMoving && Math.abs(cameraZ - targetCameraZ) < 0.1) { isMoving = false; }
        if (!spawnTimerId && !isOver && !sectorClearing && !isMoving) { spawnTimerId = setInterval(spawn3DThreatUnit, 1350); }

        // advance ONLY once quota is met AND every enemy has left the field
        if (sectorClearing && !isMoving && threatsList.length === 0) { triggerSectorPathMovement(); }

        let isOutdoorSector = ["E","F","G","H","I","J"].includes(currentSector);
        ctx.clearRect(0, 0, CW, CH);

        if (isOutdoorSector) {
            let skyGrd = ctx.createLinearGradient(0, 0, 0, HORIZON); skyGrd.addColorStop(0, "#0a1226"); skyGrd.addColorStop(0.55, "#111a33"); skyGrd.addColorStop(1, "#2a2440"); ctx.fillStyle = skyGrd; ctx.fillRect(0, 0, CW, HORIZON);
            // moon
            ctx.fillStyle = "rgba(240,240,220,0.9)"; ctx.beginPath(); ctx.arc(320, 60, 20, 0, Math.PI*2); ctx.fill();
            ctx.fillStyle = "rgba(255,255,255,0.8)"; for (let i = 1; i <= 30; i++) { let sX = (i * 73) % CW; let sY = (i * 37) % 200; let tw = Math.abs(Math.sin(cycleTick + i)) * 1.6; ctx.fillRect(sX, sY, tw, tw); }
            // distant cargo ship silhouette
            ctx.fillStyle = "#060912"; let shipX = 150 - (cameraX * 25); ctx.fillRect(shipX, 224, 80, 18); ctx.fillRect(shipX + 24, 210, 20, 14); ctx.fillRect(shipX + 52, 214, 8, 28);
            // sea
            let seaGrd = ctx.createLinearGradient(0, HORIZON, 0, CH); seaGrd.addColorStop(0, "#071a24"); seaGrd.addColorStop(0.5, "#04222a"); seaGrd.addColorStop(1, "#02141a"); ctx.fillStyle = seaGrd; ctx.fillRect(0, HORIZON, CW, CH);
            ctx.strokeStyle = "rgba(45, 212, 191, 0.18)"; ctx.lineWidth = 2; for (let waveY = HORIZON + 15; waveY < CH; waveY += 34) { ctx.beginPath(); let ws = Math.sin(cycleTick + waveY) * 12; ctx.moveTo(0, waveY + ws); ctx.bezierCurveTo(140, waveY - 14 + ws, 280, waveY + 14 + ws, CW, waveY + ws); ctx.stroke(); }
            // moon reflection
            ctx.fillStyle = "rgba(240,240,220,0.08)"; ctx.fillRect(300, HORIZON, 40, CH - HORIZON);
        } else {
            let sky = ctx.createLinearGradient(0,0,0,HORIZON); sky.addColorStop(0,"#0b1220"); sky.addColorStop(1,"#0a1a1f"); ctx.fillStyle = sky; ctx.fillRect(0,0,CW,HORIZON);
            // warehouse floodlights glow
            ctx.fillStyle = "rgba(250, 204, 21, 0.05)"; ctx.beginPath(); ctx.moveTo(60,0); ctx.lineTo(140,0); ctx.lineTo(200,HORIZON); ctx.lineTo(30,HORIZON); ctx.closePath(); ctx.fill();
            ctx.fillStyle = "#050a0c"; ctx.fillRect(0, HORIZON, CW, CH);
        }

        // perspective floor
        for (let z = 84; z >= 0; z -= 3) {
            let zPos = Math.floor(cameraZ) + z; zPos = zPos - (zPos % 3);
            let pNear = project3D(0, 0, zPos); let pFar = project3D(0, 0, zPos + 3); if (!pNear || !pFar) continue;
            let fog = Math.min(1, z / 65); let ls = 1 - fog;
            ctx.fillStyle = "rgba(" + Math.floor(22*ls) + "," + Math.floor(30*ls) + "," + Math.floor(40*ls) + ",1)";
            ctx.beginPath(); ctx.moveTo(CX0 - (4.5 * pNear.size), HORIZON + (1.6 * pNear.size)); ctx.lineTo(CX0 + (4.5 * pNear.size), HORIZON + (1.6 * pNear.size)); ctx.lineTo(CX0 + (4.5 * pFar.size), HORIZON + (1.6 * pFar.size)); ctx.lineTo(CX0 - (4.5 * pFar.size), HORIZON + (1.6 * pFar.size)); ctx.fill();
            ctx.strokeStyle = "rgba(45, 212, 191, 0.22)"; ctx.lineWidth = Math.max(1, pNear.size * 0.03); ctx.beginPath(); ctx.moveTo(CX0 - (4.5 * pNear.size), HORIZON + (1.6 * pNear.size)); ctx.lineTo(CX0 + (4.5 * pNear.size), HORIZON + (1.6 * pNear.size)); ctx.stroke();
            if (isOutdoorSector) continue;
            // warehouse walls
            let ridge = Math.floor(zPos * 2.5) % 2 === 0;
            ctx.fillStyle = "rgba(" + Math.floor((ridge?26:34)*ls) + "," + Math.floor((ridge?34:42)*ls) + "," + Math.floor((ridge?40:48)*ls) + ",1)";
            ctx.beginPath(); ctx.moveTo(CX0 - (4.5 * pNear.size), HORIZON + (1.6 * pNear.size)); ctx.lineTo(CX0 - (4.5 * pNear.size), HORIZON - (2.4 * pNear.size)); ctx.lineTo(CX0 - (4.5 * pFar.size), HORIZON - (2.4 * pFar.size)); ctx.lineTo(CX0 - (4.5 * pFar.size), HORIZON + (1.6 * pFar.size)); ctx.fill();
            ctx.beginPath(); ctx.moveTo(CX0 + (4.5 * pNear.size), HORIZON + (1.6 * pNear.size)); ctx.lineTo(CX0 + (4.5 * pNear.size), HORIZON - (2.4 * pNear.size)); ctx.lineTo(CX0 + (4.5 * pFar.size), HORIZON - (2.4 * pFar.size)); ctx.lineTo(CX0 + (4.5 * pFar.size), HORIZON + (1.6 * pFar.size)); ctx.fill();
        }

        // depth-sorted objects
        let queue = [];
        static3DObstacles.forEach(b => { if (b.z >= cameraZ) queue.push({ type: "crate", z: b.z, data: b }); });
        threatsList.forEach(t => { if (t.z >= cameraZ) queue.push({ type: "enemy", z: t.z, data: t }); });
        queue.sort((a, b) => b.z - a.z);
        queue.forEach(item => {
            if (item.type === "crate") drawContainer(item.data);
            else {
                let t = item.data; if (!isMoving && !t.isDying) t.loopTick++;
                drawSoldier(t);
                if (t.isDying) {
                    t.deathTick++;
                    if (t.deathTick > 22) { if (t.ring) t.ring.remove(); threatsList = threatsList.filter(x => x !== t); }
                }
            }
        });

        drawParticles();
    }

    function initializeActiveArcadeGameplay() {
        document.getElementById("chapterOverlay").style.display = "none";
        if (currentSector === "A" && sectorKills === 0) { document.getElementById("tutorialPopup").style.display = "block"; }
        scoreCounter.style.display = "block"; chapterTxt.style.display = "block"; targetTracker.style.display = "block"; document.getElementById("healthWrap").style.display = "block"; sight.style.display = "block"; weapon.style.display = "block";
        runLoopTimerId = setInterval(render3DSceneGrid, 1000 / 45);
    }

    window.resetArcadeEngine = function(fullReset) {
        if (spawnTimerId) { clearInterval(spawnTimerId); spawnTimerId = null; }
        clearInterval(runLoopTimerId); if(heartbeatIntervalId) { clearInterval(heartbeatIntervalId); heartbeatIntervalId = null; }
        document.querySelectorAll(".target-ring").forEach(el => el.remove()); threatsList = []; bloodParticles = []; smokeParticles = [];
        cameraZ = 0; targetCameraZ = 0; cameraX = 0; targetCameraX = 0; currentSector = "A"; sectorKills = 0; sectorClearing = false; playerHp = 100; score = 200; isMoving = false; isOver = false;
        winScreen.style.display = "none"; overScreen.style.display = "none";
        gameArea.className = ""; healthBar.style.width = "100%"; scoreCounter.innerText = "00200"; chapterTxt.innerText = "CH 1: CONTAINER PORT";
        let needed = sectorRequirements[currentSector]; targetTracker.innerText = "SECTOR " + currentSector + ": " + sectorKills + "/" + needed;

        document.getElementById("chapterOverlay").style.display = "flex";
        document.getElementById("tutorialPopup").style.display = "none";
        scoreCounter.style.display = "none"; chapterTxt.style.display = "none"; targetTracker.style.display = "none"; document.getElementById("healthWrap").style.display = "none"; sight.style.display = "none"; weapon.style.display = "none";
        setTimeout(initializeActiveArcadeGameplay, 3000);
    };

    setTimeout(initializeActiveArcadeGameplay, 3000);
</script>
</body>
</html>
'''

cb_id = random.randint(100000, 999999)
st.markdown(f'<!-- Fixed Sound Tactical Injector Frame ID: {cb_id} -->', unsafe_allow_html=True)
components.html(game_html, height=600, scrolling=False)
