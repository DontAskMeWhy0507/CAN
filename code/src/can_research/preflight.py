"""Full-file data quality manifest, without fitting any model."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from .io import read_frames, sha256_file, json_write
from .features import SCHEMA_VERSION, validate_frames, parse_id, parse_payload
from .experiment import external_specs
from .provenance import ctt_specs, json_safe


def scan_file(spec, window=64, chunksize=65536):
    path = Path(spec['path'])
    counts, windows, tail = np.zeros(2, np.int64), np.zeros(2, np.int64), np.empty(0, np.int8)
    last, negative = None, 0
    ids, first_t, last_t = set(), None, None
    rows, normalizations = 0, 0
    for df in read_frames(path, spec['kind'], chunksize, spec.get('label_policy')):
        normalizations += df.attrs.get('format_normalizations', 0)
        validate_frames(df, require_timing=spec['kind'] != 'ciciov')
        ts = np.asarray(df.timestamp, float)
        if len(ts) and np.isfinite(ts).all():
            if last is not None and ts[0] < last:
                raise ValueError('Timestamp inversion across chunks')
            first_t = float(ts[0]) if first_t is None else first_t
            last = last_t = float(ts[-1])
        # Parse every ID/payload: malformed records are not silently skipped.
        ids.update(parse_id(v) for v in df.arbitration_id)
        for row in df.itertuples(index=False):
            parse_payload(row.data_field, getattr(row, 'dlc', None))
        y = df.attack.to_numpy(np.int8)
        counts += np.bincount(y, minlength=2)
        rows += len(y)
        labels = np.r_[tail, y]
        full = len(labels) // window * window
        if full:
            windows += np.bincount(labels[:full].reshape(-1, window).max(1), minlength=2)
        tail = labels[full:]
    if not rows or not windows.sum():
        raise ValueError('File has no complete evaluation windows.')
    return dict(path=str(path.resolve()), kind=spec['kind'], bytes=path.stat().st_size, sha256=sha256_file(path),
                frames=rows, benign_frames=int(counts[0]), attack_frames=int(counts[1]),
                benign_windows=int(windows[0]), attack_windows=int(windows[1]), tail_frames=len(tail),
                unique_ids=len(ids), first_timestamp=first_t, last_timestamp=last_t,
                window_size=window, format_normalizations=normalizations,
                label_source=spec.get('label_source', 'CTT attack column'), status='PASS')


def audit_workspace(root, output, resume=False):
    root, output = Path(root).resolve(), Path(output)
    if output.exists() and any(output.iterdir()) and not resume:
        raise FileExistsError('Use a fresh preflight directory or --resume for verified completed files.')
    output.mkdir(parents=True, exist_ok=True)
    ledger_path = Path(__file__).resolve().parents[2]/'configs/external_datasets.json'
    ledger = json.loads(ledger_path.read_text(encoding='utf-8'))
    validators = {name: sha256_file(Path(__file__).parent/name)
                  for name in ['features.py', 'io.py', 'preflight.py', 'provenance.py', 'experiment.py']}
    manifest_path = output/'preflight_manifest.json'
    old_rows = {}
    if resume and manifest_path.exists():
        old = json.loads(manifest_path.read_text(encoding='utf-8'))
        if old.get('validator_hashes') == validators and old.get('external_ledger_sha256') == sha256_file(ledger_path):
            csv = output/'data_manifest.csv'
            if csv.exists():
                old_rows = {r['path']: r for r in pd.read_csv(csv).to_dict('records') if r['status'] == 'PASS'}
    manifest = dict(schema=SCHEMA_VERSION, status='RUNNING', validator_hashes=validators,
                    external_ledger_sha256=sha256_file(ledger_path),
                    scope='Full-file schema, label-policy, chronology and exact-file checks; not proof of session independence or absence of shared trace segments.')
    json_write(manifest_path, manifest)
    records = []
    try:
        specs = ctt_specs(root)
        ext, exclusions = external_specs(root, ledger, 'content')
        specs += ext
        json_write(output/'exclusions.json', exclusions)
        for spec in specs:
            try:
                previous = old_rows.get(str(Path(spec['path']).resolve()))
                if previous and previous['sha256'] == sha256_file(spec['path']):
                    record = previous
                else:
                    record = scan_file(spec)
                record.update({k: spec[k] for k in ['set', 'role', 'vehicle'] if k in spec})
            except Exception as e:
                record = dict(path=spec['path'], status='FAIL', error=repr(e))
            records.append(record)
            print(record['status'], spec['path'], flush=True)
            pd.DataFrame(records).to_csv(output/'data_manifest.csv', index=False)
        if not records or any(r['status'] == 'FAIL' for r in records):
            raise RuntimeError('Preflight found errors or no files; inspect data_manifest.csv.')
        df = pd.DataFrame(records)
        duplicates = df[df.duplicated('sha256', keep=False)]
        duplicates.to_csv(output/'identical_files.csv', index=False)
        for (_, _), group in df[df.kind.eq('ctt')].groupby(['set', 'sha256']):
            if len(group) > 1 and group.role.eq('source').any():
                raise ValueError('Identical source files or source/test bytes within a set; inspect identical_files.csv.')
        manifest.update(status='PASS', files=len(records),
                        data_manifest_sha256=sha256_file(output/'data_manifest.csv'))
    except Exception as e:
        manifest.update(status='FAIL', failure=repr(e))
        raise
    finally:
        json_write(manifest_path, json_safe(manifest))
    return pd.DataFrame(records)
