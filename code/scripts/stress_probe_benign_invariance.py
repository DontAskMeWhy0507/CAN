"""Supplementary fixed 1500-iteration MLP probes; no detector/threshold selection."""
from pathlib import Path
import sys
import json
import warnings
import argparse
import numpy as np
import pandas as pd
import joblib
from threadpoolctl import threadpool_limits
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import balanced_accuracy_score

CODE = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(CODE), str(CODE / 'src'), str(CODE / 'scripts')]
import run_benign_invariant_pipeline as r


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--available', action='store_true')
    args = parser.parse_args()
    out = r.OUT / 'stress_probe'
    out.mkdir(exist_ok=True)
    protocol = dict(methods=['frozen_source', 'white_leace_lr', 'white_pca8_lr', 'white_inlp8_lr'],
                    decoder='StandardScaler + MLP(64,32), max_iter1500, random_state42; otherwise sklearn defaults',
                    scope='embedding', labels='vehicle', selection_sha256=r.parent.sha256_file(r.OUT / 'probe_selection.json'),
                    rationale='Supplementary check after some learned probes exhausted300 iterations; no detector retuning',
                    code_sha256=r.parent.sha256_file(Path(__file__)))
    frozen = out / 'protocol.json'
    if frozen.exists():
        assert r.read(frozen) == protocol
    else:
        r.write(frozen, protocol)
    selection = r.read(r.OUT / 'probe_selection.json')
    for target, name in enumerate(r.parent.VEHICLES):
        for seed in r.SEEDS:
            fit = r.OUT / 'fits' / name / f'seed_{seed}'
            if not (fit / 'probed.json').exists():
                if args.available:
                    continue
                raise RuntimeError(f'Incomplete base run: {fit}')
            dest = out / name / f'seed_{seed}'
            dest.mkdir(parents=True, exist_ok=True)
            if (dest / 'complete.json').exists():
                continue
            states = joblib.load(fit / 'states.joblib')
            folder = r.OUT / 'embeddings' / name
            raw = {}
            for role, rows in selection.items():
                grouped = {}
                for i, (token, ix, _, _) in enumerate(rows):
                    grouped.setdefault(token, []).append((i, ix))
                z = np.empty((len(rows), 64))
                for token, pairs in grouped.items():
                    positions, ix = map(np.array, zip(*pairs))
                    zz, _, _ = r.take(folder, token, ix, seed)
                    z[positions] = zz
                raw[role] = z, np.array([row[2] for row in rows])
            results = []
            for method in protocol['methods']:
                print(f'STRESS {name} seed={seed} method={method}', flush=True)
                state = states[method]
                data = {}
                for role, (z, v) in raw.items():
                    parts = [r.transform(z[v == vehicle], vehicle, state) for vehicle in range(4)]
                    x = np.empty((len(z), parts[0].shape[1]))
                    for vehicle in range(4):
                        x[v == vehicle] = parts[vehicle]
                    data[role] = x, v
                model = make_pipeline(StandardScaler(), MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=1500, random_state=42))
                with warnings.catch_warnings(record=True) as caught:
                    warnings.simplefilter('always')
                    model.fit(*data['train'])
                score = balanced_accuracy_score(data['validation'][1], model.predict(data['validation'][0]))
                joblib.dump(model, dest / (method + '.joblib'))
                results.append(dict(target=name, seed=seed, method=method, balanced_accuracy=score,
                                    n_iter=model[-1].n_iter_, training_loss=model[-1].loss_,
                                    warnings=[str(w.message) for w in caught]))
            r.write(dest / 'complete.json', results)
    files = list(out.glob('*/seed_*/complete.json'))
    rows = [row for f in files for row in r.read(f)]
    pd.DataFrame(rows).to_csv(out / 'all_results.csv', index=False)
    pd.DataFrame(rows).groupby('method').balanced_accuracy.agg(['mean', 'min', 'max']).to_csv(out / 'summary.csv')
    r.write(out / 'status.json', dict(status='COMPLETE' if len(files) == 12 else 'PARTIAL', completed_encoders=len(files), rows=len(rows)))
    print(f'Stress probe complete for {len(files)}/12 encoders', flush=True)


if __name__ == '__main__':
    with threadpool_limits(limits=2):
        main()
