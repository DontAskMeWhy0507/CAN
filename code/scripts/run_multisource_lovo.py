"""Frozen, resumable post-hoc leave-one-vehicle-out study. New artifacts only."""
from pathlib import Path
import argparse
import collections
import gc
import hashlib
import json
import os
import platform
import sys
import time
import traceback
import warnings

CODE = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(CODE), str(CODE / 'src')]
os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG', ':4096:8')
import numpy as np
import pandas as pd
import torch
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import balanced_accuracy_score
from comparison.data import load_manifest, partitions, sample, batches, mapped
from can_research.io import sha256_file, json_write
from can_research.provenance import json_safe
from can_research.metrics import compute_binary_metrics, choose_threshold_on_validation
from can_research.models import CANTransformer
from research_multisource.model import train, infer

CACHE = CODE / 'results/comparison_data_v1'
DATA = CODE / 'results/multisource_lovo_2026-11-10'
OUT = CODE / 'results/multisource_lovo_v2_2026-11-10'
CONFIG = CODE / 'configs/multisource_lovo_2026-11-10.json'
CFG = json.loads(CONFIG.read_text())
VEHICLES = ['Impala', 'Traverse', 'Silverado', 'Forester']
TARGET = [2, 3, 3, 1]


def write(path, data):
    json_write(path, json_safe(data))


def status(stage, **kw):
    row = dict(stage=stage, utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), **kw)
    write(OUT / 'live_status.json', row)
    print(json.dumps(json_safe(row), ensure_ascii=False), flush=True)


def signature():
    paths = [Path(__file__), CONFIG, CODE / 'research_multisource/model.py',
             CODE / 'comparison/data.py', CODE / 'comparison/content_features.py',
             CODE / 'src/can_research/models.py', CODE / 'src/can_research/metrics.py',
             CODE / 'src/can_research/io.py', CODE / 'src/can_research/provenance.py']
    return dict(code={p.relative_to(CODE).as_posix(): sha256_file(p) for p in paths},
                cache_manifest=sha256_file(CACHE / 'manifest.json'), config=CFG,
                environment=dict(python=platform.python_version(), torch=torch.__version__,
                                 numpy=np.__version__, gpu=torch.cuda.get_device_name(0)))


def inventory(manifest):
    groups = collections.defaultdict(list)
    for original in manifest['files']:
        e = dict(original)
        si = int(e['set'][-2:]) - 1
        e['vehicle'] = TARGET[si] if 'unknown_vehicle' in e['folder'] else si
        groups[e['cache_sha256']].append(e)
    rejected, entries, by_source = [], [], {}
    for digest, aliases in sorted(groups.items()):
        if len({e['vehicle'] for e in aliases}) != 1:
            rejected.append(dict(hash=digest, reason='conflicting vehicle identity', aliases=aliases))
            continue
        # Prefer canonical source train, then known-vehicle captures.
        e = dict(sorted(aliases, key=lambda a: (a['folder'] != 'train_01', 'unknown_vehicle' in a['folder'], a['source']))[0])
        e['token'] = digest[:24]
        e['aliases'] = [a['source'] for a in aliases]
        e['family'] = Path(e['source']).stem.rsplit('-', 1)[0]
        entries.append(e)
        for a in aliases:
            by_source[a['source']] = e
    source = {}
    for v in range(4):
        old = partitions(manifest, f'set_{v + 1:02}')
        source[v] = {role: list({by_source[e['source']]['token']: by_source[e['source']]
                                for e in old[role] if e['source'] in by_source}.values())
                     for role in ('train', 'validation')}
        assert all(e['vehicle'] == v for es in source[v].values() for e in es)
        assert {e['token'] for e in source[v]['train']}.isdisjoint(e['token'] for e in source[v]['validation'])
    return entries, source, rejected


def split_fold(entries, source, target):
    split = {role: [e for v in range(4) if v != target for e in source[v][role]]
             for role in ('train', 'validation')}
    split['test'] = [e for e in entries if e['vehicle'] == target]
    hashes = {role: {e['cache_sha256'] for e in es} for role, es in split.items()}
    assert hashes['train'].isdisjoint(hashes['validation'])
    assert (hashes['train'] | hashes['validation']).isdisjoint(hashes['test'])
    assert all(e['vehicle'] != target for role in ('train', 'validation') for e in split[role])
    assert all(e['vehicle'] == target for e in split['test'])
    return split


def prepare():
    status('VERIFYING_FEATURE_CACHE', reused_cache=str(DATA / 'features'))
    manifest = load_manifest(CACHE, verify=False)
    entries, source, rejected = inventory(manifest)
    write(OUT / 'vehicle_identity_exclusions.json', rejected)
    write(OUT / 'data_inventory.json', entries)
    splits = {}
    for v in range(4):
        split = split_fold(entries, source, v)
        splits[str(v)] = {role: [e['token'] for e in es] for role, es in split.items()}
    write(OUT / 'folds.json', splits)
    for i, e in enumerate(entries):
        dest = DATA / 'features' / e['token']
        meta = dest / 'complete.json'
        if meta.exists():
            m = json.loads(meta.read_text())
            for name, digest in m['hashes'].items():
                if sha256_file(dest / name) != digest:
                    raise ValueError(f'Changed feature cache {dest / name}')
            continue
        status('PREPARING', capture=i + 1, total=len(entries), file=e['source'])
        if sha256_file(CACHE / e['cache']) != e['cache_sha256']:
            raise ValueError('Input binary cache hash mismatch')
        dest.mkdir(parents=True, exist_ok=True)
        raw = np.lib.format.open_memmap(dest / 'raw.npy', mode='w+', dtype=np.float32, shape=(e['windows'], 64, 28))
        structural = np.lib.format.open_memmap(dest / 'structural.npy', mode='w+', dtype=np.float32, shape=(e['windows'], 64, 30))
        y = np.lib.format.open_memmap(dest / 'y.npy', mode='w+', dtype=np.int64, shape=(e['windows'],))
        for b in batches(CACHE, e, batch_windows=512, features=True):
            ix = b['ix']
            raw[ix], structural[ix], y[ix] = b['raw'], b['structural'], b['y']
        raw.flush(); structural.flush(); y.flush()
        del raw, structural, y
        write(meta, dict(entry=e, hashes={name: sha256_file(dest / name) for name in ('raw.npy', 'structural.npy', 'y.npy')}))
    selected = sample(CACHE, [e for es in source.values() for e in es['train']],
                      CFG['train_windows_per_class_per_file'], CFG['sampling_seed'])
    write(OUT / 'selected_train_windows.json', selected)
    # Independent decoder split by source recording round, balanced in both roles.
    probe = {}
    for role in ('train', 'validation'):
        cells = []
        for v in range(4):
            for cls in (0, 1):
                candidates = []
                for e in source[v][role]:
                    yy = load_array(e, 'y')
                    candidates.extend((e['token'], int(ix), v, cls) for ix in np.flatnonzero(yy == cls))
                rng = np.random.default_rng(CFG['sampling_seed'] + v * 2 + cls)
                ix = rng.choice(len(candidates), min(len(candidates), CFG['probe_cap_per_vehicle_class']), replace=False)
                cells.append([candidates[j] for j in ix])
        n = min(map(len, cells))
        assert n > 0
        probe[role] = [row for cell in cells for row in cell[:n]]
    write(OUT / 'probe_selection.json', probe)
    write(OUT / 'preparation_complete.json', dict(status='COMPLETE', captures=len(entries),
          conflicting_hashes=len(rejected), excluded_paths=sum(len(r['aliases']) for r in rejected),
          windows=sum(e['windows'] for e in entries), per_vehicle={VEHICLES[v]: sum(e['windows'] for e in entries if e['vehicle'] == v) for v in range(4)},
          planned_fits=48))


def load_array(e, name):
    return np.load(DATA / 'features' / e['token'] / (name + '.npy'), mmap_mode='r')


def method_x(e, method, ix=None):
    x = load_array(e, 'raw' if method == 'raw' else 'structural')
    if ix is not None:
        x = x[ix]
    if method == 'relative_cadv':
        x = x[..., [0] + list(range(9, 30))]
    return x


def load_train(split, method, selected, target):
    xs, ys, ds = [], [], []
    domain_ids = [v for v in range(4) if v != target]
    for e in split['train']:
        ix = selected[e['source']]
        xs.append(method_x(e, method, ix))
        ys.append(load_array(e, 'y')[ix])
        ds.append(np.full(len(ix), domain_ids.index(e['vehicle']), dtype=np.int64))
    return np.concatenate(xs), np.concatenate(ys), np.concatenate(ds)


def load_model(folder, method):
    if (folder / 'trained.json').exists():
        meta = json.loads((folder / 'trained.json').read_text())
        if sha256_file(folder / 'checkpoint.pt') != meta['checkpoint_sha256']:
            raise ValueError('Changed frozen checkpoint')
    dim = 28 if method == 'raw' else 22 if method == 'relative_cadv' else 30
    model = CANTransformer(dim).cuda().eval()
    model.load_state_dict(torch.load(folder / 'checkpoint.pt', map_location='cuda', weights_only=True))
    return model


def unit_folder(v, seed, method):
    return OUT / 'fits' / VEHICLES[v] / f'seed_{seed}' / method


def train_all(entries, source):
    selected = json.loads((OUT / 'selected_train_windows.json').read_text())
    completed = 0
    for v in range(4):
        split = split_fold(entries, source, v)
        for method in CFG['methods']:
            todo = [s for s in CFG['seeds'] if not (unit_folder(v, s, method) / 'trained.json').exists()]
            if not todo:
                completed += 3
                continue
            status('LOADING_SOURCE', completed_fits=completed, target=VEHICLES[v], method=method)
            x, y, d = load_train(split, method, selected, v)
            for seed in CFG['seeds']:
                dest = unit_folder(v, seed, method)
                dest.mkdir(parents=True, exist_ok=True)
                if (dest / 'trained.json').exists():
                    completed += 1
                    continue
                start = time.perf_counter()
                status('STARTING_FIT', completed_fits=completed, target=VEHICLES[v], method=method, seed=seed, windows=len(y))
                def progress(row):
                    status('TRAINING', completed_fits=completed, total_fits=48, target=VEHICLES[v],
                           method=method, seed=seed, windows=len(y), **row)
                model, adv, logs = train(x, y, d, seed, CFG, method.endswith('cadv'), progress)
                torch.save(model.state_dict(), dest / 'checkpoint.pt')
                if adv is not None:
                    torch.save(adv.state_dict(), dest / 'adversary.pt')
                restored = load_model(dest, method)
                np.testing.assert_array_equal(infer(model, x[:32]), infer(restored, x[:32]))
                counts = collections.Counter((int(dom), int(label)) for dom, label in zip(d, y))
                write(dest / 'trained.json', dict(status='COMPLETE', checkpoint_sha256=sha256_file(dest / 'checkpoint.pt'),
                      seconds=time.perf_counter() - start, logs=logs, target_vehicle=VEHICLES[v],
                      source_vehicles=[VEHICLES[z] for z in range(4) if z != v],
                      train_windows=len(y), source_cell_counts={str(k): n for k, n in counts.items()},
                      training_capture_tokens=[e['token'] for e in split['train']]))
                del model, adv, restored
                torch.cuda.empty_cache()
                completed += 1
            del x, y, d
            gc.collect()
    status('TRAINING_COMPLETE', completed_fits=completed, total_fits=48)


def evaluate_all(entries, source):
    # Nothing from target scoring feeds back into training or model selection.
    assert all((unit_folder(v, s, m) / 'trained.json').exists()
               for v in range(4) for s in CFG['seeds'] for m in CFG['methods'])
    rows = []
    for v in range(4):
        split = split_fold(entries, source, v)
        families = {e['family'] for e in split['train'] if np.any(load_array(e, 'y') == 1)}
        for seed in CFG['seeds']:
            for method in CFG['methods']:
                dest = unit_folder(v, seed, method)
                if (dest / 'evaluated.json').exists():
                    rows.extend(pd.read_csv(dest / 'metrics.csv').to_dict('records'))
                    continue
                model = load_model(dest, method)
                model_rows = []
                tau = None
                for role in ('validation', 'test'):
                    ys, ss, captures = [], [], []
                    for e in split[role]:
                        status('EVALUATING', target=VEHICLES[v], seed=seed, method=method, role=role, file=e['source'])
                        score = infer(model, method_x(e, method))
                        y = np.asarray(load_array(e, 'y'))
                        pred_dir = dest / 'predictions' / role
                        pred_dir.mkdir(parents=True, exist_ok=True)
                        np.savez_compressed(pred_dir / (e['token'] + '.npz'), y=y, score=score)
                        ys.append(y); ss.append(score); captures.append((e, y, score))
                    yy, scores = np.concatenate(ys), np.concatenate(ss)
                    if role == 'validation':
                        tau = choose_threshold_on_validation(yy, scores, CFG['far_budget_per_100k'])
                        write(dest / 'threshold.json', dict(threshold=tau, source_only=True,
                              capture_tokens=[e['token'] for e in split[role]],
                              **compute_binary_metrics(yy, y_score=scores, threshold=tau)))
                    common = dict(target=VEHICLES[v], seed=seed, method=method, role=role, threshold=tau)
                    model_rows.append(dict(common, capture='ALL', family='ALL', familiarity='ALL',
                                           **compute_binary_metrics(yy, y_score=scores, threshold=tau)))
                    for e, y, score in captures:
                        model_rows.append(dict(common, capture=e['token'], family=e['family'],
                              familiarity='known' if e['family'] in families else 'unseen' if np.any(y == 1) else 'benign',
                              **compute_binary_metrics(y, y_score=score, threshold=tau)))
                    if role == 'test':
                        for familiar in ('known', 'unseen'):
                            chosen = [(y, s) for e, y, s in captures if np.any(y == 1) and ((e['family'] in families) == (familiar == 'known'))]
                            if chosen:
                                model_rows.append(dict(common, capture='FAMILY_GROUP', family='ALL', familiarity=familiar,
                                    **compute_binary_metrics(np.concatenate([p[0] for p in chosen]),
                                          y_score=np.concatenate([p[1] for p in chosen]), threshold=tau)))
                pd.DataFrame(model_rows).to_csv(dest / 'metrics.csv', index=False)
                write(dest / 'evaluated.json', dict(status='COMPLETE', threshold=tau,
                      metrics_sha256=sha256_file(dest / 'metrics.csv'),
                      prediction_hashes={p.relative_to(dest).as_posix(): sha256_file(p) for p in (dest / 'predictions').rglob('*.npz')}))
                rows.extend(model_rows)
                del model
                torch.cuda.empty_cache()
    pd.DataFrame(rows).to_csv(OUT / 'all_metrics.csv', index=False)


def probe_all(entries):
    by_token = {e['token']: e for e in entries}
    selected = json.loads((OUT / 'probe_selection.json').read_text())
    labels = {role: np.array([r[3] for r in rs]) for role, rs in selected.items()}
    vehicles = {role: np.array([r[2] for r in rs]) for role, rs in selected.items()}
    all_rows = []
    for method in CFG['methods']:
        data = {}
        for role, rs in selected.items():
            data[role] = np.stack([method_x(by_token[token], method, [ix])[0] for token, ix, _, _ in rs])
        for v in range(4):
            for seed in CFG['seeds']:
                dest = unit_folder(v, seed, method)
                if (dest / 'probes.csv').exists():
                    all_rows.extend(pd.read_csv(dest / 'probes.csv').to_dict('records'))
                    continue
                status('PROBING', target=VEHICLES[v], seed=seed, method=method)
                model = load_model(dest, method)
                z = {role: infer(model, x, embedding=True)[1] for role, x in data.items()}
                np.savez_compressed(dest / 'probe_embeddings.npz', **z)
                result = []
                for task, lab in [('vehicle', vehicles), ('attack', labels)]:
                    for decoder in ('linear', 'mlp'):
                        for control in ('learned', 'constant', 'permuted'):
                            xtr, xte = z['train'], z['validation']
                            ytr, yte = lab['train'], lab['validation']
                            if control == 'constant':
                                xtr, xte = np.zeros_like(xtr), np.zeros_like(xte)
                            if control == 'permuted':
                                ytr = np.random.default_rng(42).permutation(ytr)
                            clf = (LogisticRegression(C=1., max_iter=2000, random_state=42) if decoder == 'linear'
                                   else MLPClassifier(hidden_layer_sizes=(64, 32), alpha=.01,
                                                      max_iter=200, random_state=42, early_stopping=False))
                            pipe = make_pipeline(StandardScaler(), clf)
                            with warnings.catch_warnings(record=True) as caught:
                                warnings.simplefilter('always')
                                pipe.fit(xtr, ytr)
                            result.append(dict(target=VEHICLES[v], seed=seed, method=method, task=task,
                                decoder=decoder, control=control, balanced_accuracy=balanced_accuracy_score(yte, pipe.predict(xte)),
                                chance=.25 if task == 'vehicle' else .5,
                                warnings=' | '.join(str(w.message) for w in caught)))
                pd.DataFrame(result).to_csv(dest / 'probes.csv', index=False)
                all_rows.extend(result)
                del model
                torch.cuda.empty_cache()
        del data
        gc.collect()
    pd.DataFrame(all_rows).to_csv(OUT / 'all_probes.csv', index=False)


def analyze():
    metrics = pd.read_csv(OUT / 'all_metrics.csv')
    d = metrics[(metrics.role == 'test') & (metrics.capture == 'ALL')]
    assert len(d) == 48 and not d.duplicated(['target', 'seed', 'method']).any()
    columns = ['Recall', 'FAR_per_100k', 'AP', 'Attack_F1']
    per_vehicle = d.groupby(['target', 'method'])[columns].agg(['mean', 'std'])
    per_vehicle.to_csv(OUT / 'per_vehicle_results.csv')
    summary = d.groupby(['target', 'method'])[columns].mean().groupby('method').mean()
    summary['FAR_percent'] = summary.FAR_per_100k / 1000
    summary.to_csv(OUT / 'summary.csv')
    probes = pd.read_csv(OUT / 'all_probes.csv')
    assert len(probes) == 48 * 12
    pm = probes.groupby(['target', 'method', 'task', 'decoder', 'control']).balanced_accuracy.mean().groupby(['method', 'task', 'decoder', 'control']).mean()
    pm.to_csv(OUT / 'probe_summary.csv')
    # Paired per-capture bootstrap: conditional on captures, never a vehicle-population CI.
    bootstrap = []
    for v in VEHICLES:
        for seed in CFG['seeds']:
            for method in ['structural_cadv', 'relative_cadv']:
                left = metrics[(metrics.target == v) & (metrics.seed == seed) & (metrics.method == 'structural') & (metrics.role == 'test') & (~metrics.capture.isin(['ALL', 'FAMILY_GROUP']))].set_index('capture')
                right = metrics[(metrics.target == v) & (metrics.seed == seed) & (metrics.method == method) & (metrics.role == 'test') & (~metrics.capture.isin(['ALL', 'FAMILY_GROUP']))].set_index('capture').loc[left.index]
                a = left[['TP', 'FN', 'FP', 'TN']].to_numpy()
                b = right[['TP', 'FN', 'FP', 'TN']].to_numpy()
                rng = np.random.default_rng(42)
                ix = rng.integers(0, len(a), size=(1000, len(a)))
                def values(c):
                    tp, fn, fp, tn = c.T
                    with np.errstate(divide='ignore', invalid='ignore'):
                        return np.stack([tp / (tp + fn), 100000 * fp / (fp + tn), 2 * tp / (2 * tp + fp + fn)], axis=1)
                delta = values(b[ix].sum(1)) - values(a[ix].sum(1))
                estimate = values(b.sum(0)[None]) - values(a.sum(0)[None])
                for j, name in enumerate(['Recall', 'FAR_per_100k', 'Attack_F1']):
                    good = delta[np.isfinite(delta[:, j]), j]
                    bootstrap.append(dict(target=v, seed=seed, method=method, baseline='structural', metric=name,
                        estimate=estimate[0, j], low=np.quantile(good, .025) if len(good) else None,
                        high=np.quantile(good, .975) if len(good) else None, valid=len(good), captures=len(a)))
    pd.DataFrame(bootstrap).to_csv(OUT / 'paired_capture_bootstrap.csv', index=False)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.4))
    order = CFG['methods']
    for ax, col, label in zip(axes[:2], ['Recall', 'FAR_percent'], ['Target attack recall (%)', 'Target false alarm rate (%)']):
        vals = summary.loc[order, col] * (100 if col == 'Recall' else 1)
        ax.bar(range(4), vals, color=['#7a869a', '#2676ab', '#20856d', '#c18a38'])
        ax.set_xticks(range(4), ['Raw', 'Structural', 'Structural\n+ adversary', 'Relative\n+ adversary'])
        ax.set_ylabel(label)
        ax.set_ylim(0, 100)
    for i, decoder in enumerate(['linear', 'mlp']):
        vals = [pm.loc[(m, 'vehicle', decoder, 'learned')] * 100 for m in order]
        axes[2].bar(np.arange(4) + (i - .5) * .35, vals, width=.35, label=decoder)
    axes[2].axhline(25, color='black', linestyle='--', label='chance')
    axes[2].set_xticks(range(4), ['Raw', 'Structural', 'Structural\n+ adversary', 'Relative\n+ adversary'])
    axes[2].set_ylabel('Vehicle probe balanced accuracy (%)')
    axes[2].set_ylim(0, 100)
    axes[2].legend()
    fig.suptitle('Post-hoc multi-source leave-one-vehicle-out study | equal vehicle weights, 3 seeds')
    fig.tight_layout()
    fig.savefig(OUT / 'results_overview.png', dpi=180)
    plt.close(fig)
    report = ['NGHIÊN CỨU ĐA NGUỒN / ĐỐI KHÁNG XE — KẾT QUẢ THỰC CHẠY',
              '48 fit: 4 xe giữ ngoài × 3 seed × 4 phương pháp. Ngưỡng chỉ từ validation nguồn.',
              'Trung bình seed trong xe, sau đó trọng số ngang nhau giữa bốn xe.', '', summary.to_string(), '',
              'PROBE (encoder đóng băng; balanced accuracy):', pm.to_string(), '',
              'Giao thức mới, không so trực tiếp với A/B/C/D cũ hoặc probe 94,88% cũ.',
              'Đã loại toàn bộ hash có danh tính xe mâu thuẫn; xem vehicle_identity_exclusions.json.',
              'Hậu nghiệm trên xe đã được nghiên cứu; không xác nhận độc lập hoặc chứng minh độc lập thống kê.',
              'Probe test giữ ngoài nhóm recording-round; phiên lái độc lập chưa được xác minh.',
              'Cả recall, FAR và probe phải được xét đồng thời; probe thấp một mình không xác nhận thành công.',
              'Chi tiết từng xe/seed và CI bootstrap có điều kiện nằm trong các CSV kèm theo.']
    (OUT / 'BAO_CAO_KET_QUA.txt').write_text('\n'.join(report), encoding='utf-8')
    write(OUT / 'final_manifest.json', dict(status='COMPLETE', new_fits=48,
        artifact_hashes={p.relative_to(OUT).as_posix(): sha256_file(p) for p in OUT.rglob('*')
                        if p.is_file() and 'features' not in p.relative_to(OUT).parts and p.name not in ['live_status.json', 'final_manifest.json']},
        feature_cache=str(DATA / 'features'),
        features_manifest_hashes={p.parent.name: sha256_file(p) for p in (DATA / 'features').glob('*/complete.json')}))
    status('COMPLETE', completed_fits=48, total_fits=48, report=str(OUT / 'BAO_CAO_KET_QUA.txt'))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--stage', choices=['prepare', 'train', 'evaluate', 'probes', 'analyze', 'all'], default='all')
    args = parser.parse_args()
    if not torch.cuda.is_available():
        raise RuntimeError('CUDA required; refusing accidental CPU study')
    torch.set_num_threads(4)
    OUT.mkdir(parents=True, exist_ok=True)
    sig = signature()
    frozen = OUT / 'frozen_protocol.json'
    if frozen.exists():
        if json.loads(frozen.read_text()) != sig:
            raise ValueError('Frozen code/config changed. Start a new output version.')
    else:
        write(frozen, sig)
    try:
        if args.stage in ('prepare', 'all'):
            prepare()
        if not (OUT / 'preparation_complete.json').exists():
            raise ValueError('Prepare data first')
        entries, source, _ = inventory(load_manifest(CACHE, verify=False))
        if args.stage in ('train', 'all'):
            train_all(entries, source)
        if args.stage in ('evaluate', 'all'):
            evaluate_all(entries, source)
        if args.stage in ('probes', 'all'):
            probe_all(entries)
        if args.stage in ('analyze', 'all'):
            analyze()
    except BaseException as exc:
        status('FAILED', error=repr(exc), traceback=traceback.format_exc())
        raise


if __name__ == '__main__':
    main()
