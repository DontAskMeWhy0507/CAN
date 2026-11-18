from pathlib import Path
import sys
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from research_multisource.invariant_pipeline import (leace_fit, project, benign_normalizer,
    normalize, benign_threshold, calibrated_risk, conditional_concept, cell_weights, inlp_fit)


def test_weighted_leace_erases_cross_covariance_and_is_idempotent():
    rng = np.random.default_rng(42)
    v = np.tile(np.arange(3), 400)
    y = np.repeat([0, 1], 600)
    x = rng.normal(size=(1200, 12))
    x[:, 0] += v * 4
    x[:, 1] += y * 5
    w = cell_weights(y, v)
    z = conditional_concept(y, v, w)
    fitted = leace_fit(x, z, w)
    out = project(x, fitted)
    cross = ((out - np.average(out, axis=0, weights=w)).T * w) @ z
    assert np.linalg.norm(cross) < 1e-8
    np.testing.assert_allclose(fitted['matrix'] @ fitted['matrix'], fitted['matrix'], atol=1e-8)
    assert np.linalg.norm(out[y == 1].mean(0) - out[y == 0].mean(0)) > 3


def test_target_normalization_is_finite_with_constant_features():
    x = np.ones((1000, 64))
    for mode in ['diag', 'white']:
        state = benign_normalizer(x, mode)
        out = normalize(np.vstack([x, x[:1] * 2]), state)
        assert np.isfinite(out).all()
        assert np.max(np.abs(out)) <= 10
        np.testing.assert_array_equal(out[:-1], 0.)


def test_conservative_threshold_and_risk_decisions_agree_with_ties():
    ref = np.repeat(np.arange(100), 10).astype(float)
    score = np.array([-1, 0, 50, 98, 98.5, 99, 99.1, 100])
    for alpha in [.01, .001]:
        threshold = benign_threshold(ref, alpha)
        assert np.mean(ref >= threshold) <= alpha
        np.testing.assert_array_equal(score >= threshold, (1 - calibrated_risk(score, ref)) <= alpha)


def test_inlp_fixed_bottleneck_and_no_test_data_argument():
    rng = np.random.default_rng(43)
    v = np.tile(np.arange(3), 100)
    y = np.repeat([0, 1], 150)
    x = rng.normal(size=(300, 12)) + v[:, None]
    fitted = inlp_fit(x, y, v, dimensions=8)
    assert fitted['matrix'].shape == (12, 8)
    np.testing.assert_allclose(fitted['matrix'].T @ fitted['matrix'], np.eye(8), atol=1e-8)
