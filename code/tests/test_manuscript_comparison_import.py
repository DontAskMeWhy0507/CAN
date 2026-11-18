"""Scientific-report guards: no partial imports and no reversed tradeoff claims."""
from pathlib import Path
import importlib.util
import json
import sys

import pandas as pd
import pytest

CODE = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(CODE), str(CODE / 'src')]
import acceleration.merge  # resolve the real validation module before path fixtures

spec = importlib.util.spec_from_file_location('manuscript_import', CODE / 'scripts/update_comparison_manuscript.py')
report = importlib.util.module_from_spec(spec)
spec.loader.exec_module(report)


def test_incomplete_notebook_cannot_import_results(tmp_path, monkeypatch):
    (tmp_path / 'notebooks').mkdir()
    (tmp_path / 'notebooks/07_gpu_four_models_executed.execution.json').write_text(json.dumps({'status': 'RUNNING'}))
    monkeypatch.setattr(report, 'CODE', tmp_path)
    with pytest.raises(AssertionError, match='07_gpu'):
        report.validate_complete()


def test_negative_recall_and_increased_far_are_not_called_improvement(tmp_path, monkeypatch):
    merged = tmp_path / 'merged'
    merged.mkdir()
    monkeypatch.setattr(report, 'ROOT', tmp_path)
    monkeypatch.setattr(report, 'MERGED', merged)
    for lang in ('vi', 'en'):
        (tmp_path / 'thesis' / lang / 'figs').mkdir(parents=True)
    for name in ('Recall', 'FAR_per_100k', 'Attack_F1', 'AP'):
        (merged / (name + '.png')).write_bytes(b'test-only-copy-fixture')
    rows, refs, pairs = [], [], []
    for s in range(1, 5):
        for seed in (42, 43, 44):
            for method in report.METHODS:
                path = tmp_path / str(s) / str(seed) / method
                path.mkdir(parents=True)
                (path / 'training.json').write_text(json.dumps({'seconds': 1.0}))
                refs.append({'cell': [f'set_0{s}', seed, method], 'manifest': str(path / 'manifest.json')})
                for cond in 'ABCD':
                    structural = method == 'structural_transformer'
                    for file in ('ALL', 'capture.csv'):
                        rows.append(dict(set=f'set_0{s}', seed=seed, method=method, condition=cond,
                                         file=file, operating_point='source_calibrated',
                                         Total_Windows=100, Attack_Windows=10, Benign_Windows=90,
                                         Recall=.8 if structural else .9,
                                         FAR_per_100k=2000 if structural else 1000,
                                         Attack_F1=.7 if structural else .8, AP=.85))
            for cond in 'ABCD':
                for method in report.METHODS:
                    if method != 'structural_transformer':
                        pairs.append(dict(set=f'set_0{s}', condition=cond, opponent=method,
                                          Recall=-.1, FAR_per_100k=1000, Attack_F1=-.1, AP=0))
    pd.DataFrame(pairs).to_csv(merged / 'paired_by_set.csv', index=False)
    (merged / 'paired_capture_bootstrap.json').write_text('[]')
    data = pd.DataFrame(rows)
    english = report.results('en', data, refs)
    vietnamese = report.results('vi', data, refs)
    assert 'recall difference -0.1000, FAR difference 1000.00' in english
    assert 'does not support increased mean recall' in english
    assert 'recall is positive in 0/4' in english
    assert 'không ủng hộ giả thuyết tăng recall' in vietnamese
    assert 'bằng chứng cải thiện' not in vietnamese
    assert r'\label{tab:comparison-counts}' in english
    # A denominator mismatch must fail instead of silently publishing a table.
    data.loc[0, 'Benign_Windows'] = 91
    with pytest.raises(AssertionError, match='Benign_Windows'):
        report.results('en', data, refs)
