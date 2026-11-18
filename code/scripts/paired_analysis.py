"""Paired recall, FAR and F1 for both frozen operating points."""
import sys
import json
import argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import pandas as pd
import numpy as np
from can_research.metrics import paired_capture_bootstrap
from can_research.io import json_write, sha256_file
from can_research.provenance import completed_run_for_checkpoint, verify_artifact, json_safe


def analyze(folder, condition, n_boot=1000):
    folder = Path(folder).resolve()
    run, manifest = completed_run_for_checkpoint(folder)
    metadata = {}
    for rep in ['raw', 'structural']:
        path = folder/f'transformer__{rep}.json'
        verify_artifact(path, run, manifest)
        metadata[rep] = json.loads(path.read_text(encoding='utf-8'))
    paths = sorted((folder/'predictions'/condition).glob('*.csv.gz'))
    if not paths:
        raise ValueError('No aligned predictions.')
    for path in paths:
        verify_artifact(path, run, manifest)
    df = pd.concat([pd.read_csv(f) for f in paths], ignore_index=True)
    if df.duplicated(['capture_id', 'window_index']).any():
        raise ValueError('Repeated capture/window identities.')
    scores = df[['transformer:raw', 'transformer:structural']].to_numpy()
    if not np.isfinite(scores).all():
        raise ValueError('Nonfinite prediction scores.')
    rows = []
    for op in ['default_0.5', 'source_calibrated']:
        thresholds = [.5 if op == 'default_0.5' else metadata[r]['threshold'] for r in ['raw', 'structural']]
        for metric in ['Recall', 'FAR_per_100k', 'Attack_F1']:
            rows.append(dict(operating_point=op, raw_threshold=thresholds[0], structural_threshold=thresholds[1],
                             **paired_capture_bootstrap(df.y_true, scores[:, 0] >= thresholds[0],
                                 scores[:, 1] >= thresholds[1], df.capture_id, n_boot=n_boot, metric=metric)))
    result = dict(condition=condition, direction='structural_minus_raw', results=rows,
                  run_manifest_sha256=sha256_file(run/'run_manifest.json'),
                  analysis_sha256=sha256_file(__file__),
                  metrics_code_sha256=sha256_file(Path(__file__).resolve().parents[1]/'src/can_research/metrics.py'),
                  note='File-level descriptive resampling; shared drive sessions/traffic may invalidate an independence interpretation. Initialization seeds are not new vehicles.')
    json_write(folder/f'paired_{condition}.json', json_safe(result))
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--checkpoint-dir', required=True)
    p.add_argument('--condition', choices=list('ABCD'), required=True)
    p.add_argument('--replicates', type=int, default=1000)
    args = p.parse_args()
    print(json.dumps(json_safe(analyze(args.checkpoint_dir, args.condition, args.replicates)), indent=2))
