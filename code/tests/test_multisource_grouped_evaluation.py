"""The grouped scheduler must reproduce the frozen serial evaluator exactly."""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

CODE = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(CODE), str(CODE / 'src'), str(CODE / 'scripts')]
import evaluate_multisource_grouped as grouped


def test_grouped_matches_serial_predictions_thresholds_and_metrics(tmp_path, monkeypatch):
    r = grouped.r
    monkeypatch.setattr(r, 'CFG', dict(r.CFG, seeds=[42]))
    monkeypatch.setattr(r, 'status', lambda *args, **kwargs: None)
    monkeypatch.setattr(r, 'load_model', lambda folder, method: method)
    methods = r.CFG['methods']
    def infer(model, x, **kwargs):
        return np.clip(x[:, 0, 0] * (1 - .05 * methods.index(model)) + .01, 0, 1)
    monkeypatch.setattr(r, 'infer', infer)
    entries, source = [], {}
    for v in range(4):
        source[v] = {}
        for role in ['train', 'validation', 'extra']:
            token = f'{v}_{role}'
            e = dict(token=token, cache_sha256=token, vehicle=v, source=token,
                     windows=8, family='attack')
            entries.append(e)
            if role != 'extra':
                source[v][role] = [e]
    def array(e, name):
        if name == 'y':
            return np.array([0, 0, 1, 0, 1, 0, 1, 1])
        score = np.array([.1, .2, .15, .5, .6, .3, .8, .9]) + e['vehicle'] * .01
        return np.broadcast_to(score[:, None, None], (8, 64, 28 if name == 'raw' else 30)).copy().astype(np.float32)
    monkeypatch.setattr(r, 'load_array', array)
    reference = tmp_path / 'serial'
    monkeypatch.setattr(r, 'OUT', reference)
    for v in range(4):
        for method in methods:
            d = r.unit_folder(v, 42, method)
            d.mkdir(parents=True)
            (d / 'trained.json').write_text('{}')
    r.evaluate_all(entries, source)
    candidate = tmp_path / 'grouped'
    candidate.mkdir()
    monkeypatch.setattr(r, 'OUT', candidate)
    grouped.evaluate(entries, source)
    keys = ['target', 'seed', 'method', 'role', 'capture', 'familiarity']
    a = pd.read_csv(reference / 'all_metrics.csv').sort_values(keys).reset_index(drop=True)
    b = pd.read_csv(candidate / 'all_metrics.csv').sort_values(keys).reset_index(drop=True)
    pd.testing.assert_frame_equal(a, b, check_exact=True)
    for path in reference.glob('fits/**/predictions/**/*.npz'):
        with np.load(path) as old, np.load(candidate / path.relative_to(reference)) as new:
            np.testing.assert_array_equal(old['y'], new['y'])
            np.testing.assert_array_equal(old['score'], new['score'])
