"""Post-hoc benign-calibrated study. Never modifies parent study artifacts."""
from pathlib import Path
import argparse
import hashlib
import json
import time
import warnings
import sys
import gc

CODE = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(CODE), str(CODE / 'src'), str(CODE / 'scripts')]
import numpy as np
import pandas as pd
import torch
import joblib
from threadpoolctl import threadpool_limits
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import balanced_accuracy_score, average_precision_score
import run_multisource_lovo as parent
from research_multisource import invariant_pipeline as ip

OUT = CODE / 'results/benign_invariant_pipeline_2026-11-11'
CONFIG = CODE / 'configs/benign_invariant_pipeline_2026-11-11.json'
CFG = json.loads(CONFIG.read_text())
SEEDS = [42, 43, 44]
CAL = ['cfc622c0f26b8bf2752772b2', '1eb029c2ac266223954b2a54',
       'a662c434875ea976650c164c', 'de012dd85da143b8d26a9f8b']
ALPHAS = [.01, .001]
METHODS = CFG['methods']


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write(path, value):
    parent.write(path, value)


def status(stage, **kw):
    value = dict(stage=stage, utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), **kw)
    write(OUT / 'live_status.json', value)
    print(json.dumps(value, ensure_ascii=False), flush=True)


def freeze():
    OUT.mkdir(parents=True, exist_ok=True)
    paths = [Path(__file__), CONFIG, CODE / 'research_multisource/invariant_pipeline.py',
             CODE / 'research_multisource/model.py', CODE / 'scripts/run_multisource_lovo.py',
             CODE / 'comparison/data.py', CODE / 'src/can_research/metrics.py',
             CODE / 'src/can_research/models.py']
    value = dict(config=CFG, code={p.relative_to(CODE).as_posix(): parent.sha256_file(p) for p in paths},
                 parent_manifest=parent.sha256_file(parent.OUT / 'final_manifest.json'),
                 parent_audit=parent.sha256_file(parent.OUT / 'INDEPENDENT_AUDIT.json'),
                 torch=torch.__version__, numpy=np.__version__, calibration_tokens=CAL)
    dest = OUT / 'frozen_protocol.json'
    if dest.exists():
        assert read(dest) == value, 'Frozen protocol changed; use a new output directory'
    else:
        write(dest, value)


def packed_windows(e):
    frames = parent.mapped(parent.CACHE, e)
    n = e['windows'] * 64
    packed = np.empty(n, dtype=[('cid', '<u2'), ('dlc', 'u1'), ('payload', 'u1', (8,))])
    for name in packed.dtype.names:
        packed[name] = frames[name][:n]
    return packed.view(np.uint8).reshape(e['windows'], 64 * 11)


def prepare(entries, source):
    done = OUT / 'prepared.json'
    if done.exists():
        return
    by = {e['token']: e for e in entries}
    calibration, references = {}, set()
    for v, token in enumerate(CAL):
        e = by[token]
        assert e['vehicle'] == v and e['folder'] == 'train_01'
        assert token in {x['token'] for x in source[v]['validation']}
        assert not np.any(parent.load_array(e, 'y'))
        ix = np.linspace(0, e['windows'] - 1, 2000, dtype=np.int64)
        assert len(np.unique(ix)) == 2000
        calibration[str(v)] = dict(token=token, normalization=ix[::2].tolist(),
                                  threshold=ix[1::2].tolist(), excluded_windows=e['windows'])
        packed = packed_windows(e)
        references.update(hashlib.sha256(packed[i]).digest() for i in ix)
    write(OUT / 'calibration_selection.json', calibration)
    (OUT / 'overlap').mkdir(exist_ok=True)
    overlaps = {}
    for i, e in enumerate(entries):
        status('CHECKING_CALIBRATION_OVERLAP', capture=i + 1, total=len(entries))
        assert parent.sha256_file(parent.CACHE / e['cache']) == e['cache_sha256']
        packed = packed_windows(e)
        mask = np.fromiter((hashlib.sha256(row).digest() in references for row in packed), bool, len(packed))
        np.save(OUT / 'overlap' / (e['token'] + '.npy'), mask)
        overlaps[e['token']] = int(mask.sum())
    oldprobe = read(parent.OUT / 'probe_selection.json')
    probe = {}
    for role in ('train', 'validation'):
        masks = {e['token']: np.load(OUT / 'overlap' / (e['token'] + '.npy')) for e in entries}
        rows = [row for row in oldprobe[role] if row[0] not in CAL and not masks[row[0]][row[1]]]
        cells = [[row for row in rows if row[2] == v and row[3] == c] for v in range(4) for c in (0, 1)]
        n = min(CFG['probe_cap_per_cell'], min(map(len, cells)))
        assert n >= 50, ('Probe cell too small', role, n)
        rng = np.random.default_rng(CFG['probe_seed'])
        probe[role] = [cell[j] for cell in cells for j in rng.choice(len(cell), n, replace=False)]
    assert {r[0] for r in probe['train']}.isdisjoint(r[0] for r in probe['validation'])
    write(OUT / 'probe_selection.json', probe)
    write(OUT / 'prepared.json', dict(calibration=calibration, overlap_counts=overlaps,
          source_selection_sha256=parent.sha256_file(parent.OUT / 'selected_train_windows.json'),
          excluded_capture_windows=sum(by[t]['windows'] for t in CAL),
          probe_counts={k: len(v) for k, v in probe.items()},
          note='Aligned content overlap is a sensitivity test, not proof of independent drives.'))


def required_indices(entries, source, target):
    needed = {e['token']: set() for e in entries}
    cal = read(OUT / 'calibration_selection.json')
    for value in cal.values():
        needed[value['token']].update(value['normalization'] + value['threshold'])
    selected = read(parent.OUT / 'selected_train_windows.json')
    for v in range(4):
        if v != target:
            for e in source[v]['train']:
                needed[e['token']].update(selected[e['source']])
    for rows in read(OUT / 'probe_selection.json').values():
        for token, ix, _, _ in rows:
            needed[token].add(ix)
    for e in entries:
        if e['vehicle'] == target and e['token'] not in CAL:
            needed[e['token']] = np.arange(e['windows'], dtype=np.int64)
        else:
            needed[e['token']] = np.array(sorted(needed[e['token']]), dtype=np.int64)
    return {t: ix for t, ix in needed.items() if len(ix)}


def extract(entries, source, target):
    folder = OUT / 'embeddings' / parent.VEHICLES[target]
    folder.mkdir(parents=True, exist_ok=True)
    needed = required_indices(entries, source, target)
    by = {e['token']: e for e in entries}
    models = {}
    for i, (token, ix) in enumerate(needed.items()):
        dest = folder / (token + '.npz')
        marker = folder / (token + '.json')
        if marker.exists():
            assert parent.sha256_file(dest) == read(marker)['sha256']
            continue
        if not models:
            models = {seed: parent.load_model(parent.unit_folder(target, seed, 'structural'), 'structural') for seed in SEEDS}
        status('EXTRACTING', target=parent.VEHICLES[target], capture=i + 1, total=len(needed), windows=len(ix))
        e = by[token]
        x = parent.method_x(e, 'structural', ix)
        data = dict(ix=ix, y=np.array(parent.load_array(e, 'y')[ix]))
        for seed, model in models.items():
            score, z = parent.infer(model, x, embedding=True)
            data[f'z{seed}'], data[f'score{seed}'] = z, score
        np.savez(dest, **data)
        write(marker, dict(sha256=parent.sha256_file(dest), cache_sha256=e['cache_sha256'],
                           checkpoints={str(s): parent.sha256_file(parent.unit_folder(target, s, 'structural') / 'checkpoint.pt') for s in SEEDS}))
        del x, data
    del models
    gc.collect()
    torch.cuda.empty_cache()
    return folder


def take(folder, token, ix, seed):
    with np.load(folder / (token + '.npz')) as data:
        where = np.searchsorted(data['ix'], ix)
        assert np.array_equal(data['ix'][where], ix)
        return data[f'z{seed}'][where], data['y'][where], data[f'score{seed}'][where]


def transform(z, vehicle, state):
    if state['normalizers'] is not None:
        z = ip.normalize(z, state['normalizers'][int(vehicle)])
    if state['projection'] is not None:
        z = ip.project(z, state['projection'])
    return np.asarray(z, np.float64)


def fit_states(entries, source, target, seed, folder, dest):
    saved = dest / 'states.joblib'
    if saved.exists() and (dest / 'fitted.json').exists():
        assert parent.sha256_file(saved) == read(dest / 'fitted.json')['sha256']
        return joblib.load(saved)
    cal = read(OUT / 'calibration_selection.json')
    normalizers = {mode: {} for mode in ('diag', 'white')}
    for v in range(4):
        value = cal[str(v)]
        z, y, _ = take(folder, value['token'], value['normalization'], seed)
        assert not y.any()
        for mode in normalizers:
            normalizers[mode][v] = ip.benign_normalizer(z, mode)
    selected = read(parent.OUT / 'selected_train_windows.json')
    zs, ys, vs = [], [], []
    training_tokens = []
    for v in range(4):
        if v == target:
            continue
        for e in source[v]['train']:
            assert e['token'] not in CAL
            z, y, _ = take(folder, e['token'], selected[e['source']], seed)
            zs.append(z); ys.append(y); vs.append(np.full(len(y), v))
            training_tokens.append(e['token'])
    z, y, v = map(np.concatenate, (zs, ys, vs))
    w = ip.cell_weights(y, v)
    states, all_warnings = {}, []
    for method in METHODS:
        status('FITTING_SOURCE_HEAD', target=parent.VEHICLES[target], seed=seed, method=method)
        mode = 'diag' if method == 'diag_lr' else 'white' if method.startswith('white') else None
        state = dict(normalizers=None if mode is None else normalizers[mode], projection=None, head=None)
        x = np.array(z, dtype=np.float64)
        if mode:
            for domain in np.unique(v):
                x[v == domain] = ip.normalize(z[v == domain], normalizers[mode][int(domain)])
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always')
            if method == 'white_leace_lr':
                state['projection'] = ip.leace_fit(x, ip.conditional_concept(y, v, w), w)
            elif method == 'white_pca8_lr':
                state['projection'] = ip.pca_fit(x, w, 8)
            elif method == 'white_inlp8_lr':
                state['projection'] = ip.inlp_fit(x, y, v, dimensions=8)
            if state['projection'] is not None:
                x = ip.project(x, state['projection'])
            if not method.startswith('frozen'):
                state['head'] = ip.task_head(x, y, w)
            all_warnings.extend(dict(method=method, message=str(warn.message)) for warn in caught)
        references = {}
        for vehicle in range(4):
            c = cal[str(vehicle)]
            cz, cy, cs = take(folder, c['token'], c['threshold'], seed)
            assert not cy.any()
            references[vehicle] = cs if method.startswith('frozen') else ip.task_score(transform(cz, vehicle, state), state['head'])
        state['references'] = references
        state['thresholds'] = {alpha: ip.benign_threshold(references[target], alpha) for alpha in ALPHAS}
        if method == 'frozen_source':
            t = read(parent.unit_folder(target, seed, 'structural') / 'threshold.json')['threshold']
            state['thresholds'] = {alpha: t for alpha in ALPHAS}
        states[method] = state
    joblib.dump(states, saved)
    write(dest / 'fitted.json', dict(sha256=parent.sha256_file(saved), target=target, seed=seed,
          source_vehicles=sorted(set(v.tolist())), training_tokens=training_tokens,
          training_windows=len(y), warnings=all_warnings,
          thresholds={m: s['thresholds'] for m, s in states.items()},
          projection_details={m: {k: value for k, value in s['projection'].items() if k not in ('mean', 'matrix')}
                              for m, s in states.items() if s['projection'] is not None}))
    return states


def evaluate(entries, target, seed, folder, dest, states):
    if (dest / 'evaluated.json').exists():
        return
    per_file, aggregate = [], []
    data = []
    for e in entries:
        if e['vehicle'] != target or e['token'] in CAL:
            continue
        with np.load(folder / (e['token'] + '.npz')) as d:
            assert np.array_equal(d['ix'], np.arange(e['windows']))
            data.append((e, d[f'z{seed}'], d['y'], d[f'score{seed}'],
                         ~np.load(OUT / 'overlap' / (e['token'] + '.npy'))))
    for method, state in states.items():
        status('EVALUATING', target=parent.VEHICLES[target], seed=seed, method=method)
        prediction_dir = dest / 'predictions' / method
        prediction_dir.mkdir(parents=True, exist_ok=True)
        ys, scores, risks, masks = [], [], [], []
        for e, z, y, frozen, clean in data:
            score = frozen.astype(np.float64) if method.startswith('frozen') else ip.task_score(transform(z, target, state), state['head'])
            risk = score if method == 'frozen_source' else ip.calibrated_risk(score, state['references'][target])
            np.savez(prediction_dir / (e['token'] + '.npz'), y=y, score=score, risk=risk, clean=clean)
            ys.append(y); scores.append(score); risks.append(risk); masks.append(clean)
            for alpha in ALPHAS:
                threshold = state['thresholds'][alpha]
                if method != 'frozen_source':
                    assert np.array_equal(score >= threshold, (1 - risk) <= alpha)
                for view, mask in [('capture_disjoint', np.ones(len(y), bool)), ('content_disjoint', clean)]:
                    met = parent.compute_binary_metrics(y[mask], y_score=score[mask], threshold=threshold)
                    per_file.append(dict(target=parent.VEHICLES[target], seed=seed, method=method,
                                         alpha=alpha, view=view, token=e['token'], family=e['family'], **met))
        y, score, risk, clean = map(np.concatenate, (ys, scores, risks, masks))
        for alpha in ALPHAS:
            for view, mask in [('capture_disjoint', np.ones(len(y), bool)), ('content_disjoint', clean)]:
                yy = y[mask]
                met = parent.compute_binary_metrics(yy, y_score=score[mask], threshold=state['thresholds'][alpha])
                aggregate.append(dict(target=parent.VEHICLES[target], seed=seed, method=method, alpha=alpha,
                                      view=view, AP_risk=average_precision_score(yy, risk[mask]) if len(np.unique(yy)) == 2 else np.nan, **met))
    pd.DataFrame(per_file).to_csv(dest / 'per_capture.csv', index=False)
    pd.DataFrame(aggregate).to_csv(dest / 'metrics.csv', index=False)
    write(dest / 'evaluated.json', dict(status='COMPLETE', methods=len(states), target_windows=len(y),
          target_content_disjoint_windows=int(clean.sum()), excluded_capture=CAL[target],
          metrics_sha256=parent.sha256_file(dest / 'metrics.csv')))


def probes(target, seed, folder, dest, states):
    if (dest / 'probed.json').exists():
        return
    selection = read(OUT / 'probe_selection.json')
    raw = {}
    for role, rows in selection.items():
        zs, scores = [], []
        # Grouped reads avoid repeatedly decompressing the same capture array.
        grouped = {}
        for i, (token, ix, _, _) in enumerate(rows):
            grouped.setdefault(token, []).append((i, ix))
        zz = np.empty((len(rows), 64)); ss = np.empty(len(rows))
        for token, pairs in grouped.items():
            positions, ix = map(np.array, zip(*pairs))
            z, _, score = take(folder, token, ix, seed)
            zz[positions], ss[positions] = z, score
        raw[role] = dict(z=zz, score=ss, vehicle=np.array([r[2] for r in rows]), y=np.array([r[3] for r in rows]))
    result, warning_rows, duplicate = [], [], {}
    for method, state in states.items():
        for scope in ('embedding', 'risk'):
            # Same unmodified embedding for three head controls: reuse identical probe fits.
            key = ('raw' if method in ('frozen_source', 'frozen_targetq', 'lr_targetq') and scope == 'embedding' else method, scope)
            if key in duplicate:
                result.extend(dict(row, method=method, reused_from=duplicate[key][0]['method']) for row in duplicate[key])
                continue
            status('PROBING', target=parent.VEHICLES[target], seed=seed, method=method, scope=scope)
            xx = {}
            for role, d in raw.items():
                parts = [transform(d['z'][d['vehicle'] == v], v, state) for v in range(4)]
                x = np.empty((len(d['y']), parts[0].shape[1]))
                for v in range(4):
                    x[d['vehicle'] == v] = parts[v]
                if scope == 'risk':
                    score = d['score'] if method.startswith('frozen') else ip.task_score(x, state['head'])
                    risk = score.copy()
                    if method != 'frozen_source':
                        for v in range(4):
                            ix = d['vehicle'] == v
                            risk[ix] = ip.calibrated_risk(score[ix], state['references'][v])
                    x = risk[:, None]
                xx[role] = x
            own = []
            for task in ('vehicle', 'attack'):
                label = 'vehicle' if task == 'vehicle' else 'y'
                train_y, test_y = raw['train'][label], raw['validation'][label]
                for kind in ('LR', 'MLP') if task == 'vehicle' else ('LR',):
                    for control in ('learned', 'permuted', 'constant') if task == 'vehicle' else ('learned',):
                        if control == 'constant':
                            score = balanced_accuracy_score(test_y, np.full_like(test_y, train_y[0]))
                            nw = 0
                        else:
                            train_label = np.random.default_rng(42).permutation(train_y) if control == 'permuted' else train_y
                            clf = LogisticRegression(C=1., max_iter=2000, random_state=42) if kind == 'LR' else MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=300, random_state=42)
                            pipe = make_pipeline(StandardScaler(), clf)
                            with warnings.catch_warnings(record=True) as caught:
                                warnings.simplefilter('always')
                                pipe.fit(xx['train'], train_label)
                            nw = len(caught)
                            warning_rows.extend(dict(method=method, scope=scope, task=task, decoder=kind,
                                                     control=control, message=str(w.message)) for w in caught)
                            score = balanced_accuracy_score(test_y, pipe.predict(xx['validation']))
                        own.append(dict(target=parent.VEHICLES[target], seed=seed, method=method, scope=scope,
                                        task=task, decoder=kind, control=control, balanced_accuracy=score,
                                        dimensions=xx['train'].shape[1], warnings=nw))
            duplicate[key] = own
            result.extend(own)
    pd.DataFrame(result).to_csv(dest / 'probes.csv', index=False)
    write(dest / 'probed.json', dict(status='COMPLETE', warnings=warning_rows,
                                    sha256=parent.sha256_file(dest / 'probes.csv')))


def summarize():
    folders = [OUT / 'fits' / v / f'seed_{s}' for v in parent.VEHICLES for s in SEEDS]
    if not all((f / 'probed.json').exists() for f in folders):
        return
    metrics = pd.concat([pd.read_csv(f / 'metrics.csv') for f in folders], ignore_index=True)
    perfile = pd.concat([pd.read_csv(f / 'per_capture.csv') for f in folders], ignore_index=True)
    probe = pd.concat([pd.read_csv(f / 'probes.csv') for f in folders], ignore_index=True)
    metrics.to_csv(OUT / 'all_metrics.csv', index=False)
    perfile.to_csv(OUT / 'per_capture.csv', index=False)
    probe.to_csv(OUT / 'all_probes.csv', index=False)
    cols = ['Recall', 'FAR_per_100k', 'Attack_F1', 'AP', 'AP_risk']
    grouped = metrics.groupby(['method', 'alpha', 'view', 'target'])[cols].mean()
    grouped.to_csv(OUT / 'per_vehicle.csv')
    grouped.groupby(['method', 'alpha', 'view'])[cols].mean().to_csv(OUT / 'summary.csv')
    probe.groupby(['method', 'scope', 'task', 'decoder', 'control'])['balanced_accuracy'].agg(['mean', 'min', 'max']).to_csv(OUT / 'probe_summary.csv')
    write(OUT / 'completed.json', dict(status='COMPLETE', fitted_encoders=12, pipelines=96,
                                      metric_rows=len(metrics), probe_rows=len(probe)))
    status('COMPLETE', pipelines=96)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--target', type=int, choices=range(4))
    parser.add_argument('--stage', choices=['all', 'prepare', 'extract', 'fit', 'probe'], default='all')
    args = parser.parse_args()
    torch.set_num_threads(4)
    freeze()
    entries, source, _ = parent.inventory(parent.load_manifest(parent.CACHE, verify=False))
    prepare(entries, source)
    if args.stage == 'prepare':
        return
    for target in range(4) if args.target is None else [args.target]:
        folder = extract(entries, source, target)
        if args.stage == 'extract':
            continue
        for seed in SEEDS:
            dest = OUT / 'fits' / parent.VEHICLES[target] / f'seed_{seed}'
            dest.mkdir(parents=True, exist_ok=True)
            states = fit_states(entries, source, target, seed, folder, dest)
            evaluate(entries, target, seed, folder, dest, states)
            if args.stage != 'fit':
                probes(target, seed, folder, dest, states)
    summarize()


if __name__ == '__main__':
    with threadpool_limits(limits=4):
        main()
