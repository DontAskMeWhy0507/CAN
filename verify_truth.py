#!/usr/bin/env python3
"""Kiểm định chéo đảm bảo 0 số liệu bịa đặt và 0 lỗi sót trong thesis/vi/main.tex."""
from pathlib import Path
import sys

tex = Path("thesis/vi/main.tex").read_text(encoding="utf-8")

# 1. Các chuỗi BỊA ĐẶT / LỖI từ main_4.pdf TUYỆT ĐỐI PHẢI VẮNG MẶT
FORBIDDEN = [
    "supplementary.pdf",
    "tau_{\\text{target.}}",
    "\\tau_{target.}",
    "CPU Intel Core",
    "352.483",
    "412.015",
    "0,9124",
    "0,9245",
    "0,2131",
    "0,3412",
    "0,2679",
    "0,9102",
    "Entropy tải trọng",
    "t-SNE",
    "0,9914",
    "0,1050",
    "3,771",
    "0,004",
    "63,40",
    "Structural bỏ $\\Delta t$",
    "\\alpha = 0,4",
    "\\tau_{\\text{source}} = 0,5",
    "\\tau_{source}=0,5",
    "\\tau_{targct}",
    "69,84(%)",
    "\\subsubsection",
]

# 2. Các số liệu SỰ THẬT CỐT LÕI BẮT BUỘC PHẢI CÓ MẶT
REQUIRED_TRUTH = [
    "0,5554", "0,3357", "0,9359", "0,9638",   # Bảng 4.3 & 4.4
    "0,4859", "0,1387", "66,99",              # Bảng 4.5
    "0,7048", "0,7605", "4,999", "7,564",     # Bảng 4.6 (Target-Only thật)
    "0,9642", "0,9670", "0,7565", "0,7269",   # Bảng 4.8 (Probe thật)
    "0,6020", "0,6172", "37,53", "44,96",     # Bảng 4.9 (Adaptation thật)
    "0,3336", "0,167", "3,271", "0,0065",     # Bảng 4.10 (External thật)
    "1,083", "3,036", "0,731", "4,830",       # Bảng 4.11 (Latency thật)
    "Ryzen", "RTX",                           # Phần cứng thật
]

bad_hits = [s for s in FORBIDDEN if s in tex]
missing_truth = [s for s in REQUIRED_TRUTH if s not in tex]

if bad_hits:
    print("[LỖI] Còn sót chuỗi bịa đặt / lỗi cũ:", bad_hits)
if missing_truth:
    print("[LỖI] Thiếu số liệu sự thật cốt lõi:", missing_truth)
if not bad_hits and not missing_truth:
    print("[ĐẠT 100%] Không còn chuỗi bịa đặt; toàn bộ số liệu cốt lõi khớp chính xác bản gốc.")
    sys.exit(0)
sys.exit(1)
