import re

with open('thesis/vi/main.tex', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. ctt-content-order-comparison-v1
text = text.replace(
    r"\textbf{Giao thức chuẩn hóa theo thứ tự nội dung (\code{ctt-content-order-comparison-v1}):}",
    r"\textbf{Giao thức chuẩn hóa theo thứ tự nội dung bản ghi (đối sánh thuần nội dung):}"
)

# 2. File paths in 4.2.2 (bd-per-file-counts)
old_files_text = r"(\code{set\_04/D/force-neutral-2.csv}, 0/7.096) và $0{,}03\%$ (\code{set\_04/B/speed-1.csv}, 14/40.932) tới $97{,}81\%$ (\code{set\_04/B/interval-1.csv}, 9.692/9.909) và $96{,}92\%\text{--}97{,}22\%$ ở \code{set\_03/D}."
new_files_text = r"(bản ghi \textit{force-neutral} thuộc Tập~4, Điều kiện~D, 0/7.096) và $0{,}03\%$ (bản ghi \textit{speed} thuộc Tập~4, Điều kiện~B, 14/40.932) tới $97{,}81\%$ (bản ghi \textit{interval} thuộc Tập~4, Điều kiện~B, 9.692/9.909) và $96{,}92\%\text{--}97{,}22\%$ ở Tập~3, Điều kiện~D."
text = text.replace(old_files_text, new_files_text)

# 3. hexadecimal_benign.csv
text = text.replace(
    r"(\text{FAR}=100\% trên tệp lành \code{hexadecimal_benign.csv}):",
    r"(\text{FAR}=100\% trên bản ghi lành tính của CICIoV2024):"
)

# 4. accessory-2.csv
text = text.replace(
    r"(\code{batch=1}, 20 warmup + 900 cửa sổ \code{accessory-2.csv});",
    r"(\code{batch=1}, 20 cửa sổ tiền tố + 900 cửa sổ kiểm chuẩn độ trễ);"
)

# 5. External dataset names without underscores in prose
text = text.replace(r"Opel\_Astra\_DoS", r"Opel Astra (DoS)")
text = text.replace(r"Opel\_Astra\_benign", r"Opel Astra (lành tính)")
text = text.replace(r"Renault\_Clio\_DoS", r"Renault Clio (DoS)")
text = text.replace(r"Renault\_Clio\_benign", r"Renault Clio (lành tính)")
text = text.replace(r"CAN\_MIRGU\_attack", r"CAN-MIRGU (tấn công)")
text = text.replace(r"CAN\_MIRGU\_benign", r"CAN-MIRGU (lành tính)")

# 6. white_energy and content_disjoint in prose
text = text.replace(r"điểm năng lượng \code{white\_energy}", r"điểm năng lượng Mahalanobis $E_{\text{white}}$")
text = text.replace(r"\code{white\_energy}", r"$E_{\text{white}}$")
text = text.replace(r"\code{content\_disjoint}", r"lọc trùng mã băm SHA-256")

with open('thesis/vi/main.tex', 'w', encoding='utf-8') as f:
    f.write(text)

print("Raw code strings successfully cleaned up in thesis/vi/main.tex!")
