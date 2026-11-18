"""Compatibility names for strict dataset I/O. See io.py and preflight.py."""
from pathlib import Path
import pandas as pd
from .io import canonical_csv, read_frames, CONDITIONS, VEHICLES, sha256_file
CTT_SCENARIOS = CONDITIONS
CTT_VEHICLES = VEHICLES

def canonicalize_ctt(raw, path=None):
    return canonical_csv(raw.astype(str), 'ctt')

def canonicalize_cici_hex(raw, path=None):
    return canonical_csv(raw.astype(str), 'ciciov')

def read_canonical_file(path, nrows=None, kind='ctt', label_policy=None):
    if nrows is not None:
        raise ValueError('Use streamed read_frames; no hidden prefix sampling.')
    return pd.concat(read_frames(Path(path), kind, label_policy=label_policy), ignore_index=True)

def audit_workspace(workspace, output_dir, **kwargs):
    from .preflight import audit_workspace as audit
    return audit(workspace, output_dir, **kwargs)
