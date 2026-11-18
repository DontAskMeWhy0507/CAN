import { readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const bundleCode = readFileSync('dist/bundle.js', 'utf8');

const html = `<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Mô Hình Hóa 3D Pipeline CAN-IDS (32-D Structural Transformer)</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      background: #0a0f1d;
      color: #f8fafc;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      overflow: hidden;
      width: 100vw;
      height: 100vh;
    }
    #canvas-container {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      z-index: 1;
    }
    .hud-overlay {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      pointer-events: none;
      z-index: 10;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 16px 20px;
    }
    .header-bar {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 16px;
      pointer-events: auto;
    }
    .title-box {
      background: rgba(15, 23, 42, 0.85);
      backdrop-filter: blur(12px);
      border: 1px solid rgba(56, 189, 248, 0.3);
      border-radius: 12px;
      padding: 12px 18px;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    }
    .title-box h1 {
      font-size: 16px;
      font-weight: 700;
      color: #38bdf8;
      letter-spacing: 0.5px;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .title-box p {
      font-size: 12px;
      color: #94a3b8;
      margin-top: 4px;
    }
    .controls-nav {
      display: flex;
      gap: 6px;
      background: rgba(15, 23, 42, 0.85);
      backdrop-filter: blur(12px);
      border: 1px solid rgba(148, 163, 184, 0.2);
      border-radius: 10px;
      padding: 6px;
      pointer-events: auto;
    }
    .stage-btn {
      background: transparent;
      border: 1px solid transparent;
      color: #94a3b8;
      font-size: 11px;
      font-weight: 600;
      padding: 6px 12px;
      border-radius: 6px;
      cursor: pointer;
      transition: all 0.2s ease;
    }
    .stage-btn:hover {
      background: rgba(56, 189, 248, 0.15);
      color: #38bdf8;
    }
    .stage-btn.active {
      background: #0284c7;
      color: #ffffff;
      border-color: #38bdf8;
      box-shadow: 0 0 12px rgba(56, 189, 248, 0.4);
    }
    .mode-bar {
      display: flex;
      gap: 8px;
      background: rgba(15, 23, 42, 0.85);
      backdrop-filter: blur(12px);
      border: 1px solid rgba(148, 163, 184, 0.2);
      border-radius: 10px;
      padding: 6px;
      pointer-events: auto;
    }
    .mode-btn {
      background: rgba(30, 41, 59, 0.8);
      border: 1px solid rgba(148, 163, 184, 0.2);
      color: #cbd5e1;
      font-size: 11px;
      font-weight: 600;
      padding: 6px 12px;
      border-radius: 6px;
      cursor: pointer;
      transition: all 0.2s ease;
    }
    .mode-btn:hover { background: rgba(51, 65, 85, 0.9); }
    .mode-btn.active#btn-normal {
      background: #059669;
      color: #fff;
      border-color: #10b981;
      box-shadow: 0 0 12px rgba(16, 185, 129, 0.4);
    }
    .mode-btn.active#btn-dos {
      background: #dc2626;
      color: #fff;
      border-color: #ef4444;
      box-shadow: 0 0 12px rgba(239, 68, 68, 0.4);
    }
    .mode-btn.active#btn-fuzz {
      background: #d97706;
      color: #fff;
      border-color: #f59e0b;
      box-shadow: 0 0 12px rgba(245, 158, 11, 0.4);
    }
    .bottom-bar {
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
      gap: 20px;
    }
    .hud-card {
      background: rgba(15, 23, 42, 0.9);
      backdrop-filter: blur(14px);
      border: 1px solid rgba(56, 189, 248, 0.25);
      border-radius: 12px;
      padding: 14px 18px;
      min-width: 320px;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
      pointer-events: auto;
    }
    .hud-title {
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.8px;
      color: #64748b;
      margin-bottom: 8px;
    }
    .hud-status-line {
      font-size: 14px;
      font-weight: 700;
      margin-bottom: 6px;
    }
    .hud-metric-row {
      display: flex;
      justify-content: space-between;
      font-size: 12px;
      margin-top: 4px;
      color: #cbd5e1;
    }
    .hud-metric-val {
      font-weight: 600;
      color: #f8fafc;
    }
    .drawer-panel {
      background: rgba(15, 23, 42, 0.92);
      backdrop-filter: blur(16px);
      border: 1px solid rgba(148, 163, 184, 0.25);
      border-radius: 14px;
      padding: 16px 20px;
      max-width: 440px;
      box-shadow: 0 12px 36px rgba(0, 0, 0, 0.6);
      pointer-events: auto;
    }
    .drawer-title {
      font-size: 14px;
      font-weight: 700;
      color: #38bdf8;
      border-bottom: 1px solid rgba(148, 163, 184, 0.2);
      padding-bottom: 8px;
      margin-bottom: 10px;
    }
    .drawer-content {
      font-size: 12px;
      line-height: 1.6;
      color: #cbd5e1;
    }
    .drawer-content code {
      background: rgba(30, 41, 59, 0.8);
      color: #38bdf8;
      padding: 2px 6px;
      border-radius: 4px;
      font-family: monospace;
    }
    .drawer-content ul {
      margin-left: 18px;
      margin-top: 6px;
    }
    .stat-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 8px;
      margin: 10px 0;
    }
    .stat-box {
      background: rgba(30, 41, 59, 0.6);
      border: 1px solid rgba(148, 163, 184, 0.15);
      border-radius: 8px;
      padding: 8px 10px;
      text-align: center;
    }
    .stat-val { font-size: 15px; font-weight: 700; color: #38bdf8; }
    .stat-label { font-size: 10px; color: #94a3b8; margin-top: 2px; }
    .badge {
      display: inline-block;
      padding: 2px 6px;
      border-radius: 4px;
      font-size: 10px;
      font-weight: 600;
      margin-right: 4px;
    }
    .badge-cyan { background: rgba(56, 189, 248, 0.2); color: #38bdf8; }
    .badge-green { background: rgba(16, 185, 129, 0.2); color: #10b981; }
    .badge-amber { background: rgba(245, 158, 11, 0.2); color: #f59e0b; }
    .badge-purple { background: rgba(168, 85, 247, 0.2); color: #a855f7; }
    .mouse-hint {
      position: absolute;
      bottom: 20px;
      left: 50%;
      transform: translateX(-50%);
      font-size: 11px;
      color: #64748b;
      background: rgba(15, 23, 42, 0.7);
      padding: 6px 14px;
      border-radius: 20px;
      pointer-events: none;
      backdrop-filter: blur(8px);
    }
  </style>
</head>
<body>
  <div id="canvas-container"></div>
  
  <div class="hud-overlay">
    <!-- Header -->
    <div class="header-bar">
      <div class="title-box">
        <h1>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
          MÔ HÌNH HÓA 3D PIPELINE PHÁT HIỆN XÂM NHẬP CAN BUS
        </h1>
        <p>Học biểu diễn cấu trúc 32 chiều độc lập đặc thù xe • Transformer W=64 • Chuyển giao Zero-Shot</p>
      </div>

      <!-- Controls Navigation -->
      <div class="controls-nav">
        <button class="stage-btn active" onclick="focusStage(0)">Toàn Cảnh</button>
        <button class="stage-btn" onclick="focusStage(1)">1 · CAN Thô</button>
        <button class="stage-btn" onclick="focusStage(2)">2 · Cửa Sổ W=64</button>
        <button class="stage-btn" onclick="focusStage(3)">3 · Ma Trận 32-D</button>
        <button class="stage-btn" onclick="focusStage(4)">4 · Transformer</button>
        <button class="stage-btn" onclick="focusStage(5)">5 · Zero-Shot (A-D)</button>
      </div>

      <!-- Simulation Mode Selector -->
      <div class="mode-bar">
        <button id="btn-normal" class="mode-btn active" onclick="setSimulationMode('normal')">Xe Lành (Impala→Silverado)</button>
        <button id="btn-dos" class="mode-btn" onclick="setSimulationMode('dos')">Tấn Công DoS (Δt → 0)</button>
        <button id="btn-fuzz" class="mode-btn" onclick="setSimulationMode('fuzz')">Tấn Công Fuzzing (High Δpayload)</button>
      </div>
    </div>

    <!-- Mouse Interaction Hint -->
    <div class="mouse-hint">
      🖱️ Giữ chuột trái: Xoay 3D 360° &bull; Con lăn: Phóng to / Thu nhỏ &bull; Chuột phải: Dịch chuyển (Pan)
    </div>

    <!-- Bottom Bar (HUD & Drawer) -->
    <div class="bottom-bar">
      <!-- Live Status HUD -->
      <div class="hud-card">
        <div class="hud-title">Chỉ số giám sát thời gian thực (Live Stream)</div>
        <div id="hud-status" class="hud-status-line">
          <span style="color:#22c55e">● BENIGN (Impala→Silverado PASS)</span>
        </div>
        <div class="hud-metric-row">
          <span>Xác suất tấn công p:</span>
          <span id="hud-score" class="hud-metric-val">p = 0.04 < τ (0.50)</span>
        </div>
        <div class="hud-metric-row">
          <span>Nhịp thời gian liên tiếp (Δt):</span>
          <span id="hud-dt" class="hud-metric-val">10.4 ms (Chu kỳ ổn định)</span>
        </div>
        <div class="hud-metric-row">
          <span>Biến thiên payload cùng ID:</span>
          <span id="hud-dpay" class="hud-metric-val">0.02 (Biến thiên nhỏ)</span>
        </div>
        <div class="hud-metric-row">
          <span>Ngân sách báo động giả (FAR):</span>
          <span class="hud-metric-val" style="color:#38bdf8">≤ 100 / 100.000 cửa sổ</span>
        </div>
      </div>

      <!-- Explanatory Details Drawer -->
      <div class="drawer-panel">
        <div id="drawer-title" class="drawer-title">TOÀN CẢNH PIPELINE ĐỀ XUẤT</div>
        <div id="drawer-content" class="drawer-content">
          <p>Pipeline nghiên cứu phương pháp phát hiện xâm nhập mạng CAN khi có <strong>dịch chuyển dòng xe (Vehicle Shift)</strong> và <strong>kiểu tấn công (Attack Shift)</strong>.</p>
          <div class="stat-grid">
            <div class="stat-box"><div class="stat-val">32-D</div><div class="stat-label">Biểu diễn cấu trúc</div></div>
            <div class="stat-box"><div class="stat-val">W=64</div><div class="stat-label">Cửa sổ liên tiếp</div></div>
            <div class="stat-box"><div class="stat-val">Zero-Shot</div><div class="stat-label">Chuyển giao xe lạ</div></div>
            <div class="stat-box"><div class="stat-val">≤100/100k</div><div class="stat-label">Ngân sách FAR nguồn</div></div>
          </div>
          <p>Bấm vào các nút công đoạn phía trên để camera 3D di chuyển và phóng to từng tầng kiến trúc.</p>
        </div>
      </div>
    </div>
  </div>

  <script>
${bundleCode}
  </script>
</body>
</html>
`;

writeFileSync('pipeline-3d.html', html);
console.log('Successfully wrote standalone 3D pipeline HTML: pipeline-3d.html');

// Also write into the artifact directory for generative_ui embed
const artifactDir = 'C:/Users/tuant/.gemini/antigravity/brain/e1b75072-bddf-4f90-b3f5-1f0d8d53d83d';
writeFileSync(join(artifactDir, 'can_ids_pipeline_3d.html'), html);
console.log('Successfully wrote artifact: can_ids_pipeline_3d.html');
