import re

new_chap3_part = r"""{\renewcommand{\arraystretch}{0.9}
\begin{table}[htbp]\centering\footnotesize\setlength{\tabcolsep}{4.5pt}
\caption[Phân loại có hệ thống các cơ chế thích ứng miền và đối chứng bất biến]{Phân loại có hệ thống các cơ chế thích ứng miền và đối chứng bất biến}\label{tab:adaptation-taxonomy}
\begin{tabular}{P{2.6cm}P{2.8cm}P{1.8cm}P{2.4cm}P{1.8cm}P{3.2cm}}
\toprule
Nhóm vai trò & Cơ chế & Dữ liệu nguồn & Ngân sách xe đích & Trọng số mô hình & Nguyên lý cốt lõi\\\midrule
\textbf{Giai đoạn II (Hệ thống chính)} & Hiệu chuẩn tiền tố lành tính \& lọc $m$-trong-$n$ & Đơn nguồn (1 xe) & Tiền tố lành tính không nhãn ($K$ cửa sổ/bản ghi) & Đóng băng hoàn toàn & Ước lượng phân vị ngoại mẫu 1 chiều $\tau_{\text{target}}$ kết hợp lọc sự kiện trượt $m$-trong-$n$\\
\midrule
\textbf{Nhánh chẩn đoán \& đối chứng bất biến} & Điều chuẩn trộn phong cách (MixStyle) & Đơn nguồn (1 xe) & $0$ mẫu đích & Cập nhật khi học & Trộn thống kê $(\mu, \sigma)$ giữa các mẫu cùng nhãn trong từng lô huấn luyện\\
\textbf{Nhánh chẩn đoán \& đối chứng bất biến} & Học đa nguồn đối kháng có điều kiện (LOVO-cAdv) & Đa nguồn (3 xe) & $0$ mẫu đích & Cập nhật đối kháng & Bộ phân biệt miền định tuyến cứng theo nhãn lớp $Y$ kết hợp tầng đảo ngược gradient (GRL)\\
\textbf{Nhánh chẩn đoán \& đối chứng bất biến} & Làm trắng nền lành tính, LEACE/INLP8 \& $E_{\text{white}}$ & Đa nguồn (3 xe) & Tiền tố lành tính đối chứng & Đóng băng (hậu xử lý) & Làm trắng hiệp phương sai nền, triệt tiêu không gian con nhận diện xe và đo năng lượng Mahalanobis\\
\bottomrule\end{tabular}
\end{table}}

\section{Giai đoạn II: Hiệu chuẩn ngưỡng vận hành trên tiền tố lành tính và lọc sự kiện trượt}\label{sec:method-calibration}
Dưới tác động của dịch chuyển hiệp phương sai và dịch chuyển điểm số giữa các dòng xe (Mục~\ref{subsec:domain-shifts}), ngưỡng quyết định đóng băng từ nguồn $\tau_{\text{src}}$ thường bị lệch nghiêm trọng so với phân phối nền lành tính của phương tiện mới. Thay vì tinh chỉnh trọng số mạng nơ-ron --- vốn đòi hỏi dữ liệu tấn công có nhãn trên xe đích và tiềm ẩn nguy cơ quên tri thức nguồn --- Giai đoạn II giữ đóng băng hoàn toàn bộ mã hóa Transformer $f_\theta$ và chỉ thích ứng duy nhất một ngưỡng phân loại vô hướng $\tau_{\text{target}}$ dựa trên một đoạn tiền tố lưu lượng lành tính không nhãn thu thập trên xe đích.

\paragraph{Giao thức xác định tiền tố hợp lệ không rò rỉ:} Gọi $L_{\text{benign}}^{(j)}$ là số cửa sổ lành tính liên tiếp ở đầu bản ghi thứ $j$ trước khi xuất hiện cửa sổ tấn công đầu tiên. Với ngân sách khởi động trần $K \in \{200, 500, 1000\}$ cửa sổ mỗi bản ghi, độ dài tiền tố hợp lệ dùng cho hiệu chuẩn ngoại tuyến được chặn trên bởi:
\begin{equation}
K_{\text{valid}}^{(j)} = \min\left(K, \left\lfloor \frac{L_{\text{benign}}^{(j)}}{2} \right\rfloor\right).
\end{equation}
Ràng buộc $\lfloor L_{\text{benign}}^{(j)} / 2 \rfloor$ đóng vai trò chốt an toàn chống rò rỉ nhãn trong đánh giá ngoại tuyến, bảo đảm đoạn hiệu chuẩn hoàn toàn sạch tấn công đồng thời giữ lại ít nhất một nửa tiền tố lành tính cho tập kiểm thử hậu khởi động. Khi triển khai vật lý trên phương tiện thực tế, $K$ cửa sổ khởi động được thu thập trực tiếp trong pha bật khóa điện / nổ máy tĩnh trước khi xe vận hành.

\paragraph{Ước lượng phân vị gộp đa bản ghi:} Cho tập hợp $J$ bản ghi của cùng một phương tiện đích, hệ thống trích xuất tuần tự các điểm rủi ro vô hướng $s(X_k^{(j)}) = \operatorname{softmax}(f_\theta(X_k^{(j)}))_1$ trên toàn bộ các cửa sổ tiền tố $k \in \{0, \dots, K_{\text{valid}}^{(j)} - 1\}$ và gộp thành đa tập nền $\mathcal{S}_{\text{warm}}$ có tổng kích thước $N_{\text{pool}} = \sum_{j=1}^{J} K_{\text{valid}}^{(j)}$. Tại ngân sách báo động giả danh định $\alpha \in \{0{,}1\%, 0{,}5\%, 1{,}0\%, 2{,}0\%\}$, ngưỡng vận hành trên xe đích được xác định bằng phân vị thực nghiệm:
\begin{equation}
\tau_{\text{target}} = \operatorname{Quantile}_{1-\alpha}(\mathcal{S}_{\text{warm}}).
\end{equation}
Theo phân tích sai số phân vị mẫu hữu hạn (Mục~\ref{subsec:theory-probing-dkw}), để phân vị đuôi tại mức $\alpha$ có ý nghĩa thống kê và không suy biến về giá trị cực đại, cỡ mẫu nền cần thỏa mãn điều kiện $N_{\text{pool}}\alpha \ge 1$. Cơ chế gộp đa phiên giúp thỏa mãn chặt chẽ điều kiện này ngay cả ở ngân sách khắt khe $\alpha = 0{,}1\%$; trong trường hợp triển khai trên một chuyến đi đơn lẻ chỉ có $K = 500$ cửa sổ ($K\alpha = 0{,}5 < 1$ tại $\alpha = 0{,}1\%$), hệ thống cần tích lũy nền qua nhiều chu kỳ khởi động hoặc vận hành ở ngân sách $\alpha \ge 0{,}5\%$ kết hợp bộ lọc sự kiện.

\paragraph{Bộ lọc sự kiện trượt $m$-trong-$n$:} Nhằm triệt tiêu các xung nhiễu báo động giả đơn lẻ trên đường truyền tốc độ cao (1.000--2.000 khung tin/giây), các quyết định nhị phân hậu khởi động ($k \ge K_{\text{valid}}^{(j)}$) đi qua bộ lọc trượt nhân quả:
\begin{equation}\label{eq:mofn-filter}
\hat{Y}_k^{(m/n)} = \mathbf{1}\!\left[\sum_{r = \max(K_{\text{valid}}^{(j)},\, k - n + 1)}^{k} \mathbf{1}\!\left[s(X_r) \ge \tau_{\text{target}}\right] \ge m\right],
\end{equation}
trong đó cảnh báo chính thức chỉ kích hoạt khi có ít nhất $m$ trong tối đa $n$ cửa sổ liên tiếp vượt ngưỡng ($m/n \in \{2/3, 3/5\}$). Về chi phí trực tuyến, bước hiệu chuẩn phân vị chỉ tốn $\mathcal{O}(N_{\text{pool}} \log N_{\text{pool}})$ một lần sau pha khởi động, còn bộ lọc trượt chỉ yêu cầu một bộ đệm vòng kích thước $n$. Toàn bộ quy trình được đặc tả hình thức trong Thuật toán~\ref{alg:benign-cal-mofn}.

\begin{algorithm}[htbp]
\caption{Hiệu chuẩn nền lành tính gộp đa bản ghi ($N_{\text{pool}}$) kết hợp bộ lọc sự kiện trượt $m$-trong-$n$}\label{alg:benign-cal-mofn}
{\small\linespread{1.05}\selectfont
\begin{algorithmic}[1]
\Require Bộ phân loại nguồn đóng băng $f_\theta$; tập hợp $J$ bản ghi của xe đích $\{\mathcal{C}^{(j)}\}_{j=1}^J$ với số cửa sổ lành tính đầu bản ghi $L_{\text{benign}}^{(j)}$; ngân sách khởi động trần mỗi bản ghi $K \in \{200, 500, 1000\}$; ngân sách báo động giả mục tiêu $\alpha \in \{0{,}1\%, 0{,}5\%, 1{,}0\%, 2{,}0\%\}$; tham số lọc trượt $(m, n)$ (mặc định $2/3, 3/5$).
\Ensure Ngưỡng vận hành xe đích $\tau_{\text{target}}$ và chuỗi cảnh báo sự kiện sau khởi động $\{\widehat{Y}_{k, (j)}^{(m/n)}\}$ cho từng bản ghi $j \in \{1, \ldots, J\}$.
\State \textbf{Giai đoạn 1 --- Thu thập điểm nền lành tính gộp đa bản ghi ($N_{\text{pool}}$):}
\State $\mathcal{S}_{\text{warm}} \leftarrow [\,]$ \Comment{Đa tập (multiset) tích lũy điểm số nền lành}
\For{$j = 1$ \textbf{to} $J$}
    \State $K_{\text{valid}}^{(j)} \leftarrow \min\big(K,\, \lfloor L_{\text{benign}}^{(j)} / 2 \rfloor\big)$ \Comment{Ngân sách tiền tố hợp lệ bảo đảm an toàn nhãn}
    \State Khởi tạo trạng thái lịch sử $H_0 \leftarrow \emptyset$ cho bản ghi $j$
    \For{$k = 0$ \textbf{to} $K_{\text{valid}}^{(j)} - 1$}
        \State $X_k^{(j)}, H_{k+1} \leftarrow \Phi(\mathcal{W}_k^{(j)}; H_k)$ \Comment{Trích xuất cấu trúc theo Thuật toán~\ref{alg:causal-30d}}
        \State $s(X_k^{(j)}) \leftarrow \operatorname{softmax}(f_\theta(X_k^{(j)}))_1$ \Comment{Điểm rủi ro từ bộ mã hóa nguồn}
        \State $\mathcal{S}_{\text{warm}} \leftarrow \mathcal{S}_{\text{warm}} \sqcup [s(X_k^{(j)})]$
    \EndFor
\EndFor
\State $N_{\text{pool}} \leftarrow |\mathcal{S}_{\text{warm}}| = \sum_{j=1}^J K_{\text{valid}}^{(j)}$ \Comment{Tổng số cửa sổ nền tích lũy}
\State \textbf{Giai đoạn 2 --- Hiệu chuẩn ngưỡng phân vị thực nghiệm trên xe đích:}
\State $\tau_{\text{target}} \leftarrow \operatorname{Quantile}_{1-\alpha}(\mathcal{S}_{\text{warm}})$ \Comment{Bảo đảm điều kiện cỡ mẫu đuôi $N_{\text{pool}}\alpha \ge 1$}
\State \textbf{Giai đoạn 3 --- Suy luận hậu khởi động và lọc sự kiện trượt $m$-trong-$n$ trên từng bản ghi:}
\For{$j = 1$ \textbf{to} $J$}
    \For{$k = K_{\text{valid}}^{(j)}$ \textbf{to} $M^{(j)} - 1$}
        \State $X_k^{(j)}, H_{k+1} \leftarrow \Phi(\mathcal{W}_k^{(j)}; H_k)$
        \State $s(X_k^{(j)}) \leftarrow \operatorname{softmax}(f_\theta(X_k^{(j)}))_1$
        \State $a_k \leftarrow \mathbf{1}\big[s(X_k^{(j)}) \ge \tau_{\text{target}}\big]$ \Comment{Quyết định nhị phân thô tại cửa sổ $k$}
        \State $j_0 \leftarrow \max(K_{\text{valid}}^{(j)},\, k - n + 1)$
        \State $\widehat{Y}_{k, (j)}^{(m/n)} \leftarrow \mathbf{1}\left[\sum_{r=j_0}^{k} a_r \ge m\right]$ \Comment{Phát cảnh báo khi có $\ge m$ trên $n$ cửa sổ vượt ngưỡng}
    \EndFor
\EndFor
\State \Return $\tau_{\text{target}}, \{\widehat{Y}_{k, (j)}^{(m/n)}\}$
\end{algorithmic}}
\end{algorithm}

\section{Các cơ chế thích ứng và triệt tiêu cấp đặc trưng phục vụ chẩn đoán bất biến miền}\label{sec:domain-adaptation-methods}
Bên cạnh cơ chế hiệu chuẩn ngưỡng ở đầu ra (Giai đoạn II), một câu hỏi lý thuyết trọng tâm là liệu có thể triệt tiêu trực tiếp dấu ấn đặc thù xe ngay trong không gian biểu diễn tiềm ẩn $z_k \in \mathbb{R}^{64}$ hay không (Câu hỏi nghiên cứu RQ5b). Để kiểm định giả thuyết này một cách hệ thống và đối chứng với Giai đoạn II, khóa luận tích hợp ba nhóm phương pháp thích ứng và triệt tiêu cấp đặc trưng (tổng hợp tại nửa dưới Bảng~\ref{tab:adaptation-taxonomy}).

\subsection{Điều chuẩn phân phối ẩn bằng trộn phong cách (MixStyle)}\label{subsec:method-mixstyle}
Nhằm tăng cường sức chống chịu trước biến thiên phân phối đầu vào ngay từ pha huấn luyện đơn nguồn mà không cần dữ liệu xe đích, kỹ thuật MixStyle~\cite{zhou2021mixstyle} được thích ứng cho chuỗi thời gian CAN. Sau tầng chiếu tuyến tính ($E \in \mathbb{R}^{W \times d}, d = 64$) và trước khi cộng mã hóa vị trí, với mỗi cặp mẫu cùng nhãn $(X, \widetilde{X})$ trong cùng lô huấn luyện ($Y = \widetilde{Y}$), thống kê kỳ vọng $\mu(X)$ và độ lệch chuẩn $\sigma(X)$ theo trục khung tin:
\begin{equation}
\mu(X) = \frac{1}{W}\sum_{i=1}^W E_i, \qquad \sigma(X) = \sqrt{\frac{1}{W}\sum_{i=1}^W (E_i - \mu(X))^2 + \epsilon}.
\end{equation}
Thống kê phong cách hỗn hợp được tạo qua phép nội suy lồi với hệ số $\lambda \sim \operatorname{Beta}(\alpha_{\text{mix}}, \alpha_{\text{mix}})$ ($\alpha_{\text{mix}} = 0{,}1$):
\begin{align}
\gamma &= \lambda \sigma(X) + (1 - \lambda) \sigma(\widetilde{X}),\\
\beta &= \lambda \mu(X) + (1 - \lambda) \mu(\widetilde{X}),
\end{align}
để tạo thống kê hỗn hợp $(\beta, \gamma)$ và chuẩn hóa lại theo công thức:
\begin{equation}
\operatorname{MixStyle}(X) = \gamma \odot \frac{E - \mu(X)}{\sigma(X)} + \beta.
\end{equation}
Phép trộn chỉ kích hoạt ngẫu nhiên với xác suất $p = 0{,}5$ lúc huấn luyện; trong pha suy luận, nhánh này trở về ánh xạ đồng nhất thuần túy nên không phát sinh bất kỳ chi phí tính toán bổ sung nào.

\subsection{Học đa nguồn giữ ngoài một xe kết hợp đối kháng có điều kiện (LOVO-cAdv)}\label{subsec:method-lovo}
Khi dữ liệu huấn luyện có sẵn từ nhiều dòng xe nguồn, khóa luận thiết lập giao thức học đa nguồn giữ ngoài một xe (\textit{Leave-One-Vehicle-Out} --- LOVO) trên bốn dòng xe vật lý (Impala, Traverse, Silverado và Forester): mỗi lượt kiểm thử giữ trọn một xe làm miền đích chưa quan sát và dùng ba xe còn lại làm miền nguồn tách biệt theo mã băm SHA-256.

Kiến trúc mạng đối kháng miền (DANN~\cite{ganin2016dann}) gồm bộ trích xuất đặc trưng $G_f$, bộ phân loại tấn công $G_y$ và bộ phân biệt miền đối kháng có điều kiện $G_d$. Để tránh ép xóa nhầm các đặc trưng phân tách lớp tấn công, $G_d$ gồm hai đầu mạng MLP 2 tầng độc lập $G_{d,0}$ và $G_{d,1}$ được định tuyến cứng theo nhãn lớp thực $Y \in \{0, 1\}$ của mẫu nguồn, nối với $z_k = G_f(X_k)$ qua tầng đảo ngược gradient ($\text{GRL}_\lambda$) với hệ số $\lambda(p) = \frac{2}{1 + \exp(-10p)} - 1$ theo hàm mục tiêu:
\begin{equation}
\mathcal{L}_{\text{total}} = \mathcal{L}_y(G_y(z_k), Y) - \lambda \mathcal{L}_d(G_d(z_k), D),
\end{equation}
trong đó $D$ là nhãn định danh miền xe nguồn. Song song với đầu vào cấu trúc 30 chiều đầy đủ (\textit{Structural + cAdv}), khóa luận khảo sát thêm biến thể lược bỏ 8 byte payload tuyệt đối (\textit{Relative + cAdv}, 22 chiều --- chỉ giữ DLC, mặt nạ hiệu lực, vi sai $\Delta\text{payload}$, cờ lịch sử $h_i$ và các thống kê cục bộ) nhằm buộc bộ mã hóa tập trung hoàn toàn vào quy luật biến thiên tương đối.

\subsection{Làm trắng nền lành tính, triệt tiêu khái niệm tuyến tính (LEACE/INLP8) và điểm năng lượng Mahalanobis}\label{subsec:method-whitening}
Nhằm chẩn đoán trực tiếp mức độ tồn lưu thông tin nhận diện phương tiện và ranh giới giữa bất biến tuyến tính với rò rỉ phi tuyến trên biểu diễn ẩn đóng băng $z_k \in \mathbb{R}^{64}$, khóa luận thiết lập chuỗi hậu xử lý gồm ba bước:
\begin{enumerate}
    \item \textbf{Làm trắng hiệp phương sai nền lành tính:} Từ tập cửa sổ lành tính đối chứng thu thập trên xe đích (gồm 2.000 cửa sổ tách làm hai tập con 1.000 cửa sổ ước lượng tham số và 1.000 cửa sổ chọn ngưỡng), hệ thống tính vector kỳ vọng $\mu_b$ và ma trận hiệp phương sai chính quy hóa co $\Sigma_s = (1 - \gamma)\Sigma_b + \gamma\bar{\sigma}^2 I$ ($\gamma = 0{,}1$), rồi áp dụng phép biến đổi làm trắng $W_{\text{white}} = \Sigma_s^{-1/2}$ để đưa phân phối nền của từng xe về kỳ vọng triệt tiêu và hiệp phương sai đơn vị: $z'_k = W_{\text{white}}(z_k - \mu_b)$. (Lưu ý về thiết kế tách tập chẵn--lẻ so với chia khối thời gian liên tục sẽ được đánh giá đối chứng cụ thể trong Chương~\ref{chap:results}).
    \item \textbf{Triệt tiêu khái niệm tuyến tính:} Áp dụng phép chiếu xiên dạng đóng LEACE~\cite{belrose2023leace} ($P = I - \Sigma_X^{1/2}UU^\top \Sigma_X^{-1/2}$, trực giao dưới tích vô hướng Mahalanobis $\Sigma_X^{-1}$) hoặc phép chiếu không gian rỗng lặp INLP~\cite{ravfogel2020null} (lặp tối đa 32 vòng để rút gọn về 8 chiều dư, ký hiệu INLP8) ước lượng trên các xe nguồn nhằm xóa triệt để mọi hướng tuyến tính mang thông tin nhận diện hãng xe.
    \item \textbf{Điểm bất thường năng lượng Mahalanobis ($E_{\text{white}}$):} Tính khoảng cách bình phương trung bình chuẩn hóa trên không gian đã làm trắng (theo khoảng cách Mahalanobis~\cite{lee2018mahalanobis}) mà không phụ thuộc vào đầu phân loại nhị phân nguồn:
    \begin{equation}
    E_{\text{white}}(X_k) = \frac{1}{d}\left\|W_{\text{white}}(z_k - \mu_b)\right\|_2^2 \quad (d = 64).
    \end{equation}
\end{enumerate}

\section{Tóm tắt chương}\label{sec:method-summary}
Chương~\ref{chap:method} đã phát biểu hình thức bài toán phát hiện xâm nhập mạng CAN xuyên phương tiện và đặc tả trọn vẹn khung giải pháp đề xuất gồm hai giai đoạn cốt lõi: \textbf{Giai đoạn I} xây dựng không gian biểu diễn cấu trúc 30 chiều độc lập định danh (cùng nhánh mở rộng động học thời gian 32 chiều cho bus đồng hồ chuẩn) kết hợp bộ mã hóa Transformer 75.298 tham số; \textbf{Giai đoạn II} bổ sung cơ chế hiệu chuẩn phân vị trên tiền tố lành tính không nhãn kết hợp bộ lọc sự kiện trượt $m$-trong-$n$ nhằm khôi phục điểm vận hành mà không huấn luyện lại mô hình. Bên cạnh đó, chương đã trình bày hệ thống các phương pháp thích ứng và triệt tiêu cấp đặc trưng (MixStyle, LOVO-cAdv, làm trắng nền lành tính, LEACE/INLP8 và $E_{\text{white}}$) làm công cụ đối chứng lý thuyết cho hiện tượng đan xen đặc trưng. Chương~\ref{chap:results} sẽ triển khai đánh giá thực nghiệm toàn diện khung đề xuất và các nhánh đối chứng này theo năm câu hỏi nghiên cứu RQ1--RQ5.

"""

with open('thesis/vi/main.tex', 'r', encoding='utf-8') as f:
    text = f.read()

start_marker = r'\section{Các phương pháp thích ứng miền và hiệu chuẩn vận hành}\label{sec:domain-adaptation-methods}'
end_marker = r'\chapter{Thực nghiệm và đánh giá}\label{chap:results}'

p1 = text.find(start_marker)
p2 = text.find(end_marker)

if p1 != -1 and p2 != -1:
    updated_text = text[:p1] + new_chap3_part + text[p2:]
    with open('thesis/vi/main.tex', 'w', encoding='utf-8') as f:
        f.write(updated_text)
    print("Chapter 3 successfully updated!")
else:
    print("Could not find markers!")
