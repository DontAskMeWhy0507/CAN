"""Bilingual supplement from the separately verified post-hoc MixStyle study."""
from pathlib import Path
import json
import re
import pandas as pd
from .evidence import valid_manifest, sha
from .render import table as base_table, n, sec, sub

CODE = Path(__file__).resolve().parents[1]
STUDY = CODE/'results/mixstyle_posthoc_2026-11-09'

def table(caption,label,headers,rows,widths):
    return base_table(caption,label,headers,[[str(v).replace('_',r'\_') for v in row] for row in rows],widths)


def integrate(text, bib, lang):
    vi = lang == 'vi'
    pick = lambda a,b: a if vi else b
    if 'sec:mixstyle-study' in text:
        raise ValueError('Supplement already present; rebuild from canonical sources')
    audit = STUDY/'analysis'
    valid_manifest(audit/'manifest.json')
    report = json.loads((audit/'final_report.json').read_text())
    if report['status']!='VERIFIED_COMPLETE' or report['unperformed_secondary_studies']:
        raise ValueError('Incomplete MixStyle evidence')
    if (report['new_fits'],report['reused_baselines'],report['external_captures']) != (12,24,57):
        raise ValueError('Unexpected study matrix')
    means = pd.read_csv(audit/'six_method_equal_set.csv').set_index(['method','condition'])
    probe = pd.read_csv(audit/'probe_means.csv').set_index(['representation','target','control'])
    runtime = pd.read_csv(audit/'runtime_remeasured.csv')
    external = pd.read_csv(audit/'external_dataset_mean_seed.csv')
    names = dict(raw_transformer='Raw', structural_transformer='Structural', structural_mixstyle='Structural + MixStyle',
                 canbertplus='CANBERT+ adapted', canlp='CANLP-char-DNN adapted', assoc_rules_crysys='CrySyS-AssocRules/W64')
    methods = ['raw_transformer','structural_transformer','structural_mixstyle']
    candidate = means.loc[('structural_mixstyle','B')]
    structural = means.loc[('structural_transformer','B')]
    raw = means.loc[('raw_transformer','B')]
    title = pick('Thí nghiệm bổ sung: Structural Transformer với MixStyle','Additional study: Structural Transformer with MixStyle')
    body = '\\label{sec:mixstyle-study}\n'
    body += pick(r'''MixStyle~\cite{zhou2021mixstyle} trộn thống kê đặc trưng khi huấn luyện. Công trình gốc nghiên cứu CNN và miền thị giác; kết quả đó không xác nhận hiệu quả cho CAN một xe nguồn. Bản thích ứng ở đây tính mean/std theo trục frame sau input projection, trước positional embedding; chỉ ghép mẫu có cùng nhãn cửa sổ nguồn. Đó là lựa chọn thiết kế được kiểm tra, không phải thuật toán hoàn toàn mới hoặc tái lập nguyên trạng bài gốc.

Xác suất kích hoạt là 0,5, tham số Beta là 0,1, epsilon là $10^{-6}$; variance dùng population estimator và thống kê được detach. Mẫu tự ghép hoặc lớp singleton được giữ nguyên. Khi suy luận, phép trộn là identity và không nhận nhãn. Không sửa byte CAN hoặc tái tạo frame vật lý. Encoder, W64, đặc trưng 30 chiều, cửa sổ nguồn, split, 10 epoch, AdamW và ngưỡng nguồn giữ như đối chứng Structural. Cấu hình duy nhất được chạy ở bốn set và ba seed; không chọn seed hoặc siêu tham số theo điểm đích.

Vòng này gồm 12 fit IDS mới và 24 baseline tái sử dụng, tách khỏi 144 fit bổ sung trước đó. Một pilot hai epoch trên 80 cửa sổ chỉ kiểm tra phần mềm. Các checkpoint Set 1 được kiểm tra trên cùng 57 capture ngoại bộ, không phải 57 capture mới; không cộng các nhóm thành quan sát độc lập. Toàn bộ nghiên cứu này là hậu nghiệm sau khi các test cũ đã được xem.
''',r'''MixStyle~\cite{zhou2021mixstyle} mixes feature statistics during training. Its original evidence concerns CNNs and visual domains, not single-source CAN intrusion detection. This adaptation computes mean/std across frame positions after input projection and before positional embeddings, pairing only source windows with the same binary label. This is an evaluated design choice, not an entirely new algorithm or unchanged reproduction of the original paper.

Activation probability is 0.5, Beta concentration 0.1 and epsilon $10^{-6}$; variance uses the population estimator and statistics are detached. Self-paired and singleton examples remain unchanged. At inference the mixer is an identity and receives no labels. CAN bytes are not edited and physical frames are not synthesized. Encoder, W64, 30-dimensional inputs, source windows, split, ten epochs, AdamW and source threshold policy match Structural. One fixed configuration covers four sets and three seeds; target scores do not select seeds or hyperparameters.

This round adds 12 IDS fits and reuses 24 baselines, separately from the earlier 144 additional fits. A two-epoch pilot on 80 windows checks software only. Set 1 checkpoints are evaluated on the same 57 external captures, not 57 new captures; these groups are not independent observations. This entire study is post-hoc after earlier targets had been inspected.
''')
    rows = [[c,names[m],n(means.loc[(m,c),'Recall']),n(means.loc[(m,c),'FAR_per_100k']/1000,4),n(means.loc[(m,c),'AP']),n(means.loc[(m,c),'Attack_F1'])] for c in 'ABCD' for m in methods]
    body += table(pick('MixStyle: trung bình seed trong set rồi trọng số ngang nhau giữa set; FAR tính bằng phần trăm','MixStyle: average seeds within set, then weight sets equally; FAR in percent'), 'tab:mixstyle-ad', ['A--D',pick('Pipeline','Pipeline'),'Recall',r'FAR (\%)','AP','F1'],rows,[1,4.3,1.6,2,1.5,1.5])
    body += pick('Ở tiêu chí chính B, recall MixStyle là ','At the primary B criterion, MixStyle recall is ')+n(candidate.Recall)+pick(', so với Structural ', ', versus Structural ')+n(structural.Recall)+pick(' và Raw ',' and Raw ')+n(raw.Recall)+'. '
    body += pick('So với Structural, recall tăng ','Relative to Structural, recall increases by ')+n((candidate.Recall-structural.Recall)*100,2)+pick(' điểm phần trăm nhưng FAR cũng tăng ',' percentage points, but FAR also increases by ')+n((candidate.FAR_per_100k-structural.FAR_per_100k)/1000,2)+pick(' điểm phần trăm. AP tăng không thay thế tiêu chí recall. So với Raw, recall vẫn thấp hơn; không có cải thiện đồng thời ở B.\n',' percentage points. Improved AP does not replace the recall criterion. Recall remains below Raw; there is no simultaneous B improvement.\n')
    body += pick('Ở A/C/D, trung bình recall cao hơn Raw và FAR thấp hơn Raw, nhưng mức tăng recall chỉ xuất hiện ở 2/4, 4/4 và 1/4 set tương ứng. Vì vậy, trung bình thuận lợi ở D không phải cải thiện nhất quán giữa các xe. FAR B/D vẫn trên 64\\%, rất xa ngân sách nguồn 0,1\\%; ngân sách nguồn không bảo đảm ngân sách đích. Khoảng bootstrap theo capture và biến thiên seed được báo riêng trong dữ liệu kèm theo; không suy CI cho quần thể xe.\n','In A/C/D, mean recall is higher and FAR lower than Raw, but recall improves in only 2/4, 4/4 and 1/4 sets respectively. The favourable D average is therefore not a consistent cross-vehicle improvement. B/D FAR remains above 64\\%, far above the source budget of 0.1\\%; the source budget does not guarantee the target budget. Capture-bootstrap intervals and seed variation are reported separately in accompanying data, without vehicle-population inference.\n')
    rows = [[names[m],n(means.loc[(m,'B'),'Recall']),n(means.loc[(m,'B'),'FAR_per_100k']/1000,4),n(means.loc[(m,'B'),'AP'])] for m in names]
    body += table(pick('Sáu pipeline ở B; điểm của các bản thích ứng trong cùng giao thức','Six pipelines at B; adapted implementations under the same protocol'),'tab:mixstyle-six',[pick('Pipeline','Pipeline'),'Recall',r'FAR (\%)','AP'],rows,[6,2,2.2,2])
    body += pick('Bảng không xếp hạng trực tiếp các điểm công bố gốc. AssocRules có recall/FAR bằng không tại điểm dự đoán toàn benign; đó không phải phát hiện hiệu quả.\n','The table does not rank original published scores directly. AssocRules recall/FAR are zero at an all-benign operating point, not an effective detector.\n')
    body += sub(pick('Probe, ngoại bộ và chi phí xử lý','Probes, external evaluation and processing cost'),'')
    reps = ['raw','structural','structural_mixstyle']
    body += table(pick('Probe trên cùng 3.800 mẫu train và 4.640 mẫu validation; balanced accuracy','Probes on the same 3,800 training and 4,640 validation samples; balanced accuracy'),'tab:mixstyle-probe',['Pipeline',pick('Xe','Vehicle'),pick('Tấn công','Attack')],[[r,n(probe.loc[(r,'vehicle','learned'),'balanced_accuracy']),n(probe.loc[(r,'attack','learned'),'balanced_accuracy'])] for r in reps],[6,3,3])
    body += pick('Mức cơ hội là 0,25 cho xe và 0,5 cho tấn công. Probe xe MixStyle đạt 0,9527, cao hơn Structural 0,9488; phép đo không ủng hộ giảm khả năng giải mã tuyến tính danh tính xe. Attack probe tăng nhẹ lên 0,7737. Các đối chứng constant/random/permuted được giữ đủ; phiên ghi độc lập và tính bất biến xe vẫn chưa được chứng minh.\n','Chance is 0.25 for vehicle and 0.5 for attack. MixStyle vehicle decoding reaches 0.9527, above Structural 0.9488; this does not support reduced linear vehicle-identity decodability. Attack decoding rises slightly to 0.7737. Constant/random/permuted controls are retained; independent driving sessions and vehicle invariance remain unestablished.\n')
    rows = [[r.dataset,r.method,n(r.Recall),n(r.FAR_per_100k/1000,4)] for r in external.itertuples()]
    body += table(pick('Ngoại bộ: gộp cửa sổ trong dataset/seed rồi trung bình seed; FAR phần trăm','External: pool windows within dataset/seed, then average seeds; FAR in percent'),'tab:mixstyle-external',['Dataset','Pipeline','Recall',r'FAR (\%)'],rows,[4.4,4.8,1.6,2.2])
    body += pick('MIRGU attack có recall MixStyle 0,0486 và FAR 1,8267\\%, so với Structural 0,0546 và 2,7018\\%: giảm báo động giả đi kèm bỏ sót nhiều hơn. CICIoV vẫn có recall và FAR đều 100\\%, nghĩa là dự đoán toàn attack. Renault DoS giữ recall 0,9984 và FAR giảm từ 0,1886\\% xuống 0,1467\\%, nhưng chưa đạt 0,1\\%. Opel FAR tăng so với Structural. Các tập benign-only giữ recall/AP không xác định; giữ nguyên loại trừ OTIDS và cách ly CICIoV SPEED.\n','MIRGU attack recall/FAR are 0.0486/1.8267\\% for MixStyle versus Structural 0.0546/2.7018\\%: fewer false alarms accompany more missed attacks. CICIoV recall and FAR remain 100\\%, predicting every window as attack. Renault DoS retains recall 0.9984 while FAR falls from 0.1886\\% to 0.1467\\%, still above 0.1\\%. Opel FAR increases relative to Structural. Benign-only recall/AP remain undefined; OTIDS exclusions and CICIoV SPEED quarantine are unchanged.\n')
    body += table(pick('Đo lại cùng phiên, batch một, 900 cửa sổ mỗi cấu hình; ms','Remeasured in the same session, batch one, 900 windows per configuration; ms'),'tab:mixstyle-runtime',[pick('Thiết bị','Device'),'Pipeline','Median','P95'],[[r.device,r.representation,n(r.p50_ms,3),n(r.p95_ms,3)] for r in runtime.itertuples()],[2,5.5,2.2,2.2])
    body += pick('Phép đo gồm đọc CSV, kiểm tra, tạo cả hai biểu diễn và inference; mỗi lần có 20 warmup và 300 mẫu, lặp ba lần. GPU trước đo tải 2\\% và có khoảng 6,9 GB VRAM trống. Máy bàn dùng chung, cache, thứ tự đo và tần số xung nhịp hạn chế diễn giải chênh lệch nhỏ; chưa chứng minh MixStyle nhanh hơn. Không đo thời gian thu cửa sổ hoặc deadline ECU.\n','Measurement includes CSV reading, validation, both representations and inference; each of three repetitions uses 20 warmup and 300 measured windows. Pre-measurement GPU utilization was 2\\% with approximately 6.9 GB free VRAM. Shared desktop load, caching, measurement order and clock frequency limit interpretation of small differences; faster MixStyle inference is not established. Acquisition time and ECU deadlines are not measured.\n')
    body += pick('Kết quả này bổ sung một đánh đổi có đối chứng, không thay đổi câu trả lời RQ1 chính. Một số chỉ số tăng nhưng điều kiện B và probe không hỗ trợ chọn MixStyle như lời giải tổng quát cho chuyển xe.\n','This study adds a controlled tradeoff without changing the primary RQ1 answer. Some metrics improve, but B and probe results do not support MixStyle as a general solution to cross-vehicle transfer.\n')
    anchor = '\\chapter{'+pick('Kết luận','Conclusions')+'}\\label{chap:conclusion}'
    if text.count(anchor)!=1: raise ValueError('Conclusion boundary mismatch')
    text = text.replace(anchor,sec(title,body)+'\n'+anchor)
    brief = pick(r' Một vòng hậu nghiệm riêng với 12 fit Structural--MixStyle đạt recall B 0,8194 nhưng FAR 64,54\%; probe xe 0,9527 chưa ủng hộ giảm thông tin danh tính xe.',r' A separate post-hoc round of 12 Structural--MixStyle fits yields B recall 0.8194 with FAR 64.54\%; vehicle decoding of 0.9527 does not support reduced vehicle-identity information.')
    marker = '\\noindent\\textbf{\\textit{'+pick('Từ khóa:','Keywords:')
    pos=text.index(marker)
    text=text[:pos].rstrip()+brief+'\n\n'+text[pos:]
    future='\\section{'+pick('Hướng nghiên cứu tiếp theo','Future research')+'}'
    if text.count(future)!=1: raise ValueError('Future research boundary mismatch')
    text=text.replace(future,sub(pick('Kết luận từ thí nghiệm MixStyle','Conclusion from the MixStyle study'),pick('MixStyle tăng recall B so với Structural nhưng tăng FAR, vẫn thấp hơn Raw về recall và không giảm probe xe. Do đó chưa có căn cứ chọn nó làm mô hình cuối để khẳng định ưu thế toàn diện. Huấn luyện đa xe với xe đích tách hẳn khỏi train là một giả thuyết nghiên cứu tiếp theo, cần baseline dùng cùng dữ liệu và giao thức mới được khóa trước đánh giá.','MixStyle increases B recall relative to Structural but raises FAR, remains below Raw recall, and does not reduce vehicle decoding. It therefore does not justify selecting a final model with universal superiority. Multi-vehicle training with the target vehicle excluded is a future hypothesis requiring baselines with the same data and a protocol fixed before evaluation.'))+future)
    entry=(CODE/'notes/mixstyle_sources_2026-11-09/references.bib').read_text(encoding='utf-8')
    entry=re.sub(r'^\s*note = \{.*\}\n','',entry,flags=re.M)
    bib += '\n'+entry
    return text,bib,dict(status='VERIFIED',study_manifest_sha256=sha(audit/'manifest.json'),additional_reference='zhou2021mixstyle',new_fits=12,reused_baselines=24,external_captures_reused=57)
