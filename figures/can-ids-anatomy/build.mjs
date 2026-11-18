import { writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import * as k from "file:///C:/Users/tuant/.agents/skills/anatomy/kit/iso-kit.mjs";
import { kitScript } from "file:///C:/Users/tuant/.agents/skills/anatomy/scripts/inline-kit.mjs";

const HERE = dirname(fileURLToPath(import.meta.url));
const theme = process.argv.includes("--light") ? "light" : "dark";

const WIDTH = 680;
const HEIGHT = 440;

// Surface Plate dimensions
const PLATE = { x: -140, y: -72, w: 280, d: 144, r: 8 };
const PLATE_H = 12;
const FOOT_H = 6;

// Guide rails along X axis
const RAIL_Y1 = -20;
const RAIL_Y2 = 20;
const RAIL_X_FROM = -100;
const RAIL_X_TO = 38;
const RAIL_H = 3.6;

// Sliding Carriage (Window W=64)
const CARRIAGE_W = 68;
const CARRIAGE_D = 50;
const CARRIAGE_Z = 3.6;
const CARRIAGE_H = 6.4;
const CARRIAGE_TOP = CARRIAGE_Z + CARRIAGE_H;

// Station 1: ID Stripper Guillotine (Left, x = -72)
const STRIP_X = -72;
const STRIP_POST_Y1 = -30;
const STRIP_POST_Y2 = 30;
const STRIP_POST_H = 68;

// Station 2: Dual Sprung Probes (Center, x = -20)
const PROBE_X = -20;
const PROBE_BASE_Y = -48;
const PROBE_ARM_Z = 74;

// Station 3: Transformer 4-Head Attention Arch (Center-Right, x = 18)
const ARCH_X = 18;
const ARCH_Y1 = -28;
const ARCH_Y2 = 28;
const ARCH_Z = 82;

// Station 4: Dial Indicator (Far Right, x = 86, y = 0)
const DIAL = [86, 0];
const DIAL_R = 25;
const DIAL_Z = 82;
const DIAL_H = 10;
const DIAL_TOP = DIAL_Z + DIAL_H;

// Fit projection
const P = k.fitProjection(
  [
    ...k.boxCorners(PLATE, -PLATE_H - FOOT_H, 0),
    [STRIP_X, STRIP_POST_Y1, STRIP_POST_H + 4],
    [PROBE_X, PROBE_BASE_Y, PROBE_ARM_Z + 10],
    [ARCH_X, 0, ARCH_Z + 6],
    [DIAL[0] + DIAL_R + 6, 0, DIAL_TOP + 10],
  ],
  WIDTH,
  HEIGHT,
  { pad: 32, azimuth: 43 }
);

const at = (point) => k.iso(point, P);
const S = (paths, style) => k.solidSvg(paths, style);
const L = (d, style) => k.lineSvg(d, style);
const D = (points, style) => k.dotsSvg(points, style);
const byDepth = (points) => [...points].sort((a, b) => k.depthOf([a[0], a[1], 0], P) - k.depthOf([b[0], b[1], 0], P));

// 1. Base plate, feet, ruler, and brass badge
function plate() {
  const out = [`<path class="iso-halo" d="${k.haloOf(PLATE, -PLATE_H - FOOT_H, PLATE_H, P)}"/>`];
  
  // 4 Vibration isolation feet
  for (const [x, y] of byDepth(k.corners(PLATE, 24))) {
    out.push(S(k.cylinder(x, y, 7.5, -PLATE_H - FOOT_H, 2, P, 28), { tone: "lo" }));
    out.push(S(k.cylinder(x, y, 5.8, -PLATE_H - FOOT_H + 2, FOOT_H - 2, P, 28), { tone: "mid" }));
  }
  
  // Main beveled cast-iron slab
  out.push(S(k.slabOf(PLATE, -PLATE_H, PLATE_H, P, 8, 1.6), { tone: "mid" }));
  
  // Perimeter groove inset 5
  out.push(L(k.planOutline(k.insetPlan(PLATE, 5), 0, P), { tone: "lo" }));
  
  // 4 Corner screws with rings
  const screws = k.corners(PLATE, 11);
  out.push(L(screws.map(([x, y]) => k.ring(x, y, 2.4, 0, P, 16)).join(""), { tone: "lo" }));
  out.push(D(screws.map(([x, y]) => at([x, y, 0])), { size: 0.5 }));
  
  // Front millimeter inspection ruler strip
  const strip = { x: -110, y: PLATE.y + PLATE.d - 14, w: 220, d: 7, r: 1.2 };
  out.push(S(k.slabOf(strip, 0, 0.8, P, 3), { tone: "lo", crease: "none" }));
  const ticks = k.topTicks(strip.x + 4, strip.x + strip.w - 4, 4, 5, strip.y + 0.9, 0.8, [1.8, 3.4], P);
  out.push(L(ticks.minor, { tone: "lo" }), L(ticks.major, { tone: "mid" }));
  
  // Engraved brass specification badge on the left
  const badge = { x: -128, y: -58, w: 46, d: 24, r: 2 };
  out.push(S(k.slabOf(badge, 0, 0.8, P, 3), { tone: "hi", crease: "lo" }));
  out.push(L(k.planOutline(k.insetPlan(badge, 1.8), 0.8, P), { tone: "mid" }));
  // 3 rule lines representing text on brass badge
  out.push(
    L(k.lineOnTop([badge.x + 4, badge.y + 6], [badge.x + badge.w - 4, badge.y + 6], 0.8, P), { tone: "lo", free: true }),
    L(k.lineOnTop([badge.x + 4, badge.y + 12], [badge.x + badge.w - 8, badge.y + 12], 0.8, P), { tone: "lo", free: true }),
    L(k.lineOnTop([badge.x + 4, badge.y + 18], [badge.x + badge.w - 14, badge.y + 18], 0.8, P), { tone: "lo", free: true })
  );
  const badgeScrews = k.corners(badge, 3);
  out.push(D(badgeScrews.map(([x, y]) => at([x, y, 0.8])), { size: 0.35 }));
  
  return out.join("");
}

// 2. Guide Rails and Pillow Blocks
function rails() {
  const out = [];
  const rw = RAIL_X_TO - RAIL_X_FROM;
  
  // Dual precision rails
  for (const ry of [RAIL_Y1, RAIL_Y2]) {
    out.push(S(k.slabOf({ x: RAIL_X_FROM, y: ry - 2.5, w: rw, d: 5, r: 1 }, 0, RAIL_H, P, 3, 0.5), { tone: "mid" }));
    // Center polished rail cylinder
    out.push(S(k.cylinder(RAIL_X_FROM + rw / 2, ry, 2.2, RAIL_H, 2.2, P, 24), { tone: "hi", crease: "none" }));
  }
  
  // End stops at both extremities
  for (const rx of [RAIL_X_FROM - 5, RAIL_X_TO]) {
    out.push(S(k.slabOf({ x: rx, y: -26, w: 5, d: 52, r: 1.5 }, 0, 8, P, 3, 0.6), { tone: "mid" }));
    out.push(D([at([rx + 2.5, RAIL_Y1, 8]), at([rx + 2.5, RAIL_Y2, 8])], { size: 0.45 }));
  }
  
  return out.join("");
}

// 3. Station 1: The ID Stripper Guillotine
function stationIDStripper() {
  const out = [];
  // Twin vertical pillars
  for (const py of [STRIP_POST_Y1, STRIP_POST_Y2]) {
    out.push(S(k.cylinder(STRIP_X, py, 4.6, 0, STRIP_POST_H, P, 28, 0.6), { tone: "mid" }));
    out.push(S(k.cylinder(STRIP_X, py, 5.4, 0, 3, P, 28), { tone: "lo" })); // base ring
    out.push(S(k.cylinder(STRIP_X, py, 5.2, STRIP_POST_H, 2.4, P, 28), { tone: "hi" })); // cap
  }
  
  // Crosshead bar spanning pillars
  const cross = { x: STRIP_X - 5, y: STRIP_POST_Y1 - 2, w: 10, d: (STRIP_POST_Y2 - STRIP_POST_Y1) + 4, r: 2 };
  out.push(S(k.slabOf(cross, STRIP_POST_H - 12, 12, P, 4, 0.8), { tone: "hi" }));
  
  // Central guillotine shear block (Lưỡi gạt 11-bit ID)
  const shearWedge = { x: STRIP_X - 3.5, y: -16, w: 7, d: 32, r: 1.5 };
  out.push(S(k.slabOf(shearWedge, 24, STRIP_POST_H - 36, P, 3, 0.5), { tone: "mid" }));
  
  // Wedge blade bevel pointing downwards
  const blade = { x: STRIP_X - 2, y: -14, w: 4, d: 28, r: 0.8 };
  out.push(S(k.slabOf(blade, 14, 10, P, 2, 0.8), { tone: "hi", lit: true }));
  
  // Deflector chute for discarded ID tags (Máng xả tem ID)
  const chute = { x: STRIP_X - 18, y: -32, w: 14, d: 14, r: 1.5 };
  out.push(S(k.slabOf(chute, 0, 10, P, 3, 0.5), { tone: "lo" }));
  out.push(L(k.planOutline(k.insetPlan(chute, 1.5), 10, P), { tone: "mid" }));
  
  return out.join("");
}

// 4. Station 2: Dual Sprung Probes (Delta Payload & Timing Escapement)
function stationProbes() {
  const out = [];
  // Rear pillar base
  out.push(S(k.slabOf({ x: PROBE_X - 8, y: PROBE_BASE_Y - 8, w: 16, d: 16, r: 3 }, 0, 8, P, 4, 0.6), { tone: "mid" }));
  out.push(S(k.cylinder(PROBE_X, PROBE_BASE_Y, 5, 8, PROBE_ARM_Z - 8, P, 28), { tone: "mid", crease: "none" }));
  
  // Overhanging cantilever arm
  const arm = { x: PROBE_X - 3.5, y: PROBE_BASE_Y + 4, w: 7, d: -PROBE_BASE_Y - 4, r: 2 };
  out.push(S(k.slabOf(arm, PROBE_ARM_Z - 6, 6, P, 3, 0.5), { tone: "hi" }));
  
  // Probe bushing mount collars over the carriage
  out.push(S(k.cylinder(PROBE_X, -7, 4.2, PROBE_ARM_Z - 10, 8, P, 24), { tone: "mid" })); // Delta payload probe
  out.push(S(k.cylinder(PROBE_X, 7, 3.8, PROBE_ARM_Z - 10, 8, P, 24), { tone: "mid" })); // Delta t rhythm probe
  
  // Knurled adjuster knobs on top
  out.push(S(k.cylinder(PROBE_X, -7, 3.2, PROBE_ARM_Z, 4, P, 20), { tone: "hi" }));
  out.push(L(k.knurl(PROBE_X, -7, 3.2, PROBE_ARM_Z, PROBE_ARM_Z + 4, 20, P), { tone: "lo" }));
  out.push(S(k.cylinder(PROBE_X, 7, 3.0, PROBE_ARM_Z, 4, P, 20), { tone: "hi" }));
  out.push(L(k.knurl(PROBE_X, 7, 3.0, PROBE_ARM_Z, PROBE_ARM_Z + 4, 18, P), { tone: "lo" }));
  
  return out.join("");
}

// 5. Station 3: Transformer Multi-Head Attention Optical Arch
function stationAttentionArch() {
  const out = [];
  // Two angled upright bridge posts
  for (const ay of [ARCH_Y1, ARCH_Y2]) {
    out.push(S(k.slabOf({ x: ARCH_X - 5, y: ay - 4, w: 10, d: 8, r: 2 }, 0, ARCH_Z, P, 3, 0.6), { tone: "mid" }));
    out.push(D([at([ARCH_X, ay, ARCH_Z])], { size: 0.5 }));
  }
  
  // Curved Arch Header
  const header = { x: ARCH_X - 6, y: ARCH_Y1, w: 12, d: ARCH_Y2 - ARCH_Y1, r: 3 };
  out.push(S(k.slabOf(header, ARCH_Z - 8, 8, P, 4, 0.8), { tone: "hi" }));
  
  // 4 Optical Attention Prisms underneath the header
  const prismPositions = [-18, -6, 6, 18];
  for (const py of prismPositions) {
    out.push(S(k.slabOf({ x: ARCH_X - 3, y: py - 3, w: 6, d: 6, r: 1.2 }, ARCH_Z - 14, 6, P, 2, 0.4), { tone: "hi", lit: true }));
  }
  
  return out.join("");
}

// 6. Station 4: Sealed Threshold Dial Gauge (FAR <= 100/100k)
function stationDial() {
  const out = [];
  const [x, y] = DIAL;
  
  // Magnetic pedestal mount
  const magBase = { x: x - 18, y: y - 18, w: 36, d: 36, r: 4 };
  out.push(S(k.slabOf(magBase, 0, 10, P, 6, 0.8), { tone: "mid" }));
  out.push(L(k.planOutline(k.insetPlan(magBase, 2.5), 10, P), { tone: "lo" }));
  
  // Pedestal post up to dial
  out.push(S(k.cylinder(x, y, 5.2, 10, DIAL_Z - 10, P, 28), { tone: "mid", crease: "none" }));
  
  // Horizontal mounting bracket
  out.push(S(k.slabOf({ x: x - 8, y: y - 6, w: 16, d: 12, r: 2 }, DIAL_Z - 4, 8, P, 3, 0.5), { tone: "hi" }));
  
  // Main Circular Dial Casing
  out.push(S(k.cylinder(x, y, DIAL_R, DIAL_Z, DIAL_H, P, 64, 0.8), { tone: "hi", crease: "lo" }));
  out.push(L(k.knurl(x, y, DIAL_R, DIAL_TOP - 3.2, DIAL_TOP, 72, P, 0.3), { tone: "lo" }));
  out.push(L(k.ring(x, y, DIAL_R - 2.5, DIAL_TOP, P, 64), { tone: "lo" }));
  
  // Dial face graduations (Ticks: 0.0 to 1.0)
  const ticks = k.radialTicks(x, y, DIAL_R - 3.2, 40, 4, DIAL_TOP, [1.4, 2.8], P, -Math.PI * 0.75, Math.PI * 1.5);
  out.push(L(ticks.minor, { tone: "lo" }), L(ticks.major, { tone: "mid" }));
  
  // Red FAR Threshold fixed limit marker at 0.50 (Tau = 0.5)
  // Angle for tau=0.5: -0.75*PI + 0.5 * 1.5*PI = 0 rad
  const tauAngle = 0;
  out.push(L(k.lineOnTop([x, y], [x + Math.sin(tauAngle) * (DIAL_R - 3.2), y - Math.cos(tauAngle) * (DIAL_R - 3.2)], DIAL_TOP + 0.1, P), { tone: "hi" }));
  
  // Dial center jewel / hub
  out.push(L(k.ring(x, y, 2.2, DIAL_TOP, P, 20), { tone: "mid" }));
  out.push(D([at([x, y, DIAL_TOP + 0.2])], { size: 0.6, tone: "hi" }));
  
  // Warning Beacon atop the dial casing
  out.push(S(k.cylinder(x, y, 3.6, DIAL_TOP, 5, P, 24), { tone: "lo" }));
  out.push(S(k.cylinder(x, y, 2.8, DIAL_TOP + 5, 4, P, 20), { tone: "hi", lit: true }));
  
  return out.join("");
}

// 7. Dynamic Carriage (Window W=64 frames)
function carriageBody() {
  const out = [];
  const cPlan = { x: -CARRIAGE_W / 2, y: -CARRIAGE_D / 2, w: CARRIAGE_W, d: CARRIAGE_D, r: 4 };
  
  // Carriage base slab
  out.push(S(k.slabOf(cPlan, CARRIAGE_Z, CARRIAGE_H, P, 6, 0.6), { tone: "mid" }));
  
  // Recessed 64-Frame Magazine Bay (W=64)
  const bay = k.insetPlan(cPlan, 4);
  out.push(L(k.planOutline(bay, CARRIAGE_TOP, P), { tone: "lo" }));
  
  // 64-frame grid: 16 columns x 4 rows
  const gridDots = k.dotGrid(-CARRIAGE_W / 2 + 8, -CARRIAGE_D / 2 + 8, 14, 4, 3.8, CARRIAGE_TOP, P);
  out.push(D(gridDots, { size: 0.45, tone: "hi" }));
  
  // Front handle with knurled grip
  const handleX = 0;
  const handleY = CARRIAGE_D / 2 + 4;
  out.push(S(k.slabOf({ x: handleX - 4, y: CARRIAGE_D / 2 - 1, w: 8, d: 5, r: 1.5 }, CARRIAGE_Z + 1, 3.5, P, 2), { tone: "mid" }));
  out.push(S(k.cylinder(handleX, handleY + 2, 3.4, CARRIAGE_Z, 6, P, 20), { tone: "hi" }));
  out.push(L(k.knurl(handleX, handleY + 2, 3.4, CARRIAGE_Z, CARRIAGE_Z + 6, 20, P), { tone: "lo" }));
  
  return out.join("");
}

// Dynamic elements: Probe Plungers & Dial Needle
function dynamicNeedle(angleRad) {
  const [x, y] = DIAL;
  const p1 = [x - Math.sin(angleRad) * 4, y + Math.cos(angleRad) * 4];
  const p2 = [x + Math.sin(angleRad) * (DIAL_R - 4.5), y - Math.cos(angleRad) * (DIAL_R - 4.5)];
  return k.lineOnTop(p1, p2, DIAL_TOP + 0.2, P);
}

// Generate the complete static and moving SVG groups
const svg = k.figureSvg({
  width: WIDTH,
  height: HEIGHT,
  label: "CAN-IDS Structural Inspection Rig: precision machine with sliding carriage representing W=64 window, ID stripper guillotine, dual sprung delta probes, Transformer attention arch, and calibrated threshold dial indicator.",
  body: [
    plate(),
    rails(),
    stationIDStripper(),
    stationProbes(),
    stationAttentionArch(),
    stationDial(),
    
    // Moving Carriage Group
    `<g class="can-carriage" data-move-carriage>${carriageBody()}</g>`,
    
    // Dynamic Sprung Probes (Delta Payload & Rhythm)
    `<g class="can-probes">
      <!-- Delta payload probe plunger -->
      <path class="can-probe-payload iso-solid tone-hi iso-lit" d="" />
      <!-- Rhythm timing arm -->
      <path class="can-probe-timing iso-line tone-hi" d="" />
    </g>`,
    
    // Attention Projection Beams (from arch prisms to carriage)
    `<g class="can-attention-beams">
      <path class="beam-1 iso-line tone-faint" d="" />
      <path class="beam-2 iso-line tone-faint" d="" />
      <path class="beam-3 iso-line tone-faint" d="" />
      <path class="beam-4 iso-line tone-faint" d="" />
    </g>`,
    
    // Dial needle
    `<g class="can-dial">
      <path class="can-needle iso-line tone-hi iso-lit" style="stroke-width:1.4px" d="${dynamicNeedle(-Math.PI * 0.75 + 0.1)}" />
    </g>`,
  ].join(""),
});

// Styles
const CSS = `
.iso-stage { cursor: pointer; touch-action: manipulation; position: relative; user-select: none; }
.can-controls { display: flex; gap: 8px; justify-content: center; margin-top: 12px; margin-bottom: 8px; }
.can-btn { 
  font-family: inherit; font-size: 11px; padding: 6px 14px; border-radius: 4px; border: 1px solid var(--iso-line-mid, #555); 
  background: var(--iso-paper, #1a1a1a); color: var(--iso-ink-hi, #eee); cursor: pointer; transition: all 0.15s ease;
}
.can-btn:hover { background: var(--iso-line-lo, #333); }
.can-btn.active { background: var(--iso-ink-hi, #eee); color: var(--iso-paper, #111); font-weight: 600; border-color: var(--iso-ink-hi, #eee); }
[data-theme="light"] .can-btn.active { background: #111; color: #fff; }
.can-alarm-glow { transition: opacity 0.2s ease; opacity: 0; }
[data-alarm="true"] .can-alarm-glow { opacity: 1; }
`;

// Live interaction script
const live = `
const P = ${JSON.stringify(P)};
const DIAL = ${JSON.stringify(DIAL)};
const DIAL_R = ${DIAL_R}, DIAL_TOP = ${DIAL_TOP};
const PROBE_X = ${PROBE_X}, PROBE_ARM_Z = ${PROBE_ARM_Z};
const ARCH_X = ${ARCH_X}, ARCH_Z = ${ARCH_Z};
const CARRIAGE_W = ${CARRIAGE_W};

const stage = document.querySelector(".iso-stage");
const carriageEl = stage.querySelector("[data-move-carriage]");
const needleEl = stage.querySelector(".can-needle");
const probePayloadEl = stage.querySelector(".can-probe-payload");
const probeTimingEl = stage.querySelector(".can-probe-timing");
const readout = document.querySelector("[data-readout]");
const btns = document.querySelectorAll(".can-btn");

// Modes: 0: BENIGN, 1: DoS ATTACK, 2: FUZZING
let currentMode = 0;
let clock = 0;
let lastTime = 0;
let visible = true;
let animFrame = 0;

// Dynamic variables
let carriageX = 0;
let payloadVibe = 0;
let timingVibe = 0;
let threatProb = 0.04;
let targetProb = 0.04;

function setMode(mode) {
  currentMode = mode;
  btns.forEach((btn, idx) => {
    if (idx === mode) btn.classList.add("active");
    else btn.classList.remove("active");
  });
  if (mode === 0) targetProb = 0.04;
  else if (mode === 1) targetProb = 0.98;
  else if (mode === 2) targetProb = 0.91;
}

window.selectMode = setMode;

function updatePhysics(dt) {
  clock += dt;
  
  // Smooth threat probability follow
  threatProb += (targetProb - threatProb) * Math.min(1, dt * 5);
  
  if (currentMode === 0) {
    // Normal traffic: calm rhythmic sliding of W=64 carriage
    carriageX = Math.sin(clock * 1.5) * 8;
    payloadVibe = Math.sin(clock * 4) * 0.8;
    timingVibe = Math.sin(clock * 8) * 1.2;
  } else if (currentMode === 1) {
    // DoS Flooding: ultra-fast jitter, zero delta-t delay
    carriageX = (Math.random() - 0.5) * 3;
    payloadVibe = (Math.random() - 0.5) * 0.4;
    timingVibe = Math.sin(clock * 35) * 5.0; // intense buzz
  } else if (currentMode === 2) {
    // Fuzzing: violent payload fluctuations
    carriageX = Math.sin(clock * 1.8) * 6;
    payloadVibe = (Math.sin(clock * 18) + Math.cos(clock * 27)) * 4.5; // wild jumps
    timingVibe = Math.sin(clock * 6) * 1.5;
  }
}

function render() {
  // Move carriage
  const tStr = translateAlong(P, [carriageX, 0, 0]);
  carriageEl.setAttribute("transform", tStr);
  
  // Update dial needle
  // Dial range: from -0.75*PI to +0.75*PI for p in [0, 1]
  const needleAngle = -Math.PI * 0.75 + threatProb * (Math.PI * 1.5);
  const nx = DIAL[0], ny = DIAL[1];
  const p1 = [nx - Math.sin(needleAngle) * 4, ny + Math.cos(needleAngle) * 4];
  const p2 = [nx + Math.sin(needleAngle) * (DIAL_R - 4.5), ny - Math.cos(needleAngle) * (DIAL_R - 4.5)];
  needleEl.setAttribute("d", lineOnTop(p1, p2, DIAL_TOP + 0.2, P));
  
  // Update Sprung Probes
  const pPlungerTipZ = 12 + payloadVibe;
  const pPlungerBase = [PROBE_X, -7];
  const plungerCyl = cylinder(pPlungerBase[0], pPlungerBase[1], 1.4, pPlungerTipZ, PROBE_ARM_Z - 10 - pPlungerTipZ, P, 16);
  probePayloadEl.setAttribute("d", plungerCyl.fill + (plungerCyl.outline || ""));
  
  // Update Timing Arm line
  const tArmTipZ = 13 + timingVibe * 0.5;
  const timingLine = lineOnTop([PROBE_X, 7], [PROBE_X + timingVibe * 0.8, 7], tArmTipZ, P);
  probeTimingEl.setAttribute("d", timingLine);
  
  // Update Attention Beams
  const b1 = lineOnTop([ARCH_X - 3, -18], [-CARRIAGE_W/2 + 10 + carriageX, -10], ARCH_Z - 14, P);
  const b2 = lineOnTop([ARCH_X - 3, -6], [-CARRIAGE_W/2 + 25 + carriageX, 0], ARCH_Z - 14, P);
  const b3 = lineOnTop([ARCH_X - 3, 6], [-CARRIAGE_W/2 + 40 + carriageX, -6], ARCH_Z - 14, P);
  const b4 = lineOnTop([ARCH_X - 3, 18], [-CARRIAGE_W/2 + 55 + carriageX, 8], ARCH_Z - 14, P);
  stage.querySelector(".beam-1").setAttribute("d", b1);
  stage.querySelector(".beam-2").setAttribute("d", b2);
  stage.querySelector(".beam-3").setAttribute("d", b3);
  stage.querySelector(".beam-4").setAttribute("d", b4);
  
  // Update Live Readout
  let modeName = "BENIGN (PASS)";
  let d_t = "10.4 ms";
  let d_pay = "0.02";
  if (currentMode === 1) {
    modeName = "DoS ATTACK [TRIGGER]";
    d_t = "0.12 ms (FLOOD)";
    d_pay = "0.00";
  } else if (currentMode === 2) {
    modeName = "FUZZING [TRIGGER]";
    d_t = "9.8 ms";
    d_pay = "0.84 (JUMP)";
  }
  const isAlarm = threatProb >= 0.5;
  stage.setAttribute("data-alarm", isAlarm ? "true" : "false");
  
  const statusStr = isAlarm ? "ALERT · p=" + threatProb.toFixed(2) + " >= τ (0.50)" : "NORMAL · p=" + threatProb.toFixed(2) + " < τ";
  readout.textContent = "W=64 · " + modeName + " · Δt: " + d_t + " · Δpayload: " + d_pay + " · " + statusStr;
}

function loop(now) {
  const dt = lastTime ? Math.min((now - lastTime) / 1000, 1 / 30) : 1 / 60;
  lastTime = now;
  updatePhysics(dt);
  render();
  if (visible) animFrame = requestAnimationFrame(loop);
}

// Click stage to cycle mode
stage.addEventListener("click", () => {
  setMode((currentMode + 1) % 3);
});

// Keyboard navigation
window.addEventListener("keydown", (e) => {
  if (e.key === "1") setMode(0);
  if (e.key === "2") setMode(1);
  if (e.key === "3") setMode(2);
  if (e.key === " ") setMode((currentMode + 1) % 3);
});

new IntersectionObserver((entries) => {
  visible = entries[entries.length - 1].isIntersecting;
  if (visible && !animFrame) animFrame = requestAnimationFrame(loop);
}).observe(stage);

animFrame = requestAnimationFrame(loop);
`;

// Assemble Card Body
const cardBody = k.plateHtml({
  fig: "Fig 1",
  title: "CAN-IDS Structural Test Rig",
  hint: "Click machine or buttons below to switch traffic mode (1: Benign, 2: DoS, 3: Fuzzing)",
  readout: "W=64 · BENIGN · Δt: 10.4 ms · Δpayload: 0.02 · NORMAL · p=0.04 < τ",
  keys: [
    { mark: "lit", label: "Moving needle & Attention beams: real-time threat probability & token attention" },
    { mark: "raised", label: "Carriage (W=64) & Dual sprung probes: causal windowing, Δt rhythm & Δpayload jump" },
    { mark: "faint", label: "Station 1 ID Guillotine: strips raw CAN-ID bits to enforce vehicle-invariance" },
  ],
  caption: "Physical representation of the CAN intrusion detection mechanism under vehicle and attack shift. Window carriage (W=64 frames) passes through Station 1 where 11-bit CAN-IDs are sheared off to prevent vehicle overfitting. Station 2 measures same-ID payload jump (Δpayload) and inter-arrival time (Δt). Station 3 (Transformer arch) projects cross-attention between frames. Station 4 dial gauge evaluates intrusion probability p against the frozen threshold τ calibrated strictly on source data under FAR ≤ 100/100,000.",
  body: `
    <div class="can-controls">
      <button class="can-btn active" onclick="selectMode(0)">1 · Benign Traffic (Impala→Silverado)</button>
      <button class="can-btn" onclick="selectMode(1)">2 · DoS Flooding Attack (Δt → 0)</button>
      <button class="can-btn" onclick="selectMode(2)">3 · Payload Fuzzing (High Δpayload)</button>
    </div>
    <div class="iso-stage" tabindex="0" role="region" aria-label="CAN-IDS Structural Inspection Rig">${svg}</div>
  `,
});

const outName = theme === "light" ? "can-ids-rig-light.html" : "can-ids-rig.html";
const fullHtml = k.pageHtml({
  title: "CAN-IDS Structural Test Rig",
  theme,
  body: `<style>${CSS}</style>${cardBody}`,
  script: kitScript() + live,
});

writeFileSync(join(HERE, outName), fullHtml);
console.log("Successfully built:", outName);
