"""Second, explicitly post-hoc experiment: benign-only quadratic anomaly scores.

No claim of encoder independence: the same original 64-dimensional embedding
is retained. The hypothesis is that source attack heads restrict novel attacks.
"""
from pathlib import Path
import sys
import json
import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits
from sklearn.metrics import average_precision_score

CODE = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(CODE), str(CODE / 'src'), str(CODE / 'scripts')]
import run_benign_invariant_pipeline as r
from research_multisource import invariant_pipeline as ip


def energy(z, state):
    # Unclipped squared distance; fixed shrinkage/floor match benign normalization.
    residual = (np.asarray(z, np.float64) - state['mean']) @ state['matrix']
    return np.mean(residual * residual, axis=1)


def main():
    out = r.OUT / 'benign_distance'
    out.mkdir(exist_ok=True)
    config = dict(post_hoc=True, methods=['diag_energy', 'white_energy'],
                  hypothesis='Source-trained attack head may suppress target-specific attack deviations',
                  encoder='Same12 frozen Structural checkpoints; no encoder erasure',
                  calibration='Same1000 normalization +1000 threshold windows, whole capture excluded',
                  score='Unclipped mean squared normalized64D residual; diagonal or covariance whitening with fixed0.1 shrinkage',
                  labels_used='Confirmed-benign calibration only; no target attack labels used in score or threshold fitting',
                  thresholds=[.01, .001], claim='Benign-calibrated anomaly detection, NOT vehicle-independent representation',
                  parent_protocol=r.parent.sha256_file(r.OUT / 'frozen_protocol.json'),
                  code_sha256=r.parent.sha256_file(Path(__file__)))
    if (out / 'protocol.json').exists():
        assert r.read(out / 'protocol.json') == config
    else:
        r.write(out / 'protocol.json', config)
    entries = r.read(r.parent.OUT / 'data_inventory.json')
    cal = r.read(r.OUT / 'calibration_selection.json')
    all_rows, all_files = [], []
    for target, name in enumerate(r.parent.VEHICLES):
        folder = r.OUT / 'embeddings' / name
        c = cal[str(target)]
        for seed in r.SEEDS:
            dest = out / name / f'seed_{seed}'
            dest.mkdir(parents=True, exist_ok=True)
            if (dest / 'complete.json').exists():
                all_rows.extend(pd.read_csv(dest / 'metrics.csv').to_dict('records'))
                all_files.extend(pd.read_csv(dest / 'per_capture.csv').to_dict('records'))
                continue
            a, ya, _ = r.take(folder, c['token'], c['normalization'], seed)
            b, yb, _ = r.take(folder, c['token'], c['threshold'], seed)
            assert not ya.any() and not yb.any()
            metrics, per_file, states = [], [], {}
            for mode in ('diag', 'white'):
                method = mode + '_energy'
                print(f'DISTANCE {name} seed={seed} method={method}', flush=True)
                state = ip.benign_normalizer(a, mode)
                reference = energy(b, state)
                thresholds = {alpha: ip.benign_threshold(reference, alpha) for alpha in r.ALPHAS}
                state.update(reference=reference, thresholds=thresholds)
                states[method] = state
                yy, ss, rr, mm = [], [], [], []
                pdest = dest / 'predictions' / method
                pdest.mkdir(parents=True, exist_ok=True)
                for e in entries:
                    if e['vehicle'] != target or e['token'] in r.CAL:
                        continue
                    with np.load(folder / (e['token'] + '.npz')) as d:
                        assert np.array_equal(d['ix'], np.arange(e['windows']))
                        y = d['y']
                        score = energy(d[f'z{seed}'], state)
                    risk = ip.calibrated_risk(score, reference)
                    clean = ~np.load(r.OUT / 'overlap' / (e['token'] + '.npy'))
                    np.savez(pdest / (e['token'] + '.npz'), y=y, score=score, risk=risk, clean=clean)
                    yy.append(y); ss.append(score); rr.append(risk); mm.append(clean)
                    for alpha in r.ALPHAS:
                        assert np.array_equal(score >= thresholds[alpha], (1 - risk) <= alpha)
                        for view, mask in [('capture_disjoint', np.ones(len(y), bool)), ('content_disjoint', clean)]:
                            met = r.parent.compute_binary_metrics(y[mask], y_score=score[mask], threshold=thresholds[alpha])
                            per_file.append(dict(target=name, seed=seed, method=method, alpha=alpha, view=view, token=e['token'], family=e['family'], **met))
                y, score, risk, clean = map(np.concatenate, (yy, ss, rr, mm))
                for alpha in r.ALPHAS:
                    for view, mask in [('capture_disjoint', np.ones(len(y), bool)), ('content_disjoint', clean)]:
                        met = r.parent.compute_binary_metrics(y[mask], y_score=score[mask], threshold=thresholds[alpha])
                        metrics.append(dict(target=name, seed=seed, method=method, alpha=alpha, view=view,
                                            AP_risk=average_precision_score(y[mask], risk[mask]), **met))
            import joblib
            joblib.dump(states, dest / 'states.joblib')
            pd.DataFrame(metrics).to_csv(dest / 'metrics.csv', index=False)
            pd.DataFrame(per_file).to_csv(dest / 'per_capture.csv', index=False)
            r.write(dest / 'complete.json', dict(status='COMPLETE', calibration_capture=c['token'],
                    states_sha256=r.parent.sha256_file(dest / 'states.joblib')))
            all_rows.extend(metrics); all_files.extend(per_file)
    frame = pd.DataFrame(all_rows)
    frame.to_csv(out / 'all_metrics.csv', index=False)
    pd.DataFrame(all_files).to_csv(out / 'per_capture.csv', index=False)
    cols = ['Recall', 'FAR_per_100k', 'Attack_F1', 'AP', 'AP_risk']
    grouped = frame.groupby(['method', 'alpha', 'view', 'target'])[cols].mean()
    grouped.to_csv(out / 'per_vehicle.csv')
    grouped.groupby(['method', 'alpha', 'view'])[cols].mean().to_csv(out / 'summary.csv')
    r.write(out / 'status.json', dict(status='COMPLETE', pipelines=24, encoder_independence=False))
    print('COMPLETE:24 benign-distance pipelines', flush=True)


if __name__ == '__main__':
    with threadpool_limits(limits=2):
        main()
