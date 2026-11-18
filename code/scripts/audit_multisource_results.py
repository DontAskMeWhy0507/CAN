"""Independent artifact/metric audit; never trains, selects or alters models."""
from pathlib import Path
import json
import sys
import hashlib
import numpy as np
import pandas as pd
CODE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CODE / 'src'))
from can_research.metrics import compute_binary_metrics, choose_threshold_on_validation

OUT = CODE / 'results/multisource_lovo_v2_2026-11-10'
DATA = CODE / 'results/multisource_lovo_2026-11-10/features'


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def main():
    final = json.loads((OUT / 'final_manifest.json').read_text())
    assert final['status'] == 'COMPLETE' and final['new_fits'] == 48
    for name, expected in final['artifact_hashes'].items():
        assert digest(OUT / name) == expected, name
    inventory = {e['token']: e for e in json.loads((OUT / 'data_inventory.json').read_text())}
    folds = json.loads((OUT / 'folds.json').read_text())
    names = ['Impala', 'Traverse', 'Silverado', 'Forester']
    excluded = {r['hash'] for r in json.loads((OUT / 'vehicle_identity_exclusions.json').read_text())}
    assert not excluded.intersection(e['cache_sha256'] for e in inventory.values())
    for v, split in folds.items():
        assert all(inventory[t]['vehicle'] != int(v) for role in ['train', 'validation'] for t in split[role])
        assert all(inventory[t]['vehicle'] == int(v) for t in split['test'])
        assert not set(split['test']).intersection(split['train'] + split['validation'])
    units, predictions, max_source_far = 0, 0, 0.
    for trained_path in sorted((OUT / 'fits').glob('*/*/*/trained.json')):
        folder = trained_path.parent
        trained = json.loads(trained_path.read_text())
        assert digest(folder / 'checkpoint.pt') == trained['checkpoint_sha256']
        v = names.index(trained['target_vehicle'])
        split = folds[str(v)]
        assert trained['training_capture_tokens'] == split['train']
        table = pd.read_csv(folder / 'metrics.csv')
        threshold = json.loads((folder / 'threshold.json').read_text())['threshold']
        for role in ['validation', 'test']:
            ys, ss = [], []
            for token in split[role]:
                with np.load(folder / 'predictions' / role / (token + '.npz')) as z:
                    y, score = z['y'], z['score']
                original = np.load(DATA / token / 'y.npy', mmap_mode='r')
                np.testing.assert_array_equal(y, original)
                assert len(y) == inventory[token]['windows']
                assert np.isfinite(score).all() and ((score >= 0) & (score <= 1)).all()
                actual = compute_binary_metrics(y, y_score=score, threshold=threshold)
                rows = table[(table.role == role) & (table.capture == token)]
                assert len(rows) == 1
                for metric in ['TP', 'FP', 'TN', 'FN', 'Total_Windows', 'Recall', 'AP', 'FAR_per_100k', 'Attack_F1']:
                    np.testing.assert_allclose(rows.iloc[0][metric], actual[metric], rtol=1e-10, atol=1e-10, equal_nan=True)
                ys.append(y); ss.append(score); predictions += 1
            yy, scores = np.concatenate(ys), np.concatenate(ss)
            actual = compute_binary_metrics(yy, y_score=scores, threshold=threshold)
            row = table[(table.role == role) & (table.capture == 'ALL')].iloc[0]
            for metric in ['TP', 'FP', 'TN', 'FN', 'Total_Windows', 'Recall', 'AP', 'FAR_per_100k', 'Attack_F1']:
                np.testing.assert_allclose(row[metric], actual[metric], rtol=1e-10, atol=1e-10, equal_nan=True)
            if role == 'validation':
                assert choose_threshold_on_validation(yy, scores, 100.) == threshold
                assert actual['FAR_per_100k'] <= 100. + 1e-9
                max_source_far = max(max_source_far, actual['FAR_per_100k'])
        units += 1
    assert units == 48
    df = pd.read_csv(OUT / 'all_metrics.csv')
    test = df[(df.role == 'test') & (df.capture == 'ALL')]
    assert len(test) == 48 and not test.duplicated(['target', 'seed', 'method']).any()
    for _, g in test.groupby('target'):
        assert len(g[['Total_Windows', 'Attack_Windows', 'Benign_Windows']].drop_duplicates()) == 1
    probes = pd.read_csv(OUT / 'all_probes.csv')
    assert len(probes) == 576
    assert not probes.duplicated(['target', 'seed', 'method', 'task', 'decoder', 'control']).any()
    constants = probes[probes.control == 'constant']
    np.testing.assert_allclose(constants.balanced_accuracy, constants.chance, rtol=0, atol=1e-12)
    report = dict(status='PASS', completed_fits=units, checked_prediction_files=predictions,
                  metrics_recomputed_from_saved_scores=True, source_thresholds_recomputed=True,
                  maximum_observed_source_far_per_100k=max_source_far,
                  identical_test_denominators=True, vehicle_embargo_verified=True,
                  conflicting_identities_excluded=True, checked_probe_cells=len(probes),
                  probe_warning_cells=int(probes.warnings.notna().sum()),
                  final_manifest_sha256=digest(OUT / 'final_manifest.json'),
                  limitations='Integrity and calculation audit only; does not establish independent driving sessions, unseen development data, or vehicle invariance.')
    (OUT / 'INDEPENDENT_AUDIT.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2), flush=True)


if __name__ == '__main__':
    main()
