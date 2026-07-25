import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Cargo Waterfront", layout="wide", initial_sidebar_state="collapsed")

# Kill Streamlit padding so the game fills the screen
st.markdown(
    """
    <style>
      #MainMenu, header, footer {visibility: hidden;}
      .block-container {padding: 0 !important; max-width: 100% !important;}
      section.main > div {padding: 0 !important;}
      .stApp {background: #05070d;}
    </style>
    """,
    unsafe_allow_html=True,
)

GAME_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no"/>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  html, body { width:100%; height:100%; overflow:hidden; background:#05070d;
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; -webkit-user-select:none; user-select:none; }
  #app { position:fixed; inset:0; }
  canvas { display:block; }

  /* ---------- HUD ---------- */
  .hud { position:absolute; pointer-events:none; z-index:10; }

  #score {
    top:18px; left:18px;
    background:linear-gradient(#1b1e26,#0c0e13);
    border:2px solid #3a3f4b; border-radius:10px;
    padding:8px 16px; box-shadow:0 6px 18px rgba(0,0,0,.6), inset 0 0 0 2px #000;
  }
  #score b { font-family:'Courier New',monospace; font-size:34px; letter-spacing:3px;
    color:#ffb400; text-shadow:0 0 8px rgba(255,180,0,.8); }

  #chapter { top:18px; right:18px; text-align:right; }
  #chapter .row {
    background:linear-gradient(#12161f,#0a0d13);
    border:1px solid #2a5fff; border-radius:8px;
    padding:8px 16px; margin-bottom:8px;
    color:#66b2ff; font-weight:700; letter-spacing:2px; font-size:16px;
    text-shadow:0 0 10px rgba(60,140,255,.7); box-shadow:0 0 16px rgba(40,90,255,.25);
  }

  /* health */
  #hpwrap { bottom:22px; left:18px; display:flex; align-items:center; gap:10px; }
  #hpwrap .lbl { color:#fff; font-weight:800; font-size:16px; letter-spacing:1px;
    background:#000; padding:4px 8px; border-radius:5px; }
  #hpbar { width:260px; height:26px; background:#111; border:2px solid #333; border-radius:6px;
    display:flex; gap:2px; padding:3px; }
  #hpbar i { flex:1; background:#e0202a; border-radius:2px; box-shadow:0 0 6px rgba(224,32,42,.8);
    transition:background .2s; }
  #hpbar i.off { background:#2a1113; box-shadow:none; }

  /* crosshair (follows the mouse / finger) */
  #cross { top:50%; left:50%; transform:translate(-50%,-50%); width:46px; height:46px;
    transition:none; will-change:left,top; }
  #cross .ring { position:absolute; inset:0; border:2px solid #21e6c1; border-radius:50%;
    box-shadow:0 0 10px rgba(33,230,193,.9); opacity:.9; }
  #cross .dot { position:absolute; top:50%; left:50%; width:4px; height:4px; margin:-2px 0 0 -2px;
    background:#21e6c1; border-radius:50%; box-shadow:0 0 8px #21e6c1; }
  #cross span { position:absolute; background:#21e6c1; box-shadow:0 0 6px #21e6c1; }
  #cross .t { top:-8px; left:50%; width:2px; height:8px; margin-left:-1px; }
  #cross .b { bottom:-8px; left:50%; width:2px; height:8px; margin-left:-1px; }
  #cross .l { left:-8px; top:50%; width:8px; height:2px; margin-top:-1px; }
  #cross .r { right:-8px; top:50%; width:8px; height:2px; margin-top:-1px; }

  /* red threat rings that appear over nearby enemies (like the reference) */
  #threats { position:absolute; inset:0; z-index:7; pointer-events:none; }
  .threat { position:absolute; width:70px; height:70px; margin:-35px 0 0 -35px;
    border:3px solid #ff2b3d; border-radius:50%;
    box-shadow:0 0 16px rgba(255,43,61,.9), inset 0 0 12px rgba(255,43,61,.5);
    transition:opacity .12s; }
  .threat::before, .threat::after { content:''; position:absolute; background:#ff2b3d;
    box-shadow:0 0 8px #ff2b3d; }
  .threat::before { top:50%; left:-10px; width:20px; height:2px; margin-top:-1px; }
  .threat::after  { top:50%; right:-10px; width:20px; height:2px; margin-top:-1px; }
  .threat i { position:absolute; left:50%; width:2px; background:#ff2b3d; box-shadow:0 0 8px #ff2b3d;
    margin-left:-1px; }
  .threat i.tt { top:-10px; height:20px; } .threat i.bb { bottom:-10px; height:20px; }

  #kills { bottom:24px; left:50%; transform:translateX(-50%); text-align:center; }
  #kills .box { background:rgba(8,10,16,.72); border:1px solid #2a5fff; border-radius:8px;
    padding:6px 18px; color:#cfe4ff; font-weight:700; letter-spacing:1px; font-size:15px;
    text-shadow:0 0 8px rgba(60,140,255,.6); }

  #flash { position:absolute; inset:0; background:radial-gradient(circle at 50% 50%, rgba(255,120,60,.0), rgba(255,60,40,.0));
    z-index:9; pointer-events:none; }
  #dmg { position:absolute; inset:0; z-index:8; pointer-events:none; box-shadow:inset 0 0 0 rgba(255,0,0,0);
    transition:box-shadow .25s; }

  /* start / status overlay */
  #overlay { position:absolute; inset:0; z-index:30; display:flex; flex-direction:column;
    align-items:center; justify-content:center; text-align:center; color:#fff;
    background:radial-gradient(circle at 50% 40%, rgba(20,30,55,.55), rgba(3,5,10,.92)); }
  #overlay h1 { font-size:52px; letter-spacing:6px; color:#66b2ff;
    text-shadow:0 0 24px rgba(60,140,255,.8); margin-bottom:8px; }
  #overlay p { color:#a9c2e6; font-size:18px; margin:4px 0; max-width:560px; line-height:1.5; }
  #overlay .btn { margin-top:26px; pointer-events:auto; cursor:pointer;
    background:linear-gradient(#2a6bff,#1741c0); color:#fff; border:none; border-radius:10px;
    padding:16px 44px; font-size:20px; font-weight:800; letter-spacing:2px;
    box-shadow:0 8px 26px rgba(30,70,255,.5); }
  #overlay .btn:hover { filter:brightness(1.12); }
  #overlay small { color:#7d93b5; margin-top:18px; }
  .hidden { display:none !important; }

  #loading { position:absolute; inset:0; z-index:40; display:flex; align-items:center; justify-content:center;
    background:#05070d; color:#66b2ff; font-size:20px; letter-spacing:3px; }
</style>
</head>
<body>
<div id="app"></div>

<div id="loading">LOADING WATERFRONT…</div>

<div id="dmg"></div>
<div id="flash"></div>

<!-- HUD -->
<div id="score" class="hud"><b>00000</b></div>
<div id="chapter" class="hud">
  <div class="row">CH 1: CARGO WATERFRONT</div>
  <div class="row" id="sector">SECTOR E&nbsp; 0/4</div>
</div>
<div id="threats"></div>
<div id="cross" class="hud">
  <div class="ring"></div><div class="dot"></div>
  <span class="t"></span><span class="b"></span><span class="l"></span><span class="r"></span>
</div>
<div id="hpwrap" class="hud">
  <div class="lbl">HP</div>
  <div id="hpbar"></div>
</div>
<div id="kills" class="hud">
  <div class="box">Eliminate <b id="need">5</b> guards to advance &nbsp;·&nbsp; <span id="clearcount">0</span>/5</div>
</div>

<div id="overlay">
  <h1>CARGO WATERFRONT</h1>
  <p>Night raid on the container port. Move the crosshair with your mouse (or finger on mobile) and click / tap to fire.</p>
  <p>Clear <b>5 guards</b> and you auto-advance deeper into the docks. Survive the sectors.</p>
  <button class="btn" id="startBtn">DEPLOY</button>
  <small>Aim = move mouse / drag finger · Click or tap = shoot · Red rings mark nearby threats</small>
</div>

<script type="importmap">
{ "imports": { "three": "https://unpkg.com/three@0.160.0/build/three.module.js" } }
</script>

<script type="module">
import * as THREE from 'three';

/* =========================================================
   BASIC SETUP
========================================================= */
const app = document.getElementById('app');
const renderer = new THREE.WebGLRenderer({ antialias:true, powerPreference:'high-performance' });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.4;
app.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x070b16);
scene.fog = new THREE.FogExp2(0x0a1224, 0.0075);

const camera = new THREE.PerspectiveCamera(70, innerWidth/innerHeight, 0.1, 2000);
camera.position.set(0, 2.6, 6);

/* rig that carries the camera forward down the dock */
const rig = new THREE.Group();
rig.position.set(0, 0, 0);
scene.add(rig);
rig.add(camera);

/* =========================================================
   LIGHTING  (moonlit night)
========================================================= */
scene.add(new THREE.HemisphereLight(0x5a7099, 0x1c2740, 1.0));

const moon = new THREE.DirectionalLight(0xd8e4ff, 1.8);
moon.position.set(-60, 90, -40);
moon.castShadow = true;
moon.shadow.mapSize.set(2048, 2048);
moon.shadow.camera.near = 1;
moon.shadow.camera.far = 400;
moon.shadow.camera.left = -120; moon.shadow.camera.right = 120;
moon.shadow.camera.top = 120; moon.shadow.camera.bottom = -120;
moon.shadow.bias = -0.0004;
scene.add(moon);

const fill = new THREE.DirectionalLight(0x4a6fbf, 0.7);
fill.position.set(40, 30, 40);
scene.add(fill);

/* soft ambient so nothing ever goes pure black */
scene.add(new THREE.AmbientLight(0x8090b0, 0.45));

/* a player flashlight that follows the camera so guard faces are always visible up close */
const flashlight = new THREE.SpotLight(0xfff2d8, 2.4, 70, Math.PI/5, 0.5, 1.2);
flashlight.position.set(0, 0, 0);
camera.add(flashlight);
camera.add(flashlight.target);
flashlight.target.position.set(0, 0, -1);

/* =========================================================
   SKY : stars + moon disc
========================================================= */
(function sky(){
  const g = new THREE.BufferGeometry();
  const n = 1800, pos = new Float32Array(n*3);
  for(let i=0;i<n;i++){
    const r = 900, th = Math.random()*Math.PI*2, ph = Math.acos(2*Math.random()-1);
    pos[i*3]   = r*Math.sin(ph)*Math.cos(th);
    pos[i*3+1] = Math.abs(r*Math.cos(ph))*0.9 + 30;
    pos[i*3+2] = r*Math.sin(ph)*Math.sin(th);
  }
  g.setAttribute('position', new THREE.BufferAttribute(pos,3));
  scene.add(new THREE.Points(g, new THREE.PointsMaterial({ color:0xdfe8ff, size:1.4, sizeAttenuation:false, transparent:true, opacity:.9 })));

  const moonMat = new THREE.MeshBasicMaterial({ color:0xf2f4ff, fog:false });
  const moonDisc = new THREE.Mesh(new THREE.CircleGeometry(26, 48), moonMat);
  moonDisc.position.set(-180, 150, -520);
  scene.add(moonDisc);
  const halo = new THREE.Mesh(new THREE.CircleGeometry(46, 48),
    new THREE.MeshBasicMaterial({ color:0x9fc0ff, transparent:true, opacity:.18, fog:false }));
  halo.position.copy(moonDisc.position); halo.position.z -= 1;
  scene.add(halo);
})();

/* =========================================================
   GROUND : long concrete dock + water
========================================================= */
const DOCK_W = 34;         // dock width
const WORLD_LEN = 900;     // how far the dock runs

function concreteTexture(){
  const c = document.createElement('canvas'); c.width=c.height=512;
  const x = c.getContext('2d');
  x.fillStyle='#3a3f47'; x.fillRect(0,0,512,512);
  for(let i=0;i<9000;i++){
    const g = 40+Math.random()*40;
    x.fillStyle=`rgba(${g},${g+4},${g+8},${Math.random()*0.4})`;
    x.fillRect(Math.random()*512, Math.random()*512, 2, 2);
  }
  x.strokeStyle='rgba(15,18,22,.6)'; x.lineWidth=3;
  for(let i=0;i<=512;i+=128){ x.beginPath();x.moveTo(i,0);x.lineTo(i,512);x.stroke();
    x.beginPath();x.moveTo(0,i);x.lineTo(512,i);x.stroke(); }
  const t = new THREE.CanvasTexture(c);
  t.wrapS=t.wrapT=THREE.RepeatWrapping; t.repeat.set(6, 160);
  t.anisotropy = renderer.capabilities.getMaxAnisotropy();
  return t;
}
const dock = new THREE.Mesh(
  new THREE.PlaneGeometry(DOCK_W, WORLD_LEN),
  new THREE.MeshStandardMaterial({ map:concreteTexture(), roughness:.95, metalness:.05, color:0x8a90a0 })
);
dock.rotation.x = -Math.PI/2;
dock.position.z = -WORLD_LEN/2 + 20;
dock.receiveShadow = true;
scene.add(dock);

/* water on both sides */
const waterMat = new THREE.MeshStandardMaterial({ color:0x0a1a33, roughness:.15, metalness:.9,
  transparent:true, opacity:.96 });
function waterStrip(side){
  const w = 400;
  const m = new THREE.Mesh(new THREE.PlaneGeometry(w, WORLD_LEN), waterMat);
  m.rotation.x = -Math.PI/2; m.position.y = -0.6;
  m.position.x = side*(DOCK_W/2 + w/2); m.position.z = dock.position.z;
  scene.add(m); return m;
}
const waterL = waterStrip(-1), waterR = waterStrip(1);

/* dock edge rails */
function rail(side){
  const g = new THREE.Group();
  const mat = new THREE.MeshStandardMaterial({ color:0x1a1d24, roughness:.6, metalness:.7 });
  const bar = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.3, WORLD_LEN), mat);
  bar.position.set(side*(DOCK_W/2-0.4), 0.9, dock.position.z);
  bar.castShadow = true; g.add(bar);
  for(let z=40; z> -WORLD_LEN; z-=14){
    const p = new THREE.Mesh(new THREE.CylinderGeometry(0.12,0.12,0.9,8), mat);
    p.position.set(side*(DOCK_W/2-0.4), 0.45, z); g.add(p);
  }
  scene.add(g);
}
rail(-1); rail(1);

/* =========================================================
   SHIPPING CONTAINERS  (colored, stacked, textured)
========================================================= */
const containerColors = [0xb23b2e,0x2e5fb2,0xc9962f,0x2f8f5b,0x8a8f99,0xb2662e,0x6a2f8f];
function containerTex(base){
  const c = document.createElement('canvas'); c.width=256; c.height=128;
  const x = c.getContext('2d');
  const col = new THREE.Color(base);
  x.fillStyle = `rgb(${col.r*255|0},${col.g*255|0},${col.b*255|0})`; x.fillRect(0,0,256,128);
  // corrugation
  for(let i=0;i<256;i+=10){
    x.fillStyle='rgba(0,0,0,.18)'; x.fillRect(i,0,4,128);
    x.fillStyle='rgba(255,255,255,.06)'; x.fillRect(i+5,0,2,128);
  }
  // rust streaks
  for(let i=0;i<40;i++){
    x.fillStyle=`rgba(60,30,10,${Math.random()*.35})`;
    x.fillRect(Math.random()*256, Math.random()*90, 3, 20+Math.random()*30);
  }
  x.strokeStyle='rgba(0,0,0,.5)'; x.lineWidth=6; x.strokeRect(3,3,250,122);
  const t = new THREE.CanvasTexture(c); t.anisotropy = 4; return t;
}
const contGeo = new THREE.BoxGeometry(6, 2.6, 2.5);
const collidables = [];   // boxes we can pass / raycast context
function makeContainer(x,y,z,color,rotY=0){
  const tex = containerTex(color);
  const mat = new THREE.MeshStandardMaterial({ map:tex, roughness:.85, metalness:.25 });
  const m = new THREE.Mesh(contGeo, mat);
  m.position.set(x, y+1.3, z); m.rotation.y = rotY;
  m.castShadow = m.receiveShadow = true;
  scene.add(m); collidables.push(m);
  return m;
}

/* build clusters of containers running down both sides of the dock */
const clusters = [];   // z positions where footsteps trigger
for(let z=-20; z>-WORLD_LEN+60; z-=55){
  clusters.push(z);
  const side = (Math.random()<0.5)?-1:1;
  // a stacked wall on one side
  const bx = side*(DOCK_W/2 - 5);
  const stacks = 2 + (Math.random()*2|0);
  for(let s=0;s<stacks;s++){
    const rows = 1 + (Math.random()*2|0);
    for(let r=0;r<rows;r++){
      makeContainer(bx + s*0.2, r*2.6, z - s*2.7,
        containerColors[(Math.random()*containerColors.length)|0], (Math.random()-.5)*0.06);
    }
  }
  // scattered singles on the other side
  if(Math.random()<0.7){
    makeContainer(-side*(DOCK_W/2 - 6), 0, z + 12 - Math.random()*10,
      containerColors[(Math.random()*containerColors.length)|0], (Math.random()-.5)*0.4);
  }
}

/* =========================================================
   CRANES + CARGO SHIP (background silhouettes with lights)
========================================================= */
function crane(x,z){
  const g = new THREE.Group();
  const mat = new THREE.MeshStandardMaterial({ color:0x394050, roughness:.7, metalness:.6 });
  const legGeo = new THREE.BoxGeometry(1.1,26,1.1);
  [[-4,-2],[4,-2],[-4,4],[4,4]].forEach(([lx,lz])=>{
    const l = new THREE.Mesh(legGeo, mat); l.position.set(lx,13,lz); g.add(l);
  });
  const top = new THREE.Mesh(new THREE.BoxGeometry(11,2,10), mat); top.position.y=27; g.add(top);
  const boom = new THREE.Mesh(new THREE.BoxGeometry(2,1.4,40), mat); boom.position.set(0,27,-16); g.add(boom);
  // red beacon
  const beacon = new THREE.Mesh(new THREE.SphereGeometry(0.5,8,8),
    new THREE.MeshBasicMaterial({ color:0xff2a2a }));
  beacon.position.set(0,28.5,0); g.add(beacon);
  const bl = new THREE.PointLight(0xff2a2a, 2, 40); bl.position.copy(beacon.position); g.add(bl);
  g.position.set(x, 0, z);
  scene.add(g);
  return beacon;
}
const beacons = [];
beacons.push(crane(-70, -140));
beacons.push(crane(-72, -260));
beacons.push(crane(78, -380));

function cargoShip(x,z){
  const g = new THREE.Group();
  const hull = new THREE.Mesh(new THREE.BoxGeometry(140, 22, 34),
    new THREE.MeshStandardMaterial({ color:0x111a2c, roughness:.6, metalness:.5 }));
  hull.position.y = 8; g.add(hull);
  // deck container blocks
  for(let i=0;i<12;i++){
    const b = new THREE.Mesh(new THREE.BoxGeometry(9,7,26),
      new THREE.MeshStandardMaterial({ color:containerColors[i%containerColors.length], roughness:.8 }));
    b.position.set(-56 + i*10, 22, 0); g.add(b);
  }
  // cabin with lit windows
  const cab = new THREE.Mesh(new THREE.BoxGeometry(16,18,26),
    new THREE.MeshStandardMaterial({ color:0x1a2436 }));
  cab.position.set(58,26,0); g.add(cab);
  for(let wy=0;wy<5;wy++)for(let wx=0;wx<3;wx++){
    const w = new THREE.Mesh(new THREE.PlaneGeometry(2,1.4),
      new THREE.MeshBasicMaterial({ color:0xffd98a }));
    w.position.set(58+ (wx-1)*4, 20+wy*3, 13.1); g.add(w);
  }
  g.position.set(x,0,z); g.rotation.y = Math.PI*0.02;
  scene.add(g);
}
cargoShip(-150, -320);

/* far shoreline city lights */
(function cityLights(){
  const g = new THREE.BufferGeometry();
  const n=400, pos=new Float32Array(n*3), col=new Float32Array(n*3);
  for(let i=0;i<n;i++){
    pos[i*3]=(Math.random()-0.5)*800;
    pos[i*3+1]=Math.random()*4+1;
    pos[i*3+2]=-560 - Math.random()*120;
    const warm=Math.random()<0.7;
    col[i*3]= warm?1:0.6; col[i*3+1]= warm?0.8:0.8; col[i*3+2]= warm?0.4:1;
  }
  g.setAttribute('position', new THREE.BufferAttribute(pos,3));
  g.setAttribute('color', new THREE.BufferAttribute(col,3));
  scene.add(new THREE.Points(g, new THREE.PointsMaterial({ size:2.4, sizeAttenuation:false, vertexColors:true })));
})();

/* dock lamp posts (pools of light) */
for(let z=30; z>-WORLD_LEN; z-=48){
  const side=(z%2===0)?1:-1;
  const post = new THREE.Mesh(new THREE.CylinderGeometry(0.15,0.2,7,8),
    new THREE.MeshStandardMaterial({ color:0x20242c, metalness:.6, roughness:.5 }));
  post.position.set(side*(DOCK_W/2-1.2), 3.5, z); post.castShadow=true; scene.add(post);
  const lamp = new THREE.Mesh(new THREE.SphereGeometry(0.35,10,10),
    new THREE.MeshBasicMaterial({ color:0xffe6a8 }));
  lamp.position.set(side*(DOCK_W/2-1.2), 7, z); scene.add(lamp);
  const pl = new THREE.PointLight(0xffd18a, 3.2, 34, 2); pl.position.copy(lamp.position); scene.add(pl);
}

/* =========================================================
   GUARDS  (rigged humanoid figures)
========================================================= */
const skinMat   = new THREE.MeshStandardMaterial({ color:0xc79b7a, roughness:.7 });
const suitMat   = new THREE.MeshStandardMaterial({ color:0x1c2129, roughness:.75, metalness:.15 });
const vestMat   = new THREE.MeshStandardMaterial({ color:0x2b2f38, roughness:.6, metalness:.3 });
const gunMat    = new THREE.MeshStandardMaterial({ color:0x0e0f12, roughness:.4, metalness:.8 });

const guards = [];
function makeGuard(x,z){
  const g = new THREE.Group();

  const torso = new THREE.Mesh(new THREE.CapsuleGeometry(0.34,0.7,4,10), suitMat);
  torso.position.y = 1.32; torso.castShadow=true; g.add(torso);

  const vest = new THREE.Mesh(new THREE.BoxGeometry(0.72,0.72,0.42), vestMat);
  vest.position.y = 1.42; vest.castShadow=true; g.add(vest);

  const head = new THREE.Mesh(new THREE.SphereGeometry(0.24,16,16), skinMat);
  head.position.y = 1.95; head.castShadow=true; g.add(head);
  const helmet = new THREE.Mesh(new THREE.SphereGeometry(0.27,16,16, 0, Math.PI*2, 0, Math.PI*0.55), vestMat);
  helmet.position.y = 1.99; g.add(helmet);

  const legGeo = new THREE.CapsuleGeometry(0.16,0.72,4,8);
  const lL = new THREE.Mesh(legGeo, suitMat); lL.position.set(-0.18,0.55,0); lL.castShadow=true; g.add(lL);
  const lR = new THREE.Mesh(legGeo, suitMat); lR.position.set( 0.18,0.55,0); lR.castShadow=true; g.add(lR);

  const armGeo = new THREE.CapsuleGeometry(0.13,0.6,4,8);
  const aL = new THREE.Mesh(armGeo, suitMat); aL.position.set(-0.5,1.35,0.15); aL.rotation.x=-0.5; g.add(aL);
  const aR = new THREE.Mesh(armGeo, suitMat); aR.position.set( 0.5,1.35,0.15); aR.rotation.x=-0.5; g.add(aR);

  // rifle held forward
  const rifle = new THREE.Group();
  const body = new THREE.Mesh(new THREE.BoxGeometry(0.1,0.14,0.9), gunMat); rifle.add(body);
  const barrel = new THREE.Mesh(new THREE.CylinderGeometry(0.03,0.03,0.5,8), gunMat);
  barrel.rotation.x=Math.PI/2; barrel.position.z=-0.6; rifle.add(barrel);
  const mag = new THREE.Mesh(new THREE.BoxGeometry(0.08,0.28,0.12), gunMat); mag.position.set(0,-0.18,0.1); rifle.add(mag);
  rifle.position.set(0.42,1.25,0.35); g.add(rifle);

  // muzzle flash placeholder
  const flash = new THREE.Mesh(new THREE.SphereGeometry(0.12,8,8),
    new THREE.MeshBasicMaterial({ color:0xffcf6b, transparent:true, opacity:0 }));
  flash.position.set(0.42,1.25,-0.35); g.add(flash);
  const muzzleLight = new THREE.PointLight(0xffcf6b, 0, 10, 2);
  muzzleLight.position.copy(flash.position); g.add(muzzleLight);

  g.position.set(x, 0, z);
  g.userData = {
    alive:true, hp:2, torso, head, helmet, flash, muzzleLight, rifle,
    legL:lL, legR:lR, armL:aL, armR:aR,
    fireCd: 1.0 + Math.random()*1.2,
    fireTimer: 0.6 + Math.random()*1.4,
    wobble: Math.random()*Math.PI*2,
    walkPhase: Math.random()*Math.PI*2,
    speed: 5.5 + Math.random()*2,   // running approach speed
    engaged:false,
  };
  scene.add(g);
  guards.push(g);
  return g;
}

/* enemy hit-collection for raycaster (torso+head+vest) */
function guardHitMeshes(){
  const arr=[];
  guards.forEach(gd=>{ if(gd.userData.alive){ gd.children.forEach(c=>{ if(c.isMesh){ c.userData.guard=gd; arr.push(c);} }); } });
  return arr;
}

/* spawn a wave of guards ahead of the player */
let waveIndex = 0;
function spawnWave(zBase){
  const count = 5;              // exactly 5 per sector, always
  for(let i=0;i<count;i++){
    const x = (Math.random()-0.5)*(DOCK_W-8);
    const z = zBase - 48 - Math.random()*24;   // far away — they have to run in
    makeGuard(x, z);
  }
}

/* =========================================================
   FIRST-PERSON PISTOL  (correctly oriented, pointing forward/up)
========================================================= */
const weapon = new THREE.Group();
camera.add(weapon);

function gunMetalTexture(baseGrey){
  const c = document.createElement('canvas'); c.width=c.height=128;
  const x = c.getContext('2d');
  x.fillStyle = baseGrey; x.fillRect(0,0,128,128);
  for(let i=0;i<600;i++){
    const g = Math.random()*40;
    x.strokeStyle = `rgba(${g+10},${g+10},${g+14},${Math.random()*0.35})`;
    x.lineWidth = Math.random()*1.2;
    const y = Math.random()*128;
    x.beginPath(); x.moveTo(Math.random()*128, y); x.lineTo(Math.random()*128, y+ (Math.random()-0.5)*6); x.stroke();
  }
  for(let i=0;i<25;i++){
    x.fillStyle = `rgba(0,0,0,${0.15+Math.random()*0.2})`;
    x.beginPath(); x.arc(Math.random()*128, Math.random()*128, Math.random()*2+0.5, 0, Math.PI*2); x.fill();
  }
  const t = new THREE.CanvasTexture(c);
  t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(2,2);
  return t;
}
function buildPistol(){
  const g = new THREE.Group();
  const black = new THREE.MeshStandardMaterial({ color:0x14161b, roughness:.35, metalness:.85, map:gunMetalTexture('#1b1d22') });
  const grey  = new THREE.MeshStandardMaterial({ color:0x2a2e36, roughness:.4, metalness:.8, map:gunMetalTexture('#2f333c') });
  const glove = new THREE.MeshStandardMaterial({ color:0x14171d, roughness:.9, metalness:.05 });

  // slide (top)
  const slide = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.14, 0.62), black);
  slide.position.set(0, 0.02, -0.30); g.add(slide);
  // barrel tip
  const tip = new THREE.Mesh(new THREE.BoxGeometry(0.11, 0.12, 0.06), grey);
  tip.position.set(0, 0.02, -0.62); g.add(tip);
  // frame
  const frame = new THREE.Mesh(new THREE.BoxGeometry(0.11, 0.10, 0.5), grey);
  frame.position.set(0, -0.06, -0.24); g.add(frame);
  // grip angled back-down
  const grip = new THREE.Mesh(new THREE.BoxGeometry(0.11, 0.34, 0.16), black);
  grip.position.set(0, -0.24, 0.02); grip.rotation.x = 0.28; g.add(grip);
  // trigger guard
  const guard = new THREE.Mesh(new THREE.TorusGeometry(0.06, 0.015, 8, 16), grey);
  guard.position.set(0, -0.10, -0.05); guard.rotation.y = Math.PI/2; g.add(guard);
  // rear sight
  const sight = new THREE.Mesh(new THREE.BoxGeometry(0.11,0.03,0.04), black);
  sight.position.set(0,0.10,-0.02); g.add(sight);

  // hands (gloved) cupping the grip
  const handR = new THREE.Mesh(new THREE.BoxGeometry(0.16,0.2,0.22), glove);
  handR.position.set(0.02,-0.26,0.08); handR.rotation.x=0.3; g.add(handR);
  const handL = new THREE.Mesh(new THREE.BoxGeometry(0.16,0.16,0.2), glove);
  handL.position.set(-0.10,-0.2,0.02); handL.rotation.z=0.4; g.add(handL);
  const foreR = new THREE.Mesh(new THREE.CylinderGeometry(0.09,0.11,0.5,10), glove);
  foreR.position.set(0.08,-0.5,0.28); foreR.rotation.x=0.7; g.add(foreR);
  const foreL = new THREE.Mesh(new THREE.CylinderGeometry(0.08,0.1,0.45,10), glove);
  foreL.position.set(-0.16,-0.46,0.22); foreL.rotation.set(0.7,0,0.3); g.add(foreL);

  // muzzle flash — bright core cone + soft additive glow disc for a punchy effect
  const mflash = new THREE.Mesh(new THREE.ConeGeometry(0.16,0.34,8),
    new THREE.MeshBasicMaterial({ color:0xfff0c0, transparent:true, opacity:0, fog:false, blending:THREE.AdditiveBlending }));
  mflash.rotation.x = -Math.PI/2; mflash.position.set(0,0.02,-0.74); g.add(mflash);
  g.userData.mflash = mflash;

  const glow = new THREE.Mesh(new THREE.CircleGeometry(0.22,16),
    new THREE.MeshBasicMaterial({ color:0xffcf6b, transparent:true, opacity:0, fog:false, blending:THREE.AdditiveBlending, side:THREE.DoubleSide }));
  glow.position.set(0,0.02,-0.7); g.add(glow);
  g.userData.glow = glow;

  return g;
}
const pistol = buildPistol();
// bottom-right of the view, pointing into the scene (forward -Z), slightly up
pistol.position.set(0.28, -0.34, -0.6);
pistol.rotation.set(0.06, -0.04, 0);
weapon.add(pistol);

const muzzleLight = new THREE.PointLight(0xffb455, 0, 12, 2);
muzzleLight.position.set(0.28,-0.2,-1.1);
camera.add(muzzleLight);

/* =========================================================
   AUDIO  (WebAudio synth: footsteps + gunshots + hits)
========================================================= */
let AC = null;
function audio(){ if(!AC){ AC = new (window.AudioContext||window.webkitAudioContext)(); } return AC; }

function gunshot(){
  const ac = audio(); const t = ac.currentTime;
  // noise burst
  const buf = ac.createBuffer(1, ac.sampleRate*0.25, ac.sampleRate);
  const d = buf.getChannelData(0);
  for(let i=0;i<d.length;i++){ d[i] = (Math.random()*2-1) * Math.pow(1 - i/d.length, 3); }
  const src = ac.createBufferSource(); src.buffer = buf;
  const bp = ac.createBiquadFilter(); bp.type='lowpass'; bp.frequency.value=1800;
  const g = ac.createGain(); g.gain.setValueAtTime(0.9, t); g.gain.exponentialRampToValueAtTime(0.001, t+0.22);
  src.connect(bp).connect(g).connect(ac.destination); src.start(t);
  // low thump
  const o = ac.createOscillator(); o.type='sine'; o.frequency.setValueAtTime(160,t);
  o.frequency.exponentialRampToValueAtTime(40,t+0.12);
  const og = ac.createGain(); og.gain.setValueAtTime(0.7,t); og.gain.exponentialRampToValueAtTime(0.001,t+0.15);
  o.connect(og).connect(ac.destination); o.start(t); o.stop(t+0.16);
}
function footstep(hard){
  const ac = audio(); const t = ac.currentTime;
  const buf = ac.createBuffer(1, ac.sampleRate*0.12, ac.sampleRate);
  const d = buf.getChannelData(0);
  for(let i=0;i<d.length;i++){ d[i]=(Math.random()*2-1)*Math.pow(1-i/d.length,4); }
  const src = ac.createBufferSource(); src.buffer=buf;
  const bp = ac.createBiquadFilter(); bp.type='bandpass'; bp.frequency.value= hard?420:260; bp.Q.value=1.2;
  const g = ac.createGain(); g.gain.setValueAtTime(hard?0.5:0.32, t); g.gain.exponentialRampToValueAtTime(0.001, t+0.1);
  src.connect(bp).connect(g).connect(ac.destination); src.start(t);
}
function hitSound(){
  const ac=audio(); const t=ac.currentTime;
  const o=ac.createOscillator(); o.type='square'; o.frequency.setValueAtTime(300,t);
  o.frequency.exponentialRampToValueAtTime(90,t+0.1);
  const g=ac.createGain(); g.gain.setValueAtTime(0.25,t); g.gain.exponentialRampToValueAtTime(0.001,t+0.12);
  o.connect(g).connect(ac.destination); o.start(t); o.stop(t+0.13);
}
function hurtSound(){
  const ac=audio(); const t=ac.currentTime;
  const o=ac.createOscillator(); o.type='sawtooth'; o.frequency.setValueAtTime(120,t);
  const g=ac.createGain(); g.gain.setValueAtTime(0.3,t); g.gain.exponentialRampToValueAtTime(0.001,t+0.2);
  o.connect(g).connect(ac.destination); o.start(t); o.stop(t+0.21);
}

/* =========================================================
   HUD helpers
========================================================= */
const scoreEl   = document.querySelector('#score b');
const sectorEl  = document.getElementById('sector');
const clearEl   = document.getElementById('clearcount');
const hpbar     = document.getElementById('hpbar');
const dmgEl     = document.getElementById('dmg');
const overlay   = document.getElementById('overlay');
const startBtn  = document.getElementById('startBtn');
const loadingEl = document.getElementById('loading');

const HP_SEG = 24;
for(let i=0;i<HP_SEG;i++){ const s=document.createElement('i'); hpbar.appendChild(s); }
function renderHP(){
  const on = Math.round(state.hp/100*HP_SEG);
  [...hpbar.children].forEach((s,i)=> s.classList.toggle('off', i>=on));
}
function setScore(v){ scoreEl.textContent = String(v).padStart(5,'0'); }
function setSector(){ sectorEl.innerHTML = 'SECTOR '+String.fromCharCode(69+ (state.sector%4)) +'&nbsp; '+ (state.sector%4)+'/4'; }

/* =========================================================
   GAME STATE
========================================================= */
const state = {
  running:false, hp:100, score:0, sector:0,
  cleared:0, killsThisWave:0,
  lastStepZ:0, stepPhase:0,
  yaw:0, pitch:0,
};

function startGame(){
  overlay.classList.add('hidden');
  audio(); // unlock
  // hard reset: remove every leftover guard/puff from a previous run so old
  // enemies never bleed into the new one
  guards.forEach(gd=> scene.remove(gd));
  guards.length = 0;
  puffs.forEach(p=> scene.remove(p));
  puffs.length = 0;
  state.running=true; state.hp=100; state.score=0; state.sector=0;
  state.cleared=0; state.killsThisWave=0; state.stepPhase=0;
  rig.position.set(0,0,0);
  spawnWave(0);
  setScore(0); renderHP(); setSector();
}
startBtn.addEventListener('click', startGame);

/* =========================================================
   INPUT : arcade aim-follow (NO pointer lock — works in the
   Streamlit iframe AND on touch screens) + click/tap fire
========================================================= */
const canvas = renderer.domElement;
const crossEl = document.getElementById('cross');

// aim in normalized device coords (-1..1). Starts centered.
const aim = { ndcX:0, ndcY:0, px:innerWidth/2, py:innerHeight/2 };

function setAimFromPoint(clientX, clientY){
  const r = canvas.getBoundingClientRect();
  const x = Math.max(r.left, Math.min(r.right,  clientX));
  const y = Math.max(r.top,  Math.min(r.bottom, clientY));
  aim.px = x - r.left;
  aim.py = y - r.top;
  aim.ndcX =  ( (x - r.left) / r.width  ) * 2 - 1;
  aim.ndcY = -( (y - r.top ) / r.height ) * 2 + 1;
  // move the crosshair DOM to the pointer
  crossEl.style.left = aim.px + 'px';
  crossEl.style.top  = aim.py + 'px';
}

/* ---- MOUSE ---- */
canvas.addEventListener('mousemove', (e)=> setAimFromPoint(e.clientX, e.clientY));
canvas.addEventListener('mousedown', (e)=>{
  if(!state.running) return;
  setAimFromPoint(e.clientX, e.clientY);
  fire();
});

/* ---- TOUCH (mobile) ---- */
canvas.addEventListener('touchstart', (e)=>{
  if(!state.running) return;
  const t = e.touches[0]; setAimFromPoint(t.clientX, t.clientY);
  fire();
  e.preventDefault();
}, {passive:false});
canvas.addEventListener('touchmove', (e)=>{
  const t = e.touches[0]; setAimFromPoint(t.clientX, t.clientY);
  e.preventDefault();
}, {passive:false});

/* ---- MOVEMENT : WASD / arrow keys, forward-back-left-right ---- */
const keys = { fwd:false, back:false, left:false, right:false };
function keyDir(e){
  const k = e.key.toLowerCase();
  if(k==='w'||k==='arrowup')    return 'fwd';
  if(k==='s'||k==='arrowdown')  return 'back';
  if(k==='a'||k==='arrowleft')  return 'left';
  if(k==='d'||k==='arrowright') return 'right';
  return null;
}
addEventListener('keydown', e=>{ const d=keyDir(e); if(d){ keys[d]=true; e.preventDefault?.(); } });
addEventListener('keyup',   e=>{ const d=keyDir(e); if(d){ keys[d]=false; } });

/* =========================================================
   FIRING
========================================================= */
const raycaster = new THREE.Raycaster();
const losRaycaster = new THREE.Raycaster();
const losFrom = new THREE.Vector3();
const losTo = new THREE.Vector3();
const losDir = new THREE.Vector3();
/* true if nothing in `collidables` blocks the line from a guard's chest to the player's camera */
function hasLineOfSight(gd){
  losFrom.set(gd.position.x, 1.4, gd.position.z);
  camera.getWorldPosition(losTo);
  losDir.subVectors(losTo, losFrom);
  const dist = losDir.length();
  losDir.normalize();
  losRaycaster.set(losFrom, losDir);
  losRaycaster.far = dist;
  const blocked = losRaycaster.intersectObjects(collidables, false);
  return blocked.length === 0;
}
let recoil = 0;
function fire(){
  gunshot();
  recoil = 0.16;
  pistol.userData.mflash.material.opacity = 1;
  pistol.userData.mflash.rotation.z = Math.random()*Math.PI;
  pistol.userData.glow.material.opacity = 0.9;
  muzzleLight.intensity = 7;

  raycaster.setFromCamera(new THREE.Vector2(aim.ndcX, aim.ndcY), camera);
  // check guards AND containers together so a container in front of a guard blocks the shot
  const combined = guardHitMeshes().concat(collidables);
  const hits = raycaster.intersectObjects(combined, false);
  if(hits.length && hits[0].object.userData.guard){
    const gd = hits[0].object.userData.guard;
    const headHit = hits[0].object === gd.userData.head || hits[0].object === gd.userData.helmet;
    gd.userData.hp -= headHit ? 2 : 1;
    hitSound();
    // blood puff
    puff(hits[0].point, 0xaa1518);
    if(gd.userData.hp<=0){ killGuard(gd); }
  } else if(hits.length){
    // hit a container instead — spark puff, no damage
    puff(hits[0].point, 0xd8d8c8);
  }
}

function killGuard(gd){
  gd.userData.alive=false;
  gd.userData.vy = 0; gd.userData.dying = true;
  state.score += 100; setScore(state.score);
  state.killsThisWave++;
  state.cleared = state.killsThisWave;
  clearEl.textContent = Math.min(state.killsThisWave,5);
  if(state.killsThisWave>=5){
    // advance
    state.killsThisWave = 0;
    beginAdvance();
  }
}

/* small particle puff */
const puffs = [];
function puff(pos, color){
  const g = new THREE.Group();
  for(let i=0;i<8;i++){
    const p = new THREE.Mesh(new THREE.SphereGeometry(0.05,6,6),
      new THREE.MeshBasicMaterial({ color, transparent:true, opacity:1 }));
    p.position.copy(pos);
    p.userData.v = new THREE.Vector3((Math.random()-.5)*3,(Math.random()*2),(Math.random()-.5)*3);
    g.add(p);
  }
  g.userData.life = 0.5; scene.add(g); puffs.push(g);
}

/* =========================================================
   AUTO ADVANCE : walk forward to next sector
========================================================= */
function beginAdvance(){
  state.sector++;
  setSector();
  // purge every guard from the previous wave (dead or not) before the next 5 spawn
  guards.forEach(gd=> scene.remove(gd));
  guards.length = 0;
  spawnWave(rig.position.z);
  clearEl.textContent = 0;
}

/* =========================================================
   RESIZE
========================================================= */
addEventListener('resize', ()=>{
  camera.aspect = innerWidth/innerHeight; camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});

/* =========================================================
   RED THREAT RINGS  (appear over nearby enemies, like the reference)
========================================================= */
const threatsEl = document.getElementById('threats');
const ringPool = [];               // reusable DOM rings
const projV = new THREE.Vector3();
function getRing(i){
  if(ringPool[i]) return ringPool[i];
  const d = document.createElement('div');
  d.className = 'threat';
  d.innerHTML = '<i class="tt"></i><i class="bb"></i>';
  threatsEl.appendChild(d);
  ringPool[i] = d; return d;
}
function updateThreats(){
  const r = renderer.domElement.getBoundingClientRect();
  let used = 0;
  guards.forEach(gd=>{
    if(!gd.userData.alive) return;
    const gap = rig.position.z - gd.position.z;      // distance in front of player
    if(gap > 55 || gap < 2) return;                  // only rings for nearby enemies
    if(!hasLineOfSight(gd)) return;                  // hidden behind a container = no threat marker
    // project the guard's chest to screen space
    projV.set(gd.position.x, 1.5, gd.position.z);
    projV.project(camera);
    if(projV.z > 1) return;                          // behind camera
    const x = (projV.x * 0.5 + 0.5) * r.width;
    const y = (-projV.y * 0.5 + 0.5) * r.height;
    const ring = getRing(used++);
    ring.style.display = 'block';
    ring.style.left = x + 'px';
    ring.style.top  = y + 'px';
    // closer = larger, brighter
    const scale = Math.max(0.6, Math.min(2.2, 26/Math.max(4,gap)));
    ring.style.transform = 'scale('+scale+')';
    ring.style.opacity = String(Math.max(0.35, 1 - gap/55));
  });
  for(let i=used;i<ringPool.length;i++){ ringPool[i].style.display='none'; }
}

/* =========================================================
   MAIN LOOP
========================================================= */
const clock = new THREE.Clock();
let beaconBlink = 0;

function animate(){
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const t = clock.elapsedTime;

  // water shimmer
  waterMat.metalness = 0.85 + Math.sin(t*0.7)*0.05;

  // beacon blink
  beaconBlink += dt;
  const on = (Math.sin(beaconBlink*4)>0);
  beacons.forEach(b=> b.material.color.setHex(on?0xff2a2a:0x330808));

  if(state.running){
    // camera look softly follows where you are aiming (arcade pan)
    const wantYaw   = -aim.ndcX * 0.42;
    const wantPitch =  aim.ndcY * 0.30;
    state.yaw   += (wantYaw   - state.yaw)   * Math.min(1, dt*8);
    state.pitch += (wantPitch - state.pitch) * Math.min(1, dt*8);
    camera.rotation.order='YXZ';
    camera.rotation.y = state.yaw;
    camera.rotation.x = state.pitch + recoil*0.5;
    // free movement — forward/back/left/right, independent of aim direction
    let mx = 0, mz = 0;
    if(keys.fwd)   mz -= 1;
    if(keys.back)  mz += 1;
    if(keys.left)  mx -= 1;
    if(keys.right) mx += 1;
    const isMoving = (mx !== 0 || mz !== 0);
    if(isMoving){
      const len = Math.hypot(mx, mz);
      mx /= len; mz /= len;
      const moveSpeed = 8.5;
      rig.position.x += mx * moveSpeed * dt;
      rig.position.z += mz * moveSpeed * dt;
      camera.position.y = 2.6 + Math.sin(t*10)*0.045;   // walking head-bob
      state.stepPhase += moveSpeed*dt;
      if(state.stepPhase > 1.3){ state.stepPhase = 0; footstep(false); }
    } else {
      camera.position.y = 2.6;
    }
    rig.position.x = Math.max(-DOCK_W/2+3, Math.min(DOCK_W/2-3, rig.position.x));
    rig.position.z = Math.max(-WORLD_LEN+80, Math.min(20, rig.position.z));

    // recoil recover
    recoil *= 0.82;
    pistol.position.z = -0.6 + recoil;
    pistol.userData.mflash.material.opacity *= 0.7;
    pistol.userData.glow.material.opacity *= 0.7;
    muzzleLight.intensity *= 0.75;

    // weapon idle sway
    weapon.position.x = Math.sin(t*1.3)*0.008;
    weapon.position.y = Math.sin(t*2.1)*0.006;

    /* ---- FOOTSTEP when passing a container cluster ---- */
    for(const cz of clusters){
      if(state.lastStepZ > cz && rig.position.z <= cz){
        footstep(true);   // heavier step passing a container
      }
    }
    state.lastStepZ = rig.position.z;

    /* ---- GUARD AI ---- */
    const ENGAGE_DIST = 20;   // distance at which a guard stops running and aims
    guards.forEach(gd=>{
      const u = gd.userData;
      if(u.alive){
        // face player
        gd.lookAt(rig.position.x, gd.position.y, rig.position.z);
        u.wobble += dt;
        u.flash.material.opacity *= 0.6;
        u.muzzleLight.intensity *= 0.6;

        const dz = gd.position.z - rig.position.z;   // how far ahead of player
        const gap = -dz;                             // positive distance in front
        u.engaged = gap <= ENGAGE_DIST;
        const moving = !u.engaged;

        if(moving){
          // ---- RUNNING toward the player ----
          const step = u.speed * dt;
          gd.position.z += step;
          gd.position.x += (rig.position.x - gd.position.x) * Math.min(1, dt*0.4);
          u.walkPhase += dt * 12;                     // fast sprint cadence
          const sw = Math.sin(u.walkPhase) * 1.0;
          u.legL.rotation.x =  sw;
          u.legR.rotation.x = -sw;
          u.armL.rotation.x = -0.25 + sw*0.7;          // arms pump opposite legs
          u.armR.rotation.x = -0.25 - sw*0.7;
          u.torso.rotation.x = 0.16;                   // forward sprint lean
          u.torso.position.y = 1.32 + Math.abs(Math.sin(u.walkPhase))*0.06;
          u.rifle.position.set(0.4, 1.1, 0.3);
          u.rifle.rotation.set(-0.1, 0, 0);
        } else {
          // ---- PLANTED & AIMING ----
          u.walkPhase += dt * 2;
          const idle = Math.sin(u.walkPhase) * 0.05;
          u.legL.rotation.x = idle;
          u.legR.rotation.x = -idle;
          u.torso.rotation.x = 0;
          u.torso.position.y = 1.32;
          u.armR.rotation.x = -1.4;                    // shoulder the rifle
          u.armL.rotation.x = -1.15;
          u.rifle.position.set(0.16, 1.52, -0.05);      // raised to aim down sights
          u.rifle.rotation.set(0, 0, 0);
        }

        // shoot at player once planted and in range, only with clear line of sight
        if(u.engaged){
          u.fireTimer -= dt;
          if(u.fireTimer<=0){
            u.fireTimer = u.fireCd;
            const canSee = hasLineOfSight(gd);
            if(canSee){
              u.flash.material.opacity = 1;
              u.muzzleLight.intensity = 4;
              // rifle recoil kick
              u.rifle.position.z -= 0.08;
              // chance to hit player
              if(Math.random()<0.5){
                state.hp = Math.max(0, state.hp - (6+Math.random()*8));
                renderHP(); hurtSound();
                dmgEl.style.boxShadow='inset 0 0 120px rgba(255,0,0,.55)';
                setTimeout(()=> dmgEl.style.boxShadow='inset 0 0 0 rgba(255,0,0,0)', 120);
                if(state.hp<=0) gameOver();
              }
            }
          }
        }
      } else if(u.dying){
        // ragdoll drop
        u.vy = (u.vy||0) - 9*dt;
        gd.position.y += u.vy*dt;
        gd.rotation.z += 2.4*dt;
        if(gd.position.y < -1.2){ u.dying=false; gd.visible=false; }
      }
    });

    /* ---- puffs ---- */
    for(let i=puffs.length-1;i>=0;i--){
      const g=puffs[i]; g.userData.life-=dt;
      g.children.forEach(p=>{ p.position.addScaledVector(p.userData.v, dt); p.material.opacity=Math.max(0,g.userData.life*2); });
      if(g.userData.life<=0){ scene.remove(g); puffs.splice(i,1); }
    }

    /* ---- red threat rings over nearby enemies ---- */
    updateThreats();
  } else {
    for(let i=0;i<ringPool.length;i++){ ringPool[i].style.display='none'; }
  }

  renderer.render(scene, camera);
}

function gameOver(){
  state.running=false;
  document.exitPointerLock?.();
  overlay.classList.remove('hidden');
  overlay.querySelector('h1').textContent='YOU WERE DOWNED';
  overlay.querySelectorAll('p')[0].innerHTML = 'Final score: <b>'+state.score+'</b> · Sectors cleared: <b>'+state.sector+'</b>';
  overlay.querySelectorAll('p')[1].textContent = 'Regroup and run the waterfront again.';
  startBtn.textContent='REDEPLOY';
}

/* boot */
loadingEl.classList.add('hidden');
animate();
</script>
</body>
</html>
"""

components.html(GAME_HTML, height=900, scrolling=False)
