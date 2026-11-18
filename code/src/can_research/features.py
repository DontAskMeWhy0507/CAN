"""Completed-window features, continuous causal history inside each source file.

    Local counts use the complete window. Decisions are made at window end.
    Caller creates one WindowExtractor per capture; arbitrary I/O chunks must
    not change windows, history, or predictions. No target-fitted normalization.
"""
from __future__ import annotations
from collections import Counter
import numpy as np
import pandas as pd

SCHEMA_VERSION = 'can-thesis-v2.1'


def validate_frames(df, require_timing=True):
    required = {'arbitration_id', 'data_field', 'attack', 'timestamp'}
    if not required.issubset(df):
        raise ValueError(f'Missing frame fields: {required - set(df.columns)}')
    if not df['attack'].isin([0, 1]).all():
        raise ValueError('Missing/invalid ground truth; never default labels to benign.')
    ts = np.asarray(df.timestamp, float)
    if np.isinf(ts).any():
        raise ValueError('Infinite timestamps are not missing timestamps.')
    if require_timing and (not np.isfinite(ts).all()):
        raise ValueError('Timing tier requires real, finite timestamps.')
    if np.isfinite(ts).any() and not np.isfinite(ts).all():
        raise ValueError('Mixed missing and present timestamps.')
    if np.isfinite(ts).all() and len(ts) > 1 and (np.diff(ts) < 0).any():
        raise ValueError('Non-monotonic timestamps: shuffled data or mixed captures.')


def parse_payload(payload, dlc=None):
    text = str(payload).strip().upper()
    if len(text) % 2 or len(text) > 16 or any(c not in '0123456789ABCDEF' for c in text):
        raise ValueError(f'Invalid classic-CAN payload: {text!r}')
    n = len(text) // 2
    if dlc is not None and not pd.isna(dlc):
        if float(dlc) != n:
            raise ValueError(f'DLC {dlc} disagrees with actual payload length {n}.')
    b = np.zeros(8, dtype=np.float32)
    b[:n] = list(bytes.fromhex(text))
    mask = (np.arange(8) < n).astype(np.float32)
    return b / 255., mask, n / 8.


def parse_id(value):
    text = str(value).strip().upper().removeprefix('0X')
    if not text or any(c not in '0123456789ABCDEF' for c in text):
        raise ValueError(f'Invalid CAN ID: {value!r}')
    cid = int(text, 16)
    if not 0 <= cid <= 0x7FF:
        raise ValueError('This experiment supports standard 11-bit CAN only; no truncation of extended IDs.')
    return cid


def select_features(raw, structural, representation, tier='timed'):
    if tier not in {'timed', 'content'}:
        raise ValueError(tier)
    ri = list(range(29)) if tier == 'timed' else list(range(28))
    si = list(range(32)) if tier == 'timed' else [i for i in range(32) if i not in (26, 27)]
    if representation == 'raw':
        return raw[..., ri]
    if representation == 'raw_no_id':
        return raw[..., [i for i in ri if i >= 11]]
    if representation == 'id_only':
        return raw[..., :11]
    if representation == 'payload_only':
        return raw[..., 11:28]
    if representation == 'timing_only':
        if tier != 'timed':
            raise ValueError('Timing-only model cannot use content tier.')
        return structural[..., 26:28]
    if representation == 'raw_plus_structural':
        extra = [i for i in si if i >= 17 and i != 26]
        return np.concatenate([raw[..., ri], structural[..., extra]], axis=-1)
    drops = {'structural': [], 'structural_no_delta': list(range(17, 26)),
             'structural_no_payload': list(range(1, 9)), 'structural_no_rank_w': [30],
             'structural_no_timing': [26, 27], 'structural_no_local': [28, 29, 30],
             'structural_no_transition': [31]}
    if representation not in drops:
        raise ValueError(f'Unknown representation: {representation}')
    return structural[..., [i for i in si if i not in drops[representation]]]


class WindowExtractor:
    def __init__(self, window_size=64, tier='timed'):
        if window_size < 2 or tier not in {'timed', 'content'}:
            raise ValueError('Invalid window configuration.')
        self.w, self.tier = window_size, tier
        self.pending = pd.DataFrame()
        self.history, self.prev_t, self.last_seen_t = {}, None, None
        self.frames_seen = self.windows_seen = 0

    def feed(self, frames):
        validate_frames(frames, require_timing=self.tier == 'timed')
        if len(frames):
            ts = np.asarray(frames.timestamp, float)
            if np.isfinite(ts).all():
                if self.last_seen_t is not None and ts[0] < self.last_seen_t:
                    raise ValueError('Timestamp inversion across I/O chunks.')
                self.last_seen_t = ts[-1]
        self.frames_seen += len(frames)
        df = pd.concat([self.pending, frames], ignore_index=True) if len(self.pending) else frames.reset_index(drop=True)
        n = len(df) // self.w
        self.pending = df.iloc[n * self.w:].copy()
        raw = np.zeros((n, self.w, 29), np.float32)
        structural = np.zeros((n, self.w, 32), np.float32)
        labels, starts, ends = np.zeros(n, np.int8), np.zeros(n), np.zeros(n)
        for k in range(n):
            block = df.iloc[k * self.w:(k + 1) * self.w]
            ids = [parse_id(v) for v in block.arbitration_id]
            counts, transitions = Counter(ids), Counter(zip(ids[:-1], ids[1:]))
            ranks = {v: i for i, v in enumerate(dict.fromkeys(ids))}
            labels[k] = int(block.attack.max())
            starts[k], ends[k] = block.timestamp.iloc[0], block.timestamp.iloc[-1]
            for j, row in enumerate(block.itertuples(index=False)):
                cid, t = ids[j], float(row.timestamp)
                b, mask, dlc = parse_payload(row.data_field, getattr(row, 'dlc', None))
                dt = 0. if self.prev_t is None or self.tier == 'content' else t - self.prev_t
                logdt = np.log1p(1000 * min(dt, 10.))
                raw[k, j, :11] = [(cid >> bit) & 1 for bit in range(10, -1, -1)]
                raw[k, j, 11:28] = np.r_[dlc, b, mask]
                raw[k, j, 28] = logdt
                structural[k, j, :17] = np.r_[dlc, b, mask]
                if cid in self.history:
                    last_t, last_b, last_mask = self.history[cid]
                    structural[k, j, 17:25] = np.abs(b - last_b) * mask * last_mask
                    structural[k, j, 25] = 1
                    if self.tier == 'timed':
                        structural[k, j, 27] = np.log1p(1000 * min(t - last_t, 10.))
                structural[k, j, 26] = logdt
                structural[k, j, 28:31] = [counts[cid] / self.w, ranks[cid] / len(ranks), ranks[cid] / self.w]
                if j:
                    structural[k, j, 31] = transitions[(ids[j-1], cid)] / (self.w - 1)
                self.history[cid], self.prev_t = (t, b, mask), t
        first = self.windows_seen
        self.windows_seen += n
        return raw, structural, labels, np.arange(first, first+n), starts, ends

    def finish(self):
        # A discarded short tail is still input data and must satisfy the schema.
        for row in self.pending.itertuples(index=False):
            parse_id(row.arbitration_id)
            parse_payload(row.data_field, getattr(row, 'dlc', None))
        return dict(frames=self.frames_seen, windows=self.windows_seen, tail_frames=len(self.pending))


def extract_windows(df, window_size=64, tier='timed', representation='structural'):
    extractor = WindowExtractor(window_size, tier)
    out = extractor.feed(df)
    extractor.finish()
    return select_features(out[0], out[1], representation, tier), out[2]
