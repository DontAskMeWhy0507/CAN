"""Mô đun biểu diễn cấu trúc độc lập CAN ID (Structural ID-Agnostic Representation) - Phase 3.

Tuân thủ nghiêm ngặt yêu cầu của README.md:
1. "The proposed representation must not use a globally meaningful raw CAN-ID."
2. 32 đặc trưng cấu trúc cho mỗi gói tin (Structural Features):
   - DLC và 8 byte payload + 8 masks (17 đặc trưng)
   - Độ lệch payload (delta bytes) so với gói trước có cùng ID cục bộ (8 đặc trưng)
   - Cờ đánh dấu đã xuất hiện ID này trước đó chưa (1 đặc trưng)
   - Khoảng cách thời gian nguyên nhân log_dt (1 đặc trưng)
   - Khoảng cách thời gian giữa 2 gói cùng ID log_same_id_dt (1 đặc trưng)
   - Tần suất xuất hiện ID trong cửa sổ 64 frames (1 đặc trưng)
   - Thứ tự xuất hiện đầu tiên của ID trong cửa sổ (local first-occurrence rank) (1 đặc trưng)
   - Mã định danh cục bộ đã tái lập chỉ mục (local ID re-indexed token) (1 đặc trưng)
   - Tần suất chuyển tiếp giữa 2 ID liên tiếp trong cửa sổ (transition frequency) (1 đặc trưng)
3. Mô hình Structural CAN Transformer với cơ chế Attention học trên chuỗi 64 cửa sổ.
"""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.metrics import accuracy_score, average_precision_score, f1_score, precision_score, recall_score


WINDOW_SIZE = 64
STRUCTURAL_FEATURE_DIM = 32


def clean_hex_string(val: Any) -> str:
    """Làm sạch chuỗi hex và xử lý triệt để NaN / rỗng."""
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return ""
    text = str(val).strip()
    if text.lower() in ("nan", "na", "null", "none", ""):
        return ""
    text = text.replace("0x", "").replace("0X", "")
    return re.sub(r"[^0-9A-Fa-f]", "", text)


def extract_structural_windows(
    df: pd.DataFrame,
    window_size: int = 64,
    flatten: bool = False,
) -> Tuple[np.ndarray, np.ndarray]:
    """Trích xuất cửa sổ 64 gói tin sang biểu diễn Cấu trúc Độc lập ID (Structural ID-Agnostic).
    
    Returns:
        X_win: shape (N_windows, 64, 32) nếu flatten=False, hoặc (N_windows, 2048) nếu flatten=True
        y_win: shape (N_windows,) nhãn 0 hoặc 1 (1 nếu cửa sổ có ít nhất 1 frame attack)
    """
    n_frames = len(df)
    num_windows = n_frames // window_size
    if num_windows == 0:
        out_shape = (0, window_size * STRUCTURAL_FEATURE_DIM) if flatten else (0, window_size, STRUCTURAL_FEATURE_DIM)
        return np.empty(out_shape, dtype=np.float32), np.empty((0,), dtype=int)

    # 1. Thu thập chuỗi thô
    ids_raw = [clean_hex_string(x) for x in (df["arbitration_id"].values if "arbitration_id" in df.columns else [""] * n_frames)]
    payloads_raw = [clean_hex_string(x) for x in (df["data_field"].values if "data_field" in df.columns else [""] * n_frames)]
    
    if "timestamp" in df.columns:
        ts = pd.to_numeric(df["timestamp"], errors="coerce").fillna(0.0).values
    else:
        ts = np.arange(n_frames, dtype=np.float64) * 0.001

    if "attack" in df.columns:
        y_frames = pd.to_numeric(df["attack"], errors="coerce").fillna(0).astype(int).values
    else:
        y_frames = np.zeros(n_frames, dtype=int)

    # 2. Xử lý trạng thái liên tục giữa các gói (prev_state) trong nội bộ file
    # prev_state[id] = (last_timestamp, last_byte_vals)
    prev_state: Dict[str, Tuple[float, List[int]]] = {}

    windows_X = np.zeros((num_windows, window_size, STRUCTURAL_FEATURE_DIM), dtype=np.float32)
    windows_y = np.zeros(num_windows, dtype=int)

    for w_idx in range(num_windows):
        start = w_idx * window_size
        end = start + window_size
        
        w_ids = ids_raw[start:end]
        w_ts = ts[start:end]
        w_payloads = payloads_raw[start:end]
        w_y = y_frames[start:end]

        # Nhãn cửa sổ: 1 nếu có >= 1 frame attack
        windows_y[w_idx] = 1 if np.any(w_y == 1) else 0

        # Thống kê cấu trúc cục bộ bên trong cửa sổ 64 frames
        id_counts = Counter(w_ids)
        unique_ids = []
        seen = set()
        for cid in w_ids:
            if cid not in seen:
                seen.add(cid)
                unique_ids.append(cid)
        n_unique = max(len(unique_ids), 1)
        id_to_rank = {cid: idx / n_unique for idx, cid in enumerate(unique_ids)}
        id_to_reindexed = {cid: idx / float(window_size) for idx, cid in enumerate(unique_ids)}

        trans_counts = Counter()
        for idx in range(window_size - 1):
            trans_counts[(w_ids[idx], w_ids[idx + 1])] += 1

        # Trích xuất 32 đặc trưng cho từng frame
        for i in range(window_size):
            cid = w_ids[i]
            t = w_ts[i]
            p_hex = w_payloads[i]
            if len(p_hex) % 2 != 0:
                p_hex = "0" + p_hex
            num_b = min(len(p_hex) // 2, 8)
            b_vals = [int(p_hex[j * 2 : j * 2 + 2], 16) for j in range(num_b)] + [0] * (8 - num_b)

            # [0]: dlc
            windows_X[w_idx, i, 0] = num_b / 8.0
            # [1..8]: 8 byte payload
            for j in range(8):
                windows_X[w_idx, i, 1 + j] = b_vals[j] / 255.0
            # [9..16]: 8 mặt nạ (masks)
            for j in range(8):
                windows_X[w_idx, i, 9 + j] = 1.0 if j < num_b else 0.0

            # [17..24]: delta bytes so với gói trước CÙNG ID
            # [25]: has_prev_same_id
            # [27]: log_same_id_time_delta
            if cid in prev_state:
                last_t, last_b = prev_state[cid]
                for j in range(8):
                    windows_X[w_idx, i, 17 + j] = abs(b_vals[j] - last_b[j]) / 255.0
                windows_X[w_idx, i, 25] = 1.0
                dt_same = max(0.0, t - last_t)
                windows_X[w_idx, i, 27] = np.log1p(min(dt_same, 10.0) * 1000.0)
            else:
                windows_X[w_idx, i, 25] = 0.0
                windows_X[w_idx, i, 27] = 0.0

            # Cập nhật trạng thái
            prev_state[cid] = (t, b_vals)

            # [26]: log_causal_dt (khoảng cách so với gói ngay trước)
            dt_prev = max(0.0, t - w_ts[i - 1]) if i > 0 else 0.0
            windows_X[w_idx, i, 26] = np.log1p(min(dt_prev, 10.0) * 1000.0)

            # [28]: Tần suất xuất hiện ID trong cửa sổ
            windows_X[w_idx, i, 28] = id_counts[cid] / float(window_size)
            # [29]: Thứ tự xuất hiện đầu tiên của ID
            windows_X[w_idx, i, 29] = id_to_rank.get(cid, 0.0)
            # [30]: Local ID re-indexed token
            windows_X[w_idx, i, 30] = id_to_reindexed.get(cid, 0.0)
            # [31]: Tần suất chuyển tiếp cặp ID
            trans_key = (w_ids[i - 1], cid) if i > 0 else None
            windows_X[w_idx, i, 31] = (trans_counts[trans_key] / (window_size - 1.0)) if trans_key in trans_counts else 0.0

    if flatten:
        windows_X = windows_X.reshape(num_windows, window_size * STRUCTURAL_FEATURE_DIM)

    return windows_X, windows_y


class CANTransformer(nn.Module):
    """Mô hình Structural CAN Transformer Encoder với Attention Head theo README.md."""
    def __init__(
        self,
        in_features: int = 32,
        d_model: int = 64,
        nhead: int = 4,
        num_layers: int = 2,
        dim_feedforward: int = 128,
        dropout: float = 0.1,
    ):
        super().__init__()
        self.input_proj = nn.Linear(in_features, d_model)
        self.pos_encoder = nn.Parameter(torch.randn(1, WINDOW_SIZE, d_model) * 0.02)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            batch_first=True,
            activation="gelu",
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.classifier = nn.Sequential(
            nn.LayerNorm(d_model),
            nn.Linear(d_model, 32),
            nn.ReLU(),
            nn.Linear(32, 2),
        )

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        # x shape: (batch_size, 64, in_features)
        h = self.input_proj(x) + self.pos_encoder
        encoded = self.transformer(h)
        pooled = encoded.mean(dim=1)
        logits = self.classifier(pooled)
        return logits, pooled
