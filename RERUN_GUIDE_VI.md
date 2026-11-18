> **Cập nhật 08/11/2026:** bộ so sánh có thể chạy nằm trong `code/comparison/`
> và notebook 06–08. Đọc `VIEC_BAN_CAN_LAM.txt` và `code/comparison/README.txt`.
> Quét CTT thật phát hiện timestamp đi lùi, nên bộ so sánh mới dùng content-only
> raw28/structural30 theo thứ tự file. Các lệnh timed v2.1 dưới đây là giao thức
> trước đó và có thể bị chặn bởi kiểm tra thời gian; không dùng để bỏ qua lỗi dữ liệu.

# Chạy và hoàn thiện khóa luận — giao thức v2.1

Cập nhật 06/11/2026. Bản tiếng Việt là nguồn, tiếng Anh là bản dịch. Code và bản thảo đã được sửa đồng bộ; **thực nghiệm xác nhận chưa chạy**. Kiểm thử tổng hợp không phải kết quả IDS. Việc cần bạn làm được rút gọn trong `VIEC_BAN_CAN_LAM.txt`.

## 1. Chạy toàn bộ

Từ thư mục dự án `F:\00_Research`:

```powershell
.venv/Scripts/python.exe -m pip install -r code/requirements.txt
.venv/Scripts/python.exe -m pytest -q
.venv/Scripts/python.exe code/scripts/run_study.py --plan
.venv/Scripts/python.exe code/scripts/run_study.py --stage all
```

Nếu chưa có môi trường, tạo bằng `python -m venv .venv`. Trên Linux/Colab dùng `python` trong môi trường đã cài phụ thuộc. Giữ bản PyTorch tương thích CUDA; kiểm tra `torch.cuda.is_available()`. CPU được hỗ trợ nhưng chưa có cơ sở ước lượng thời gian huấn luyện. Đọc dữ liệu đầy đủ và lưu dự đoán cũng cần thời gian, RAM và dung lượng ổ đĩa.

Đường dẫn mặc định của launcher dựa trên vị trí code, không phụ thuộc thư mục shell. Có thể chỉ rõ `--root /duong/dan/code --output /duong/dan/ket_qua`. `root` chứa thư mục `data/`; thư mục kết quả cần được giữ bền vững nếu dùng Colab.

## 2. Chia giai đoạn và tiếp tục sau khi ngắt

`run_study.py --stage` nhận các giá trị theo thứ tự:

| Giai đoạn | Công việc |
|---|---|
| `preflight` | Quét toàn file, kiểm tra đủ bốn set và A–D, schema/nhãn/thời gian, hash, tệp trùng hệt |
| `primary` | 4 set × 3 seed × 4 mô hình = 48 lần fit; external timed ở Set 1 |
| `ablation` | 4 set × 3 seed × 13 biểu diễn = 156 lần fit |
| `content` | Set 1 × 3 seed × 3 mô hình = 9 lần fit; external không dùng thời gian |
| `sensitivity` | Cửa sổ 32 và 128; mỗi loại 4 set × 3 seed × 2 Transformer = 24 lần fit |
| `analysis` | Tổng hợp đủ ma trận, chênh lệch ghép cặp, hình recall/FAR/F1; bootstrap A–D cho primary |
| `probes` | Probe xe/tấn công và đối chứng cho 12 cặp encoder primary |
| `all` | Thực hiện lần lượt toàn bộ các giai đoạn trên |

Tổng cộng 261 lần fit mô hình IDS, chưa tính các bộ giải mã tuyến tính của probe. Đây là kế hoạch trước chạy, không phải số thí nghiệm đã hoàn tất. Lặp lại cùng lệnh sẽ xác minh và bỏ qua đơn vị đã hoàn tất tương thích. Lần chưa hoàn tất được giữ trong `attempt_###` và khởi chạy lại với tên mới; không có resume từ epoch dở dang. Khi code, dữ liệu, cấu hình hoặc môi trường thay đổi, dùng thư mục nghiên cứu mới và không trộn kết quả.

Preflight có thể tiếp tục theo file: chỉ tái sử dụng kiểm tra thành công khi mã kiểm tra, ledger và hash file vẫn khớp. Lỗi hoặc thư mục bắt buộc thiếu làm dừng giai đoạn. Không sửa nhãn, sắp xếp timestamp hoặc bỏ dòng chỉ để vượt kiểm tra. Báo cáo preflight không chứng minh các đoạn trace không chồng lặp hoặc các phiên lái độc lập.

## 3. Notebook và Colab

Sáu notebook trong `code/notebooks/` chỉ gọi các module chung. Đặt `PROJECT_HINT` đến thư mục chứa `code/` và `thesis/`; notebook tự tìm đúng thư mục code. Mọi ô được để chưa thực thi, không có số liệu giả.

Thứ tự: `Notebook.ipynb` → `can-train-and-test.ipynb` → `03_structural_id_agnostic_method.ipynb` → `04_external_validation.ipynb` → `02_shift_and_representation_analysis.ipynb`. Notebook `05_comparison_with_lampe2024.ipynb` kiểm tra số học công bố và tổng hợp, không xếp hạng điểm frame với window. Notebook chính tự kiểm tra GPU nhưng không tự đổi phần cứng Colab.

Nếu chép dữ liệu sang ổ cục bộ Colab, giữ nguyên cây `code/data/` và dùng `--output` trên Drive. Không coi các file cùng tên trên hai máy là cùng dữ liệu nếu hash khác.

## 4. Giao thức phải giữ nguyên

- Cửa sổ hoàn chỉnh không chồng lặp, không nối qua file; lịch sử liên tục trong từng file. Frame cuối chưa đủ cửa sổ vẫn được kiểm tra và đếm.
- Lấy mẫu toàn file, tối đa 1.000 cửa sổ/lớp/file; cùng lựa chọn cho mọi mô hình. v2.1 tách luồng ngẫu nhiên theo tên file và lớp để không phụ thuộc chunksize/thứ tự file. Không gộp với v2.0.
- Nhóm hậu tố bản ghi lớn nhất dùng làm validation nguồn. Đây chưa phải xác nhận phiên lái độc lập.
- Mỗi mô hình có ngưỡng mặc định 0,5 và ngưỡng chọn trên nguồn để tối đa recall với FAR ≤ 100/100.000 cửa sổ lành; khi hòa ưu tiên ít FP rồi ngưỡng cao hơn. Ngân sách nguồn không bảo đảm FAR đích.
- Điều kiện B là phép so chính cho RQ1; D kiểm tra giới hạn dịch chuyển đồng thời. Báo recall cùng FAR đích, F1, AP và mẫu số. Không chọn chỉ số hay ngưỡng theo test.
- Chênh lệch chính là structural trừ raw, trung bình seed trong từng set rồi trọng số set bằng nhau. Bốn set dùng lại xe: Impala→Silverado; Traverse→Forester; Silverado→Forester; Forester→Traverse. Không gộp ba set để tuyên bố xe ở set thứ tư chưa thấy.
- 13 ablation gồm 11 biểu diễn đã có, thêm bỏ riêng byte payload tuyệt đối và bỏ riêng chiều hạng/W. Không mặc định các biến thể này tốt hơn.

## 5. Dữ liệu ngoại bộ

Ledger ở `code/configs/external_datasets.json`. Dữ liệu thiếu hoặc bị loại được ghi riêng. Trạng thái COMPLETE của run chỉ xác nhận các capture đủ điều kiện đã được xử lý, không xác nhận đủ mọi dataset mong muốn.

| Dữ liệu | Phạm vi |
|---|---|
| Automotive v2 | Bốn log Opel/Renault; DoS theo khoảng timestamp đã kiểm tra và chữ ký frame. Có lưu lượng nền dùng chung; không coi là phiên độc lập. |
| CAN-MIRGU | Tìm log lành/tấn công đệ quy. Yêu cầu nhãn cuối dòng; suspension dùng nhãn khoảng đình chỉ, không có nghĩa mọi frame nhãn 1 đều được chèn độc hại. |
| CICIoV2024 | Tầng content: raw 28, structural 30 chiều, học lại từ nguồn. Thứ tự hàng cung cấp không tự chứng minh thứ tự vật lý. SPEED bị cách ly vì 4.989/24.951 dòng khác byte với bản decimal. |
| OTIDS | Bản chuyển đổi và bản shuffled bị tắt; cần nguồn gốc nhãn và bản ghi theo thời gian trước khi bật lại. |

Không tự sửa byte SPEED hoặc mặc định bản decimal đúng. Khi có bản chuẩn, chạy `code/scripts/verify_ciciov_representations.py`, cập nhật ledger có lý do, rồi làm lại preflight và nghiên cứu trong thư mục mới.

Nguồn dữ liệu: [can-train-and-test](https://arxiv.org/abs/2308.04972), [CAN-MIRGU](https://github.com/sampathrajapaksha/CAN-MIRGU), [CICIoV2024](https://www.unb.ca/cic/datasets/iov-dataset-2024.html), [Automotive v2](https://data.4tu.nl/articles/dataset/Automotive_Controller_Area_Network_CAN_Bus_Intrusion_Dataset/12696950/2), [OTIDS](https://ocslab.hksecurity.net/Dataset/CAN-intrusion-dataset).

## 6. Tổng hợp, probe và bất định

Launcher ghi kết quả vào `code/results/confirmatory_v21/`. Các thư mục `summaries/<giai_doan>/` chứa:

- `coverage.json`: đủ/thiếu ma trận, hash manifest đầu vào.
- `all_metrics.csv`, `mean_std_by_seed.csv`, `per_capture_mean_std.csv`: số đếm, metric và biến thiên seed.
- `paired_by_seed.csv`, `paired_by_set.csv`, `paired_equal_set_mean.csv`: chênh lệch của các cặp đối chứng.
- Hình recall, FAR và F1 theo điều kiện; không thay thế bảng số hoặc dùng trục khác để che kết quả kém.

`paired_A.json` đến `paired_D.json` ở mỗi checkpoint primary ghi chênh lệch recall/FAR/F1 cho cả hai ngưỡng. Bootstrap 1.000 lần lấy lại toàn file bằng cùng mẫu cho hai mô hình. Dưới ba file không tạo khoảng; báo số lần hợp lệ khi có mẫu thiếu mẫu số. File có thể chia sẻ phiên ghi, nên khoảng này chỉ mô tả có điều kiện, không đại diện quần thể xe.

Probe cân bằng xe × nhãn trong mỗi phía, dùng LR C=1 và tối đa 2.000 vòng; scaler chỉ fit trên probe-train. Cùng mẫu được dùng cho hai encoder. Đối chứng: embedding hằng, Gaussian độc lập train/test, nhãn train hoán vị; hai đối chứng ngẫu nhiên lặp năm seed định trước. Lưu `probe_windows.csv.gz`, hash dữ liệu/checkpoint và metric. Không dùng probe để chọn IDS hoặc diễn giải probe gần ngẫu nhiên thành chứng minh đã xóa hết thông tin xe.

## 7. Đo thời gian nếu cần tuyên bố về chi phí

Sau khi có primary hoàn tất, thay hai đường dẫn mẫu bằng checkpoint thực và một file validation nguồn cố định:

```powershell
.venv/Scripts/python.exe code/scripts/benchmark_runtime.py --checkpoint-dir "DUONG_DAN_CHECKPOINT" --file "FILE_VALIDATION_CTT.csv" --output code/results/runtime_v21.json --device cpu
```

Mặc định warmup 50, đo 1.000 cửa sổ đầu kế tiếp, lặp ba lần, batch=1. Có thể chọn `--device cuda` nếu phù hợp. Benchmark là tiền tố cố định chỉ phục vụ hiệu năng phần mềm, không tính kết quả phát hiện. Nó gồm parser, bộ trích xuất chung tạo cả raw/structural, truyền dữ liệu và inference. Báo median/p95 thời gian xử lý cùng khoảng thời gian thu nhận cửa sổ; OS cache có thể ảnh hưởng lần đọc sau. Không suy ra độ trễ phát hiện sự kiện, queueing hay deadline ECU.

## 8. Hoàn thiện bản nộp

Giữ toàn bộ thư mục run, không chỉ bảng tổng hợp: manifest, split, coverage, window index, checkpoint, metadata ngưỡng, dự đoán và danh mục loại trừ. Sau khi có số thật, cập nhật đồng thời tóm tắt Việt/Anh, Chương 5, hình và kết luận. Giữ cả thất bại C/D và N/A hợp lệ.

Code chưa tái lập trung thành các thuật toán SOTA bên ngoài. Nếu muốn tuyên bố vượt công bố gần nhất, cần tái lập đúng baseline quan hệ hoặc phương pháp tương ứng trong cùng giao thức, hoặc thu hẹp tuyên bố về so sánh biểu diễn đã triển khai. Entropy, Hamming, DANN và reconstruction là hướng nghiên cứu thêm, không phải kết quả hay điều kiện bảo đảm Q1.

Xác nhận mẫu/rubric, tên đề tài được duyệt và nội dung cam đoan với GVHD. Phần tóm tắt đã tách cỡ 12pt, nhãn từ khóa đậm nghiêng theo mẫu UET công khai; chưa có xác nhận mẫu áp dụng cho khóa hiện tại. Bài Jo–Kim 2026 vẫn chỉ được dùng trong phạm vi thông tin đã tiếp cận, không lấy hai bài trước thay cho toàn văn.

## 9. Kiểm tra và biên dịch

```powershell
python code/scripts/check_manuscript.py
```

Trong `thesis/vi` và `thesis/en`, lần lượt chạy:

```powershell
../../.tools/tectonic/tectonic.exe --outdir ../../code/output/thesis_compile_check/vi main.tex
```

Đổi thư mục đầu ra thành `en` khi biên dịch bản Anh. Dùng font Times New Roman, Arial và Consolas phù hợp; xem PDF sau biên dịch, không chỉ dựa vào mã thoát. Nguồn trước lần sửa này được giữ trong `revision_backup/before_full_revision_2026-11-06.zip`; notebook trước v2.1 có bản sao riêng.

Các file `phase*`, `master_*`, bảng so sánh cũ và `verification_report.json` ngày 04/11 là hồ sơ lịch sử. Báo cáo kiểm tra hiện tại là `code/results/revision_v21_checks.json`; không coi hồ sơ cũ là kết quả của phiên bản này.

## 10. Bổ sung đối chứng từ bài báo

Đọc `KE_HOACH_SO_SANH.txt` trước khi chạy toàn bộ. Kế hoạch mới ưu tiên CANBERT+,
CANLP và một phương pháp từ framework CrySyS; các adapter ngoài hiện **chưa triển
khai**. `run_study.py --stage all` chỉ chạy các mô hình hiện có.

Thứ tự: chuẩn bị GPU/dữ liệu và preflight → adapter/đặc tả → pilot trên nguồn →
chốt phiên bản → chạy ma trận đối chứng → phân tích → ablation và cập nhật bản
thảo. Chốt code trước khi chạy full để tránh phải chạy lại do thay đổi hash.
Repo ngoài dùng môi trường riêng. Ngưỡng anomaly score cần hiệu chuẩn từ nguồn;
không mặc định ngưỡng 0,5 cho mọi thuật toán.

Danh sách 12 công trình và các PDF ở `code/notes/doi_thu_2026-11-06/`;
`comparison_plan.json` ghi trạng thái kế hoạch và đầu ra cần có. Kế hoạch không
đồng nghĩa đã tích hợp hoặc chạy các phương pháp đó. Báo cáo kiểm tra v2.1 giữ
kết quả kiểm thử phần mềm cũ và ghi riêng lần cập nhật tài liệu/kế hoạch này.
