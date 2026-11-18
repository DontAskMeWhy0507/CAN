"""Compact figures, paired capture sensitivity, and Vietnamese research handoff."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parents[1] / 'results/benign_invariant_pipeline_2026-11-11'
LABELS = {'frozen_source': 'Original / source threshold', 'frozen_targetq': 'Original / target threshold',
          'lr_targetq': 'Shared LR / target threshold', 'diag_lr': 'Benign diagonal + LR',
          'white_lr': 'Benign whitening + LR', 'white_leace_lr': 'Whitening + LEACE + LR',
          'white_pca8_lr': 'Whitening + PCA8 + LR', 'white_inlp8_lr': 'Whitening + INLP8 + LR'}


def bootstrap(files):
    rows = []
    f = files[(files.alpha == .01) & (files.view == 'content_disjoint')]
    rng = np.random.default_rng(20261111)
    for vehicle, group in f.groupby('target'):
        tokens = sorted(group.token.unique())
        seeds = sorted(group.seed.unique())
        values = {}
        for method, g in group.groupby('method'):
            values[method] = np.array([g[g.seed == seed].set_index('token').loc[tokens, ['TP', 'FN', 'FP', 'TN']].to_numpy() for seed in seeds])
        draws = rng.integers(len(tokens), size=(1000, len(tokens)))
        def measures(counts):
            tp, fn, fp, tn = np.moveaxis(counts, -1, 0)
            with np.errstate(divide='ignore', invalid='ignore'):
                return np.stack([tp / (tp + fn), fp / (fp + tn), 2 * tp / (2 * tp + fp + fn)], -1)
        baseline = values['frozen_targetq']
        for method, array in values.items():
            if method == 'frozen_targetq':
                continue
            estimate = (measures(array.sum(1)) - measures(baseline.sum(1))).mean(0)
            delta = (measures(array[:, draws, :].sum(2)) - measures(baseline[:, draws, :].sum(2))).mean(0)
            for j, metric in enumerate(['Recall', 'FAR', 'F1']):
                valid = delta[:, j][np.isfinite(delta[:, j])]
                lo, hi = np.quantile(valid, [.025, .975]) if len(valid) else [np.nan, np.nan]
                rows.append(dict(target=vehicle, method=method, comparator='frozen_targetq', metric=metric,
                                 estimate=estimate[j], low=lo, high=hi, valid_replicates=len(valid), captures=len(tokens),
                                 interpretation='Descriptive paired capture resampling; not independent-drive or new-vehicle confidence.'))
    pd.DataFrame(rows).to_csv(OUT / 'paired_capture_bootstrap.csv', index=False)


def main():
    assert json.loads((OUT / 'AUDIT.json').read_text())['status'] == 'PASS'
    summary = pd.read_csv(OUT / 'summary.csv')
    probes = pd.read_csv(OUT / 'probe_summary.csv')
    allprobes = pd.read_csv(OUT / 'all_probes.csv')
    allmetrics = pd.read_csv(OUT / 'all_metrics.csv')
    files = pd.read_csv(OUT / 'per_capture.csv')
    bootstrap(files)
    s = summary[(summary.alpha == .01) & (summary.view == 'content_disjoint')].set_index('method').loc[list(LABELS)]
    p = probes[(probes.scope == 'embedding') & (probes.task == 'vehicle') & (probes.control == 'learned')].pivot(index='method', columns='decoder', values='mean').loc[list(LABELS)]
    risk = probes[(probes.scope == 'risk') & (probes.task == 'vehicle') & (probes.control == 'learned')].pivot(index='method', columns='decoder', values='mean').loc[list(LABELS)]
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10})
    fig, axes = plt.subplots(1, 3, figsize=(16, 6.2), gridspec_kw={'width_ratios': [1, 1, 1]})
    yy = np.arange(len(s))
    for ax, cols, title in [(axes[0], (s.Recall * 100, s.FAR_per_100k / 1000), 'Held-out attack detection'),
                            (axes[1], (p.LR * 100, p.MLP * 100), 'Vehicle probe: representation'),
                            (axes[2], (risk.LR * 100, risk.MLP * 100), 'Vehicle probe: scalar risk')]:
        names = ('Recall', 'FAR') if ax is axes[0] else ('LR', 'MLP (300 max)')
        for off, data, color, label in zip([-.17, .17], cols, ['#206b9e', '#d78735'], names):
            ax.barh(yy + off, data, height=.3, label=label, color=color)
            for y, value in zip(yy + off, data):
                ax.text(value + .6, y, f'{value:.1f}', fontsize=8, va='center')
        if ax is not axes[0]:
            ax.axvline(25, color='#555', linestyle='--', linewidth=1, label='Chance 25%')
        else:
            ax.axvline(1, color='#777', linestyle=':', linewidth=1, label='Calibration target 1%')
        ax.set(yticks=yy, yticklabels=list(LABELS.values()) if ax is axes[0] else [''] * len(s),
               xlim=(0, 110), xlabel='Percent', title=title)
        ax.invert_yaxis(); ax.grid(axis='x', alpha=.15); ax.set_axisbelow(True)
        ax.legend(loc='upper center', bbox_to_anchor=(.5, -.13), ncol=2, frameon=False, fontsize=8)
        ax.spines[['top', 'right']].set_visible(False)
    fig.suptitle('Benign-target calibration and source-fitted vehicle erasure', fontsize=15)
    fig.text(.5, .015, 'Equal vehicle weight after averaging 3 seeds. Entire calibration captures and aligned content matches excluded.\nRisk compression does not establish representation independence. Original/source threshold uses its pre-existing source FAR budget.', ha='center', fontsize=9)
    fig.subplots_adjust(left=.21, right=.98, bottom=.24, top=.88, wspace=.15)
    fig.savefig(OUT / 'results_overview.png', dpi=160)
    fig.savefig(OUT / 'results_overview.pdf')
    plt.close(fig)
    lines = ['KẾT QUẢ THỬ NGHIỆM HIỆU CHUẨN LÀNH TÍNH VÀ GIẢM THÔNG TIN XE — 11/11/2026', '',
             'Trạng thái: hoàn tất 96 pipeline trên 12 encoder đóng băng; kiểm toán tính lại quyết định và metric: PASS.',
             'Đây là nghiên cứu hậu nghiệm, có sử dụng dữ liệu lành của xe đích theo sự cho phép của người dùng; không phải zero-shot thuần nguồn.', '',
             'THIẾT KẾ',
             'Mỗi xe dành riêng một bản ghi lành: 2.000 cửa sổ W64 lấy trải đều toàn bản ghi; 1.000 vị trí chẵn chuẩn hóa, 1.000 vị trí lẻ chọn ngưỡng. Phải quan sát cả bản ghi, không thể gọi là vài giây khởi động.',
             'Xóa toàn bộ bốn bản ghi hiệu chuẩn (54.231 cửa sổ) khỏi đánh giá; kiểm tra bổ sung loại 740 cửa sổ trùng nội dung ở một bản ghi khác. Trùng nội dung xét CID/DLC/payload ở cửa sổ W64 căn chỉnh.',
             'Giữ lại từng xe để kiểm tra (LOVO), ba seed 42/43/44. Encoder Structural giữ nguyên; eraser, PCA, INLP và đầu LR chỉ fit trên ba xe nguồn. Chuẩn hóa xe mới chỉ dùng phần lành riêng của xe đó.',
             'Hai ngưỡng được cố định trước: alpha 1% chính, 0,1% phụ. Ngưỡng gốc frozen_source giữ nguyên ngân sách FAR nguồn cũ; nhãn alpha trong dòng này không làm thay đổi ngưỡng.',
             'Không dùng nhãn tấn công đích để chọn phương pháp, chiều nén hay ngưỡng. Nhãn đích chỉ dùng kiểm tra và probe hậu nghiệm; các xe đã xuất hiện ở vòng nghiên cứu trước, không phải bộ xác nhận hoàn toàn mới.', '',
             'KẾT QUẢ CHÍNH — trung bình đều 4 xe sau trung bình 3 seed; loại trùng nội dung; alpha=1%',
             'method | recall% | FAR% | F1 | AP | probe xe LR% | probe xe MLP300%']
    for method, row in s.iterrows():
        lines.append(f'{method} | {100*row.Recall:.2f} | {row.FAR_per_100k/1000:.3f} | {row.Attack_F1:.4f} | {row.AP:.4f} | {100*p.loc[method,"LR"]:.2f} | {100*p.loc[method,"MLP"]:.2f}')
    lines += ['', 'DIỄN GIẢI VÀ GIỚI HẠN',
              'Probe xe cân bằng có mức ngẫu nhiên 25%. Probe trên biểu diễn và probe trên điểm rủi ro một chiều là hai phép đo khác nhau. Nếu chỉ probe điểm rủi ro giảm thì không được kết luận encoder không chứa thông tin xe.',
              'LEACE xóa tương quan tuyến tính thực nghiệm với khái niệm xe có điều kiện theo nhãn trên nguồn. Điều đó không bảo đảm độc lập phi tuyến, không bảo đảm chuyển giao tới xe chưa thấy. INLP ở đây là biến thể có điều kiện dừng tại 8 chiều, có PCA8 làm đối chứng nén.',
              'Chuẩn hóa dùng trung bình/hiệp phương sai nền lành riêng từng xe. Cơ chế xử lý được chia sẻ nhưng trạng thái hiệu chuẩn vẫn phụ thuộc xe; không gọi toàn bộ hệ thống là hoàn toàn không phụ thuộc xe.',
              'Ngưỡng phân vị có hiệu lực thực nghiệm trên 1.000 mẫu hiệu chuẩn, không phải cam kết FAR trên xe/phiên khác. CAN có phụ thuộc thời gian và dịch chuyển phân phối. Ở alpha 0,1% và 1.000 mẫu, ngưỡng rất bảo thủ, nằm trên giá trị hiệu chuẩn lớn nhất.',
              'Tách bản ghi kiểm chứng được bằng hash; độc lập phiên lái chưa có metadata để xác nhận. Loại trùng cửa sổ căn chỉnh chưa phát hiện được mọi đoạn trùng lệch vị trí.',
              'Probe train/validation tách bản ghi, cân bằng xe x nhãn (1.600 mẫu mỗi phần). Probe train có thể trùng dữ liệu học encoder/đầu phân loại nguồn; kết quả validation là phép kiểm tra giải mã, không phải thí nghiệm nhân quả.',
              'Không được dùng việc xóa biểu diễn đến hằng số hoặc đánh mất khả năng phát hiện làm bằng chứng thành công. Cần đồng thời xem FAR, recall, AP và probe.',
              'Khoảng bootstrap trong paired_capture_bootstrap.csv lấy lại cả bản ghi theo cặp; chỉ mô tả các bản ghi hiện có, không phải độ tin cậy trên quần thể xe hay phiên lái độc lập.', '',
              'CẢNH BÁO TỐI ƯU PROBE']
    warnings = allprobes[allprobes.warnings > 0]
    lines.append(f'{len(warnings)}/{len(allprobes)} ô kết quả probe có cảnh báo (kể cả kết quả điều khiển sao chép từ cùng biểu diễn). Chi tiết thông điệp trong fits/*/seed_*/probed.json; không xem không hội tụ là bằng chứng độc lập.')
    if len(warnings):
        lines.append(warnings.groupby(['task', 'decoder', 'control']).size().to_string())
    stress_status = OUT / 'stress_probe/status.json'
    if stress_status.exists() and json.loads(stress_status.read_text())['status'] == 'COMPLETE':
        stress = pd.read_csv(OUT / 'stress_probe/all_results.csv')
        table = stress.groupby('method').agg(probe_mean=('balanced_accuracy', 'mean'),
                                            probe_min=('balanced_accuracy', 'min'),
                                            probe_max=('balanced_accuracy', 'max'),
                                            max_iterations=('n_iter', 'max'))
        lines += ['', 'KIỂM TRA BỔ SUNG: MLP GIỚI HẠN 1.500 VÒNG',
                  'Chạy cùng cấu trúc MLP(64,32), cùng dữ liệu/seed probe; kéo dài tối ưu cho bốn nhánh. Không dùng kết quả này để sửa detector hay ngưỡng.', table.to_string(),
                  'Các giá trị probe trong bảng này nằm trên thang 0–1. Chi tiết và model probe lưu tại stress_probe/.']
        fig, ax = plt.subplots(figsize=(8.5, 4.5))
        methods = ['frozen_source', 'white_leace_lr', 'white_pca8_lr', 'white_inlp8_lr']
        x = np.arange(len(methods))
        for i, method in enumerate(methods):
            vals = stress[stress.method == method].balanced_accuracy.to_numpy() * 100
            ax.bar(i, vals.mean(), width=.55, color=['#526c83', '#3f8c94', '#ad8d45', '#a55c72'][i])
            ax.scatter(i + np.linspace(-.17, .17, len(vals)), vals, s=14, color='#222', zorder=3)
            ax.text(i, vals.mean() + 3, f'{vals.mean():.1f}%', ha='center', fontsize=11)
        ax.axhline(25, color='#444', ls='--', label='Chance 25%')
        ax.set(xticks=x, xticklabels=['Original', 'Whitening + LEACE', 'Whitening + PCA8', 'Whitening + INLP8'],
               ylim=(0, 105), ylabel='Vehicle balanced accuracy (%)', title='Fresh nonlinear probes: MLP, maximum 1500 iterations')
        ax.spines[['top', 'right']].set_visible(False)
        ax.legend(loc='upper right', frameon=False)
        fig.text(.5, .015, 'Bars: mean over 4 encoders held out by vehicle × 3 seeds. Dots: individual probe results.\nEach probe uses a fixed, balanced, recording-disjoint four-vehicle split.', ha='center', fontsize=9)
        fig.subplots_adjust(bottom=.22)
        fig.savefig(OUT / 'stress_probe_overview.png', dpi=160)
        plt.close(fig)
    lines += ['', 'CÁCH DIỄN ĐẠT ĐÓNG GÓP TRONG KHÓA LUẬN',
              '1. Xây dựng giao thức đánh giá tách biệt hiệu chuẩn ngưỡng, chuẩn hóa theo nền lành và loại bỏ thông tin xe trên biểu diễn CAN, với đối chứng đầu phân loại và đối chứng nén cùng số chiều.',
              '2. Hiện thực và đánh giá các pipeline dùng một bản ghi lành riêng của xe mới; các phép biến đổi LEACE/INLP và đầu phân loại được học trên xe nguồn. Đây là ứng dụng/điều chỉnh các kỹ thuật có sẵn, không tuyên bố phát minh LEACE hay INLP.',
              '3. Định lượng đồng thời khả năng phát hiện tấn công, báo động giả và khả năng giải mã xe bằng probe mới; chỉ ra đánh đổi khi giảm thông tin xe và giới hạn chuyển giao giữa các xe được khảo sát.',
              'Không viết: chứng minh biểu diễn hoàn toàn độc lập xe, bảo đảm FAR 1% trên mọi xe, hay không cần dữ liệu xe mới.',
              'Hướng nghiên cứu tiếp theo, CHƯA CHẠY: học lại encoder với ràng buộc bất biến phi tuyến có điều kiện theo nhãn và đối chứng cùng kiến trúc; kiểm tra trên xe/phiên mới chưa từng được dùng để xây dựng giả thuyết. Không xem đây là giải pháp đã đạt.', '',
              'TÀI LIỆU NỀN',
              'LEACE: https://arxiv.org/html/2306.03819v4 — Belrose và cộng sự; giới hạn ở linear concept erasure.',
              'INLP: https://aclanthology.org/2020.acl-main.647/ — Ravfogel và cộng sự, ACL 2020.', '',
              'TÁI LẬP',
              'Chạy: .venv/Scripts/python.exe -u code/scripts/run_benign_invariant_pipeline.py',
              'Kiểm toán: .venv/Scripts/python.exe code/scripts/audit_benign_invariant_pipeline.py',
              'Báo cáo: .venv/Scripts/python.exe code/scripts/report_benign_invariant_pipeline.py',
              'Chạy lại tái sử dụng artifact có hash, không huấn luyện lại encoder. frozen_protocol.json khóa cấu hình và mã thực thi.',
              'Các số liệu đầy đủ: summary.csv, per_vehicle.csv, all_metrics.csv, all_probes.csv, per_capture.csv. Ngưỡng, phép chiếu và model LR: fits/*/seed_*/states.joblib.']
    (OUT / 'BAO_CAO_KET_QUA.txt').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(s[['Recall', 'FAR_per_100k', 'Attack_F1', 'AP']].to_string())
    print(p.to_string())


if __name__ == '__main__':
    main()
