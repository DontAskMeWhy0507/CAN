"""Metrics with explicit denominators; AP is never substituted with F1."""
from __future__ import annotations
import numpy as np
from sklearn.metrics import average_precision_score


def compute_binary_metrics(y_true, y_pred=None, y_score=None, threshold=0.5):
    y = np.asarray(y_true)
    if y.ndim != 1 or not np.isin(y, [0, 1]).all():
        raise ValueError('Labels must be a one-dimensional binary vector.')
    score = None if y_score is None else np.asarray(y_score, dtype=float)
    if score is not None and (score.shape != y.shape or not np.isfinite(score).all()):
        raise ValueError('Scores must be finite and aligned with labels.')
    if y_pred is None:
        if score is None:
            raise ValueError('Predictions or continuous scores are required.')
        y_pred = score >= threshold
    p = np.asarray(y_pred)
    if p.shape != y.shape or not np.isin(p, [0, 1]).all():
        raise ValueError('Predictions must be aligned binary values.')
    tp, fn = int(((y == 1) & (p == 1)).sum()), int(((y == 1) & (p == 0)).sum())
    tn, fp = int(((y == 0) & (p == 0)).sum()), int(((y == 0) & (p == 1)).sum())
    pos, neg, n = tp + fn, tn + fp, len(y)
    # F1 is meaningful for positive-only detection but cannot establish discrimination.
    # On benign-only data, omit all attack-class metrics, even if false alerts occur.
    f1 = 2 * tp / (2 * tp + fp + fn) if pos else np.nan
    precision = tp / (tp + fp) if pos and tp + fp else np.nan
    recall = tp / pos if pos else np.nan
    ap = float(average_precision_score(y, score)) if score is not None and pos and neg else np.nan
    return dict(Total_Windows=n, Attack_Windows=pos, Benign_Windows=neg,
                TP=tp, FP=fp, TN=tn, FN=fn, Attack_F1=f1, Precision=precision,
                Recall=recall, AP=ap, PR_AUC=ap,
                FAR_per_100k=100000 * fp / neg if neg else np.nan,
                Accuracy=(tp + tn) / n if n else np.nan,
                Attack_Prevalence=pos / n if n else np.nan,
                Metric_Status='empty' if not n else 'two_class' if pos and neg else 'single_class',
                AP_Status='ok' if score is not None and pos and neg else 'requires_scores_and_both_classes')


def choose_threshold_on_validation(y, scores, far_budget=100.0):
    """Maximize source-validation recall within an empirical FAR budget.

    Ties prefer fewer false alerts, then a higher threshold. This does not
    guarantee the same FAR on target data. The validation set is not rebalanced.
    """
    y, scores = np.asarray(y), np.asarray(scores, float)
    if set(np.unique(y)) != {0, 1} or y.shape != scores.shape or not np.isfinite(scores).all():
        raise ValueError('Calibration requires aligned finite scores and both source classes.')
    if not 0 <= far_budget <= 100000:
        raise ValueError('Invalid FAR budget.')
    order = np.argsort(-scores, kind='stable')
    s, labels = scores[order], y[order]
    ends = np.r_[np.flatnonzero(np.diff(s) != 0), len(s) - 1]
    tps = np.cumsum(labels == 1)[ends]
    fps = np.cumsum(labels == 0)[ends]
    feasible = np.flatnonzero(fps * 100000 / (y == 0).sum() <= far_budget)
    threshold = float(np.nextafter(scores.max(), np.inf))
    if len(feasible):
        best = max(feasible, key=lambda k: (tps[k], -fps[k], s[ends[k]]))
        threshold = float(s[ends[best]])
    return threshold


def paired_capture_bootstrap(y, a, b, groups, n_boot=1000, seed=42, metric='Attack_F1'):
    """Paired whole-file resampling using sufficient confusion counts.

    Differences are b minus a. Intervals describe these captures, not new cars.
    """
    y, a, b, groups = map(np.asarray, (y, a, b, groups))
    if not (y.shape == a.shape == b.shape == groups.shape):
        raise ValueError('Bootstrap vectors must be aligned.')
    if y.ndim != 1 or any(not np.isin(v, [0, 1]).all() for v in [y, a, b]):
        raise ValueError('Bootstrap requires binary vectors.')
    if metric not in {'Attack_F1', 'Recall', 'FAR_per_100k'} or n_boot < 1:
        raise ValueError('Unsupported bootstrap metric or replicate count.')
    unique = np.unique(groups)
    counts = []
    for g in unique:
        ix = groups == g
        counts.append([[int(((y[ix] == truth) & (p[ix] == pred)).sum())
                        for truth, pred in [(1, 1), (1, 0), (0, 1), (0, 0)]] for p in [a, b]])
    counts = np.asarray(counts, dtype=np.int64)

    def difference(c):
        tp, fn, fp, tn = c.T
        if metric == 'Recall':
            denom, numer = tp + fn, tp
        elif metric == 'FAR_per_100k':
            denom, numer = fp + tn, 100000 * fp
        else:
            if (tp + fn == 0).any():
                return np.nan
            denom, numer = 2 * tp + fp + fn, 2 * tp
        if (denom == 0).any():
            return np.nan
        values = numer / denom
        return float(values[1] - values[0])

    estimate = difference(counts.sum(0)) if len(counts) else np.nan
    common = dict(metric=metric, estimate=float(estimate), groups=len(unique), requested_replicates=n_boot)
    if len(unique) < 3:
        return dict(status='insufficient_capture_groups', valid_replicates=0, **common)
    rng, deltas = np.random.default_rng(seed), []
    for _ in range(n_boot):
        delta = difference(counts[rng.integers(len(unique), size=len(unique))].sum(0))
        if np.isfinite(delta):
            deltas.append(delta)
    if not deltas:
        return dict(status='no_valid_replicates', valid_replicates=0, **common)
    low, high = np.quantile(deltas, [.025, .975])
    return dict(status='descriptive_capture_bootstrap', **common,
                valid_replicates=len(deltas), low=float(low), high=float(high))
