"""Bộ chuyển đổi đa tập dữ liệu (Multi-Dataset Adapters) - Phase 4.

Chuẩn hóa các bộ dữ liệu ngoại vi (CAN_HCRL_OTIDS, Automotive CAN Bus v2, CAN-MIRGU)
về lược đồ chuẩn (Canonical Frame Schema):
- timestamp: float (giây)
- arbitration_id: str (hex không tiền tố 0x)
- data_field: str (chuỗi hex 16 ký tự = 8 bytes)
- attack: int (0: benign, 1: attack)
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Generator, List, Optional, Tuple, Union

import numpy as np
import pandas as pd


def otids_chunk_to_canonical(chunk: pd.DataFrame) -> pd.DataFrame:
    """Chuyển đổi một khối DataFrame từ bộ dữ liệu CAN_HCRL_OTIDS sang Canonical Schema."""
    # 1. Chuẩn hóa payload hex từ DLC0 .. DLC7
    cols = [f"DLC{i}" for i in range(8)]
    byte_cols = []
    for c in cols:
        if c in chunk.columns:
            s = chunk[c].fillna("00").astype(str).str.strip().apply(
                lambda x: x.zfill(2) if len(x) < 2 else x[:2]
            )
        else:
            s = pd.Series(["00"] * len(chunk), index=chunk.index)
        byte_cols.append(s)
    
    payload = byte_cols[0]
    for b in byte_cols[1:]:
        payload = payload + b

    # 2. Chuẩn hóa ID
    id_col = "ID1" if "ID1" in chunk.columns else ("arbitration_id" if "arbitration_id" in chunk.columns else None)
    if id_col:
        ids = chunk[id_col].astype(str).str.strip().str.replace("0x", "", case=False)
    else:
        ids = pd.Series(["000"] * len(chunk), index=chunk.index)

    # 3. Chuẩn hóa Timestamp
    ts_col = "TS" if "TS" in chunk.columns else ("timestamp" if "timestamp" in chunk.columns else None)
    if ts_col:
        timestamps = pd.to_numeric(chunk[ts_col], errors="coerce").fillna(0.0).values
    else:
        timestamps = np.arange(len(chunk), dtype=np.float64) * 0.001

    # 4. Chuẩn hóa nhãn target (0 = benign, >0 = attack)
    if "target" in chunk.columns:
        targets = pd.to_numeric(chunk["target"], errors="coerce").fillna(0).astype(int).values
        y_attack = (targets > 0).astype(int)
    elif "attack" in chunk.columns:
        y_attack = pd.to_numeric(chunk["attack"], errors="coerce").fillna(0).astype(int).values
    else:
        y_attack = np.zeros(len(chunk), dtype=int)

    return pd.DataFrame({
        "timestamp": timestamps,
        "arbitration_id": ids.values,
        "data_field": payload.values,
        "attack": y_attack
    })


def parse_candump_chunk(lines: List[str], attack_intervals: Optional[List[Tuple[float, float]]] = None) -> pd.DataFrame:
    """Phân tích các dòng log candump: (timestamp) interface ID#PAYLOAD."""
    pattern = re.compile(r"\(([\d\.]+)\)\s+\S+\s+([0-9A-Fa-f]+)#([0-9A-Fa-f]*)")
    ts_list, id_list, data_list = [], [], []

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        match = pattern.search(line)
        if match:
            t = float(match.group(1))
            cid = match.group(2)
            p = match.group(3)
            # Pad payload to 16 hex chars (8 bytes)
            p = (p + "0000000000000000")[:16]
            ts_list.append(t)
            id_list.append(cid)
            data_list.append(p)

    if not ts_list:
        return pd.DataFrame(columns=["timestamp", "arbitration_id", "data_field", "attack"])

    ts_arr = np.array(ts_list, dtype=np.float64)
    y_attack = np.zeros(len(ts_arr), dtype=int)

    if attack_intervals:
        for start_t, end_t in attack_intervals:
            y_attack[(ts_arr >= start_t) & (ts_arr <= end_t)] = 1

    return pd.DataFrame({
        "timestamp": ts_arr,
        "arbitration_id": id_list,
        "data_field": data_list,
        "attack": y_attack
    })
