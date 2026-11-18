"""Single-window processing benchmark; never used as detection evidence."""
import argparse
import json
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
import torch
from can_research.features import WindowExtractor, select_features
from can_research.io import read_frames, sha256_file, json_write
from can_research.models import CANTransformer, predict_scores
from can_research.experiment import environment_manifest
from can_research.provenance import completed_run_for_checkpoint, verify_artifact, json_safe


def benchmark(folder, file, output, warmup=50, windows=1000, repeats=3, device='cpu'):
    folder, file, output = Path(folder).resolve(), Path(file).resolve(), Path(output)
    run, manifest = completed_run_for_checkpoint(folder)
    if output.exists():
        raise FileExistsError('Use a new runtime report path.')
    if warmup < 0 or windows < 1 or repeats < 1:
        raise ValueError('Invalid benchmark sizes.')
    measurements = {}
    for rep in ['raw', 'structural']:
        cp = folder/f'transformer__{rep}.pt'
        verify_artifact(cp, run, manifest)
        checkpoint = torch.load(cp, map_location='cpu', weights_only=True)
        model = CANTransformer(checkpoint['input_dim'], window_size=checkpoint['window_size']).to(device)
        model.load_state_dict(checkpoint['state_dict'])
        config = manifest['config']
        latency, span = [], []
        for _ in range(repeats):
            extractor = WindowExtractor(checkpoint['window_size'], config['tier'])
            frames = iter(read_frames(file, 'ctt', chunksize=checkpoint['window_size']))
            count = 0
            while count < warmup + windows:
                if device == 'cuda':
                    torch.cuda.synchronize()
                start = time.perf_counter()
                try:
                    chunk = next(frames)
                except StopIteration:
                    break
                raw, st, y, ix, starts, ends = extractor.feed(chunk)
                if not len(y):
                    break
                predict_scores(model, select_features(raw, st, rep, config['tier']), device, batch_size=1)
                if device == 'cuda':
                    torch.cuda.synchronize()
                elapsed = 1000 * (time.perf_counter()-start)
                if count >= warmup:
                    latency.append(elapsed)
                    span.append(1000 * (ends[0] - starts[0]))
                count += 1
            if count < warmup + windows:
                raise ValueError('Capture too short for the declared warmup and measurement budget.')
        measurements[rep] = dict(samples=len(latency), processing_ms_mean=float(np.mean(latency)),
                                  processing_ms_p50=float(np.quantile(latency, .5)),
                                  processing_ms_p95=float(np.quantile(latency, .95)),
                                  window_span_ms_p50=float(np.quantile(span, .5)),
                                  window_span_ms_p95=float(np.quantile(span, .95)),
                                  checkpoint_sha256=sha256_file(cp))
    result = environment_manifest(dict(warmup=warmup, windows=windows, repeats=repeats,
                                      batch_size=1, device=device), file.parent)
    result.update(status='COMPLETE', selected_device=device, data_sha256=sha256_file(file), data_path=str(file),
                  run_manifest_sha256=sha256_file(run/'run_manifest.json'), measurements=measurements,
                  benchmark_code_sha256=sha256_file(__file__),
                  scope='Fixed capture prefix for performance only. Includes CSV parsing, the shared extractor (which constructs BOTH representations), feature selection, host/device transfer and inference. Repeated reads may use OS cache. Acquisition span is separate. No event-level delay, queueing, ECU deadline or embedded deployment claim.')
    json_write(output, json_safe(result))
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--checkpoint-dir', required=True)
    p.add_argument('--file', required=True, help='A chronological CTT CSV; preferably fixed source validation')
    p.add_argument('--output', required=True)
    p.add_argument('--warmup', type=int, default=50)
    p.add_argument('--windows', type=int, default=1000)
    p.add_argument('--repeats', type=int, default=3)
    p.add_argument('--device', choices=['cpu', 'cuda'], default='cpu')
    a = p.parse_args()
    print(json.dumps(benchmark(a.checkpoint_dir, a.file, a.output, a.warmup, a.windows, a.repeats, a.device), indent=2))
