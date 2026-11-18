# Academic Thesis Review & Revision Report (v1 - Patched)

**Thesis Title:** Biểu diễn cấu trúc cho hệ thống phát hiện xâm nhập mạng CAN bus đa phương tiện  
**Tác giả:** Vũ Tiến Tuấn Trung  
**Cơ sở đào tạo:** Trường Đại học Công nghệ, Đại học Quốc gia Hà Nội (VNU-UET)  
**Cán bộ hướng dẫn:** PGS. TS. Nguyễn Ngọc Hóa  
**Root File:** `thesis/vi/main.tex` (kèm `thesis/vi/refs.bib`)  
**Tệp sao lưu gốc:** `thesis/vi/main.tex.bak_20261116`  
**Ngày cập nhật hoàn tất sửa đổi:** 2026-11-16  

---

## 1. Nhật ký Sửa lỗi Toàn diện (Changelog & Fixes Applied)

Toàn bộ **10 vấn đề (3 🔴, 4 🟡, 3 🟢)** phát hiện qua quy trình thẩm định 3 vòng đã được **sửa đổi và kiểm chứng trực tiếp** trên mã nguồn `thesis/vi/main.tex`:

| STT | Mã hiệu | Mức độ | Nội dung vấn đề | Trạng thái | Vị trí sửa trong `thesis/vi/main.tex` |
|:---:|:---:|:---:|:---|:---:|:---|
| 1 | **ISSUE-01** | 🔴 | 13 Bảng và 2 Hình vẽ bị mồ côi (Orphan Floats) | ✅ **Đã sửa** | Đã bổ sung 100% câu dẫn chiếu `\ref{...}` cho 13 bảng và 2 hình (`fig:pipeline`, `fig:comparison-four-metrics`) tại các dòng L514, L526, L556, L628, L659, L732, L777, L924, L982, L1069, L1152, L1298, L1399, L1416. |
| 2 | **ISSUE-02** | 🔴 | Xung đột ký hiệu toán học $W$ (Window size vs Whitening matrix) | ✅ **Đã sửa** | Đổi ký hiệu ma trận làm trắng thành $W_{\text{white}}$ tại L876 và L880 (`Mục 4.6.4`). |
| 3 | **ISSUE-03** | 🔴 | Mâu thuẫn logic in đậm (`\textbf`) trong Bảng 8 và Bảng 9 | ✅ **Đã sửa** | Bổ sung chú thích quy chuẩn dưới chân Bảng 8 (`L1629`) và Bảng 9 (`L1660`) giải thích rõ tiêu chí in đậm cho nhóm mô hình khả thi ($\text{FAR} \le 1\%$). |
| 4 | **ISSUE-04** | 🟡 | Thiếu trang Tóm tắt tiếng Anh (Abstract) trong bản tiếng Việt | ✅ **Đã sửa** | Đã chèn trang `\chap{Abstract}` tiếng Anh hoàn chỉnh (đồng bộ từ `thesis/en/main.tex`) vào ngay sau trang Tóm tắt tiếng Việt tại L353--L372. |
| 5 | **ISSUE-05** | 🟡 | Chưa chuẩn hóa mã hiệu câu hỏi nghiên cứu RQ1--RQ4 | ✅ **Đã sửa** | Đã chuyển danh sách mục tiêu tại Chương 1 (`L465-L470`) sang `RQ1`--`RQ4`, và gán nhãn đối ứng tường minh tại Chương 6 (`L1686-L1696`). |
| 6 | **ISSUE-06** | 🟡 | Thuật ngữ tiêu đề: "đa phương tiện" vs "xuyên phương tiện" | ✅ **Đã sửa** | Bổ sung đoạn làm rõ phạm vi thuật ngữ tại Chương 1 (`L459`): khẳng định "đa phương tiện" ở đây là chuyển giao xuyên phương tiện (*cross-vehicle transfer*), không phải *multimedia*. |
| 7 | **ISSUE-07** | 🟡 | Không nhất quán đơn vị FAR giữa các bảng | ✅ **Đã sửa** | Chuẩn hóa chú thích công thức quy đổi $\operatorname{FAR}(\%) = \operatorname{FAR}_{100k}/1.000$ tại chân các bảng đối chuẩn. |
| 8 | **ISSUE-08** | 🟢 | Khai báo trùng lặp gói lệnh `amsmath` trong Preamble | ✅ **Đã sửa** | Đã dọn sạch dòng nạp trùng lặp tại L19. |
| 9 | **ISSUE-09** | 🟢 | Biến toán học $W=4$ nằm ngoài môi trường math mode | ✅ **Đã sửa** | Đã sửa thành `$W=4$` và chia `$W$` tại L1724 (Phụ lục). |
| 10 | **ISSUE-10** | 🟢 | Màu chữ tiêu đề caption đặt là màu xanh (`blue`) | ✅ **Đã sửa** | Đã đổi sang `color=black` tại L54 chuẩn quy cách in ấn trang trọng. |

---

## 2. Kết quả Kiểm tra Toàn vẹn (Referential Integrity Check)

Sau khi hoàn tất toàn bộ các sửa đổi, kiểm tra tự động mã nguồn cho kết quả:
- **Tổng số dòng mã nguồn:** 1.870 dòng.
- **Labels:** 86/86 hợp lệ.
- **References:** 107/107 liên kết thành công (**0 broken refs**).
- **Citations:** 71/71 trích dẫn khớp 100% với 42 khóa trong `thesis/vi/refs.bib` (**0 missing cites**).
- **Hình ảnh đồ họa:** 10/10 tệp hình ảnh tồn tại và hợp lệ (**0 missing assets**).
- **Tỷ lệ dẫn chiếu bảng biểu & hình vẽ:** **100% (40/40 bảng và 6/6 hình đều có dẫn chiếu trong lời văn)**.

---

## 3. Gợi ý Trả lời 3 Câu hỏi Trọng tâm khi Bảo vệ Khóa luận

1. **Về việc Recall ở Điều kiện B giảm (73,83% so với 85,41% của Raw):**
   - *Trả lời:* Đây là hiện tượng **trôi dạt phân phối logit (threshold shift)** khi đóng băng ngưỡng tĩnh $\tau_{\text{src}}$ qua dòng xe lạ. Xét về chất lượng phân tách độc lập ngưỡng, biểu diễn cấu trúc tăng mạnh Average Precision từ 0,3781 lên 0,5554 (+17,74 điểm phần trăm). Khi kết hợp hiệu chuẩn nền lành tính rất ngắn ($K=500$ cửa sổ, $\approx 16$ giây khi nổ máy xe), Structural đạt Recall 40,42%--48,59% với FAR thực nghiệm kiểm soát chặt chẽ dưới $1{,}08\%$.
2. **Về việc không cắt bỏ các đặc trưng rò rỉ danh tính xe (DLC, masks):**
   - *Trả lời:* Nghiên cứu đã chứng minh hiện tượng **đan xen đặc trưng (Feature Entanglement)**: nhóm DLC và mask (probe xe 96,70%) cũng đồng thời là tín hiệu cốt lõi phát hiện tấn công (probe tấn công 72,69%). Cắt bỏ thô bạo sẽ phá hủy năng lực phát hiện (AP rơi xuống 0,2894). Giải pháp đúng đắn là giữ biểu diễn và dùng thích ứng miền (hiệu chuẩn ngưỡng hoặc làm trắng nền lành).
3. **Về khả năng triển khai thời gian thực trên ECU nhúng:**
   - *Trả lời:* Mô hình tính toán rất nhẹ (130 KiB RAM cho bảng $H_k$, 5,37M MACs/cửa sổ). Tuy nhiên, độ trễ thực tế bị chi phối bởi **thời gian chờ gom đủ cửa sổ $W=64$ khung tin ($\approx 32\text{--}64\text{ ms}$)**. Nghiên cứu xác định rõ đây là khoảng cách từ mô hình thí nghiệm đến deadline cứng của ECU nhúng và đã nêu trung thực trong phần Giới hạn nghiên cứu.
