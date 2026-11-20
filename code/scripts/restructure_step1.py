import re

with open('thesis/vi/main.tex', 'r', encoding='utf-8') as f:
    text = f.read()

# ---------------------------------------------------------------------------
# 1. Opening of Chapter 4: Add RQ mapping box
# ---------------------------------------------------------------------------
ch4_old_intro = r"""\chapter{Thực nghiệm và đánh giá}\label{chap:results}
Chương này phân biệt phép so chính đã định nghĩa tiêu chí với phân tích bổ sung hậu nghiệm. Mọi số tổng hợp dùng trung bình seed trong set rồi trọng số ngang nhau giữa các set; không xem số cửa sổ là số xe độc lập. Dấu -- là không xác định, không phải số không. Bố cục chương được tổ chức theo bốn phần: Mục 4.1 xác lập thiết lập và giao thức thực nghiệm; Mục 4.2 đánh giá chuyển giao zero-shot và chẩn đoán biểu diễn cấu trúc tương ứng RQ1--RQ4; Mục 4.3 đánh giá các cơ chế thích ứng miền và khôi phục điểm vận hành; và Mục 4.4 phân tích chi phí xử lý cùng các đe dọa tính hợp lệ."""

ch4_new_intro = r"""\chapter{Thực nghiệm và đánh giá}\label{chap:results}
Chương này triển khai hệ thống thực nghiệm đối chứng đa phương tiện diện rộng nhằm kiểm chứng thực nghiệm các giả thuyết khoa học và trả lời trọn vẹn năm câu hỏi nghiên cứu (RQ1--RQ5) đã xác lập ở phần Mở đầu. Bố cục chương và bản đồ ánh xạ câu hỏi nghiên cứu được tổ chức như sau:
\begin{itemize}
    \item \textbf{Mục~\ref{sec:comparison-protocol} (Thiết lập và giao thức thực nghiệm):} Trình bày quy tắc chia tách dữ liệu, lấy mẫu reservoir, cấu hình siêu tham số và hệ thống độ đo kiểm định.
    \item \textbf{Mục~\ref{sec:zeroshot-eval} (Đánh giá chuyển giao zero-shot và chẩn đoán biểu diễn):}
    \begin{itemize}
        \item \textit{Mục~\ref{subsec:eval-perf-far} \&~\ref{subsec:monotonic-timed}:} Trả lời \textbf{RQ1} về hiệu năng chuyển giao phương tiện và sự phân kỳ giữa chất lượng xếp hạng độc lập ngưỡng (AP) với độ nhạy tại ngưỡng tĩnh, cùng vai trò của động học thời gian.
        \item \textit{Mục~\ref{subsec:eval-ablation}:} Trả lời \textbf{RQ2} về đóng góp của từng nhóm thành phần đặc trưng (cú pháp, vi sai $\Delta\text{payload}$, thống kê cục bộ) và độ nhạy kích thước cửa sổ $W$.
        \item \textit{Mục~\ref{subsec:eval-probing}:} Trả lời \textbf{RQ3} về hiện tượng đan xen đặc trưng và giới hạn của tính bất biến biểu diễn thông qua thăm dò tuyến tính có kiểm soát.
        \item \textit{Mục~\ref{subsec:eval-external}:} Trả lời \textbf{RQ4} về năng lực tổng quát hóa ngoại bộ trên ba bộ dữ liệu độc lập và ranh giới thất bại thực tế.
    \end{itemize}
    \item \textbf{Mục~\ref{sec:adaptation-eval} (Đánh giá các cơ chế thích ứng miền và khôi phục điểm vận hành):}
    \begin{itemize}
        \item \textit{Mục~\ref{sec:benign-calibration}:} Trả lời \textbf{RQ5a} về khôi phục điểm vận hành qua hiệu chuẩn tiền tố lành tính không giám sát ($K=500$, lọc trượt $m$-trong-$n$) và lợi thế tham số so với mô hình thuần đích.
        \item \textit{Mục~\ref{sec:feature-invariance}:} Trả lời \textbf{RQ5b} về giới hạn của các kỹ thuật thích ứng và triệt tiêu cấp đặc trưng (MixStyle, LOVO-cAdv, làm trắng nền lành tính và LEACE/INLP8).
    \end{itemize}
    \item \textbf{Mục~\ref{sec:runtime} \&~\ref{sec:threats-to-validity}:} Phân tích chi phí tính toán, độ trễ thời gian thực và thảo luận các mối đe dọa tính hợp lệ.
\end{itemize}"""

if ch4_old_intro in text:
    text = text.replace(ch4_old_intro, ch4_new_intro)
    print("1. Ch4 intro replaced successfully!")
else:
    print("Warning: ch4_old_intro not matched exactly!")

# ---------------------------------------------------------------------------
# 2. Section 4.1.1: Add dataset split & filtering rules from Table 1.3
# ---------------------------------------------------------------------------
target_411 = r"Các tệp nguồn được gom theo hậu tố vòng ghi (nhóm hậu tố lớn nhất làm validation; không tái huấn luyện trên tập validation sau khi chốt ngưỡng)."
replace_411 = r"""Về quy tắc chia tách và lọc tệp trên các bộ dữ liệu nghiên cứu: đối với \textit{can-train-and-test}, tập validation nguồn được tách theo hậu tố vòng ghi độc lập, tuyệt đối không can thiệp vào tập kiểm thử chính thức; đối với \textit{Automotive v2}, nhãn tấn công DoS được xác định nghiêm ngặt theo khoảng cách thời gian và chữ ký khung tin thay vì gán nhãn thô toàn bộ tệp; đối với \textit{CAN-MIRGU}, toàn bộ khung tin được đồng bộ nhãn từ nhật ký tấn công và kiểm tra tính toàn vẹn; đối với \textit{CICIoV2024}, thực nghiệm tuân thủ giao thức thứ tự hàng trong tệp CSV do không có dấu thời gian đo lường; và bộ dữ liệu \textit{OTIDS} chưa đưa vào kết luận chính thức do cần xác minh tính nhất quán nhãn sau chuyển đổi. Các tệp nguồn được gom theo hậu tố vòng ghi (nhóm hậu tố lớn nhất làm validation; không tái huấn luyện trên tập validation sau khi chốt ngưỡng)."""

if target_411 in text:
    text = text.replace(target_411, replace_411)
    print("2. Section 4.1.1 dataset filtering rules added!")
else:
    print("Warning: target_411 not found!")

with open('thesis/vi/main.tex', 'w', encoding='utf-8') as f:
    f.write(text)
