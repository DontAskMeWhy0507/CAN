"""Regression tests for study validity, not expected detector performance."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from can_research.experiment import sample_source
from can_research.features import SCHEMA_VERSION, extract_windows, parse_payload
from can_research.io import CONDITIONS, VEHICLES, sha256_file, json_write
from can_research.metrics import paired_capture_bootstrap
from can_research.probes import evaluate_controls
from can_research.provenance import json_safe, verify_preflight
from can_research.preflight import audit_workspace
from can_research.reporting import summarize, paired_tables


def capture(n=256, offset=0):
    return pd.DataFrame(dict(timestamp=offset + np.arange(n)*.001,
                             arbitration_id=['001', '002']*(n//2),
                             data_field=[f'{i % 256:02X}' for i in range(n)],
                             attack=((np.arange(n)//8) % 2)))


def test_reservoir_is_identical_across_chunk_sizes_and_file_order(tmp_path):
    files = [tmp_path/f'DoS-{i}.csv' for i in [1, 2]]
    for i, p in enumerate(files):
        capture(offset=i).to_csv(p, index=False)
    cfg = dict(window_size=4, tier='timed', chunksize=7, sampling_seed=19,
               train_windows_per_class_per_file=5)
    a = sample_source(files, cfg)
    b = sample_source(files, dict(cfg, chunksize=128))
    for x, y in zip(a[:3], b[:3]):
        np.testing.assert_array_equal(x, y)
    assert a[4] == b[4]
    c = sample_source(files[::-1], cfg)
    assert sorted(a[4], key=lambda r: (r['file'], r['window_index'])) == sorted(c[4], key=lambda r: (r['file'], r['window_index']))


def test_content_rejects_infinity_and_fractional_dlc():
    df = capture(8)
    df.timestamp = np.inf
    with pytest.raises(ValueError, match='Infinite'):
        extract_windows(df, 4, tier='content')
    with pytest.raises(ValueError, match='DLC'):
        parse_payload('AA', 1.5)


def test_new_ablations_remove_only_named_components():
    df = capture(8)
    full, _ = extract_windows(df, 4)
    payload, _ = extract_windows(df, 4, representation='structural_no_payload')
    rank, _ = extract_windows(df, 4, representation='structural_no_rank_w')
    np.testing.assert_array_equal(payload, full[..., [0, *range(9, 32)]])
    np.testing.assert_array_equal(rank, full[..., [*range(30), 31]])


@pytest.mark.parametrize('metric,expected', [('Recall', .5), ('FAR_per_100k', 50000.), ('Attack_F1', 2/15)])
def test_paired_bootstrap_reports_primary_metric_and_direction(metric, expected):
    y = np.tile([0, 0, 1, 1], 3)
    raw = np.tile([0, 0, 1, 0], 3)
    st = np.tile([1, 0, 1, 1], 3)
    r = paired_capture_bootstrap(y, raw, st, np.repeat(['a', 'b', 'c'], 4), n_boot=30, metric=metric)
    assert r['estimate'] == pytest.approx(expected)
    assert r['low'] == pytest.approx(expected) and r['high'] == pytest.approx(expected)
    assert r['valid_replicates'] == 30


def test_undefined_bootstrap_is_json_null_not_a_made_up_zero():
    r = paired_capture_bootstrap([1, 1, 1], [0, 0, 0], [1, 1, 1], ['a', 'b', 'c'], metric='FAR_per_100k')
    assert r['status'] == 'no_valid_replicates'
    assert json_safe(r)['estimate'] is None


def test_probe_controls_do_not_masquerade_as_learned_embeddings():
    y = np.tile([0, 1], 50)
    z = np.column_stack([y, 1-y]).astype(float)
    rows = evaluate_controls(z, z, y, y, repeats=2)
    assert len(rows) == 6
    by_kind = {r['control']: r for r in rows}
    assert by_kind['learned']['balanced_accuracy'] == 1
    assert by_kind['constant']['balanced_accuracy'] == .5
    assert set(by_kind) == {'learned', 'constant', 'random_embedding', 'permuted_train_labels'}


def make_workspace(root):
    serial = 0
    for name in VEHICLES:
        for folder in ['train_01', *CONDITIONS.values()]:
            for suffix in ([1, 2] if folder == 'train_01' else [3]):
                p = root/'data/can-train-and-test'/name/folder/f'DoS-{suffix}.csv'
                p.parent.mkdir(parents=True, exist_ok=True)
                capture(128, serial).to_csv(p, index=False)
                serial += 1


def test_preflight_requires_all_splits_and_rejects_modified_data(tmp_path):
    make_workspace(tmp_path)
    out = tmp_path/'audit'
    report = audit_workspace(tmp_path, out)
    manifest = json.loads((out/'preflight_manifest.json').read_text())
    assert manifest['status'] == 'PASS' and len(report) == 24
    p = Path(report.iloc[0]['path'])
    specs = [dict(path=str(p), kind='ctt')]
    verify_preflight(out, specs, manifest['external_ledger_sha256'])
    d = pd.read_csv(p, dtype={'arbitration_id': str, 'data_field': str})
    d.loc[0, 'data_field'] = 'FF'
    d.to_csv(p, index=False)
    with pytest.raises(ValueError, match='missing/changed'):
        verify_preflight(out, specs, manifest['external_ledger_sha256'])
    missing = next((tmp_path/'data/can-train-and-test/set_04'/CONDITIONS['D']).glob('*.csv'))
    missing.unlink()
    with pytest.raises(FileNotFoundError, match='Missing required'):
        audit_workspace(tmp_path, tmp_path/'incomplete')
    assert json.loads((tmp_path/'incomplete/preflight_manifest.json').read_text())['status'] == 'FAIL'


def reporting_fixture(root, set_name='set_01', seeds=(42,)):
    root.mkdir()
    rows = []
    for seed in seeds:
        for condition in 'ABCD':
            for op in ['default_0.5', 'source_calibrated']:
                for model, recall in [('transformer:raw', .2), ('transformer:structural', .4)]:
                    rows.append(dict(set=set_name, seed=seed, tier='timed', window=64, model=model,
                                     condition=condition, operating_point=op, file='ALL',
                                     Recall=recall, FAR_per_100k=0., Attack_F1=recall, Precision=1., AP=.6,
                                     Attack_Windows=10, Benign_Windows=90))
    pd.DataFrame(rows).to_csv(root/'metrics.csv', index=False)
    pd.DataFrame([dict(set=set_name, role='train', path='capture.csv', sha256='fixture')]).to_csv(root/'data_manifest.csv', index=False)
    m = dict(status='COMPLETE', schema=SCHEMA_VERSION, root=str(root), versions={}, source_hashes={},
             config=dict(sets=[set_name], seeds=list(seeds), planned_sets=['set_01', 'set_02'],
                         planned_seeds=[42], models=['transformer:raw', 'transformer:structural'], window_size=64, tier='timed'),
             artifact_hashes={p.name: sha256_file(p) for p in root.iterdir()})
    json_write(root/'run_manifest.json', m)
    return root


def test_summary_discloses_coverage_and_pairs_before_averaging(tmp_path):
    a = reporting_fixture(tmp_path/'a')
    b = reporting_fixture(tmp_path/'b', 'set_02')
    out, _ = summarize([a])
    assert json.loads((out/'coverage.json').read_text())['status'] == 'PARTIAL_MATRIX'
    with pytest.raises(ValueError, match='Incomplete research matrix'):
        summarize([a], require_complete=True)
    out, _ = summarize([a, b], require_complete=True)
    paired = pd.read_csv(out/'paired_equal_set_mean.csv')
    assert np.allclose(paired.Recall_delta, .2)
    assert paired.observed_sets.eq(2).all()
    with pytest.raises(ValueError, match='Duplicate'):
        summarize([a, a])
    with (a/'metrics.csv').open('a') as f:
        f.write('\n')
    with pytest.raises(ValueError, match='changed run artifact'):
        summarize([a, b])


def test_paired_analysis_rejects_different_denominators():
    rows = [dict(set='set_01', seed=42, tier='timed', window=64, condition='B', operating_point='source_calibrated',
                 model=model, Attack_Windows=n, Benign_Windows=90, **{m: .5 for m in ['Recall', 'FAR_per_100k', 'Attack_F1', 'Precision', 'AP']})
            for model, n in [('transformer:raw', 10), ('transformer:structural', 11)]]
    with pytest.raises(ValueError, match='matching denominators'):
        paired_tables(pd.DataFrame(rows))
