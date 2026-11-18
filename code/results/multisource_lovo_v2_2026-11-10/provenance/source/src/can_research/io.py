"""Strict streamed adapters. Input bytes and labels are never silently repaired."""
from __future__ import annotations
import hashlib
import json
import re
from pathlib import Path
import numpy as np
import pandas as pd

CONDITIONS = {'A': 'test_01_known_vehicle_known_attack',
              'B': 'test_02_unknown_vehicle_known_attack',
              'C': 'test_03_known_vehicle_unknown_attack',
              'D': 'test_04_unknown_vehicle_unknown_attack'}
VEHICLES = {'set_01': ('Chevrolet Impala', 'Chevrolet Silverado'),
            'set_02': ('Chevrolet Traverse', 'Subaru Forester'),
            'set_03': ('Chevrolet Silverado', 'Subaru Forester'),
            'set_04': ('Subaru Forester', 'Chevrolet Traverse')}
LOG = re.compile(r'^\((\d+(?:\.\d+)?)\)\s+\S+\s+([0-9A-Fa-f]+)#([0-9A-Fa-f]*)(?:\s+([01]))?$')


def sha256_file(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def _labels(series, binary=True):
    a = pd.to_numeric(series, errors='raise').to_numpy(float)
    if not np.isfinite(a).all() or (a < 0).any() or (a != np.floor(a)).any():
        raise ValueError('Missing or invalid label.')
    if binary and not np.isin(a, [0, 1]).all():
        raise ValueError('Expected explicit binary labels.')
    return (a > 0).astype(np.int8)


def _dlc(v):
    s = str(v).strip().strip('[]')
    if not s.isdigit() or not 0 <= int(s) <= 8:
        raise ValueError(f'Invalid classic-CAN DLC {v!r}')
    return int(s)


def ciciov_byte(value):
    """Lossless lexical normalization of the observed CICIoV export artifact.

    Single digits followed by .0 are unambiguous in decimal and hexadecimal.
    SPEED's export format uses 0.0/2.0. Its semantic disagreement with the decimal
    companion is recorded separately and the file is quarantined in the ledger.
    Never guess the base of 10.0, truncate fractions, or delete arbitrary chars.
    """
    s = str(value).strip()
    if re.fullmatch(r'[0-9]\.0', s):
        s = s[0]
    if re.fullmatch(r'[0-9a-fA-F]{1,2}', s) is None:
        raise ValueError(f'Invalid CICIoV hex byte: {value!r}')
    return s.zfill(2)


def canonical_csv(raw, kind):
    if kind == 'ctt':
        for key in ['timestamp', 'arbitration_id', 'data_field', 'attack']:
            if key not in raw:
                raise ValueError(f'Missing CTT field {key}')
        out = raw[['timestamp', 'arbitration_id', 'data_field']].copy()
        if 'dlc' in raw or 'DLC' in raw:
            out['dlc'] = raw['dlc' if 'dlc' in raw else 'DLC'].map(_dlc)
            if 'dlc' in raw and 'DLC' in raw and not out['dlc'].equals(raw['DLC'].map(_dlc)):
                raise ValueError('Conflicting declared DLC columns.')
        out['attack'] = _labels(raw.attack)
    elif kind == 'ciciov':
        label = raw['label'].str.upper()
        if label.eq('').any():
            raise ValueError('CICIoV labels cannot be empty.')
        # Allowed labels are verified against supplied dataset schema.
        if not label.isin(['BENIGN', 'ATTACK']).all():
            raise ValueError(f'Unknown CICIoV labels: {label.unique().tolist()}')
        dlcs = raw['DLC'].map(_dlc) if 'DLC' in raw else pd.Series(8, index=raw.index)
        payload, normalizations = [], 0
        for ix, row in raw.iterrows():
            original = [str(row[f'DATA_{j}']).strip() for j in range(int(dlcs.loc[ix]))]
            normalizations += sum(re.fullmatch(r'[0-9]\.0', v) is not None for v in original)
            values = [ciciov_byte(v) for v in original]
            payload.append(''.join(values))
        out = pd.DataFrame({'timestamp': np.nan, 'arbitration_id': raw.ID.to_numpy(),
                            'data_field': payload, 'dlc': dlcs.to_numpy(),
                            'attack': label.ne('BENIGN').astype(np.int8).to_numpy()})
        out.attrs['format_normalizations'] = normalizations
    elif kind == 'otids':
        if not {'TS', 'ID1', 'LEN', 'target'}.issubset(raw):
            raise ValueError('OTIDS schema is not supported.')
        dlcs, payload = raw.LEN.map(_dlc), []
        for ix, row in raw.iterrows():
            values = [str(row[f'DLC{j}']).strip().zfill(2) for j in range(int(dlcs.loc[ix]))]
            if any(re.fullmatch('[0-9a-fA-F]{2}', v) is None for v in values):
                raise ValueError('Invalid OTIDS hex byte.')
            payload.append(''.join(values))
        out = pd.DataFrame({'timestamp': raw.TS.to_numpy(), 'arbitration_id': raw.ID1.to_numpy(),
                            'data_field': payload, 'dlc': dlcs.to_numpy(),
                            'attack': _labels(raw.target, binary=False)})
    else:
        raise ValueError(kind)
    out['timestamp'] = pd.to_numeric(out.timestamp, errors='raise')
    return out.reset_index(drop=True)


def read_frames(path, kind='ctt', chunksize=8192, label_policy=None):
    """Full file iterator. No nrows/prefix truncation in research runs.

    log policies: trailing (MIRGU), benign, or verified_dos with inclusive
    start/end and signature. Unverified labels cause an error, never benign.
    """
    path = Path(path)
    if kind in {'ctt', 'ciciov', 'otids'}:
        if kind == 'otids' and ('_B.' in path.name or '_UB.' in path.name):
            raise ValueError('Shuffled OTIDS derivatives are excluded from sequence evaluation.')
        for chunk in pd.read_csv(path, dtype=str, keep_default_na=False, chunksize=chunksize):
            yield canonical_csv(chunk, kind)
        return
    if kind != 'log' or not label_policy:
        raise ValueError('Log input requires explicit label provenance.')
    rows = []
    with path.open(encoding='utf-8-sig') as f:
        for lineno, line in enumerate(f, 1):
            if not line.strip() or line.lstrip().startswith('#'):
                continue
            m = LOG.fullmatch(line.strip())
            if not m:
                raise ValueError(f'{path.name}:{lineno}: malformed/unsupported frame')
            ts, cid, payload, trailing = m.groups()
            ts = float(ts)
            mode = label_policy['mode']
            if mode == 'trailing':
                if trailing is None:
                    raise ValueError(f'{path}:{lineno}: missing trailing frame label')
                label = int(trailing)
            elif mode == 'benign':
                label = 0
            elif mode == 'verified_dos':
                inside = label_policy['start'] <= ts <= label_policy['end']
                signature = int(cid, 16) == 0 and payload.upper() == '0000000000000000'
                if inside and not signature:
                    raise ValueError(f'{path}:{lineno}: DoS interval contradicts signature')
                label = int(inside)
            else:
                raise ValueError(f'Unsupported/unverified log label policy: {mode}')
            rows.append((ts, cid, payload, label))
            if len(rows) == chunksize:
                yield pd.DataFrame(rows, columns=['timestamp', 'arbitration_id', 'data_field', 'attack'])
                rows = []
    if rows:
        yield pd.DataFrame(rows, columns=['timestamp', 'arbitration_id', 'data_field', 'attack'])


def capture_group(path):
    """Conservative recording-round group, subject to provenance review.

    All attack files sharing a trailing recording number stay together. This
    is stricter than random windows but not proof of independent drive sessions.
    """
    m = re.search(r'-(\d+)$', Path(path).stem)
    if not m:
        raise ValueError(f'No source capture-round suffix: {path}')
    return m.group(1)


def source_split(files, seed=42):
    groups = sorted({capture_group(p) for p in files}, key=int)
    if len(groups) < 2:
        raise ValueError('At least two source capture groups required; no random-window fallback.')
    # A fixed group split shared by every seed/representation. No test labels.
    validation_group = groups[-1]
    train = [p for p in files if capture_group(p) != validation_group]
    validation = [p for p in files if capture_group(p) == validation_group]
    return train, validation


def json_write(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')
