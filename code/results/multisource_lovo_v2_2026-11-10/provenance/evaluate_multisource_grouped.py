"""I/O-efficient evaluation of the SAME frozen LOVO fits, then original probes/analysis.

Only scheduling differs from the frozen runner: keep 12 small models resident,
read a capture once per representation, and score with the identical infer()
function and batch size. No training or hyperparameter selection occurs here.
"""
from pathlib import Path
import collections
import gc
import json
import sys
import shutil
import numpy as np
import pandas as pd
import torch
sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_multisource_lovo as r


def evaluate(entries, source):
    all_rows = []
    for v in range(4):
        split = r.split_fold(entries, source, v)
        families = {e['family'] for e in split['train'] if np.any(r.load_array(e, 'y') == 1)}
        models, rows, thresholds = {}, {}, {}
        for seed in r.CFG['seeds']:
            for method in r.CFG['methods']:
                key = (seed, method)
                dest = r.unit_folder(v, seed, method)
                if (dest / 'evaluated.json').exists():
                    meta = json.loads((dest / 'evaluated.json').read_text())
                    if r.sha256_file(dest / 'metrics.csv') != meta['metrics_sha256']:
                        raise ValueError('Changed completed metrics')
                    all_rows.extend(pd.read_csv(dest / 'metrics.csv').to_dict('records'))
                    continue
                models[key] = r.load_model(dest, method)
                rows[key] = []
        if not models:
            continue
        # Source-only exact-score equivalence check for each checkpoint and input variant.
        e = split['validation'][0]
        for key, model in models.items():
            x = r.method_x(e, key[1], np.arange(min(512, e['windows'])))
            expected = r.infer(model, x)
            actual = r.infer(model, np.array(x, copy=True))
            np.testing.assert_array_equal(actual, expected)
        for role in ('validation', 'test'):
            saved = []
            for n, e in enumerate(split[role]):
                r.status('GROUPED_EVALUATION', target=r.VEHICLES[v], role=role,
                         capture=n + 1, captures=len(split[role]), models=len(models), file=e['source'])
                y = np.array(r.load_array(e, 'y'), copy=True)
                scores = {}
                for rep, methods in [('raw', ['raw']), ('structural', ['structural', 'structural_cadv', 'relative_cadv'])]:
                    needed = [key for key in models if key[1] in methods]
                    if not needed:
                        continue
                    x = np.array(r.load_array(e, rep), copy=True)
                    for key in needed:
                        bx = x[..., [0] + list(range(9, 30))] if key[1] == 'relative_cadv' else x
                        score = r.infer(models[key], bx)
                        scores[key] = score
                        dest = r.unit_folder(v, *key) / 'predictions' / role
                        dest.mkdir(parents=True, exist_ok=True)
                        np.savez_compressed(dest / (e['token'] + '.npz'), y=y, score=score)
                        del bx
                    del x
                saved.append((e, y, scores))
            yy = np.concatenate([y for _, y, _ in saved])
            for key in models:
                seed, method = key
                dest = r.unit_folder(v, seed, method)
                ss = np.concatenate([s[key] for _, _, s in saved])
                if role == 'validation':
                    thresholds[key] = r.choose_threshold_on_validation(yy, ss, r.CFG['far_budget_per_100k'])
                    r.write(dest / 'threshold.json', dict(threshold=thresholds[key], source_only=True,
                            capture_tokens=[e['token'] for e in split[role]],
                            **r.compute_binary_metrics(yy, y_score=ss, threshold=thresholds[key])))
                tau = thresholds[key]
                common = dict(target=r.VEHICLES[v], seed=seed, method=method, role=role, threshold=tau)
                rows[key].append(dict(common, capture='ALL', family='ALL', familiarity='ALL',
                    **r.compute_binary_metrics(yy, y_score=ss, threshold=tau)))
                for e, y, scores in saved:
                    rows[key].append(dict(common, capture=e['token'], family=e['family'],
                        familiarity='known' if e['family'] in families else 'unseen' if np.any(y == 1) else 'benign',
                        **r.compute_binary_metrics(y, y_score=scores[key], threshold=tau)))
                if role == 'test':
                    for familiar in ('known', 'unseen'):
                        chosen = [(y, s[key]) for e, y, s in saved if np.any(y == 1) and ((e['family'] in families) == (familiar == 'known'))]
                        if chosen:
                            rows[key].append(dict(common, capture='FAMILY_GROUP', family='ALL', familiarity=familiar,
                                **r.compute_binary_metrics(np.concatenate([p[0] for p in chosen]),
                                    y_score=np.concatenate([p[1] for p in chosen]), threshold=tau)))
            del saved, yy
            gc.collect()
        for key in models:
            dest = r.unit_folder(v, *key)
            pd.DataFrame(rows[key]).to_csv(dest / 'metrics.csv', index=False)
            r.write(dest / 'evaluated.json', dict(status='COMPLETE', threshold=thresholds[key],
                metrics_sha256=r.sha256_file(dest / 'metrics.csv'),
                prediction_hashes={p.relative_to(dest).as_posix(): r.sha256_file(p) for p in (dest / 'predictions').rglob('*.npz')},
                execution_driver='evaluate_multisource_grouped.py', source_score_equivalence='exact'))
            all_rows.extend(rows[key])
        del models
        torch.cuda.empty_cache()
        gc.collect()
    pd.DataFrame(all_rows).to_csv(r.OUT / 'all_metrics.csv', index=False)


def main():
    torch.set_num_threads(4)
    from can_research.models import set_seed
    set_seed(42)  # Match deterministic-backend flags used by the frozen trainer.
    frozen = json.loads((r.OUT / 'frozen_protocol.json').read_text())
    if r.signature() != frozen:
        raise ValueError('Original frozen training code/config/environment changed')
    for v in range(4):
        for seed in r.CFG['seeds']:
            for method in r.CFG['methods']:
                dest = r.unit_folder(v, seed, method)
                meta = json.loads((dest / 'trained.json').read_text())
                if r.sha256_file(dest / 'checkpoint.pt') != meta['checkpoint_sha256']:
                    raise ValueError('Incomplete or changed frozen fit')
    driver = Path(__file__).resolve()
    shutil.copy2(driver, r.OUT / 'provenance' / driver.name)
    r.write(r.OUT / 'evaluation_execution.json', dict(driver_sha256=r.sha256_file(driver),
        change='Evaluation scheduling only: score all checkpoints per capture to avoid repeated disk reads.',
        unchanged=['48 frozen checkpoints', 'source/target windows', 'float32 features', 'bfloat16 inference',
                   'infer() batch size 256', 'source threshold rule', 'metrics', 'probe protocol'],
        target_model_selection=False))
    entries, source, _ = r.inventory(r.load_manifest(r.CACHE, verify=False))
    try:
        evaluate(entries, source)
        r.probe_all(entries)
        r.analyze()
    except BaseException as exc:
        r.status('FAILED', error=repr(exc))
        raise


if __name__ == '__main__':
    main()
