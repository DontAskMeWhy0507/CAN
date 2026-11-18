"""Source-fitted concept erasure and explicitly benign-target-calibrated inference."""
import math
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler


def cell_weights(y, vehicle):
    w = np.zeros(len(y), dtype=np.float64)
    for v in np.unique(vehicle):
        for c in (0, 1):
            ix = (vehicle == v) & (y == c)
            if not ix.any():
                raise ValueError('Missing vehicle x class source cell')
            w[ix] = 1. / ix.sum()
    return w / w.sum()


def benign_normalizer(x, mode):
    x = np.asarray(x, np.float64)
    mean = x.mean(0)
    cov = np.cov(x, rowvar=False, ddof=0)
    if mode == 'diag':
        floor = max(float(np.trace(cov) / x.shape[1]) * 1e-4, 1e-8)
        matrix = np.diag(1. / np.sqrt(np.maximum(np.diag(cov), floor)))
    elif mode == 'white':
        scale = max(float(np.trace(cov) / x.shape[1]), 1e-8)
        cov = .9 * cov + .1 * scale * np.eye(x.shape[1])
        val, vec = np.linalg.eigh(cov)
        matrix = (vec * (1 / np.sqrt(np.maximum(val, scale * 1e-8)))) @ vec.T
    else:
        raise ValueError(mode)
    return dict(mean=mean, matrix=matrix)


def normalize(x, state):
    return np.clip((np.asarray(x, np.float64) - state['mean']) @ state['matrix'], -10., 10.)


def conditional_concept(y, vehicle, w):
    domains = np.unique(vehicle)
    onehot = (vehicle[:, None] == domains[None, :]).astype(np.float64)
    concepts = []
    for c in (0, 1):
        ix = y == c
        center = np.average(onehot[ix], axis=0, weights=w[ix])
        concepts.append((onehot - center) * ix[:, None])
    return np.concatenate(concepts, axis=1)


def leace_fit(x, concept, w):
    """Weighted empirical LEACE, row-vector convention; not a nonlinear guarantee."""
    x = np.asarray(x, np.float64)
    w = np.asarray(w, np.float64) / np.sum(w)
    mean = np.sum(x * w[:, None], axis=0)
    xc = x - mean
    zc = concept - np.sum(concept * w[:, None], axis=0)
    cov = (xc.T * w) @ xc
    cross = (xc.T * w) @ zc
    val, vec = np.linalg.eigh(cov)
    keep = val > max(val.max() * 1e-10, 1e-12)
    sqrt = (vec[:, keep] * np.sqrt(val[keep])) @ vec[:, keep].T
    invsqrt = (vec[:, keep] * (1 / np.sqrt(val[keep]))) @ vec[:, keep].T
    u, s, _ = np.linalg.svd(invsqrt @ cross, full_matrices=False)
    rank = int(np.sum(s > max(s.max() * 1e-9, 1e-12)))
    u = u[:, :rank]
    column_projection = np.eye(x.shape[1]) - sqrt @ u @ u.T @ invsqrt
    matrix = column_projection.T
    residual = matrix.T @ cross
    if np.linalg.norm(residual) > 1e-6 * max(np.linalg.norm(cross), 1.):
        raise ValueError('LEACE empirical covariance constraint failed')
    return dict(mean=mean, matrix=matrix, removed_rank=rank,
                cross_covariance_before=float(np.linalg.norm(cross)),
                cross_covariance_after=float(np.linalg.norm(residual)))


def pca_fit(x, w, dimensions=8):
    mean = np.sum(x * w[:, None], axis=0)
    xc = x - mean
    val, vec = np.linalg.eigh((xc.T * w) @ xc)
    return dict(mean=mean, matrix=vec[:, np.argsort(val)[::-1][:dimensions]])


def inlp_fit(x, y, vehicle, seed=20261111, dimensions=8):
    """Conditional INLP adaptation: fixed residual dimension, source data only."""
    w = cell_weights(y, vehicle)
    mean = np.sum(x * w[:, None], axis=0)
    xc = x - mean
    rng = np.random.default_rng(seed)
    cells = [np.flatnonzero((y == c) & (vehicle == v)) for v in np.unique(vehicle) for c in (0, 1)]
    n = min(200, min(map(len, cells)))
    ix = np.concatenate([rng.choice(cell, n, replace=False) for cell in cells])
    projection = np.eye(x.shape[1])
    rank_remaining = x.shape[1]
    log = []
    for iteration in range(32):
        if rank_remaining <= dimensions:
            break
        rows = []
        for cls in (0, 1):
            take = ix[y[ix] == cls]
            clf = LogisticRegression(C=.1, max_iter=1000, random_state=42)
            clf.fit(xc[take] @ projection, vehicle[take])
            coef = clf.coef_ - clf.coef_.mean(0, keepdims=True)
            rows.append(coef @ projection)
        _, s, vt = np.linalg.svd(np.concatenate(rows), full_matrices=False)
        rank = min(int(np.sum(s > max(s.max() * 1e-8, 1e-10))), rank_remaining - dimensions)
        if rank == 0:
            break
        q = vt[:rank].T
        projection = projection - q @ q.T
        # Re-orthogonalize to avoid accumulating numerical artifacts.
        val, vec = np.linalg.eigh((projection + projection.T) / 2)
        rank_remaining -= rank
        basis = vec[:, np.argsort(val)[-rank_remaining:]]
        projection = basis @ basis.T
        log.append(dict(iteration=iteration + 1, remaining=rank_remaining))
    val, vec = np.linalg.eigh(projection)
    basis = vec[:, np.argsort(val)[-rank_remaining:]]
    return dict(mean=mean, matrix=basis, dimensions=rank_remaining, log=log,
                source_fit_samples=len(ix))


def project(x, state):
    return (x - state['mean']) @ state['matrix']


def task_head(x, y, w):
    scaler = StandardScaler().fit(x, sample_weight=w)
    clf = LogisticRegression(C=1., max_iter=2000, random_state=42)
    # Preserve conventional regularization strength while balancing six cells.
    clf.fit(scaler.transform(x), y, sample_weight=w * len(w))
    return dict(scaler=scaler, classifier=clf)


def task_score(x, head):
    return head['classifier'].decision_function(head['scaler'].transform(x))


def benign_threshold(scores, alpha):
    a = np.sort(np.asarray(scores, np.float64))
    if not len(a) or not np.isfinite(a).all() or not 0 < alpha < 1:
        raise ValueError('Invalid calibration score or alpha')
    k = math.ceil((len(a) + 1) * (1 - alpha))
    return np.inf if k > len(a) else float(np.nextafter(a[k - 1], np.inf))


def calibrated_risk(scores, reference):
    """One minus conservative empirical upper-tail p-value; ties count against alert."""
    ref = np.sort(np.asarray(reference, np.float64))
    lower = np.searchsorted(ref, scores, side='left')
    return lower / (len(ref) + 1.)
