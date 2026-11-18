import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

// Setup Scene, Camera, Renderer
const container = document.getElementById('canvas-container');
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0a0f1d);
scene.fog = new THREE.FogExp2(0x0a0f1d, 0.012);

const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.set(0, 32, 68);

const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false, powerPreference: 'high-performance' });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
container.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.05;
controls.maxPolarAngle = Math.PI / 2 - 0.02; // Don't go below floor
controls.minDistance = 10;
controls.maxDistance = 150;
controls.target.set(4, 5, 0);

// Lighting
const ambientLight = new THREE.AmbientLight(0xffffff, 0.85);
scene.add(ambientLight);

const dirLight = new THREE.DirectionalLight(0xffffff, 1.8);
dirLight.position.set(20, 50, 30);
dirLight.castShadow = true;
dirLight.shadow.mapSize.width = 2048;
dirLight.shadow.mapSize.height = 2048;
scene.add(dirLight);

const pointLight1 = new THREE.PointLight(0x38bdf8, 2.5, 60);
pointLight1.position.set(-20, 15, 10);
scene.add(pointLight1);

const pointLight2 = new THREE.PointLight(0xa855f7, 2.5, 60);
pointLight2.position.set(18, 18, 10);
scene.add(pointLight2);

// Ground Grid
const gridHelper = new THREE.GridHelper(160, 80, 0x3b82f6, 0x1e293b);
gridHelper.position.y = -0.05;
scene.add(gridHelper);

// Helper for text sprites
function createTextSprite(text, { color = '#ffffff', fontSize = 24, bg = 'rgba(15,23,42,0.85)', borderColor = '#38bdf8', padding = 8 } = {}) {
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  ctx.font = `bold ${fontSize}px "Segoe UI", Roboto, sans-serif`;
  const metrics = ctx.measureText(text);
  const textWidth = metrics.width;
  const w = textWidth + padding * 2;
  const h = fontSize + padding * 2 + 4;
  canvas.width = w * 2;
  canvas.height = h * 2;
  ctx.scale(2, 2);

  if (bg) {
    ctx.fillStyle = bg;
    ctx.roundRect ? ctx.roundRect(2, 2, w - 4, h - 4, 6) : ctx.rect(2, 2, w - 4, h - 4);
    ctx.fill();
  }
  if (borderColor) {
    ctx.strokeStyle = borderColor;
    ctx.lineWidth = 2;
    ctx.stroke();
  }
  ctx.fillStyle = color;
  ctx.font = `bold ${fontSize}px "Segoe UI", Roboto, sans-serif`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(text, w / 2, h / 2);

  const texture = new THREE.CanvasTexture(canvas);
  texture.minFilter = THREE.LinearFilter;
  const spriteMaterial = new THREE.SpriteMaterial({ map: texture, transparent: true });
  const sprite = new THREE.Sprite(spriteMaterial);
  sprite.scale.set(w * 0.055, h * 0.055, 1);
  return sprite;
}

// Global animated objects array
const animators = [];

// ============================================================
// STAGE 1: CAN Raw Stream & Input Validation (X = -36)
// ============================================================
const stage1Group = new THREE.Group();
stage1Group.position.set(-36, 0, 0);

// Platform base
const baseGeo1 = new THREE.BoxGeometry(14, 0.8, 18);
const baseMat1 = new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.4, metalness: 0.8 });
const base1 = new THREE.Mesh(baseGeo1, baseMat1);
base1.position.y = 0.4;
base1.receiveShadow = true;
stage1Group.add(base1);

// Stage Label
const s1Label = createTextSprite("STAGE 1: CAN RAW STREAM", { color: '#38bdf8', fontSize: 22 });
s1Label.position.set(0, 13, 0);
stage1Group.add(s1Label);

const s1Sub = createTextSprite("11-bit ID · DLC · 8B Payload · Monotonic Time", { color: '#94a3b8', fontSize: 14, bg: null, borderColor: null });
s1Sub.position.set(0, 11.5, 0);
stage1Group.add(s1Sub);

// Simulated incoming CAN frame cards
const framesGroup = new THREE.Group();
const frameColors = [0x0284c7, 0x0ea5e9, 0x38bdf8];
const frames = [];
for (let i = 0; i < 5; i++) {
  const fGeo = new THREE.BoxGeometry(4.2, 2.2, 0.4);
  const fMat = new THREE.MeshStandardMaterial({
    color: frameColors[i % 3],
    roughness: 0.2,
    metalness: 0.5,
    transparent: true,
    opacity: 0.95
  });
  const fMesh = new THREE.Mesh(fGeo, fMat);
  fMesh.position.set(0, 3 + i * 1.5, (i - 2) * 2.5);
  fMesh.castShadow = true;
  framesGroup.add(fMesh);
  frames.push(fMesh);
}
stage1Group.add(framesGroup);

// ID Stripper Blade (Mechanical Laser Guillotine)
const bladeGeo = new THREE.BoxGeometry(0.3, 9, 12);
const bladeMat = new THREE.MeshStandardMaterial({
  color: 0xef4444,
  emissive: 0xef4444,
  emissiveIntensity: 0.6,
  roughness: 0.1,
  metalness: 0.9,
  transparent: true,
  opacity: 0.85
});
const blade = new THREE.Mesh(bladeGeo, bladeMat);
blade.position.set(6, 5.5, 0);
stage1Group.add(blade);

const bladeLabel = createTextSprite("RAW-ID STRIPPER (11-BIT CLEAVE)", { color: '#ef4444', fontSize: 13, borderColor: '#ef4444' });
bladeLabel.position.set(6, 10.8, 0);
stage1Group.add(bladeLabel);

scene.add(stage1Group);

// ============================================================
// STAGE 2: Causal Sliding Window W=64 (X = -18)
// ============================================================
const stage2Group = new THREE.Group();
stage2Group.position.set(-18, 0, 0);

const base2 = new THREE.Mesh(new THREE.BoxGeometry(14, 0.8, 18), baseMat1);
base2.position.y = 0.4;
stage2Group.add(base2);

const s2Label = createTextSprite("STAGE 2: CAUSAL WINDOW (W = 64)", { color: '#10b981', fontSize: 22, borderColor: '#10b981' });
s2Label.position.set(0, 13, 0);
stage2Group.add(s2Label);

const s2Sub = createTextSprite("Non-overlapping Stride · Strict Within-File · Y_k = max(y_i)", { color: '#94a3b8', fontSize: 14, bg: null, borderColor: null });
s2Sub.position.set(0, 11.5, 0);
stage2Group.add(s2Sub);

// 3D Stack of 64 Frame slices (grouped into 8 block slabs)
const stackGroup = new THREE.Group();
const slabMeshes = [];
for (let s = 0; s < 8; s++) {
  const slabGeo = new THREE.BoxGeometry(6.5, 0.7, 8);
  const slabMat = new THREE.MeshStandardMaterial({
    color: 0x059669,
    roughness: 0.3,
    metalness: 0.6,
    transparent: true,
    opacity: 0.85
  });
  const slab = new THREE.Mesh(slabGeo, slabMat);
  slab.position.set(0, 1.8 + s * 0.9, 0);
  stackGroup.add(slab);
  slabMeshes.push(slab);
}
stage2Group.add(stackGroup);

// Scanning plane inside window buffer
const scanPlaneGeo = new THREE.BoxGeometry(7, 0.1, 8.5);
const scanPlaneMat = new THREE.MeshBasicMaterial({ color: 0x34d399, transparent: true, opacity: 0.75 });
const scanPlane = new THREE.Mesh(scanPlaneGeo, scanPlaneMat);
scanPlane.position.y = 5;
stage2Group.add(scanPlane);

animators.push((clock) => {
  scanPlane.position.y = 2 + (Math.sin(clock * 3) + 1) * 3.2;
});

scene.add(stage2Group);

// ============================================================
// STAGE 3: 32-D Structural Feature Matrix (X = 2)
// ============================================================
const stage3Group = new THREE.Group();
stage3Group.position.set(2, 0, 0);

const base3 = new THREE.Mesh(new THREE.BoxGeometry(18, 0.8, 20), baseMat1);
base3.position.y = 0.4;
stage3Group.add(base3);

const s3Label = createTextSprite("STAGE 3: 32-D STRUCTURAL TENSOR", { color: '#f59e0b', fontSize: 22, borderColor: '#f59e0b' });
s3Label.position.set(0, 14, 0);
stage3Group.add(s3Label);

const s3Sub = createTextSprite("Shape: (64, 32) · ID-Renaming Invariant · Zero Raw ID", { color: '#94a3b8', fontSize: 14, bg: null, borderColor: null });
s3Sub.position.set(0, 12.5, 0);
stage3Group.add(s3Sub);

// Decomposed 4 feature groups
const featureGroup = new THREE.Group();

// 1. Payload & Length Masks (17 dims: DLC 1 + Bytes 8 + Mask 8)
const pBlockGeo = new THREE.BoxGeometry(2.4, 7, 7);
const pBlockMat = new THREE.MeshStandardMaterial({ color: 0x38bdf8, roughness: 0.3, metalness: 0.7 });
const pBlock = new THREE.Mesh(pBlockGeo, pBlockMat);
pBlock.position.set(-5, 4.5, 0);
featureGroup.add(pBlock);

const pLabel = createTextSprite("Payload & Masks\n[0..16] (17-D)", { color: '#38bdf8', fontSize: 13, borderColor: '#38bdf8' });
pLabel.position.set(-5, 9, 0);
featureGroup.add(pLabel);

// 2. Delta-Payload Same-ID (9 dims: Delta bytes 8 + Flag 1)
const dBlockGeo = new THREE.BoxGeometry(2.0, 7, 7);
const dBlockMat = new THREE.MeshStandardMaterial({ color: 0x10b981, roughness: 0.3, metalness: 0.7 });
const dBlock = new THREE.Mesh(dBlockGeo, dBlockMat);
dBlock.position.set(-1.8, 4.5, 0);
featureGroup.add(dBlock);

const dLabel = createTextSprite("Δ-Payload Same-ID\n[17..25] (9-D)", { color: '#10b981', fontSize: 13, borderColor: '#10b981' });
dLabel.position.set(-1.8, 9, 0);
featureGroup.add(dLabel);

// 3. Timing Dynamics (2 dims: Δt inter-frame & Δt same-ID)
const tBlockGeo = new THREE.BoxGeometry(1.2, 7, 7);
const tBlockMat = new THREE.MeshStandardMaterial({ color: 0xf59e0b, roughness: 0.3, metalness: 0.7 });
const tBlock = new THREE.Mesh(tBlockGeo, tBlockMat);
tBlock.position.set(1.2, 4.5, 0);
featureGroup.add(tBlock);

const tLabel = createTextSprite("Timing Δt\n[26..27] (2-D)", { color: '#f59e0b', fontSize: 13, borderColor: '#f59e0b' });
tLabel.position.set(1.2, 9, 0);
featureGroup.add(tLabel);

// 4. Local ID Topology & Bigrams (4 dims: freq, rank_distinct, rank_w, transition_bigram)
const topBlockGeo = new THREE.BoxGeometry(1.6, 7, 7);
const topBlockMat = new THREE.MeshStandardMaterial({ color: 0xa855f7, roughness: 0.3, metalness: 0.7 });
const topBlock = new THREE.Mesh(topBlockGeo, topBlockMat);
topBlock.position.set(4.0, 4.5, 0);
featureGroup.add(topBlock);

const topLabel = createTextSprite("Local Topology\n[28..31] (4-D)", { color: '#a855f7', fontSize: 13, borderColor: '#a855f7' });
topLabel.position.set(4.0, 9, 0);
featureGroup.add(topLabel);

stage3Group.add(featureGroup);
scene.add(stage3Group);

// ============================================================
// STAGE 4: Transformer Deep Neural Core (X = 22)
// ============================================================
const stage4Group = new THREE.Group();
stage4Group.position.set(22, 0, 0);

const base4 = new THREE.Mesh(new THREE.BoxGeometry(16, 0.8, 20), baseMat1);
base4.position.y = 0.4;
stage4Group.add(base4);

const s4Label = createTextSprite("STAGE 4: TRANSFORMER ENCODER", { color: '#ec4899', fontSize: 22, borderColor: '#ec4899' });
s4Label.position.set(0, 14, 0);
stage4Group.add(s4Label);

const s4Sub = createTextSprite("d_model=64 · 2 Layers · 4 Heads · Mean Pooling → MLP", { color: '#94a3b8', fontSize: 14, bg: null, borderColor: null });
s4Sub.position.set(0, 12.5, 0);
stage4Group.add(s4Sub);

// 2 Transformer Encoder Stack
const tfLayer1 = new THREE.Mesh(
  new THREE.BoxGeometry(9, 2.2, 9),
  new THREE.MeshStandardMaterial({ color: 0x9333ea, roughness: 0.3, metalness: 0.8, transparent: true, opacity: 0.85 })
);
tfLayer1.position.y = 3;
stage4Group.add(tfLayer1);

const tfL1Text = createTextSprite("Layer 1: 4 Attention Heads", { color: '#f3e8ff', fontSize: 12, bg: null, borderColor: null });
tfL1Text.position.set(0, 3, 4.8);
stage4Group.add(tfL1Text);

const tfLayer2 = new THREE.Mesh(
  new THREE.BoxGeometry(9, 2.2, 9),
  new THREE.MeshStandardMaterial({ color: 0x7e22ce, roughness: 0.3, metalness: 0.8, transparent: true, opacity: 0.85 })
);
tfLayer2.position.y = 6.2;
stage4Group.add(tfLayer2);

const tfL2Text = createTextSprite("Layer 2: Feed-Forward (d_ff=128)", { color: '#f3e8ff', fontSize: 12, bg: null, borderColor: null });
tfL2Text.position.set(0, 6.2, 4.8);
stage4Group.add(tfL2Text);

// Mean Pooling Funnel (Aggregator)
const poolGeo = new THREE.ConeGeometry(3.6, 2.2, 32);
const poolMat = new THREE.MeshStandardMaterial({ color: 0xd946ef, roughness: 0.2, metalness: 0.8 });
const poolMesh = new THREE.Mesh(poolGeo, poolMat);
poolMesh.rotation.x = Math.PI;
poolMesh.position.y = 8.8;
stage4Group.add(poolMesh);

const poolText = createTextSprite("Mean Pooling: 64 tokens → 1 vector (64-D)", { color: '#f472b6', fontSize: 12 });
poolText.position.set(0, 8.8, 3.8);
stage4Group.add(poolText);

// MLP Head (Linear 64->32->2)
const mlpGeo = new THREE.CylinderGeometry(1.4, 1.4, 1.8, 24);
const mlpMat = new THREE.MeshStandardMaterial({ color: 0xf43f5e, roughness: 0.3, metalness: 0.7 });
const mlpMesh = new THREE.Mesh(mlpGeo, mlpMat);
mlpMesh.position.y = 10.8;
stage4Group.add(mlpMesh);

const mlpText = createTextSprite("MLP Classifier: Logits (z0, z1)", { color: '#fb7185', fontSize: 12 });
mlpText.position.set(0, 10.8, 3.2);
stage4Group.add(mlpText);

// Attention beams inside Transformer
const beamGroup = new THREE.Group();
const beams = [];
for (let b = 0; b < 6; b++) {
  const lineGeo = new THREE.BufferGeometry().setFromPoints([
    new THREE.Vector3(-3.5 + Math.random() * 7, 2, -3.5 + Math.random() * 7),
    new THREE.Vector3(-3.5 + Math.random() * 7, 7.2, -3.5 + Math.random() * 7)
  ]);
  const lineMat = new THREE.LineBasicMaterial({ color: 0xf472b6, transparent: true, opacity: 0.7 });
  const line = new THREE.Line(lineGeo, lineMat);
  beamGroup.add(line);
  beams.push(line);
}
stage4Group.add(beamGroup);

scene.add(stage4Group);

// ============================================================
// STAGE 5: Source Threshold & Domain Shift Transfer (X = 42)
// ============================================================
const stage5Group = new THREE.Group();
stage5Group.position.set(42, 0, 0);

const base5 = new THREE.Mesh(new THREE.BoxGeometry(18, 0.8, 22), baseMat1);
base5.position.y = 0.4;
stage5Group.add(base5);

const s5Label = createTextSprite("STAGE 5: ZERO-SHOT DOMAIN SHIFT", { color: '#38bdf8', fontSize: 22, borderColor: '#38bdf8' });
s5Label.position.set(0, 15, 0);
stage5Group.add(s5Label);

const s5Sub = createTextSprite("Frozen Model & Threshold τ · FAR ≤ 100/100,000 Budget", { color: '#94a3b8', fontSize: 14, bg: null, borderColor: null });
s5Sub.position.set(0, 13.5, 0);
stage5Group.add(s5Sub);

// Threshold Barrier (Laser Gateway at tau = 0.50)
const gateGeo = new THREE.BoxGeometry(0.3, 10, 16);
const gateMat = new THREE.MeshStandardMaterial({
  color: 0x38bdf8,
  emissive: 0x0284c7,
  emissiveIntensity: 0.5,
  transparent: true,
  opacity: 0.45,
  roughness: 0.1
});
const gate = new THREE.Mesh(gateGeo, gateMat);
gate.position.set(-6, 6, 0);
stage5Group.add(gate);

const gateText = createTextSprite("FROZEN THRESHOLD BARRIER\nτ = 0.50 (FAR ≤ 100/100k)", { color: '#38bdf8', fontSize: 13, borderColor: '#38bdf8' });
gateText.position.set(-6, 12, 0);
stage5Group.add(gateText);

// 4 Transfer Condition Pods (A, B, C, D)
const conditions = [
  { name: "Set A: Known Vehicle\nKnown Attack (In-domain)", z: -6.5, color: 0x10b981 },
  { name: "★ Set B: VEHICLE SHIFT\nImpala → Silverado / Forester", z: -2.2, color: 0x38bdf8, highlight: true },
  { name: "Set C: Attack Shift\nKnown Car → Unseen Attack", z: 2.2, color: 0xf59e0b },
  { name: "Set D: Dual Shift\nUnseen Car → Unseen Attack", z: 6.5, color: 0xef4444 },
];

conditions.forEach((c) => {
  const cGeo = new THREE.CylinderGeometry(1.6, 1.8, 1.4, 20);
  const cMat = new THREE.MeshStandardMaterial({
    color: c.color,
    roughness: 0.3,
    metalness: 0.8,
    emissive: c.highlight ? c.color : 0x000000,
    emissiveIntensity: c.highlight ? 0.4 : 0
  });
  const cMesh = new THREE.Mesh(cGeo, cMat);
  cMesh.position.set(0, 1.6, c.z);
  stage5Group.add(cMesh);

  const cText = createTextSprite(c.name, { color: c.highlight ? '#38bdf8' : '#e2e8f0', fontSize: 11, borderColor: c.highlight ? '#38bdf8' : null });
  cText.position.set(0, 3.2, c.z);
  stage5Group.add(cText);
});

// Final Decision Output Orbs
const benignOrb = new THREE.Mesh(
  new THREE.SphereGeometry(1.8, 32, 32),
  new THREE.MeshStandardMaterial({ color: 0x22c55e, emissive: 0x22c55e, emissiveIntensity: 0.7, roughness: 0.1 })
);
benignOrb.position.set(6, 6, -4);
stage5Group.add(benignOrb);

const bLabel = createTextSprite("BENIGN (NORMAL)\np < τ (Passed)", { color: '#22c55e', fontSize: 13, borderColor: '#22c55e' });
bLabel.position.set(6, 8.8, -4);
stage5Group.add(bLabel);

const attackOrb = new THREE.Mesh(
  new THREE.SphereGeometry(1.8, 32, 32),
  new THREE.MeshStandardMaterial({ color: 0xef4444, emissive: 0xef4444, emissiveIntensity: 0.8, roughness: 0.1 })
);
attackOrb.position.set(6, 6, 4);
stage5Group.add(attackOrb);

const aLabel = createTextSprite("ATTACK DETECTED\np ≥ τ (ALARM)", { color: '#ef4444', fontSize: 13, borderColor: '#ef4444' });
aLabel.position.set(6, 8.8, 4);
stage5Group.add(aLabel);

scene.add(stage5Group);

// ============================================================
// Inter-Stage Connecting Data Conduits (Laser Tubes)
// ============================================================
function createConduit(p1, p2, color = 0x38bdf8) {
  const curve = new THREE.LineCurve3(p1, p2);
  const tubeGeo = new THREE.TubeGeometry(curve, 20, 0.25, 12, false);
  const tubeMat = new THREE.MeshStandardMaterial({ color, emissive: color, emissiveIntensity: 0.6, roughness: 0.2 });
  const tube = new THREE.Mesh(tubeGeo, tubeMat);
  scene.add(tube);
}

createConduit(new THREE.Vector3(-29, 4.5, 0), new THREE.Vector3(-25, 4.5, 0), 0x0284c7);
createConduit(new THREE.Vector3(-11, 4.5, 0), new THREE.Vector3(-7, 4.5, 0), 0x10b981);
createConduit(new THREE.Vector3(11, 4.5, 0), new THREE.Vector3(14, 4.5, 0), 0xf59e0b);
createConduit(new THREE.Vector3(30, 8.8, 0), new THREE.Vector3(34, 6.0, 0), 0xec4899);

// Data Particles streaming between stages
const particleGeo = new THREE.SphereGeometry(0.2, 12, 12);
const particleMat = new THREE.MeshBasicMaterial({ color: 0x38bdf8 });
const particles = [];
for (let p = 0; p < 25; p++) {
  const part = new THREE.Mesh(particleGeo, particleMat);
  part.position.set(-42 + p * 3.5, 4.5 + (Math.random() - 0.5) * 0.5, (Math.random() - 0.5) * 0.5);
  scene.add(part);
  particles.push(part);
}

animators.push((clock) => {
  particles.forEach((part, idx) => {
    part.position.x += 0.35;
    if (part.position.x > 48) part.position.x = -44;
  });
});

// ============================================================
// Camera Animations & Navigation Focus Points
// ============================================================
let targetCamPos = camera.position.clone();
let targetLookAt = controls.target.clone();
let animatingCam = false;

function setCameraFocus(pos, lookAt) {
  targetCamPos.copy(pos);
  targetLookAt.copy(lookAt);
  animatingCam = true;
}

window.focusStage = function(stageIdx) {
  document.querySelectorAll('.stage-btn').forEach((btn, idx) => {
    if (idx === stageIdx) btn.classList.add('active');
    else btn.classList.remove('active');
  });

  if (stageIdx === 0) {
    // Full Overview
    setCameraFocus(new THREE.Vector3(4, 38, 72), new THREE.Vector3(4, 5, 0));
    updateDrawer("TOÀN CẢNH PIPELINE ĐỀ XUẤT", `
      <p>Pipeline nghiên cứu phương pháp phát hiện xâm nhập mạng CAN khi có <strong>dịch chuyển dòng xe (Vehicle Shift)</strong> và <strong>kiểu tấn công (Attack Shift)</strong>.</p>
      <div class="stat-grid">
        <div class="stat-box"><div class="stat-val">32-D</div><div class="stat-label">Biểu diễn cấu trúc</div></div>
        <div class="stat-box"><div class="stat-val">W=64</div><div class="stat-label">Cửa sổ liên tiếp</div></div>
        <div class="stat-box"><div class="stat-val">Zero-Shot</div><div class="stat-label">Chuyển giao xe lạ</div></div>
        <div class="stat-box"><div class="stat-val">≤100/100k</div><div class="stat-label">Ngân sách FAR nguồn</div></div>
      </div>
      <p>5 công đoạn liên hoàn loại bỏ hoàn toàn 11-bit CAN-ID thô, nắm bắt tương quan qua Attention, và kiểm chứng trên 4 điều kiện A/B/C/D.</p>
    `);
  } else if (stageIdx === 1) {
    // Stage 1: Raw CAN
    setCameraFocus(new THREE.Vector3(-36, 14, 25), new THREE.Vector3(-36, 5, 0));
    updateDrawer("STAGE 1: CAN RAW STREAM & INPUT CONTRACT", `
      <p><strong>Dữ liệu đầu vào:</strong> Các log CAN thô gồm 4 trường cốt lõi: <code>timestamp</code>, <code>arbitration_id</code>, <code>data_field</code>, <code>attack</code>.</p>
      <ul>
        <li><strong>Kiểm tra Schema nghiêm ngặt:</strong> Chỉ nhận CAN cổ điển 11-bit (0x000 - 0x7FF), payload hex chẵn ≤ 8 bytes.</li>
        <li><strong>Chống đảo ngược thời gian:</strong> Timestamp phải hữu hạn và đơn điệu tăng (t_i ≥ t_{i-1}). Dữ liệu xáo trộn bị dừng ngay.</li>
        <li><strong>ID Stripper:</strong> Lưỡi gạt cơ khí cắt bỏ 11-bit ID thô trước khi đưa vào mô hình để triệt tiêu việc học thuộc lòng nhãn xe.</li>
      </ul>
    `);
  } else if (stageIdx === 2) {
    // Stage 2: Window W=64
    setCameraFocus(new THREE.Vector3(-18, 14, 25), new THREE.Vector3(-18, 5, 0));
    updateDrawer("STAGE 2: CAUSAL WINDOWING (W = 64)", `
      <p><strong>Cửa sổ trượt nhân quả:</strong> Gom cụm 64 khung tin liên tiếp không chồng lặp (stride = 64).</p>
      <ul>
        <li><strong>Ranh giới file tuyệt đối:</strong> Cửa sổ không bao giờ nối tắt qua biên file khác để tránh rò rỉ ngữ cảnh giữa các phiên lái.</li>
        <li><strong>Bảo toàn lịch sử qua I/O Chunks:</strong> Từ điển <code>history[ID] = (t_trước, payload_trước)</code> được duy trì liên tục qua các khối đọc dữ liệu.</li>
        <li><strong>Nhãn cửa sổ:</strong> Y_k = max(y_i) ∈ {0, 1}. Chỉ cần 1 frame mang nhãn tấn công, cả cửa sổ là Dương tính.</li>
      </ul>
    `);
  } else if (stageIdx === 3) {
    // Stage 3: 32-D Features
    setCameraFocus(new THREE.Vector3(2, 16, 26), new THREE.Vector3(2, 5, 0));
    updateDrawer("STAGE 3: BIỂU DIỄN CẤU TRÚC 32 CHIỀU", `
      <p><strong>Đột phá cốt lõi:</strong> Thay thế hoàn toàn 11 bit ID bằng ma trận cấu trúc 32 chiều bất biến với phép đổi tên ID (1-to-1 permutation invariant):</p>
      <ul>
        <li><span class="badge badge-cyan">[0..16] Payload & Masks (17-D)</span>: d_i / 8, 8 bytes payload (/255), 8 mặt nạ nhị phân.</li>
        <li><span class="badge badge-green">[17..25] Biến thiên cùng ID (9-D)</span>: |b_i - b_q| đo độ giật payload của cùng tín hiệu + cờ lịch sử.</li>
        <li><span class="badge badge-amber">[26..27] Nhịp thời gian (2-D)</span>: log(1 + 1000·min(Δt, 10)) cho nhịp liên tiếp và nhịp cùng ID.</li>
        <li><span class="badge badge-purple">[28..31] Topology cục bộ (4-D)</span>: Tần suất ID trong cửa sổ, thứ tự xuất hiện, và tần suất cặp chuyển tiếp bigram.</li>
      </ul>
    `);
  } else if (stageIdx === 4) {
    // Stage 4: Transformer
    setCameraFocus(new THREE.Vector3(22, 18, 28), new THREE.Vector3(22, 6, 0));
    updateDrawer("STAGE 4: TRANSFORMER DEEP ENCODER", `
      <p><strong>Kiến trúc mạng nơ-ron:</strong> Mô hình chú ý chụp bắt mối tương quan ngữ cảnh đa chiều giữa 64 khung tin liên tiếp.</p>
      <ul>
        <li><strong>Linear Projection & Positional Embedding:</strong> Chiếu 32 chiều lên 64 chiều (d_model=64) + cộng vector vị trí thứ tự thời gian.</li>
        <li><strong>2 tầng Transformer Encoder:</strong> 4 Attention Heads, Feed-Forward 128, kích hoạt GELU, Dropout 0.1.</li>
        <li><strong>Mean Pooling:</strong> Gom 64 vector thời gian thành 1 vector đặc trưng toàn cục duy nhất (64-D).</li>
        <li><strong>MLP Head:</strong> LayerNorm → Linear(64→32) → ReLU → Linear(32→2) đưa ra phân bố xác suất p(attack).</li>
      </ul>
    `);
  } else if (stageIdx === 5) {
    // Stage 5: Domain Shift & Threshold
    setCameraFocus(new THREE.Vector3(42, 18, 28), new THREE.Vector3(42, 6, 0));
    updateDrawer("STAGE 5: SOURCE CALIBRATION & DOMAIN SHIFT", `
      <p><strong>Hiệu chuẩn nghiêm ngặt từ nguồn & Đánh giá Zero-Shot:</strong></p>
      <ul>
        <li><strong>Ngưỡng hiệu chuẩn τ:</strong> Chọn trên Validation nguồn sao cho tối đa hóa Recall và khống chế <strong>FAR ≤ 100 / 100.000 cửa sổ lành</strong>.</li>
        <li><strong>Đóng băng tuyệt đối (Frozen Zero-Shot):</strong> Khi đem sang xe lạ (Set B, D), mô hình và ngưỡng τ không được chỉnh lại.</li>
        <li><strong>Thử thách 4 điều kiện benchmark:</strong>
          <br>• <strong>Set A</strong>: Xe quen - Tấn công quen (Đối chứng).
          <br>• <strong>Set B (Trọng tâm)</strong>: Xe lạ - Tấn công quen (Impala→Silverado / Traverse→Forester).
          <br>• <strong>Set C</strong>: Xe quen - Tấn công lạ.
          <br>• <strong>Set D</strong>: Xe lạ - Tấn công lạ (Thử thách kép).
        </li>
      </ul>
    `);
  }
};

// Simulation Mode Switcher (Normal vs DoS vs Fuzzing)
let simMode = 'normal';
window.setSimulationMode = function(mode) {
  simMode = mode;
  document.querySelectorAll('.mode-btn').forEach(btn => btn.classList.remove('active'));
  document.getElementById('btn-' + mode)?.classList.add('active');

  const hudStatus = document.getElementById('hud-status');
  const hudScore = document.getElementById('hud-score');
  const hudDt = document.getElementById('hud-dt');
  const hudDpay = document.getElementById('hud-dpay');

  if (mode === 'normal') {
    benignOrb.scale.set(1.4, 1.4, 1.4);
    attackOrb.scale.set(1.0, 1.0, 1.0);
    benignOrb.material.emissiveIntensity = 1.0;
    attackOrb.material.emissiveIntensity = 0.2;
    gateMat.color.setHex(0x38bdf8);
    hudStatus.innerHTML = '<span style="color:#22c55e">● BENIGN (Impala→Silverado PASS)</span>';
    hudScore.textContent = 'p = 0.04 < τ (0.50)';
    hudDt.textContent = '10.4 ms (Chu kỳ ổn định)';
    hudDpay.textContent = '0.02 (Biến thiên nhỏ)';
  } else if (mode === 'dos') {
    benignOrb.scale.set(1.0, 1.0, 1.0);
    attackOrb.scale.set(1.5, 1.5, 1.5);
    benignOrb.material.emissiveIntensity = 0.2;
    attackOrb.material.emissiveIntensity = 1.2;
    gateMat.color.setHex(0xef4444);
    hudStatus.innerHTML = '<span style="color:#ef4444">▲ ATTACK: DoS FLOODING (ALARM)</span>';
    hudScore.textContent = 'p = 0.98 ≥ τ (Trigger Cảnh báo)';
    hudDt.textContent = '0.12 ms (Sập nhịp thời gian)';
    hudDpay.textContent = '0.00 (Payload không đổi)';
  } else if (mode === 'fuzz') {
    benignOrb.scale.set(1.0, 1.0, 1.0);
    attackOrb.scale.set(1.5, 1.5, 1.5);
    benignOrb.material.emissiveIntensity = 0.2;
    attackOrb.material.emissiveIntensity = 1.2;
    gateMat.color.setHex(0xf59e0b);
    hudStatus.innerHTML = '<span style="color:#f59e0b">▲ ATTACK: PAYLOAD FUZZING (ALARM)</span>';
    hudScore.textContent = 'p = 0.92 ≥ τ (Trigger Cảnh báo)';
    hudDt.textContent = '9.8 ms (Chu kỳ bình thường)';
    hudDpay.textContent = '0.84 (Đột biến dữ liệu)';
  }
};

function updateDrawer(title, html) {
  document.getElementById('drawer-title').textContent = title;
  document.getElementById('drawer-content').innerHTML = html;
}

// Window resize handler
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// Render Loop
const clock = new THREE.Clock();

function animate() {
  requestAnimationFrame(animate);
  const time = clock.getElapsedTime();

  // Smooth camera transitions
  if (animatingCam) {
    camera.position.lerp(targetCamPos, 0.06);
    controls.target.lerp(targetLookAt, 0.06);
    if (camera.position.distanceTo(targetCamPos) < 0.2 && controls.target.distanceTo(targetLookAt) < 0.2) {
      animatingCam = false;
    }
  }

  // Run dynamic animators
  animators.forEach(fn => fn(time));

  // Pulse Attention Beams in Transformer
  beams.forEach((beam, idx) => {
    beam.material.opacity = 0.3 + Math.sin(time * 6 + idx) * 0.4;
  });

  // Oscillate incoming frame cards
  frames.forEach((f, idx) => {
    f.position.y = 3 + idx * 1.5 + Math.sin(time * 2 + idx) * 0.2;
  });

  controls.update();
  renderer.render(scene, camera);
}

animate();
window.setSimulationMode('normal');
