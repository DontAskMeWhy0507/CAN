"""Compatibility interfaces. Scientific runs should use run_experiments.py."""
from pathlib import Path
import pandas as pd
from .features import extract_windows
from .metrics import compute_binary_metrics

FRAME_FEATURE_COLUMNS = [*[f"id_bit_{i}" for i in range(11)], "dlc", *[f"byte_{i}" for i in range(8)], *[f"mask_{i}" for i in range(8)], "log_time_delta"]
FEATURE_COLUMNS = FRAME_FEATURE_COLUMNS

def compute_ctt_metrics(y_true, y_pred, y_prob=None):
    return compute_binary_metrics(y_true, y_pred, y_prob)

def extract_windows_from_df(df, window_size=64, flatten=True):
    x, y = extract_windows(df, window_size, representation="raw")
    return (x.reshape(len(x), window_size * 29) if flatten else x), y

def load_balanced_train_windows(train_folder, window_size=64, max_windows_per_file=2000, flatten=True, random_state=42, max_rows_per_file=None):
    from .experiment import sample_source
    if max_rows_per_file is not None:
        raise ValueError("Prefix truncation is no longer supported. Use full-file reservoir sampling.")
    cfg = dict(window_size=window_size, tier="timed", sampling_seed=random_state, chunksize=8192, train_windows_per_class_per_file=max_windows_per_file // 2)
    raw, _, y, _, _ = sample_source(sorted(Path(train_folder).glob("*.csv")), cfg)
    return (raw.reshape(len(raw), -1) if flatten else raw), y

def compute_shift_effects(df):
    key = 'condition' if 'condition' in df else 'Condition'
    selections = {c: df.loc[df[key].str.startswith(c), 'Attack_F1'] for c in 'ABCD'}
    if any(len(rows) != 1 for rows in selections.values()):
        raise ValueError('Select exactly one matched row for each A/B/C/D condition before computing descriptive contrasts.')
    values = {c: rows.iloc[0] for c, rows in selections.items()}
    a,b,c,d = (values[k] for k in 'ABCD')
    return pd.DataFrame({'Shift_Effect': ['A-B', 'A-C', 'C-D', '(A-B)-(C-D)'], 'Delta_F1': [a-b,a-c,c-d,(a-b)-(c-d)]})
