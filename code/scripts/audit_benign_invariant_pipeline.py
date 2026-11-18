"""Recompute decisions/counts from saved artifacts, independently of the runner."""
from pathlib import Path
import sys
import json
import math
import hashlib
import numpy as np
import pandas as pd
import joblib

CODE = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(CODE), str(CODE / 'src')]
from can_research.io import sha256_file, json_write
from can_research.provenance import json_safe
from sklearn.metrics import average_precision_score

OUT = CODE / 'results/benign_invariant_pipeline_2026-11-11'
OLD = CODE / 'results/multisource_lovo_v2_2026-11-10'


def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def main():
    assert read(OUT / 'completed.json')['status'] == 'COMPLETE'
    protocol = read(OUT / 'frozen_protocol.json')
    for p, digest in protocol['code'].items():
        assert sha256_file(CODE / p) == digest
    assert sha256_file(OLD / 'final_manifest.json') == protocol['parent_manifest']
    cal = read(OUT / 'calibration_selection.json')
    reserved = {c['token'] for c in cal.values()}
    for c in cal.values():
        assert len(c['normalization']) == len(c['threshold']) == 1000
        assert set(c['normalization']).isdisjoint(c['threshold'])
    selection = read(OUT / 'probe_selection.json')
    assert {r[0] for r in selection['train']}.isdisjoint(r[0] for r in selection['validation'])
    for role, rows in selection.items():
        counts = np.zeros((4, 2), int)
        for token, ix, v, y in rows:
            assert token not in reserved
            assert not np.load(OUT / 'overlap' / (token + '.npy'), mmap_mode='r')[ix]
            counts[v, y] += 1
        assert np.all(counts == counts[0, 0])
    checks, max_calibration_far, fits, warning_count = 0, 0., 0, 0
    for target, name in enumerate(['Impala', 'Traverse', 'Silverado', 'Forester']):
        for seed in (42, 43, 44):
            folder = OUT / 'fits' / name / f'seed_{seed}'
            fitted = read(folder / 'fitted.json')
            assert fitted['source_vehicles'] == [v for v in range(4) if v != target]
            assert set(fitted['training_tokens']).isdisjoint(reserved)
            assert sha256_file(folder / 'states.joblib') == fitted['sha256']
            states = joblib.load(folder / 'states.joblib')
            metrics = pd.read_csv(folder / 'metrics.csv')
            filemetrics = pd.read_csv(folder / 'per_capture.csv')
            for method, state in states.items():
                fits += 1
                for alpha in (.01, .001):
                    threshold = state['thresholds'][alpha]
                    if method == 'frozen_source':
                        assert threshold == read(OLD / 'fits' / name / f'seed_{seed}' / 'structural/threshold.json')['threshold']
                    else:
                        ref = np.sort(np.asarray(state['references'][target], dtype=np.float64))
                        assert len(ref) == 1000 and np.isfinite(ref).all()
                        expected = np.nextafter(ref[math.ceil((len(ref) + 1) * (1 - alpha)) - 1], np.inf)
                        assert threshold == expected
                        far = float(np.mean(ref >= threshold))
                        assert far <= alpha
                        max_calibration_far = max(max_calibration_far, far)
                    aggregated = {view: [[], [], []] for view in ('capture_disjoint', 'content_disjoint')}
                    for p in (folder / 'predictions' / method).glob('*.npz'):
                        assert p.stem not in reserved
                        d = np.load(p)
                        assert np.isfinite(d['score']).all()
                        y, score, risk = d['y'], d['score'], d['risk']
                        if method == 'frozen_source':
                            original = np.load(OLD / 'fits' / name / f'seed_{seed}' / 'structural/predictions/test' / p.name)
                            assert np.array_equal(y, original['y'])
                            assert np.array_equal(score, original['score']), 'Frozen baseline score changed'
                        assert np.array_equal(d['clean'], ~np.load(OUT / 'overlap' / (p.stem + '.npy')))
                        if method != 'frozen_source':
                            assert np.array_equal(score >= threshold, (1 - risk) <= alpha)
                        for view, mask in [('capture_disjoint', np.ones(len(y), bool)), ('content_disjoint', d['clean'])]:
                            yy, ss = y[mask], score[mask]
                            pred = ss >= threshold
                            row = filemetrics[(filemetrics.method == method) & (filemetrics.alpha == alpha) & (filemetrics.view == view) & (filemetrics.token == p.stem)].iloc[0]
                            counts = dict(TP=((yy == 1) & pred).sum(), FP=((yy == 0) & pred).sum(),
                                          TN=((yy == 0) & ~pred).sum(), FN=((yy == 1) & ~pred).sum())
                            for k, value in counts.items():
                                assert row[k] == value, (name, seed, method, p.stem, k)
                            for collection, value in zip(aggregated[view], (yy, ss, risk[mask])):
                                collection.append(value)
                            checks += 1
                    for view, groups in aggregated.items():
                        yy, ss, rr = map(np.concatenate, groups)
                        pred = ss >= threshold
                        row = metrics[(metrics.method == method) & (metrics.alpha == alpha) & (metrics.view == view)].iloc[0]
                        tp, fp = ((yy == 1) & pred).sum(), ((yy == 0) & pred).sum()
                        pos, neg = (yy == 1).sum(), (yy == 0).sum()
                        recomputed = dict(Total_Windows=len(yy), Attack_Windows=pos, Benign_Windows=neg,
                                          Recall=tp / pos, FAR_per_100k=fp / neg * 100000,
                                          Attack_F1=2 * tp / (tp + fp + pos), AP=average_precision_score(yy, ss),
                                          AP_risk=average_precision_score(yy, rr))
                        for k, value in recomputed.items():
                            assert np.isclose(row[k], value, rtol=1e-10, atol=1e-10), (name, seed, method, k)
            warning_count += len(read(folder / 'probed.json')['warnings'])
    audit = dict(status='PASS', pipeline_fits=fits, capture_metric_checks=checks,
                 calibration_windows_per_threshold=1000, max_calibration_far=max_calibration_far,
                 probe_warning_count=warning_count,
                 checks=['frozen code signatures', 'parent manifest unchanged', 'capture embargo',
                         'normalization/threshold index separation', 'balanced record-disjoint probes',
                         'probe calibration-content exclusion', 'source-only fit metadata',
                         'threshold order statistics', 'raw-score/risk decision equivalence',
                         'frozen baseline predictions equal parent', 'content exclusion masks',
                         'confusion counts', 'aggregate recall/FAR/F1/AP/AP-risk'],
                 limitations=['This recomputation is not an external reviewer.',
                              'Recorded driving-session independence remains unverified.',
                              'Probe failure to decode would not establish statistical independence.'])
    json_write(OUT / 'AUDIT.json', json_safe(audit))
    print(json.dumps(audit), flush=True)


if __name__ == '__main__':
    main()
