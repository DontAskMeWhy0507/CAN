"""Independent count/threshold recomputation for the benign-distance supplement."""
from pathlib import Path
import sys
import json
import math
import numpy as np
import pandas as pd
import joblib
from sklearn.metrics import average_precision_score

CODE = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(CODE), str(CODE / 'src')]
from can_research.io import sha256_file, json_write

ROOT = CODE / 'results/benign_invariant_pipeline_2026-11-11'
OUT = ROOT / 'benign_distance'


def main():
    assert json.loads((OUT / 'status.json').read_text())['status'] == 'COMPLETE'
    protocol = json.loads((OUT / 'protocol.json').read_text())
    assert sha256_file(CODE / 'scripts/evaluate_benign_distance.py') == protocol['code_sha256']
    cal = json.loads((ROOT / 'calibration_selection.json').read_text())
    reserved = {c['token'] for c in cal.values()}
    checks = 0
    for v, name in enumerate(['Impala', 'Traverse', 'Silverado', 'Forester']):
        c = cal[str(v)]
        for seed in (42, 43, 44):
            folder = OUT / name / f'seed_{seed}'
            meta = json.loads((folder / 'complete.json').read_text())
            assert sha256_file(folder / 'states.joblib') == meta['states_sha256']
            states = joblib.load(folder / 'states.joblib')
            metrics = pd.read_csv(folder / 'metrics.csv')
            calibration = np.load(ROOT / 'embeddings' / name / (c['token'] + '.npz'))
            norm = calibration[f'z{seed}'][np.searchsorted(calibration['ix'], c['normalization'])].astype(float)
            threshold_z = calibration[f'z{seed}'][np.searchsorted(calibration['ix'], c['threshold'])].astype(float)
            for method, state in states.items():
                np.testing.assert_allclose(state['mean'], norm.mean(0), rtol=1e-12, atol=1e-12)
                ref = np.mean(((threshold_z - state['mean']) @ state['matrix']) ** 2, axis=1)
                np.testing.assert_allclose(state['reference'], ref, rtol=1e-12, atol=1e-12)
                collections = [[], [], [], []]
                for p in (folder / 'predictions' / method).glob('*.npz'):
                    assert p.stem not in reserved
                    d = np.load(p)
                    assert np.array_equal(d['clean'], ~np.load(ROOT / 'overlap' / (p.stem + '.npy')))
                    for collection, k in zip(collections, ['y', 'score', 'risk', 'clean']):
                        collection.append(d[k])
                y, score, risk, clean = map(np.concatenate, collections)
                for alpha in (.01, .001):
                    expected = np.nextafter(np.sort(ref)[math.ceil((len(ref) + 1) * (1 - alpha)) - 1], np.inf)
                    assert state['thresholds'][alpha] == expected
                    assert np.array_equal(score >= expected, 1 - risk <= alpha)
                    for view, mask in [('capture_disjoint', np.ones(len(y), bool)), ('content_disjoint', clean)]:
                        yy, ss, rr = y[mask], score[mask], risk[mask]
                        pred = ss >= expected
                        tp, fp = ((yy == 1) & pred).sum(), ((yy == 0) & pred).sum()
                        pos, neg = (yy == 1).sum(), (yy == 0).sum()
                        row = metrics[(metrics.method == method) & (metrics.alpha == alpha) & (metrics.view == view)].iloc[0]
                        values = dict(TP=tp, FP=fp, TN=neg - fp, FN=pos - tp, Recall=tp / pos,
                                      FAR_per_100k=100000 * fp / neg, Attack_F1=2 * tp / (tp + fp + pos),
                                      AP=average_precision_score(yy, ss), AP_risk=average_precision_score(yy, rr))
                        for k, value in values.items():
                            assert np.isclose(row[k], value, rtol=1e-10, atol=1e-10), (name, seed, method, k)
                        checks += 1
    result = dict(status='PASS', metric_rows=checks, pipelines=24,
                  checked=['code signature', 'state hashes', 'benign normalization mean', 'calibration scores',
                           'thresholds', 'capture/content embargo', 'risk decisions', 'confusion counts and AP'],
                  encoder_independence_claim=False)
    json_write(OUT / 'AUDIT.json', result)
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
