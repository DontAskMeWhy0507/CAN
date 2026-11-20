#!/usr/bin/env python3
"""
Công cụ kiểm toán và chuẩn hóa LaTeX cho khóa luận tốt nghiệp.
Hỗ trợ 2 chế độ:
  1. --mode audit        : Quét toàn bộ thư mục .tex, báo cáo 4 nhóm lỗi (chỉ đọc).
  2. --mode fix-decimals : Chuyển dấu '.' thập phân -> ',' trong tabular/longtable
                           (có tạo bản sao lưu .bak và hỗ trợ --dry-run).
"""

import argparse
import re
import shutil
from pathlib import Path
from typing import List, Tuple

# 1. Danh sách chuỗi biến code / tên tệp thô cần thay trong thân bài chính
RAW_CODE_PATTERNS = [
    (r"\bprefix_end\b", "Thay bằng ký hiệu $L_{\\text{benign}}$"),
    (r"\bsampling_seed\b", "Bỏ tên biến code trong văn xuôi (giữ số ở Bảng 4.2)"),
    (r"ctt-content-order-comparison-v1", "Chuyển vào Phụ lục A.1, dùng tên tiếng Việt ở Chương 4"),
    (r"\bfrac_score_1\b", "Viết thành 'tỷ lệ cửa sổ nhận điểm cực đại 1,0'"),
    (r"\bwhite_energy\b", "Thay bằng $E_{\\text{white}}$ hoặc 'điểm năng lượng làm trắng'"),
    (r"\bcontent_disjoint\b", "Thay bằng 'lọc trùng nội dung theo mã băm SHA-256'"),
    (r"\b(?:dlc_and_masks|dlc_masks_9D|local_stats|no_payload|no_delta|no_local(?:_stats)?|no_transition|has_prev_1D|all_30D)\b",
     "Chuyển sang tên tiếng Việt trong thân bài"),
    (r"\b(?:structural_no_payload|structural_no_delta|structural_no_local|structural_mixstyle)\b",
     "Thay bằng tên biến thể học thuật (bỏ dấu gạch dưới)"),
    (r"\b(?:Opel_Astra_DoS|Opel_Astra_benign|Renault_Clio_DoS|Renault_Clio_benign|CAN_MIRGU_attack|CAN_MIRGU_benign)\b",
     "Bỏ dấu gạch dưới (ví dụ: Opel Astra (DoS))"),
    (r"\bset_0[1-4]\b", "Thống nhất thành 'Tập 1' .. 'Tập 4'"),
    (r"\b[a-zA-Z0-9_\-/]+\.csv\b", "Tránh đưa tên tệp .csv thô vào thân bài chính"),
    (r"\b(?:multisource_lovo_v2|benign_invariant_pipeline|WindowExtractor|\.frames\.f32)\b",
     "Chỉ giữ ở Phụ lục cấu hình mã nguồn"),
]

# 2. Danh sách thuật ngữ Anh-Việt dễ bị dùng lẫn lộn trong văn xuôi tiếng Việt
MIXED_TERM_PATTERNS = [
    (r"\bframes?\b", "Thống nhất thành 'khung tin'"),
    (r"\bwindows?\b", "Thống nhất thành 'cửa sổ'"),
    (r"\bfiles?\b", "Thống nhất thành 'tệp dữ liệu' hoặc 'bản ghi'"),
    (r"\bcaptures?\b", "Thống nhất thành 'bản ghi'"),
    (r"\btraces?\b", "Thống nhất thành 'bản ghi' hoặc 'luồng ghi'"),
    (r"\bseeds?\b", "Thống nhất thành 'hạt giống' (trừ tên cột ngắn nếu cần)"),
    (r"\bfit\b", "Tránh dùng động từ 'fit' xen tiếng Việt -> 'ước lượng' / 'khớp'"),
    (r"\bbenign\b", "Thống nhất thành 'lành tính' (trừ nhãn tiếng Anh cố định)"),
    (r"\bwarmup\b", "Thống nhất thành 'tiền tố lành tính' / 'pha khởi động'"),
]

# 3. Dấu hiệu rò rỉ kết quả ngược trong Chương 1 & Chương 3
BACKWARD_LEAK_PATTERNS = [
    (r"(?:Mục|Bảng|Hình)\s+4\.\d+", "Tham chiếu sang Chương 4 từ chương lý thuyết/phương pháp"),
    (r"(?:Phụ lục|Mục|Bảng)\s+[AB]\.\d+", "Tham chiếu sang kết quả Phụ lục thực nghiệm"),
    (r"\b3\.539\b|\b6\.000\b", "Số liệu thực nghiệm N_pool rò rỉ sang Chương 1/3"),
    (r"\b100\s+tệp\b|\b136\s+tệp\b|\b236\s+tệp\b", "Số liệu kiểm toán CTT rò rỉ sang Chương 1/3"),
    (r"Set\s*4|Tập\s*4", "Nhắc kết quả Tập 4 trong chương lý thuyết/phương pháp"),
]

# Các vùng LaTeX bên trong bảng TUYỆT ĐỐI KHÔNG ĐƯỢC đụng vào khi sửa dấu thập phân
PROTECT_REGEXES = [
    r"(?<!\\)%[^\n]*",                                           # Comment LaTeX
    r"\\(?:label|ref|eqref|pageref|autoref|cite|citep|citet|url|href|includegraphics)\s*(?:\[[^\]]*\])?\{[^}]*\}",
    r"\\(?:begin|end)\{(?:tabularx?|longtable)\}(?:\[[^\]]*\])?(?:\{[^}]*\})?\{[^}]*\}",
    r"\b\d+\.\d+\s*(?:cm|mm|pt|bp|em|ex|in|sp|\\textwidth|\\linewidth|\\columnwidth|\\paperwidth)\b",
    r"\\(?:arraystretch|baselinestretch)\}\{[\d.]+\}",
    r"(?:Bảng|Hình|Mục|Chương|Thuật toán|Phụ lục|Table|Figure|Section)\s+[A-Z0-9]+\.\d+(?:\.\d+)?",
    r"\bCAN\s*2\.0[AB]?\b",
    r"\bv\d+\.\d+(?:\.\d+)?\b",
    r"\b[a-zA-Z0-9_\-/]+\.(?:csv|tex|pdf|png|jpg|py|f32)\b",
    r"\b\d{1,3}(?:\.\d{3}){2,}\b",                               # Số nhiều dấu chấm hàng nghìn (vd: 5.359.680)
]

TABLE_ENV_RE = re.compile(
    r"(\\begin\{(?:tabularx?|longtable)\}.*?\\end\{(?:tabularx?|longtable)\})",
    re.DOTALL,
)

# Số thập phân CHẮC CHẮN: 0.xxx (mọi độ dài) HOẶC [1-9]\d*\.\d{1,2} HOẶC [1-9]\d*\.\d{4,}
CERTAIN_DECIMAL_RE = re.compile(
    r"(?<![\d.])(0\.\d+|[1-9]\d*\.(?:\d{1,2}|\d{4,}))(?![\d.])"
)

# Số 3 chữ số sau dấu chấm với phần nguyên khác 0: MƠ HỒ giữa hàng nghìn (75.170) và thập phân (1.083 ms)
AMBIGUOUS_3DIGIT_RE = re.compile(
    r"(?<![\d.])([1-9]\d*\.\d{3})(?![\d.])"
)


def mask_protected(text: str) -> Tuple[str, List[str]]:
    """Ẩn tạm các đoạn mã LaTeX cần bảo vệ bằng placeholder."""
    placeholders: List[str] = []

    def _repl(match: re.Match) -> str:
        idx = len(placeholders)
        placeholders.append(match.group(0))
        return f"@@MASK_{idx}@@"

    masked = text
    for pat in PROTECT_REGEXES:
        masked = re.sub(pat, _repl, masked)
    return masked, placeholders


def unmask_protected(text: str, placeholders: List[str]) -> str:
    """Khôi phục các đoạn mã LaTeX đã ẩn."""
    restored = text
    for idx in range(len(placeholders) - 1, -1, -1):
        restored = restored.replace(f"@@MASK_{idx}@@", placeholders[idx])
    return restored


def strip_comments_and_commands_for_prose(line: str) -> str:
    """Loại bỏ comment và nội dung trong \label/\ref/\cite để tránh báo động giả."""
    line = re.sub(r"(?<!\\)%.*$", "", line)
    line = re.sub(r"\\(?:label|ref|eqref|cite|includegraphics|input|include)\{[^}]*\}", "", line)
    return line


def audit_file(tex_path: Path, is_theory_or_method: bool) -> dict:
    content = tex_path.read_text(encoding="utf-8")
    lines = content.splitlines()
    report = {
        "certain_decimals": [],
        "ambiguous_3digit": [],
        "raw_code": [],
        "mixed_terms": [],
        "backward_leaks": [],
    }

    # A. Kiểm tra dấu thập phân trong bảng
    for match in TABLE_ENV_RE.finditer(content):
        table_start_line = content[: match.start()].count("\n") + 1
        masked, _ = mask_protected(match.group(0))
        for m in CERTAIN_DECIMAL_RE.finditer(masked):
            line_no = table_start_line + masked[: m.start()].count("\n")
            report["certain_decimals"].append((line_no, m.group(1)))
        for m in AMBIGUOUS_3DIGIT_RE.finditer(masked):
            line_no = table_start_line + masked[: m.start()].count("\n")
            report["ambiguous_3digit"].append((line_no, m.group(1)))

    # B. Kiểm tra từng dòng cho biến code, thuật ngữ lẫn lộn và rò rỉ ngược
    for idx, raw_line in enumerate(lines, start=1):
        clean_line = strip_comments_and_commands_for_prose(raw_line)
        if not clean_line.strip():
            continue

        for pat, hint in RAW_CODE_PATTERNS:
            for m in re.finditer(pat, clean_line):
                report["raw_code"].append((idx, m.group(0), hint))

        for pat, hint in MIXED_TERM_PATTERNS:
            for m in re.finditer(pat, clean_line, flags=re.IGNORECASE):
                report["mixed_terms"].append((idx, m.group(0), hint))

        if is_theory_or_method:
            for pat, hint in BACKWARD_LEAK_PATTERNS:
                for m in re.finditer(pat, clean_line):
                    report["backward_leaks"].append((idx, m.group(0), hint))

    return report


def fix_decimals_in_file(tex_path: Path, force_3digit: bool, dry_run: bool) -> Tuple[int, List[Tuple[int, str]]]:
    content = tex_path.read_text(encoding="utf-8")
    total_replaced = 0
    skipped_ambiguous: List[Tuple[int, str]] = []

    def _process_table(match: re.Match) -> str:
        nonlocal total_replaced
        table_start_line = content[: match.start()].count("\n") + 1
        masked, placeholders = mask_protected(match.group(0))

        def _to_comma(num_match: re.Match) -> str:
            nonlocal total_replaced
            total_replaced += 1
            return num_match.group(1).replace(".", ",")

        updated = CERTAIN_DECIMAL_RE.sub(_to_comma, masked)

        if force_3digit:
            updated = AMBIGUOUS_3DIGIT_RE.sub(_to_comma, updated)
        else:
            for m in AMBIGUOUS_3DIGIT_RE.finditer(updated):
                line_no = table_start_line + updated[: m.start()].count("\n")
                skipped_ambiguous.append((line_no, m.group(1)))

        return unmask_protected(updated, placeholders)

    new_content = TABLE_ENV_RE.sub(_process_table, content)

    if not dry_run and total_replaced > 0:
        backup_path = tex_path.with_suffix(tex_path.suffix + ".bak")
        shutil.copy2(tex_path, backup_path)
        tex_path.write_text(new_content, encoding="utf-8")

    return total_replaced, skipped_ambiguous


def main() -> None:
    parser = argparse.ArgumentParser(description="Kiểm toán và chuẩn hóa LaTeX khóa luận.")
    parser.add_argument("target", type=Path, help="Đường dẫn thư mục chứa .tex hoặc một tệp .tex cụ thể")
    parser.add_argument("--mode", choices=["audit", "fix-decimals"], default="audit")
    parser.add_argument("--dry-run", action="store_true", help="Xem trước số lượng thay đổi, không ghi tệp")
    parser.add_argument("--force-3digit", action="store_true",
                        help="Cũng đổi các số dạng X.XXX (chỉ nên bật cho tệp chứa bảng ms/% như Bảng 4.12-4.14)")
    args = parser.parse_args()

    tex_files = [args.target] if args.target.is_file() else sorted(args.target.rglob("*.tex"))
    if not tex_files:
        print("Không tìm thấy tệp .tex nào.")
        return

    if args.mode == "audit":
        for path in tex_files:
            name_low = path.name.lower()
            is_ch1_or_ch3 = any(k in name_low for k in ["ch1", "ch3", "chap1", "chap3", "chuong1", "chuong3", "background", "method"])
            rep = audit_file(path, is_theory_or_method=is_ch1_or_ch3)
            total_hits = sum(len(v) for v in rep.values())
            if total_hits == 0:
                continue

            print(f"\n==================== {path} ====================")
            if rep["certain_decimals"]:
                sample = ", ".join(f"L{ln}:{val}" for ln, val in rep["certain_decimals"][:12])
                print(f"  [Dấu chấm thập phân trong bảng] ({len(rep['certain_decimals'])}): {sample} ...")
            if rep["ambiguous_3digit"]:
                sample = ", ".join(f"L{ln}:{val}" for ln, val in rep["ambiguous_3digit"][:12])
                print(f"  [Số X.XXX cần duyệt tay (hàng nghìn vs 3 chữ số thập phân)] ({len(rep['ambiguous_3digit'])}): {sample}")
            if rep["raw_code"]:
                print(f"  [Tên biến code / tệp thô] ({len(rep['raw_code'])}):")
                for ln, tok, hint in rep["raw_code"][:15]:
                    print(f"    - Dòng {ln}: '{tok}' -> {hint}")
            if rep["backward_leaks"]:
                print(f"  [Nghi vấn rò rỉ kết quả ngược Chương 1/3] ({len(rep['backward_leaks'])}):")
                for ln, tok, hint in rep["backward_leaks"]:
                    print(f"    - Dòng {ln}: '{tok}' -> {hint}")
            if rep["mixed_terms"]:
                print(f"  [Thuật ngữ Anh-Việt lẫn lộn] ({len(rep['mixed_terms'])} vị trí, 10 mẫu đầu):")
                for ln, tok, hint in rep["mixed_terms"][:10]:
                    print(f"    - Dòng {ln}: '{tok}' -> {hint}")

    else:
        for path in tex_files:
            count, ambig = fix_decimals_in_file(path, force_3digit=args.force_3digit, dry_run=args.dry_run)
            prefix = "[DRY-RUN] " if args.dry_run else ""
            if count > 0 or ambig:
                print(f"{prefix}{path}: đã đổi {count} số thập phân '.' -> ','"
                      f" | giữ nguyên {len(ambig)} số X.XXX cần duyệt tay.")
                if ambig:
                    print("   -> Danh sách X.XXX giữ nguyên:", ", ".join(f"L{ln}:{v}" for ln, v in ambig[:15]))


if __name__ == "__main__":
    main()
