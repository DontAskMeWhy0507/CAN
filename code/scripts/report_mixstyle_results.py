"""Verify external predictions and report the new experiment without editing thesis."""
from pathlib import Path
import hashlib
import json
import sys
CODE = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(CODE), str(CODE/'src')]
import numpy as np
import pandas as pd
from can_research.io import sha256_file, json_write
from can_research.provenance import json_safe
from can_research.metrics import compute_binary_metrics
from thesis_final.evidence import valid_manifest, effect_label

OUT = CODE/'results/mixstyle_posthoc_2026-11-09'
OLD = CODE/'results/content_completion_2026-11-09/external/attempt_001'
METHOD = 'structural_mixstyle'
KEYS = ['Total_Windows','Attack_Windows','Benign_Windows','TP','FP','TN','FN','Recall','FAR_per_100k','AP','Attack_F1']


def verify_values(computed, row):
    for key in KEYS:
        if not np.isclose(computed[key], row[key], equal_nan=True, rtol=1e-10, atol=1e-10):
            raise ValueError(f'External prediction/metric mismatch: {key}')


def main():
    paths = [p for p in (OUT/'external').glob('attempt_*/manifest.json')
             if json.loads(p.read_text())['status']=='COMPLETE']
    if len(paths) != 1: raise ValueError('Need one complete external evaluation')
    valid_manifest(paths[0]); valid_manifest(OLD/'manifest.json')
    dest = paths[0].parent
    coverage = json.loads((dest/'coverage.json').read_text())
    oldcoverage = json.loads((OLD/'coverage.json').read_text())
    if [{k: v for k, v in r.items() if k!='prediction'} for r in coverage] != oldcoverage:
        raise ValueError('External ledger differs from frozen study')
    new = pd.read_csv(dest/'external_metrics.csv', float_precision='round_trip')
    old = pd.read_csv(OLD/'external_metrics.csv', float_precision='round_trip')
    d = pd.concat([old, new], ignore_index=True)
    expected = {(r['dataset'], r['file'], seed, rep) for r in coverage if r['status']=='COMPLETE'
                for seed in [42,43,44] for rep in ['raw','structural',METHOD]}
    keys = ['dataset','file','seed','representation']
    if d.duplicated(keys).any() or set(d[keys].itertuples(index=False, name=None)) != expected:
        raise ValueError('Missing or duplicate external metric cells')
    pooled = []
    for dataset in sorted(d.dataset.unique()):
        entries = [r for r in coverage if r['status']=='COMPLETE' and r['dataset']==dataset]
        for seed in [42,43,44]:
            ys, scores = [], {rep: [] for rep in ['raw','structural',METHOD]}
            thresholds = {}
            for entry in entries:
                token = hashlib.sha256(entry['file'].encode()).hexdigest()[:20]+'.npz'
                with np.load(dest/token) as a, np.load(OLD/token) as b:
                    np.testing.assert_array_equal(a['y'], b['y'])
                    np.testing.assert_array_equal(a['window_index'], b['window_index'])
                    np.testing.assert_array_equal(a['window_index'], np.arange(entry['windows']))
                    y = a['y']; ys.append(y)
                    for rep in scores:
                        score = a[f'seed_{seed}'] if rep==METHOD else b[f'{rep}_{seed}']
                        row = d[(d.dataset==dataset)&(d.file==entry['file'])&(d.seed==seed)&(d.representation==rep)].iloc[0]
                        thresholds.setdefault(rep, row.threshold)
                        if row.threshold != thresholds[rep]: raise ValueError('Threshold varies by capture')
                        verify_values(compute_binary_metrics(y, y_score=score, threshold=row.threshold), row)
                        scores[rep].append(score)
            y = np.concatenate(ys)
            for rep, parts in scores.items():
                pooled.append(dict(dataset=dataset, seed=seed, method=rep, captures=len(entries),
                                   threshold=thresholds[rep],
                                   **compute_binary_metrics(y, y_score=np.concatenate(parts), threshold=thresholds[rep])))
    analysis = OUT/'analysis'
    d.to_csv(analysis/'external_capture_metrics_verified.csv', index=False)
    pooled = pd.DataFrame(pooled)
    pooled.to_csv(analysis/'external_dataset_seed_pooled.csv', index=False)
    metrics = ['Recall','FAR_per_100k','AP','Attack_F1']
    extmean = pooled.groupby(['dataset','method'])[metrics].agg(lambda s: s.mean() if s.notna().all() else np.nan)
    extmean.to_csv(analysis/'external_dataset_mean_seed.csv')
    mean = pd.read_csv(analysis/'equal_set.csv').set_index(['method','condition'])
    main = pd.read_csv(analysis/'metrics_verified.csv')
    candidate_rows = main[main.method==METHOD]
    if (candidate_rows.groupby(['set','seed']).threshold.nunique() != 1).any():
        raise ValueError('Candidate threshold differs between captures or conditions')
    validation = candidate_rows[candidate_rows.condition.eq('validation') & candidate_rows.file.eq('ALL')]
    if len(validation) != 12 or (validation.FAR_per_100k > 100 + 1e-9).any():
        raise ValueError('Source validation budget violated or incomplete')
    # Reject silent drift in the frozen comparator aggregates.
    frozen = pd.read_csv(CODE/'output/thesis_supervisor_final_2026-11-09/audit/primary_equal_set.csv').set_index(['method','condition'])
    six_methods = pd.concat([frozen, mean.loc[[METHOD]]])
    if six_methods.index.duplicated().any(): raise ValueError('Duplicate method/condition aggregate')
    six_methods.to_csv(analysis/'six_method_equal_set.csv')
    for rep in ['raw_transformer','structural_transformer']:
        for c in 'ABCD':
            np.testing.assert_allclose(mean.loc[(rep,c),metrics].to_numpy(float), frozen.loc[(rep,c),metrics].to_numpy(float), rtol=1e-12, atol=1e-12)
    secondary_paths = [p for p in (OUT/'secondary').glob('attempt_*/manifest.json')
                       if json.loads(p.read_text())['status']=='COMPLETE']
    if len(secondary_paths) != 1: raise ValueError('Complete matched probe and runtime checks before final report')
    valid_manifest(secondary_paths[0])
    secondary = secondary_paths[0].parent
    probe = pd.read_csv(secondary/'probe_means.csv').set_index(['representation','target','control'])
    timing = pd.read_csv(secondary/'runtime.csv')
    if len(timing)!=6 or timing.duplicated(['device','representation']).any() or not timing.n.eq(900).all():
        raise ValueError('Incomplete matched runtime matrix')
    if not np.isfinite(timing[['p50_ms','p95_ms','mean_ms']].to_numpy()).all():
        raise ValueError('Invalid timing')
    probe.to_csv(analysis/'probe_means.csv')
    timing.to_csv(analysis/'runtime_remeasured.csv', index=False)
    lines = ['KẾT QUẢ THỬ NGHIỆM BỔ SUNG MIXSTYLE — HOÀN TẤT 10/11/2026',
             'Thí nghiệm hậu nghiệm; giữ nguyên kết quả và bản khóa luận đã bàn giao.',
             '12 fit mới (4 set x 3 seed), 24 baseline tái sử dụng; W64/content/file-order.',
             'Có thêm một pilot phần mềm 2 epoch trên 80 cửa sổ; không tính vào 12 fit nghiên cứu.',
             'Ngưỡng chỉ chọn từ validation nguồn với FAR budget 100/100000.',
             'Mọi điểm dưới đây trung bình seed trong set, rồi trọng số ngang nhau giữa set.', '']
    comparisons = []
    byset = pd.read_csv(analysis/'by_set.csv').set_index(['set','method','condition'])
    for c in 'ABCD':
        lines.append('Điều kiện '+c)
        for rep in ['raw_transformer','structural_transformer',METHOD]:
            r = mean.loc[(rep,c)]
            lines.append(f'  {rep}: Recall {r.Recall*100:.2f}%; FAR {r.FAR_per_100k/1000:.2f}%; AP {r.AP:.4f}; F1 {r.Attack_F1:.4f}')
        candidate = mean.loc[(METHOD,c)]
        for rep in ['raw_transformer','structural_transformer']:
            base = mean.loc[(rep,c)]
            dr, df = candidate.Recall-base.Recall, candidate.FAR_per_100k-base.FAR_per_100k
            wins = sum(byset.loc[(s,METHOD,c),'Recall'] > byset.loc[(s,rep,c),'Recall'] for s in [f'set_0{i}' for i in range(1,5)])
            label = effect_label(dr, df)
            comparisons.append(dict(condition=c, baseline=rep, recall_delta_pp=dr*100, far_delta_pp=df/1000,
                                    interpretation=label, sets_with_higher_recall=int(wins)))
            lines.append(f'  So với {rep}: delta Recall {dr*100:+.2f} điểm %; delta FAR {df/1000:+.2f} điểm %; Recall cao hơn ở {wins}/4 set; {label}.')
        lines.append('')
    lines += ['NGOẠI BỘ: 57 capture, cùng checkpoint set_01, không hiệu chỉnh xe đích.',
              'Bảng này gộp số đếm/cửa sổ trong mỗi dataset trước, sau đó trung bình 3 seed.',
              'Không so số gộp này với trung bình ngang nhau giữa capture trong bảng khác.']
    for dataset in sorted(d.dataset.unique()):
        lines.append(dataset)
        for rep in ['raw','structural',METHOD]:
            r = extmean.loc[(dataset,rep)]
            def fmt(x, scale=1): return 'không xác định' if pd.isna(x) else f'{x*scale:.4f}'
            lines.append(f'  {rep}: Recall% {fmt(r.Recall,100)}, FAR% {fmt(r.FAR_per_100k,.001)}, AP {fmt(r.AP)}')
    flags = []
    for _,r in main[(main.method==METHOD)&main.file.eq('ALL')].iterrows():
        if r.TP+r.FP == 0: flags.append(f'{r["set"]}/{r.seed}/{r.condition}: toàn benign')
        if r.TP+r.FP == r.Total_Windows: flags.append(f'{r["set"]}/{r.seed}/{r.condition}: toàn attack')
    for _,r in pooled[(pooled.method==METHOD)&(pooled.Attack_Windows>0)&(pooled.Benign_Windows>0)].iterrows():
        if r.TP+r.FP == 0: flags.append(f'Ngoại bộ {r.dataset}/{r.seed}: toàn benign trên tập có cả hai lớp')
        if r.TP+r.FP == r.Total_Windows: flags.append(f'Ngoại bộ {r.dataset}/{r.seed}: toàn attack trên tập có cả hai lớp')
    lines += ['', 'ĐIỂM VẬN HÀNH SUY BIẾN', *(flags or ['Không có pooled cell dự đoán toàn một lớp trong CTT.']),
              '', 'PROBE TRÊN ĐÚNG MẪU ĐÃ DÙNG CHO BASELINE']
    for rep in ['raw','structural',METHOD]:
        vehicle = probe.loc[(rep,'vehicle','learned'),'balanced_accuracy']
        attack = probe.loc[(rep,'attack','learned'),'balanced_accuracy']
        lines.append(f'  {rep}: vehicle balanced accuracy {vehicle*100:.2f}%; attack {attack*100:.2f}%.')
    lines += ['Chance: vehicle 25%, attack 50%; báo đủ constant/random/permuted controls trong probe_means.csv.',
              'Probe là khả năng giải mã tuyến tính hậu nghiệm, không chứng minh độc lập xe hoặc phiên ghi.',
              '', 'THỜI GIAN SUY LUẬN — ĐO LẠI CẢ BA PIPELINE CÙNG PHIÊN']
    for _,r in timing.iterrows():
        lines.append(f'  {r.device}/{r.representation}: median {r.p50_ms:.3f} ms; p95 {r.p95_ms:.3f} ms; n={int(r.n)}.')
    lines += ['Batch1: đọc CSV, kiểm tra, tạo cả hai biểu diễn và inference. Máy desktop dùng chung,',
              'đọc lặp có cache; không phải deadline ECU, độ trễ thu thập hay bằng chứng GPU huấn luyện chậm.',
              '', 'GIỚI HẠN',
              '- six_method_equal_set.csv bổ sung ba đối thủ thích ứng từ bảng cũ; không dùng điểm công bố gốc để xếp hạng.',
              '- Một cấu hình cố định, không chọn seed/set tốt nhất. Không bảo đảm thắng phương pháp gốc.',
              '- Test đã xem trước nên đây là hậu nghiệm; chưa xác nhận trên xe/phiên mới độc lập.',
              '- Capture bootstrap là mô tả theo capture, không phải CI cho quần thể xe.',
              '- Đã chạy probe và đo lại runtime; các phép đo này không xác nhận bất biến xe hay thời gian thực trên ECU.',
              '- CUDA attention cảnh báo có thuật toán backward không tất định; cùng seed không bảo đảm tái lập bit-for-bit giữa các lần huấn luyện.',
              '- Không đổi criterion Recall B sang AP hoặc sang điều kiện khác nếu B thất bại.',
              '- Điểm tăng chỉ đáng gọi cải thiện đồng thời nếu recall tăng và FAR không tăng so cùng baseline.',
              '', 'Nguồn phương pháp: Zhou et al., Domain Generalization with MixStyle, ICLR 2021.',
              'https://arxiv.org/abs/2104.02008v1',
              'Bản thích ứng: chuỗi sau linear projection, ghép cùng nhãn nguồn; không phải bản CNN gốc.']
    (analysis/'BAO_CAO_MIXSTYLE.txt').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    pd.DataFrame(comparisons).to_csv(analysis/'comparisons.csv', index=False)
    report = dict(status='VERIFIED_COMPLETE', new_fits=12, reused_baselines=24, external_captures=57,
                  external_metric_rows=len(d), primary_baseline_aggregates_unchanged=True,
                  post_hoc=True, inference_labels_used=False, primary_comparisons=[r for r in comparisons if r['condition']=='B'],
                  unperformed_secondary_studies=[], completion_date='2026-11-10',
                  secondary_manifest_sha256=sha256_file(secondary_paths[0]),
                  aggregation_fix_provenance='provenance/aggregation_fix.json',
                  analysis_runner_sha256=sha256_file(CODE/'scripts/run_mixstyle_study.py'),
                  report_script_sha256=sha256_file(Path(__file__)))
    json_write(analysis/'final_report.json', json_safe(report))
    hashes = {p.relative_to(analysis).as_posix(): sha256_file(p) for p in analysis.glob('*') if p.is_file() and p.name!='manifest.json'}
    json_write(analysis/'manifest.json', dict(status='COMPLETE', artifact_hashes=hashes))
    print('\n'.join(lines[:25]))
    print('VERIFIED: 57 external captures /', len(d), 'aligned metric rows; report:', analysis/'BAO_CAO_MIXSTYLE.txt')


if __name__ == '__main__': main()
