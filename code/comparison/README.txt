CHẠY SO SÁNH CAN IDS — 08/11/2026

MỞ THEO THỨ TỰ
1. code/notebooks/06_prepare_comparison_data.ipynb
2. code/notebooks/07_run_paper_comparisons.ipynb
3. code/notebooks/08_analyze_paper_comparisons.ipynb

Notebook 06 cài dependencies, tải/kiểm tra ba repo đúng commit, dùng cache dữ liệu
đã chuẩn bị hoặc tạo cache từ CTT gốc. Notebook 07 chạy pilot nguồn rồi full run;
Notebook 08 chỉ tổng hợp khi đủ ma trận. Các ô notebook được để chưa thực thi.

DỮ LIỆU VÀ PHẠM VI
236 file CTT gốc nằm tại code/data/can-train-and-test/. Cache compact lưu timestamp,
ID, DLC, byte payload và nhãn frame nguyên giá trị; không xóa trùng, không sort,
không dựng timestamp. Full-file scan ghi số frame/cửa sổ/tail, hash input/cache
và số lần timestamp đi lùi. Đây là phép so content-only theo thứ tự file.
Trong dữ liệu thật có timestamp đi lùi, nên không chạy mặc định nhánh có timing.
Nhánh hiện hành có raw 28 và structural 30 chiều, tương ứng bỏ timing khỏi v2.1;
không gộp số của nhánh này với kết quả timed 29/32 chiều.
Thứ tự file không tự chứng minh chronology vật lý. Không suy ra latency thực xe.
Cache toàn file không chứng minh các phiên độc lập hoặc không chồng lặp đoạn.

NĂM MÔ HÌNH ĐÃ TÍCH HỢP
- raw_transformer, structural_transformer: dùng model và CE/AdamW/Cosine của code
  chung, cùng mẫu nguồn; chỉ khác biểu diễn 28/30 chiều.
- canbertplus: import nguyên BERT và BERTLM từ repo OSUSecLab, vocab source-only,
  PAD/SEP/CLS/UNK/MASK và token ID/DLC/byte vị trí đúng định nghĩa tokenizer gốc.
  Dùng pretrain masked-ID 15% trên cửa sổ benign nguồn, fine-tune frame-label;
  classifier trên đầu ra MLM như can_finetune.py. Score window = max frame score.
  Mặc định 768 hidden/6 layers/12 heads; pretrain 3 và fine-tune 3 epoch.
  Vòng lặp PyTorch thay Lightning, shared sampling/group split/W64/source threshold,
  epoch cố định và đảm bảo ít nhất một token mask khi batch không có mask là các
  thay đổi có chủ đích. Không tự nhận đã tái lập metric công bố.
- canlp: port kiến trúc char TF-IDF unigram + tối đa 256 bigram, thêm ID/2048,
  Dense 128/ReLU/dropout .15/Dense 64/ReLU/2 lớp sang PyTorch. Adam .001,
  eps 1e-7, batch 512, 30 epoch. TF-IDF fit chỉ trên frame trong mẫu nguồn.
  Giữ nhãn frame gốc; score window = max frame score. Chữ hex chuẩn hóa uppercase.
  Thay random/balanced train-test của notebook tác giả bằng grouped source split,
  không xóa trùng dòng, nhãn nhị phân và epoch cố định thay best-val checkpoint.
  Đây là CANLP-char-DNN adapted, chưa phải tái lập bản journal nguyên trạng.
- assoc_rules_crysys: import nguyên implementation benchmark CrySyS. Fit chỉ
  benign nguồn, cửa sổ 64/stride64 thay 900/450. Mỗi cửa sổ lấy mẫu được đánh dấu
  riêng để không ghép quan hệ qua khoảng trống giữa mẫu/file. K-means có ngẫu
  nhiên nên chạy đủ ba seed. Giữ heuristic upstream: KNN được diễn giải là
  K-means, dist_threshold=.3; itemsets tối đa 3 khi train và 2 khi score.
  Ghi tên CrySyS-AssocRules/W64; không gọi là tái lập trung thành D'Angelo 2023.

GIAO THỨC
W64 đủ/non-overlap/không nối file. Tối đa 1.000 cửa sổ mỗi lớp/file, reservoir
toàn file; cùng source sample cho mọi mô hình và seed. Validation nguồn theo
hậu tố recording-round; không dùng test để chọn model/vocab/scaler/ngưỡng.
Ngưỡng source-calibrated tối đa recall trong FAR <=100/100k benign windows nguồn.
FAR đích có thể cao hơn. Không áp ngưỡng .5 làm mặc định cho anomaly score Assoc.
Benign-only/MLM/frame-supervised/window-supervised là các điều kiện khác nhau,
phải báo rõ. Không dùng nhãn đích để tinh chỉnh hoặc đổi phương pháp theo score.
Tập đích đã từng được xem trước; không gọi là benchmark hoàn toàn chưa tiếp xúc.

PILOT VÀ FULL
Pilot thu nhỏ mô hình/epoch, source sample và validation; không đánh giá A–D.
Pilot được gắn software_validation_only và bị từ chối bởi hàm tổng hợp nghiên cứu.
Full mặc định 4 set x 3 seed x 5 mô hình = 60 đơn vị IDS. Pretrain/fine-tune là
hai bước bên trong một đơn vị CANBERT+, không tính 60 là 60 optimizer phases.
Mỗi cell có attempt mới khi chưa hoàn tất; COMPLETE chỉ bỏ qua khi config/code/
data/environment/output hashes còn khớp. Không resume từ epoch dở dang.

LỆNH TẠI F:\00_Research
  .venv/Scripts/python.exe code/scripts/run_comparison.py --stage setup
  .venv/Scripts/python.exe code/scripts/run_comparison.py --stage prepare
  .venv/Scripts/python.exe code/scripts/run_comparison.py --stage pilot --output code/results/comparison_pilot
  .venv/Scripts/python.exe code/scripts/run_comparison.py --stage run
  .venv/Scripts/python.exe code/scripts/run_comparison.py --stage summarize
Trên Colab dùng python của kernel. Có thể chỉ định --cache/--output/--sets/--seeds/
--methods. Tập subset là giao thức khác; không trộn vào output của ma trận đầy đủ.
Không đổi code hoặc cấu hình giữa chừng; nếu cần đổi, dùng thư mục output mới.
--stage setup tải đúng commit và xác minh file hash; không cài dependency repo
gốc đè lên môi trường. Các adapter hiện cần numpy/pandas/torch/scipy/sklearn và
các module dùng chung trong requirements.txt; không cần TensorFlow/Lightning.

GIỮ KẾT QUẢ
Giữ manifest, selected_source_windows, split, checkpoint, prediction csv.gz,
score frame .frames.f32 (float32 little-endian, windows x 64 theo CSV đi kèm),
source threshold, training history và coverage. Tổng hợp có Recall/FAR/F1/AP,
per-capture, seed, paired equal-set differences và bootstrap theo capture file.
CI là mô tả có điều kiện, không phải CI cho quần thể xe; bốn set dùng lại xe.
RAM/VRAM/thời gian full cần đo trên GPU thực tế; chỉ pilot CPU được kiểm tra tại đây.

NGUỒN
CANBERT+: https://www.usenix.org/conference/vehiclesec26/presentation/won
CANLP: https://doi.org/10.1109/TDSC.2025.3596516
CrySyS: https://arxiv.org/abs/2606.30430
URL, commit và file hashes của code gốc: comparison/upstream.lock.json.
