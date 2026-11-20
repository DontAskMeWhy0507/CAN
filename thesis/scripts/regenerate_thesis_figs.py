"""Regenerate publication-grade thesis figures (VI & EN) from frozen CSV results.

Reads frozen result tables in ``f:/00_Research/code/results/`` read-only and
writes 15 localized 300-DPI PNG figures into ``thesis/vi/figs/`` and
``thesis/en/figs/`` (leaving ``en/figs/calibration_recovery_comparison.png``
and all files under ``code/`` untouched).

Usage:
    f:/00_Research/.venv/Scripts/python.exe f:/00_Research/thesis/scripts/regenerate_thesis_figs.py
"""
from __future__ import annotations

from pathlib import Path
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from matplotlib.ticker import FuncFormatter
import numpy as np
import pandas as pd


ROOT = Path("f:/00_Research")
RESULTS = ROOT / "code/results"
VI_FIGS = ROOT / "thesis/vi/figs"
EN_FIGS = ROOT / "thesis/en/figs"


# ---------------------------------------------------------------------------
# 1. Pipeline Architecture Diagram (pipeline_architecture_30d.png, VI & EN)
# ---------------------------------------------------------------------------
def _draw_box(
    ax,
    x: float,
    y: float,
    w: float,
    h: float,
    *,
    fc: str,
    ec: str,
    lw: float = 1.2,
    r: float = 0.08,
    zorder: int = 2,
    ls: str = "-",
) -> FancyBboxPatch:
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle=f"round,pad=0,rounding_size={r}",
        facecolor=fc,
        edgecolor=ec,
        linewidth=lw,
        linestyle=ls,
        zorder=zorder,
    )
    ax.add_patch(patch)
    return patch


def _draw_arrow(
    ax,
    p0: tuple[float, float],
    p1: tuple[float, float],
    *,
    color: str = "#374151",
    lw: float = 1.4,
    style: str = "-|>",
    ls: str = "-",
    rad: float = 0.0,
    ms: float = 11.0,
    zorder: int = 5,
) -> None:
    arr = FancyArrowPatch(
        p0,
        p1,
        arrowstyle=style,
        mutation_scale=ms,
        linewidth=lw,
        linestyle=ls,
        color=color,
        connectionstyle=f"arc3,rad={rad}",
        zorder=zorder,
    )
    ax.add_patch(arr)


def generate_pipeline_architecture(lang: str, out_path: Path) -> None:
    """Draw the 4-column Structural Transformer 30D architecture diagram."""
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "mathtext.fontset": "dejavusans",
            "font.sans-serif": ["DejaVu Sans"],
        }
    )

    is_vi = lang == "vi"
    W, H = 10.95, 8.60
    FS_HDR = 14.3
    FS_C3HDR = 14.0
    FS_SUB = 14.0
    FS_BODY = 13.9

    fig = plt.figure(figsize=(W, H), dpi=300)
    ax = fig.add_axes([0.002, 0.002, 0.996, 0.996])
    ax.set_xlim(0.0, W)
    ax.set_ylim(0.0, H)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    # 4-column x-layout totaling 10.95 in (scaled for >=8.0 pt print at 0.98\textwidth = 6.366 in)
    pad_in = 0.055
    c1_x, c1_w = 0.02, 2.00
    gap12_x, gap12_w = 2.02, 1.52
    c2_x, c2_w = 3.54, 2.50
    gap23_x, gap23_w = 6.04, 0.14
    c3_x, c3_w = 6.18, 2.20
    gap34_x, gap34_w = 8.38, 0.15
    c4_x, c4_w = 8.53, 2.40

    col_y, col_h = 0.06, 8.48
    hdr_h = 1.04
    hdr_y = col_y + col_h - hdr_h
    top_inner = hdr_y - 0.14

    cols = [
        (
            c1_x,
            c1_w,
            "#A21CAF",
            "#FDF4FF",
            "#F5D0FE",
            "1. ĐẦU VÀO &\nTRẠNG THÁI" if is_vi else "1. INPUT &\nCAUSAL STATE",
        ),
        (
            c2_x,
            c2_w,
            "#0F766E",
            "#F0FDFA",
            "#CCFBF1",
            "2. TRÍCH XUẤT\nĐẶC TRƯNG (30D)" if is_vi else "2. STRUCTURAL\nEXTRACTOR (30D)",
        ),
        (
            c3_x,
            c3_w,
            "#C2410C",
            "#FFF7ED",
            "#FFEDD5",
            "3. MÃ HÓA\nTRANSFORMER\n(75.298 THAM SỐ)" if is_vi else "3. TRANSFORMER\nENCODER\n(75,298 PARAMS)",
        ),
        (
            c4_x,
            c4_w,
            "#0369A1",
            "#F0F9FF",
            "#E0F2FE",
            "4. GIAI ĐOẠN II:\nHIỆU CHUẨN & LỌC" if is_vi else "4. STAGE II:\nCALIBRATION & FILTER",
        ),
    ]

    for col_idx, (cx, cw, ec, bg, hbg, title) in enumerate(cols):
        _draw_box(ax, cx, col_y, cw, col_h, fc=bg, ec=ec, lw=1.5, r=0.11, zorder=1)
        _draw_box(ax, cx + 0.04, hdr_y, cw - 0.08, hdr_h - 0.04, fc=hbg, ec=ec, lw=0.8, r=0.08, zorder=2)
        ax.text(
            cx + cw / 2,
            hdr_y + (hdr_h - 0.04) / 2,
            title,
            ha="center",
            va="center",
            fontsize=FS_C3HDR if col_idx == 2 else FS_HDR,
            fontweight="bold",
            color="#111827",
            linespacing=1.22 if col_idx == 2 else 1.26,
            zorder=3,
        )

    # ---------------- COL 1 ----------------
    b1a_x, b1a_w = c1_x + pad_in, c1_w - 2 * pad_in
    b1a_h = 2.36
    b1a_y = top_inner - b1a_h
    _draw_box(ax, b1a_x, b1a_y, b1a_w, b1a_h, fc="white", ec="#9333EA", lw=1.05, r=0.08, zorder=3)
    ax.text(
        b1a_x + b1a_w / 2,
        b1a_y + b1a_h - 0.38,
        "Luồng CAN\nBus Thô" if is_vi else "Raw CAN Bus\nStream",
        ha="center",
        va="center",
        fontsize=FS_SUB,
        fontweight="bold",
        color="#111827",
        linespacing=1.12,
        zorder=4,
    )
    ax.text(
        b1a_x + b1a_w / 2,
        b1a_y + 1.12,
        "Cửa sổ rời rạc\n$W = 64$ khung"
        if is_vi
        else "Non-overlapping\n$W = 64$ frames",
        ha="center",
        va="center",
        fontsize=FS_BODY,
        color="#374151",
        linespacing=1.18,
        zorder=4,
    )
    ax.text(
        b1a_x + b1a_w / 2,
        b1a_y + 0.34,
        r"$F_i=(t_i,c_i,d_i,\mathbf{b}_i,y_i)$",
        ha="center",
        va="center",
        fontsize=FS_BODY,
        color="#1D4ED8",
        zorder=4,
    )

    b1b_x, b1b_w = b1a_x, b1a_w
    b1b_y = 0.18
    b1b_h = b1a_y - 0.18 - b1b_y
    _draw_box(ax, b1b_x, b1b_y, b1b_w, b1b_h, fc="white", ec="#9333EA", lw=1.05, r=0.08, zorder=3)
    ax.text(
        b1b_x + b1b_w / 2,
        b1b_y + b1b_h - 0.36,
        r"Bảng Lịch Sử $H_k$" if is_vi else r"History Table $H_k$",
        ha="center",
        va="center",
        fontsize=FS_SUB,
        fontweight="bold",
        color="#111827",
        zorder=4,
    )
    ax.text(
        b1b_x + b1b_w / 2,
        b1b_y + b1b_h * 0.72,
        "Khóa: 11-bit ID\n(130 KiB RAM)" if is_vi else "Key: 11-bit ID\n(130 KiB RAM)",
        ha="center",
        va="center",
        fontsize=FS_BODY,
        color="#374151",
        linespacing=1.18,
        zorder=4,
    )
    ax.text(
        b1b_x + b1b_w / 2,
        b1b_y + b1b_h * 0.44,
        r"Lưu: $d_q, \mathbf{b}_q, \mathbf{m}_q$" + "\n" + "(DLC, payload,\nmặt nạ)"
        if is_vi
        else r"Stores: $d_q, \mathbf{b}_q, \mathbf{m}_q$" + "\n" + "(DLC, payload,\nmask)",
        ha="center",
        va="center",
        fontsize=FS_BODY,
        color="#1F2937",
        linespacing=1.18,
        zorder=4,
    )
    ax.text(
        b1b_x + b1b_w / 2,
        b1b_y + 0.68,
        "Đặt lại: đầu mỗi\ntệp / chu kỳ\nkhóa điện"
        if is_vi
        else "Reset: per file /\nignition cycle",
        ha="center",
        va="center",
        fontsize=FS_BODY,
        fontweight="bold",
        color="#B91C1C",
        linespacing=1.15,
        zorder=4,
    )

    # ---------------- COL 2 (Sequential 0&1-8 -> 9-16 -> 17-24 -> 25 -> 26-29) ----------------
    f_specs = [
        (
            "Chỉ số 0 & 1–8 (9D):" if is_vi else "Indices 0 & 1–8 (9D):",
            r"DLC $d_i/8$ &" + "\n" + r"Payload $b_{i,j}/255$"
            if is_vi
            else r"Norm. DLC $d_i/8$ &" + "\n" + r"Payload $b_{i,j}/255$",
            1.20,
        ),
        (
            "Chỉ số 9–16 (8D):" if is_vi else "Indices 9–16 (8D):",
            r"Mặt nạ: $m_{i,j} = \mathbf{1}[j < d_i]$"
            if is_vi
            else r"Mask: $m_{i,j} = \mathbf{1}[j < d_i]$",
            0.96,
        ),
        (
            "Chỉ số 17–24 (8D):" if is_vi else "Indices 17–24 (8D):",
            r"Vi sai cùng ID:" + "\n" + r"$|b_{i,j}-b_{q,j}|\,m_{i,j}m_{q,j}/255$"
            if is_vi
            else r"Same-ID delta:" + "\n" + r"$|b_{i,j}-b_{q,j}|\,m_{i,j}m_{q,j}/255$",
            1.28,
        ),
        (
            "Chỉ số 25 (1D):" if is_vi else "Index 25 (1D):",
            r"Cờ lịch sử:" + "\n" + r"$h_i = \mathbf{1}[H_k(c_i) \neq \emptyset]$"
            if is_vi
            else r"History flag:" + "\n" + r"$h_i = \mathbf{1}[H_k(c_i) \neq \emptyset]$",
            1.20,
        ),
        (
            "Chỉ số 26–29 (4D):" if is_vi else "Indices 26–29 (4D):",
            r"$f_k(c_i)/W$, $\operatorname{rank}_0(c_i)/U_k$,"
            + "\n"
            + r"$\operatorname{rank}_0(c_i)/W$,"
            + "\n"
            + (r"Chuyển tiếp:" + "\n" + r"$T_k(c_{i-1}, c_i)/(W-1)$" if is_vi else r"Transition:" + "\n" + r"$T_k(c_{i-1}, c_i)/(W-1)$"),
            1.96,
        ),
    ]

    b2_x, b2_w = c2_x + pad_in, c2_w - 2 * pad_in
    y_cursor = top_inner
    gap_v = (top_inner - 0.18 - sum(bh for _, _, bh in f_specs)) / 4.0
    f_boxes = []
    for title, body, bh in f_specs:
        by = y_cursor - bh
        _draw_box(ax, b2_x, by, b2_w, bh, fc="white", ec="#0D9488", lw=1.0, r=0.07, zorder=3)
        ax.text(
            b2_x + b2_w / 2,
            by + bh - 0.26,
            title,
            ha="center",
            va="center",
            fontsize=FS_SUB,
            fontweight="bold",
            color="#111827",
            zorder=4,
        )
        ax.text(
            b2_x + b2_w / 2,
            by + (bh - 0.38) / 2,
            body,
            ha="center",
            va="center",
            fontsize=FS_BODY,
            color="#1D4ED8",
            linespacing=1.18,
            zorder=4,
        )
        f_boxes.append((b2_x, by, b2_w, bh))
        y_cursor = by - gap_v

    # ---------------- GAP 1-2 (Non-colliding Bridge) ----------------
    _draw_arrow(
        ax,
        (b1a_x + b1a_w, b1a_y + b1a_h * 0.62),
        (b2_x, f_boxes[0][1] + f_boxes[0][3] * 0.55),
        color="#374151",
        lw=1.6,
        ms=10.5,
    )

    pill_w, pill_h = 1.38, 1.38
    pill_x = gap12_x + (gap12_w - pill_w) / 2
    pill_y = (f_boxes[2][1] + f_boxes[3][1] + f_boxes[3][3]) / 2 - pill_h / 2 + 0.10
    _draw_box(ax, pill_x, pill_y, pill_w, pill_h, fc="#F3F4F6", ec="#6B7280", lw=1.05, r=0.09, zorder=4)
    ax.text(
        pill_x + pill_w / 2,
        pill_y + pill_h / 2,
        r"Truy xuất &" + "\n" + r"Cập nhật" + "\n" + r"$H_k$" if is_vi else r"Causal" + "\n" + r"Lookup &" + "\n" + r"Update $H_k$",
        ha="center",
        va="center",
        fontsize=FS_BODY,
        fontweight="bold",
        color="#1F2937",
        linespacing=1.18,
        zorder=5,
    )
    _draw_arrow(
        ax,
        (b1b_x + b1b_w, pill_y + pill_h / 2),
        (pill_x, pill_y + pill_h / 2),
        color="#4B5563",
        lw=1.4,
        style="<|-|>",
        ms=7.5,
    )
    _draw_arrow(
        ax,
        (pill_x + pill_w, pill_y + pill_h * 0.68),
        (b2_x, f_boxes[2][1] + f_boxes[2][3] * 0.50),
        color="#4B5563",
        lw=1.35,
        style="<|-|>",
        ms=8.5,
    )
    _draw_arrow(
        ax,
        (pill_x + pill_w, pill_y + pill_h * 0.32),
        (b2_x, f_boxes[3][1] + f_boxes[3][3] * 0.50),
        color="#4B5563",
        lw=1.35,
        style="<|-|>",
        ms=8.5,
    )

    # ---------------- COL 3 (Vertical Flow of 4 Stages) ----------------
    b3_x, b3_w = c3_x + pad_in, c3_w - 2 * pad_in
    s3_specs = [
        (
            1.26,
            "#FFFFFF",
            "#EA580C",
            "Ma trận cửa sổ" if is_vi else "Window Tensor",
            r"$X_k \in \mathbb{R}^{64 \times 30}$",
            "#1D4ED8",
        ),
        (
            1.64,
            "#FFFFFF",
            "#EA580C",
            "Chiếu tuyến tính" if is_vi else "Linear Projection",
            (r"$30 \to 64$" + "\n" + r"+ Mã hóa vị trí" + "\n" + r"($64 \times 64$)")
            if is_vi
            else (r"$30 \to 64$" + "\n" + r"+ PosEnc ($64 \times 64$)"),
            "#C2410C",
        ),
        (
            1.56,
            "#FFFFFF",
            "#EA580C",
            "2 Lớp Encoder" if is_vi else "2 Encoder Layers",
            ("4 Heads, FFN 128\nGELU, Dropout 0,1" if is_vi else "4 Heads, FFN 128\nGELU, Dropout 0.1"),
            "#374151",
        ),
        (
            1.56,
            "#FFFBEB",
            "#D97706",
            "Mean Pooling",
            (r"Biểu diễn ẩn" if is_vi else "Latent Vector") + "\n" + r"$z_k \in \mathbb{R}^{64}$",
            "#1D4ED8",
        ),
    ]

    s3_gap = (top_inner - 0.22 - sum(item[0] for item in s3_specs)) / 3.0
    s3_cursor = top_inner
    s3_boxes = []
    for sh, fc, ec, title, body, body_col in s3_specs:
        sy = s3_cursor - sh
        _draw_box(ax, b3_x, sy, b3_w, sh, fc=fc, ec=ec, lw=1.15, r=0.08, zorder=3)
        ax.text(
            b3_x + b3_w / 2,
            sy + sh - 0.30,
            title,
            ha="center",
            va="center",
            fontsize=FS_SUB,
            fontweight="bold",
            color="#111827",
            zorder=4,
        )
        ax.text(
            b3_x + b3_w / 2,
            sy + (sh - 0.42) / 2,
            body,
            ha="center",
            va="center",
            fontsize=FS_BODY,
            color=body_col,
            linespacing=1.18,
            zorder=4,
        )
        s3_boxes.append((b3_x, sy, b3_w, sh))
        s3_cursor = sy - s3_gap

    for i in range(3):
        top_box = s3_boxes[i]
        bot_box = s3_boxes[i + 1]
        _draw_arrow(
            ax,
            (top_box[0] + top_box[2] / 2, top_box[1]),
            (bot_box[0] + bot_box[2] / 2, bot_box[1] + bot_box[3]),
            color="#EA580C",
            lw=1.5,
            ms=10.0,
        )

    _draw_arrow(
        ax,
        (c2_x + c2_w, s3_boxes[0][1] + s3_boxes[0][3] / 2),
        (b3_x, s3_boxes[0][1] + s3_boxes[0][3] / 2),
        color="#0F766E",
        lw=1.7,
        ms=10.5,
    )

    # ---------------- COL 4 (Stage II: 3-box vertical flow) ----------------
    b4_x, b4_w = c4_x + pad_in, c4_w - 2 * pad_in
    b4a_h, b4b_h, b4c_h = 2.05, 2.05, 2.05
    badge_h = 0.46
    b4_gap = (top_inner - 0.20 - badge_h - (b4a_h + b4b_h + b4c_h)) / 3.0

    b4a_y = top_inner - b4a_h
    _draw_box(ax, b4_x, b4a_y, b4_w, b4a_h, fc="white", ec="#0284C7", lw=1.1, r=0.08, zorder=3)
    ax.text(
        b4_x + b4_w / 2,
        b4a_y + b4a_h - 0.32,
        "Đầu Phân Loại Nhị Phân" if is_vi else "Binary Classifier Head",
        ha="center",
        va="center",
        fontsize=FS_SUB,
        fontweight="bold",
        color="#111827",
        zorder=4,
    )
    ax.text(
        b4_x + b4_w / 2,
        b4a_y + 1.15,
        r"LayerNorm $\to$ Linear(64 $\to$ 32)" + "\n" + r"$\to$ ReLU $\to$ Linear(32 $\to$ 2)",
        ha="center",
        va="center",
        fontsize=FS_BODY,
        color="#374151",
        linespacing=1.14,
        zorder=4,
    )
    ax.text(
        b4_x + b4_w / 2,
        b4a_y + 0.38,
        r"Điểm rủi ro: $s_k = P(Y_k=1 \mid X_k)$" if is_vi else r"Risk score: $s_k = P(Y_k=1 \mid X_k)$",
        ha="center",
        va="center",
        fontsize=FS_BODY,
        fontweight="bold",
        color="#1D4ED8",
        zorder=4,
    )

    b4b_y = b4a_y - b4_gap - b4b_h
    _draw_box(ax, b4_x, b4b_y, b4_w, b4b_h, fc="#F0FDF4", ec="#16A34A", lw=1.3, r=0.08, zorder=3)
    ax.text(
        b4_x + b4_w / 2,
        b4b_y + b4b_h - 0.32,
        "Hiệu Chuẩn Tiền Tố Lành Tính" if is_vi else "Benign Prefix Calibration",
        ha="center",
        va="center",
        fontsize=FS_SUB,
        fontweight="bold",
        color="#15803D",
        zorder=4,
    )
    ax.text(
        b4_x + b4_w / 2,
        b4b_y + 1.15,
        (r"Khởi động đích: $K = 500$ cửa sổ" + "\n" + r"($N_{\mathrm{pool}} \in [3.539, 6.000]$)"
        if is_vi
        else r"Target warmup: $K = 500$ windows" + "\n" + r"($N_{\mathrm{pool}} \in [3,539, 6,000]$)"),
        ha="center",
        va="center",
        fontsize=FS_BODY,
        color="#374151",
        linespacing=1.14,
        zorder=4,
    )
    ax.text(
        b4_x + b4_w / 2,
        b4b_y + 0.38,
        r"$\tau_{\mathrm{target}} = \operatorname{Q}_{1-\alpha}(s_k)$" + (r" (FAR $\leq \alpha$)" if is_vi else r" (FAR $\leq \alpha$)"),
        ha="center",
        va="center",
        fontsize=FS_BODY,
        fontweight="bold",
        color="#1D4ED8",
        zorder=4,
    )

    b4c_y = b4b_y - b4_gap - b4c_h
    _draw_box(ax, b4_x, b4c_y, b4_w, b4c_h, fc="white", ec="#0284C7", lw=1.1, r=0.08, zorder=3)
    ax.text(
        b4_x + b4_w / 2,
        b4c_y + b4c_h - 0.32,
        "Bộ Lọc Sự Kiện Trượt" if is_vi else "Causal Event Filter",
        ha="center",
        va="center",
        fontsize=FS_SUB,
        fontweight="bold",
        color="#111827",
        zorder=4,
    )
    ax.text(
        b4_x + b4_w / 2,
        b4c_y + 1.15,
        ("Lọc $m$-trong-$n$ trượt nhân quả\n(cấu hình 2/3 hoặc 3/5)"
        if is_vi
        else "Causal $m$-out-of-$n$ filter\n(2/3 or 3/5 config)"),
        ha="center",
        va="center",
        fontsize=FS_BODY,
        color="#374151",
        linespacing=1.14,
        zorder=4,
    )
    ax.text(
        b4_x + b4_w / 2,
        b4c_y + 0.38,
        "Cắt giảm FAR thêm gần 5 lần" if is_vi else "Suppresses FAR by ~5x",
        ha="center",
        va="center",
        fontsize=FS_BODY,
        color="#B91C1C",
        fontweight="bold",
        zorder=4,
    )

    badge_y = b4c_y - b4_gap - badge_h
    _draw_box(ax, b4_x, badge_y, b4_w, badge_h, fc="#DCFCE7", ec="#16A34A", lw=1.2, r=0.08, zorder=3)
    ax.text(
        b4_x + b4_w / 2,
        badge_y + badge_h / 2,
        r"$\widehat{Y}_k \in \{0, 1\}$: CẢNH BÁO BẢO VỆ" if is_vi else r"$\widehat{Y}_k \in \{0, 1\}$: SECURE ALERT",
        ha="center",
        va="center",
        fontsize=FS_SUB,
        fontweight="bold",
        color="#166534",
        zorder=4,
    )

    # Downward flow in Col 4
    _draw_arrow(
        ax,
        (b4_x + b4_w / 2, b4a_y),
        (b4_x + b4_w / 2, b4b_y + b4b_h),
        color="#0369A1",
        lw=1.5,
        ms=9.5,
    )
    _draw_arrow(
        ax,
        (b4_x + b4_w / 2, b4b_y),
        (b4_x + b4_w / 2, b4c_y + b4c_h),
        color="#16A34A",
        lw=1.5,
        ms=9.5,
    )
    _draw_arrow(
        ax,
        (b4_x + b4_w / 2, b4c_y),
        (b4_x + b4_w / 2, badge_y + badge_h),
        color="#16A34A",
        lw=1.5,
        ms=9.5,
    )

    # Route z_k from Col 3 Stage 4 to Col 4 Box 1
    zk_x = b3_x + b3_w
    zk_y = s3_boxes[3][1] + s3_boxes[3][3] / 2
    bus_x = gap34_x + gap34_w / 2
    b4a_mid_y = b4a_y + b4a_h / 2
    ax.plot([zk_x, bus_x], [zk_y, zk_y], color="#0369A1", lw=1.6, zorder=5)
    ax.plot([bus_x, bus_x], [zk_y, b4a_mid_y], color="#0369A1", lw=1.6, zorder=5)
    _draw_arrow(
        ax,
        (bus_x, b4a_mid_y),
        (b4_x, b4a_mid_y),
        color="#0369A1",
        lw=1.6,
        ms=10.0,
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=300, bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)


# ---------------------------------------------------------------------------
# 2. Five-Method Comparison (comparison_v1[_vi]_*.png, 4 VI + 4 EN)
# ---------------------------------------------------------------------------
COMP_METHODS = [
    "raw_transformer",
    "structural_transformer",
    "canbertplus",
    "canlp",
    "assoc_rules_crysys",
]
COMP_LABELS = [
    "Raw TF (28D)",
    "Structural TF (30D)",
    "CANBERT+ adapted",
    "CANLP-char-DNN adapted",
    "CrySyS-AssocRules/W64",
]
# Okabe-Ito colorblind-safe palette
COMP_COLORS = ["#0072B2", "#D55E00", "#009E73", "#E69F00", "#CC79A7"]


def load_comparison_means() -> pd.DataFrame:
    csv_path = RESULTS / "comparison_merged_fast/all_metrics.csv"
    df = pd.read_csv(csv_path)
    sub = df[
        (df["file"] == "ALL")
        & (df["operating_point"] == "source_calibrated")
        & (df["condition"].isin(["A", "B", "C", "D"]))
    ].copy()
    metrics = ["Recall", "FAR_per_100k", "Attack_F1", "AP"]
    per_set = sub.groupby(["set", "method", "condition"], as_index=False)[metrics].mean()
    means = per_set.groupby(["method", "condition"], as_index=False)[metrics].mean()
    return means


def generate_comparison_figures(means: pd.DataFrame) -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.sans-serif": ["DejaVu Sans"],
            "font.size": 10.5,
        }
    )

    conditions = ["A", "B", "C", "D"]
    metric_specs = {
        "Recall": {
            "ylim": (0.0, 1.08),
            "yticks": [0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
            "ylabel_vi": "Recall",
            "ylabel_en": "Recall",
        },
        "FAR_per_100k": {
            "ylim": (0.0, 80000.0),
            "yticks": [0, 20000, 40000, 60000, 80000],
            "ylabel_vi": "FAR / 100.000 cửa sổ",
            "ylabel_en": "FAR / 100,000 windows",
        },
        "Attack_F1": {
            "ylim": (0.0, 1.08),
            "yticks": [0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
            "ylabel_vi": "Attack F1",
            "ylabel_en": "Attack F1",
        },
        "AP": {
            "ylim": (0.0, 1.08),
            "yticks": [0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
            "ylabel_vi": "Average Precision (AP)",
            "ylabel_en": "Average Precision (AP)",
        },
    }

    x = np.arange(len(conditions))
    n_m = len(COMP_METHODS)
    bar_w = 0.15

    for lang in ("vi", "en"):
        is_vi = lang == "vi"
        out_dir = VI_FIGS if is_vi else EN_FIGS
        out_dir.mkdir(parents=True, exist_ok=True)

        for metric, spec in metric_specs.items():
            fig, ax = plt.subplots(figsize=(4.4, 3.1), dpi=300)
            fig.patch.set_facecolor("white")

            piv = means.pivot(index="condition", columns="method", values=metric).reindex(conditions)
            for idx, (m, label, color) in enumerate(zip(COMP_METHODS, COMP_LABELS, COMP_COLORS)):
                offset = (idx - (n_m - 1) / 2.0) * bar_w
                vals = piv[m].values
                ax.bar(
                    x + offset,
                    vals,
                    width=bar_w,
                    label=label,
                    color=color,
                    edgecolor="#1F2937",
                    linewidth=0.55,
                    zorder=3,
                )

            ax.set_xticks(x)
            ax.set_xticklabels(conditions, rotation=0, fontsize=11.0, fontweight="bold")
            ax.set_xlabel(
                "Điều kiện đánh giá" if is_vi else "Evaluation condition",
                fontsize=11.0,
                labelpad=5,
            )
            ax.set_ylabel(spec["ylabel_vi"] if is_vi else spec["ylabel_en"], fontsize=11.0, labelpad=5)
            ax.set_ylim(*spec["ylim"])
            ax.set_yticks(spec["yticks"])
            if metric == "FAR_per_100k":
                ax.yaxis.set_major_formatter(
                    FuncFormatter(lambda v, _: "0" if v == 0 else f"{int(v // 1000)}k")
                )
            ax.tick_params(axis="y", labelsize=10.5)
            ax.grid(axis="y", linestyle="--", alpha=0.35, zorder=0)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)

            ax.legend(
                loc="lower center",
                bbox_to_anchor=(0.48, 1.02),
                ncol=2,
                frameon=True,
                facecolor="white",
                edgecolor="#D1D5DB",
                fontsize=9.9,
                handlelength=1.1,
                columnspacing=0.75,
                borderpad=0.30,
            )

            fig.tight_layout()
            fname = f"comparison_v1_vi_{metric}.png" if is_vi else f"comparison_v1_{metric}.png"
            fig.savefig(out_dir / fname, dpi=300, bbox_inches="tight", pad_inches=0.04)
            plt.close(fig)


# ---------------------------------------------------------------------------
# 3. Benign Calibration Recovery (VI ONLY: calibration_recovery_comparison.png)
# ---------------------------------------------------------------------------
def _format_atk(name: str) -> str:
    mapping = {
        "DoS": "DoS",
        "double": "Double",
        "force-neutral": "Force-Neut.",
        "fuzzing": "Fuzzing",
        "interval": "Interval",
        "rpm": "RPM",
        "rpm-accessory": "RPM-Acc.",
        "speed": "Speed",
        "speed-accessory": "Speed-Acc.",
        "standstill": "Standstill",
        "systematic": "Systematic",
        "triple": "Triple",
    }
    return mapping.get(name, name.capitalize())


def generate_calibration_recovery_vi() -> None:
    """Regenerate VI calibration_recovery_comparison.png (EN is kept untouched)."""
    cal_dir = RESULTS / "benign_calibration_posthoc_2026-11-10"
    summary = pd.read_csv(cal_dir / "benign_calibration_summary.csv")
    atk_summary = pd.read_csv(cal_dir / "per_attack_summary.csv")

    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["DejaVu Serif"],
            "font.size": 11.4,
            "axes.labelsize": 11.6,
            "axes.titlesize": 11.8,
            "xtick.labelsize": 11.4,
            "ytick.labelsize": 11.4,
            "legend.fontsize": 11.2,
        }
    )

    methods = ["raw_transformer", "structural_transformer", "structural_mixstyle"]
    display_names = {
        "raw_transformer": "Raw Transformer",
        "structural_transformer": "Structural Transformer",
        "structural_mixstyle": "Structural + MixStyle",
    }
    colors = {
        "raw_transformer": "#d95f02",
        "structural_transformer": "#1f78b4",
        "structural_mixstyle": "#2ca02c",
    }
    markers = {
        "raw_transformer": "s",
        "structural_transformer": "o",
        "structural_mixstyle": "^",
    }

    fig, axes = plt.subplots(2, 2, figsize=(8.2, 6.1), dpi=300)
    fig.patch.set_facecolor("white")

    # (a) Condition B, K=500
    ax1 = axes[0, 0]
    sub_b = summary[(summary.condition == "B") & (summary.warmup_k == 500)]
    for m in methods:
        data = sub_b[sub_b.method == m].sort_values("target_far_budget")
        ax1.plot(
            data["FAR_pct"],
            data["Recall"] * 100.0,
            marker=markers[m],
            color=colors[m],
            linewidth=2.0,
            markersize=6,
            label=display_names[m],
        )
    ax1.set_title("(a) Điều kiện B (Xe lạ, Tấn công quen)", pad=8, fontweight="bold")
    ax1.set_xlabel("FAR thực nghiệm trên đích (%)")
    ax1.set_ylabel("Recall tấn công (%)")
    ax1.grid(True, linestyle="--", alpha=0.6)

    # (b) Condition D, K=500
    ax2 = axes[0, 1]
    sub_d = summary[(summary.condition == "D") & (summary.warmup_k == 500)]
    for m in methods:
        data = sub_d[sub_d.method == m].sort_values("target_far_budget")
        ax2.plot(
            data["FAR_pct"],
            data["Recall"] * 100.0,
            marker=markers[m],
            color=colors[m],
            linewidth=2.0,
            markersize=6,
            label=display_names[m],
        )
    ax2.set_title("(b) Điều kiện D (Xe lạ, Tấn công lạ)", pad=8, fontweight="bold")
    ax2.set_xlabel("FAR thực nghiệm trên đích (%)")
    ax2.set_ylabel("Recall tấn công (%)")
    ax2.grid(True, linestyle="--", alpha=0.6)

    # (c) Condition B per-attack F1 (K=500, budget 1.0%)
    ax3 = axes[1, 0]
    atk_b = atk_summary[
        (atk_summary.condition == "B")
        & (atk_summary.warmup_k == 500)
        & (atk_summary.target_far_budget == 1000)
    ]
    attacks_b = sorted(atk_b.attack_type.unique(), reverse=True)
    y_pos = np.arange(len(attacks_b))
    bar_h = 0.26
    for i, m in enumerate(methods):
        vals = [
            atk_b[(atk_b.method == m) & (atk_b.attack_type == a)]["Attack_F1"].values[0]
            for a in attacks_b
        ]
        ax3.barh(
            y_pos + (i - 1) * bar_h,
            vals,
            height=bar_h,
            label=display_names[m],
            color=colors[m],
            alpha=0.88,
        )
    ax3.set_title("(c) Điều kiện B: F1 theo loại tấn công", pad=8, fontweight="bold")
    ax3.set_yticks(y_pos)
    ax3.set_yticklabels([_format_atk(a) for a in attacks_b], fontsize=11.4)
    ax3.set_xlabel("Điểm F1 (Lớp tấn công)")
    ax3.set_xlim(0.0, 1.05)
    ax3.grid(True, linestyle="--", alpha=0.5, axis="x")

    # (d) Condition D per-attack F1 (K=500, budget 1.0%)
    ax4 = axes[1, 1]
    atk_d = atk_summary[
        (atk_summary.condition == "D")
        & (atk_summary.warmup_k == 500)
        & (atk_summary.target_far_budget == 1000)
    ]
    attacks_d = sorted(atk_d.attack_type.unique(), reverse=True)
    y_pos_d = np.arange(len(attacks_d))
    for i, m in enumerate(methods):
        vals = [
            atk_d[(atk_d.method == m) & (atk_d.attack_type == a)]["Attack_F1"].values[0]
            for a in attacks_d
        ]
        ax4.barh(
            y_pos_d + (i - 1) * bar_h,
            vals,
            height=bar_h,
            label=display_names[m],
            color=colors[m],
            alpha=0.88,
        )
    ax4.set_title("(d) Điều kiện D: F1 tấn công zero-day", pad=8, fontweight="bold")
    ax4.set_yticks(y_pos_d)
    ax4.set_yticklabels([_format_atk(a) for a in attacks_d], fontsize=11.4)
    ax4.set_xlabel("Điểm F1 (Lớp tấn công)")
    ax4.set_xlim(0.0, 0.75)
    ax4.grid(True, linestyle="--", alpha=0.5, axis="x")

    handles, labels = ax1.get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.995),
        ncol=3,
        frameon=True,
        facecolor="white",
        edgecolor="#cccccc",
        fontsize=11.2,
        columnspacing=1.0,
        handlelength=1.6,
    )

    fig.tight_layout(rect=[0, 0, 1, 0.94], w_pad=1.6)
    VI_FIGS.mkdir(parents=True, exist_ok=True)
    fig.savefig(VI_FIGS / "calibration_recovery_comparison.png", dpi=300, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)


# ---------------------------------------------------------------------------
# 4. Multi-Source LOVO Overview (multisource_lovo_overview.png, VI & EN)
# ---------------------------------------------------------------------------
def generate_multisource_lovo() -> None:
    lovo_dir = RESULTS / "multisource_lovo_v2_2026-11-10"
    summary = pd.read_csv(lovo_dir / "summary.csv").set_index("method")
    probes = pd.read_csv(lovo_dir / "probe_summary.csv")
    pm = probes[(probes["task"] == "vehicle") & (probes["control"] == "learned")].set_index(
        ["method", "decoder"]
    )["balanced_accuracy"]

    order = ["raw", "structural", "structural_cadv", "relative_cadv"]
    xlabels = ["Raw", "Structural", "Structural + cAdv", "Relative + cAdv"]
    bar_colors = ["#7a869a", "#2676ab", "#20856d", "#c18a38"]

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.sans-serif": ["DejaVu Sans"],
            "font.size": 10.5,
        }
    )

    for lang in ("vi", "en"):
        is_vi = lang == "vi"
        out_dir = VI_FIGS if is_vi else EN_FIGS
        out_dir.mkdir(parents=True, exist_ok=True)

        fig, axes = plt.subplots(1, 3, figsize=(8.0, 3.6), dpi=300)
        fig.patch.set_facecolor("white")
        x = np.arange(len(order))

        # Panel 1: Recall (%)
        recalls = (summary.loc[order, "Recall"] * 100.0).values
        bars1 = axes[0].bar(x, recalls, color=bar_colors, edgecolor="#1F2937", linewidth=0.55, zorder=3)
        axes[0].set_ylabel("Recall phát hiện (%)" if is_vi else "Target attack recall (%)", fontsize=11.0)
        for b, v in zip(bars1, recalls):
            axes[0].text(b.get_x() + b.get_width() / 2, v + 2.0, f"{v:.1f}", ha="center", va="bottom", fontsize=9.4)

        # Panel 2: FAR (%)
        fars = summary.loc[order, "FAR_percent"].values
        bars2 = axes[1].bar(x, fars, color=bar_colors, edgecolor="#1F2937", linewidth=0.55, zorder=3)
        axes[1].set_ylabel("Tỷ lệ báo động giả (%)" if is_vi else "Target FAR (%)", fontsize=11.0)
        for b, v in zip(bars2, fars):
            axes[1].text(b.get_x() + b.get_width() / 2, v + 2.0, f"{v:.1f}", ha="center", va="bottom", fontsize=9.4)

        # Panel 3: Vehicle Probe Balanced Accuracy (%)
        width = 0.36
        lr_vals = [pm.loc[(m, "linear")] * 100.0 for m in order]
        mlp_vals = [pm.loc[(m, "mlp")] * 100.0 for m in order]
        b_lr = axes[2].bar(
            x - width / 2,
            lr_vals,
            width=width,
            color="#206b9e",
            edgecolor="#1F2937",
            linewidth=0.55,
            label="Tuyến tính (LR)" if is_vi else "Linear (LR)",
            zorder=3,
        )
        b_mlp = axes[2].bar(
            x + width / 2,
            mlp_vals,
            width=width,
            color="#d78735",
            edgecolor="#1F2937",
            linewidth=0.55,
            label="MLP",
            zorder=3,
        )
        axes[2].axhline(
            25.0,
            color="#111827",
            linestyle="--",
            linewidth=1.2,
            label="Ngẫu nhiên (25%)" if is_vi else "Chance (25%)",
            zorder=2,
        )
        axes[2].set_ylabel(
            "Probe xe cân bằng (%)" if is_vi else "Vehicle probe acc. (%)",
            fontsize=11.0,
        )
        for b, v in zip(b_lr, lr_vals):
            axes[2].text(
                b.get_x() + b.get_width() / 2,
                v + 2.0,
                f"{v:.1f}",
                ha="center",
                va="bottom",
                rotation=90,
                fontsize=9.0,
                clip_on=False,
            )
        for b, v in zip(b_mlp, mlp_vals):
            axes[2].text(
                b.get_x() + b.get_width() / 2,
                v + 2.0,
                f"{v:.1f}",
                ha="center",
                va="bottom",
                rotation=90,
                fontsize=9.0,
                clip_on=False,
            )

        handles, labels = axes[2].get_legend_handles_labels()
        fig.legend(
            handles,
            labels,
            loc="upper center",
            bbox_to_anchor=(0.68, 0.915),
            ncol=3,
            frameon=True,
            facecolor="white",
            edgecolor="#D1D5DB",
            fontsize=10.5,
            handlelength=1.1,
            columnspacing=0.7,
            borderpad=0.25,
        )

        for idx_ax, ax in enumerate(axes):
            ax.set_xticks(x)
            ax.set_xticklabels(xlabels, fontsize=10.5, rotation=24, ha="right")
            ax.set_ylim(0, 126 if idx_ax == 2 else 112)
            if idx_ax == 2:
                ax.set_xlim(-0.6, 3.6)
            ax.set_yticks([0, 20, 40, 60, 80, 100])
            ax.tick_params(axis="y", labelsize=10.5)
            ax.grid(axis="y", linestyle="--", alpha=0.22, zorder=0)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)

        fig.suptitle(
            "Học đa nguồn LOVO (trung bình đều 4 xe đích, 3 seed)"
            if is_vi
            else "Multi-source LOVO study (equal mean across 4 target vehicles, 3 seeds)",
            fontsize=12.0,
            fontweight="bold",
            y=0.99,
        )
        fig.tight_layout(rect=[0, 0, 1, 0.83])
        fig.savefig(out_dir / "multisource_lovo_overview.png", dpi=300, bbox_inches="tight", pad_inches=0.05)
        plt.close(fig)


# ---------------------------------------------------------------------------
# 5. Benign Invariant Overview (benign_invariant_overview.png, VI & EN)
# ---------------------------------------------------------------------------
def generate_benign_invariant() -> None:
    inv_dir = RESULTS / "benign_invariant_pipeline_2026-11-11"
    summary = pd.read_csv(inv_dir / "summary.csv")
    probes = pd.read_csv(inv_dir / "probe_summary.csv")

    sub = summary[(summary["alpha"] == 0.01) & (summary["view"] == "content_disjoint")].set_index("method")
    emb = probes[
        (probes["scope"] == "embedding")
        & (probes["task"] == "vehicle")
        & (probes["control"] == "learned")
    ].set_index(["method", "decoder"])["mean"]
    risk = probes[
        (probes["scope"] == "risk")
        & (probes["task"] == "vehicle")
        & (probes["control"] == "learned")
    ].set_index(["method", "decoder"])["mean"]

    # Aligned with tab:benign-invariant-main row order
    order = [
        "frozen_source",
        "frozen_targetq",
        "lr_targetq",
        "diag_lr",
        "white_lr",
        "white_pca8_lr",
        "white_leace_lr",
        "white_inlp8_lr",
    ]
    labels_en = [
        "Original /\nsource thresh.",
        "Original /\ntarget thresh.",
        "Shared LR /\ntarget thresh.",
        "Benign diag\n+ LR",
        "Benign whitening\n+ LR",
        "Whitening +\nPCA8 + LR",
        "Whitening +\nLEACE + LR",
        "Whitening +\nINLP8 + LR",
    ]
    labels_vi = [
        "Gốc /\nngưỡng nguồn",
        "Gốc /\nngưỡng đích",
        "LR chung /\nngưỡng đích",
        "Chuẩn hóa\nđường chéo + LR",
        "Làm trắng lành\n+ LR",
        "Làm trắng +\nPCA8 + LR",
        "Làm trắng +\nLEACE + LR",
        "Làm trắng +\nINLP8 + LR",
    ]

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.sans-serif": ["DejaVu Sans"],
            "font.size": 11.0,
        }
    )

    for lang in ("vi", "en"):
        is_vi = lang == "vi"
        out_dir = VI_FIGS if is_vi else EN_FIGS
        out_dir.mkdir(parents=True, exist_ok=True)
        row_labels = labels_vi if is_vi else labels_en

        fig, axes = plt.subplots(1, 3, figsize=(9.4, 6.1), dpi=300, sharey=True)
        fig.patch.set_facecolor("white")
        y = np.arange(len(order))
        height = 0.28
        off = 0.205

        # Panel 1: Held-out attack detection (Recall % and FAR %)
        recalls = (sub.loc[order, "Recall"] * 100.0).values
        fars = (sub.loc[order, "FAR_per_100k"] / 1000.0).values

        axes[0].axvline(
            1.0,
            color="#4B5563",
            linestyle=":",
            linewidth=1.3,
            label="Mục tiêu 1%" if is_vi else "Target 1%",
            zorder=1,
        )
        axes[0].barh(
            y - off,
            recalls,
            height=height,
            color="#206b9e",
            edgecolor="#1F2937",
            linewidth=0.45,
            label="Recall",
            zorder=3,
        )
        axes[0].barh(
            y + off,
            fars,
            height=height,
            color="#d78735",
            edgecolor="#1F2937",
            linewidth=0.45,
            label="FAR",
            zorder=3,
        )
        for yi, rv, fv in zip(y, recalls, fars):
            axes[0].text(rv + 1.6, yi - off, f"{rv:.1f}", va="center", ha="left", fontsize=11.0, zorder=4)
            fx = max(fv + 2.5, 3.6) if fv < 3.0 else fv + 1.6
            axes[0].text(
                fx,
                yi + off,
                f"{fv:.1f}",
                va="center",
                ha="left",
                fontsize=11.0,
                zorder=4,
                bbox=dict(boxstyle="round,pad=0.04", facecolor="white", edgecolor="none", alpha=0.90),
            )
        axes[0].set_title(
            "Phát hiện xe giữ ngoài\n(α = 1%)" if is_vi else "Held-out detection\n(α = 1%)",
            fontsize=12.2,
            fontweight="bold",
            pad=8,
        )

        # Panel 2: Vehicle probe 64D embedding
        emb_lr = [emb.loc[(m, "LR")] * 100.0 for m in order]
        emb_mlp = [emb.loc[(m, "MLP")] * 100.0 for m in order]
        axes[1].axvline(
            25.0,
            color="#4B5563",
            linestyle="--",
            linewidth=1.3,
            label="Ngẫu nhiên 25%" if is_vi else "Chance 25%",
            zorder=1,
        )
        axes[1].barh(
            y - off,
            emb_lr,
            height=height,
            color="#206b9e",
            edgecolor="#1F2937",
            linewidth=0.45,
            label="LR",
            zorder=3,
        )
        axes[1].barh(
            y + off,
            emb_mlp,
            height=height,
            color="#d78735",
            edgecolor="#1F2937",
            linewidth=0.45,
            label="MLP (300)" if is_vi else "MLP (300 max)",
            zorder=3,
        )
        for yi, lv, mv in zip(y, emb_lr, emb_mlp):
            axes[1].text(lv + 1.6, yi - off, f"{lv:.1f}", va="center", ha="left", fontsize=11.0, zorder=4)
            axes[1].text(mv + 1.6, yi + off, f"{mv:.1f}", va="center", ha="left", fontsize=11.0, zorder=4)
        axes[1].set_title(
            "Probe xe:\nbiểu diễn (64D / 8D)" if is_vi else "Vehicle probe:\nembedding (64D / 8D)",
            fontsize=12.2,
            fontweight="bold",
            pad=8,
        )

        # Panel 3: Vehicle probe 1D scalar risk
        r_lr = [risk.loc[(m, "LR")] * 100.0 for m in order]
        r_mlp = [risk.loc[(m, "MLP")] * 100.0 for m in order]
        axes[2].axvline(
            25.0,
            color="#4B5563",
            linestyle="--",
            linewidth=1.3,
            label="Ngẫu nhiên 25%" if is_vi else "Chance 25%",
            zorder=1,
        )
        axes[2].barh(
            y - off,
            r_lr,
            height=height,
            color="#206b9e",
            edgecolor="#1F2937",
            linewidth=0.45,
            label="LR",
            zorder=3,
        )
        axes[2].barh(
            y + off,
            r_mlp,
            height=height,
            color="#d78735",
            edgecolor="#1F2937",
            linewidth=0.45,
            label="MLP (300)" if is_vi else "MLP (300 max)",
            zorder=3,
        )
        for yi, lv, mv in zip(y, r_lr, r_mlp):
            axes[2].text(lv + 1.6, yi - off, f"{lv:.1f}", va="center", ha="left", fontsize=11.0, zorder=4)
            axes[2].text(mv + 1.6, yi + off, f"{mv:.1f}", va="center", ha="left", fontsize=11.0, zorder=4)
        axes[2].set_title(
            "Probe xe:\nđiểm rủi ro 1D" if is_vi else "Vehicle probe:\n1D scalar risk",
            fontsize=12.2,
            fontweight="bold",
            pad=8,
        )

        axes[0].set_yticks(y)
        axes[0].set_yticklabels(row_labels, fontsize=12.0)
        axes[0].invert_yaxis()
        axes[0].set_ylim(len(order) - 0.45, -0.55)

        for idx_ax, ax in enumerate(axes):
            ax.set_xlim(0, 130)
            ax.set_xticks([0, 50, 100])
            ax.tick_params(axis="x", labelsize=12.0)
            ax.set_xlabel("Tỷ lệ (%)" if is_vi else "Percent (%)", fontsize=12.0)
            ax.grid(axis="x", linestyle="--", alpha=0.22, zorder=0)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)

        h0, lab0 = axes[0].get_legend_handles_labels()
        h1, lab1 = axes[1].get_legend_handles_labels()
        fig.subplots_adjust(left=0.185, right=0.985, top=0.89, bottom=0.19, wspace=0.11)

        pos0 = axes[0].get_position()
        pos1 = axes[1].get_position()
        pos2 = axes[2].get_position()
        cx0 = 0.5 * (pos0.x0 + pos0.x1)
        cx12 = 0.5 * (pos1.x0 + pos2.x1)

        fig.legend(
            h0,
            lab0,
            loc="upper center",
            bbox_to_anchor=(cx0, 0.115),
            ncol=1,
            frameon=False,
            fontsize=12.0,
            handlelength=1.2,
        )
        fig.legend(
            h1,
            lab1,
            loc="upper center",
            bbox_to_anchor=(cx12, 0.115),
            ncol=3,
            frameon=False,
            fontsize=12.0,
            handlelength=1.2,
            columnspacing=0.9,
        )

        fig.savefig(out_dir / "benign_invariant_overview.png", dpi=300, bbox_inches="tight", pad_inches=0.05)
        plt.close(fig)


def main() -> None:
    print("Generating pipeline_architecture_30d.png (VI & EN)...")
    generate_pipeline_architecture("vi", VI_FIGS / "pipeline_architecture_30d.png")
    generate_pipeline_architecture("en", EN_FIGS / "pipeline_architecture_30d.png")

    print("Loading comparison_merged_fast/all_metrics.csv and generating comparison_v1 figures...")
    comp_means = load_comparison_means()
    generate_comparison_figures(comp_means)

    print("Generating calibration_recovery_comparison.png (VI only)...")
    generate_calibration_recovery_vi()

    print("Generating multisource_lovo_overview.png (VI & EN)...")
    generate_multisource_lovo()

    print("Generating benign_invariant_overview.png (VI & EN)...")
    generate_benign_invariant()

    print("Done! All 15 target figures generated at 300 DPI.")


if __name__ == "__main__":
    main()
