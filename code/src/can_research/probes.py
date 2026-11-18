"""Frozen linear decoding with explicit controls and capture provenance."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import torch
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import balanced_accuracy_score, accuracy_score
from .io import source_split, VEHICLES, json_write, sha256_file
from .experiment import sample_source, environment_manifest
from .features import select_features
from .models import CANTransformer, predict_scores
from .provenance import ctt_root, completed_run_for_checkpoint, verify_artifact


def balanced_cells(y, vehicle, seed):
    rng = np.random.default_rng(seed)
    cells = [np.flatnonzero((y == c) & (vehicle == v)) for v in np.unique(vehicle) for c in [0, 1]]
    n = min(map(len, cells))
    if n == 0:
        raise ValueError('Every vehicle x attack cell must be present for a balanced probe.')
    return np.concatenate([rng.choice(ix, n, replace=False) for ix in cells])


def evaluate_controls(train_z, test_z, train_y, test_y, repeats=5):
    """No probe hyperparameter or seed is selected using held-out accuracy."""
    rows = []
    variants = [('learned', 42), ('constant', 42)]
    variants += [(kind, 42 + i) for kind in ['random_embedding', 'permuted_train_labels'] for i in range(repeats)]
    for kind, seed in variants:
        rng = np.random.default_rng(seed)
        xtr, xte, ytr = train_z, test_z, train_y
        if kind == 'constant':
            xtr, xte = np.zeros_like(train_z), np.zeros_like(test_z)
        elif kind == 'random_embedding':
            xtr, xte = rng.standard_normal(train_z.shape), rng.standard_normal(test_z.shape)
        elif kind == 'permuted_train_labels':
            ytr = rng.permutation(train_y)
        probe = make_pipeline(StandardScaler(), LogisticRegression(C=1., max_iter=2000, random_state=seed))
        probe.fit(xtr, ytr)
        pred = probe.predict(xte)
        rows.append(dict(control=kind, control_seed=seed, accuracy=accuracy_score(test_y, pred),
                         balanced_accuracy=balanced_accuracy_score(test_y, pred),
                         chance=1/len(np.unique(test_y)), n_train=len(train_y), n_test=len(test_y)))
    return rows


def run_probe(root, checkpoint_dir, output):
    root, folder, out = Path(root).resolve(), Path(checkpoint_dir).resolve(), Path(output)
    run, manifest = completed_run_for_checkpoint(folder)
    if out.exists() and any(out.iterdir()):
        raise FileExistsError('Use a fresh probe output directory.')
    metas = {}
    for rep in ['raw', 'structural']:
        for suffix in ['json', 'pt']:
            verify_artifact(folder/f'transformer__{rep}.{suffix}', run, manifest)
        metas[rep] = json.loads((folder/f'transformer__{rep}.json').read_text(encoding='utf-8'))
    for field in ['tier', 'window_size', 'seed']:
        if metas['raw'][field] != metas['structural'][field]:
            raise ValueError(f'Unmatched checkpoint metadata: {field}')
    cfg = dict(window_size=metas['raw']['window_size'], tier=metas['raw']['tier'], sampling_seed=20261103,
               chunksize=8192, train_windows_per_class_per_file=200, controls_repeats=5)
    out.mkdir(parents=True, exist_ok=True)
    protocol = environment_manifest(cfg, root)
    protocol.update(checkpoint_dir=str(folder), run_manifest_sha256=sha256_file(run/'run_manifest.json'),
                    checkpoint_hashes={r: sha256_file(folder/f'transformer__{r}.pt') for r in metas},
                    vehicle_classes={str(i): VEHICLES[s][0] for i, s in enumerate(VEHICLES)},
                    limitation='Post-hoc linear decodability only. The encoder has seen source training captures. Probe test holds out recording-round groups; independent driving sessions are not established. Controls are adaptations, not an exact Hewitt-Liang replication.')
    json_write(out/'protocol.json', protocol)
    try:
        pools = {'train': [], 'test': []}
        identifiers = {'train': [], 'test': []}
        coverage, data_manifest = [], []
        hashes = {}
        for vehicle, set_name in enumerate(VEHICLES):
            files = sorted((ctt_root(root)/set_name/'train_01').glob('*.csv'))
            tr, te = source_split(files)
            for role, paths in [('train', tr), ('test', te)]:
                for p in paths:
                    digest = sha256_file(p)
                    if digest in hashes:
                        raise ValueError(f'Duplicate probe capture bytes: {p} and {hashes[digest]}')
                    hashes[digest] = str(p)
                    data_manifest.append(dict(path=str(p), sha256=digest, role=role, vehicle=vehicle))
                raw, st, y, report, selected = sample_source(paths, cfg)
                pools[role].append((raw, st, y, np.full(len(y), vehicle)))
                identifiers[role].extend(dict(s, probe_role=role, vehicle=vehicle) for s in selected)
                coverage.extend(dict(r, probe_role=role, vehicle=vehicle) for r in report)
        data = {role: tuple(np.concatenate([p[j] for p in parts]) for j in range(4)) for role, parts in pools.items()}
        chosen = {role: balanced_cells(v[2], v[3], 42) for role, v in data.items()}
        selected_rows = [identifiers[role][i] for role, ix in chosen.items() for i in ix]
        pd.DataFrame(selected_rows).to_csv(out/'probe_windows.csv.gz', index=False)
        pd.DataFrame(data_manifest).to_csv(out/'data_manifest.csv', index=False)
        pd.DataFrame(coverage).to_csv(out/'probe_coverage.csv', index=False)
        rows = []
        for rep in ['raw', 'structural']:
            checkpoint = torch.load(folder/f'transformer__{rep}.pt', map_location='cpu', weights_only=True)
            model = CANTransformer(checkpoint['input_dim'], window_size=checkpoint['window_size'])
            model.load_state_dict(checkpoint['state_dict'])
            embedding = {}
            for role, (raw, st, y, vehicle) in data.items():
                ix = chosen[role]
                _, z = predict_scores(model, select_features(raw[ix], st[ix], rep, cfg['tier']), embeddings=True)
                embedding[role] = (z, y[ix], vehicle[ix])
            for target, col in [('attack', 1), ('vehicle', 2)]:
                rows.extend(dict(r, representation=rep, target=target, model_seed=metas[rep]['seed'])
                            for r in evaluate_controls(embedding['train'][0], embedding['test'][0],
                                embedding['train'][col], embedding['test'][col], cfg['controls_repeats']))
        pd.DataFrame(rows).to_csv(out/'probe_results.csv', index=False)
        protocol['artifact_hashes'] = {p.name: sha256_file(p) for p in out.iterdir() if p.is_file() and p.name != 'protocol.json'}
        protocol['status'] = 'COMPLETE'
    except Exception as e:
        protocol.update(status='FAILED', failure=repr(e))
        raise
    finally:
        json_write(out/'protocol.json', protocol)
    return pd.DataFrame(rows)
