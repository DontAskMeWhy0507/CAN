"""Checks shared by experiment runners and post-hoc analyses."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from .features import SCHEMA_VERSION
from .io import CONDITIONS, VEHICLES, sha256_file


def ctt_root(root):
    root = Path(root).resolve()
    candidates = [root / 'data/can-train-and-test', root / 'can-train-and-test']
    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    raise FileNotFoundError(f'Cannot find can-train-and-test below {root}')


def ctt_specs(root, sets=None):
    base = ctt_root(root)
    specs = []
    for name in sets or VEHICLES:
        if name not in VEHICLES:
            raise ValueError(f'Unknown vehicle set: {name}')
        for role, folder in [('source', 'train_01'), *CONDITIONS.items()]:
            files = sorted((base / name / folder).glob('*.csv'))
            if not files:
                raise FileNotFoundError(f'Missing required CTT split: {base/name/folder}')
            vehicle = VEHICLES[name][int(role in {'B', 'D'})]
            specs.extend(dict(path=str(p.resolve()), kind='ctt', set=name, role=role,
                              vehicle=vehicle, label_source='CTT attack column') for p in files)
    return specs


def check_config(config):
    if config.get('protocol') != SCHEMA_VERSION:
        raise ValueError(f'Expected protocol {SCHEMA_VERSION}; do not mix older runs.')
    for field in ['sets', 'seeds', 'models']:
        values = config[field]
        if not values or len(values) != len(set(values)):
            raise ValueError(f'Empty or repeated {field}')
    if not set(config['sets']) <= set(VEHICLES):
        raise ValueError('Unknown CTT set.')
    for field in ['chunksize', 'train_windows_per_class_per_file', 'epochs', 'batch_size']:
        if not isinstance(config[field], int) or isinstance(config[field], bool) or config[field] < 1:
            raise ValueError(f'{field} must be a positive integer')
    if config['window_size'] < 2 or config['tier'] not in {'timed', 'content'}:
        raise ValueError('Invalid feature configuration.')
    if not 0 <= config['far_budget_per_100k'] <= 100000:
        raise ValueError('Invalid source FAR budget.')


def verify_preflight(directory, specs, ledger_hash):
    """Verify all required files against a successful full-file scan, by content."""
    directory = Path(directory)
    manifest = json.loads((directory / 'preflight_manifest.json').read_text(encoding='utf-8'))
    if manifest.get('status') != 'PASS' or manifest.get('schema') != SCHEMA_VERSION:
        raise ValueError('Preflight is incomplete or belongs to a different protocol.')
    if manifest['external_ledger_sha256'] != ledger_hash:
        raise ValueError('External ledger changed after preflight.')
    data_path = directory / 'data_manifest.csv'
    if sha256_file(data_path) != manifest['data_manifest_sha256']:
        raise ValueError('Preflight data manifest changed.')
    for name, digest in manifest['validator_hashes'].items():
        if sha256_file(Path(__file__).parent / name) != digest:
            raise ValueError(f'Validator changed after preflight: {name}')
    rows = pd.read_csv(data_path).to_dict('records')
    by_hash = {r['sha256']: r for r in rows if r['status'] == 'PASS'}
    verified = {}
    for spec in specs:
        p = Path(spec['path']).resolve()
        digest = sha256_file(p)
        record = by_hash.get(digest)
        if record is None or record['kind'] != spec['kind']:
            raise ValueError(f'File missing/changed since preflight: {p}')
        verified[str(p)] = digest
    return dict(manifest_sha256=sha256_file(directory/'preflight_manifest.json'),
                data_manifest_sha256=manifest['data_manifest_sha256'], files=verified)


def completed_run_for_checkpoint(folder):
    folder = Path(folder).resolve()
    run = folder.parent.parent
    manifest = json.loads((run/'run_manifest.json').read_text(encoding='utf-8'))
    if manifest.get('status') != 'COMPLETE':
        raise ValueError('Analysis requires a completed run.')
    if manifest['config'].get('purpose') == 'software_validation_only':
        raise ValueError('Synthetic software checks are not research results.')
    if manifest['schema'] != SCHEMA_VERSION:
        raise ValueError('Checkpoint protocol differs from the analysis implementation.')
    for name in ['features.py', 'models.py', 'io.py', 'experiment.py']:
        if manifest['source_hashes'].get(name) != sha256_file(Path(__file__).parent/name):
            raise ValueError(f'Checkpoint feature/model implementation changed: {name}')
    artifacts = manifest.get('artifact_hashes', {})
    if not artifacts:
        raise ValueError('Missing checkpoint/prediction integrity manifest.')
    return run, manifest


def verify_artifact(path, run, manifest):
    path = Path(path).resolve()
    key = path.relative_to(run).as_posix()
    if manifest['artifact_hashes'].get(key) != sha256_file(path):
        raise ValueError(f'Missing or changed run artifact: {key}')


def json_safe(value):
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(v) for v in value]
    if isinstance(value, (np.integer, np.bool_)):
        return value.item()
    if isinstance(value, (float, np.floating)):
        return float(value) if np.isfinite(value) else None
    return value
