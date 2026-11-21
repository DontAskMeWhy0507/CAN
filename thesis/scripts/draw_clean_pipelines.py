#!/usr/bin/env python3
"""
Sinh lại Hình 3.1 (pipeline_overview_stage12.png) và Hình 3.2 (pipeline_architecture_30d.png)
theo bố cục ngang chuẩn bài báo quốc tế, đồng bộ phong cách BaiMau.pdf.
"""
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon, Circle

plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["mathtext.fontset"] = "dejavusans"


def add_box(ax, x, y, w, h, fc, ec, lw=1.4, r=0.12, ls="-", zorder=2):
    patch = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0.0,rounding_size={r}",
        facecolor=fc, edgecolor=ec, linewidth=lw, linestyle=ls, zorder=zorder
    )
    ax.add_patch(patch)
    return patch


def add_arrow(ax, x1, y1, x2, y2, color="#2C3E50", lw=1.5, ls="-", style="-|>", rad=0.0, zorder=5):
    ax.annotate(
        "", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(
            arrowstyle=style, color=color, lw=lw, linestyle=ls,
            mutation_scale=13, shrinkA=0, shrinkB=0,
            connectionstyle=f"arc3,rad={rad}"
        ),
        zorder=zorder
    )


def add_pill(ax, cx, cy, w, h, text, fc, ec, tc="white", fs=8.3, bold=True, zorder=6):
    add_box(ax, cx - w / 2, cy - h / 2, w, h, fc=fc, ec=ec, lw=1.2, r=h * 0.45, zorder=zorder)
    ax.text(
        cx, cy, text, ha="center", va="center",
        fontsize=fs, fontweight="bold" if bold else "normal",
        color=tc, linespacing=1.18, zorder=zorder + 1
    )


# =====================================================================
# HÌNH 3.1: SƠ ĐỒ TỔNG QUAN LUỒNG NGUỒN - ĐÍCH (2 LÀN NGANG)
# =====================================================================
def draw_fig31_overview(out_dir: Path):
    fig, ax = plt.subplots(figsize=(14.2, 5.5), dpi=300)
    ax.set_xlim(0, 14.2)
    ax.set_ylim(0, 5.5)
    ax.axis("off")

    # Tiêu đề 2 miền trên cùng
    add_box(ax, 0.20, 4.92, 6.40, 0.42, fc="#EBF5FB", ec="#2874A6", lw=1.2, r=0.10)
    ax.text(3.40, 5.13, "MIỀN XE NGUỒN (Huấn luyện & Chọn ngưỡng ngoại tuyến)",
            ha="center", va="center", fontsize=10.0, fontweight="bold", color="#1B4F72")

    add_box(ax, 7.30, 4.92, 6.70, 0.42, fc="#EAFAF1", ec="#1E8449", lw=1.2, r=0.10)
    ax.text(10.65, 5.13, "MIỀN XE ĐÍCH (Chuyển giao xuyên phương tiện — Không nhãn tấn công)",
            ha="center", va="center", fontsize=10.0, fontweight="bold", color="#145A32")

    # Đường phân tách dọc (Nguồn | Đích) và ngang (GĐ I | GĐ II)
    ax.plot([6.95, 6.95], [0.15, 5.38], color="#566573", lw=1.6, ls=":", zorder=1)
    ax.plot([0.15, 14.05], [2.58, 2.58], color="#7F8C8D", lw=1.3, ls="--", zorder=1)

    # ---- LÀN TRÊN: GIAI ĐOẠN I (ZERO-SHOT ĐÓNG BĂNG) ----
    ax.text(0.25, 4.62, "Giai đoạn I: Kiểm định Zero-Shot đóng băng hoàn toàn từ nguồn",
            ha="left", va="center", fontsize=9.3, fontweight="bold", color="#1B4F72")

    # B1: Dữ liệu nguồn
    add_box(ax, 0.25, 2.85, 1.65, 1.52, fc="#F4F9FD", ec="#2E86C1", lw=1.4)
    ax.text(1.075, 4.10, "Dữ liệu xe nguồn", ha="center", va="center", fontsize=8.8, fontweight="bold", color="#1B4F72")
    ax.text(1.075, 3.40, "Tách vòng ghi\nTrain / Validation\nHợp đồng dữ liệu\n(SHA-256, schema)",
            ha="center", va="center", fontsize=7.9, color="#2C3E50", linespacing=1.28)

    # B2: Trích xuất 30D
    add_box(ax, 2.25, 2.85, 1.72, 1.52, fc="#E8F8F5", ec="#16A085", lw=1.4)
    ax.text(3.11, 4.10, "Trích xuất 30D", ha="center", va="center", fontsize=8.8, fontweight="bold", color="#0E6251")
    ax.text(3.11, 3.40, "Cửa sổ $W = 64$\nLoại bỏ 11-bit ID\nCập nhật $H_k$\n(Nhánh nội dung)",
            ha="center", va="center", fontsize=7.9, color="#2C3E50", linespacing=1.28)

    # B3: Huấn luyện nguồn
    add_box(ax, 4.32, 2.85, 1.98, 1.52, fc="#FEF9E7", ec="#D68910", lw=1.4)
    ax.text(5.31, 4.10, "Huấn luyện nguồn", ha="center", va="center", fontsize=8.8, fontweight="bold", color="#7E5109")
    ax.text(5.31, 3.40, "Học Transformer $f_\\theta$\n(75.298 tham số)\nChọn $\\tau_{\\mathrm{src}}$ trên Val\n(FAR ≤ 0,1%)",
            ha="center", va="center", fontsize=7.9, color="#2C3E50", linespacing=1.28)

    add_arrow(ax, 1.90, 3.61, 2.25, 3.61)
    add_arrow(ax, 3.97, 3.61, 4.32, 3.61)

    # Mũi tên băng qua biên Nguồn -> Đích (GĐ I)
    add_arrow(ax, 6.30, 3.61, 7.62, 3.61, color="#1B4F72", lw=1.8)
    add_pill(ax, 6.95, 3.61, 1.06, 0.56, "Đóng băng\n$\\theta$ và $\\tau_{\\mathrm{src}}$", fc="#2C3E50", ec="#1C2833", fs=7.7)

    # B4: Suy luận zero-shot xe đích
    add_box(ax, 7.62, 2.85, 2.85, 1.52, fc="#F5EEF8", ec="#7D3C98", lw=1.4)
    ax.text(9.045, 4.10, "Suy luận Zero-Shot trên Xe đích", ha="center", va="center", fontsize=8.8, fontweight="bold", color="#4A235A")
    ax.text(9.045, 3.40, "Xe chưa từng quan sát (ĐK B, D, Ngoại bộ)\nTrích xuất cấu trúc 30D (nhân quả)\nChấm điểm $f_\\theta$ → So sánh ngưỡng $\\tau_{\\mathrm{src}}$",
            ha="center", va="center", fontsize=7.9, color="#2C3E50", linespacing=1.30)

    # B5: Hệ quả GĐ I
    add_box(ax, 10.82, 2.85, 3.18, 1.52, fc="#FDEDEC", ec="#C0392B", lw=1.5)
    ax.text(12.41, 4.10, "Phân kỳ xếp hạng & ngưỡng tĩnh", ha="center", va="center", fontsize=8.8, fontweight="bold", color="#922B21")
    ax.text(12.41, 3.40, "• AP xếp hạng vượt trội (+17,74%pt)\n• Trôi dạt logit do đan xen đặc trưng\n• Ngưỡng tĩnh $\\tau_{\\mathrm{src}}$ sụp đổ (FAR > 52%)",
            ha="center", va="center", fontsize=7.9, color="#641E16", linespacing=1.30)

    add_arrow(ax, 10.47, 3.61, 10.82, 3.61, color="#922B21")

    # ---- LÀN DƯỚI: GIAI ĐOẠN II (KHÔI PHỤC VẬN HÀNH) ----
    ax.text(0.25, 2.24, "Giai đoạn II: Khôi phục điểm vận hành qua hiệu chuẩn tiền tố lành tính & lọc sự kiện (Đề xuất)",
            ha="left", va="center", fontsize=9.3, fontweight="bold", color="#145A32")

    # C1: Khối cam kết nguyên tắc
    add_box(ax, 0.25, 0.35, 3.72, 1.55, fc="#F8F9F9", ec="#95A5A6", lw=1.2, ls="--")
    ax.text(2.11, 1.62, "Nguyên tắc chuyển giao an toàn", ha="center", va="center", fontsize=8.6, fontweight="bold", color="#2C3E50")
    ax.text(0.42, 0.96, "• Không thu thập dữ liệu tấn công có nhãn trên xe đích\n• Không huấn luyện lại hay tinh chỉnh trọng số $\\theta$\n• Chỉ ước lượng 1 ngưỡng phân vị vô hướng $\\tau_{\\mathrm{target}}$",
            ha="left", va="center", fontsize=7.9, color="#34495E", linespacing=1.35)

    # C2: Tái sử dụng f_theta
    add_box(ax, 4.32, 0.35, 1.98, 1.55, fc="#FEF9E7", ec="#D68910", lw=1.4)
    ax.text(5.31, 1.62, "Bộ mã hóa nguồn $f_\\theta$", ha="center", va="center", fontsize=8.8, fontweight="bold", color="#7E5109")
    ax.text(5.31, 0.96, "Giữ nguyên trọng số $\\theta$\n(Bộ nén rủi ro 1D:\n$64\\times 30 \\rightarrow s_k \\in [0, 1]$)",
            ha="center", va="center", fontsize=7.9, color="#2C3E50", linespacing=1.30)

    # Mũi tên truyền f_theta từ GĐ I xuống GĐ II
    add_arrow(ax, 5.31, 2.85, 5.31, 1.90, color="#B7950B", lw=1.5, ls="--")
    ax.text(5.40, 2.35, "Tái sử dụng $\\theta$", ha="left", va="center", fontsize=7.8, fontweight="bold", color="#7E5109")

    # Mũi tên băng qua biên Nguồn -> Đích (GĐ II)
    add_arrow(ax, 6.30, 1.12, 7.62, 1.12, color="#1E8449", lw=1.8)
    add_pill(ax, 6.95, 1.12, 1.06, 0.48, "Đóng băng $\\theta$", fc="#1E8449", ec="#145A32", fs=8.0)

    # C3: Tiền tố lành tính đích
    add_box(ax, 7.62, 0.35, 1.92, 1.55, fc="#EAFAF1", ec="#27AE60", lw=1.4)
    ax.text(8.58, 1.62, "Tiền tố lành tính", ha="center", va="center", fontsize=8.8, fontweight="bold", color="#145A32")
    ax.text(8.58, 0.96, "Khởi động xe đích\n$K = 500$ cửa sổ lành\n(không nhãn tấn công)",
            ha="center", va="center", fontsize=7.9, color="#2C3E50", linespacing=1.30)

    # C4: Hiệu chuẩn & Lọc trượt
    add_box(ax, 9.88, 0.35, 2.02, 1.55, fc="#E8F8F5", ec="#148F77", lw=1.4)
    ax.text(10.89, 1.62, "Hiệu chuẩn & Lọc", ha="center", va="center", fontsize=8.8, fontweight="bold", color="#0E6251")
    ax.text(10.89, 0.96, "$\\tau_{\\mathrm{target}} = Q_{1-\\alpha}(\\mathcal{S}_{\\mathrm{warm}})$\nBộ lọc trượt $m$-trong-$n$\n(2/3 hoặc 3/5 cửa sổ)",
            ha="center", va="center", fontsize=7.9, color="#2C3E50", linespacing=1.30)

    # C5: Kết quả vận hành
    add_box(ax, 12.24, 0.35, 1.76, 1.55, fc="#D5F5E3", ec="#196F3D", lw=1.6)
    ax.text(13.12, 1.62, "Vận hành ổn định", ha="center", va="center", fontsize=8.8, fontweight="bold", color="#145A32")
    ax.text(13.12, 0.96, "FAR ≤ 1,08%\nSau lọc: 0,14–0,22%\nỔn định đuôi FAR",
            ha="center", va="center", fontsize=7.9, fontweight="bold", color="#145A32", linespacing=1.32)

    add_arrow(ax, 9.54, 1.12, 9.88, 1.12, color="#1E8449")
    add_arrow(ax, 11.90, 1.12, 12.24, 1.12, color="#1E8449")

    plt.tight_layout(pad=0.2)
    fig.savefig(out_dir / "pipeline_overview_stage12.png", dpi=300, bbox_inches="tight")
    fig.savefig(out_dir / "pipeline_overview_stage12.pdf", bbox_inches="tight")
    plt.close(fig)


# =====================================================================
# HÌNH 3.2: KIẾN TRÚC CHI TIẾT KHUNG HAI GIAI ĐOẠN (CHUẨN BAIMAU.PDF)
# =====================================================================
def draw_fig32_architecture(out_dir: Path):
    fig, ax = plt.subplots(figsize=(15.2, 6.8), dpi=300)
    ax.set_xlim(0, 15.2)
    ax.set_ylim(0, 6.8)
    ax.axis("off")

    # ---- HAI KHUNG NÉT ĐỨT GIAI ĐOẠN I & GIAI ĐOẠN II ----
    add_box(ax, 0.15, 0.22, 8.20, 6.38, fc="#F7FBFE", ec="#1B4F72", lw=1.7, r=0.18, ls="--", zorder=1)
    ax.text(0.35, 6.36, "GIAI ĐOẠN I: BIỂU DIỄN CẤU TRÚC ĐỘC LẬP ĐỊNH DANH & BỘ MÃ HÓA NGUỒN ĐÓNG BĂNG",
            ha="left", va="center", fontsize=9.8, fontweight="bold", color="#1B4F72", zorder=2)

    add_box(ax, 8.65, 0.22, 6.40, 6.38, fc="#F5FCF7", ec="#1E6B3A", lw=1.7, r=0.18, ls="--", zorder=1)
    ax.text(8.85, 6.36, "GIAI ĐOẠN II: HIỆU CHUẨN NGƯỠNG & LỌC SỰ KIỆN TRƯỢT",
            ha="left", va="center", fontsize=9.8, fontweight="bold", color="#145A32", zorder=2)

    # ==========================================================
    # CỘT 1 (STAGE I): ĐẦU VÀO & BẢNG LỊCH SỬ H_k
    # ==========================================================
    # Hộp trên: Luồng CAN Bus Thô
    add_box(ax, 0.32, 3.65, 2.00, 2.38, fc="white", ec="#8E44AD", lw=1.5, r=0.12)
    add_box(ax, 0.32, 5.55, 2.00, 0.48, fc="#F4ECF7", ec="#8E44AD", lw=1.2, r=0.10)
    ax.text(1.32, 5.79, "1. Đầu vào CAN Bus", ha="center", va="center", fontsize=9.0, fontweight="bold", color="#5B2C6F")
    ax.text(1.32, 5.02, "Cửa sổ rời rạc W = 64\n$F_i = (t_i, c_i, d_i, \\mathbf{b}_i)$",
            ha="center", va="center", fontsize=8.4, color="#2C3E50", linespacing=1.35)
    add_box(ax, 0.44, 3.82, 1.76, 0.72, fc="#FDEDEC", ec="#C0392B", lw=1.0, r=0.08)
    ax.text(1.32, 4.18, "Loại bỏ 11-bit ID thô\nkhỏi đầu vào phân loại",
            ha="center", va="center", fontsize=7.8, fontweight="bold", color="#922B21", linespacing=1.25)

    # Hộp dưới: Bảng lịch sử H_k
    add_box(ax, 0.32, 0.45, 2.00, 2.75, fc="white", ec="#7D3C98", lw=1.5, r=0.12)
    add_box(ax, 0.32, 2.72, 2.00, 0.48, fc="#F4ECF7", ec="#7D3C98", lw=1.2, r=0.10)
    ax.text(1.32, 2.96, "Bảng lịch sử $H_k$", ha="center", va="center", fontsize=9.0, fontweight="bold", color="#5B2C6F")
    ax.text(1.32, 1.98, "Khóa: 11-bit ID ($c_i$)\nLưu: $(d_q, \\mathbf{b}_q, \\mathbf{m}_q)$\n130 KiB (Python)\n≈ 20,48 KiB (C/C++)",
            ha="center", va="center", fontsize=8.1, color="#2C3E50", linespacing=1.30)
    ax.text(1.32, 0.78, "Đặt lại: đầu bản ghi /\nchu kỳ khóa điện",
            ha="center", va="center", fontsize=7.8, fontweight="bold", color="#A93226", linespacing=1.22)

    # ==========================================================
    # CỘT 2 (STAGE I): TRÍCH XUẤT ĐẶC TRƯNG 30D
    # ==========================================================
    add_box(ax, 2.92, 0.45, 2.48, 5.58, fc="#E8F8F5", ec="#148F77", lw=1.5, r=0.12)
    add_box(ax, 2.92, 5.55, 2.48, 0.48, fc="#D1F2EB", ec="#148F77", lw=1.2, r=0.10)
    ax.text(4.16, 5.79, "2. Trích xuất cấu trúc (30D)", ha="center", va="center", fontsize=9.0, fontweight="bold", color="#0E6251")

    cards = [
        (4.36, 1.04, "Hình thái khung (0–16, 17D)",
         "DLC $d_i/8$, Payload $b_{i,j}/255$\nMặt nạ $m_{i,j} = \\mathbf{1}[j < d_i]$"),
        (3.16, 1.06, "Vi sai cùng ID (17–25, 9D)",
         "$|b_{i,j}-b_{q,j}| m_{i,j} m_{q,j}/255$\nCờ lịch sử $h_i = \\mathbf{1}[H_k(c_i) \\neq \\emptyset]$"),
        (1.96, 1.06, "Thống kê cục bộ (26–28, 3D)",
         "Tần suất $f_k(c_i)/W$\nHạng $\\mathrm{rank}_0(c_i)/U_k$, $\\mathrm{rank}_0(c_i)/W$"),
        (0.62, 1.20, "Chuyển tiếp ID (29, 1D)",
         "Cặp kề $T_k(c_{i-1}, c_i)/(W-1)$\n(Bus đồng hồ chuẩn: +$\\Delta t, \\Delta t_{\\mathrm{ID}}$ → 32D)"),
    ]
    for cy, ch, ctitle, cbody in cards:
        add_box(ax, 3.04, cy, 2.24, ch, fc="white", ec="#76D7C4", lw=1.1, r=0.08)
        ax.text(4.16, cy + ch - 0.22, ctitle, ha="center", va="center", fontsize=8.1, fontweight="bold", color="#0E6251")
        ax.text(4.16, cy + (ch - 0.30) / 2, cbody, ha="center", va="center", fontsize=7.6, color="#1B4F72", linespacing=1.28)

    # Mũi tên Cột 1 <-> Cột 2
    add_arrow(ax, 2.32, 4.85, 2.92, 4.85, color="#2C3E50", lw=1.6)
    ax.text(2.62, 5.05, "$\\mathcal{W}_k$", ha="center", va="center", fontsize=8.6, fontweight="bold", color="#2C3E50")

    add_arrow(ax, 2.32, 2.08, 2.92, 2.08, color="#148F77", lw=1.4)
    ax.text(2.62, 2.26, "Tra cứu", ha="center", va="center", fontsize=7.4, fontweight="bold", color="#0E6251")
    add_arrow(ax, 2.92, 1.56, 2.32, 1.56, color="#7D3C98", lw=1.4)
    ax.text(2.62, 1.35, "Cập nhật", ha="center", va="center", fontsize=7.4, fontweight="bold", color="#5B2C6F")

    # ==========================================================
    # CỘT 3 (STAGE I): TRANSFORMER ĐÓNG BĂNG + ĐẦU PHÂN LOẠI
    # ==========================================================
    add_box(ax, 5.94, 0.45, 2.26, 5.58, fc="#FEF9E7", ec="#D68910", lw=1.5, r=0.12)
    add_box(ax, 5.94, 5.55, 2.26, 0.48, fc="#FCF3CF", ec="#D68910", lw=1.2, r=0.10)
    ax.text(7.07, 5.79, "3. Mã hóa Transformer", ha="center", va="center", fontsize=9.0, fontweight="bold", color="#7E5109")

    # Pill badge Đóng băng
    add_pill(ax, 7.07, 5.26, 2.04, 0.34, "ĐÓNG BĂNG θ (75.298 tham số)", fc="#1B4F72", ec="#154360", fs=7.4)

    tf_blocks = [
        (4.24, 0.72, "Chiếu tuyến tính & Vị trí", "30 → 64 + PosEnc (64×64)"),
        (3.20, 0.78, "2 Lớp Transformer Encoder", "4 Heads, FFN 128, GELU, Drop 0,1"),
        (2.20, 0.74, "Gộp trung bình (Mean Pool)", "Biểu diễn ẩn $z_k \\in \\mathbb{R}^{64}$"),
        (0.75, 1.18, "Đầu phân loại nhị phân", "LN → Lin(64→32) → ReLU\n→ Lin(32→2) → Softmax\nĐiểm rủi ro $s_k \\in [0, 1]$"),
    ]
    for by, bh, btitle, bbody in tf_blocks:
        add_box(ax, 6.06, by, 2.02, bh, fc="white", ec="#F5B041", lw=1.1, r=0.08)
        ax.text(7.07, by + bh - 0.21, btitle, ha="center", va="center", fontsize=8.1, fontweight="bold", color="#7E5109")
        ax.text(7.07, by + (bh - 0.28) / 2, bbody, ha="center", va="center", fontsize=7.6, color="#2C3E50", linespacing=1.25)

    # Mũi tên dọc giữa 4 khối Transformer
    add_arrow(ax, 7.07, 4.24, 7.07, 3.98, color="#B7950B", lw=1.4)
    add_arrow(ax, 7.07, 3.20, 7.07, 2.94, color="#B7950B", lw=1.4)
    add_arrow(ax, 7.07, 2.20, 7.07, 1.93, color="#B7950B", lw=1.4)

    # Mũi tên Cột 2 -> Cột 3
    add_arrow(ax, 5.40, 3.25, 5.94, 3.25, color="#2C3E50", lw=1.6)
    ax.text(5.67, 3.47, "$X_k$", ha="center", va="center", fontsize=8.6, fontweight="bold", color="#2C3E50")
    ax.text(5.67, 3.03, "64×30", ha="center", va="center", fontsize=7.6, color="#566573")

    # ==========================================================
    # GIAI ĐOẠN II (PHẢI): 2 NHÁNH RÕ RÀNG TỪ ĐIỂM RỦI RO s_k
    # ==========================================================
    y_main = 1.34  # Trục ngang chính căn giữa Đầu phân loại và Hình thoi quyết định

    # Điểm chia nhánh tại x = 8.95
    ax.plot([8.20, 8.95], [y_main, y_main], color="#1B4F72", lw=1.8, zorder=4)
    ax.add_patch(Circle((8.95, y_main), 0.055, facecolor="#1B4F72", edgecolor="#1B4F72", zorder=6))
    ax.text(8.50, y_main + 0.22, "$s_k$", ha="center", va="center", fontsize=9.2, fontweight="bold", color="#1B4F72")

    # ---- NHÁNH TRÊN: PHA KHỞI ĐỘNG LÀNH TÍNH (1 LẦN) ----
    add_box(ax, 9.20, 3.92, 5.68, 2.10, fc="#EAFAF1", ec="#27AE60", lw=1.3, r=0.12, ls=":")
    ax.text(9.35, 5.79, "Pha khởi động lành tính (1 lần, không nhãn, $k < K_{\\mathrm{valid}}$)",
            ha="left", va="center", fontsize=8.4, fontweight="bold", color="#145A32")

    # Box 2a: Tích lũy S_warm
    add_box(ax, 9.35, 4.12, 2.40, 1.42, fc="white", ec="#27AE60", lw=1.2, r=0.09)
    ax.text(10.55, 5.26, "Tích lũy điểm nền", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#145A32")
    ax.text(10.55, 4.58, "Tiền tố lành $K = 500$ cửa sổ\nĐa tập $\\mathcal{S}_{\\mathrm{warm}}$ ($N_{\\mathrm{pool}}$)\nChặn an toàn $\\lfloor L_{\\mathrm{benign}}/2 \\rfloor$",
            ha="center", va="center", fontsize=7.8, color="#2C3E50", linespacing=1.28)

    # Box 2b: Ước lượng phân vị 1D
    add_box(ax, 12.25, 4.12, 2.48, 1.42, fc="white", ec="#1E8449", lw=1.3, r=0.09)
    ax.text(13.49, 5.26, "Ước lượng phân vị 1D", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#145A32")
    ax.text(13.49, 4.58, "$\\tau_{\\mathrm{target}} = Q_{1-\\alpha}(\\mathcal{S}_{\\mathrm{warm}})$\nNgân sách danh định $\\alpha$\n(Chỉ 1 tham số vô hướng)",
            ha="center", va="center", fontsize=7.8, color="#145A32", linespacing=1.28)

    add_arrow(ax, 11.75, 4.83, 12.25, 4.83, color="#1E8449", lw=1.5)

    # Mũi tên đi lên từ điểm chia nhánh -> Box 2a
    ax.plot([8.95, 8.95], [y_main, 4.83], color="#1E8449", lw=1.6, zorder=4)
    add_arrow(ax, 8.95, 4.83, 9.35, 4.83, color="#1E8449", lw=1.6)
    ax.text(8.95, 3.25, "$k < K_{\\mathrm{valid}}$", ha="center", va="center", fontsize=7.5,
            fontweight="bold", color="#145A32", rotation=90,
            bbox=dict(boxstyle="round,pad=0.15", fc="#F5FCF7", ec="none"), zorder=5)

    # ---- NHÁNH DƯỚI: PHA GIÁM SÁT VẬN HÀNH ----
    add_box(ax, 9.20, 0.45, 5.68, 2.65, fc="#EBF5FB", ec="#2E86C1", lw=1.3, r=0.12, ls=":")
    ax.text(9.35, 2.86, "Pha giám sát hậu khởi động ($k \\geq K_{\\mathrm{valid}}$)",
            ha="left", va="center", fontsize=8.4, fontweight="bold", color="#1B4F72")

    # Hình thoi quyết định: s_k >= tau_target ?
    dx_c, dy_c = 10.12, y_main
    dx_r, dy_r = 0.78, 0.68
    diamond = Polygon([
        (dx_c, dy_c + dy_r),
        (dx_c + dx_r, dy_c),
        (dx_c, dy_c - dy_r),
        (dx_c - dx_r, dy_c),
    ], closed=True, facecolor="#FEF9E7", edgecolor="#D4AC0D", linewidth=1.6, zorder=3)
    ax.add_patch(diamond)
    ax.text(dx_c, dy_c, "$s_k \\geq \\tau_{\\mathrm{target}}$ ?",
            ha="center", va="center", fontsize=8.4, fontweight="bold", color="#7E5109", zorder=4)

    # Mũi tên từ điểm chia nhánh -> Hình thoi
    add_arrow(ax, 8.95, y_main, dx_c - dx_r, y_main, color="#1B4F72", lw=1.7)

    # Mũi tên phản hồi ngưỡng tau_target từ Box 2b -> đỉnh trên Hình thoi
    y_mid = 3.50
    ax.plot([13.49, 13.49], [4.12, y_mid], color="#1E8449", lw=1.6, zorder=4)
    ax.plot([13.49, dx_c], [y_mid, y_mid], color="#1E8449", lw=1.6, zorder=4)
    add_arrow(ax, dx_c, y_mid, dx_c, dy_c + dy_r, color="#1E8449", lw=1.6)
    ax.text(11.82, y_mid, "Ngưỡng vận hành $\\tau_{\\mathrm{target}}$",
            ha="center", va="center", fontsize=8.0, fontweight="bold", color="#145A32",
            bbox=dict(boxstyle="round,pad=0.2", fc="#F5FCF7", ec="#A9DFBF", lw=0.8), zorder=6)

    # Box 2c: Bộ lọc trượt m-trong-n
    add_box(ax, 11.35, 0.68, 1.65, 1.32, fc="white", ec="#2874A6", lw=1.3, r=0.09)
    ax.text(12.175, 1.75, "Lọc m-trong-n", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#1B4F72")
    ax.text(12.175, 1.15, "Trượt nhân quả\n(2/3 hoặc 3/5)\n$\\sum a_r \\geq m$",
            ha="center", va="center", fontsize=7.9, color="#2C3E50", linespacing=1.26)

    add_arrow(ax, dx_c + dx_r, y_main, 11.35, y_main, color="#2874A6", lw=1.5)
    ax.text(11.12, y_main + 0.20, "$a_k$", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#1B4F72")

    # Box 2d: Cảnh báo đầu ra
    add_box(ax, 13.36, 0.68, 1.38, 1.32, fc="white", ec="#1E8449", lw=1.4, r=0.09)
    ax.text(14.05, 1.76, "Quyết định $\\hat{Y}_k$", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#1B4F72")
    ax.text(14.05, 1.30, "0: Bình thường", ha="center", va="center", fontsize=7.8, fontweight="bold", color="#1E8449")
    ax.text(14.05, 0.94, "1: Xâm nhập", ha="center", va="center", fontsize=7.8, fontweight="bold", color="#C0392B")

    add_arrow(ax, 13.00, y_main, 13.36, y_main, color="#1E8449", lw=1.5)

    plt.tight_layout(pad=0.2)
    fig.savefig(out_dir / "pipeline_architecture_30d.png", dpi=300, bbox_inches="tight")
    fig.savefig(out_dir / "pipeline_architecture_30d.pdf", bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    target_dir = Path("thesis/vi/figs")
    target_dir.mkdir(parents=True, exist_ok=True)
    draw_fig31_overview(target_dir)
    draw_fig32_architecture(target_dir)
    print("Đã xuất thành công Hình 3.1 và Hình 3.2 vào:", target_dir.resolve())
