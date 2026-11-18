"""Matched post-hoc probes and batch-one timing for frozen MixStyle models."""
from pathlib import Path
import json
import sys
import time
import subprocess
CODE = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(CODE), str(CODE/'src'), str(CODE/'scripts')]
import numpy as np
import pandas as pd
import torch
from run_mixstyle_study import complete_unit, new_attempt, finish, write, DEFAULT_OUT, METHOD, SETS, SEEDS, CACHE
from research_mixstyle.model import MixStyleTransformer
from complete_content_studies import selection, pool, baseline
from comparison.data import load_manifest, partitions, records
from extensions.content import Features, select
from can_research.models import predict_scores
from can_research.probes import balanced_cells, evaluate_controls
from can_research.io import sha256_file, read_frames
from thesis_final.evidence import valid_manifest

OLD = CODE/'results/content_completion_2026-11-09/probes/attempt_001'


def load_model(s, seed, device):
    folder = complete_unit(DEFAULT_OUT, s)
    m = json.loads((folder/'manifest.json').read_text())
    for name in ['research_mixstyle/model.py', 'src/can_research/models.py', 'comparison/content_features.py']:
        if m['signature']['code'][name] != sha256_file(CODE/name):
            raise ValueError(f'Frozen training implementation changed: {name}')
    model = MixStyleTransformer().to(device).eval()
    model.load_state_dict(torch.load(folder/f'seed_{seed}.pt', weights_only=True, map_location=device))
    return model, str(folder/'manifest.json')


def runtime(dest, manifest):
    entry = partitions(manifest, 'set_01')['validation'][0]
    rows = []
    for device in ['cpu', 'cuda']:
        for rep in ['raw', 'structural', METHOD]:
            if rep == METHOD: model, ref = load_model('set_01', 42, device)
            else: model, _, ref = baseline('set_01', 42, rep, device)
            samples = []
            for repeat in range(3):
                features = Features()
                chunks = iter(read_frames(CODE/entry['source'], 'ctt', 64))
                for i in range(320):
                    if device == 'cuda': torch.cuda.synchronize()
                    start = time.perf_counter()
                    record = records(next(chunks))
                    raw, structural = features.feed(record)
                    x = structural if rep == METHOD else select(raw, structural, rep)
                    predict_scores(model, x, device, 1)
                    if device == 'cuda': torch.cuda.synchronize()
                    if i >= 20: samples.append((time.perf_counter()-start)*1000)
            rows.append(dict(device=device, representation=rep, n=len(samples),
                             p50_ms=np.quantile(samples,.5), p95_ms=np.quantile(samples,.95),
                             mean_ms=np.mean(samples), checkpoint_manifest=ref))
            print('RUNTIME', device, rep, rows[-1]['p50_ms'], flush=True)
    pd.DataFrame(rows).to_csv(dest/'runtime.csv', index=False)
    write(dest/'runtime_protocol.json', dict(source=entry['source'], batch_size=1,
        warmup_windows_per_repeat=20, measured_windows_per_repeat=300, repeats=3,
        baseline_measurements='remeasured_in_same_session',
        scope='CSV parse + validation + both content representations + inference; repeated cached reads. '
              'No acquisition wait, ECU deadline or training-speed claim. Sequential desktop measurement, not randomized timing trial.'))


def probes(dest, manifest):
    valid_manifest(OLD/'manifest.json')
    data, selected = {}, []
    for role in ['train', 'validation']:
        pools, available = [], []
        for vehicle, s in enumerate(SETS):
            es = partitions(manifest, s)[role]
            chosen = selection(es, 64, 200)
            _, st, y, _ = pool(es, 64, chosen)
            pools.append((st, y, np.full(len(y), vehicle)))
            available.extend(dict(role=role, set=s, file=e['source'], window=i)
                             for e in es for i in chosen[e['source']])
        arrays = tuple(np.concatenate([p[j] for p in pools]) for j in range(3))
        ix = balanced_cells(arrays[1], arrays[2], 42)
        data[role] = tuple(v[ix] for v in arrays)
        selected.extend(available[i] for i in ix)
        print('PROBE DATA', role, len(ix), flush=True)
    selected = pd.DataFrame(selected)
    old_selected = pd.read_csv(OLD/'selected_probe_windows.csv.gz')
    pd.testing.assert_frame_equal(selected, old_selected, check_dtype=False)
    selected.to_csv(dest/'selected_probe_windows.csv.gz', index=False)
    rows = []
    for s in SETS:
        for seed in SEEDS:
            model, ref = load_model(s, seed, 'cuda')
            embeddings = {role: predict_scores(model, arrays[0], 'cuda', 128, embeddings=True)[1]
                          for role, arrays in data.items()}
            for target, col in [('attack', 1), ('vehicle', 2)]:
                rows.extend(dict(r, encoder_set=s, model_seed=seed, representation=METHOD,
                                 target=target, checkpoint_manifest=ref)
                            for r in evaluate_controls(embeddings['train'], embeddings['validation'],
                                data['train'][col], data['validation'][col], repeats=5))
            print('PROBE', s, seed, flush=True)
    candidate = pd.DataFrame(rows)
    keys = ['encoder_set','model_seed','representation','target','control','control_seed']
    if len(candidate) != 288 or candidate.duplicated(keys).any(): raise ValueError('Incomplete probes')
    candidate.to_csv(dest/'probe_results.csv', index=False)
    allrows = pd.concat([pd.read_csv(OLD/'probe_results.csv'), candidate], ignore_index=True)
    if len(allrows) != 864 or allrows.duplicated(keys).any(): raise ValueError('Invalid paired probe matrix')
    if not np.isfinite(allrows.balanced_accuracy).all() or not allrows.balanced_accuracy.between(0,1).all():
        raise ValueError('Invalid probe score')
    allrows.to_csv(dest/'all_probe_results.csv', index=False)
    # Average control repetitions and model seeds within each encoder set first.
    per = allrows.groupby(['encoder_set','representation','target','control']).balanced_accuracy.mean()
    per.groupby(['representation','target','control']).mean().to_csv(dest/'probe_means.csv')
    write(dest/'probe_protocol.json', dict(selected_windows_match_frozen_probe=True,
        reference_manifest_sha256=sha256_file(OLD/'manifest.json'), n_train=len(data['train'][1]),
        n_validation=len(data['validation'][1]), controls_repeats=5,
        scope='Balanced post-hoc linear decodability with recording-round holdout. Encoder saw its own '
              'source training captures. Does not prove vehicle independence or independent driving sessions.'))


def main():
    if not torch.cuda.is_available(): raise ValueError('CUDA required')
    torch.set_num_threads(4)
    # Timing runs only after all IDS inference is finished.
    external_units = [p for p in (DEFAULT_OUT/'external').glob('attempt_*/manifest.json')
                      if json.loads(p.read_text())['status']=='COMPLETE']
    if len(external_units) != 1: raise ValueError('Complete external evaluation before timing')
    valid_manifest(external_units[0])
    sig = dict(stage='secondary', post_hoc=True, completion_date='2026-11-10',
               code={p.relative_to(CODE).as_posix(): sha256_file(p) for p in [Path(__file__).resolve(),
                   CODE/'research_mixstyle/model.py', CODE/'scripts/complete_content_studies.py',
                   CODE/'src/can_research/probes.py', CODE/'src/can_research/models.py',
                   CODE/'extensions/content.py', CODE/'comparison/data.py',
                   CODE/'src/can_research/io.py', CODE/'scripts/run_mixstyle_study.py']},
               checkpoints={s: sha256_file(complete_unit(DEFAULT_OUT,s)/'manifest.json') for s in SETS},
               reference_probe_manifest_sha256=sha256_file(OLD/'manifest.json'))
    dest, done = new_attempt(DEFAULT_OUT/'secondary', sig)
    if done:
        print('VERIFIED', dest); return
    try:
        gpu = subprocess.run(['nvidia-smi', '--query-gpu=name,driver_version,utilization.gpu,memory.used,memory.free',
                              '--format=csv,noheader'], capture_output=True, text=True, check=True).stdout.strip()
        write(dest/'hardware_context.json', dict(before_measurement=gpu,
              torch=torch.__version__, numpy=np.__version__, pandas=pd.__version__,
              note='Shared Windows desktop; timing is descriptive, not a controlled automotive deadline measurement.'))
        print('VERIFY CACHE; GPU:', gpu, flush=True)
        manifest = load_manifest(CACHE, verify=True)
        runtime(dest, manifest)
        probes(dest, manifest)
        finish(dest, sig)
        print('SECONDARY COMPLETE', dest, flush=True)
    except BaseException as exc:
        write(dest/'manifest.json', dict(status='FAILED', signature=sig, error=repr(exc)))
        raise


if __name__ == '__main__': main()
