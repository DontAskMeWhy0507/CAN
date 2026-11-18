"""Isolated, source-only post-hoc study; never edits frozen thesis artifacts."""
from pathlib import Path
import argparse
import hashlib
import json
import platform
import sys
import time
CODE = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(CODE), str(CODE/'src')]
import numpy as np
import pandas as pd
import torch
from comparison.data import load_manifest, partitions, sample, training_data, batches
from comparison.analysis import paired_counts
from can_research.models import predict_scores
from can_research.metrics import compute_binary_metrics, choose_threshold_on_validation
from can_research.io import sha256_file, json_write, read_frames
from can_research.provenance import json_safe
from extensions.content import Features, content_records
from research_mixstyle.model import train, MixStyleTransformer
from thesis_final.evidence import check_metrics, equal_set, valid_manifest

CACHE = CODE/'results/comparison_data_v1'
BASE = CODE/'results/comparison_gpu4_reuse_v1'
OLD_EXTERNAL = CODE/'results/content_completion_2026-11-09/external/attempt_001'
DEFAULT_OUT = CODE/'results/mixstyle_posthoc_2026-11-09'
METHOD = 'structural_mixstyle'
CFG = json.loads((CODE/'comparison/config.json').read_text())
PROPOSAL = CODE/'notes/mixstyle_proposed_protocol_2026-11-09.json'
SEEDS = [42, 43, 44]
SETS = [f'set_0{i}' for i in range(1, 5)]


def write(path, value):
    json_write(path, json_safe(value))


def signature():
    files = [Path(__file__), PROPOSAL, CODE/'comparison/config.json', CODE/'configs/external_datasets.json']
    files += list((CODE/'research_mixstyle').glob('*.py'))
    files += [CODE/p for p in ['comparison/data.py', 'comparison/content_features.py',
              'comparison/analysis.py', 'extensions/content.py', 'src/can_research/models.py',
              'src/can_research/metrics.py', 'src/can_research/io.py',
              'src/can_research/provenance.py', 'thesis_final/evidence.py']]
    return dict(code={p.relative_to(CODE).as_posix(): sha256_file(p) for p in files},
                cache_manifest=sha256_file(CACHE/'manifest.json'),
                environment=dict(python=platform.python_version(), torch=torch.__version__,
                                 numpy=np.__version__, pandas=pd.__version__, gpu=torch.cuda.get_device_name(0)),
                protocol=json.loads(PROPOSAL.read_text(encoding='utf-8')),
                post_hoc=True, method=METHOD)


def new_attempt(parent, sig):
    parent.mkdir(parents=True, exist_ok=True)
    completed = []
    for p in sorted(parent.glob('attempt_*/manifest.json')):
        m = json.loads(p.read_text())
        if m['status'] == 'COMPLETE':
            valid_manifest(p)
            if m['signature'] != sig:
                raise ValueError('Signature changed; use a new output directory')
            completed.append(p.parent)
    if len(completed) > 1:
        raise ValueError('Duplicate completed unit')
    if completed:
        return completed[0], True
    p = parent/f'attempt_{len(list(parent.glob("attempt_*")))+1:03}'
    p.mkdir()
    write(p/'manifest.json', dict(status='RUNNING', signature=sig))
    return p, False


def finish(dest, sig, **extra):
    hashes = {p.relative_to(dest).as_posix(): sha256_file(p) for p in dest.rglob('*')
              if p.is_file() and p.name != 'manifest.json'}
    write(dest/'manifest.json', dict(status='COMPLETE', signature=sig, artifact_hashes=hashes, **extra))


def verify_inputs(out, manifest, sig):
    path = out/'verified_inputs.json'
    if path.exists():
        old = json.loads(path.read_text())
        if old['signature'] != sig:
            raise ValueError('Frozen study inputs changed; use a new output directory')
        # Recheck every previously verified path; no trust based on mtime.
        for name, digest in old['hashes'].items():
            if sha256_file(CODE/name) != digest:
                raise ValueError(f'Changed input: {name}')
        return
    hashes = {}
    for e in manifest['files']:
        for p, expected in [(CODE/e['source'], e['source_sha256']), (CACHE/e['cache'], e['cache_sha256'])]:
            if sha256_file(p) != expected:
                raise ValueError(f'Changed data: {p}')
            hashes[p.relative_to(CODE).as_posix()] = expected
    for s in SETS:
        for seed in SEEDS:
            for rep in ['raw', 'structural']:
                p = BASE/s/f'seed_{seed}'/(rep+'_transformer')/'attempt_001/manifest.json'
                m = valid_manifest(p)
                hashes[p.relative_to(CODE).as_posix()] = sha256_file(p)
                for name, digest in m['artifact_hashes'].items():
                    hashes[(p.parent/name).relative_to(CODE).as_posix()] = digest
    write(path, dict(status='PASS', signature=sig, hashes=hashes))


def calibrate_rows(dest, models, entries, condition, thresholds, set_name, selected=None):
    rows, coverage, all_y = [], [], []
    all_s = {seed: [] for seed in models}
    saved = []
    for entry in entries:
        ys, indices = [], []
        scores = {seed: [] for seed in models}
        chosen = None if selected is None else selected[entry['source']]
        for b in batches(CACHE, entry, features=True, selected=chosen):
            ys.append(b['y']); indices.append(b['ix'])
            for seed, model in models.items():
                scores[seed].append(predict_scores(model, b['structural'], 'cuda', 128))
        y, ix = np.concatenate(ys), np.concatenate(indices)
        if selected is None and not np.array_equal(ix, np.arange(entry['windows'])):
            raise ValueError('Incomplete capture coverage')
        pred = dict(y=y, window_index=ix)
        for seed in models:
            score = np.concatenate(scores[seed])
            if score.shape != y.shape or not np.isfinite(score).all():
                raise ValueError('Invalid prediction')
            pred[f'seed_{seed}'] = score
            all_s[seed].append(score)
        all_y.append(y)
        name = condition+'_'+hashlib.sha256(entry['source'].encode()).hexdigest()[:20]+'.npz'
        np.savez_compressed(dest/name, **pred)
        coverage.append(dict(condition=condition, file=entry['source'], prediction=name, windows=len(y)))
        saved.append((entry['source'], pred))
        print('SCORE', set_name, condition, Path(entry['source']).name, len(y), flush=True)
    yy = np.concatenate(all_y)
    ss = {seed: np.concatenate(v) for seed, v in all_s.items()}
    if thresholds is None:
        thresholds = {seed: choose_threshold_on_validation(yy, v, CFG['far_budget_per_100k']) for seed, v in ss.items()}
    saved.append(('ALL', dict(y=yy, **{f'seed_{k}': v for k, v in ss.items()})))
    for file, pred in saved:
        for seed in models:
            rows.append(dict(set=set_name, seed=seed, method=METHOD, condition=condition, file=file,
                             operating_point='source_calibrated', threshold=thresholds[seed],
                             **compute_binary_metrics(pred['y'], y_score=pred[f'seed_{seed}'], threshold=thresholds[seed])))
    return rows, coverage, thresholds


def run_study(out, manifest, sig, pilot=False):
    for s in (SETS[:1] if pilot else SETS):
        unit_sig = dict(sig, set=s, software_validation_only=pilot)
        dest, done = new_attempt(out/('pilot' if pilot else 'main')/s, unit_sig)
        if done:
            print('VERIFIED', dest, flush=True); continue
        try:
            split = partitions(manifest, s)
            chosen = sample(CACHE, split['train'], 8 if pilot else 1000, CFG['sampling_seed'])
            split_names = {k: [e['source'] for e in es] for k, es in split.items()}
            if not pilot:
                for seed in SEEDS:
                    for rep in ['raw', 'structural']:
                        base = BASE/s/f'seed_{seed}'/(rep+'_transformer')/'attempt_001'
                        if chosen != json.loads((base/'selected_source_windows.json').read_text()):
                            raise ValueError('Sampling differs from baseline')
                        if split_names != json.loads((base/'split.json').read_text()):
                            raise ValueError('Split differs from baseline')
            write(dest/'selected_source_windows.json', chosen)
            write(dest/'split.json', split_names)
            b = training_data(CACHE, split['train'], chosen)
            models, logs = {}, {}
            for seed in (SEEDS[:1] if pilot else SEEDS):
                print('TRAIN', s, seed, 'source windows', len(b['y']), flush=True)
                start = time.perf_counter()
                model, history = train(b['structural'], b['y'], dict(CFG, epochs=2) if pilot else CFG, seed, 'cuda')
                torch.save(model.state_dict(), dest/f'seed_{seed}.pt')
                restored = MixStyleTransformer().to('cuda').eval()
                restored.load_state_dict(torch.load(dest/f'seed_{seed}.pt', weights_only=True, map_location='cuda'))
                original = predict_scores(model, b['structural'][:16], 'cuda')
                np.testing.assert_array_equal(original, predict_scores(restored, b['structural'][:16], 'cuda'))
                models[seed] = restored
                logs[seed] = dict(seconds=time.perf_counter()-start, history=history, source_windows=len(b['y']))
            del b
            write(dest/'training.json', logs)
            val_selected = sample(CACHE, split['validation'], 8) if pilot else None
            rows, coverage, thresholds = calibrate_rows(dest, models, split['validation'], 'validation', None, s, val_selected)
            write(dest/'thresholds.json', thresholds)
            if not pilot:
                for condition in 'ABCD':
                    rs, cov, _ = calibrate_rows(dest, models, split[condition], condition, thresholds, s)
                    rows.extend(rs); coverage.extend(cov)
            d = pd.DataFrame(rows)
            check_metrics(d)
            d.to_csv(dest/'metrics.csv', index=False)
            write(dest/'coverage.json', coverage)
            finish(dest, unit_sig, software_validation_only=pilot, new_fits=len(models))
            del models
            torch.cuda.empty_cache()
        except BaseException as exc:
            write(dest/'manifest.json', dict(status='FAILED', signature=unit_sig, error=repr(exc)))
            raise


def complete_unit(out, s):
    paths = [p for p in (out/'main'/s).glob('attempt_*/manifest.json')
             if json.loads(p.read_text())['status'] == 'COMPLETE']
    if len(paths) != 1:
        raise ValueError(f'Expected one completed unit for {s}')
    valid_manifest(paths[0])
    return paths[0].parent


def external(out, sig):
    source = complete_unit(out, 'set_01')
    dest, done = new_attempt(out/'external', dict(sig, stage='external', checkpoint_manifest=sha256_file(source/'manifest.json')))
    if done:
        return
    unit_sig = json.loads((dest/'manifest.json').read_text())['signature']
    try:
        valid_manifest(OLD_EXTERNAL/'manifest.json')
        prior = json.loads((OLD_EXTERNAL/'coverage.json').read_text())
        prior_complete = {str(Path(r['file']).resolve()): r for r in prior if r['status'] == 'COMPLETE'}
        models = {}
        for seed in SEEDS:
            model = MixStyleTransformer().to('cuda').eval()
            model.load_state_dict(torch.load(source/f'seed_{seed}.pt', map_location='cuda', weights_only=True))
            models[seed] = model
        thresholds = {int(k): v for k, v in json.loads((source/'thresholds.json').read_text()).items()}
        rows, coverage = [], []
        ledger = json.loads((CODE/'configs/external_datasets.json').read_text())
        for dataset in ledger['datasets']:
            if not dataset['enabled']:
                coverage.append(dict(dataset=dataset['name'], status='EXCLUDED', reason=dataset['reason'])); continue
            paths = sorted(CODE.glob(dataset['glob']))
            if not paths:
                raise ValueError('Missing enabled external dataset')
            for path in paths:
                if path.name in dataset.get('excluded_files', {}):
                    coverage.append(dict(dataset=dataset['name'], file=str(path), status='QUARANTINED', reason=dataset['excluded_files'][path.name])); continue
                old = prior_complete[str(path.resolve())]
                digest = sha256_file(path)
                if digest != old['sha256']:
                    raise ValueError('External input changed')
                features, pending, ys = Features(), None, []
                scores = {seed: [] for seed in SEEDS}
                frames = 0
                for chunk in read_frames(path, dataset['kind'], 65536, dataset.get('label_policy')):
                    r = content_records(chunk); frames += len(r)
                    r = np.concatenate([pending, r]) if pending is not None else r
                    n = len(r)//64*64; pending = r[n:].copy()
                    if not n: continue
                    _, st = features.feed(r[:n]); ys.append(r['label'][:n].reshape(-1, 64).max(1))
                    for seed, model in models.items():
                        scores[seed].append(predict_scores(model, st, 'cuda', 128))
                y = np.concatenate(ys)
                token = hashlib.sha256(str(path).encode()).hexdigest()[:20]+'.npz'
                with np.load(OLD_EXTERNAL/token) as z:
                    np.testing.assert_array_equal(y, z['y'])
                    np.testing.assert_array_equal(np.arange(len(y)), z['window_index'])
                if frames != old['frames'] or len(y) != old['windows'] or len(pending) != old['tail']:
                    raise ValueError('External coverage mismatch')
                pred = dict(y=y, window_index=np.arange(len(y)))
                for seed in SEEDS:
                    score = np.concatenate(scores[seed]); pred[f'seed_{seed}'] = score
                    rows.append(dict(dataset=dataset['name'], file=str(path), seed=seed, representation=METHOD,
                                     threshold=thresholds[seed], **compute_binary_metrics(y, y_score=score, threshold=thresholds[seed])))
                np.savez_compressed(dest/token, **pred)
                coverage.append(dict(old, prediction=token))
                print('EXTERNAL', dataset['name'], path.name, len(y), flush=True)
        if sum(r['status']=='COMPLETE' for r in coverage) != len(prior_complete):
            raise ValueError('Missing external captures')
        pd.DataFrame(rows).to_csv(dest/'external_metrics.csv', index=False)
        write(dest/'coverage.json', coverage)
        finish(dest, unit_sig, external_captures=len(prior_complete))
    except BaseException as exc:
        write(dest/'manifest.json', dict(status='FAILED', signature=unit_sig, error=repr(exc)))
        raise


def summarize(out):
    frames = []
    for s in SETS:
        unit = complete_unit(out, s)
        d = pd.read_csv(unit/'metrics.csv', float_precision='round_trip'); check_metrics(d)
        coverage = json.loads((unit/'coverage.json').read_text())
        split = json.loads((unit/'split.json').read_text())
        if {(r['condition'], r['file']) for r in coverage} != {(c, f) for c, fs in split.items() if c != 'train' for f in fs}:
            raise ValueError('Coverage differs from split')
        if len(coverage) != len({(r['condition'], r['file']) for r in coverage}):
            raise ValueError('Duplicate coverage')
        for r in coverage:
            with np.load(unit/r['prediction']) as z:
                np.testing.assert_array_equal(z['window_index'], np.arange(r['windows']))
                if set(z.files) != {'y', 'window_index', *[f'seed_{seed}' for seed in SEEDS]}:
                    raise ValueError('Wrong prediction keys')
                for seed in SEEDS:
                    row = d[(d.seed==seed)&(d.condition==r['condition'])&(d.file==r['file'])]
                    if len(row) != 1: raise ValueError('Missing/duplicate metric row')
                    row = row.iloc[0]
                    computed = compute_binary_metrics(z['y'], y_score=z[f'seed_{seed}'], threshold=row.threshold)
                    for k in ['TP','FP','TN','FN','Recall','FAR_per_100k','AP','Attack_F1']:
                        if not np.isclose(computed[k], row[k], rtol=1e-10, atol=1e-10, equal_nan=True):
                            raise ValueError(f'Prediction/metric mismatch: {k}')
        frames.append(d)
        for seed in SEEDS:
            for rep in ['raw', 'structural']:
                base = BASE/s/f'seed_{seed}'/(rep+'_transformer')/'attempt_001'
                # Baseline artifacts also contain the historical default_0.5
                # rows.  This study compares source-calibrated operating
                # points only, matching the MixStyle rows and avoiding
                # duplicate capture indices in the paired analysis.
                baseline = pd.read_csv(base/'metrics.csv')
                baseline = baseline[baseline.operating_point.eq('source_calibrated')].copy()
                if baseline.empty or baseline[['set', 'seed', 'method', 'condition', 'file']].duplicated().any():
                    raise ValueError(f'Invalid source-calibrated baseline matrix: {base}')
                frames.append(baseline)
    d = pd.concat(frames, ignore_index=True); check_metrics(d)
    dest = out/'analysis'; dest.mkdir(exist_ok=True)
    d.to_csv(dest/'metrics_verified.csv', index=False)
    per, mean = equal_set(d)
    per.to_csv(dest/'by_set.csv'); mean.to_csv(dest/'equal_set.csv')
    # The frozen baseline artifacts also retain a default_0.5 operating point.
    # The primary protocol compares source-calibrated thresholds only; keep the
    # default operating point in metrics_verified.csv for provenance, but do
    # not let it enter the primary matrix or paired capture analysis.
    calibrated = d[d.operating_point.eq('source_calibrated')]
    pooled = calibrated[calibrated.file.eq('ALL')&calibrated.condition.isin(list('ABCD'))]
    if len(pooled) != 4*3*3*4: raise ValueError('Incomplete experimental matrix')
    pooled.groupby(['set','method','condition'])[['Recall','FAR_per_100k','AP','Attack_F1']].std().to_csv(dest/'seed_std.csv')
    intervals = []
    for (s, seed, condition), g in calibrated[calibrated.file.ne('ALL')&calibrated.condition.isin(list('ABCD'))].groupby(['set','seed','condition']):
        candidate = g[g.method==METHOD].set_index('file').sort_index()
        for opponent in ['raw_transformer','structural_transformer']:
            baseline = g[g.method==opponent].set_index('file').sort_index()
            if not candidate.index.equals(baseline.index): raise ValueError('Unpaired captures')
            for metric in ['Recall','FAR_per_100k','Attack_F1']:
                intervals.append(dict(set=s, seed=seed, condition=condition, baseline=opponent,
                    **paired_counts(baseline[['TP','FP','TN','FN']].to_numpy(), candidate[['TP','FP','TN','FN']].to_numpy(), metric)))
    write(dest/'capture_intervals.json', intervals)
    write(dest/'audit.json', dict(status='PASS', new_fits=12, reused_baselines=24, post_hoc=True,
                                 prediction_metrics_recomputed=True, source_only=True))
    print(mean.to_string(), flush=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--stage', choices=['pilot','run','external','summarize','all'], default='all')
    p.add_argument('--output', type=Path, default=DEFAULT_OUT)
    args = p.parse_args()
    if not torch.cuda.is_available(): raise RuntimeError('This run requires a CUDA GPU')
    torch.set_num_threads(4)
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=True)
    sig = signature()
    if args.stage != 'summarize':
        m = load_manifest(CACHE, verify=False)
        print('VERIFY input hashes and baseline artifacts', flush=True)
        verify_inputs(out, m, sig)
        write(out/'protocol.json', dict(signature=sig, implementation_status='IMPLEMENTED',
                                      note='Original proposal retained as design provenance; outcomes are in manifests.'))
    stages = ['pilot','run','external','summarize'] if args.stage == 'all' else [args.stage]
    for stage in stages:
        write(out/'progress.json', dict(status='RUNNING', stage=stage))
        if stage in ['pilot','run']: run_study(out, m, sig, pilot=stage=='pilot')
        elif stage == 'external': external(out, sig)
        else: summarize(out)
    write(out/'progress.json', dict(status='COMPLETE', scope=args.stage))


if __name__ == '__main__':
    main()
