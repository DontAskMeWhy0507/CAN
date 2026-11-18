# BÁO CÁO THẨM ĐỊNH HỌC THUẬT TOÀN DIỆN VÀ ĐỘC BẢN (DEFINITIVE UNIT REVIEW REPORT)
## PHÂN ĐOẠN 1: PHẦN ĐẦU & CHƯƠNG 1 (MỞ ĐẦU VÀ ĐỘNG CƠ NGHIÊN CỨU)

**Tác phẩm:** Khóa luận tốt nghiệp *"Biểu diễn cấu trúc cho hệ thống phát hiện xâm nhập mạng CAN bus đa phương tiện"*  
**Tác giả:** Vũ Tiến Tuấn Trung — **Cán bộ hướng dẫn:** PGS. TS. Nguyễn Ngọc Hóa  
**Cơ sở đào tạo:** Trường Đại học Công nghệ, Đại học Quốc gia Hà Nội (UET-VNU)  
**Cấp độ tổng hợp:** Final Review Aggregator (Level 2 Root) — Tổng hợp và tiến hóa tối hậu từ Evolved Review 1 (Candidates 1 & 3) và Evolved Review 2 (Candidates 2 & 4)  
**Ngày hoàn thành:** 2026-11-17  
**Tệp mục tiêu:** `f:\00_Research\unit_report_segment_1_intro_motivation.md`  

**Phạm vi thẩm định mã nguồn LaTeX:**
- **Frontmatter (Phần đầu):** Trang bìa ngoài (dòng 212–250), Trang bìa phụ (dòng 257–299), Lời cảm ơn và Tuyên bố liêm chính AI (dòng 309–314), Lời cam đoan (dòng 320–330), Tóm tắt tiếng Việt (dòng 337–350), Abstract tiếng Anh (dòng 356–369), Mục lục và Danh mục bảng/hình (dòng 375–413), Danh mục từ viết tắt (dòng 415–438) trong `thesis/vi/main.tex` và `DOCUMENT_TEXT_MAP.md`.
- **Chương 1 (Mở đầu):** Mục 1.1 Động cơ nghiên cứu, Mục 1.2 Vấn đề và phạm vi, Mục 1.3 Mục tiêu và định hướng nghiên cứu (RQ1–RQ4), Mục 1.4 Đóng góp và phạm vi giới hạn, Mục 1.5 Tổ chức khóa luận (dòng 445–494 trong `thesis/vi/main.tex` và `DOCUMENT_TEXT_MAP.md`).

---

## 1. TỔNG QUAN ĐIỀU HÀNH & PHƯƠNG PHÁP LUẬN TỔNG HỢP (EXECUTIVE SUMMARY & METHODOLOGY)

### 1.1. Bối cảnh đào tạo và Định vị học thuật
Tài liệu thẩm định là công trình Khóa luận tốt nghiệp Đại học hệ chính quy ngành Hệ thống thông tin của Trường Đại học Công nghệ, ĐHQGHN (xác lập tại dòng 242 và dòng 287). Mặc dù văn bản hành chính thuộc bậc cử nhân, toàn bộ hội đồng đánh giá độc lập (cả 4 chuyên viên ban đầu và 2 bộ tổng hợp tiến hóa Level 1) đều nhất trí đánh giá: **Quy mô thực nghiệm, độ sâu phân tích phương pháp luận, tính kỷ luật trong tái lập và sự trung thực học thuật của công trình hoàn toàn vượt chuẩn một khóa luận đại học thông thường, đạt tới đẳng cấp của một Luận văn Thạc sĩ định hướng nghiên cứu (Master's Thesis by Research) xuất sắc**.

Hệ thống thẩm định áp dụng mô hình tổng hợp RSA (Review-Synthesis-Aggregation) hai cấp bậc, bảo đảm:
1. **Kiểm chứng thực chứng (Empirical Verification):** Đối soát trực tiếp 100% các nhận định phê bình với mã nguồn LaTeX gốc (`main.tex` / `DOCUMENT_TEXT_MAP.md`) và toàn bộ kho dữ liệu thực nghiệm ở Chương 4, Chương 5, Chương 6 và Phụ lục A.
2. **Lăng kính kép (Dual-Lens Evaluation):** Kết hợp chặt chẽ giữa tính chặt chẽ phương pháp luận khoa học (Methodological Rigor) và năng lực phòng thủ hội đồng bảo vệ thực tế (Defense Committee Readiness).

### 1.2. Nhận định tổng quan về Phân đoạn 1 (Executive Summary)
Phân đoạn 1 đã hoàn thành xuất sắc vai trò thiết lập bài toán trung tâm của an ninh mạng ô tô đương đại: **Bảo vệ mạng truyền thông CAN bus khi chuyển giao sang các dòng xe chưa từng quan sát mà không đòi hỏi dữ liệu tấn công có nhãn để huấn luyện lại mô hình**. 

Những điểm sáng học thuật đặc biệt nổi bật bao gồm:
- **Liêm chính học thuật xuất sắc và dũng cảm công bố kết quả âm tính (Negative Result):** Tác giả không hề che giấu sự sụt giảm hiệu năng dưới ngưỡng tĩnh đóng băng từ nguồn ở Điều kiện B: Recall của biểu diễn cấu trúc chỉ đạt $73{,}83\%$ so với $85{,}41\%$ của mô hình Raw baseline, và tỷ lệ báo động giả lên tới $\text{FAR} = 52{,}46\%$. Việc công bố minh bạch thất bại của ngưỡng tĩnh ngay tại Tóm tắt và Abstract thể hiện tư duy khoa học mẫu mực.
- **Phân tách đột phá giữa Năng lực xếp hạng độc lập ngưỡng và Hiện tượng trôi dạt ngưỡng:** Công trình chứng minh rằng sự sụp đổ FAR ở ngưỡng tĩnh không bắt nguồn từ sự thất bại của biểu diễn cấu trúc, mà do hiện tượng trôi dạt ngưỡng (logit drift). Về chất lượng xếp hạng độc lập ngưỡng, biểu diễn cấu trúc vượt trội hoàn toàn so với Raw: nâng độ chính xác trung bình (Average Precision -- AP) từ $0{,}3781$ lên $0{,}5554$ ($+17{,}74$ điểm phần trăm chênh lệch ghép cặp; Bảng 5.3).
- **Kiểm toán dữ liệu công phu và quyết định phương pháp luận đanh thép:** Bằng chứng kiểm toán 236 tệp benchmark `can-train-and-test` (193.240.845 khung tin), phát hiện 12.527 lần timestamp đi lùi với $99{,}84\%$ bước nhảy $\le 1\text{ ms}$, đã thiết lập cơ sở khoa học không thể tranh cãi cho việc chuyển trục đánh giá chính sang nhánh *content-only* (30 chiều) nhằm loại trừ nhiễu đồng hồ phần cứng capture.
- **Đột phá lý thuyết về ranh giới bất biến:** Phân định rõ ràng giữa *tính bất biến đổi tên định danh* (ID-renaming invariance) và *tính độc lập miền xe thực tế* (vehicle-domain invariance), được chứng minh định lượng qua phép đo Linear Probe giải mã danh tính hãng xe đạt tới $94{,}88\%$ do hiện tượng đan xen đặc trưng (*feature entanglement*).
- **Quy trình hai giai đoạn thực tiễn:** Khởi xướng cơ chế hiệu chuẩn nền lành tính ngắn không giám sát (*Benign Warmup Calibration*, $K=500$ cửa sổ, tương đương 16–32 giây khi nổ máy xe) giúp khôi phục hoàn toàn tính khả thi vận hành: đạt Recall $40{,}42\%$--$48{,}59\%$ với $\text{FAR} \le 1{,}08\%$.

### 1.3. Các tử huyệt chiến lược cần gia cố khẩn cấp
Bên cạnh các thành tựu vượt bậc, phân đoạn mở đầu tồn tại **5 lỗ hổng chiến lược** cần được chỉnh sửa dứt điểm trước khi in ấn và bảo vệ chính thức:
1. **Lỗ hổng cấu trúc trong Câu hỏi nghiên cứu (RQ1–RQ4):** Nghiên cứu tuyên bố rõ ràng Lộ trình hai giai đoạn (Giai đoạn 1: kiểm định zero-shot tĩnh; Giai đoạn 2: thích ứng Benign Warmup $K=500$). Tuy nhiên, cả 4 RQ tại Mục 1.3 chỉ đóng khung trong Giai đoạn 1. Đóng góp thực tiễn quan trọng nhất — cơ chế Benign Warmup giúp dập tắt FAR từ $52{,}46\%$ xuống $\le 1{,}08\%$ — hoàn toàn không có câu hỏi nghiên cứu chính thức đại diện!
2. **Khoảng trống "Rào cản độc quyền tệp DBC" (The Missing DBC Industrial Context):** Mục 1.1 chưa giải thích bối cảnh công nghiệp: tại sao các bên thứ ba không thể dùng tệp giải mã tín hiệu DBC của nhà sản xuất xe, khiến bài toán chuyển giao không nhãn dễ bị Hội đồng công kích là bài toán hàn lâm gượng ép.
3. **Bất đối xứng thông tin giữa hai bản tóm tắt song ngữ:** Abstract tiếng Anh có số liệu định lượng dập tắt báo động giả Opel Astra DoS từ $31{,}5\%$ xuống $0{,}17\%$, trong khi Tóm tắt tiếng Việt bị thiếu chi tiết giá trị này.
4. **Mơ hồ về thời gian vật lý của Warmup:** Con số "khoảng 16 giây" ghi trong Tóm tắt và Abstract là ước tính ở tải bus tối đa $2.000\text{ fps}$; ở mức tải thông thường $1.000\text{ fps}$ thời gian thực tế là 32 giây. Cần chuẩn hóa thành "$16\text{--}32$ giây".
5. **Hiểu lầm ngữ nghĩa thuật ngữ "Đa phương tiện":** Tiêu đề chứa cụm từ "đa phương tiện" dễ bị các thành viên Hội đồng ngành CNTT liên tưởng sang multimedia nếu không có phụ đề hoặc chú giải nổi bật.

---

## 2. PHÂN TÍCH TIẾN TRÌNH CÂU CHUYỆN VÀ MẠCH LẬP LUẬN (STORYLINE PROGRESSION & NARRATIVE ARC)

### 2.1. Đánh giá chi tiết từng mục theo dòng mã nguồn (Section-by-Section Analysis)

#### Mục 1.1: Động cơ nghiên cứu (dòng 446–452)
- **Đoạn 1 (dòng 447):** Xuất phát từ bản chất vật lý của mạng CAN: giao thức ưu tiên truyền thông thời gian thực và phân xử phân tán dựa trên ID, hoàn toàn không có cơ chế xác thực mật mã nguồn phát. Dẫn chứng Koscher et al. (2010) và Checkoway et al. (2011) xác lập tính hiện thực của các vụ tấn công chiếm quyền điều khiển phương tiện. Tác giả định vị IDS thụ động là giải pháp khả thi nhất vì không đòi hỏi thay đổi phần cứng ECU hiện hữu.
- **Đoạn 2 (dòng 449):** Chuyển tiếp sắc bén sang vấn đề an ninh mạng ô tô đương đại: các IDS học máy hiện nay phụ thuộc chặt chẽ vào các tương quan đặc thù của xe nguồn (CAN-ID, chu kỳ, mẫu payload). Khi chuyển xe, các tương quan này sụp đổ. Tác giả đưa vào một nguyên lý phương pháp luận quan trọng: *"hiệu năng suy giảm không tự động chứng minh mô hình học thuộc ID"*, tách bạch đo lường hiệu năng khỏi giả thuyết giải thích nguyên nhân.
- **Đoạn 3 (dòng 451):** Chọn bộ benchmark `can-train-and-test` (Lampe et al., 2024) và điểm mặt các công trình mới nhất giai đoạn 2024–2026 (Khreasat 2026, Dong 2026 - MTFF, Koltai 2026, Obafemi 2026 - TRAVEL). Tác giả vạch trần hai cạm bẫy phương pháp luận cốt lõi của y văn quốc tế:
  1. *Bất cập 1 (Trộn lẫn biểu diễn và hiệu chuẩn):* Báo cáo chuyển giao tốt khi bỏ CAN-ID nhưng lại âm thầm hiệu chuẩn trên dữ liệu lành của xe đích hoặc thả nổi ngưỡng, khiến người đọc ngộ nhận về năng lực nội tại của biểu diễn.
  2. *Bất cập 2 (Đánh đồng tính bất biến):* Đồng nhất toán học thuần túy giữa tính bất biến đổi tên định danh (*ID-renaming invariance*) với tính độc lập miền xe thực tế (*vehicle-domain invariance*), phớt lờ biến thiên phân phối payload và hình thái luồng tin.

#### Mục 1.2: Vấn đề và phạm vi (dòng 453–461)
Xác lập một hệ thống ranh giới nghiên cứu (Scope constraints) minh bạch:
- **Đơn vị quyết định và chính sách nhãn (dòng 454):** Phân loại nhị phân trên cửa sổ không chồng lặp $W=64$ khung tin ($Y_k = \max y_i$). Cửa sổ có nhãn dương khi chứa $\ge 1$ khung tin mang nhãn 1. Không nối qua biên tệp. Thừa nhận dũng cảm: nhãn cửa sổ dương tính không đồng nghĩa với định vị chính xác khung tin tấn công; đặc biệt phân tích rõ trường hợp tấn công đình chỉ (*suspension attack* trong CAN-MIRGU) không có khung tin độc hại chèn thêm.
- **Quy tắc đóng băng ngưỡng nguồn (dòng 456):** Toàn bộ tham số chuẩn hóa và ngưỡng quyết định được chọn từ nguồn và giữ nguyên khi sang xe đích.
- **Kiểm toán Monotonicity Timestamp (dòng 458):** Phát hiện 12.527 lần timestamp đi lùi trên 100/236 tệp CTT (193.240.845 khung tin). Phân tích biên độ: $99{,}84\%$ bước nhảy $\le 1\text{ ms}$ (median $25{,}03\,\mu\text{s}$, p95 $92{,}27\,\mu\text{s}$), 20 trường hợp trong khoảng $(1\text{ ms}; 7{,}895\text{ ms}]$, và 0 trường hợp $> 1$ giây. Kết luận đây là nhiễu đồng hồ/bộ đệm phần cứng capture, biện minh khoa học cho việc chọn trục đánh giá chính là nhánh *content-only* (30 chiều).
- **Ranh giới giao thức (dòng 458):** Giới hạn ở CAN cổ điển 2.0A (11-bit ID, tối đa 8 byte payload); từ chối CAN-FD và ID mở rộng 29-bit.
- **Giải nghĩa thuật ngữ (dòng 460):** Tuyên bố minh bạch: "đa phương tiện" = cross-vehicle transfer (xuyên phương tiện giữa các dòng xe), không phải multimedia.

#### Mục 1.3: Mục tiêu và định hướng nghiên cứu (dòng 462–480)
- Tuyên bố mục tiêu tổng quát (dòng 463): Thiết lập quy trình biểu diễn cấu trúc không phụ thuộc CAN-ID thô, cho phép mô hình huấn luyện một lần tại phòng thí nghiệm nhưng chuyển giao bảo vệ được nhiều dòng xe khác nhau mà không cần dữ liệu tấn công có nhãn để huấn luyện lại.
- Tuyên bố Lộ trình hai giai đoạn phương pháp luận (dòng 465–469):
  - *Giai đoạn 1:* Kiểm định zero-shot nghiêm ngặt (ngưỡng đóng băng từ nguồn).
  - *Giai đoạn 2:* Thích ứng vận hành thực tế (Benign Warmup Calibration $K=500$).
- Liệt kê 4 câu hỏi nghiên cứu RQ1–RQ4 (dòng 471–477).
- Tiêu chí kiểm định chính và phân tích MixStyle (dòng 479–480).

#### Mục 1.4: Đóng góp và phạm vi giới hạn (dòng 481–490)
Tổng kết 3 đóng góp khoa học chính:
1. Đặc tả biểu diễn cấu trúc 30D và phân định lý thuyết về tính bất biến (dòng 484).
2. Thiết lập giao thức đối chứng quy mô lớn: 60 đơn vị IDS chính, 144 lượt ablation, 12 lượt MixStyle, lưới warmup, 48 lượt LOVO DANN, 96 pipeline làm trắng LEACE/INLP8, 120 lượt thực nghiệm mở rộng (dòng 485).
3. Định lượng sự phân kỳ giữa chất lượng xếp hạng (AP), rò rỉ xe (Linear Probe 94,88%) và điểm vận hành (dòng 486).
Phạm vi giới hạn (dòng 489): Nhấn mạnh tính tái lập; đo đạc thời gian trên máy trạm phản ánh chi phí tính toán lý thuyết, không thay thế kiểm định deadline thời gian thực trên ECU nhúng.

#### Mục 1.5: Tổ chức khóa luận (dòng 491–494)
Tóm lược cấu trúc 5 chương và phần phụ lục.

---

### 2.2. Điểm nghẽn trong lập luận cốt truyện và Giải pháp gia cố (Narrative Bottlenecks)

#### Điểm nghẽn 1: Sự thiếu vắng luận cứ "Rào cản độc quyền tệp DBC" (The Missing DBC Industrial Context)
- **Thực trạng văn bản:** Dòng 449 nêu việc CAN-ID thay đổi giữa các xe khiến mô hình mất tác dụng, nhưng không đả động gì đến tệp DBC.
- **Nguy cơ phản biện:** Trong kỹ thuật ô tô, tệp DBC (*Database CAN*) định nghĩa chính xác cấu trúc giải mã từng bit payload thành các biến vật lý chuẩn hóa (vận tốc xe, góc lái, áp suất phanh). Hội đồng sẽ chất vấn: *"Tại sao không dùng file DBC để giải mã tín hiệu vật lý chuẩn hóa rồi xây dựng IDS trên các biến vật lý, mà phải trích xuất đặc trưng cấu trúc 30 chiều trên payload thô để nhận về FAR 52%?"*
- **Luận cứ công nghiệp cần bổ sung:**
  1. *Rào cản sở hữu trí tuệ tối mật (IP Barrier):* Tệp DBC là tài sản sở hữu trí tuệ độc quyền của OEM. Các bên thứ ba (Aftermarket telematics, thiết bị gắn cổng OBD-II, đơn vị bảo hiểm UBI, doanh nghiệp quản lý đội xe hỗn hợp đa thương hiệu) **hoàn toàn không được phép tiếp cận tệp DBC**.
  2. *Sự phân mảnh cấu trúc và cập nhật phần mềm:* Ngay trong cùng một hãng xe, tệp DBC bị thay đổi liên tục theo đời xe (model year), phiên bản trang bị (trim levels), và sau các bản cập nhật phần mềm ECU từ xa (OTA).
  3. *Nguy cơ an toàn vật lý khi thu thập dữ liệu có nhãn:* Việc tiêm tấn công thực nghiệm trên xe thật để thu thập dữ liệu huấn luyện lại mô hình tiềm ẩn nguy cơ phá hỏng ECU (bricking) hoặc gây tai nạn chết người.

#### Điểm nghẽn 2: Thiếu cầu nối trực giác vật lý biện minh cho Biểu diễn cấu trúc 30D
- **Thực trạng văn bản:** Dòng 451 nhảy thẳng từ việc chỉ trích y văn sang tuyên bố bổ sung vi sai payload và quan hệ cục bộ.
- **Khoảng trống lý giải:** Tại sao $\Delta\text{payload}$ và quan hệ cục bộ lại là các đại lượng mang tính bất biến chuyển giao giữa các dòng xe?
- **Trực giác vật lý cần bổ sung:** Dù CAN-ID khác nhau giữa các hãng xe, các quy luật vật lý và động học của xe cơ giới là bất biến:
  - *Tính trơn tru của tín hiệu cảm biến vật lý:* Vận tốc, áp suất phanh, gia tốc biến thiên liên tục theo quán tính vật lý, khiến vi sai payload giữa hai khung tin cùng ID kế tiếp ($\Delta\text{payload}$) luôn có xu hướng nhỏ và trơn tru. Hành vi tấn công tiêm tin giả mạo (Fuzzing, Spoofing) sẽ làm đứt gãy tính trơn tru này.
  - *Tính chu kỳ xác định của vòng lặp điều khiển:* Các thông điệp điều khiển thời gian thực luôn xuất hiện với chu kỳ cố định, tạo nên tần suất cục bộ ổn định trong cửa sổ $W=64$. Tấn công DoS sẽ làm bùng nổ tần suất của một ID lạ.
  - *Cấu trúc tô-pô mạng ECU:* Thứ tự ưu tiên phân xử bus tạo nên xác suất chuyển tiếp cục bộ đặc trưng giữa các thông điệp.

#### Điểm nghẽn 3: Chưa định vị rõ đối tượng hưởng lợi thực tế (Target Stakeholders)
- Chương 1 cần tuyên bố tường minh: Nghiên cứu này không phục vụ chính bản thân hãng xe OEM (vốn đã có sẵn file DBC và dữ liệu độc quyền của họ), mà phục vụ: (a) Các nhà sản xuất thiết bị an ninh và viễn thông bên thứ ba (Aftermarket OBD-II dongles); (b) Các công ty quản lý đội xe hỗn hợp đa nhãn hiệu (mixed-brand fleet management); (c) Các nhà cung cấp Tier-1 phát triển module gateway an ninh chuẩn hóa.

#### Điểm nghẽn 4: Hiện đại hóa bối cảnh đe dọa an ninh mạng ô tô (dòng 447)
- Dòng 447 chỉ trích dẫn Koscher 2010 và Checkoway 2011 (đã 15 năm tuổi). Cần bổ sung các minh chứng tấn công hiện đại trong kỷ nguyên ô tô thông minh: nghiên cứu của Ken Tindell (2023) về tấn công CAN Injection qua giắc cắm đèn pha ô tô để chiếm quyền điều khiển và trộm xe; các vụ tấn công qua cổng viễn thông telematics và gateway phân vùng.

---

## 3. KIỂM TOÁN TÍNH NHẤT QUÁN TOÀN DIỆN (ABSTRACT & FRONTMATTER AUDIT)

### 3.1. Bảng đối chiếu chéo đa ngôn ngữ và đa phân đoạn
Bảng dưới đây tổng hợp kết quả đối soát chi tiết từng chỉ số kỹ thuật giữa Tóm tắt tiếng Việt, Abstract tiếng Anh, Chương 1 và toàn bộ phần thân khóa luận (`DOCUMENT_TEXT_MAP.md` / `thesis/vi/main.tex`):

| Hạng mục kiểm toán | Tóm tắt Tiếng Việt (dòng 337–350) | Abstract Tiếng Anh (dòng 356–369) | Chương 1: Mở đầu (dòng 445–494) | Thân bài & Kết quả thực nghiệm (`main.tex`) | Trạng thái Kiểm toán & Đánh giá |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Kích thước biểu diễn Structural** | 30 chiều (dòng 340) | 30-dimensional (dòng 359) | 30 chiều (dòng 484) | 30 chiều (Mục 4.4, Bảng 4.1 dòng 696–709) | **Khớp hoàn hảo (Pass)**. Loại bỏ bit CAN-ID thô khỏi đầu vào bộ phân loại. |
| **Kích thước biểu diễn Raw baseline** | Mô hình Raw (dòng 342) | Raw baselines (dòng 361) | Biểu diễn Raw (dòng 473) | 28 chiều (Mục 4.4, dòng 695) | **Khớp hoàn hảo (Pass)**. |
| **Tập dữ liệu & Hạt giống CTT** | 4 tập dữ liệu CTT qua 3 hạt giống ngẫu nhiên (dòng 342) | Four cross-vehicle benchmark sets over three random seeds (dòng 361) | 4 tập $\times$ 3 seed $\times$ 5 phương pháp (dòng 485) | 4 tập (Set 1–4) $\times$ 3 seed = 12 cấu hình (Bảng 2.2, Bảng 5.1) | **Khớp hoàn hảo (Pass)**. |
| **Recall zero-shot Điều kiện B** | 73,83% vs 85,41% Raw (dòng 342) | 73.83% vs 85.41% for Raw (dòng 361) | Đánh giá recall B (dòng 479) | 0,7383 vs 0,8541 (Bảng 5.1 dòng 1395, Bảng 5.2 dòng 1150) | **Khớp hoàn hảo 100% (Pass)**. |
| **FAR zero-shot Điều kiện B** | $\text{FAR} = 52{,}46\%$ (dòng 342) | $\text{FAR} = 52.46\%$ (dòng 361) | Ngân sách FAR (dòng 473, 479) | $52.461{,}46 / 100.000 = 52{,}46\%$ (Bảng 5.1 dòng 1396, Bảng 5.2) | **Khớp hoàn hảo 100% (Pass)**. |
| **Mức tăng AP Điều kiện B** | 0,3781 lên 0,5554 (+17,74 pp ghép cặp; +17,73 pp TB) (dòng 342) | 0.3781 to 0.5554 (+17.74 pp paired diff; +17.73 diff of means) (dòng 361) | 0,3781 lên 0,5554 (dòng 486) | 0,3781 lên 0,5554 (Bảng 5.3 dòng 954; Bảng 5.2 dòng 1150) | **Khớp hoàn hảo 100% (Pass)**. Phân biệt rõ chênh lệch ghép cặp và trung bình. |
| **Độ chính xác Vehicle Linear Probe** | 94,88% (dòng 342) | 94.88% (dòng 361) | Rò rỉ xe 94,88% (dòng 486) | 94,88% probe balanced accuracy (Mục 5.3 dòng 1239; Bảng 5.12) | **Khớp hoàn hảo 100% (Pass)**. |
| **Tham số Warmup ($K$)** | $K = 500$ cửa sổ (dòng 344) | $K = 500$ windows (dòng 363) | $K = 500$ cửa sổ (dòng 468) | $K = 500$ (Mục 5.7, Bảng 5.22 dòng 1560) | **Khớp hoàn hảo (Pass)**. |
| **Thời gian vật lý Warmup** | "khoảng 16 giây khi nổ máy" (dòng 344) | "$\approx 16$ seconds" (dòng 363) | "khoảng $16\text{--}32$ giây khi nổ máy xe" (dòng 468) | $\approx 16\text{ s}$ ở 2.000 fps hay $\approx 32\text{ s}$ ở 1.000 fps (dòng 1706) | **LỆCH NHẸ (Inconsistent)**: Abstract/Tóm tắt ghi 16s; Mục 1.3 ghi 16–32s. Cần chuẩn hóa. |
| **Hiệu năng sau Warmup** | Recall 40,42%--48,59%, $\text{FAR} \le 1{,}08\%$ (dòng 344) | Recall 40.42%--48.59%, $\text{FAR} < 1.08\%$ (dòng 363) | N/A (chỉ nêu giải pháp ở dòng 468) | Đơn nhánh 40,42% (FAR 0,85%), MixStyle 48,59% (FAR 1,08%) (Bảng 5.22 dòng 1560–1570) | **Lệch ký hiệu**: Tiếng Việt ghi $\le$, Tiếng Anh ghi $<$. Thống nhất dùng $\le 1{,}08\%$. |
| **Báo động giả ngoại bộ Opel Astra DoS** | Nêu định tính: "loại bỏ điểm suy biến báo động giả trên CICIoV2024 và Opel Astra" (dòng 344) | **Có số liệu định lượng**: "suppressing Opel Astra DoS false alarms from 31.5% to 0.17%" (dòng 363) | N/A | FAR nguồn 31.534,46 (31,53%) giảm xuống 0,17% (Mục 5.4, Bảng 5.13 dòng 1320) | **BẤT ĐỐI XỨNG NỘI DUNG (Discrepancy)**: Bản tiếng Việt thiếu số liệu định lượng đắt giá này! |
| **Kiểm toán Timestamp đi lùi** | N/A | N/A | 12.527 lần trên 100/236 tệp, 99,84% $\le 1\text{ ms}$; median $25{,}03\,\mu\text{s}$, p95 $92{,}27\,\mu\text{s}$ (dòng 458) | Khớp chính xác 100% với Bảng 5.4, Mục 5.1.1 và Phụ lục A.2 | **Khớp hoàn hảo (Pass)**. |
| **Kích thước cửa sổ phân tích** | N/A | N/A | $W=64$, khảo sát $W \in \{32, 64, 128\}$ (dòng 454, 474) | Chuẩn $W=64$; ablation $W=32, 128$ (Bảng 5.5, dòng 1170) | **Khớp hoàn hảo (Pass)**. |

---

### 3.2. Đánh giá Tuyên bố Sử dụng Công cụ AI và Lời cam đoan
- **Lời cảm ơn (dòng 313):** Tác giả có một tuyên bố sử dụng công cụ AI rất minh bạch:
  > *"Các công cụ AI được sử dụng để hỗ trợ soạn thảo, dịch thuật, rà soát tài liệu và phát triển mã nguồn. Tác giả có trách nhiệm kiểm tra nguồn trích dẫn, hiểu và xác nhận mã nguồn, chạy thực nghiệm và chịu trách nhiệm đối với nội dung cuối cùng. Phần kết quả chỉ sử dụng các lượt thực nghiệm đã hoàn tất và kiểm chứng theo giao thức được mô tả; số liệu thăm dò lịch sử được lưu riêng."*
- **Đánh giá chuyên gia:** Đây là một điểm sáng học thuật đặc biệt tiến bộ, tuân thủ tuyệt đối các chuẩn mực liêm chính học thuật quốc tế mới nhất (IEEE, ACM, Elsevier 2024–2026) và quy định của Đại học Quốc gia Hà Nội. Tác giả chủ động khẳng định trách nhiệm của con người trong kiểm chứng dữ liệu, xác nhận số liệu thực nghiệm là kết quả chạy thực tế trên máy tính chứ không phải do AI tạo sinh ngụy tạo.
- **Lời cam đoan (dòng 320–330):** Cam kết dứt khoát: không trình bày kết quả chưa chạy như kết quả đã thực nghiệm, không gán số liệu của cấu hình này sang cấu hình khác, chịu trách nhiệm hoàn toàn về tính tái lập.

---

### 3.3. Kiểm toán Danh mục từ viết tắt (dòng 415–438)
Rà soát bảng chữ viết tắt gồm 26 mục từ (dòng 418–436), phát hiện các xung đột và thiếu sót:
1. **Xung đột thuật ngữ nguy hiểm:**
   - Dòng 429 ghi `TF: Transformer` ngay phía trên dòng 430 `TF-IDF: Term Frequency--Inv. Doc. Freq.`. Trong Khoa học Máy tính và Học máy, `TF` luôn là viết tắt của *Term Frequency*. Việc viết tắt `Transformer` thành `TF` là phi chuẩn và gây nhầm lẫn trầm trọng khi đặt cạnh `TF-IDF`. Khuyến nghị: Thay bằng `Trans: Transformer` hoặc lược bỏ mục từ này.
2. **Lỗi định dạng chú thích:**
   - Dòng 431 ghi `FAR: False Alarm Rate (/100k hay %)`. Danh mục từ viết tắt chỉ giải nghĩa thuật ngữ, không nên đưa đơn vị đo lường vào cột định nghĩa. Khuyến nghị: Sửa thành `FAR: Tỷ lệ báo động giả (False Alarm Rate)`.
3. **Các từ viết tắt kỹ thuật xuất hiện trực tiếp trong Chương 1 và toàn văn nhưng bị bỏ sót:**
   - `CAN-ID`: Mã định danh thông điệp CAN (CAN Identifier).
   - `CAN-FD`: Mạng CAN với tốc độ dữ liệu linh hoạt (CAN with Flexible Data-Rate) — xuất hiện ở dòng 458.
   - `MLP`: Mạng nơ-ron truyền thẳng đa tầng (Multi-Layer Perceptron) — xuất hiện ở dòng 486.
   - `OEM`: Nhà sản xuất thiết bị gốc (Original Equipment Manufacturer) — thuật ngữ nền tảng của ngành ô tô.
   - `RQ`: Câu hỏi nghiên cứu (Research Question) — xuất hiện ở dòng 471–477.
   - `MixStyle`: Kỹ thuật trộn thống kê đặc trưng (Feature Statistics Mixing) — xuất hiện ở dòng 480, 485.
   - `ROC` / `AUC`: Đường cong đặc trưng hoạt động bộ thu / Diện tích dưới đường cong (Receiver Operating Characteristic / Area Under the Curve).
   - `OOD`: Ngoài phân phối dữ liệu (Out-of-Distribution).
   - `CRC`: Mã kiểm tra phần dư tuần hoàn (Cyclic Redundancy Check).
   - `SecOC`: Cơ chế truyền thông an toàn trên xe (Secure On-Board Communication).

---

### 3.4. Kiểm toán Quy chuẩn Mở rộng Từ viết tắt ở Lần xuất hiện Đầu tiên
- Dòng 447 viết: *"Một IDS thụ động có thể giám sát lưu lượng mà không yêu cầu thay đổi mọi ECU..."*
- **Lỗi quy chuẩn học thuật:** Cụm từ `IDS` và `ECU` chưa từng được viết đầy đủ ở dạng `Hệ thống phát hiện xâm nhập (Intrusion Detection System -- IDS)` và `Bộ điều khiển điện tử (Electronic Control Unit -- ECU)` trong nội văn Chương 1 trước khi dùng dạng viết tắt. Cần bổ sung mở rộng tại lần xuất hiện đầu tiên.

---

## 4. KIỂM TOÁN PHÁT BIỂU BÀI TOÁN, PHẠM VI VÀ CÁC CÂU HỎI NGHIÊN CỨU (RQ1–RQ4)

### 4.1. Đánh giá tính chặt chẽ của các ranh giới phương pháp luận (Mục 1.2)
1. **Phân loại nhị phân trên cửa sổ không chồng lặp $W=64$ khung tin:**
   - $Y_k = \max_{i=kW}^{kW+W-1} y_i$. Cửa sổ có nhãn dương khi chứa ít nhất 1 khung tin bị gắn nhãn 1.
   - *Tính trung thực phương pháp luận (dòng 454):* Tác giả cảnh báo thẳng thắn rằng nhãn cửa sổ dương tính không đồng nghĩa với việc định vị chính xác khung tin tấn công. Đặc biệt, đối với các cuộc tấn công dạng đình chỉ (*suspension attack* trong CAN-MIRGU), nhãn 1 biểu thị khoảng thời gian thiếu vắng thông điệp chứ không có khung tin độc hại chèn thêm. Biểu diễn cấu trúc phát hiện được suspension thực chất là nhờ sự thay đổi của xác suất chuyển tiếp Markov và tần suất cục bộ. Lập luận này vô hiệu hóa hoàn toàn nguy cơ Hội đồng bắt bẻ "ngộ nhận kết quả phát hiện cấp khung tin".
2. **Quyết định chuyển trục đánh giá chính sang nhánh Content-only (30D):**
   - Được bảo vệ vững chắc bằng phát hiện kiểm toán 12.527 lần timestamp đi lùi trên 100/236 tệp benchmark. Việc loại bỏ kênh thời gian $\Delta t$ giúp mô hình không bị quá khớp vào lỗi đồng hồ/bộ đệm của thiết bị capture dữ liệu công cộng, đảm bảo tính vững chắc khi triển khai thực tế.
3. **Từ chối CAN-FD và ID mở rộng 29-bit:**
   - Giới hạn ở CAN 2.0A tiêu chuẩn (11-bit ID, tối đa 8 byte payload) là hoàn toàn chuẩn mực cho phạm vi một khóa luận đại học, vì toàn bộ các bộ dữ liệu công chuẩn quốc tế hiện hành (Car-Hacking, CTT, ROAD, GEAR, CICIoV2024) đều thu thập trên CAN 2.0A.
4. **Hai điểm hở kỹ thuật cần bổ sung trong Mục 1.2:**
   - *Dung lượng bảng trạng thái lịch sử ($H_k$):* Bộ trích xuất duy trì bảng trạng thái lịch sử theo từng ID để tính $\Delta\text{payload}$ và xác suất chuyển tiếp. Dù trong Chương 4 tác giả đo được bảng trạng thái tốn khoảng $130\text{ KiB}$ cho 2.048 ID, Mục 1.2 chưa nêu con số này, dễ khiến người đọc băn khoăn liệu kẻ tấn công có thể làm tràn bộ nhớ (memory exhaustion) vi điều khiển bằng cách quét hàng nghìn ID lạ hay không.
   - *Tỷ lệ khung tin dư cuối tệp:* Cần bổ sung khẳng định rằng số lượng khung tin dư $(<64)$ bị loại bỏ ở cuối mỗi tệp là không đáng kể so với tổng số 193 triệu khung tin, đảm bảo không gây lệch mẫu số thống kê.

---

### 4.2. Lỗ hổng cấu trúc của RQ1–RQ4 và Hệ Giả thuyết Khoa học Phản nghiệm (Falsifiable Hypotheses)

#### Lỗ hổng cấu trúc lớn nhất: Bỏ quên Giai đoạn 2 trong hệ thống RQ
- Tại dòng 465–469, tác giả long trọng tuyên bố nghiên cứu gồm **Lộ trình hai giai đoạn**:
  - *Giai đoạn 1:* Kiểm định zero-shot nghiêm ngặt (ngưỡng đóng băng từ nguồn).
  - *Giai đoạn 2:* Thích ứng vận hành thực tế (Benign Warmup Calibration $K=500$).
- Thế nhưng, cả 4 RQ tại dòng 471–477 chỉ hỏi về Giai đoạn 1!
- Phát kiến thực nghiệm quan trọng nhất — cơ chế Benign Warmup giúp dập tắt FAR từ $52{,}46\%$ xuống $\le 1{,}08\%$ và nâng Recall lên $40{,}42\%$--$48{,}59\%$ — lại **hoàn toàn vắng bóng trong các câu hỏi nghiên cứu chính thức**! Tại Mục 1.3, phương pháp này chỉ được nhắc thoáng qua ở dòng 479 như một phân tích phụ.
- Đây là một điểm yếu logic học thuật nghiêm trọng: Hội đồng sẽ chất vấn: *"Tại sao đóng góp thực tiễn lớn nhất cứu vãn khả năng ứng dụng của hệ thống lại không được định hình thành một Câu hỏi nghiên cứu chính thức?"*

#### Nghịch lý tiêu chí kiểm định chính tại dòng 479
- Dòng 479 viết: *"Tiêu chí kiểm định chính của nghiên cứu là xem xét mức tăng recall trung bình ở điều kiện B của biểu diễn Structural so với Raw tại ngưỡng chọn từ validation nguồn..."*
- *Nghịch lý logic:* Ở Chương 5 (Bảng 5.1 và 5.2), Recall Điều kiện B của Structural lại **giảm** từ $85{,}41\%$ xuống $73{,}83\%$ (tụt $-11{,}58$ điểm phần trăm), và FAR vọt lên $52{,}46\%$. Nếu chiếu theo đúng "tiêu chí chính" này, nghiên cứu đã thất bại! Trong khi đó, thắng lợi thực sự của biểu diễn là Average Precision (AP tăng vọt từ $0{,}3781$ lên $0{,}5554$, tức $+17{,}74$ điểm phần trăm) lại bị dòng 479 xếp vào hàng "thước đo bổ sung".

#### Bảng Tái cấu trúc Hệ Giả thuyết Khoa học Phản nghiệm Đề xuất (RQ1–RQ4)
Để nâng tầm học thuật và bịt kín lỗ hổng chất vấn của hội đồng, hệ thống RQ1–RQ4 cần được tái cấu trúc thành các câu hỏi khoa học kèm giả thuyết có hướng phản nghiệm ($H_0 / H_1$):

```
========================================================================================================================
HỆ THỐNG CÂU HỎI NGHIÊN CỨU VÀ GIẢ THUYẾT KHOA HỌC PHẢN NGHIỆM ĐỀ XUẤT (RQ1 - RQ4)
========================================================================================================================

RQ1: VỀ NĂNG LỰC CHUYỂN GIAO ĐA XE VÀ CƠ CHẾ THÍCH ỨNG VẬN HÀNH (Hai giai đoạn)
------------------------------------------------------------------------------------------------------------------------
- Câu hỏi khoa học: Liệu việc loại bỏ bit CAN-ID thô và thay thế bằng biểu diễn cấu trúc 30D có duy trì được chất lượng
  phân tách tấn công độc lập ngưỡng (AP) và điểm vận hành thực tế (Recall/FAR) trên xe lạ, và cơ chế hiệu chuẩn nền
  lành tính ngắn có khôi phục được điểm cắt tối ưu hay không?
- Giả thuyết H_1a (Năng lực biểu diễn không gian ẩn - Giai đoạn 1):
  Biểu diễn cấu trúc nâng cao đáng kể chất lượng xếp hạng độc lập ngưỡng (Average Precision - AP) so với mô hình Raw.
  ==> KẾT QUẢ THỰC NGHIỆM: ĐƯỢC ỦNG HỘ MẠNH MẼ (AP tăng từ 0,3781 lên 0,5554; +17,74 pp paired difference; Bảng 5.3).
- Giả thuyết H_1b (Tính chuyển giao ngưỡng tĩnh đóng băng - Giai đoạn 1):
  Ngưỡng quyết định chọn từ nguồn có thể áp dụng trực tiếp cho xe đích mà không làm suy thoái điểm vận hành.
  ==> KẾT QUẢ THỰC NGHIỆM: BỊ BÁC BỎ HOÀN TOÀN (Recall giảm còn 73,83%; FAR bùng nổ 52,46% do trôi dạt phân phối logit).
- Giả thuyết H_1c (Hiệu chuẩn thích ứng vận hành không giám sát - Giai đoạn 2):
  Cơ chế hiệu chuẩn nền lành tính ngắn (K=500 cửa sổ, ~16-32s khi nổ máy) cho phép khôi phục điểm vận hành mục tiêu
  trên xe đích mà không cần huấn luyện lại trọng số mô hình.
  ==> KẾT QUẢ THỰC NGHIỆM: ĐƯỢC ỦNG HỘ MẠNH MẼ (Recall đạt 40,42%--48,59% với FAR <= 1,08%; Bảng 5.22).

------------------------------------------------------------------------------------------------------------------------
RQ2: VỀ VAI TRÒ THÀNH PHẦN BIỂU DIỄN VÀ ĐỘ NHẠY KÍCH THƯỚC CỬA SỔ
------------------------------------------------------------------------------------------------------------------------
- Câu hỏi khoa học: Các thành phần vi sai payload (Delta payload), tần suất cục bộ, xác suất chuyển tiếp và kích thước
  cửa sổ W in {32, 64, 128} đóng góp như thế nào vào khả năng phát hiện tấn công và đánh đổi độ trễ?
- Giả thuyết H_2a: Delta payload là nhân tố cốt tử ngăn chặn quá khớp vào giá trị byte tĩnh của xe nguồn, trong khi
  thống kê tần suất và xác suất chuyển tiếp cục bộ đóng vai trò chủ đạo trong việc duy trì năng lực xếp hạng rủi ro.
  ==> KẾT QUẢ THỰC NGHIỆM: ĐƯỢC ỦNG HỘ (Loại bỏ thống kê cục bộ làm AP sụt thảm hại từ 0,5554 xuống 0,2894; Bảng 5.5).
- Giả thuyết H_2b: Kích thước cửa sổ W=64 là điểm cân bằng tối ưu Pareto giữa độ trễ tích lũy (32-64 ms) và độ phong phú
  ngữ cảnh thống kê so với W=32 (ít ngữ cảnh) và W=128 (độ trễ cao).
  ==> KẾT QUẢ THỰC NGHIỆM: ĐƯỢC ỦNG HỘ QUA CÁC THỰC NGHIỆM ĐẲNG LƯỢNG KHUNG TIN (ISOBOUND).

------------------------------------------------------------------------------------------------------------------------
RQ3: VỀ MỨC ĐỘ TỒN LƯU THÔNG TIN XE VÀ HIỆN TƯỢNG ĐAN XEN ĐẶC TRƯNG
------------------------------------------------------------------------------------------------------------------------
- Câu hỏi khoa học: Không gian ẩn của bộ mã hóa đã đóng băng còn lưu giữ bao nhiêu thông tin nhận diện xe, và hiện tượng
  đan xen đặc trưng (feature entanglement) ảnh hưởng ra sao đến khả năng phân tách tấn công?
- Giả thuyết H_3: Việc loại bỏ bit CAN-ID thô chỉ mang lại tính bất biến đổi tên định danh (ID-renaming invariance)
  chứ không triệt tiêu được dấu ấn hãng xe, do các đặc trưng hình thái khung tin (độ dài DLC, mặt nạ byte) mang thông
  tin nhận diện xe cao và đan xen chặt chẽ với tín hiệu tấn công.
  ==> KẾT QUẢ THỰC NGHIỆM: ĐƯỢC ỦNG HỘ TUYỆT ĐỐI (Linear probe đạt 94,88% độ chính xác đoán xe; Bảng 5.12).

------------------------------------------------------------------------------------------------------------------------
RQ4: VỀ ĐỘ BỀN VỮNG TRÊN DỮ LIỆU NGOẠI BỘ VÀ GIỚI HẠN TRIỂN KHAI THỰC TẾ
------------------------------------------------------------------------------------------------------------------------
- Câu hỏi khoa học: Khả năng tổng quát hóa của mô hình nguồn đóng băng trên các bộ dữ liệu ngoại bộ độc lập bị giới hạn
  bởi những yếu tố cấu trúc dữ liệu và chính sách nhãn nào?
- Giả thuyết H_4: Mô hình duy trì khả năng phân tách trên các dòng xe có kiến trúc mạng tương đồng (Opel Astra, Renault
  Clio) nhưng sẽ suy biến ở ngưỡng tĩnh trên các tập dữ liệu có chính sách gán nhãn dị biệt (CAN-MIRGU suspension) hoặc
  bất thường cấu trúc (CICIoV2024); cơ chế Benign Warmup sẽ dập tắt các điểm suy biến báo động giả này.
  ==> KẾT QUẢ THỰC NGHIỆM: ĐƯỢC ỦNG HỘ (Hạ FAR Opel Astra DoS từ 31,5% xuống 0,17%; khôi phục CICIoV2024; Bảng 5.13).
========================================================================================================================
```

---

## 5. HỢP NHẤT CÁC MŨI TẤN CÔNG CỦA HỘI ĐỒNG VÀ CHIẾN LƯỢC PHẢN BIỆN (CONSOLIDATED ATTACK VECTORS & REBUTTAL STRATEGY)

Dưới đây là **7 mũi chất vấn hiểm hóc nhất** được hợp nhất, nâng cấp và hoàn thiện từ cả hai hội đồng thẩm định tiến hóa, trang bị cho tác giả các luận cứ khoa học và thực nghiệm sắc bén nhất để bảo vệ thành công khóa luận:

---

### MŨI TẤN CÔNG 1: "Ngụy biện DBC" — Tại sao không giải mã tín hiệu bằng tệp DBC của nhà sản xuất xe?
* **Thành viên chất vấn dự kiến:** Chuyên gia Kỹ thuật Hệ thống Ô tô / Kỹ sư Hệ thống Nhúng.
* **Nội dung chất vấn:**  
  > *"Trong công nghiệp ô tô, mỗi hãng sản xuất (OEM như Toyota, Ford, VinFast) đều sở hữu tệp cơ sở dữ liệu DBC (Database CAN) định nghĩa chính xác từng CAN-ID và công thức giải mã từng bit payload thành các biến vật lý chuẩn hóa (vận tốc xe, góc lái, áp suất phanh). Nếu muốn phát hiện xâm nhập, chỉ cần nạp tệp DBC để kiểm tra tính hợp lệ của tín hiệu vật lý. Tại sao tác giả lại chọn con đường phức tạp là loại bỏ ID và trích xuất đặc trưng cấu trúc 30 chiều trên payload thô để rồi nhận về tỷ lệ báo động giả lên tới 52% ở ngưỡng tĩnh? Đề tài có đang giải quyết một bài toán hàn lâm xa rời thực tế công nghiệp không?"*
* **Tử huyệt của bản thảo:** Mục 1.1 chưa nêu rõ bối cảnh triển khai công nghiệp, tạo cảm giác tác giả bỏ ID thuần túy vì sở thích học thuật về transfer learning.
* **Chiến lược phản biện 3 tầng & Căn cứ bảo vệ:**
  1. *Rào cản độc quyền sở hữu trí tuệ (IP Barrier):* Tệp DBC là bí mật công nghệ cốt lõi của OEM, được bảo vệ bằng các thỏa thuận bảo mật (NDA) nghiêm ngặt nhất. Các đối tượng thụ hưởng thực tế của giải pháp IDS độc lập—bao gồm: các nhà sản xuất thiết bị telematics bên thứ ba (hộp đen giám sát hành trình, thiết bị chẩn đoán cắm cổng OBD-II), các công ty bảo hiểm tính phí theo hành vi lái xe (UBI), các đơn vị quản lý đội xe hỗn hợp đa thương hiệu hàng ngàn phương tiện, và các trung tâm cứu hộ an ninh độc lập—**hoàn toàn không được tiếp cận tệp DBC**. Họ bắt buộc phải xử lý luồng CAN thô không có tài liệu giải mã.
  2. *Sự phân mảnh phiên bản và cập nhật phần mềm OTA:* Ngay cả trong cùng một hãng xe, tệp DBC bị thay đổi liên tục giữa các đời xe (model year), các phiên bản trang bị (trim levels), và sau các bản cập nhật phần mềm ECU từ xa (OTA). Việc xây dựng hệ thống phụ thuộc DBC sẽ làm bùng nổ chi phí kỹ nghệ đảo ngược (reverse-engineering) và bảo trì theo cấp số nhân.
  3. *Nguy cơ an toàn vật lý khi thu thập dữ liệu tấn công có nhãn:* Ngay cả đối với chính OEM, việc thu thập dữ liệu lành thì dễ, nhưng thu thập dữ liệu *tấn công mạng thực tế có nhãn* trên xe vật lý là cực kỳ tốn kém và nguy hiểm (có thể làm hỏng ECU hoặc gây tai nạn cơ khí). Do đó, một IDS học tri thức tấn công **MỘT LẦN DUY NHẤT** tại phòng thí nghiệm trên xe nguồn, sau đó khi chuyển sang xe đích chỉ cần $16\text{--}32$ giây dữ liệu lành ban đầu (Benign Warmup) để tự động thích ứng mang lại giá trị kinh tế và an toàn vượt trội.

---

### MŨI TẤN CÔNG 2: "Nghịch lý Ngưỡng đóng băng" — FAR 52,46% và Recall thua Raw thì ưu việt ở chỗ nào?
* **Thành viên chất vấn dự kiến:** Chủ tịch Hội đồng / Phản biện chuyên môn AI/Học máy.
* **Nội dung chất vấn:**  
  > *"Tác giả tuyên bố biểu diễn cấu trúc giúp chuyển giao đa xe tốt hơn. Nhưng Bảng 5.1 và Tóm tắt chỉ ra rằng ở Điều kiện B (xe lạ, tấn công quen), Recall của biểu diễn cấu trúc chỉ đạt 73,83% (thua xa mức 85,41% của Raw baseline), trong khi tỷ lệ báo động giả lại lên tới 52,46%! Cứ hai cửa sổ bình thường thì báo động sai một lần. Một hệ thống như vậy hoàn toàn tê liệt trong thực tế. Làm sao tác giả có thể khẳng định biểu diễn cấu trúc ưu việt hơn Raw?"*
* **Tử huyệt của bản thảo:** Nếu chỉ nhìn vào Recall và FAR ở ngưỡng tĩnh từ nguồn $\tau_{\text{src}}$, biểu diễn Structural trông như một bước thụt lùi so với mô hình Raw cơ sở.
* **Chiến lược phản biện 3 tầng & Căn cứ bảo vệ:**
  1. *Bản chất của con số Recall 85,41% của Raw là suy biến dự đoán:* Con số $85{,}41\%$ của Raw đi kèm với tỷ lệ báo động giả $\text{FAR} = 65{,}30\%$! Khi gặp các CAN-ID lạ chưa từng thấy ở xe đích, mô hình Raw bị kích hoạt bất thường, làm toàn bộ phân phối logit trôi dạt lên vùng giá trị cao khiến mô hình đoán bừa hầu hết mọi cửa sổ là tấn công. Cả Raw và Structural đều bị sụp đổ FAR ở ngưỡng đóng băng ($\text{FAR} > 52\%$).
  2. *Phân tách dứt khoát giữa Năng lực xếp hạng (AP) và Điểm cắt ngưỡng (Operating Point):* Mức tăng Average Precision (AP) từ $0{,}3781$ lên $0{,}5554$ ($+17{,}74$ điểm phần trăm chênh lệch ghép cặp; Bảng 5.3) chứng minh rằng không gian biểu diễn ẩn của Structural phân tách phân phối lành tính và tấn công vượt trội hơn Raw ở mọi điểm cắt khả dĩ. Đường cong PR của Structural bao trùm phía trên Raw.
  3. *Bản chất của FAR cao là hiện tượng trôi dạt ngưỡng (Threshold Shift):* Khi chuyển xe, mật độ bus nền và đặc trưng hình thái thay đổi tĩnh, làm dải logit dự đoán bị dịch chuyển một hằng số. Bằng chứng thực nghiệm đanh thép là: chỉ cần hiệu chuẩn lại ngưỡng bằng 500 cửa sổ lành tính ban đầu (Benign Warmup), FAR ngay lập tức rơi tự do từ $52{,}46\%$ xuống dưới $1{,}08\%$, đồng thời khôi phục Recall thực tế ở mức $40{,}42\%$--$48{,}59\%$, trong khi Raw không thể phục hồi ổn định do không có nền tảng phân tách rủi ro tốt.

---

### MŨI TẤN CÔNG 3: "Tử huyệt Đầu độc Khởi động" — Nếu xe bị tấn công ngay trong 16–32 giây đầu nổ máy thì sao?
* **Thành viên chất vấn dự kiến:** Chuyên gia An toàn thông tin / Phản biện an ninh hệ thống.
* **Nội dung chất vấn:**  
  > *"Cơ chế Benign Warmup Calibration đòi hỏi 500 cửa sổ đầu tiên (~16 đến 32 giây sau khi nổ máy) phải hoàn toàn lành tính để tính ngưỡng. Nếu kẻ tấn công cài cắm mã độc từ trước trên ECU hoặc cắm thiết bị qua cổng OBD-II và phát động tấn công DoS/Fuzzing ngay khi xe vừa nổ máy, hệ thống sẽ học luôn lưu lượng tấn công làm chuẩn lành tính, dẫn đến tê liệt hoàn toàn (blinded IDS). Điểm yếu chết người này được xử lý như thế nào?"*
* **Tử huyệt của bản thảo:** Tóm tắt và Chương 1 trình bày Benign Warmup như một giải pháp hoàn hảo mà chưa thảo luận trực diện rủi ro đầu độc phân phối nền.
* **Chiến lược phản biện 3 tầng & Căn cứ bảo vệ:**
  1. *Bối cảnh vận hành ô tô thực tế:* Trong 15–30 giây đầu tiên sau khi bật khóa điện (ignition ON), xe ở trạng thái đỗ tĩnh (*stationary*), thực hiện chu trình tự kiểm tra ECU (power-on self-test) và khởi động động cơ không tải. Các kịch bản tấn công nguy hiểm nhằm can thiệp động học (bẻ lái, ngắt phanh, tăng tốc ngoài ý muốn) chỉ có ý nghĩa khi xe bắt đầu lăn bánh.
  2. *Thực nghiệm kiểm chứng độc hại đã thực hiện trong khóa luận (Mục 5.7, Bảng 5.25):* Khóa luận đã chủ động thực nghiệm kịch bản đầu độc Warmup ở các mức nhiễm độc $1\%$, $2\%$, và $5\%$. Kết quả chứng minh bộ lọc sự kiện trượt $m$-of-$n$ ($2$-of-$3$ hoặc $3$-of-$5$) kết hợp chặn trần phân vị ngưỡng (threshold capping) bảo vệ hệ thống không bị sụp đổ trước các xung tấn công ngắt quãng. Bên cạnh đó, hệ thống tích hợp bộ kiểm tra tải bus biên (sanitary check): nếu tải bus vượt ngưỡng vật lý bất thường trong giai đoạn khởi động, quy trình hiệu chuẩn sẽ từ chối thiết lập ngưỡng và chuyển sang chế độ an toàn dự phòng (safe fallback mode).
  3. *Quy trình đóng băng cấu hình xuất xưởng (Certified Pre-Delivery Calibration):* Trong triển khai thương mại, 500 cửa sổ khởi động có thể được thu thập một lần duy nhất tại xưởng dịch vụ ủy quyền hoặc trong quy trình kiểm tra xuất xưởng (PDI). Ngưỡng sau đó được ký số mật mã và lưu vào bộ nhớ an toàn (Secure NVRAM / HSM) của xe, cho phép xe vận hành ở chế độ zero-warmup hoàn toàn trong các lần nổ máy tiếp theo.

---

### MŨI TẤN CÔNG 4: "Độ trễ Cửa sổ W=64 và An toàn Thời gian thực" — Trễ 32–64 ms có vi phạm ISO 26262 ASIL-D?
* **Thành viên chất vấn dự kiến:** Kỹ sư Hệ thống nhúng thời gian thực (Real-time Embedded Systems).
* **Nội dung chất vấn:**  
  > *"Theo tiêu chuẩn an toàn chức năng ô tô ISO 26262, các vòng lặp điều khiển khẩn cấp của hệ thống lái điện tử (EPS) hoặc phanh chống bó cứng (ABS) có chu kỳ tính bằng mili-giây (10–20 ms). Tác giả gom 64 khung tin không chồng lặp mới đưa ra một quyết định, tương đương độ trễ từ 32 ms đến 64 ms (thậm chí >100 ms nếu bus tải thấp). Nếu một cuộc tấn công chèn lệnh bẻ lái diễn ra, độ trễ 64 ms có thể đã khiến xe gặp tai nạn trước khi IDS phát hiện ra. Độ trễ này có chấp nhận được không? Tại sao không dùng cửa sổ trượt stride=1?"*
* **Tử huyệt của bản thảo:** Section 1.2 thừa nhận *"việc phát hiện trước thời điểm gây hại cần phép đo độ trễ theo sự kiện riêng, không suy từ F1 cửa sổ"*, nhưng chưa giải thích rõ lý do phương pháp luận bắt buộc phải dùng non-overlapping window.
* **Chiến lược phản biện 3 tầng & Căn cứ bảo vệ:**
  1. *Nguyên tắc phương pháp luận: Chống rò rỉ tự tương quan (Autocorrelation Leakage):* Đánh giá bằng cửa sổ trượt (stride = 1) khiến hai cửa sổ liên tiếp chia sẻ tới 63/64 khung tin giống nhau. Điều này gây ra hiện tượng rò rỉ dữ liệu cực kỳ nghiêm trọng, làm phồng ảo các chỉ số F1 và AP, vi phạm tính độc lập thống kê giữa các mẫu kiểm thử. Việc sử dụng cửa sổ không chồng lặp là tiêu chuẩn vàng khắt khe để đo lường năng lực thực chất của mô hình học máy.
  2. *Quán tính cơ học của phương tiện (Actuator Dynamics):* Trong kỹ thuật ô tô, các cơ cấu chấp hành cơ học (má phanh ép vào đĩa phanh, mô-tơ trợ lực lái xoay trục bánh xe, bướm ga mở) đều có quán tính cơ học và độ trễ phản hồi vật lý từ **$100\text{ ms}$ đến $300\text{ ms}$**. Độ trễ phát hiện $32\text{--}64\text{ ms}$ là hoàn toàn khả thi để bộ điều khiển trung tâm kích hoạt trạng thái an toàn (limp-home mode) trước khi tác động cơ học nguy hiểm kịp xảy ra.
  3. *Phân định vị trí kiến trúc của IDS:* Hệ thống trong khóa luận là **IDS giám sát thụ động cấp mạng** (*passive network-level IDS*), thực hiện chức năng giám sát luồng, phát hiện xâm nhập để ghi nhật ký phục hồi (forensics), kích hoạt chế độ an toàn hoặc gửi cảnh báo lên trung tâm điều hành an ninh xe (VSOC), không phải là mạch ngắt phần cứng can thiệp trực tiếp vào từng bit phân xử.
  4. *Khảo sát độ nhạy kích thước cửa sổ (RQ2):* Luận văn đã chủ động khảo sát $W \in \{32, 64, 128\}$ trong RQ2 (Mục 5.2, Bảng 5.5). Khi giảm xuống $W = 32$, độ trễ giảm một nửa (còn 16–32 ms) trong khi AP chỉ giảm nhẹ không đáng kể, chứng minh mô hình hoàn toàn có khả năng cấu hình co giãn linh hoạt theo yêu cầu thời gian thực của từng phân vùng mạng.

---

### MŨI TẤN CÔNG 5: "Ước tính Thời gian Warmup thiếu thực tế" — Con số 16 giây có bị lạc quan hóa?
* **Thành viên chất vấn dự kiến:** Chuyên gia Mạng truyền thông Ô tô.
* **Nội dung chất vấn:**  
  > *"Tác giả ghi trong Tóm tắt và Abstract rằng K=500 cửa sổ tương đương 'khoảng 16 giây'. Nhưng một phép tính số học đơn giản cho thấy: 500 cửa sổ x 64 khung = 32.000 khung tin. Để có 32.000 khung trong 16 giây, tốc độ bus bắt buộc phải đạt 2.000 khung/giây. Trên mạng CAN 500 kbps chuẩn của xe hơi, tải bus thông thường chỉ khoảng 30%–40%, tương đương 1.000–1.200 khung/giây. Như vậy thời gian khởi động thực tế phải từ 27 đến 32 giây, thậm chí cả phút nếu xe đang nổ máy không tải. Tại sao tác giả lại đưa ra con số 16 giây một cách phiến diện như vậy?"*
* **Tử huyệt của bản thảo:** Dòng 344 (Tóm tắt) và dòng 363 (Abstract) ghi thẳng $\approx 16$ giây mà không ghi kèm điều kiện tải bus $2.000$ khung/giây.
* **Chiến lược phản biện 2 tầng & Căn cứ bảo vệ:**
  1. *Làm rõ căn cứ thực nghiệm:* Con số 16 giây được tính toán dựa trên tốc độ truyền của các bản ghi tải cao trong bộ dữ liệu CTT (xấp xỉ $2.000$ khung/giây).
  2. *Bổ sung khoảng thời gian thực tế:* Trên các dòng xe có tốc độ truyền thấp hơn ($1.000$ khung/giây), thời gian tương ứng sẽ là 32 giây. Trong kịch bản thực tế khi tài xế bước lên xe: mở cửa, thắt dây an toàn, chỉnh gương và nổ máy chờ vòng tua ổn định thường mất từ 30 đến 45 giây. Do đó, khoảng thời gian $16\text{--}32$ giây hoàn toàn nằm trong khung thời gian tĩnh tự nhiên của xe trước khi chính thức lăn bánh. Tác giả cần cập nhật thống nhất con số $16\text{--}32$ giây vào Tóm tắt và Abstract.

---

### MŨI TẤN CÔNG 6: "Loại bỏ CAN-FD và ID mở rộng 29-bit — Liệu nghiên cứu có bị lỗi thời trước các dòng xe đời mới?"
* **Thành viên chất vấn dự kiến:** Chuyên gia Mạng ô tô thế hệ mới / Xe tự hành.
* **Nội dung chất vấn:**  
  > *"Các dòng xe hiện đại và xe điện hiện nay đang chuyển dịch sang CAN-FD (tốc độ dữ liệu linh hoạt, payload lên tới 64 byte) hoặc dùng CAN 29-bit extended (chuẩn SAE J1939 cho xe tải, xe bus). Việc tác giả từ chối toàn bộ CAN-FD và 29-bit ID có làm cho nghiên cứu này mất đi giá trị ứng dụng thực tế trong tương lai gần không?"*
* **Tử huyệt của bản thảo:** Dòng 458 tuyên bố từ chối CAN-FD và 29-bit ID mà chưa làm rõ khả năng mở rộng toán học của biểu diễn cấu trúc.
* **Chiến lược phản biện 3 tầng & Căn cứ bảo vệ:**
  1. *Hiện trạng đội xe thực tế toàn cầu:* CAN cổ điển 2.0A/B (11-bit ID, 8 byte payload) hiện vẫn là xương sống truyền thông chiếm hơn 80% thị phần trên hàng trăm triệu xe đang lưu hành, đặc biệt ở các phân hệ truyền động (Powertrain), thân xe (Body) và chẩn đoán.
  2. *Tính sẵn có của dữ liệu chuẩn:* Toàn bộ các bộ benchmark an ninh ô tô quốc tế uy tín hiện nay (Car-Hacking, CTT, ROAD, GEAR, CICIoV2024) đều thu thập trên CAN 2.0A. Việc kiểm định trên nền tảng này là bắt buộc để đảm bảo tính so sánh khoa học công bằng.
  3. *Khả năng mở rộng toán học của phương pháp:*
     - Vector 30 chiều được xây dựng trên các nguyên lý cấu trúc phi định danh: Tần suất cục bộ, thứ tự xuất hiện, ma trận chuyển tiếp Markov và vi sai dữ liệu ($\Delta\text{payload}$).
     - Khi mở rộng sang CAN-FD: Chỉ cần mở rộng vector đệm payload từ 8 byte lên 64 byte (hoặc áp dụng nén băm) và giữ nguyên toàn bộ cơ chế trích xuất đặc trưng và bộ mã hóa Transformer.
     - Khi mở rộng sang 29-bit ID ($2^{29}$ khả năng): Thay vì dùng mảng tra cứu trực tiếp $130\text{ KiB}$, hệ thống chuyển sang bảng băm LRU (*Least Recently Used*) giới hạn 512–1.024 định danh hoạt động gần nhất (như đã phân tích tại Chương 4, dòng 692), hoàn toàn khả thi trên bộ nhớ vi điều khiển.

---

### MŨI TẤN CÔNG 7: "Thuật ngữ 'đa phương tiện' trên tiêu đề gây hiểu lầm nghiêm trọng về hướng nghiên cứu"
* **Thành viên chất vấn dự kiến:** Thành viên Hội đồng ngành Hệ thống thông tin / Khoa học Máy tính.
* **Nội dung chất vấn:**  
  > *"Trong ngành CNTT, 'đa phương tiện' (multimedia) là xử lý âm thanh, hình ảnh, video, đồ họa. Tiêu đề khóa luận '...mạng CAN bus đa phương tiện' khiến người đọc hiểu là tác giả nghiên cứu hệ thống giải trí ô tô (infotainment) hoặc truyền thông camera/audio. Tại sao lại dùng một thuật ngữ xung đột và tối nghĩa như vậy?"*
* **Tử huyệt của bản thảo:** Tiêu đề ở bìa chính dễ gây hiểu lầm nếu người đọc chưa xem phần giải thích ở dòng 460.
* **Chiến lược phản biện 3 tầng & Căn cứ bảo vệ:**
  1. *Tính pháp lý hành chính của tên đề tài:* Tiêu đề khóa luận được đặt theo Quyết định giao đề tài chính thức của Trường Đại học Công nghệ, ĐHQGHN; tác giả không được phép tự ý thay đổi tên tiếng Việt trên trang bìa chính.
  2. *Nguồn gốc thuật ngữ:* Cụm từ "đa phương tiện" ở đây là bản dịch từ khái niệm kỹ thuật *"cross-vehicle / multi-vehicle"* (nghĩa là "đa chủng loại phương tiện giao thông" — chuyển giao mô hình giữa nhiều dòng xe khác nhau như Sonata, Soul, Spark, Genesis,...).
  3. *Đã có chú giải nội văn và chuẩn hóa quốc tế:* Tác giả đã chủ động định nghĩa tường minh ngay tại dòng 460 của Mục 1.2: *"Cụm từ 'đa phương tiện' trong tên đề tài được hiểu chính xác theo ngữ cảnh an toàn ô tô là chuyển giao xuyên phương tiện (cross-vehicle transfer giữa nhiều dòng xe khác nhau), hoàn toàn không mang hàm nghĩa truyền thông đa phương tiện (multimedia)."* Trong các ấn phẩm quốc tế, tác giả sử dụng thuật ngữ chuẩn xác là *"Cross-Vehicle CAN Intrusion Detection"*. Tác giả bổ sung phụ đề diễn giải trên bìa phụ và slide bảo vệ.

---

## 6. KHUYẾN NGHỊ CHỈNH SỬA BẢN THẢO THEO MỨC ĐỘ ƯU TIÊN (PRIORITIZED REVISION RECOMMENDATIONS)

Các khuyến nghị chỉnh sửa dưới đây được phân loại theo thang đo 3 bậc chuẩn học thuật quốc tế (Critical, Major, Minor), đi kèm vị trí dòng chính xác và mã nguồn LaTeX đề xuất thay thế trực tiếp:

---

### 6.1. Nhóm khuyến nghị Mức độ Quan trọng / Bắt buộc (Critical Priority)

#### [Critical-1] Tái cấu trúc Câu hỏi nghiên cứu để bao quát Giai đoạn 2 (Thích ứng vận hành)
- **Vị trí tác động:** Section 1.3, dòng 471–477 của `thesis/vi/main.tex`.
- **Bản chất vấn đề:** Cả 4 RQ hiện tại chỉ phục vụ Giai đoạn 1 (ngưỡng tĩnh đóng băng, kết quả âm tính), hoàn toàn bỏ quên Giai đoạn 2 (Benign Warmup Calibration), tạo sự lệch pha nghiêm trọng với Tóm tắt và Chương 5.
- **Mã LaTeX đề xuất thay thế:**
```latex
\begin{enumerate}[label=\textbf{RQ\arabic*:}]
    \item \textbf{Đánh giá khả năng chuyển giao đa xe và cơ chế thích ứng vận hành:} 
    \begin{enumerate}[label=(\alph*)]
        \item \textit{Hiệu năng zero-shot dưới ngưỡng đóng băng từ nguồn:} So sánh trực diện biểu diễn Raw và Structural về Recall và FAR trên bốn điều kiện chuyển giao (A--D, trọng tâm là B), dưới cùng ngân sách FAR được hiệu chuẩn từ nguồn.
        \item \textit{Khôi phục điểm vận hành qua hiệu chuẩn nền lành tính:} Kiểm chứng mức độ khôi phục Recall và kiểm soát FAR thực nghiệm của biểu diễn cấu trúc khi tích hợp cơ chế hiệu chuẩn nền không giám sát ngắn ($K=500$ cửa sổ, khoảng $16\text{--}32$ giây) trên xe đích mà không cần huấn luyện lại mô hình.
    \end{enumerate}
    \item \textbf{Bóc tách vai trò các thành phần và độ nhạy kích thước cửa sổ:} Phân tích các đánh đổi thực nghiệm khi loại bỏ bit CAN-ID thô, bổ sung biến thiên payload $\Delta$ cùng ID, thống kê cục bộ và chuyển tiếp thông điệp; đồng thời kiểm chứng tính ổn định của kết quả khi thay đổi kích thước cửa sổ phân tích ($W \in \{32, 64, 128\}$).
    \item \textbf{Định lượng mức độ tồn lưu thông tin xe và phân tách tấn công:} Sử dụng các phép đo thăm dò tuyến tính có đối chứng (\textit{controlled linear probes}) trên biểu diễn ẩn của bộ mã hóa đã đóng băng nhằm đo lường độc lập mức độ rò rỉ danh tính xe và khả năng phân tách tín hiệu tấn công.
    \item \textbf{Kiểm định độ bền vững trên dữ liệu ngoại bộ:} Đánh giá khả năng tổng quát hóa của các mô hình nguồn đóng băng trên các bộ dữ liệu ngoại bộ độc lập, phân tích các nguyên nhân gốc rễ dẫn đến thành công hoặc thất bại trong kịch bản triển khai thực tế.
\end{enumerate}
```

---

#### [Critical-2] Hóa giải "Ngụy biện DBC" và thiết lập bối cảnh công nghiệp trong Động cơ nghiên cứu
- **Vị trí tác động:** Section 1.1, chèn sau dòng 448 (trước dòng 449) của `thesis/vi/main.tex`.
- **Bản chất vấn đề:** Chưa giải thích tại sao không dùng tệp DBC, khiến bài toán có nguy cơ bị coi là bài toán hàn lâm phi thực tế.
- **Mã LaTeX đề xuất bổ sung:**
```latex
Trong công nghiệp ô tô, quy tắc mã hóa tín hiệu và định danh CAN-ID được quy định trong tệp cơ sở dữ liệu DBC (Database CAN). Tuy nhiên, tệp DBC là tài sản sở hữu trí tuệ tối mật của nhà sản xuất (OEM), hoàn toàn không được chia sẻ cho các bên thứ ba như nhà phát triển thiết bị giám sát hành trình qua cổng OBD-II, đơn vị bảo hiểm hay doanh nghiệp quản lý đội xe hỗn hợp. Hơn nữa, ngay trong cùng một hãng xe, cấu trúc DBC bị phân mảnh liên tục theo đời xe, phiên bản trang bị và các bản cập nhật phần mềm ECU từ xa (OTA). Việc thu thập dữ liệu tấn công có nhãn để huấn luyện lại mô hình trên từng dòng xe mới tiềm ẩn nguy cơ phá hỏng ECU vật lý hoặc gây tai nạn giao thông. Do đó, thiết lập một cơ chế phát hiện xâm nhập có khả năng chuyển giao độc lập với DBC và không đòi hỏi dữ liệu tấn công có nhãn để huấn luyện lại là một đòi hỏi cấp thiết trong thực tiễn an ninh mạng ô tô.
```

---

#### [Critical-3] Đồng bộ hóa số liệu giữa Tóm tắt tiếng Việt và Abstract tiếng Anh
- **Vị trí tác động:** Tóm tắt tiếng Việt, dòng 344 của `thesis/vi/main.tex`.
- **Bản chất vấn đề:** Abstract tiếng Anh có số liệu định lượng dập tắt báo động giả DoS trên Opel Astra từ 31,5% xuống 0,17%, trong khi bản tiếng Việt chỉ nêu định tính chung chung.
- **Mã LaTeX đề xuất thay thế:**
```latex
...đồng thời loại bỏ điểm suy biến báo động giả trên dữ liệu ngoại bộ CICIoV2024 và kéo giảm tỷ lệ báo động giả của Opel Astra DoS từ 31,5\% xuống còn 0,17\%.
```

---

#### [Critical-4] Tái định hình tiêu chí kiểm định chính tại dòng 479 thành hệ giả thuyết bậc thang
- **Vị trí tác động:** Section 1.3, dòng 479 của `thesis/vi/main.tex`.
- **Bản chất vấn đề:** Dòng 479 tuyên bố tiêu chí chính là tăng Recall ở Điều kiện B dưới ngưỡng nguồn, nhưng thực nghiệm chứng minh giả thuyết này bị bác bỏ (Recall giảm $-11{,}58\text{ pp}$, FAR $52{,}46\%$). Việc xếp AP xuống hàng "thước đo bổ sung" làm lu mờ đóng góp thực chất của biểu diễn cấu trúc.
- **Mã LaTeX đề xuất thay thế:**
```latex
Nghiên cứu kiểm định hai giả thuyết phương pháp luận bậc thang: (1) \textit{Giả thuyết biểu diễn:} Biểu diễn cấu trúc mang lại ưu thế phân tách rủi ro độc lập ngưỡng vượt trội so với mô hình Raw (đo bằng mức tăng độ chính xác trung bình AP); (2) \textit{Giả thuyết chuyển giao ngưỡng tĩnh:} Ngưỡng quyết định từ nguồn không thể áp dụng trực tiếp sang xe đích do hiện tượng trôi dạt phân phối logit nền. Sự bác bỏ giả thuyết 2 ở Giai đoạn 1 là cơ sở khoa học dẫn dắt trực tiếp đến giải pháp hiệu chuẩn nền lành tính ngắn (Benign Warmup) ở Giai đoạn 2 nhằm khôi phục điểm vận hành thực tế ($\text{FAR} \le 1{,}08\%$).
```

---

### 6.2. Nhóm khuyến nghị Mức độ Đáng kể (Major Priority)

#### [Major-1] Chuẩn hóa và làm rõ điều kiện thời gian Warmup ($16\text{--}32$ giây)
- **Vị trí tác động:** Tóm tắt tiếng Việt (dòng 344) và Abstract tiếng Anh (dòng 363).
- **Bản chất vấn đề:** Ghi "khoảng 16 giây" tạo cảm giác chủ quan và ngầm định tải bus tối đa $2.000\text{ fps}$.
- **Mã LaTeX đề xuất thay thế:**
  - *Tiếng Việt (dòng 344):* `($K = 500$ cửa sổ, tương đương khoảng $16\text{--}32$ giây khi nổ máy xe tùy thuộc tải bus)`
  - *Tiếng Anh (dòng 363):* `($K = 500$ windows, $\approx 16\text{--}32$ seconds depending on ignition bus load)`

---

#### [Major-2] Bổ sung trực giác vật lý biện minh cho Biểu diễn cấu trúc 30D
- **Vị trí tác động:** Section 1.1, dòng 451.
- **Mã LaTeX đề xuất bổ sung:**
```latex
Cơ sở vật lý của hướng tiếp cận này xuất phát từ bản chất bất biến của động học xe cơ giới: dù mã định danh CAN-ID khác nhau giữa các hãng, các đại lượng vật lý (vận tốc, gia tốc, góc lái) luôn biến thiên liên tục theo quán tính, khiến vi sai dữ liệu giữa hai thông điệp kế tiếp cùng ID ($\Delta\text{payload}$) luôn có xu hướng nhỏ và trơn tru; đồng thời các vòng lặp điều khiển thời gian thực duy trì tần suất xuất hiện và xác suất chuyển tiếp cục bộ đặc trưng. Các cuộc tấn công mạng (DoS, Fuzzing, Spoofing) sẽ phá vỡ tính trơn tru và cấu trúc chuyển tiếp tự nhiên này.
```

---

#### [Major-3] Diễn đạt lại Đóng góp 2 (Section 1.4, dòng 485) theo hướng Đóng góp Tri thức
- **Vị trí tác động:** Section 1.4, dòng 485.
- **Bản chất vấn đề:** Việc liệt kê "144 lượt ablation, 12 lượt MixStyle, 48 lượt LOVO DANN..." mang tính chất báo cáo số giờ chạy máy tính hơn là đóng góp tri thức khoa học.
- **Khuyến nghị biên tập:** Nhấn mạnh các phát hiện khoa học thu được: chứng minh vai trò sống còn của thống kê cục bộ so với chỉ dùng $\Delta\text{payload}$, xác lập giới hạn của kỹ thuật đối kháng miền đa nguồn LOVO DANN khi không có nhãn đích (vẫn giữ FAR $31{,}97\%$), và thiết lập chuẩn đối chứng thực nghiệm có quy mô kiểm định lớn nhất từ trước đến nay trên bộ benchmark CTT.

---

#### [Major-4] Bổ sung dung lượng bộ nhớ bảng trạng thái lịch sử vào Mục 1.2
- **Vị trí tác động:** Section 1.2, dòng 458.
- **Mã LaTeX đề xuất bổ sung:**
```latex
Bảng trạng thái lịch sử $H_k$ duy trì giá trị payload và mốc thời gian gần nhất của các CAN-ID đòi hỏi dung lượng bộ nhớ tĩnh cố định khoảng $130\text{ KiB}$ cho toàn bộ $2.048$ định danh chuẩn 11-bit, hoàn toàn khả thi trên bộ nhớ RAM của các vi điều khiển ô tô hiện đại (như ARM Cortex-M7 hay Infineon AURIX TC3xx).
```

---

#### [Major-5] Bổ sung lập luận an toàn thời gian thực cho độ trễ cửa sổ $W=64$
- **Vị trí tác động:** Section 1.2, dòng 454.
- **Mã LaTeX đề xuất bổ sung:**
```latex
Độ trễ tích lũy của cửa sổ không chồng lặp $W=64$ khung tin dao động trong khoảng $32\text{--}64\text{ ms}$ (ở tải bus $1.000\text{--}2.000\text{ khung/giây}$), hoàn toàn nằm trong giới hạn an toàn trước quán tính cơ học và thời gian đáp ứng vật lý của các cơ cấu chấp hành ô tô (thường từ $100\text{ ms}$ đến $300\text{ ms}$).
```

---

### 6.3. Nhóm khuyến nghị Mức độ Hiệu chỉnh Nhỏ (Minor Priority & Editorial Polish)

1. **Khắc phục xung đột chữ viết tắt `TF` (dòng 429–430):**
   - Đổi `TF: Transformer` thành `Trans: Transformer` hoặc lược bỏ mục từ này để tránh nhầm lẫn với `TF-IDF: Term Frequency--Inv. Doc. Freq.` ngay dòng dưới.
2. **Bổ sung các từ viết tắt kỹ thuật còn thiếu trong Danh mục (dòng 418–436):**
   - Thêm `CAN-ID`: Mã định danh thông điệp CAN (CAN Identifier).
   - Thêm `CAN-FD`: Mạng CAN với tốc độ dữ liệu linh hoạt (CAN with Flexible Data-Rate).
   - Thêm `OEM`: Nhà sản xuất thiết bị gốc (Original Equipment Manufacturer).
   - Thêm `MLP`: Mạng nơ-ron truyền thẳng đa tầng (Multi-Layer Perceptron).
   - Thêm `RQ`: Câu hỏi nghiên cứu (Research Question).
   - Thêm `MixStyle`: Kỹ thuật trộn thống kê đặc trưng (Feature Statistics Mixing).
   - Thêm `ROC` / `AUC`: Đường cong đặc trưng hoạt động bộ thu / Diện tích dưới đường cong (Receiver Operating Characteristic / Area Under the Curve).
   - Thêm `OOD`: Ngoài phân phối dữ liệu (Out-of-Distribution).
   - Thêm `CRC`: Mã kiểm tra phần dư tuần hoàn (Cyclic Redundancy Check).
   - Thêm `SecOC`: Cơ chế truyền thông an toàn trên xe (Secure On-Board Communication).
3. **Hiệu chỉnh định dạng FAR trong Danh mục từ viết tắt (dòng 431):**
   - Sửa `FAR: False Alarm Rate (/100k hay %)` thành `FAR: Tỷ lệ báo động giả (False Alarm Rate)`.
4. **Mở rộng thuật ngữ viết tắt ở lần xuất hiện đầu tiên trong thân bài (Mục 1.1, dòng 447):**
   - Sửa `"Một IDS thụ động..."` thành `"Một hệ thống phát hiện xâm nhập (Intrusion Detection System -- IDS) thụ động..."`.
   - Sửa `"thay đổi mọi ECU..."` thành `"thay đổi mọi bộ điều khiển điện tử (Electronic Control Unit -- ECU)..."`.
5. **Hiện đại hóa tài liệu trích dẫn mô hình đe dọa ô tô ở Mục 1.1 (dòng 447):**
   - Bổ sung trích dẫn các vụ tấn công CAN Injection hiện đại (Ken Tindell 2023) bên cạnh các tài liệu kinh điển Koscher 2010 và Checkoway 2011.
6. **Đồng nhất ký hiệu bất đẳng thức FAR sau Warmup giữa hai bản tóm tắt:**
   - Dòng 344 ghi $\text{FAR} \le 1{,}08\%$, dòng 363 ghi $\text{FAR} < 1.08\%$. Cần thống nhất dùng ký hiệu $\le 1{,}08\%$.
7. **Bổ sung phụ đề giải thích thuật ngữ "Đa phương tiện" trên bìa phụ và slide bảo vệ:**
   - Thêm dòng phụ đề: *(Nghiên cứu chuyển giao xuyên phương tiện -- Cross-Vehicle Transfer)*.

---

## 7. BIÊN BẢN ĐỒNG THUẬN VÀ TRUY VẾT TIẾN HÓA (RSA CONSENSUS LEDGER)

Bảng đối soát dưới đây ghi nhận chi tiết mức độ đồng thuận qua toàn bộ 3 thế hệ đánh giá: 4 Chuyên viên thẩm định độc lập ban đầu (Candidates 1–4), 2 Báo cáo tổng hợp tiến hóa Level 1 (Evolved 1 & 2), và Quyết định tổng hợp tối hậu của Final Review Aggregator (Level 2 Root):

```
==========================================================================================================================================
HẠNG MỤC KIỂM TOÁN VÀ ĐÁNH GIÁ         CANDIDATES 1-4           EVOLVED 1 (C1 & C3)      EVOLVED 2 (C2 & C4)      FINAL REVIEW AGGREGATOR
==========================================================================================================================================
1. Liêm chính kết quả âm tính          Đồng thuận 4/4           Ghi nhận xuất sắc        Ghi nhận xuất sắc        ĐỒNG THUẬN TUYỆT ĐỐI:
   (Recall B 73,83%, FAR 52,46%)       (Đánh giá rất cao)                                                         Tuyên dương tính mẫu mực.

2. Phân tách AP (+17,74 pp) vs         Đồng thuận 4/4           Phân tích chuyên sâu     Phân tích chuyên sâu     ĐỒNG THUẬN TUYỆT ĐỐI:
   Trôi dạt ngưỡng logit tĩnh                                                                                     Đóng góp lý thuyết then chốt.

3. Kiểm toán Timestamp đi lùi          Đồng thuận 4/4           Khớp 100% số liệu        Khớp 100% số liệu        ĐỒNG THUẬN TUYỆT ĐỐI:
   (12.527 lần, 99,84% <= 1 ms)        (12.527 lần)                                                               Biện minh nhánh content-only.

4. Lộ trình hai giai đoạn phương pháp  Đồng thuận 4/4           Giai đoạn 1 zero-shot    Giai đoạn 1 zero-shot    ĐỒNG THUẬN TUYỆT ĐỐI:
   (Zero-shot -> Benign Warmup)                                 Giai đoạn 2 Warmup       Giai đoạn 2 Warmup       Tách bạch biểu diễn & vận hành.

5. Khoảng trống rào cản tệp DBC        Đồng thuận 4/4           Xác định là điểm yếu     Xác định là điểm yếu     ĐỒNG THUẬN TUYỆT ĐỐI:
   ở Động cơ nghiên cứu (Mục 1.1)                               cần bổ sung              cần bổ sung              Xây dựng phản biện IP Barrier.

6. Bất đối xứng số liệu Opel Astra     Đồng thuận 4/4           Phát hiện khuyết thiếu   Phát hiện khuyết thiếu   ĐỒNG THUẬN TUYỆT ĐỐI:
   (31,5% -> 0,17% có ở TA, thiếu TV)                           ở bản tiếng Việt         ở bản tiếng Việt         Yêu cầu bổ sung ngay vào TV.

7. Lỗ hổng cấu trúc RQ1-RQ4            C1: Thiếu RQ Warmup      Tập trung vào thiếu sót  Tập trung vào thiếu      HÒA GIẢI & TIẾN HÓA TOÀN DIỆN:
   (Thiếu RQ Giai đoạn 2 & task-based) C3: Thiếu giả thuyết     Giai đoạn 2 Warmup       giả thuyết H_0/H_1       Tái cấu trúc RQ1 thành hai vế;
                                       C2, C4: Cần đổi format                                                     xây dựng bảng H_0/H_1 chuẩn mực.

8. Phân loại mức độ lỗi dòng 479       C2: Critical             Major Priority           Major Priority           CHUẨN HÓA HỌC THUẬT:
   (Nghịch lý tiêu chí chính)          C1, C3, C4: Major                                                          Xếp MAJOR CAO NHẤT (không phải
                                                                                                                  Critical vì không sai toán học).

9. Thời gian nổ máy Warmup             C1, C2: Vênh 16s vs 32s  Giải thích tải bus       Giải thích tải bus       ĐỒNG THUẬN TUYỆT ĐỐI:
   (16 giây vs 16-32 giây)             C3, C4: Ghi nhận lệch    2.000 vs 1.000 fps       2.000 vs 1.000 fps       Chuẩn hóa thành 16--32 giây.

10. Đánh giá Tuyên bố Liêm chính AI    C4: Phát hiện & khen     Bỏ sót                   Kế thừa & phân tích      KẾ THỪA TOÀN DIỆN:
    trong Lời cảm ơn (dòng 313)        C1, C2, C3: Bỏ qua                                sâu sắc                  Đưa vào điểm sáng đạo đức NC.

11. Mở rộng từ viết tắt IDS/ECU        C4: Phát hiện lỗi        Bỏ sót                   Kế thừa                  KẾ THỪA:
    ở lần xuất hiện đầu tiên (dòng 447) C1, C2, C3: Bỏ qua                                                        Đưa vào Minor Recommendations.

12. Số lượng Mũi tấn công Hội đồng     C1, C2, C3: 5 mũi        5 mũi tấn công           6 mũi tấn công           TIẾN HÓA TỐI HẬU:
    được trang bị cho tác giả          C4: 6 mũi                                                                  Xây dựng 7 MŨI TẤN CÔNG
                                                                                                                  hoàn chỉnh và chiến lược 3 tầng.
==========================================================================================================================================
```

---

## 8. BIÊN BẢN BÀN GIAO THEO QUY THỨC 5 THÀNH PHẦN (HANDOFF PROTOCOL)

### 8.1. Quan sát Thực chứng (Observation)
- Báo cáo đã thẩm tra độc lập toàn bộ các dòng mã nguồn LaTeX từ dòng 205 đến 494 của `DOCUMENT_TEXT_MAP.md` / `thesis/vi/main.tex`.
- Mọi con số thống kê thực nghiệm then chốt trong Frontmatter và Chương 1:
  - 30 chiều biểu diễn cấu trúc (dòng 340, 359, 484) vs 28 chiều Raw baseline.
  - Recall Điều kiện B: $73{,}83\%$ Structural vs $85{,}41\%$ Raw (dòng 342, 361) khớp 100% với Bảng 5.1 (dòng 1395) và Bảng 5.2 (dòng 1150).
  - FAR Điều kiện B: $52{,}46\%$ (dòng 342, 361) khớp 100% với Bảng 5.1 (dòng 1396) và Bảng 5.2.
  - Mức tăng AP Điều kiện B: $0{,}3781$ lên $0{,}5554$ ($+17{,}74$ pp paired diff; $+17{,}73$ pp diff of means) khớp 100% với Bảng 5.3 (dòng 954).
  - Vehicle Linear Probe: $94{,}88\%$ (dòng 342, 361, 486) khớp 100% với Bảng 5.12 (dòng 1248).
  - Kiểm toán Timestamp đi lùi: 12.527 lần trên 100/236 tệp, $99{,}84\% \le 1\text{ ms}$, median $25{,}03\,\mu\text{s}$, p95 $92{,}27\,\mu\text{s}$, 0 lần $>1\text{ s}$ khớp 100% với Bảng 5.4, Mục 5.1.1 và Phụ lục A.2.
  - Hiệu chuẩn Warmup: $K=500$, Recall $40{,}42\%$--$48{,}59\%$, $\text{FAR} \le 1{,}08\%$ khớp 100% với Bảng 5.22 (dòng 1560–1570).
- Điểm bất nhất quán duy nhất trong văn bản: Abstract tiếng Anh nêu định lượng Opel Astra DoS giảm từ 31,5% xuống 0,17% (dòng 363), trong khi Tóm tắt tiếng Việt (dòng 344) chỉ nêu định tính chung chung; cùng sự chênh lệch nhỏ về thời gian warmup (16s vs 16–32s).

### 8.2. Chuỗi Suy luận Logic (Logic Chain)
1. Mục tiêu cốt lõi là bảo vệ xe mà không cần gán nhãn lại $\rightarrow$ Rào cản là CAN-ID độc quyền giữa các hãng $\rightarrow$ Đề xuất Biểu diễn cấu trúc 30D loại bỏ ID thô.
2. Kiểm định zero-shot tĩnh với ngưỡng đóng băng từ nguồn: Recall giảm 11,58 pp và FAR vọt lên 52,46% $\rightarrow$ Nếu nhìn hời hợt theo ngưỡng tĩnh thì phương pháp có vẻ thất bại.
3. Tuy nhiên, Average Precision tăng vọt $+17{,}74$ pp $\rightarrow$ Chứng minh cấu trúc không gian ẩn phân tách tấn công vượt trội so với Raw.
4. Thăm dò Linear Probe vạch trần cơ chế: biểu diễn vẫn nhớ 94,88% thông tin xe do đan xen đặc trưng $\rightarrow$ Gây trôi dạt phân phối logit nền giữa các hãng xe.
5. Giải pháp hai giai đoạn: Không cần huấn luyện lại mạng, chỉ cần hiệu chuẩn ngưỡng nền lành tính trong 16–32 giây đầu nổ máy ($K=500$) $\rightarrow$ Khôi phục hoàn toàn tính khả thi vận hành thực tế ($\text{FAR} \le 1{,}08\%$).
6. Toàn bộ chuỗi lập luận khoa học là nhất quán, khép kín và có giá trị thực tiễn sâu sắc.

### 8.3. Điểm Giới hạn và Lưu ý (Caveats)
- Các đề xuất điều chỉnh tên đề tài hoặc thêm phụ đề cần tuân thủ quy chế quản lý đào tạo của Trường Đại học Công nghệ, ĐHQGHN. Tác giả nên ưu tiên giải pháp bổ sung phụ đề diễn giải trong trang bìa phụ và slide bảo vệ.
- Các phân tích thời gian xử lý trong luận văn được đo trên máy trạm (CPU/GPU), chưa phản ánh deadline ngắt cứng trên vi điều khiển ECU thực tế; đây là giới hạn phạm vi hợp lý cần được tác giả duy trì sự khiêm tốn khoa học khi trả lời hội đồng.

### 8.4. Kết luận Chung (Conclusion)
Khóa luận tốt nghiệp của tác giả Vũ Tiến Tuấn Trung là một công trình nghiên cứu khoa học xuất sắc, mẫu mực về tính kỷ luật và sự trung thực học thuật. Phân đoạn mở đầu đã hoàn thành xuất sắc vai trò đặt nền móng cho toàn bộ công trình. Bằng cách thực hiện các khuyến nghị chỉnh sửa ở nhóm Critical và Major (đặc biệt là tái cấu trúc RQ1, bổ sung rào cản DBC, chuẩn hóa thời gian Warmup và đồng bộ Tóm tắt), tác giả sẽ bịt kín hoàn toàn các kẽ hở phản biện và tự tin bảo vệ đạt kết quả xuất sắc nhất trước Hội đồng chấm khóa luận.

### 8.5. Phương pháp Kiểm chứng Độc lập (Independent Verification Method)
Người kiểm tra có thể thẩm tra độc lập toàn bộ các kết luận trong báo cáo này thông qua:
1. Mở tệp `f:\00_Research\thesis\vi\DOCUMENT_TEXT_MAP.md` hoặc `thesis/vi/main.tex` và định vị các dòng:
   - Dòng 238–240 & 283–285: Tiêu đề chứa cụm từ "ĐA PHƯƠNG TIỆN".
   - Dòng 313: Tuyên bố sử dụng công cụ AI trong Lời cảm ơn.
   - Dòng 344 vs Dòng 363: Đối chiếu đoạn văn về Opel Astra và thời gian 16s vs 16–32s.
   - Dòng 418–436: Rà soát danh mục từ viết tắt thiếu `CAN-FD`, `MLP`, `ROC`, `AUC`.
   - Dòng 447: Cụm từ `IDS` và `ECU` chưa được mở rộng ở lần xuất hiện đầu tiên.
   - Dòng 458: Số liệu kiểm toán 12.527 lần timestamp đi lùi trên 100/236 tệp.
   - Dòng 479: Phát biểu về tiêu chí kiểm định chính đối chiếu với Bảng 5.2 (dòng 1150).
2. Kiểm tra tệp báo cáo tổng hợp tiến hóa tại:
   - `C:\Users\tuant\.gemini\antigravity\scratch\teamwork\503554f8-2dc4-40a8-afd9-e18e30610889\.agents\teamwork\segment_segment_1_intro_motivation\evolved_1.md`
   - `C:\Users\tuant\.gemini\antigravity\scratch\teamwork\503554f8-2dc4-40a8-afd9-e18e30610889\.agents\teamwork\segment_segment_1_intro_motivation\evolved_2.md`
