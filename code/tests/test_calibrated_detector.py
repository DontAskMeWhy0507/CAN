from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import pytest
from research_multisource.calibrated_detector import BenignCalibratedDetector
from research_multisource.invariant_pipeline import task_head


def detector():
    rng = np.random.default_rng(11)
    x = rng.normal(size=(120, 64))
    y = (x[:, 0] > 0).astype(int)
    return BenignCalibratedDetector('white_lr', task_head(x, y, np.full(len(y), 1 / len(y))))


def test_calibration_requires_disjoint_window_ids():
    d = detector()
    x = np.random.default_rng(12).normal(size=(1000, 64))
    with pytest.raises(ValueError, match='overlap'):
        d.calibrate(x, x, range(1000), range(1000))
    with pytest.raises(RuntimeError, match='Calibrate'):
        d.predict(x)


def test_deployment_roundtrip_preserves_decisions(tmp_path):
    import joblib
    rng = np.random.default_rng(13)
    a, b = rng.normal(size=(1000, 64)), rng.normal(size=(1000, 64))
    d = detector().calibrate(a, b, range(1000), range(1000, 2000))
    x = rng.normal(size=(75, 64))
    expected = d.predict(x)
    assert np.array_equal(expected['attack'], 1 - expected['risk'] <= .01)
    path = tmp_path / 'detector.joblib'
    d.save(path)
    restored = joblib.load(path).predict(x)
    assert np.array_equal(restored['attack'], expected['attack'])
    np.testing.assert_array_equal(restored['score'], expected['score'])
