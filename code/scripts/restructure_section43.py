import re

with open('thesis/vi/main.tex', 'r', encoding='utf-8') as f:
    text = f.read()

# ---------------------------------------------------------------------------
# 1. Extract Table B.13 block from Appendix B
# ---------------------------------------------------------------------------
pos_lovo = text.rfind(r'\label{tab:multisource-lovo}')
start_lovo = text.rfind(r'\begin{table}', 0, pos_lovo)
end_lovo = text.find(r'\end{table}', pos_lovo) + len(r'\end{table}')
table_lovo_code = text[start_lovo:end_lovo]

# Check if there is an outer brace {\renewcommand{\arraystretch}{0.85} ... }
outer_start = text.rfind(r'{\renewcommand{\arraystretch}', 0, start_lovo)
if outer_start != -1 and start_lovo - outer_start < 50:
    outer_end = text.find(r'}', end_lovo)
    table_lovo_block = text[outer_start:outer_end+1]
else:
    table_lovo_block = table_lovo_code

print("Extracted Table B.13 block length:", len(table_lovo_block))

# ---------------------------------------------------------------------------
# 2. Extract Section 4.3 components
# ---------------------------------------------------------------------------
p_start = text.find(r'\section{Đánh giá các cơ chế thích ứng miền và khôi phục điểm vận hành (RQ5a, RQ5b)}')
p_end = text.find(r'\section{Chi phí xử lý thực nghiệm và các đe dọa tính hợp lệ}')
sub_text = text[p_start:p_end]

m1 = sub_text.find(r'\subsection{Đánh giá thực nghiệm Structural Transformer kết hợp MixStyle')
m2 = sub_text.find(r'\subsection[Khôi phục điểm vận hành qua hiệu chuẩn nền lành tính]')
m3 = sub_text.find(r'\subsection{Đánh giá học đa nguồn LOVO')
m4 = sub_text.find(r'\subsection[Triệt tiêu thông tin xe tuyến tính')

# Text segments
mixstyle_text = sub_text[m1:m2]
calibration_text = sub_text[m2:m3]
lovo_text = sub_text[m3:m4]
whitening_text = sub_text[m4:]

# ---------------------------------------------------------------------------
# 3. Clean up Calibration Text (Mục 4.3.1)
# ---------------------------------------------------------------------------
# Change subsection header to RQ5a
cal_header_old = r"\subsection[Khôi phục điểm vận hành qua hiệu chuẩn nền lành tính]{Khôi phục điểm vận hành qua hiệu chuẩn nền lành tính (Benign Warmup Calibration)}\label{sec:benign-calibration}"
cal_header_new = r"""\subsection{Khôi phục điểm vận hành qua hiệu chuẩn nền lành tính và đối chứng thuần đích (RQ5a)}\label{sec:benign-calibration}
Nhằm giải quyết sự trôi dạt phân phối điểm nền (\textit{threshold shift}) khiến tỷ lệ báo động giả vượt $52\%$ ở Điều kiện B khi sử dụng ngưỡng tĩnh đóng băng từ nguồn, Giai đoạn II áp dụng cơ chế hiệu chuẩn nền lành tính không giám sát ($K_{\text{valid}} = \min(K, \lfloor L_{\text{benign}}/2 \rfloor)$, $K \in \{200, 500, 1000\}$, $\alpha \in \{0{,}1\%, 1{,}0\%}$) kết hợp bộ lọc sự kiện trượt $m$-trong-$n$ (Mục~\ref{sec:method-calibration}). Cần lưu ý rằng biến thể \code{Structural + MixStyle} xuất hiện trong Bảng~\ref{tab:benign-calibration-summary} là nhánh điều chuẩn biểu diễn trong pha huấn luyện nguồn (đã đặc tả ở Chương~\ref{chap:method}), được đưa vào đối chứng song song tại đây để khảo sát tác động cộng hưởng với hiệu chuẩn ngưỡng; phân tích chi tiết về bản thân kỹ thuật MixStyle ở trạng thái chưa hiệu chuẩn được trình bày tại Mục~\ref{subsec:eval-mixstyle}."""

# Remove the defensive K=1000 sentence and replace intro
cal_old_intro = r"""Nhằm giải quyết sự trôi dạt phân phối điểm nền (\textit{threshold shift}) khiến FAR vượt $52\%$ ở Điều kiện B, nghiên cứu áp dụng cơ chế hiệu chuẩn nền lành tính không giám sát ($K_{\text{valid}} = \min(K, \lfloor \mathrm{prefix\_end}/2 \rfloor)$, $K \in \{200, 500, 1000\}$, $\alpha \in \{0{,}1\%, 1{,}0\%}$) kết hợp lọc sự kiện trượt $m$-trong-$n$ (Mục~\ref{subsec:method-calibration}). Kết quả đánh giá hậu khởi động được trình bày tại Hình~\ref{fig:calibration-recovery}, Bảng~\ref{tab:benign-calibration-summary} và Bảng~\ref{tab:cal-baselines-mofn}. Cần lưu ý rằng Hình~\ref{fig:calibration-recovery}(c)--(d) trực quan hóa điểm F1 theo từng loại tấn công ở điều kiện B và D tại thiết lập $K=1000, \alpha=1{,}0\%$ nhằm minh họa tính hội tụ khi điều kiện mẫu đuôi $K\alpha \ge 1$ được thỏa mãn hoàn toàn; trong khi đó, phần bình luận và các khuyến nghị vận hành thực tế của khóa luận tập trung vào chế độ ngặt hơn với ngân sách khởi động $K=500$ (đối chiếu chi tiết tại Bảng~\ref{tab:benign-calibration-summary})."""

cal_new_intro = r"""Kết quả đánh giá hậu khởi động được trình bày tại Hình~\ref{fig:calibration-recovery}, Bảng~\ref{tab:benign-calibration-summary} và Bảng~\ref{tab:cal-baselines-mofn}."""

cal_caption_old = r"\caption[Đánh giá khôi phục điểm vận hành qua hiệu chuẩn nền lành tính xe đích]{Đánh giá khôi phục điểm vận hành qua hiệu chuẩn nền lành tính xe đích: (a)--(b) Đường cong Recall theo ngân sách FAR thực nghiệm tại $K=500$; (c)--(d) Điểm F1 theo từng loại tấn công ở điều kiện B và D vẽ tại $K=1000$, ngân sách FAR $1{,}0\%$ (bổ sung bảng đối chiếu chi tiết tại $K \in \{200, 500, 1000\}$ ở Bảng~\ref{tab:benign-calibration-summary}).}\label{fig:calibration-recovery}"
cal_caption_new = r"\caption[Đánh giá khôi phục điểm vận hành qua hiệu chuẩn nền lành tính xe đích]{Đánh giá khôi phục điểm vận hành qua hiệu chuẩn nền lành tính xe đích: (a)--(b) Đường cong Recall theo ngân sách FAR thực nghiệm tại $K=500$; (c)--(d) Điểm F1 theo từng loại tấn công ở điều kiện B và D tại ngân sách khởi động $K=500, \alpha=1{,}0\%$ (đối chiếu chi tiết tại Bảng~\ref{tab:benign-calibration-summary}).}\label{fig:calibration-recovery}"

cleaned_cal_text = calibration_text.replace(cal_header_old, cal_header_new)
if cal_old_intro in cleaned_cal_text:
    cleaned_cal_text = cleaned_cal_text.replace(cal_old_intro, cal_new_intro)
cleaned_cal_text = cleaned_cal_text.replace(cal_caption_old, cal_caption_new)
# Replace prefix_end with L_benign
cleaned_cal_text = cleaned_cal_text.replace(r"\mathrm{prefix\_end}", r"L_{\text{benign}}")
cleaned_cal_text = cleaned_cal_text.replace(r"prefix\_end", r"$L_{\text{benign}}$")

# ---------------------------------------------------------------------------
# 4. Clean up MixStyle Text (Mục 4.3.2.1)
# ---------------------------------------------------------------------------
mix_header_old = r"\subsection{Đánh giá thực nghiệm Structural Transformer kết hợp MixStyle (RQ5b)}\label{sec:mixstyle-study}"
mix_header_new = r"\subsubsection{Điều chuẩn phân phối ẩn bằng MixStyle}\label{subsec:eval-mixstyle}"
cleaned_mix_text = mixstyle_text.replace(mix_header_old, mix_header_new)
cleaned_mix_text = cleaned_mix_text.replace(r"và~\ref{tab:mixstyle-runtime}, Mục~\ref{subsec:app-mixstyle}", r"Mục~\ref{subsec:app-mixstyle}")
cleaned_mix_text = cleaned_mix_text.replace(r"và~\ref{tab:mixstyle-runtime}), MixStyle", r"), MixStyle")

# ---------------------------------------------------------------------------
# 5. Clean up LOVO Text (Mục 4.3.2.2) and embed Table B.13
# ---------------------------------------------------------------------------
lovo_header_old = r"\subsection{Đánh giá học đa nguồn LOVO với bộ phân loại đối kháng có điều kiện (RQ5b)}\label{sec:multisource-lovo}"
lovo_header_new = r"\subsubsection{Học đa nguồn LOVO kết hợp đối kháng có điều kiện}\label{subsec:eval-lovo}"
cleaned_lovo_text = lovo_text.replace(lovo_header_old, lovo_header_new)
cleaned_lovo_text = cleaned_lovo_text.replace(r"Bảng~\ref{tab:multisource-lovo} (Phụ lục~\ref{app:sensitivity}) và Hình~\ref{fig:multisource-lovo}", r"Bảng~\ref{tab:multisource-lovo} và Hình~\ref{fig:multisource-lovo}")
cleaned_lovo_text = cleaned_lovo_text.replace(r"(Bảng~\ref{tab:multisource-lovo}, Phụ lục~\ref{app:sensitivity})", r"(Bảng~\ref{tab:multisource-lovo})")

# Insert Table B.13 right after Figure 4.3 in LOVO
fig_lovo_end = cleaned_lovo_text.find(r"\end{figure}") + len(r"\end{figure}")
cleaned_lovo_text = (
    cleaned_lovo_text[:fig_lovo_end]
    + "\n\n"
    + table_lovo_block
    + "\n\n"
    + cleaned_lovo_text[fig_lovo_end:]
)

# ---------------------------------------------------------------------------
# 6. Clean up Whitening Text (Mục 4.3.2.3)
# ---------------------------------------------------------------------------
white_header_old = r"\subsection[Triệt tiêu thông tin xe tuyến tính và điểm năng lượng]{Triệt tiêu thông tin xe tuyến tính (LEACE/INLP8) và điểm năng lượng (RQ5b)}\label{sec:benign-invariant}"
white_header_new = r"\subsubsection{Làm trắng nền lành tính, triệt tiêu tuyến tính LEACE/INLP8 và điểm năng lượng Mahalanobis}\label{subsec:eval-whitening}"
cleaned_white_text = whitening_text.replace(white_header_old, white_header_new)

# ---------------------------------------------------------------------------
# 7. Assemble New Section 4.3
# ---------------------------------------------------------------------------
sec43_new_intro = r"""\section{Đánh giá các cơ chế thích ứng miền và khôi phục điểm vận hành (RQ5a, RQ5b)}\label{sec:adaptation-eval}
Phần này đánh giá có hệ thống các giải pháp nhằm khắc phục sự sụp đổ của ngưỡng tĩnh và kiểm định giới hạn của tính bất biến biểu diễn xuyên phương tiện: khởi đầu với cơ chế đề xuất cốt lõi ở \textbf{Giai đoạn II} (hiệu chuẩn ngưỡng vận hành trên tiền tố lành tính không giám sát và lọc sự kiện trượt, trả lời \textbf{RQ5a} tại Mục~\ref{sec:benign-calibration}); tiếp theo là \textbf{nhánh chẩn đoán và đối chứng bất biến miền} (gồm điều chuẩn MixStyle, học đa nguồn đối kháng LOVO-cAdv, làm trắng nền lành tính và triệt tiêu tuyến tính LEACE/INLP8, trả lời \textbf{RQ5b} tại Mục~\ref{sec:feature-invariance}).

"""

sec432_header = r"""
\subsection{Đánh giá các cơ chế thích ứng và triệt tiêu cấp đặc trưng (RQ5b)}\label{sec:feature-invariance}
Phần này đánh giá các phương pháp tiếp cận hướng tới việc triệt tiêu sự khác biệt phân phối trực tiếp trong không gian biểu diễn ẩn $z_k \in \mathbb{R}^{64}$ thay vì chỉ can thiệp ngưỡng phân loại ở đầu ra.

"""

new_sec43 = (
    sec43_new_intro
    + cleaned_cal_text.strip()
    + "\n\n"
    + sec432_header
    + cleaned_mix_text.strip()
    + "\n\n"
    + cleaned_lovo_text.strip()
    + "\n\n"
    + cleaned_white_text.strip()
    + "\n\n"
)

# Replace Section 4.3 in main text
text = text[:p_start] + new_sec43 + text[p_end:]
print("Section 4.3 successfully restructured!")

# ---------------------------------------------------------------------------
# 8. Clean up Appendix B: Remove Table B.13, Table B.12, Table B.16
# ---------------------------------------------------------------------------
# Remove Table B.13 from Appendix B.5
app_lovo_old = r"""\section{Kết quả mở rộng của học đa nguồn LOVO và bất biến biểu diễn}\label{sec:app-lovo}
Bảng~\ref{tab:multisource-lovo} tổng hợp chi tiết kết quả 48 lượt huấn luyện học đa nguồn giữ ngoài một xe (LOVO) kèm nhánh phân loại đối kháng có điều kiện (\code{cAdv}) qua bốn tập đối chuẩn can-train-and-test tại ngưỡng validation từ ba xe nguồn."""

app_lovo_new = r"""\section{Kết quả mở rộng của học đa nguồn LOVO và bất biến biểu diễn}\label{sec:app-lovo}
Kết quả chi tiết 48 lượt huấn luyện của học đa nguồn LOVO và thăm dò phân loại xe/tấn công đã được đưa lên trình bày trực tiếp tại Bảng~\ref{tab:multisource-lovo} (Chương~\ref{chap:results}, Mục~\ref{subsec:eval-lovo}). Phần này lưu giữ các ghi chú bổ trợ về tính ổn định của các nhánh đối kháng qua từng hạt giống ngẫu nhiên."""

if app_lovo_old in text:
    text = text.replace(app_lovo_old, app_lovo_new)
    # Remove the table block if still in Appendix B
    if table_lovo_block in text:
        text = text.replace(table_lovo_block, "")
        print("Table B.13 moved from Appendix B to Chapter 4!")

# Remove Table B.12 and its text from Appendix B.4
pos_b12 = text.rfind(r'\label{tab:mixstyle-runtime}')
if pos_b12 != -1:
    start_b12 = text.rfind(r'\begin{longtable}', 0, pos_b12)
    end_b12 = text.find(r'\end{longtable}', pos_b12) + len(r'\end{longtable}')
    # Also find the discussion paragraph after B.12
    disc_start = end_b12
    disc_end = text.find(r'\section{Kết quả mở rộng của học đa nguồn LOVO', disc_start)
    old_b12_section = text[start_b12:disc_end]
    new_b12_section = r"""Do MixStyle chuyển về phép đồng nhất (identity) khi suy luận, chi phí suy luận của \code{Structural + MixStyle} hoàn toàn tương đương \code{Structural}. Chi phí phân rã ba thành phần trên CPU/GPU đã được trình bày tại Bảng~\ref{tab:runtime-decomp} (Chương~\ref{chap:results}, Mục~\ref{sec:runtime}).

"""
    text = text[:start_b12] + new_b12_section + text[disc_end:]
    print("Table B.12 removed from Appendix B.4!")

# Remove Table B.16 from Appendix B.7
pos_b16 = text.rfind(r'\label{tab:extension-runtime}')
if pos_b16 != -1:
    start_b16 = text.rfind(r'\section{Kiểm toán thời gian xử lý tổng hợp và độ phức tạp tĩnh}', 0, pos_b16)
    end_b16 = text.find(r'\end{longtable}', pos_b16) + len(r'\end{longtable}')
    new_b16_section = r"""\section{Kiểm toán độ phức tạp kiến trúc, FLOPs và bộ nhớ trạng thái}\label{subsec:complexity-audit}"""
    text = text[:start_b16] + new_b16_section + text[end_b16:]
    print("Table B.16 removed from Appendix B.7!")

# Update Section 4.4.1 (sec:runtime) text
runtime_ref_old = r"""hai bảng đo tổng hợp gộp I/O--trích xuất kép (Bảng~\ref{tab:extension-runtime} $6{,}176\text{ ms}$ và Bảng~\ref{tab:mixstyle-runtime} $4{,}001\text{ ms}$) được lưu tại Mục~\ref{subsec:app-runtime-audit}, Phụ lục~\ref{app:sensitivity}"""
runtime_ref_new = r"""Do MixStyle chuyển về phép đồng nhất (identity) khi suy luận, chi phí suy luận của \code{Structural + MixStyle} hoàn toàn tương đương \code{Structural}. Chi tiết phân rã ba thành phần được tổng hợp tại Bảng~\ref{tab:runtime-decomp} và kiểm toán độ phức tạp tĩnh tại Bảng~\ref{tab:model-complexity-audit} (Phụ lục~\ref{app:sensitivity})"""

text = text.replace(runtime_ref_old, runtime_ref_new)

# Update Appendix B opening sentence to "14 bảng"
text = text.replace(r"Phụ lục này lưu trữ đầy đủ 17 bảng", r"Phụ lục này lưu trữ đầy đủ 14 bảng")
text = text.replace(r"17 bảng kiểm toán độ nhạy", r"14 bảng kiểm toán độ nhạy")

# ---------------------------------------------------------------------------
# 9. Refactor Section 4.4.2: Threats to validity
# ---------------------------------------------------------------------------
p_validity_start = text.find(r'\subsection{Đe dọa tính hợp lệ}\label{sec:threats-to-validity}')
p_validity_end = text.find(r'\section{Tóm tắt chương}', p_validity_start)

threats_new = r"""\subsection{Đe dọa tính hợp lệ}\label{sec:threats-to-validity}
Khóa luận nhận diện năm nhóm đe dọa tính hợp lệ cần được xem xét khi diễn giải kết quả:
\begin{enumerate}
    \item \textbf{Hiệu lực kết cấu và thiết kế đối chuẩn đa phương tiện:}
    \begin{itemize}
        \item \textit{Đa dạng nền tảng vật lý:} Bộ đối chuẩn CTT chỉ gồm 4 dòng xe vật lý với 3 xe đích phân biệt (Subaru Forester xuất hiện lặp ở cả Tập 2 và Tập 3), và các vòng ghi chưa có siêu dữ liệu chuyến lái độc lập hoàn toàn.
        \item \textit{Sai lệch gộp và mức độ giám sát:} Nhãn nhị phân cấp cửa sổ $W=64$ không đo lường định vị khung tin hay độ trễ tiền sự cố; các mô hình baseline cấp khung tin (\code{CANLP}, \code{CANBERT+}) chịu bất lợi quy nạp lớn khi đối chuẩn dưới cùng một ngưỡng FAR cố định so với pooling trung bình.
        \item \textit{Phạm vi kiểm thử ngoại bộ:} Đánh giá trên 57 bản ghi ngoại bộ sử dụng mô hình neo huấn luyện từ Tập 1 (xe nguồn Chevrolet Impala), chưa bao quát toàn bộ 4 tập huấn luyện nguồn.
    \end{itemize}

    \item \textbf{Độ ổn định vùng đuôi và tính dừng của luồng dữ liệu:}
    \begin{itemize}
        \item \textit{Dịch chuyển tiên nghiệm lớp:} Việc lấy mẫu reservoir áp trần $1.000$ cửa sổ/lớp tạo tỷ lệ lớp nhân tạo cân bằng ($50:50$), lệch xa phân bố tấn công thực tế ($0{,}03\%\text{--}8\%$), thúc đẩy hiện tượng bão hòa logit và trôi dạt ngưỡng.
        \item \textit{Kích thước mẫu khởi động đơn chuyến:} Tại ngân sách khắt khe $\alpha=0{,}1\%$, một chuyến đi đơn lẻ với $K=500$ cửa sổ ($K\alpha = 0{,}5 < 1$) nhạy cảm với phương sai đuôi; phân vị chỉ ổn định vững chắc khi gộp đa phiên ($N_{\text{pool}} \ge 3.539$) hoặc vận hành ở $\alpha \ge 0{,}5\%$.
        \item \textit{Tự tương quan chuỗi:} Luồng dữ liệu CAN thực tế có tính tự tương quan thời gian mạnh và tính phi dừng giữa các chuyến lái, do đó các chặn phân vị IID không cấu thành cam kết phân phối tự do trong mọi điều kiện vận hành.
    \end{itemize}

    \item \textbf{Giới hạn của phép thăm dò tuyến tính:}
    \begin{itemize}
        \item \textit{Cảnh báo hội tụ tối ưu:} Phép thăm dò tuyến tính ghi nhận cảnh báo hội tụ ở một số ô tham số (98/576 ô ở LOVO, 133 ô ở làm trắng) do đặc tính phân tách gần như hoàn hảo của không gian đặc trưng.
        \item \textit{Tồn dư phi tuyến:} Việc triệt tiêu thông tin xe trên bộ thăm dò tuyến tính hoặc trên điểm rủi ro 1 chiều không đồng nghĩa với tính bất biến toàn diện, khi bộ giải mã MLP phi tuyến vẫn trích xuất được $42{,}01\%\text{--}57{,}17\%$ nhãn xe.
    \end{itemize}

    \item \textbf{Tính hậu nghiệm và tính toàn vẹn thời gian:}
    \begin{itemize}
        \item \textit{Bản chất phân tích chẩn đoán:} Các phân tích MixStyle, LOVO và làm trắng hiệp phương sai được thiết kế theo hướng chẩn đoán hậu nghiệm sau khi quan sát hiện tượng phân kỳ ở 4 tập đối chuẩn.
        \item \textit{Xáo trộn dấu thời gian:} Hiện tượng đảo ngược dấu thời gian dưới mili-giây trên CTT buộc mô hình chính phải vận hành ở chế độ thuần nội dung, chưa thay thế hoàn toàn đánh giá trên luồng bus vật lý thời gian thực.
    \end{itemize}

    \item \textbf{Khoảng cách triển khai trên vi điều khiển nhúng:}
    \begin{itemize}
        \item \textit{Độ trễ gom cửa sổ:} Mặc dù thời gian suy luận thuần trên CPU chỉ tốn $0{,}731\text{ ms}$, việc gom đủ $W=64$ khung tin trên đường truyền 500~kbps đòi hỏi độ trễ tích lũy vật lý $32\text{--}64\text{ ms}$.
        \item \textit{Ràng buộc phần cứng thực tế:} Các phép đo lường trên máy trạm chưa phản ánh đầy đủ xung đột hàng đợi bus, tranh chấp bộ nhớ hay hạn chế ngắt thời gian thực trên vi điều khiển chuyên dụng của ô tô.
    \end{itemize}
\end{enumerate}

"""

text = text[:p_validity_start] + threats_new + text[p_validity_end:]
print("Section 4.4.2 refactored successfully!")

with open('thesis/vi/main.tex', 'w', encoding='utf-8') as f:
    f.write(text)

print("All restructurings applied to thesis/vi/main.tex!")
