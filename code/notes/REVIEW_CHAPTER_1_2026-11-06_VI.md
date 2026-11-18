# Rà soát Chương 1 — Mở đầu

**Cập nhật 06/11/2026:** Theo yêu cầu của tác giả, các đề xuất về khoảng trống nghiên cứu, phạm vi chỉ dùng dữ liệu nguồn, câu hỏi, giả thuyết và trạng thái đóng góp đã được áp dụng vào Chương 1 tiếng Việt và bản dịch tiếng Anh. Cách diễn giải nhãn suspension được đồng bộ tại tóm tắt và định nghĩa nhãn cửa sổ. Phần dưới giữ nguyên nội dung đánh giá trước khi sửa để lưu dấu vết quyết định; kết quả mô hình v2 vẫn chưa có.

Ngày rà soát: 06/11/2026. Bản nguồn tại thời điểm rà soát: `thesis/vi/main.tex`, dòng 120–156. Phần dưới ghi nhận đánh giá trước khi sửa; trạng thái áp dụng được nêu ở đầu tài liệu. Không có rubric chính thức của khoa nên không gán điểm.

## Kết luận

Chương 1 có cấu trúc hợp lý, đặt đúng bài toán chuyển xe/tấn công và đã tránh nhiều khẳng định quá mức. Tuy nhiên, trước khi dùng làm bản nộp, cần (1) nêu khoảng trống nghiên cứu chính xác hơn so với công trình gần, (2) xác định phép đo chính và điều kiện bác bỏ giả thuyết, (3) phân biệt đóng góp đã làm với kế hoạch thí nghiệm, và (4) sửa cách diễn giải nhãn ở tóm tắt và các phần liên quan. Kết quả mô hình theo giao thức v2 vẫn chưa chạy; vì vậy Chương 1 hiện bảo vệ được **thiết kế nghiên cứu**, chưa bảo vệ được **hiệu quả của biểu diễn**.

## Đánh giá từng mục

| Mục | Điểm đã tốt | Việc cần sửa, theo mức ưu tiên |
| --- | --- | --- |
| 1.1 Động cơ (121–126) | Nêu đúng rủi ro CAN, phân biệt sụt giảm hiệu năng với nguyên nhân, ghi nhận A–D là giao thức của Lampe–Meng. | **Cao:** Đoạn 124 cần nguồn trực tiếp cho vấn đề chuyển miền; hai bài tấn công năm 2010–2011 chỉ hỗ trợ bối cảnh an ninh. Thêm 2–3 câu đặt khoảng trống cạnh nghiên cứu chuyển tiếp/quan hệ của Khreasat–González và benchmark nhiều dữ liệu của Koltai và cộng sự. Giá trị riêng nên là phép đối chứng biểu diễn với cùng mô hình, mẫu nguồn và ngưỡng nguồn, cùng phân tích cơ chế thất bại; không phải việc dùng nhiều dataset. |
| 1.2 Vấn đề và phạm vi (128–131) | Đơn vị dự đoán theo cửa sổ, giới hạn Classic CAN và không suy ra độ trễ từ F1 đã nêu rõ. | **Cao:** Viết rõ ngay tại đây ngân sách dữ liệu đích: mô hình, chuẩn hóa và ngưỡng chỉ học/chọn từ nguồn; tại test chỉ được đọc quá khứ của trace để trích xuất đặc trưng. Điều này làm rõ nghĩa “chuyển xe” và phân biệt với target adaptation. **Vừa:** Cụm ở tên đề tài “CAN bus đa phương tiện” dễ được hiểu là multimedia; nếu tên chưa bị khóa, cân nhắc “trên nhiều mẫu xe”. Giữ câu cảnh báo rằng bỏ bit ID thô không chứng minh độc lập với xe. |
| 1.3 Câu hỏi nghiên cứu (133–140) | RQ2 yêu cầu đối chứng kiểm soát; đoạn 140 nhận ra detection và vehicle probe là hai phép đo riêng. | **Cao:** RQ1 “hiệu năng” chưa chỉ rõ tiêu chí chính. Cần nêu attack recall ở ngưỡng chọn theo ngân sách FAR nguồn, luôn kèm FAR đích và số mẫu; F1/AP là bổ sung. Bốn set dùng lại các xe, không tạo bốn cặp hoàn toàn độc lập. **Cao:** RQ3 nói “giảm thông tin nhận diện xe”, trong khi probe LR chỉ kiểm tra khả năng giải mã tuyến tính ở phép chia này. Viết đúng phạm vi phép đo. **Vừa:** RQ4 dùng “bộ dữ liệu độc lập” quá mạnh khi provenance của capture chưa xác nhận; dùng “bộ dữ liệu khác nguồn, đủ điều kiện về nhãn và schema”, nêu từng cơ chế. |
| 1.4 Giả thuyết và bác bỏ (142–145) | Có dự kiến trường hợp thất bại và không xem điểm thấp là vô giá trị. | **Cao:** “Chỉ tốt trên một set” và “probe vẫn cao” chưa phải tiêu chí bác bỏ được định nghĩa trước. Cần định trước phép so sánh ghép cặp, điều kiện B/D, tiêu chí lợi ích và cách xử lý FAR đích. Câu “lợi thế biến mất khi hiệu chuẩn raw trên dữ liệu nguồn” cần sửa vì giao thức chính hiện đã hiệu chuẩn ngưỡng nguồn cho **cả** raw và structural. Không dùng nhãn test đích để chỉnh các tiêu chí sau khi xem kết quả. |
| 1.5 Đóng góp và trạng thái bằng chứng (147–153) | Có ý thức ghi trạng thái các thí nghiệm chưa xong. | **Cao:** Mục 1 là đặc tả/triển khai, chưa tự chứng minh tính mới thuật toán; các thành phần ID-relations/history/timing đã có nghiên cứu gần. Mục 2 là thiết kế đối chứng đã cấu hình nhưng chưa có kết quả. Mục 3 là đóng góp về kiểm chứng dữ liệu/phần mềm có bằng chứng cục bộ, song không phải bằng chứng detector tốt. Mục 4 là kế hoạch, nên chuyển ra đoạn “đánh giá dự kiến” thay vì đặt chung danh sách đóng góp. Sau rerun, thay bằng các phát hiện thực nghiệm có số liệu và giới hạn. |
| 1.6 Tổ chức (155–156) | Khớp cấu trúc bản thảo. | **Thấp:** Khi hoàn tất thực nghiệm, cập nhật “thực nghiệm chờ chạy” thành nội dung thật; hiện câu này phù hợp bản sửa phương pháp, chưa phù hợp bản nộp cuối. |

## Đối chiếu câu hỏi với bằng chứng hiện có

| Câu hỏi | Bằng chứng bắt buộc | Trạng thái kiểm tra ngày 06/11/2026 |
| --- | --- | --- |
| RQ1 | Kết quả 4 set × 3 seed × A–D, hai ngưỡng, confusion counts và FAR/recall theo file/cơ chế | `primary.json` đã cấu hình; chưa thấy kết quả v2 hoàn tất trong `code/results`. |
| RQ2 | Ablation bỏ ID, thêm structure và loại nhóm đặc trưng, cùng mẫu nguồn và classifier | `ablation.json` có 11 biểu diễn; chưa chạy xác nhận. Kiến trúc Transformer cùng kiểu nhưng tầng vào khác số tham số. |
| RQ3 | So sánh ghép cặp raw/structural và probe xe/tấn công trên embedding cố định | Script hiện có, chưa có đầu ra v2. Probe LR không chứng minh độc lập thống kê với danh tính xe. Đối chứng embedding hằng/ngẫu nhiên được bản thảo yêu cầu nhưng script hiện chưa tạo. |
| RQ4 | Checkpoint nguồn đóng băng trên dữ liệu khác nguồn có nhãn, thứ tự và schema đáng tin; chia theo cơ chế | Chưa có kết quả xác nhận. CICIoV SPEED tạm loại, OTIDS chưa đủ provenance; CAN-MIRGU cần preflight toàn file và tách injection/masquerade/suspension. |

## Mâu thuẫn liên quan cần sửa cùng Chương 1

Tóm tắt tiếng Việt dòng 70 và abstract tiếng Anh dòng 81 viết cửa sổ dương nếu chứa “khung tin độc hại”. Công thức Chương 2 (dòng 179) thực ra lấy max của **nhãn do từng dataset cung cấp**. CAN-MIRGU gán nhãn 1 cho toàn khoảng suspension dù không có frame tấn công được chèn; bài công bố mô tả rõ chính sách này. Cần viết: “cửa sổ dương tính nếu có ít nhất một frame được dataset gán nhãn 1; ý nghĩa nhãn 1 phụ thuộc chính sách của từng bộ dữ liệu.” Sau đó tách nhãn frame chèn và nhãn khoảng tấn công khi phân tích kết quả. Không được diễn giải window recall thành tỷ lệ phát hiện từng frame độc hại.

Tên đề tài ở dòng 44/51 tuy có câu giới hạn ở dòng 131 nhưng vẫn hàm ý đã đạt “độc lập đặc thù xe”. Nếu chưa bị cố định bởi thủ tục nộp đề tài, tên thận trọng hơn là: **“Đánh giá biểu diễn cấu trúc không dùng CAN-ID thô cho phát hiện xâm nhập CAN trên nhiều mẫu xe”**. Đây là đề xuất biên tập, không phải yêu cầu đổi tên đã phê duyệt.

## Đề xuất câu chữ trọng tâm

**Cuối mục 1.1, thay phần nêu khoảng trống:**

> can-train-and-test đã cung cấp bốn điều kiện xe quen/lạ và tấn công quen/lạ; các nghiên cứu gần đây cũng đã dùng đặc trưng quan hệ hoặc đánh giá trên nhiều bộ dữ liệu. Vì vậy, khóa luận không xem việc bỏ CAN-ID, dùng Transformer hay chạy nhiều tập dữ liệu riêng lẻ là đóng góp mới. Câu hỏi trọng tâm là: trong cùng dữ liệu nguồn, cùng bộ phân loại và quy tắc chọn ngưỡng không dùng dữ liệu đích, việc bỏ giá trị ID thô đồng thời thêm lịch sử payload và quan hệ cục bộ làm thay đổi khả năng phát hiện theo từng điều kiện chuyển dịch và cơ chế tấn công như thế nào?

**Bản câu hỏi nghiên cứu chặt hơn:**

1. Tại ngưỡng chọn từ validation nguồn theo cùng ngân sách FAR, attack recall và FAR trên test thay đổi thế nào qua A–D và bốn set? F1, AP và số mẫu hỗ trợ diễn giải ra sao?
2. Với cùng classifier và mẫu nguồn, phần thay đổi nào đến từ bỏ bit ID thô, và phần nào đến từ thêm payload history, timing và thống kê quan hệ?
3. Khi so raw và structural, khả năng giải mã tuyến tính nhãn xe từ embedding thay đổi thế nào, và sự thay đổi đó đi cùng chất lượng phát hiện tấn công ra sao?
4. Khi áp dụng checkpoint đã đóng băng lên các dữ liệu khác nguồn có nhãn/schema được kiểm chứng, phương pháp thành công hoặc thất bại ở cơ chế nào?

**Giả thuyết cần tiền định trước khi chạy:** lấy chênh lệch structural trừ raw của attack recall tại ngưỡng hiệu chỉnh trên nguồn làm phép so chính ở B; báo FAR đích đồng thời. D là phép thử khó về tấn công lạ. Không gọi một lợi thế là “chuyển xe tốt hơn” nếu chỉ xuất hiện ở một set, mất khi xem FAR đích, hoặc phụ thuộc vào đổi ngưỡng theo nhãn test. Cần xác định trước thế nào là hiệu quả đủ lớn để có ý nghĩa sử dụng, dựa vào chi phí báo động giả có thể chấp nhận; hiện chưa có chuẩn vận hành hoặc số đo độ trễ để tự đặt mức đó.

## Ưu tiên thực hiện

1. Sửa định nghĩa nhãn ở tóm tắt và Chương 2; thống nhất với CAN-MIRGU suspension.
2. Viết lại khoảng trống cuối 1.1 và đặt quy tắc source-only trong 1.2.
3. Chốt endpoint, RQ3 và tiêu chí bác bỏ trước khi xem kết quả v2.
4. Tách phần đóng góp đã thực hiện khỏi kế hoạch, rồi cập nhật sau khi có thực nghiệm.
5. Kiểm tra tên đề tài với hồ sơ đã phê duyệt; nếu sửa được, làm rõ “nhiều mẫu xe”.

## Nguồn gốc được đối chiếu

- Lampe & Meng (2024), [can-train-and-test](https://doi.org/10.1016/j.cose.2024.103777): bộ đối chuẩn và bốn điều kiện đánh giá.
- Khreasat & González (2026), [Relational Modelling for Automotive Cybersecurity](https://pmc.ncbi.nlm.nih.gov/articles/PMC13210679/): đặc trưng chuyển tiếp/quan hệ, giới hạn chuyển bộ dữ liệu và hiệu chỉnh bằng dữ liệu đích.
- Koltai, Ács & Gazdag (2026), [CAN We Trust Your Results?](https://arxiv.org/html/2606.30430v1): benchmark năm phương pháp trên bảy bộ dữ liệu; chỉ dùng như công trình gần về giao thức, không coi số điểm của họ là đối chứng cùng bài toán.
- Rajapaksha và cộng sự (2024), [CAN-MIRGU](https://www.ndss-symposium.org/wp-content/uploads/vehiclesec2024-43-paper.pdf): chính sách nhãn suspension ở mục dữ liệu cạnh Hình 5.
- Kidmose, Kidmose & Meng (2025), [can-sleuth](https://link.springer.com/article/10.1007/s10207-025-01038-8): rủi ro phụ thuộc train/test và giới hạn bộ dữ liệu.

