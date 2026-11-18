# Audit khóa luận: những việc cần bổ sung để hướng tới mức xuất sắc

Rà soát ngày 05/11/2026. Phạm vi: hai bản LaTeX trong thesis/vi và thesis/en, thư mục code, kết quả và các ghi chú audit hiện có. Đây là danh sách công việc có thể kiểm chứng, không bảo đảm 100 điểm. Chưa có rubric hiện hành hoặc kết quả huấn luyện v2 để xác nhận mức điểm.

**Quy ước đường dẫn sau khi gộp:** các tên như `method_vi.tex` hoặc `results_en.tex` xuất hiện trong ghi chú audit cũ nay chỉ vị trí chương tương ứng bên trong `thesis/vi/main.tex` hoặc `thesis/en/main.tex`; các file chương riêng đã được lưu ngoài thesis trong `revision_backup/thesis_sources_before_flatten_2026-11-05/`.

## Nhận định tổng thể

Bản thảo đã có câu hỏi nghiên cứu, feature 29/32 chiều, giao thức source-only và mô tả giới hạn khá cẩn trọng. Khoảng trống quyết định: chương kết quả vẫn ghi “chờ chạy” cho RQ1–RQ4. Kiểm thử phần mềm, số liệu thăm dò cũ và trích dẫn bài báo không thay thế được bằng chứng hiệu quả của checkpoint v2. Tính mới cũng cần đối chiếu sâu hơn với các nghiên cứu về quan hệ ID, lịch sử payload và benchmark nhiều dataset.

P0 = bắt buộc trước bản nộp; P1 = quan trọng để bảo vệ đóng góp; P2 = mở rộng khi còn nguồn lực hoặc giữ tuyên bố tương ứng. Những mục dưới đây phân biệt hiện trạng với việc cần thực hiện.

## Phần I — Bài báo nào cần bổ sung, dẫn chứng cho câu nào?

**Cập nhật bibliography 05/11/2026:** ban đầu có 18 mục BibTeX. Đợt đầu thêm Kidmose 2025, Koltai 2026, Dong 2026, Jo--Kim 2026, Obafemi 2026, Hewitt--Liang 2019, Gulrajani--Lopez-Paz 2021 và Saito--Rehmsmeier 2015. Đợt này thêm năm công trình có vai trò cụ thể: Rajapaksha et al. 2023 (survey), Sharmin et al. 2024 (thiết kế benchmark), Cho--Shin 2016 (fingerprint ECU theo thời gian), Chiscop et al. 2021 (sửa payload không đổi timing), Jeong et al. 2024 (giải mã tín hiệu cần CAN database). Hiện mỗi bản VI/EN có **31 mục BibTeX, cả 31 đều được trích**: **29 công trình nghiên cứu phân biệt + một bản ghi dataset Dupont 2019 + một entry arXiv v1 trùng công trình Lampe--Meng journal**. Hai refs.bib giống nhau và hai bản biên dịch được bằng Tectonic. Đây là kiểm tra cấu trúc/citation/biên dịch, chưa xác nhận chất lượng dịch hoặc thể thức cuối.

Quy tắc: mỗi trích dẫn phải đứng cạnh một mệnh đề cụ thể. Bài mô tả dataset dùng cho nguồn gốc nhãn và thiết kế thử nghiệm; bài đề xuất IDS dùng để đối chiếu ý tưởng; bài về metric dùng để biện hộ cách đánh giá. Không đưa một con số F1 công bố vào bảng so sánh trực tiếp khi khác dữ liệu, nhãn, đơn vị và điều kiện dùng dữ liệu đích.

| Ưu tiên | Nguồn gốc đã đối chiếu | Bổ sung ở đâu và chứng minh điều gì | Việc cần kiểm thêm |
|---|---|---|---|
| Nền tảng | [Rajapaksha et al. 2023](https://doi.org/10.1145/3570954), 10.1145/3570954 | Mở đầu nghiên cứu liên quan: phân loại AI IDS và giới hạn dataset; không dùng survey làm số liệu đối chuẩn | Khi mở rộng literature matrix, đối chiếu từng phương pháp gốc thay vì trích số từ survey |
| Phương pháp | [Sharmin et al. 2024](https://arxiv.org/abs/2402.06904), 10.3233/JCS-230027 | Cơ sở cho điều kiện so sánh: attack model, workload, metric và giao thức đánh giá phải khớp | Điền bảng đối chiếu split, đơn vị frame/window và target-data budget cho từng baseline |
| Timing | [Cho & Shin 2016](https://www.usenix.org/conference/usenixsecurity16/technical-sessions/presentation/cho) | Đối chiếu fingerprint đồng hồ ECU theo xe với đặc trưng thời gian không gắn ECU của khóa luận | Nếu tái lập, phải huấn luyện baseline ECU theo protocol gốc; không lấy điểm công bố để xếp hạng |
| Payload | [Chiscop et al. 2021](https://www.scitepress.org/Link.aspx?doi=10.5220/0010445504880496), 10.5220/0010445504880496 | Dẫn chứng cơ chế sửa thông điệp không đổi timing và động cơ của payload branch | Kiểm tấn công modification trong tập đích; hiện chưa có benchmark matched |
| Tín hiệu | [Jeong et al. 2024, X-CANIDS](https://arxiv.org/abs/2303.12278), 10.1109/TVT.2023.3327275 | Đối chiếu mô hình có CAN database để giải mã tín hiệu với biểu diễn byte/bit không DBC | Ghi rõ tính sẵn có của CAN database và khác biệt đơn vị nhãn, split nếu so định lượng |
| Bắt buộc | [Lampe & Meng, can-train-and-test](https://arxiv.org/abs/2308.04972), bài nguồn benchmark và README cục bộ | background_vi/en: A/B/C/D, bốn set và xe nguồn/đích; method: tuân thủ split; results: không gọi bốn set là bốn xe đích độc lập | Nêu rõ ba xe đích phân biệt: Silverado, Forester, Traverse; Forester và Traverse được dùng lại ở set khác |
| Bắt buộc | [Kidmose et al., can-sleuth 2025](https://link.springer.com/article/10.1007/s10207-025-01038-8), 10.1007/s10207-025-01038-8 | background/related: giới hạn dataset, CTT v1.5, suppress/masquerade; method: nhãn của suppress không thể đánh giá ngây thơ như frame chèn | Không tự dùng điểm F1 suppress trong bài làm ground truth cho mô hình này; bản v1.5 chưa có trong workspace |
| Bắt buộc | [Rajapaksha et al., CAN-MIRGU 2024](https://www.ndss-symposium.org/wp-content/uploads/vehiclesec2024-43-paper.pdf), 10.14722/vehiclesec.2024.23043 | background/method/results: phân biệt real injection, simulated masquerade/suspension và nhãn cả khoảng suspension | Ghép với audit cục bộ để nêu đúng policy; không gọi tất cả nhãn 1 là frame do kẻ tấn công phát |
| Bắt buộc | [Khreasat & González 2026](https://www.mdpi.com/1424-8220/26/10/2964), 10.3390/s26102964 | related: transition/topology đã được nghiên cứu; method: khác ở payload history và strict source-only; discussion: những gì vẫn trùng | Tách phần tác giả dùng normal target calibration khỏi strict source-only; xem full method trước khi tái lập |
| Bắt buộc | [Dong et al., MTFF 2026](https://pmc.ncbi.nlm.nih.gov/articles/PMC13468888/), 10.3390/s26154758 | related: bài đã kết hợp intra-ID history và inter-ID scheduling; sửa mọi câu gợi ý đây là ý tưởng lần đầu | Phương pháp frame-level, dữ liệu/split khác; chỉ so định tính trước khi có adapter chung |
| Bắt buộc | [Koltai et al. 2026](https://arxiv.org/abs/2606.30430), [code tác giả](https://github.com/CrySyS/Cross-Dataset-Study-of-Automotive-IDS-Evaluation) | related: benchmark nhiều dataset đã có; discussion: điểm khác phải là kiểm soát representation/target budget/cơ chế, không chỉ “đánh giá nhiều tập” | arXiv hiện ghi accepted ACSW'26; kiểm thông tin kỷ yếu trước khi trích phiên bản xuất bản |
| Quan trọng | [Islam et al., Graph IDS](https://arxiv.org/abs/2009.11440), 10.1109/TITS.2020.3025685 | related: quan hệ ID/đồ thị không mới; đối chứng chỉ khi tái lập đúng graph construction và classifier | Bài journal xuất bản 2022 dù DOI gắn năm 2020; kiểm metadata BibTeX |
| Quan trọng | [Islam et al., Hybrid UIDS 2026](https://pmc.ncbi.nlm.nih.gov/articles/PMC12986820/), 10.3390/s26051489 | related/discussion: hướng universal có timing/volume và bước hiệu chỉnh; bảng so ghi chính xác lượng dữ liệu đích được dùng | Không xếp điểm target-calibrated chung với zero-target-budget |
| Quan trọng | [Neto et al., CICIoV2024](https://www.unb.ca/cic/datasets/iov-dataset-2024.html), 10.1016/j.iot.2024.101209 | background/method: provenance của dữ liệu Ford, schema; giải thích vì sao local CSV không có timestamp đo được và phải dùng content tier | Trang tác giả không chứng nhận bản SPEED cục bộ đúng; kiểm lại file chuẩn theo hash |
| Quan trọng | [ROAD, Verma et al.](https://doi.org/10.1371/journal.pone.0296879) | background/limitations: cơ chế tấn công thật và dataset ngoài CTT; đề xuất external validation nếu tải/adapter được | Chưa có dataset và adapter trong workspace: không ghi như kết quả đã chạy |
| Phương pháp | [Hewitt & Liang 2019](https://aclanthology.org/D19-1275/) và [Saito & Rehmsmeier 2015](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0118432) | method: control cho probe và PR/denominator khi lệch lớp | Đây là nguyên lý phương pháp từ NLP/đánh giá nhị phân, không phải bằng chứng hiệu quả trên CAN |

**Đã nhập và trích:** tám bài mới ở cả hai refs.bib, đoạn related VI/EN và probe trong method VI/EN. Bài Jo--Kim mới được kiểm ở abstract/metadata công khai, vì toàn văn bị hạn chế; đoạn văn chỉ nói ở mức abstract. Koltai được trích theo arXiv v1 và ghi trạng thái accepted từ trang arXiv, chưa tự đổi thành bài kỷ yếu khi thiếu metadata kỷ yếu. File code/notes/RESEARCH_ADDITIONAL_REFERENCES_2026-11-04.bib vẫn là bản nháp lịch sử, không phải bibliography mà thesis đọc. Không tăng số tài liệu bằng các bài chỉ báo accuracy trên random split một xe.

**Bảng literature nên thêm vào related:** hàng là các bài gần nhất; cột là ID value/key, payload, same-ID history, timing/transition, mô hình, dữ liệu đích dùng để fit/threshold, đơn vị quyết định, source code, khác biệt kiểm chứng. Ô nào chưa đọc đủ toàn văn ghi “chưa xác minh”, không suy từ tiêu đề “universal”.

## Phần II — So sánh cái gì, như thế nào?

### Câu hỏi 1: Chuyển xe và tấn công

- **Cặp chính:** Transformer raw và Transformer structural, cùng W=64, cùng file/window train, cùng encoder/head, seed 42/43/44, cùng source validation, hai ngưỡng 0,5 và source-calibrated. Primary có 4 set × 3 seed × 4 cấu hình = 48 fit. Bảng chính phải có A/B/C/D **riêng từng set**, không lấy trung bình che D.
- **Ma trận CTT:** A=xe quen/tấn công quen; B=xe lạ/tấn công quen; C=xe quen/tấn công lạ; D=xe lạ/tấn công lạ. B trả lời transfer xe trong attack quen; D là stress test mạnh hơn. A−B, A−C hoặc tương tác chỉ là chênh lệch mô tả nếu capture/prevalence khác, không là tác động nhân quả thuần.
- **Endpoint đề xuất khóa trước rerun:** attack recall tại ngưỡng chọn duy nhất từ validation nguồn theo ngân sách FAR đã khai báo; luôn đi cùng FAR đích và TP/FP/TN/FN. Báo F1, AP, prevalence và ngưỡng 0,5 để phân biệt vấn đề ranking với vấn đề threshold. Ngân sách FAR nguồn không là ràng buộc đảm bảo trên target.
- **Bảng/đồ thị:** mỗi model×set×condition×threshold: mean ± SD của ba seed và từng seed trong phụ lục; forest/dumbbell plot paired structural−raw cho B và D theo set; PR/score distribution chỉ khi cùng tập nhãn. Đơn vị phân tích là capture/session khi có căn cứ, seed chỉ đo biến thiên tối ưu.

### Câu hỏi 2: Lợi ích do bỏ ID, thêm cấu trúc hay do classifier?

- **Ablation có sẵn:** raw → raw_no_id (bỏ ID); raw → raw_plus_structural (thêm history/structure nhưng giữ ID); raw_plus_structural → structural (bỏ ID trên nền feature phong phú); structural → structural_no_delta/no_timing/no_local/no_transition. So theo cặp trên cùng set, seed, split, W, architecture, threshold rule. Cấu hình ablation hiện 4×3×11 = 132 fit nếu chạy toàn bộ.
- **Ablation cần triển khai:** structural_no_absolute_payload (bỏ byte tuyệt đối 1–8 nhưng giữ DLC/mask/delta/timing/structure); mục này chưa có trong code/src/can_research/features.py:73–78. Nó kiểm liệu giá trị payload tuyệt đối hay sự thay đổi cùng ID tạo tín hiệu. Không được kết luận điều này chỉ từ structural_no_delta.
- **Ma trận model × representation:** Transformer raw/structural đã có; thêm LR structural và XGB raw vào primary để thành ba họ × hai đầu vào, 24 fit bổ sung ở bốn set/ba seed. So representation **trong cùng classifier** rồi so classifier **trên cùng representation**. Khi cần, một baseline mean/pooled features + LR hoặc MLP nhỏ giúp kiểm tra attention có thật sự cần.
- **Baseline bài báo:** một tái lập relational/transition trung thành là đủ hữu ích hơn nhiều tên mô hình sơ sài. Trước hết chạy đúng thiết lập gốc; sau đó chuyển sang cùng CTT split, window label, ngưỡng và target budget. Ghi chi tiết adapter, số chiều và thay đổi so bản gốc. Điểm in trong bài chỉ là bối cảnh khi chưa tái lập cùng giao thức.

### Câu hỏi 3: Kiểm tra tổng quát hóa ngoài CTT và cơ chế khó

- **Timed external:** checkpoint Set 1 đã đóng băng trên CAN-MIRGU và Automotive v2; báo từng file, xe, attack family, nhãn, prevalence và FP/giờ khi có timestamp. Không gộp benign-only, attack-only và mixed rồi so AP/FAR thiếu mẫu số.
- **Content external:** CICIoV dùng model huấn luyện lại trên CTT không có các chiều thời gian; so raw-content với structural-content, không so như thể cùng checkpoint timed. Nếu không chứng minh thứ tự dòng là thứ tự vật lý, diễn giải history/transition có điều kiện.
- **Suspension/suppress:** event onset/interval và độ trễ cảnh báo; thêm timeout baseline khi policy profile được xác định. Một window classifier chỉ phát quyết định cuối W; phải báo latency thu thập cửa sổ. Thêm error case replay/masquerade giữ lưu lượng gần benign để thử sự phụ thuộc vào injection rate.
- **Probe:** raw/structural embedding và engineered features, cùng file-group split, cùng ngân sách probe; thêm constant/random control và attack-probe. Chỉ kết luận giảm khả năng giải mã tuyến tính xe trong probe này, không tuyên bố độc lập thống kê với xe.

### Quy tắc báo cáo để bảng so sánh có giá trị

1. Một hàng chỉ so được khi cùng tập test, nhãn, đơn vị cửa sổ, training budget và target-data budget; ghi khác biệt nếu không thể cân bằng.
2. Lưu confusion counts và N+/N− cho mọi điểm; AP chỉ khi có hai lớp và score liên tục; single-class metric N/A đúng nghĩa.
3. Công bố nhóm file/vehicle/capture dùng lặp giữa set. Bootstrap theo đơn vị độc lập có căn cứ; không dùng hàng trăm nghìn cửa sổ làm bậc tự do thống kê.
4. Predefine bảng chính trước khi xem rerun; mọi ablation/threshold chọn thêm sau đó đánh dấu exploratory.
5. Khi có kết quả âm tính, viết điều kiện thất bại và loại tín hiệu nào mô hình không thấy. Không gộp nó khỏi abstract hoặc conclusion.

## Phần III — Code review: lỗi, rủi ro và phần còn thiếu

**Phạm vi:** đọc entry point experiment.py, io.py, features.py, models.py, metrics.py, preflight.py, summarize_results.py, package_revision.py, các config và 17 test protocol. Worktree sau đổi thư mục có nhiều file cũ được Git ghi là deleted và bản mới untracked; git diff --stat đơn thuần không phản ánh đầy đủ mã hiện hành. Ngày 05/11/2026, chạy lại 17 test: 17 passed trong 5,96 giây. Review này chưa chạy full preflight hay huấn luyện v2 trên dataset thật. Theo quy trình code-review-expert, đây là phát hiện để lập kế hoạch, chưa sửa code huấn luyện trong đợt audit.

### P0/P1: phải xử lý trước run xác nhận hoặc gói nộp

1. **P0 — Gói thesis thiếu đầu vào: đã sửa 05/11/2026.** Hai `main.tex` đã tự chứa nội dung chương và bảng; script đóng gói lấy đúng hai master, hai `refs.bib`, hai thư mục `figs/`, và fail nếu thiếu nguồn LaTeX bắt buộc. ZIP mới đã kiểm checksum từng file, giải nén vào thư mục tạm và biên dịch thành công cả VI/EN. Khi nộp trên máy khác vẫn phải có font và bộ TeX tương ứng.
2. **P1 — Đánh giá “streaming” vẫn giữ toàn bộ dự đoán trong RAM.** code/src/can_research/experiment.py:111–145 lưu y_parts/score_parts cho mỗi file rồi all_y/all_scores cho toàn condition; với nhiều file lớn × nhiều mô hình, bộ nhớ tăng theo tổng window, trái với kỳ vọng chỉ xử lý từng chunk. File dự đoán đã ghi gzip nhưng metric/AP/threshold vẫn concat lại. **Sửa:** dùng confusion counts cộng dồn ở ngưỡng đã khóa; AP/ranking và chọn ngưỡng cần chiến lược lưu score ra disk hoặc external merge/đọc theo lô có giới hạn. Đo peak RAM trên log lớn trước khi gọi khả năng streaming là đã kiểm chứng.
3. **P1 — Preflight có thể bỏ sót thành phần dự kiến.** code/src/can_research/preflight.py:49–63 glob các CTT file hiện thấy và external_specs hiện thấy; chỉ fail nếu danh sách rỗng hoặc một file tìm thấy fail. Nếu thiếu một set/thư mục test/attack file nhưng vẫn còn file khác, báo cáo có thể PASS. experiment.py:160–178 cũng ghi excluded “files_not_found”, nhưng run.py:248–264 vẫn COMPLETE nếu external không còn file đủ điều kiện. **Sửa:** kiểm expected set/folder và số file tối thiểu từ ledger; phân biệt DATA_COMPLETE và RUN_COMPLETE; fail hoặc ghi trạng thái thiếu coverage rõ trước kết luận external.
4. **P1 — Bằng chứng tách session còn yếu.** code/src/can_research/io.py:156–176 nhóm theo số cuối tên file, chọn nhóm lớn nhất làm validation; không đối chiếu metadata chuyến lái hoặc đoạn chung giữa train/validation/test. experiment.py:219–224 chỉ phát hiện file trùng hash nguyên bản trong cùng set. **Sửa:** capture ledger và near-duplicate trace audit; nếu không có metadata, giới hạn kết luận/CI. Đây là rủi ro phương pháp, chưa chứng minh có leakage thực tế.

### P2: cần bổ sung để hỗ trợ các claim mạnh

5. **P2 — Thiếu ablation payload tuyệt đối.** features.py:73–78 chưa có structural_no_absolute_payload; chỉ có no_delta. Thêm selector, test xác nhận đúng chiều và cùng window; chạy so cặp theo bảng Phần II.
6. **P2 — Chưa chọn checkpoint/hyperparameter bằng nguồn theo tiêu chí công bố.** models.py:37–69 chạy đúng 10 epoch, lưu train loss nhưng không có validation curve/early stopping. 10 epoch bằng nhau là kiểm soát ngân sách, không chứng minh hội tụ. Giữ cấu hình frozen nếu mục tiêu confirmatory, nhưng báo learning curve nguồn và phân tích sensitivity trước khi khẳng định kiến trúc tốt hơn.
7. **P2 — File manifest chưa băm toàn bộ logic chạy.** experiment.py:184–190 băm các .py trong package can_research nhưng không gồm scripts, runner và bản hướng dẫn/đóng gói; config và external ledger được ghi riêng. Thêm git revision/dirty status hoặc manifest code đầy đủ cho rerun, nhất là khi giải nén ZIP không có Git.
8. **P2 — summarize_results thiếu kiểm ma trận dự kiến.** code/scripts/summarize_results.py:44–56 chỉ chặn seed trùng; một tập con set/seed COMPLETE vẫn sinh mean/std mà không cảnh báo thiếu 12 tổ hợp chính hoặc thiếu A–D ở từng cấu hình (shift_rows bỏ qua im lặng nếu thiếu condition). Thêm báo coverage, expected grid từ config và cờ PARTIAL/CONFIRMATORY_COMPLETE; cho phép tổng hợp pilot nhưng không đặt tên như bảng xác nhận.
9. **P2 — Chưa có output theo sự kiện.** score_files lưu window_index, start/end, y_true và score (experiment.py:115–129), nhưng chưa tính event onset, false alerts/giờ hoặc latency; paired_analysis.py:22–26 bootstrap theo tên file. Thêm event policy, có test boundary, tách nhóm cơ chế; với capture/session chưa rõ, CI chỉ mô tả có điều kiện.
10. **P2 — Xử lý lỗi sớm có thể để RUNNING.** experiment.py:197–207 ghi run_manifest RUNNING trước khi đọc/parse external ledger, còn try bắt lỗi bắt đầu tại dòng 207. Nếu ledger hỏng hoặc bị xóa, file manifest có thể mãi RUNNING. Đưa khởi tạo và đọc ledger trong try/finally hoặc đặt trạng thái FAILED khi thất bại sớm. Đây là lỗi trạng thái, không phải bằng chứng sai metric đã tính.

**Điểm code đang làm đúng trong phạm vi đã xem:** parser từ chối timestamp thiếu ở timed tier, payload/DLC/ID sai và nhãn thiếu; window không đi qua ranh giới file; history được giữ qua chunk; test kiểm phép đổi tên ID; AP và FAR không được bịa cho tập thiếu lớp; source sampling quét toàn file; ngưỡng chọn từ validation nguồn; output run chặn ghi đè. Những đặc điểm này có test, nhưng 17 test tổng hợp không thay cho full-data audit, kiểm tra leakage capture hoặc kết quả mô hình.

**Thứ tự sửa mã:** gói nộp + preflight coverage → chạy một pilot nhỏ kiểm RAM/manifest/đúng số cửa sổ → khóa giao thức và chạy primary → thêm ablation/baseline/event analysis → kiểm summary completeness → build lại hai PDF. Sau mỗi sửa ảnh hưởng dữ liệu hoặc feature, tăng schema/protocol version và không gộp kết quả từ trước sửa.

### Bảng thực thi, sản phẩm và điều kiện qua cổng

| Giai đoạn | Việc chạy / số fit dự kiến | Cần lưu và đưa lại | Chỉ chuyển bước khi |
|---|---|---|---|
| G0 — Dữ liệu | Full preflight CTT và external đã bật; không fit | data_manifest, exclusions, ledger, hash, báo cáo capture overlap | Không có file dùng với schema/nhãn sai; mọi file thiếu có lý do |
| G1 — Pilot | Set 1, seed 42, primary: 4 fit; đo peak RAM và thời gian mỗi model | run_manifest, split, coverage, sampled_windows, checkpoint, metrics, predictions | COMPLETE, số window khớp preflight, không OOM, ngưỡng chỉ từ validation nguồn |
| G2 — Main | 4 set × 3 seed × 4 model = 48 fit, tính cả pilot nếu config/hash không đổi | Toàn bộ thư mục run theo set/seed, summary và ma trận A–D | Đủ 12 cặp set/seed, hai ngưỡng, bốn model, không thiếu condition |
| G3 — Giải thích | Ablation hiện có 4×3×11 = 132 fit nếu chạy toàn bộ; ưu tiên các cặp ở Phần II. LR-structural + XGB-raw thêm 24 fit | Config riêng có protocol version, checkpoint, bảng paired theo set/seed | Mọi cặp chỉ đổi một yếu tố và cùng mẫu/split; báo cả kết quả âm tính |
| G4 — Ngoại bộ và nhạy W | Content 1 set×3 seed×3 model = 9 fit; W32/W128 tổng 4×3×2×2 = 48 fit nếu chạy đủ | External manifest, family/label ledger, bản kiểm SPEED, event metrics khi có onset | Không trộn timed/content, không gộp nhãn theo cơ chế khác, không dùng target để chọn ngưỡng |
| G5 — Viết và nộp | Sinh bảng từ run hoàn tất, kiểm song ngữ và build PDF | Hai source bundle, hai PDF, logs, rubric đối chiếu | Biên dịch từ ZIP sạch, trích dẫn đầy đủ, số liệu VI/EN nhất quán |

Các số fit là số cấu hình theo JSON hiện tại, không là ước tính giờ GPU. Chạy một pilot G1, đo thời gian, peak RAM và dung lượng checkpoint/predictions thật rồi tính nguồn lực còn lại. Nếu sửa parser, feature, split hoặc nhãn giữa G1 và G2, kết quả pilot không được gộp vào G2. Lệnh hiện có trong RERUN_GUIDE_VI.md; trước khi dùng, sửa các đường dẫn thesis cũ ở mục 9 như phát hiện P0 số 1.

## P0 — Bắt buộc

### P0.1. Chốt dữ liệu, nhãn và provenance

**Hiện trạng:** results_vi.tex đã ghi nhận nhãn Automotive v2, CICIoV SPEED tạm loại, OTIDS tắt và CAN-MIRGU tìm thấy đệ quy. Danh mục code/results/inventory_reorg_final kiểm tra tối đa 128 frame đầu mỗi file; 293 file và 0 lỗi ở đó không chứng nhận toàn bộ dữ liệu. Full preflight trên mọi file dùng cho xác nhận chưa có.

**Cần làm:** một ledger theo file gồm URL và phiên bản tải, hash, xe, capture/session, attack family, schema, thứ tự thời gian, loại nhãn (frame chèn hay khoảng tấn công), số frame/window, lý do loại. Chạy preflight toàn file, lưu log và bản cấu hình. Xác minh nguồn chuẩn CICIoV SPEED trước khi bật lại; không tự sửa 4.989 byte khác giữa hai bản xuất. OTIDS chỉ được dùng sau khi kiểm nguồn gốc nhãn và thứ tự chuỗi.

**Viết vào:** method_vi.tex mục “Hợp đồng dữ liệu”, results_vi.tex mục chất lượng dữ liệu và các đoạn tương ứng bản Anh. Tóm tắt ledger trong phụ lục. **Đạt khi:** mọi dòng kết quả truy được về file/hash/chính sách nhãn và mọi file loại trừ có lý do.

### P0.2. Tách nhãn suspension khỏi nhãn frame độc hại được chèn

**Hiện trạng:** code/results/suspension_semantics_audit.json ghi năm log suspension với 2.976.163 frame, trong đó 976.309 frame mang nhãn 1; ID bị đình chỉ không xuất hiện trong khoảng nhãn 1. Bản thảo mới nêu tìm thấy các log này, chưa giải thích rõ ngữ nghĩa nhãn.

**Cần viết:** Y_window = 1 khi cửa sổ có ít nhất một frame **mang nhãn dương theo chính sách dataset**. Với suspension, nhãn 1 đánh dấu khoảng bị tấn công trên những frame còn lại, không có nghĩa từng frame đó được attacker chèn. Báo injection, masquerade và suspension riêng; dùng event/interval cho cơ chế xóa frame. Bài gốc [CAN-MIRGU](https://www.ndss-symposium.org/wp-content/uploads/vehiclesec2024-43-paper.pdf) mô tả chính sách nhãn này. [can-sleuth](https://link.springer.com/article/10.1007/s10207-025-01038-8) cảnh báo F1 dựa trên nhãn frame của suppress có thể gây hiểu sai.

**Viết vào:** background_vi.tex (dataset), method_vi.tex (định nghĩa nhãn), results_vi.tex (bảng theo cơ chế) và EN tương ứng. **Đạt khi:** không còn diễn giải dương tính suspension thành số frame độc hại được chèn.

### P0.3. Chạy v2 và thay bảng “chờ chạy” bằng bằng chứng

**Hiện trạng:** bảng tab:pending trong results_vi.tex và results_en.tex còn chờ RQ1–RQ4. code/configs/primary.json định nghĩa 4 set × 3 seed × 4 cấu hình = 48 lần fit dự kiến. Đây chưa phải kết quả đã chạy.

**Cần làm:** chốt endpoint chính, ví dụ attack recall ở ngưỡng chọn trên validation nguồn và FAR quan sát trên đích; báo thêm ngưỡng 0,5. Chạy đủ A–D cho các tổ hợp hợp lệ. Mỗi bảng cần run ID, set, seed, model, representation, threshold, TP/FP/TN/FN, N+ và N−, precision, recall, F1, AP, FAR, prevalence và ca N/A. Trình bày riêng B và D, không chỉ trung bình. Chỉ dùng run COMPLETE có config, code hash, data hash và checkpoint nhất quán. Nếu target đã được xem ở thăm dò, gọi đây là rerun kiểm chứng sau chỉnh giao thức, không mô tả như test chưa từng được xem.

**Viết vào:** thay bảng chờ ở hai file results; cập nhật cùng lúc abstract, introduction và conclusion. **Đạt khi:** mọi kết luận RQ1–RQ4 trỏ tới run có thể kiểm lại, kể cả kết quả kém.

### P0.4. Kiểm rò rỉ và xác định đơn vị độc lập

**Hiện trạng:** method_vi.tex chia train/validation theo hậu tố vòng ghi nhưng chưa xác minh hậu tố có nghĩa là chuyến lái độc lập. Một số log Automotive v2 cùng nền benign. Bốn set CTT cũng không tương đương bốn cặp xe/capture hoàn toàn độc lập.

**Cần làm:** manifest source/validation/test theo xe, capture, ngày/chuyến khi có metadata; kiểm hash toàn file, đoạn trùng và attack trace dựng từ cùng benign trace. Công bố việc dùng lại capture/xe. Ba seed đo bất định huấn luyện trên split cố định, không tăng số xe. Bootstrap theo capture/session có căn cứ; nếu chỉ biết file, ghi CI có điều kiện theo file.

**Viết vào:** method_vi.tex mục tách nguồn, results_vi.tex phần validity, phụ lục và EN tương ứng. **Đạt khi:** người đọc xác định được mọi ranh giới học, chọn ngưỡng và đánh giá.

### P0.5. Bản nộp phải build và đóng gói lại được

**Hiện trạng 05/11/2026:** đã gộp mỗi bản thành một `main.tex`, cập nhật script tái tạo bảng, guide và script đóng gói. Hai PDF biên dịch thành công vào `code/output/thesis_compile_check/`. ZIP mới có manifest/checksum và đã được giải nén, biên dịch thử độc lập trong thư mục tạm trên cùng máy; chưa kiểm trên máy khác.

**Cần làm:** đọc PDF để tìm tràn bảng, font lỗi, citation [?], hình sai, thuật ngữ/số liệu hai bản lệch nhau. Lấy rubric/mẫu áp dụng cho khóa hiện hành từ khoa hoặc giảng viên rồi đối chiếu bìa, bố cục, phụ lục, yêu cầu nộp. **Đạt khi:** cả VI và EN được kiểm thị giác và đúng thể thức hiện hành.

## P1 — Cần để bảo vệ tính mới và phương pháp

### P1.1. Bảng đối chiếu công trình gần nhất

**Hiện trạng:** related_vi.tex đã được bổ sung can-sleuth, Koltai, MTFF, Jo--Kim và Obafemi cùng bản EN, nhưng bảng hiện mới định tính và chưa có tái lập định lượng. “Bỏ ID + thêm cấu trúc + Transformer + nhiều dataset” chưa đủ chứng minh thuật toán mới.

**Cần viết:** ma trận mỗi bài gồm: ID làm giá trị hay khóa, payload/history, timing/transition, có dùng normal target data hoặc nhãn đích không, xe/capture, đơn vị frame/window/event, code và phép so cùng giao thức. Định vị đóng góp hẹp, có thể kiểm chứng: trong điều kiện source-only, tổ hợp payload history và quan hệ cục bộ giúp/hại transfer ở cơ chế nào. Tính bất biến với phép đổi tên ID nhất quán là tính chất toán học hẹp, không chứng minh độc lập danh tính xe.

**Nguồn đã thêm:** [Koltai et al. 2026](https://arxiv.org/abs/2606.30430), [Kidmose et al. 2025](https://link.springer.com/article/10.1007/s10207-025-01038-8), [Dong et al. 2026](https://pmc.ncbi.nlm.nih.gov/articles/PMC13468888/) và các bài liệt kê ở đầu Phần I; tiếp tục kiểm khả năng tái lập định lượng trước khi đưa số liệu của họ vào bảng kết quả.

### P1.2. Tách ảnh hưởng của biểu diễn và classifier

**Hiện trạng:** primary có Transformer raw/structural, XGBoost structural và LR raw. So hai Transformer là cặp đúng câu hỏi representation; so XGB structural với LR raw không cô lập feature. Ablation chưa có structural giữ delta nhưng bỏ payload tuyệt đối.

**Cần làm:** thêm LR structural và XGB raw để thành 3 họ classifier × 2 representation. Ưu tiên raw, raw-no-ID, raw-plus-structural, structural, structural-no-delta và structural-no-absolute-payload mới, trên cùng split/window/checkpoint rule. Xem learning curves và tiêu chí chọn checkpoint: 10 epoch chung chưa chứng minh các mô hình hội tụ. Nếu khẳng định hơn công trình gần, tái lập trung thành ít nhất một baseline relational/transition, kiểm fidelity ở thiết lập gốc rồi mới adapter CTT; ghi rõ mọi thay đổi. Structural XGB không được gọi là Graph IDS.

**Viết vào:** method_vi.tex bảng ablation và results_vi.tex bảng ghép cặp; EN tương ứng. **Đạt khi:** mỗi claim về ID, payload history hoặc Transformer có một phép so chỉ thay yếu tố tương ứng.

### P1.3. Phân tích cơ chế lỗi

Delta hiện là trị tuyệt đối của chênh byte trước cùng ID; không có DBC nên không biết counter, checksum, bit-field hay đơn vị vật lý. History cập nhật cả qua frame mang nhãn tấn công; một chuỗi tấn công dài có thể làm delta nhỏ dần, đây là giả thuyết cần thử. Feature hiện không có bộ quét deadline trực tiếp cho ID đã biến mất.

**Cần làm:** báo false negative cho replay/masquerade, recall theo thời gian từ event onset, suspension theo event/interval; so cùng benign trace khi có thể. Nếu thử baseline timeout theo ID, ghi ngân sách profile xe đích: dùng profile lành đích là một chế độ thích nghi riêng. Stress test thay payload có kiểm soát phải ghi là synthetic. Viết giới hạn này trong method và discussion của hai bản, không gọi delta byte là tốc độ cảm biến.

### P1.4. Probe có control và đồng thời đo khả năng phát hiện

**Hiện trạng:** bản thảo mới đề nghị LR probe xe/tấn công, chưa có kết quả v2. Probe xe gần chance có thể do embedding mất cả tín hiệu tấn công.

**Cần làm:** probe cùng split/nhóm, cùng ngân sách cho engineered features, raw embedding và structural embedding; thêm embedding hằng/ngẫu nhiên, cân bằng xe × attack family khi đủ mẫu, báo attack utility song song. Không chọn IDS bằng probe trên target rồi gọi target evaluation là source-only. [Hewitt & Liang](https://aclanthology.org/D19-1275/) đề xuất control tasks trong NLP; áp dụng nguyên tắc này sang CAN là **đề xuất phương pháp**, không phải kết quả CAN đã công bố.

### P1.5. Báo gánh nặng cảnh báo và bất định đúng mẫu số

**Hiện trạng:** FAR trên 100.000 benign windows và AP được định nghĩa nhưng chưa có FP theo giờ, false-alert events, event recall/latency, prevalence từng tập và CI theo session thực.

**Cần làm:** với dữ liệu có timestamp/onset đã xác minh, báo benign hours, FP windows/giờ, quy tắc gộp alert, false-alert events/giờ, sự kiện phát hiện/bỏ sót, latency tới cảnh báo đầu, thời lượng cửa sổ p50/p95/p99. CICIoV thiếu timestamp thì giữ các metric theo thời gian là N/A. AP đi cùng positive prevalence; không so AP các tập khác prevalence như cùng độ khó. Báo N− và FP khi FAR rất thấp; 0 FP quan sát không chứng minh FAR thật bằng 0. [Saito & Rehmsmeier](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0118432) hỗ trợ vai trò PR trên dữ liệu lệch lớp, không thay việc báo mẫu số.

## P2 — Chọn lọc khi còn thời gian

- W=32/128: chạy trên split và quy tắc ngưỡng cố định; báo tradeoff theo **thời lượng thực** của cửa sổ.
- ROAD hoặc CTT v1.5: bổ sung cơ chế còn thiếu sau khi kiểm provenance, nhãn và trùng lặp. Với suppress, metric frame thông thường có thể vô nghĩa; thiết kế đánh giá event trước.
- Runtime/nhúng: chỉ giữ tuyên bố nếu đo parser + feature + inference batch=1 và chờ đủ W trên phần cứng ghi rõ, kèm warmup và p50/p95/p99. GPU batch throughput không là latency cảnh báo.
- Baseline dùng dữ liệu lành đích: nếu so với nghiên cứu universal/relational có target calibration, báo riêng lượng target data và giai đoạn sử dụng. Không xếp hạng chung như cùng điều kiện source-only.

## Thứ tự thực hiện

1. Chốt ledger, nhãn và full preflight (P0.1–P0.2); dừng huấn luyện xác nhận nếu dữ liệu dùng có schema/nhãn/thứ tự chưa rõ.
2. Khóa protocol, kiểm capture overlap, chạy primary và lưu manifest (P0.3–P0.4). Chỉ tổng hợp run COMPLETE cùng giao thức.
3. Viết bảng related work, chạy ablation/baseline theo claim, phân tích lỗi và probe (P1); không chọn cấu hình bằng test đích rồi báo là chưa từng nhìn.
4. Cập nhật số thật vào VI/EN, chỉnh mức khẳng định trong abstract/conclusion, build và đọc hai PDF từ gói nộp (P0.5). Xin rubric hiện hành để đối chiếu các mục hình thức.

Mỗi câu kết luận cuối cần nêu phạm vi xe/set/family, đơn vị frame/window/event, ngưỡng và mẫu số, số liệu truy ngược về run, cùng giới hạn áp dụng. Nếu D hoặc suspension thất bại, nêu ngay trong phần thảo luận. Phân biệt “identifier-renaming invariant” với “vehicle-agnostic”, “unseen attack” với “zero-day”, và “source threshold selection” với “target adaptation”. Điểm tối đa phụ thuộc rubric và hội đồng; tiêu chí có thể kiểm được là mọi claim có bằng chứng, mọi giới hạn được nói rõ và hai bản nộp tái lập được.
