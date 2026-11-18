"""Audit CAN-MIRGU suspension label semantics, without changing source logs.

This is a data audit, not a detector evaluation. Labels are read as published.
The absence of the suspended identifier during positive intervals is recorded;
no labels are inferred from filenames or replaced.
"""
import argparse
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path


def audit(path, window_size=64):
    target = int(path.stem.split('_')[1], 16)
    counts, target_counts, windows = Counter(), Counter(), Counter()
    identifiers = {0: set(), 1: set()}
    intervals, pending, previous_label, previous_ts = [], [], None, None
    digest = hashlib.sha256()
    first_ts = last_ts = None
    with path.open('rb') as stream:
        for lineno, raw in enumerate(stream, 1):
            digest.update(raw)
            line = raw.decode('utf-8-sig').strip()
            if not line:
                continue
            fields = line.split()
            if len(fields) != 4 or fields[-1] not in {'0', '1'}:
                raise ValueError(f'{path}:{lineno}: unexpected labeled candump format')
            ts = Decimal(fields[0].strip('()'))
            cid = int(fields[2].split('#')[0], 16)
            label = int(fields[3])
            if previous_ts is not None and ts < previous_ts:
                raise ValueError(f'{path}:{lineno}: timestamp inversion')
            first_ts = ts if first_ts is None else first_ts
            last_ts = ts
            counts[label] += 1
            target_counts[label] += int(cid == target)
            identifiers[label].add(cid)
            if label != previous_label:
                intervals.append({'label': label, 'first_timestamp': str(ts), 'frames': 0})
            intervals[-1]['frames'] += 1
            intervals[-1]['last_timestamp'] = str(ts)
            previous_ts, previous_label = ts, label
            pending.append(label)
            if len(pending) == window_size:
                windows[max(pending)] += 1
                pending = []
    return dict(file=path.as_posix(), sha256=digest.hexdigest(), target_id=f'{target:03X}',
                first_timestamp=str(first_ts), last_timestamp=str(last_ts),
                frame_labels={str(k): counts[k] for k in (0, 1)},
                window_labels={str(k): windows[k] for k in (0, 1)},
                target_id_counts_by_label={str(k): target_counts[k] for k in (0, 1)},
                distinct_id_counts_by_label={str(k): len(identifiers[k]) for k in (0, 1)},
                label_intervals=intervals, discarded_tail_frames=len(pending))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', default='.')
    parser.add_argument('--output', default='results/suspension_semantics_audit.json')
    args = parser.parse_args()
    paths = sorted((Path(args.root) / 'data/CAN-MIRGU/Attack/Suspension_attacks').glob('*.log'))
    if not paths:
        raise ValueError('No suspension logs found')
    rows = [audit(path) for path in paths]
    chronological = sorted(rows, key=lambda row: Decimal(row['first_timestamp']))
    gaps = [dict(previous=a['file'], following=b['file'],
                 gap_seconds=str(Decimal(b['first_timestamp']) - Decimal(a['last_timestamp'])))
            for a, b in zip(chronological, chronological[1:])]
    report = dict(created_utc=datetime.now(timezone.utc).isoformat(),
                  audit_scope='Full scan of supplied suspension logs only; no model inference',
                  window_size=64, files=rows, interfile_timestamp_gaps=gaps,
                  interpretation='Positive labels mark periods of suspension; the targeted ID is absent. '
                  'These labels are not injected-malicious-frame labels. Near-contiguous timestamps '
                  'are a dependency warning, not proof of a common drive-session identity.',
                  primary_source='https://www.ndss-symposium.org/wp-content/uploads/vehiclesec2024-23043-paper.pdf')
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(dict(files=len(rows), frames=sum(sum(r['frame_labels'].values()) for r in rows),
                          positive_frames=sum(r['frame_labels']['1'] for r in rows),
                          target_frames_during_positive=sum(r['target_id_counts_by_label']['1'] for r in rows),
                          output=str(out)), ensure_ascii=False))
