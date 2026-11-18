"""Import verified shared-protocol results into both thesis languages.

--prepare adds methods and explicit pending blocks without importing partial scores.
--watch waits for the real notebooks, then verifies and imports the complete matrix.
Scientific runner sources/configuration are never modified.
"""
# CANONICAL WRITER ROUTE: historical generation requires explicit opt-in.
if __name__ == '__main__':
    import sys as _final_sys
    if '--legacy-manuscript' in _final_sys.argv:
        _final_sys.argv.remove('--legacy-manuscript')
    else:
        from pathlib import Path as _FinalPath
        import subprocess as _final_subprocess
        _final_args = _final_sys.argv[1:]
        if not any(v in _final_args for v in ['--check','--build']):
            _final_args = ['--build', *_final_args]
        raise SystemExit(_final_subprocess.call([_final_sys.executable, str(_FinalPath(__file__).with_name('finalize_thesis_for_supervisor.py')), *_final_args]))

from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import time
import zipfile

ROOT = Path(__file__).resolve().parents[2]
CODE = ROOT / 'code'
MERGED = CODE / 'results/comparison_merged_fast'
REPORT = CODE / 'results/manuscript_comparison_update.json'
METHODS = ['raw_transformer', 'structural_transformer', 'canbertplus', 'canlp', 'assoc_rules_crysys']
LABELS = dict(zip(METHODS, ['Raw TF', 'Structural TF', 'CANBERT+ adapted', 'CANLP-char-DNN adapted', 'CrySyS-AssocRules/W64']))


def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def atomic_json(path, data):
    tmp = path.with_suffix('.json.saving')
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    tmp.replace(path)


def block(text, key, body, anchor):
    start, end = '% BEGIN COMPARISON ' + key, '% END COMPARISON ' + key
    replacement = start + '\n' + body.strip() + '\n' + end + '\n'
    if start in text:
        pattern = re.escape(start) + r'\n.*?' + re.escape(end) + r'(?:\n|$)'
        text, count = re.subn(pattern, lambda _: replacement, text, flags=re.S)
        assert count == 1
        return text
    assert text.count(anchor) == 1, (key, anchor)
    return text.replace(anchor, replacement + '\n' + anchor)


METHOD_VI = r'''
\section{Phép so sánh thực thi trên CTT: nội dung và thứ tự file}\label{sec:comparison-protocol}
\textbf{Giao thức đang thực thi là \code{ctt-content-order-comparison-v1}.}
Thiết kế v2.1 có thời gian trong các mục trước là đặc tả tham chiếu; không phải lược đồ của ma trận năm mô hình này. Quét toàn bộ 236 file CTT cho thấy 193.240.845 khung dữ liệu, 3.019.271 cửa sổ W64 hoàn chỉnh và 12.527 lần timestamp giảm trong 100 file. Số cửa sổ trên là toàn bộ kho dữ liệu, bao gồm cả vai trò huấn luyện, validation và kiểm thử; không phải mẫu số test của mỗi mô hình. Chênh lệch 236 so với tổng số dòng 193.241.081 là một dòng tiêu đề mỗi file. Số dòng và số khung dữ liệu không được dùng thay thế nhau.

Cache giữ nguyên ID, DLC, payload, nhãn, timestamp và thứ tự dòng; không sắp xếp lại, xóa trùng hay dựng thời gian. Phép so bỏ raw index 28 và structural index 26--27 theo chỉ số bắt đầu từ 0: raw còn 28 chiều và structural còn 30 chiều. Các đặc trưng lịch sử được tính theo thứ tự file, không diễn giải thành chu kỳ vật lý. Nhánh timed vẫn bị chặn cho tới khi nguồn timestamp được xác minh. Hash manifest cache là \code{03a6bbf16efb4f583ca5566025c8bdc3cc0b65a7138a0a29f652505b2c367f29}.

Ma trận gồm bốn set, seed 42/43/44 và năm phương pháp: tổng 60 đơn vị IDS, mỗi đơn vị đánh giá A--D. Pretrain và fine-tune của CANBERT+ là hai giai đoạn trong một đơn vị, không phải hai cell độc lập. W64 không chồng lặp và không nối file. Reservoir lấy tối đa 1.000 cửa sổ mỗi lớp mỗi file trên toàn bộ nhóm huấn luyện nguồn, sampling seed 20261103. Các phương pháp nhận cùng chỉ mục mẫu nguồn. Validation tách theo nhóm hậu tố recording-round; vocabulary, TF-IDF và mọi tham số học chỉ dùng nguồn.

\subsection{Đối thủ, supervision và thay đổi so với công bố}
Raw và Structural Transformer dùng cùng kiến trúc bộ mã hóa, mẫu nguồn, CE/AdamW/Cosine, 10 epoch, batch 128 và learning rate 0,001; khác biệt chính là biểu diễn 28/30 chiều. Chênh lệch này kiểm tra gói biểu diễn, chưa tách được ảnh hưởng bỏ ID khỏi từng đặc trưng cấu trúc.

CANBERT+~\cite{won2026canbertplus} dùng module BERT/MLM của tác giả, hidden 768, 6 lớp và 12 head. Vocabulary chỉ từ nguồn; pretrain masked-ID 15\% trên benign nguồn trong 3 epoch, sau đó fine-tune nhãn frame 3 epoch, batch 8. Chuyển vòng lặp Lightning sang PyTorch, lấy mẫu nguồn chung, split theo nhóm, W64, epoch cố định và bảo đảm có token mask trong batch là các thay đổi được công bố ở đây. Điểm cửa sổ là điểm frame lớn nhất, không phải kết quả định vị frame.

CANLP~\cite{balasubramanian2025canlp} được thích ứng thành char TF-IDF unigram, tối đa 256 bigram và ID/2048, tiếp theo Dense 128/64 với dropout 0,15 và hai lớp đầu ra. Bản PyTorch dùng Adam 0,001, batch 512, 30 epoch, nhãn frame gốc và max score/W64. TF-IDF fit trên các frame thuộc mẫu huấn luyện nguồn. Split nguồn theo nhóm, không xóa trùng, nhãn nhị phân và epoch cố định thay lựa chọn checkpoint của notebook gốc; tên báo cáo là CANLP-char-DNN adapted.

CrySyS-AssocRules/W64 lấy implementation association rules trong framework~\cite{koltai2026trust}, fit chỉ benign nguồn. Độ dài/stride 64/64 thay 900/450 của implementation tham chiếu; không ghép quan hệ qua khoảng trống giữa mẫu được chọn. Giữ k-cluster mặc định 300, distance threshold 0,3 và itemset tối đa 3 khi học, 2 khi chấm. Đây là baseline được thích ứng từ framework, không phải tuyên bố tái lập nguyên trạng một phương pháp khác có tên gần giống. Commit của CANBERT+, CANLP và CrySyS lần lượt là \code{4c81d9b08e6e0c17b8e70bdab518209e399f0dbe}, \code{8df8bb74a7aa9925187f4faff05d6c8b824ba5d1} và \code{59b9f29f81b0f56f49c218cb1bd8e97552b8d22c}.

Các điều kiện supervision và ngân sách tính toán khác nhau: Transformer học nhãn cửa sổ, CANBERT+ có thêm pretrain benign và nhãn frame, CANLP học nhãn frame, AssocRules chỉ học benign. Vì vậy đây là so sánh pipeline dưới giao thức dữ liệu/đánh giá chung, không phải ablation cùng ngân sách hay phép xếp hạng trực tiếp các điểm công bố gốc. Mọi bản thích ứng phải giữ tên tương ứng trong bảng.

\subsection{Ngưỡng, ghép cặp, tăng tốc và giới hạn diễn giải}
Ngưỡng được chọn từ validation nguồn để tối đa recall trong ngân sách FAR 100/100.000 cửa sổ benign nguồn. Không hiệu chỉnh bằng nhãn đích; FAR đích có thể vượt ngân sách. Báo recall cùng FAR, F1 lớp tấn công, AP và số đếm TP/FP/TN/FN. Max frame score/W64 chỉ đồng nhất đơn vị quyết định, không chứng minh nhãn supervision hoặc chi phí các phương pháp bằng nhau.

Phép so chính lấy Structural trừ đối thủ trong cùng set và seed. Trung bình seed trước trong từng set, rồi trung bình ngang nhau bốn set. B và D được phân tích riêng; A và C vẫn phải báo. Bootstrap ghép cặp lấy lại toàn capture file và tính lại từ số đếm; khoảng này mô tả biến thiên có điều kiện trên các file quan sát được, không phải khoảng tin cậy cho quần thể xe. Bốn set dùng lại xe, các cửa sổ tương quan và chronology vật lý chưa xác minh là những giới hạn còn lại.

Bốn phương pháp neural chạy trên RTX 5060; AssocRules chạy CPU bằng backend cache lời gọi chính xác. Backend giữ thuật toán học/score gốc, cache theo cặp ID--payload và giữ nguyên thứ tự cộng ở kiểm tra phân phối. Pilot nguồn k=2 cho score/rule/centroid trùng khớp và tăng tốc chấm khoảng 8,3 lần; đó là kiểm tra phần mềm, không phải bằng chứng cùng mức tăng tốc ở full k=300 hay cải thiện chất lượng IDS. Thời gian fit trong artifact không bao gồm toàn bộ đọc dữ liệu và đánh giá, không được đổi tên thành độ trễ online.

Bốn cell GPU Set 1/seed 42 hoàn tất trước được tái sử dụng sau khi xác minh hash, môi trường và cấu hình khoa học; manifest gốc được giữ, lineage được lưu riêng. Các cell còn thiếu chạy mới. Bộ gộp từ chối pilot, thiếu/trùng cell hoặc khác dữ liệu/code/môi trường; chỉ danh sách phương pháp để chia lịch GPU/CPU được chuẩn hóa. Manifest thực thi không bị viết lại để làm giống nhau.
'''

METHOD_EN = r'''
\section{Executed CTT comparison: content and file order}\label{sec:comparison-protocol}
\textbf{The executing protocol is \code{ctt-content-order-comparison-v1}.}
The timed v2.1 design in preceding sections is a reference specification, not the schema of this five-method matrix. Scanning all 236 CTT files identified 193,240,845 data frames, 3,019,271 completed W64 windows and 12,527 timestamp decreases across 100 files. This window count covers the entire repository, including training, validation and test roles; it is not each method's test denominator. The difference of 236 from 193,241,081 lines is one header per file. Line counts and data-frame counts are distinct.

The cache retains original IDs, DLCs, payloads, labels, timestamps and row order without sorting, deduplication or synthetic time. Removing zero-based raw index 28 and structural indices 26--27 leaves 28 raw and 30 structural dimensions. History features follow file order and are not interpreted as physical transmission periods. Timed execution remains blocked until timestamp provenance is resolved. The cache-manifest hash is \code{03a6bbf16efb4f583ca5566025c8bdc3cc0b65a7138a0a29f652505b2c367f29}.

Four sets, seeds 42/43/44 and five methods form 60 IDS units, each evaluated on A--D. CANBERT+ pretraining and fine-tuning are two phases within one unit. W64 windows do not overlap or cross files. Full-file reservoir sampling selects at most 1,000 windows per class per source training file, with sampling seed 20261103 and identical source-window indices across methods. Source validation is grouped by recording-round suffix; vocabularies, TF-IDF and all learned parameters use source data only.

\subsection{Comparators, supervision and departures from publications}
Raw and Structural Transformer share encoder architecture, source samples, CE/AdamW/Cosine, 10 epochs, batch 128 and learning rate 0.001; their principal difference is the 28/30-dimensional representation. This comparison tests the representation package and does not isolate identifier removal from each added structural feature.

CANBERT+~\cite{won2026canbertplus} imports the authors' BERT/MLM modules with hidden size 768, six layers and 12 heads. The vocabulary is source-only; benign-source pretraining masks 15\% of identifiers for three epochs, followed by three epochs of frame-supervised fine-tuning with batch eight. Replacing Lightning with a PyTorch loop, shared sampling, grouped splits, W64, fixed epochs and ensuring at least one masked token per batch are disclosed adaptations. The window score is the maximum frame score and does not measure frame localization.

CANLP~\cite{balasubramanian2025canlp} is adapted to character TF-IDF unigrams, at most 256 bigrams and ID/2048, followed by Dense 128/64, dropout 0.15 and two output classes. The PyTorch port uses Adam 0.001, batch 512, 30 epochs, original frame labels and maximum score/W64. TF-IDF fits only frames within sampled source-training windows. Grouped source splits, no deduplication, binary labels and fixed epochs replace the original notebook's selection procedure; the reported name is CANLP-char-DNN adapted.

CrySyS-AssocRules/W64 imports the association-rule implementation from the framework~\cite{koltai2026trust}, fitting benign source data only. Window/stride 64/64 replaces the reference implementation's 900/450; relations never bridge gaps between selected samples. Default cluster count 300, distance threshold 0.3 and maximum itemset sizes three for fitting and two for scoring are retained. This is a framework-derived adapted comparator, not a claim to reproduce a different similarly named method unchanged. Pinned commits for CANBERT+, CANLP and CrySyS are respectively \code{4c81d9b08e6e0c17b8e70bdab518209e399f0dbe}, \code{8df8bb74a7aa9925187f4faff05d6c8b824ba5d1} and \code{59b9f29f81b0f56f49c218cb1bd8e97552b8d22c}.

Supervision and compute budgets differ: the Transformers use window labels; CANBERT+ additionally uses benign pretraining and frame labels; CANLP uses frame labels; AssocRules uses benign traffic only. This compares complete pipelines under shared data/evaluation rules, not equal-budget ablations or original published scores. Adaptation qualifiers remain visible in result tables.

\subsection{Thresholds, pairing, acceleration and interpretation limits}
Source validation selects the threshold maximizing recall under a FAR budget of 100 per 100,000 benign source windows. Target labels never calibrate the threshold, and target FAR may exceed the budget. Recall is reported with FAR, attack F1, AP and TP/FP/TN/FN counts. Maximum frame score/W64 aligns the decision unit without equalizing supervision or computational cost.

Paired differences subtract each opponent from Structural within each set and seed. Seeds are averaged within a set before equally weighting the four sets. B and D are discussed separately; A and C remain reported. Paired bootstrap resamples entire capture files and recomputes metrics from confusion counts. Its intervals describe conditional variation over observed files, not population-level vehicle confidence intervals. Reused vehicles across sets, dependent windows and unverified physical chronology remain limitations.

Four neural methods execute on an RTX 5060; AssocRules uses an exact-call CPU cache backend. It preserves native fitting/scoring, caches ID--payload pairs and retains the native summation order for distribution checks. A source-only k=2 pilot matched scores, rules and centroids and accelerated scoring by approximately 8.3 times. This is software validation, not evidence of the same speedup at full k=300 or improved IDS quality. Recorded fit duration excludes complete data loading and evaluation and is not online latency.

Four previously completed GPU cells for Set 1/seed 42 are reused only after verifying hashes, environment and scientific configuration; original manifests remain intact with separate lineage. Remaining cells execute afresh. The merger rejects pilots, missing/duplicate cells and incompatible data/code/environments; only the method list used for GPU/CPU scheduling is normalized. Execution manifests are not rewritten to appear identical.
'''


def table(caption, label, headers, rows, widths):
    spec = ''.join('P{' + w + 'cm}' for w in widths)
    head = ' & '.join(headers) + r'\\\midrule'
    return (r'\begin{longtable}{' + spec + '}\n' + r'\caption{' + caption + r'}\label{' + label + r'}\\\toprule' + '\n' +
            head + r'\endfirsthead' + '\n' + r'\toprule' + '\n' + head + r'\endhead' + '\n' +
            '\n'.join(' & '.join(row) + r'\\' for row in rows) + '\n' + r'\bottomrule\end{longtable}' + '\n')


def pending(lang):
    if lang == 'vi':
        return r'''\section{Ma trận so sánh năm mô hình đang thực thi}\label{sec:comparison-results}
Giao thức, dữ liệu và các bản thích ứng được nêu tại Mục~\ref{sec:comparison-protocol}. Chưa nhập kết quả từng phần vào bảng chính: chỉ khi đủ 60 cell hợp lệ và các notebook hoàn tất, bảng, hình, tóm tắt và kết luận mới được cập nhật từ đầu ra thật. Các bảng lịch sử bên dưới không phải kết quả của ma trận này. RQ1 được đánh giá trong phạm vi content/file-order; ablation, probe, độ nhạy W32/W128 và ngoại bộ không tự hoàn tất chỉ vì ma trận năm mô hình hoàn tất.'''
    return r'''\section{Executing five-method comparison matrix}\label{sec:comparison-results}
Section~\ref{sec:comparison-protocol} specifies the protocol, data and adaptations. Partial runs are not imported into the primary table. Verified completion of all 60 cells and the notebooks is required before tables, figures, abstracts and conclusions are updated from actual outputs. Historical tables below do not belong to this matrix. RQ1 is evaluated within the content/file-order scope; ablations, probes, W32/W128 sensitivity and external tests do not become complete merely because the five-method matrix finishes.'''


def validate_complete(reuse_verified=False):
    sys.path[:0] = [str(CODE), str(CODE / 'src')]
    from acceleration.merge import merge
    for name in ('07_gpu_four_models_executed', '09_assoc_cpu_acceleration', '08_merged_results_executed'):
        state = json.loads((CODE / 'notebooks' / (name + '.execution.json')).read_text())
        assert state['status'] == 'COMPLETE', name
    # Revalidate manifests, hashes, complete cells, signatures and paired denominators.
    # The notebook packager may read MERGED concurrently. Revalidation writes
    # elsewhere and compares values; it must never rewrite the archived inputs.
    verification = CODE / 'results/manuscript_verified_comparison'
    if not reuse_verified:
        merge([CODE / 'results/comparison_gpu4_reuse_v1', CODE / 'results/assoc_exact_fast_v1'], verification)
    else:
        # A layout-only rebuild may reuse the completed independent audit. This
        # option assumes per-cell artifacts have remained untouched since it.
        audit = json.loads((verification / 'coverage.json').read_text())
        assert audit['status'] == 'COMPLETE_MATRIX' and audit['cells'] == 60
    import pandas as pd
    keys = ['set', 'seed', 'method', 'condition', 'file', 'operating_point']
    a = pd.read_csv(MERGED / 'all_metrics.csv').sort_values(keys).reset_index(drop=True)
    b = pd.read_csv(verification / 'all_metrics.csv').sort_values(keys).reset_index(drop=True)
    pd.testing.assert_frame_equal(a, b)
    assert json.loads((MERGED / 'source_references.json').read_text()) == json.loads((verification / 'source_references.json').read_text())
    refs = json.loads((MERGED / 'source_references.json').read_text())
    for ref in refs:
        assert digest(ref['manifest']) == ref['sha256'], ref['manifest']
    expected = {(f'set_0{s}', seed, method) for s in range(1, 5) for seed in (42, 43, 44) for method in METHODS}
    assert {tuple(r['cell']) for r in refs} == expected and len(refs) == 60
    return refs


def results(lang, data, refs):
    import numpy as np
    import pandas as pd
    vi = lang == 'vi'
    metrics = ['Recall', 'FAR_per_100k', 'Attack_F1', 'AP']
    pooled = data[(data.file == 'ALL') & (data.operating_point == 'source_calibrated') & data.condition.isin(list('ABCD'))]
    assert len(pooled) == 240
    per_set = pooled.groupby(['set', 'method', 'condition'])[metrics].mean()
    means = per_set.groupby(['method', 'condition'])[metrics].mean()
    num = lambda x, digits=4: '--' if pd.isna(x) else f'{x:.{digits}f}'
    titles = ['Điều kiện', 'Phương pháp', 'Recall', 'FAR', 'F1', 'AP'] if vi else ['Cond.', 'Method', 'Recall', 'FAR', 'F1', 'AP']
    rows = [[cond, LABELS[method], *[num(means.loc[(method, cond), m], 2 if m == 'FAR_per_100k' else 4) for m in metrics]] for cond in 'ABCD' for method in METHODS]
    body = (r'\section{' + ('Kết quả xác minh của ma trận năm mô hình' if vi else 'Verified five-method comparison results') + r'}\label{sec:comparison-results}' + '\n')
    body += (r'Đã xác minh 60 cell và 240 tổ hợp cell--điều kiện A--D theo Mục~\ref{sec:comparison-protocol}. Mỗi số trong bảng chính là trung bình ba seed trong từng set rồi trung bình ngang nhau bốn set; không gộp mọi cửa sổ thành trọng số xe. Ký hiệu -- là chỉ số không xác định. Dữ liệu lịch sử phía sau vẫn được tách riêng.' if vi else
             r'All 60 cells and 240 cell--condition A--D combinations have been verified under Section~\ref{sec:comparison-protocol}. Primary entries average three seeds within each set and then equally weight four sets; windows are not pooled as vehicle weights. A dash marks an undefined metric. Historical results below remain separate.') + '\n'
    body += table('Content/file-order, W64; source-calibrated; equal set weights; FAR per 100,000 benign windows', 'tab:comparison-main', titles, rows, ['1.2', '4.0', '1.7', '2.2', '1.7', '1.7'])
    denominators = []
    for (s, cond), group in pooled.groupby(['set', 'condition']):
        for col in ('Attack_Windows', 'Benign_Windows', 'Total_Windows'):
            assert group[col].nunique() == 1, (s, cond, col)
        denominators.append([s.replace('_', r'\_'), cond, str(int(group.Attack_Windows.iloc[0])), str(int(group.Benign_Windows.iloc[0])), str(int(group.Total_Windows.iloc[0]))])
    body += table('Test-window denominators shared by five methods and three seeds', 'tab:comparison-counts', ['Set', 'Cond.', 'Attack', 'Benign', 'Total'], denominators, ['2.0', '1.2', '2.7', '2.7', '2.7'])
    pairs = pd.read_csv(MERGED / 'paired_by_set.csv')
    pmean = pairs.groupby(['opponent', 'condition'])[metrics].mean()
    prows = [[cond, LABELS[opp], *[num(pmean.loc[(opp, cond), m], 2 if m == 'FAR_per_100k' else 4) for m in metrics]] for cond in 'BD' for opp in METHODS if opp != 'structural_transformer']
    body += table('Structural minus opponent; equal set weights; FAR per 100,000 benign windows', 'tab:comparison-paired', titles[:2] + [r'$\Delta R$', r'$\Delta$ FAR', r'$\Delta$ F1', r'$\Delta$ AP'], prows, ['1.2', '4.0', '1.7', '2.2', '1.7', '1.7'])
    body += r'\subsection{' + ('Diễn giải phép so chính và đánh đổi' if vi else 'Primary comparison and tradeoffs') + '}\n'
    for cond in 'BD':
        delta = pmean.loc[('raw_transformer', cond)]
        setrows = pairs[(pairs.opponent == 'raw_transformer') & (pairs.condition == cond)]
        positives = int((setrows.Recall > 0).sum())
        sentence = (f"Điều kiện {cond}: Structural trừ Raw có chênh lệch recall {num(delta.Recall)}, FAR {num(delta.FAR_per_100k, 2)} trên 100.000, F1 {num(delta.Attack_F1)} và AP {num(delta.AP)}; recall dương ở {positives}/4 set sau trung bình seed. " if vi else
                    f"Condition {cond}: Structural minus Raw yields recall difference {num(delta.Recall)}, FAR difference {num(delta.FAR_per_100k, 2)} per 100,000, F1 difference {num(delta.Attack_F1)} and AP difference {num(delta.AP)}; recall is positive in {positives}/4 seed-averaged sets. ")
        if pd.isna(delta.Recall) or pd.isna(delta.FAR_per_100k):
            sentence += ('Chỉ số không xác định nên không kết luận hướng đánh đổi. ' if vi else 'An undefined metric prevents a directional tradeoff conclusion. ')
        elif delta.Recall > 0 and delta.FAR_per_100k > 0:
            sentence += ('Recall tăng đi cùng FAR tăng, nên đây là đánh đổi thay vì ưu thế đồng thời. ' if vi else 'Recall increases together with FAR, indicating a tradeoff rather than simultaneous improvement. ')
        elif delta.Recall <= 0:
            sentence += ('Kết quả không ủng hộ giả thuyết tăng recall trung bình ở điều kiện này. ' if vi else 'This does not support increased mean recall in this condition. ')
        else:
            sentence += ('Recall trung bình tăng mà FAR trung bình không tăng trong phạm vi phép so này. ' if vi else 'Mean recall increases without increased mean FAR within this comparison. ')
        body += sentence + '\n\n'
    body += ('Các đối thủ trong Bảng~\\ref{tab:comparison-paired} được giữ nguyên kể cả khi tốt hơn Structural. Dấu dương của FAR là nhiều báo động giả hơn; dấu dương của recall/F1/AP là tăng chỉ số tương ứng. Không quy mọi chênh lệch cho tính độc lập xe khi supervision, pretrain và kiến trúc khác nhau.\n' if vi else
             'Opponents in Table~\\ref{tab:comparison-paired} remain reported even when they outperform Structural. Positive FAR means more false alarms, whereas positive recall/F1/AP means an increase in that metric. Differences cannot all be attributed to vehicle invariance because supervision, pretraining and architectures differ.\n')
    structural = means.loc['structural_transformer']
    raw = means.loc['raw_transformer']
    body += (f"FAR đích của Structural ở B là {structural.loc['B', 'FAR_per_100k'] / 1000:.2f}\\% và ở D là {structural.loc['D', 'FAR_per_100k'] / 1000:.2f}\\%, trong khi ngân sách validation nguồn chỉ 0,1\\%. Đây là thất bại chuyển giao điểm vận hành: giảm FAR so với Raw vẫn chưa tạo ra mức báo động giả phù hợp triển khai. Giả thuyết chính tăng recall ở B không được ủng hộ nếu chênh lệch B không dương. " if vi else
             f"Structural target FAR is {structural.loc['B', 'FAR_per_100k'] / 1000:.2f}\\% in B and {structural.loc['D', 'FAR_per_100k'] / 1000:.2f}\\% in D, against a source-validation budget of 0.1\\%. This is an operating-point transfer failure: reducing FAR relative to Raw does not establish deployment-suitable false-alarm levels. The primary increased-recall hypothesis for B is unsupported when the B difference is nonpositive. ")
    body += (f"AP của Structural/Raw là {structural.loc['B', 'AP']:.4f}/{raw.loc['B', 'AP']:.4f} ở B và {structural.loc['D', 'AP']:.4f}/{raw.loc['D', 'AP']:.4f} ở D. AP tăng phản ánh chất lượng xếp hạng tốt hơn trong phép so này, nhưng là chỉ số bổ sung và không thay thế tiêu chí recall tại ngưỡng nguồn đã chọn. F1 ở từng điều kiện phải được giữ riêng, không chọn lại chỉ số chính sau khi xem test.\n\n" if vi else
             f"Structural/Raw AP is {structural.loc['B', 'AP']:.4f}/{raw.loc['B', 'AP']:.4f} in B and {structural.loc['D', 'AP']:.4f}/{raw.loc['D', 'AP']:.4f} in D. Increased AP indicates better ranking within this comparison, but remains secondary and does not replace recall at the source-selected threshold. Condition-specific F1 remains separate; the primary metric is not reselected after viewing targets.\n\n")
    assoc = pooled[pooled.method == 'assoc_rules_crysys']
    if len(assoc) and (assoc.Recall == 0).all() and (assoc.FAR_per_100k == 0).all():
        thresholds = []
        for ref in refs:
            if ref['cell'][2] == 'assoc_rules_crysys':
                thresholds.append(json.loads((Path(ref['manifest']).parent / 'calibration.json').read_text())['threshold'])
        if len(thresholds) == 12 and all(t > 1 for t in thresholds):
            body += (r'AssocRules có recall và FAR bằng 0 ở cả 48 tổ hợp set--seed--điều kiện. Cả 12 ngưỡng nguồn đều bằng \code{1.0000000000000002}, lớn hơn miền score [0,1], nên operating point này dự đoán toàn bộ là bình thường. FAR bằng 0 vì vậy không phải bằng chứng phát hiện tốt; đây là điểm vận hành suy biến dưới ngân sách nguồn và bản thích ứng W64 hiện tại. AP vẫn đo xếp hạng trước ngưỡng. Kết quả này không chứng minh thuật toán gốc ở W900/stride450 thất bại; cần một nghiên cứu độ nhạy thiết kế riêng và không đổi ngưỡng bằng nhãn test để làm đẹp bảng.' if vi else
                     r'AssocRules has zero recall and FAR in all 48 set--seed--condition combinations. All 12 source thresholds equal \code{1.0000000000000002}, exceeding the score range [0,1], so this operating point predicts every window as benign. Zero FAR is therefore not evidence of effective detection: this is a degenerate operating point under the source budget and current W64 adaptation. AP still measures ranking before thresholding. This does not establish failure of the original W900/stride450 algorithm; a separately designed sensitivity study is required, without using test labels to improve the reported threshold.') + '\n\n'
    for metric in ('Recall', 'FAR_per_100k', 'Attack_F1', 'AP'):
        src = MERGED / (metric + '.png')
        assert src.is_file(), src
        shutil.copy2(src, ROOT / 'thesis' / lang / 'figs' / ('comparison_v1_' + metric + '.png'))
        body += (r'\begin{figure}[htbp]\centering\includegraphics[width=\linewidth]{figs/comparison_v1_' + metric + '.png}' + '\n' +
                 r'\caption{Content/file-order, W64: ' + metric.replace('_', r'\_') + r'; source-calibrated; equal set weights.}\label{fig:comparison-' + metric + r'}\end{figure}' + '\n')
    body += r'\FloatBarrier' + '\n' + r'\subsection{' + ('Biến thiên, cơ chế thất bại và chi phí fit' if vi else 'Variation, failure mechanisms and fit cost') + '}\n'
    sd = pooled.groupby(['set', 'method', 'condition'])[metrics].std()
    detail = []
    for s in ('set_01', 'set_02', 'set_03', 'set_04'):
        for cond in 'BD':
            for method in METHODS:
                ix = (s, method, cond)
                detail.append([s.replace('_', r'\_'), cond, LABELS[method], num(per_set.loc[ix, 'Recall']) + r' $\pm$ ' + num(sd.loc[ix, 'Recall']), num(per_set.loc[ix, 'FAR_per_100k'], 2)])
    body += table('B/D by set; recall mean and sample SD across three seeds; FAR per 100,000', 'tab:comparison-sets', ['Set', 'Cond.', 'Method', 'Recall', 'FAR'], detail, ['1.6', '1.2', '4.0', '3.5', '2.2'])
    intervals = json.loads((MERGED / 'paired_capture_bootstrap.json').read_text())
    cirows = []
    for item in intervals:
        if item['opponent'] != 'raw_transformer' or item['condition'] not in 'BD' or item['metric'] != 'Recall':
            continue
        ci = item['ci95']
        cirows.append([item['set'].replace('_', r'\_'), str(item['seed']), item['condition'], num(item['estimate']), '--' if ci is None else '[' + num(ci[0]) + ', ' + num(ci[1]) + ']', str(item['files']) + '; ' + str(item['valid_replicates']) + '/' + str(item['requested_replicates'])])
    body += table('Structural minus Raw: conditional whole-file recall bootstrap, 95 percent', 'tab:comparison-ci', ['Set', 'Seed', 'Cond.', r'$\Delta R$', 'Interval', 'Files; draws'], cirows, ['1.6', '1.1', '1.2', '1.8', '3.7', '2.9'])
    files = data[(data.file != 'ALL') & (data.operating_point == 'source_calibrated') & data.condition.isin(list('BD')) & (data.method == 'structural_transformer') & (data.Attack_Windows > 0)]
    grouped = files.groupby(['condition', 'file'])[['Recall', 'FAR_per_100k']].mean().sort_values('Recall').head(8)
    bad = [[cond, next((part for part in Path(name).parts if part.startswith('set_')), 'capture').replace('_', r'\_') + '/' + Path(name).name.replace('_', r'\_'), num(r.Recall), num(r.FAR_per_100k, 2)] for (cond, name), r in grouped.iterrows()]
    body += table('Structural: eight lowest mean-recall B/D captures (descriptive); FAR per 100,000', 'tab:comparison-failures', ['Cond.', 'Set/capture', 'Recall', 'FAR'], bad, ['1.2', '7.0', '1.8', '2.2'])
    costs = {m: [] for m in METHODS}
    for ref in refs:
        p = Path(ref['manifest']).parent / 'training.json'
        costs[ref['cell'][2]].append(json.loads(p.read_text())['seconds'])
    body += table('Recorded fit seconds: median [min, max] across 12 cells', 'tab:comparison-cost', ['Method', 'Fit seconds'], [[LABELS[m], f'{np.median(v):.2f} [{min(v):.2f}, {max(v):.2f}]'] for m, v in costs.items()], ['6.0', '6.0'])
    body += (r'Thời gian trên chỉ đo đoạn fit được script ghi, trong môi trường có các job đồng thời; không phải benchmark thông lượng được cô lập. Khoảng bootstrap từng set/seed/capture nằm trong \code{paired_capture_bootstrap.json}; số đếm, hai operating point, per-file metrics và trường hợp không xác định nằm trong \code{all_metrics.csv}. Các khoảng bootstrap không được trung bình rồi gọi là CI đa xe. Ablation, probe xe/tấn công, độ nhạy cửa sổ và đánh giá ngoại bộ còn là các câu hỏi mở.' if vi else
             r'These durations cover the recorded fit segment in an environment with concurrent jobs, not an isolated throughput benchmark. Per-set/seed capture-bootstrap intervals are in \code{paired_capture_bootstrap.json}; counts, both operating points, per-file metrics and undefined cases are in \code{all_metrics.csv}. Bootstrap intervals are not averaged and relabelled as multi-vehicle confidence intervals. Ablations, vehicle/attack probes, window sensitivity and external evaluation remain open.') + '\n'
    return body


def update_sources(complete=False, refs=None):
    import pandas as pd
    data = pd.read_csv(MERGED / 'all_metrics.csv') if complete else None
    abstract_vi = ('Phép so chính hiện thực thi theo nội dung và thứ tự file: raw 28 chiều, structural 30 chiều, W64, bốn set, ba seed và năm phương pháp. Timestamp đi lùi được giữ để kiểm toán và không dùng làm đặc trưng; không khẳng định thứ tự dòng là chronology vật lý. CANBERT+, CANLP-char-DNN và CrySyS-AssocRules/W64 là các bản thích ứng có công bố thay đổi, không dùng trực tiếp điểm số công bố gốc để xếp hạng. ' +
                   ('Ma trận 60 cell đã được xác minh; số liệu và đánh đổi recall/FAR được trình bày tại Mục~\\ref{sec:comparison-results}. ' if complete else 'Ma trận 60 cell đang chạy; chưa có kết luận định lượng từ các lượt chưa hoàn tất. ') +
                   'Kết quả này không tự trả lời các câu hỏi về loại trừ đặc trưng, probe xe, ngoại bộ hay độ trễ triển khai.')
    abstract_en = ('The primary comparison uses content and file order: 28 raw dimensions, 30 structural dimensions, W64, four sets, three seeds and five methods. Reversed timestamps are retained for audit and excluded from features; physical chronology is not asserted. CANBERT+, CANLP-char-DNN and CrySyS-AssocRules/W64 are disclosed adaptations, and original published scores are not directly ranked. ' +
                   ('The 60-cell matrix has been verified; measured recall/FAR tradeoffs appear in Section~\\ref{sec:comparison-results}. ' if complete else 'The 60-cell matrix is executing; incomplete runs do not support quantitative conclusions. ') +
                   'This comparison does not itself answer feature-ablation, vehicle-probe, external-transfer or deployment-latency questions.')
    if complete:
        pairs = pd.read_csv(MERGED / 'paired_by_set.csv')
        b = pairs[(pairs.opponent == 'raw_transformer') & (pairs.condition == 'B')]
        dr, df = b.Recall.mean(), b.FAR_per_100k.mean()
        abstract_vi += f' Ở B, Structural trừ Raw có chênh lệch recall trung bình {dr:.4f} và FAR {df:.2f}/100.000, với trọng số ngang nhau giữa set; hai đại lượng phải được diễn giải cùng nhau.'
        abstract_en += f' In B, Structural minus Raw yields mean recall difference {dr:.4f} and FAR difference {df:.2f}/100,000 under equal set weights; these quantities must be interpreted together.'
    for lang in ('vi', 'en'):
        path = ROOT / 'thesis' / lang / 'main.tex'
        text = path.read_text(encoding='utf-8')
        # Each standalone manuscript includes both abstracts.
        for tag, paragraph in [('vi', abstract_vi), ('en', abstract_en)]:
            pattern = r'(% Begin inlined (?:\.\./' + tag + r'/)?abstract_' + tag + r'\.tex\n)(.*?)(% End inlined (?:\.\./' + tag + r'/)?abstract_' + tag + r'\.tex)'
            def abstract_match(m):
                inner = m[2]
                intro = (r'\noindent\textbf{Tóm tắt:} Khóa luận khảo sát chuyển giao phát hiện xâm nhập CAN khi đổi xe và kiểu tấn công. Biểu diễn structural bỏ bit ID thô ở đầu vào bộ phân loại nhưng vẫn dùng ID làm khóa lịch sử payload và quan hệ cục bộ. Nhãn cửa sổ dương khi có ít nhất một frame mang nhãn 1 theo chính sách dữ liệu.' if tag == 'vi' else
                         r'\noindent\textbf{Abstract:} This thesis examines transfer of CAN intrusion detection across vehicles and attack types. Structural inputs exclude raw ID bits while still using IDs as keys for payload history and local relations. A window is positive when at least one frame carries label 1 under the dataset annotation policy.')
                key = re.search(r'\\noindent\\textbf\{\\textit\{(?:Từ khóa|Keywords):\}\}.*', inner).group(0)
                return m[1] + r'\begingroup\fontsize{12}{12}\selectfont' + '\n' + intro + '\n\n' + paragraph + '\n\n' + key + '\n' + r'\par\endgroup' + '\n' + m[3]
            text, count = re.subn(pattern, abstract_match, text, flags=re.S)
            assert count == 1, (lang, tag)
        status_title = ('Trạng thái thực nghiệm của bản chỉnh sửa' if lang == 'vi' else 'Experimental status of this revision')
        status_body = (r'Phép so chính dùng content/file-order theo Mục~\ref{sec:comparison-protocol}. ' + (r'Đã đủ 60 cell; kết quả mới ở Mục~\ref{sec:comparison-results}. ' if complete else 'Ma trận 60 cell đang chạy; chỉ nhập bảng chính khi đủ kết quả hợp lệ. ') + 'Các bảng thăm dò và thiết kế timed v2.1 vẫn được ghi riêng. Ablation, probe, ngoại bộ và runtime chưa được xem là hoàn tất.' if lang == 'vi' else
                       r'The primary comparison uses content/file order under Section~\ref{sec:comparison-protocol}. ' + (r'All 60 cells are complete; new results appear in Section~\ref{sec:comparison-results}. ' if complete else 'The 60-cell matrix is executing; primary tables require verified completion. ') + 'Historical tables and the timed v2.1 design remain separate. Ablations, probes, external evaluation and runtime are not automatically complete.')
        text = re.sub(r'(\\frontchapter\{' + re.escape(status_title) + r'\}\n).*?(?=% End inlined front_)', lambda m: m[1] + status_body + '\n', text, flags=re.S)
        text = block(text, 'METHOD', METHOD_VI if lang == 'vi' else METHOD_EN, '% End inlined method_' + lang + '.tex')
        # Long commit hashes are separate items so they cannot stretch a prose line.
        hashes = ['4c81d9b08e6e0c17b8e70bdab518209e399f0dbe', '8df8bb74a7aa9925187f4faff05d6c8b824ba5d1', '59b9f29f81b0f56f49c218cb1bd8e97552b8d22c']
        hash_list = '\n' + r'\begin{itemize}' + '\n' + '\n'.join(r'\item ' + name + ': ' + r'\code{' + h + '}' for name, h in zip(['CANBERT+', 'CANLP', 'CrySyS'], hashes)) + '\n' + r'\end{itemize}'
        pattern = (r'Commit của CANBERT\+, CANLP và CrySyS lần lượt là .*?\.' if lang == 'vi' else r'Pinned commits for CANBERT\+, CANLP and CrySyS are respectively .*?\.')
        text = re.sub(pattern, lambda _: ('Các commit nguồn được ghim:' if lang == 'vi' else 'Pinned source commits:') + hash_list, text)
        anchor = r'\section{Bằng chứng kiểm tra chất lượng dữ liệu}' if lang == 'vi' else r'\section{Data-quality evidence}'
        if anchor not in text and lang == 'en':
            anchor = next(x for x in text.splitlines() if x.startswith(r'\section{') and 'quality' in x.lower() and text.index(x) > text.index(r'\label{chap:results}'))
        text = block(text, 'RESULTS', results(lang, data, refs) if complete else pending(lang), anchor)
        note = ((r'\section{Kết luận từ phép so nội dung đã xác minh}' if complete else r'\section{Phạm vi của phép so đang chạy}') + '\n' + abstract_vi if lang == 'vi' else
                (r'\section{Conclusion from the verified content comparison}' if complete else r'\section{Scope of the executing comparison}') + '\n' + abstract_en)
        text = block(text, 'CONCLUSION', note, '% End inlined conclusion_' + lang + '.tex')
        if complete:
            if lang == 'vi':
                text = text.replace('Ba đóng góp trên thuộc phương pháp và kiểm chứng dữ liệu. Hiệu quả của structural so với raw cần được xác nhận bằng đánh giá bốn set, ba seed, probe và ngoại suy.', 'Ngoài phương pháp và kiểm chứng dữ liệu, ma trận content/file-order bốn set, ba seed và năm mô hình đã hoàn tất tại Mục~\\ref{sec:comparison-results}. Kết quả phân biệt chất lượng xếp hạng với recall và FAR tại ngưỡng nguồn; probe và ngoại suy vẫn cần bằng chứng riêng.')
                text = text.replace('ma trận kết quả chưa hoàn thành', 'ma trận so sánh nội dung đã hoàn tất và các thực nghiệm mở rộng còn thiếu')
                text = text.replace('Chờ chạy cấu hình primary', r'Đã hoàn tất content/file-order; timed chờ xác minh timestamp')
                text = text.replace('Số liệu lịch sử tạo động lực nghiên cứu nhưng chưa trả lời các câu hỏi theo giao thức v2.1.', 'Số liệu lịch sử tạo động lực nghiên cứu; kết quả mới chỉ xác nhận phép so content/file-order ở Mục~\\ref{sec:comparison-results}, không xác nhận nhánh timed v2.1.')
                text = text.replace('Trước hết, hoàn tất benchmark bốn set, ba seed với cùng phép chia nguồn và hai quy tắc ngưỡng.', 'Ma trận năm mô hình, bốn set và ba seed theo content/file-order đã hoàn tất; timed v2.1 vẫn cần xác minh nguồn timestamp trước khi chạy.')
                text = text.replace('So sánh định lượng chính xác với bộ phát hiện quan hệ hoặc phổ quát gần đây cần tái lập đúng phương pháp trong một giao thức chung được công bố.', 'Phép so định lượng với CANBERT+, CANLP-char-DNN và CrySyS-AssocRules/W64 đã được thực hiện dưới các bản thích ứng công bố rõ. So sánh với các bộ phát hiện quan hệ hoặc phổ quát khác vẫn cần triển khai và xác minh riêng.')
            else:
                text = text.replace('These three contributions concern methods and data validation. The performance of structural versus raw inputs still requires the four-set, three-seed evaluation, probes and external tests.', 'In addition to methods and data validation, the four-set, three-seed, five-method content/file-order matrix is complete in Section~\\ref{sec:comparison-results}. Results distinguish ranking quality from recall and FAR at source-selected thresholds; probes and external tests still require separate evidence.')
                text = text.replace('the unfinished result matrix', 'the completed content comparison and outstanding extended experiments')
                text = text.replace('Pending: primary configuration', 'Content/file-order complete; timed awaits verified timestamps')
                text = text.replace(r'\section{Required protocol-v2.1 result matrix}', r'\section{Extended experiments beyond the content comparison}')
                text = text.replace('The historical results motivate investigation but do not answer the research questions under protocol v2.1.', 'Historical results motivate investigation; new evidence confirms only the content/file-order comparison in Section~\\ref{sec:comparison-results}, not timed protocol v2.1.')
                text = text.replace('First, complete the four-set, three-seed primary benchmark using identical source splits and both threshold rules.', 'The five-method, four-set, three-seed content/file-order matrix is complete; timed v2.1 still requires verified timestamp provenance before execution.')
                text = text.replace('Exact quantitative comparison with recent relational or universal detectors requires faithful reproductions under a documented common protocol.', 'CANBERT+, CANLP-char-DNN and CrySyS-AssocRules/W64 have been quantitatively compared under disclosed adaptations. Other relational or universal comparators still require separate implementation and validation.')
        if lang == 'vi':
            text = text.replace('CAN-FD, ID mở rộng, dữ liệu đảo thời gian hoặc nhãn chưa xác định sẽ bị từ chối.', 'CAN-FD, ID mở rộng hoặc nhãn chưa xác định sẽ bị từ chối. Nhánh có thời gian từ chối timestamp đảo; phép so content/file-order giữ timestamp để kiểm toán nhưng không sử dụng làm đặc trưng.')
            text = text.replace('biểu diễn structural 32 chiều không đưa', 'biểu diễn structural (30 chiều trong phép so nội dung; 32 chiều trong đặc tả có thời gian) không đưa')
            text = text.replace('29 chiều raw hoặc 32 chiều structural', '28 chiều raw / 30 chiều structural (content); 29/32 khi timed hợp lệ')
            text = text.replace('raw 29 chiều hoặc structural 32 chiều', 'raw 28 / structural 30 chiều (content)')
            text = text.replace(r'\section{Ma trận kết quả v2.1 cần hoàn thành}', r'\section{Thực nghiệm mở rộng ngoài ma trận so sánh nội dung}')
        else:
            text = text.replace('CAN-FD, extended identifiers, reversed timestamps and unknown labels are rejected.', 'CAN-FD, extended identifiers and unknown labels are rejected. The timed branch rejects reversed timestamps; the content/file-order comparison retains timestamps for audit but excludes them from features.')
            text = text.replace('32-dimensional structural representation', 'structural representation (30 dimensions in the content comparison; 32 in the timed specification)')
            text = text.replace('29-dimensional raw or 32-dimensional structural inputs', '28 raw / 30 structural dimensions (content); 29/32 for valid timed inputs')
        # Mark the older prose as reference design/history rather than overriding new results.
        marker = '% Begin inlined results_' + lang + '.tex\n'
        scope = ('Các kết quả mới chỉ thuộc nhánh content/file-order tại Mục~\\ref{sec:comparison-results}. Các đoạn nói chưa có xác nhận v2.1 bên dưới chỉ nhánh timed và các thí nghiệm mở rộng; số lịch sử không được trộn vào ma trận mới.' if lang == 'vi' else
                 'New results belong only to the content/file-order branch in Section~\\ref{sec:comparison-results}. Statements below about pending v2.1 confirmation refer to the timed branch and extended experiments; historical numbers are not merged into the new matrix.')
        text = block(text, 'SCOPE', scope, '% End inlined front_' + lang + '.tex')
        text = text.replace(r'\setlength{\emergencystretch}{3em}', r'\setlength{\emergencystretch}{5em}')
        path.write_text(text, encoding='utf-8')


def build_pdfs():
    out = CODE / 'output/thesis_comparison_2026-11-08'
    for lang in ('vi', 'en'):
        dest = out / lang
        dest.mkdir(parents=True, exist_ok=True)
        cmd = [str(ROOT / '.tools/tectonic/tectonic.exe'), '-X', 'compile', 'main.tex', '--outdir', str(dest), '--keep-logs']
        with (dest / 'build_console.log').open('w', encoding='utf-8') as log:
            subprocess.run(cmd, cwd=ROOT / 'thesis' / lang, stdout=log, stderr=subprocess.STDOUT, check=True)
        assert (dest / 'main.pdf').is_file()
        console = (dest / 'build_console.log').read_text(encoding='utf-8')
        if 'Overfull' in console or re.search(r'(?:Citation|Reference).*undefined|undefined references', console, re.I):
            raise RuntimeError('PDF has an overflow or unresolved reference; inspect ' + str(dest / 'build_console.log'))
        # Render all final pages for subsequent visual review; extraction alone is insufficient.
        render = out / ('render_' + lang)
        render.mkdir(exist_ok=True)
        subprocess.run(['pdftoppm', '-scale-to', '1100', '-png', str(dest / 'main.pdf'), str(render / 'page')], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True)
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--prepare', action='store_true')
    p.add_argument('--watch', action='store_true')
    p.add_argument('--build', action='store_true')
    p.add_argument('--reuse-verified-results', action='store_true', help='Layout-only rebuild after an independent completed audit; per-cell outputs must be untouched')
    a = p.parse_args()
    state = {'status': 'PREPARING' if a.prepare else 'WAITING_FOR_NOTEBOOKS', 'pid': __import__('os').getpid(), 'utc': datetime.now(timezone.utc).isoformat()}
    atomic_json(REPORT, state)
    try:
        if a.watch:
            while True:
                names = ('07_gpu_four_models_executed', '09_assoc_cpu_acceleration', '08_merged_results_executed')
                states = [json.loads((CODE / 'notebooks' / (n + '.execution.json')).read_text()) for n in names]
                if any(s['status'] == 'FAILED' for s in states):
                    raise RuntimeError('A notebook failed; partial scores are not imported')
                if all(s['status'] == 'COMPLETE' for s in states):
                    break
                state['utc'] = datetime.now(timezone.utc).isoformat()
                atomic_json(REPORT, state)
                time.sleep(30)
        refs = None if a.prepare else validate_complete(reuse_verified=a.reuse_verified_results)
        update_sources(complete=not a.prepare, refs=refs)
        subprocess.run([sys.executable, str(CODE / 'scripts/check_manuscript.py')], cwd=ROOT, check=True)
        out = build_pdfs() if a.build else None
        state.update(status='METHODS_PREPARED_RESULTS_PENDING' if a.prepare else 'RESULTS_IMPORTED_VISUAL_REVIEW_REQUIRED', utc=datetime.now(timezone.utc).isoformat(),
                     sources={lang: {'path': str(ROOT / 'thesis' / lang / 'main.tex'), 'sha256': digest(ROOT / 'thesis' / lang / 'main.tex')} for lang in ('vi', 'en')},
                     pdf_folder=str(out) if out else None,
                     remaining=['Rendered final PDF visual review', 'Content-compatible ablations/probes/window sensitivity', 'Verified external transfer', 'Online runtime measurement'])
        if not a.prepare:
            state['source_references_sha256'] = digest(MERGED / 'source_references.json')
            archive = CODE / 'output/manuscript_comparison_2026-11-08.zip'
            with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
                for lang in ('vi', 'en'):
                    for name in ('main.tex', 'refs.bib'):
                        path = ROOT / 'thesis' / lang / name
                        z.write(path, path.relative_to(ROOT).as_posix())
                    for path in (ROOT / 'thesis' / lang / 'figs').glob('*'):
                        if path.is_file():
                            z.write(path, path.relative_to(ROOT).as_posix())
                    if out:
                        path = out / lang / 'main.pdf'
                        z.write(path, path.relative_to(ROOT).as_posix())
                for path in MERGED.glob('*'):
                    if path.is_file():
                        z.write(path, path.relative_to(ROOT).as_posix())
            state['archive'] = str(archive)
        atomic_json(REPORT, state)
    except BaseException as exc:
        state.update(status='FAILED', error=repr(exc), utc=datetime.now(timezone.utc).isoformat())
        atomic_json(REPORT, state)
        raise


if __name__ == '__main__':
    main()
