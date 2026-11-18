"""Resumable study orchestration. Completed attempts are immutable."""
import argparse
import json
import subprocess
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from can_research.experiment import run, environment_manifest
from can_research.preflight import audit_workspace
from can_research.reporting import summarize
from can_research.probes import run_probe
from can_research.io import sha256_file, json_write
from can_research.provenance import verify_artifact
from paired_analysis import analyze

CODE = Path(__file__).resolve().parents[1]
NAMES = ['primary', 'ablation', 'content', 'window_32', 'window_128']


def configurations(root):
    for name in NAMES:
        cfg = json.loads((CODE/'configs'/f'{name}.json').read_text(encoding='utf-8'))
        cfg['planned_sets'], cfg['planned_seeds'] = cfg['sets'].copy(), cfg['seeds'].copy()
        for set_name in cfg['planned_sets']:
            for seed in cfg['planned_seeds']:
                yield name, set_name, seed, dict(cfg, sets=[set_name], seeds=[seed])


def completed_attempt(base, config, root):
    found = []
    for attempt in sorted(base.glob('attempt_*')):
        path = attempt/'run_manifest.json'
        if not path.exists():
            continue
        manifest = json.loads(path.read_text(encoding='utf-8'))
        if manifest['status'] != 'COMPLETE':
            continue
        current = environment_manifest(config, root)
        if any(manifest[k] != current[k] for k in ['config', 'source_hashes', 'versions']):
            raise ValueError(f'Completed attempt uses different code/config/environment; choose a new --output: {attempt}')
        if manifest['external_ledger_sha256'] != sha256_file(CODE/'configs/external_datasets.json'):
            raise ValueError('Ledger changed; choose a new study output.')
        # Check every recorded output before resuming a completed unit.
        for rel in manifest['artifact_hashes']:
            verify_artifact(attempt/rel, attempt.resolve(), manifest)
        original_root = manifest['root'].replace('\\', '/').rstrip('/') + '/'
        inputs = json.loads((attempt/'verified_input_hashes.json').read_text(encoding='utf-8'))
        for original, digest in inputs.items():
            relative = original.replace('\\', '/').removeprefix(original_root)
            if Path(relative).is_absolute() or sha256_file(root/relative) != digest:
                raise ValueError('Input data changed after completed attempt.')
        found.append(attempt)
    if len(found) > 1:
        raise ValueError(f'Multiple completed attempts for one cell: {base}')
    return found[0] if found else None


def new_attempt(base):
    base.mkdir(parents=True, exist_ok=True)
    i = 1
    while (base/f'attempt_{i:03d}').exists():
        i += 1
    return base/f'attempt_{i:03d}'


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--root', default=str(CODE), help='Code directory containing data/')
    p.add_argument('--output', default=str(CODE/'results/confirmatory_v21'))
    p.add_argument('--stage', choices=['preflight', 'primary', 'ablation', 'content', 'sensitivity', 'analysis', 'probes', 'all'], default='all')
    p.add_argument('--plan', action='store_true', help='Print the commands/fit counts without reading datasets or training')
    args = p.parse_args()
    root, output = Path(args.root).resolve(), Path(args.output).resolve()
    if args.plan:
        for name in NAMES:
            cfg = json.loads((CODE/'configs'/f'{name}.json').read_text())
            print(f"{name}: {len(cfg['sets'])} sets x {len(cfg['seeds'])} seeds x {len(cfg['models'])} models = {len(cfg['sets'])*len(cfg['seeds'])*len(cfg['models'])} fits")
        print('Order: preflight -> primary -> ablation -> content -> sensitivity -> analysis -> probes. Interrupted attempts restart; completed compatible attempts are verified and skipped.')
        return
    output.mkdir(parents=True, exist_ok=True)
    preflight = output/'preflight'
    if args.stage in {'preflight', 'all'}:
        audit_workspace(root, preflight, resume=True)
    stages = NAMES if args.stage == 'all' else (['window_32', 'window_128'] if args.stage == 'sensitivity' else [args.stage])
    completed = {n: [] for n in NAMES}
    for name, set_name, seed, config in configurations(root):
        base = output/name/f'{set_name}_seed_{seed}'
        if name not in stages and args.stage not in {'analysis', 'probes'}:
            continue
        attempt = completed_attempt(base, config, root)
        if attempt is None and name in stages:
            attempt = new_attempt(base)
            print(f'RUN {name} {set_name} seed={seed} -> {attempt}', flush=True)
            run(config, root, attempt, preflight)
        if attempt:
            completed[name].append(attempt)
            print(f'VERIFIED {name} {set_name} seed={seed}', flush=True)
        elif args.stage == 'analysis':
            raise ValueError(f'Missing study cell: {name} {set_name} {seed}')
    if args.stage in {'analysis', 'all'}:
        for name, paths in completed.items():
            subprocess.run([sys.executable, str(CODE/'scripts/summarize_results.py'), *map(str, paths),
                            '--output', str(output/'summaries'/name), '--require-complete'], check=True)
        for attempt in completed['primary']:
            folder = next(attempt.glob('set_*/seed_*'))
            for condition in 'ABCD':
                analyze(folder, condition)
    if args.stage in {'probes', 'all'}:
        if len(completed['primary']) != 12:
            raise ValueError('Complete all twelve primary cells before study-wide probes.')
        for attempt in completed['primary']:
            folder = next(attempt.glob('set_*/seed_*'))
            base = output/'probes'/f'{folder.parent.name}_{folder.name}'
            complete = []
            for dest in base.glob('attempt_*'):
                path = dest/'protocol.json'
                if path.exists():
                    m = json.loads(path.read_text(encoding='utf-8'))
                    if m['status'] == 'COMPLETE':
                        if m['run_manifest_sha256'] != sha256_file(attempt/'run_manifest.json'):
                            raise ValueError('Probe checkpoint changed.')
                        if m['source_hashes'] != environment_manifest({}, root)['source_hashes']:
                            raise ValueError('Probe analysis code changed; use a new study output.')
                        for rel, digest in m['artifact_hashes'].items():
                            if sha256_file(dest/rel) != digest:
                                raise ValueError('Probe output changed.')
                        complete.append(dest)
            if not complete:
                run_probe(root, folder, new_attempt(base))
    json_write(output/'latest_invocation.json', dict(stage=args.stage, status='COMPLETE',
               note='Invocation completed; this is not a certificate of publication readiness or a replacement for reading coverage reports.'))
    print('Finished stage:', args.stage)


if __name__ == '__main__':
    main()
