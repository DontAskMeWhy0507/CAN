"""Reproducible training and streaming evaluation. Run via run_experiments.py."""
from __future__ import annotations
import argparse
import gzip
import hashlib
import importlib.metadata
import json
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
import torch
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from .features import SCHEMA_VERSION, WindowExtractor, select_features
from .io import CONDITIONS, VEHICLES, read_frames, sha256_file, source_split, capture_group, json_write
from .metrics import compute_binary_metrics, choose_threshold_on_validation
from .models import CANTransformer, train_transformer, predict_scores, set_seed
from .provenance import check_config, ctt_root, ctt_specs, verify_preflight, json_safe


def iter_windows(path, kind, config, label_policy=None, report=None):
    extractor = WindowExtractor(config['window_size'], config['tier'])
    for df in read_frames(path, kind, config['chunksize'], label_policy):
        result = extractor.feed(df)
        if len(result[2]):
            yield result
    summary = extractor.finish()
    if report is not None:
        report.update(summary)


def sample_source(files, config):
    """Uniform random-priority reservoirs over ALL windows, per file and class.

    Samples are identical across model initialization seeds. Limits bound memory,
    not the prefix of a recording. Selection uses only source-training labels.
    """
    cap = config['train_windows_per_class_per_file']
    collected, reports, selected = [], [], []
    for path in files:
        # Separate class streams make selection independent of I/O chunking.
        # A file-local seed makes moving the workspace or adding another file
        # leave the selected windows in this capture unchanged.
        token = f"{config['sampling_seed']}:{Path(path).name}"
        file_seed = int.from_bytes(hashlib.sha256(token.encode()).digest()[:8], 'little')
        rng = {cls: np.random.default_rng(np.random.SeedSequence([file_seed, cls])) for cls in (0, 1)}
        banks = {0: None, 1: None}
        counts = np.zeros(2, dtype=np.int64)
        scan = {}
        for raw, st, y, ix, start, end in iter_windows(path, 'ctt', config, report=scan):
            for cls in (0, 1):
                mask = y == cls
                counts[cls] += mask.sum()
                if not mask.any():
                    continue
                new = (rng[cls].random(mask.sum()), raw[mask], st[mask], y[mask], ix[mask])
                old = banks[cls]
                merged = new if old is None else tuple(np.concatenate([a, b]) for a, b in zip(old, new))
                take = np.argsort(merged[0], kind='stable')[:cap]
                banks[cls] = tuple(a[take] for a in merged)
        for cls, bank in banks.items():
            reports.append(dict(file=str(path), capture_group=capture_group(path), label=cls,
                                available_windows=int(counts[cls]), sampled_windows=0 if bank is None else len(bank[0]),
                                **scan))
            if bank is not None:
                collected.append(bank[1:4])
                selected.extend(dict(file=str(path), window_index=int(i), label=cls) for i in bank[4])
        print(f'Scanned source {path.name}: benign={counts[0]}, attack={counts[1]}', flush=True)
    if not collected:
        raise ValueError('Empty source training set.')
    raw, st, y = [np.concatenate([b[i] for b in collected]) for i in range(3)]
    if set(np.unique(y)) != {0, 1}:
        raise ValueError('Training set has fewer than two classes.')
    return raw, st, y, reports, selected


def train_models(raw, st, y, config, seed, out, device):
    bundles = {}
    for name in config['models']:
        classifier, representation = name.split(':', 1)
        x = select_features(raw, st, representation, config['tier']).copy()
        print(f'Train {name}, seed={seed}, shape={x.shape}', flush=True)
        start = time.perf_counter()
        set_seed(seed)
        if classifier == 'transformer':
            model, history = train_transformer(x, y, config, seed, device)
            torch.save({'state_dict': model.state_dict(), 'input_dim': x.shape[-1],
                        'window_size': config['window_size']}, out / (name.replace(':', '__') + '.pt'))
        elif classifier == 'lr':
            model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, random_state=seed))
            model.fit(x.reshape(len(x), -1), y)
            history = []
            joblib.dump(model, out / (name.replace(':', '__') + '.joblib'))
        elif classifier == 'xgboost':
            from xgboost import XGBClassifier
            model = XGBClassifier(n_estimators=100, max_depth=6, learning_rate=.1,
                                   random_state=seed, n_jobs=config.get('cpu_threads', 4), eval_metric='logloss')
            model.fit(x.reshape(len(x), -1), y)
            history = []
            joblib.dump(model, out / (name.replace(':', '__') + '.joblib'))
        else:
            raise ValueError(f'Unknown classifier {classifier}')
        metadata = dict(name=name, seed=seed, representation=representation,
                        tier=config['tier'], window_size=config['window_size'], input_dim=x.shape[-1],
                        train_seconds=time.perf_counter() - start, train_windows=len(y),
                        parameters=sum(p.numel() for p in model.parameters()) if classifier == 'transformer' else None,
                        history=history)
        bundles[name] = dict(model=model, representation=representation, metadata=metadata)
    return bundles


def score_files(specs, bundles, config, out, device, condition, calibrating=False):
    """One parser pass per file; all fitted models see identical windows."""
    out.mkdir(parents=True, exist_ok=True)
    all_y, all_scores = [], {name: [] for name in bundles}
    records = []
    scan_reports = []
    for spec in specs:
        path = Path(spec['path'])
        y_parts, score_parts = [], {name: [] for name in bundles}
        dest = out / (hashlib.sha256(str(path).encode()).hexdigest()[:12] + '_' + path.stem + '.csv.gz')
        with gzip.open(dest, 'wt', encoding='utf-8', newline='') as handle:
            first = True
            scan = {}
            for raw, st, y, ix, starts, ends in iter_windows(path, spec['kind'], config, spec.get('label_policy'), scan):
                frame = pd.DataFrame({'source_file': str(path), 'capture_id': str(path),
                                      'window_index': ix, 'y_true': y, 'start_time': starts, 'end_time': ends})
                y_parts.append(y)
                for name, bundle in bundles.items():
                    x = select_features(raw, st, bundle['representation'], config['tier'])
                    scores = predict_scores(bundle['model'], x, device, config['batch_size'])
                    frame[name] = scores
                    score_parts[name].append(scores)
                frame.to_csv(handle, index=False, header=first)
                first = False
        if not y_parts:
            raise ValueError(f'No complete windows: {path}')
        y = np.concatenate(y_parts)
        scan_reports.append(dict(file=str(path), **scan))
        all_y.append(y)
        for name, bundle in bundles.items():
            scores = np.concatenate(score_parts[name])
            all_scores[name].append(scores)
        print(f'Evaluated {condition}: {path.name}, windows={len(y)}', flush=True)
    y = np.concatenate(all_y)
    joined = {name: np.concatenate(parts) for name, parts in all_scores.items()}
    if calibrating:
        for name, bundle in bundles.items():
            threshold = choose_threshold_on_validation(y, joined[name], config['far_budget_per_100k'])
            bundle['threshold'] = threshold
            bundle['metadata']['threshold'] = threshold
            bundle['metadata']['validation_benign'] = int((y == 0).sum())
            bundle['metadata']['validation_attack'] = int((y == 1).sum())
            bundle['metadata']['validation_far_resolution'] = 100000 / int((y == 0).sum())
            bundle['metadata']['validation_at_selected_threshold'] = json_safe(compute_binary_metrics(
                y, y_score=joined[name], threshold=threshold))
    for name, bundle in bundles.items():
        for op, threshold in {'default_0.5': .5, 'source_calibrated': bundle['threshold']}.items():
            for spec, file_y, file_scores in zip(specs, all_y, all_scores[name]):
                records.append(dict(condition=condition, file=str(spec['path']), model=name,
                                    operating_point=op, threshold=threshold,
                                    **compute_binary_metrics(file_y, y_score=file_scores, threshold=threshold)))
            records.append(dict(condition=condition, file='ALL', model=name, operating_point=op,
                                threshold=threshold, **compute_binary_metrics(y, y_score=joined[name], threshold=threshold)))
    pd.DataFrame(scan_reports).to_csv(out/'window_coverage.csv', index=False)
    return records


def external_specs(root, ledger, tier):
    specs, excluded = [], []
    for entry in ledger['datasets']:
        if not entry['enabled'] or tier not in entry['tiers']:
            excluded.append({'dataset': entry['name'], 'reason': entry.get('reason', 'incompatible_feature_tier')})
            continue
        files = sorted(root.glob(entry['glob']))
        if not files:
            excluded.append({'dataset': entry['name'], 'reason': 'files_not_found'})
        for file in files:
            if file.name in entry.get('excluded_files', {}):
                excluded.append({'dataset': entry['name'], 'file': str(file),
                                 'reason': entry['excluded_files'][file.name]})
                continue
            specs.append(dict(path=str(file), kind=entry['kind'], label_policy=entry.get('label_policy'),
                              name=entry['name'], label_source=entry['label_source']))
    return specs, excluded


def environment_manifest(config, root):
    versions = {}
    for name in ['numpy', 'pandas', 'torch', 'scikit-learn', 'xgboost', 'scipy', 'joblib']:
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = 'not_installed'
    code_root = Path(__file__).parent
    return dict(schema=SCHEMA_VERSION, config=config, python=sys.version, platform=platform.platform(),
                versions=versions, device=torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU',
                source_hashes={p.name: sha256_file(p) for p in sorted(code_root.glob('*.py'))},
                root=str(root.resolve()), status='RUNNING',started_utc=datetime.now(timezone.utc).isoformat())


def run(config, root, output, preflight=None):
    check_config(config)
    root, output = Path(root).resolve(), Path(output).resolve()
    if output.exists() and any(output.iterdir()):
        raise FileExistsError('Use a fresh output directory; never overwrite a scientific run.')
    output.mkdir(parents=True, exist_ok=True)
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    torch.set_num_threads(config.get('cpu_threads', 4))
    metadata = environment_manifest(config, root)
    json_write(output / 'run_manifest.json', metadata)
    code_root = Path(__file__).resolve().parents[2]
    ledger = json.loads((code_root / 'configs/external_datasets.json').read_text(encoding='utf-8'))
    metadata['external_ledger_sha256'] = sha256_file(code_root / 'configs/external_datasets.json')
    json_write(output / 'external_ledger.json', ledger)
    metrics, source_manifest = [], []
    try:
        required = ctt_specs(root, config['sets'])
        if config.get('external') and 'set_01' in config['sets']:
            required += external_specs(root, ledger, config['tier'])[0]
        if config.get('purpose') != 'software_validation_only':
            audit = verify_preflight(preflight or root/'results/preflight_v2', required,
                                     metadata['external_ledger_sha256'])
            metadata['preflight'] = {k: v for k, v in audit.items() if k != 'files'}
            json_write(output/'verified_input_hashes.json', audit['files'])
        for set_name in config['sets']:
            source_root = ctt_root(root)
            source = source_root / set_name
            files = sorted((source / 'train_01').glob('*.csv'))
            train, validation = source_split(files)
            set_out = output / set_name
            set_out.mkdir()
            all_ctt = [(p, 'train') for p in train] + [(p, 'validation') for p in validation]
            all_ctt += [(p, c) for c, folder in CONDITIONS.items() for p in sorted((source / folder).glob('*.csv'))]
            hashes = {}
            for p, role in all_ctt:
                digest = sha256_file(p)
                previous = hashes.get(digest, set())
                if previous and (role in {'train', 'validation'} or previous & {'train', 'validation'}):
                    raise ValueError(f'Identical source/capture bytes across split roles: {p}, {previous}, {role}')
                hashes.setdefault(digest, set()).add(role)
                source_manifest.append(dict(set=set_name, role=role, path=str(p.relative_to(root)),
                                            bytes=p.stat().st_size, sha256=digest))
            raw, st, y, coverage, selected = sample_source(train, config)
            pd.DataFrame(coverage).to_csv(set_out / 'train_coverage.csv', index=False)
            pd.DataFrame(selected).to_csv(set_out / 'sampled_windows.csv.gz', index=False)
            json_write(set_out / 'split.json', dict(train=[str(p.relative_to(root)) for p in train],
                       validation=[str(p.relative_to(root)) for p in validation],
                       group_rule='trailing recording number; drive-session independence not established'))
            for seed in config['seeds']:
                run_out = set_out / f'seed_{seed}'
                run_out.mkdir()
                bundles = train_models(raw, st, y, config, seed, run_out, device)
                rows = score_files([dict(path=str(p), kind='ctt') for p in validation], bundles, config,
                                   run_out / 'predictions/validation', device, 'validation', True)
                for name, bundle in bundles.items():
                    json_write(run_out / (name.replace(':', '__') + '.json'), bundle['metadata'])
                for condition, folder in CONDITIONS.items():
                    tests = sorted((source / folder).glob('*.csv'))
                    if not tests:
                        raise FileNotFoundError(source / folder)
                    rows += score_files([dict(path=str(p), kind='ctt') for p in tests], bundles, config,
                                        run_out / 'predictions' / condition, device, condition)
                if config.get('external', False) and set_name == 'set_01':
                    specs, excluded = external_specs(root, ledger, config['tier'])
                    json_write(run_out / 'external_exclusions.json', excluded)
                    ext_manifest = []
                    for ix, spec in enumerate(specs):
                        p = Path(spec['path'])
                        ext_manifest.append({**spec, 'sha256': sha256_file(p), 'bytes': p.stat().st_size})
                        rows += score_files([spec], bundles, config, run_out / 'predictions' / f'external_{ix}',
                                            device, 'external:' + spec['name'] + ':' + p.name)
                    json_write(run_out / 'external_manifest.json', ext_manifest)
                for r in rows:
                    r.update(set=set_name, seed=seed, tier=config['tier'], window=config['window_size'])
                pd.DataFrame(rows).to_csv(run_out / 'metrics.csv', index=False)
                metrics.extend(rows)
                pd.DataFrame(metrics).to_csv(output / 'metrics.csv', index=False)
        pd.DataFrame(source_manifest).to_csv(output / 'data_manifest.csv', index=False)
        metadata['artifact_hashes'] = {p.relative_to(output).as_posix(): sha256_file(p)
                                      for p in sorted(output.rglob('*')) if p.is_file()
                                      and p.name != 'run_manifest.json'}
        metadata['status'] = 'COMPLETE'
    except Exception as e:
        metadata['status'], metadata['failure'] = 'FAILED', repr(e)
        pd.DataFrame(source_manifest).to_csv(output / 'data_manifest.csv', index=False)
        raise
    finally:
        metadata['finished_utc'] = datetime.now(timezone.utc).isoformat()
        json_write(output / 'run_manifest.json', metadata)
    return pd.DataFrame(metrics)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--config', default='configs/primary.json')
    p.add_argument('--root', default='.')
    p.add_argument('--output', required=True)
    p.add_argument('--preflight', help='Successful full-file preflight directory (default ROOT/results/preflight_v2)')
    p.add_argument('--sets', nargs='+')
    p.add_argument('--seeds', nargs='+', type=int)
    args = p.parse_args()
    config = json.loads(Path(args.config).read_text(encoding='utf-8'))
    config.setdefault('planned_sets', config['sets'].copy())
    config.setdefault('planned_seeds', config['seeds'].copy())
    if args.sets:
        config['sets'] = args.sets
    if args.seeds:
        config['seeds'] = args.seeds
    run(config, args.root, args.output, args.preflight)
