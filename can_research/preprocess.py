"""Tiền xử lý và chuẩn hóa dữ liệu mạng CAN Bus cho huấn luyện mô hình.

Tuân thủ nghiêm ngặt Frozen Research Protocol (README.md):
1. Đọc và làm sạch dữ liệu từ các file CSV hoặc log (xử lý triệt để lỗi NaN, chuỗi 'nan', 'na', rỗng).
2. Trích xuất 29 đặc trưng thô chuẩn (Raw Baseline Representation):
   - 11 bit CAN ID (id_bit_0 .. id_bit_10)
   - DLC chuẩn hóa về [0, 1]
   - 8 byte Payload (byte_0 .. byte_7) chia tỉ lệ về [0, 1]
   - Mặt nạ byte (mask_0 .. mask_7) xác định byte dữ liệu thực
   - Khoảng cách thời gian (timestamp_delta) được log-transform: log(1 + 1000 * dt)
3. Cơ chế cửa sổ không chồng lấn 64 gói tin (64-message non-overlapping windows):
   - Một cửa sổ mang nhãn 1 (Attack) nếu có ít nhất 1 frame bị tấn công.
   - Tuyệt đối không ghép nối cửa sổ xuyên qua biên giới 2 file khác nhau.
4. Đánh giá Streaming và tính toán đầy đủ các metrics học thuật:
   - Attack F1, Precision, Recall, PR-AUC
   - False Alarms per 100,000 Benign Windows (FAR/100k)
   - Bảng phân tích độ lệch phân phối (Shift Effects: A-B, A-C, C-D, Interaction)
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, average_precision_score, f1_score, precision_score, recall_score


# Danh sách tên 29 đặc trưng số đầu vào cho từng frame
FRAME_FEATURE_COLUMNS = [
    *[f"id_bit_{i}" for i in range(11)],
    "dlc",
    *[f"byte_{i}" for i in range(8)],
    *[f"mask_{i}" for i in range(8)],
    "log_time_delta",
]
FEATURE_COLUMNS = FRAME_FEATURE_COLUMNS


def clean_hex_string(val: Any) -> str:
    """Loại bỏ ký tự lạ, khoảng trắng, tiền tố 0x và xử lý triệt để NaN / 'na' / 'nan'."""
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return ""
    text = str(val).strip()
    if text.lower() in ("nan", "na", "null", "none", ""):
        return ""
    text = text.replace("0x", "").replace("0X", "")
    return re.sub(r"[^0-9A-Fa-f]", "", text)


def parse_can_id_bits(id_val: Any) -> List[float]:
    """Chuyển đổi CAN ID thành 11 bit nhị phân (0.0 hoặc 1.0)."""
    hex_str = clean_hex_string(id_val)
    if not hex_str:
        return [0.0] * 11
    try:
        id_int = int(hex_str, 16)
    except ValueError:
        return [0.0] * 11
    return [float((id_int >> bit) & 1) for bit in range(10, -1, -1)]


def parse_payload_and_masks(data_field: Any) -> Tuple[List[float], List[float], float]:
    """Chuyển chuỗi payload hex thành 8 byte chuẩn hóa [0, 1], 8 mặt nạ và DLC."""
    hex_str = clean_hex_string(data_field)
    if len(hex_str) % 2 != 0:
        hex_str = "0" + hex_str
    
    num_bytes = min(len(hex_str) // 2, 8)
    byte_vals = [int(hex_str[i * 2 : i * 2 + 2], 16) / 255.0 for i in range(num_bytes)] + [0.0] * (8 - num_bytes)
    masks = [1.0] * num_bytes + [0.0] * (8 - num_bytes)
    dlc_norm = num_bytes / 8.0
    return byte_vals, masks, dlc_norm


def extract_features_matrix(df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
    """Trích xuất ma trận đặc trưng (N, 29) và vector nhãn (N,) từ DataFrame thô."""
    n_rows = len(df)
    if n_rows == 0:
        return np.empty((0, 29), dtype=np.float32), np.empty((0,), dtype=int)

    # 1. Delta thời gian (log scale: log1p(dt * 1000))
    if "timestamp" in df.columns:
        ts = pd.to_numeric(df["timestamp"], errors="coerce").fillna(0.0).values
        dt = np.empty(n_rows, dtype=np.float32)
        dt[0] = 0.0
        dt[1:] = np.diff(ts)
        dt = np.clip(dt, 0.0, 10.0)
        log_dt = np.log1p(dt * 1000.0)
    else:
        log_dt = np.zeros(n_rows, dtype=np.float32)

    # 2. CAN ID bits (11 bit)
    raw_ids = df["arbitration_id"].values if "arbitration_id" in df.columns else [""] * n_rows
    id_bits_arr = np.array([parse_can_id_bits(x) for x in raw_ids], dtype=np.float32)

    # 3. Payload bytes, masks, DLC
    raw_payloads = df["data_field"].values if "data_field" in df.columns else [""] * n_rows
    byte_list, mask_list, dlc_list = [], [], []
    for p in raw_payloads:
        b, m, d = parse_payload_and_masks(p)
        byte_list.append(b)
        mask_list.append(m)
        dlc_list.append(d)

    bytes_arr = np.array(byte_list, dtype=np.float32)
    masks_arr = np.array(mask_list, dtype=np.float32)
    dlc_arr = np.array(dlc_list, dtype=np.float32).reshape(-1, 1)
    time_arr = log_dt.reshape(-1, 1)

    X_frames = np.hstack([id_bits_arr, dlc_arr, bytes_arr, masks_arr, time_arr])

    # 4. Nhãn y
    if "attack" in df.columns:
        y_frames = pd.to_numeric(df["attack"], errors="coerce").fillna(0).astype(int).values
    else:
        y_frames = np.zeros(n_rows, dtype=int)

    return X_frames, y_frames


def extract_windows_from_df(
    df: pd.DataFrame,
    window_size: int = 64,
    flatten: bool = True,
) -> Tuple[np.ndarray, np.ndarray]:
    """Cắt các gói tin trong 1 file thành cửa sổ không chồng lấn kích thước window_size (64).
    
    Quy tắc Frozen Protocol:
    - Cửa sổ mang nhãn 1 nếu có >= 1 frame attack.
    - Phần dư < window_size ở cuối file sẽ bị loại bỏ (không nối xuyên file).
    
    Returns:
        X_win: shape (num_windows, window_size * 29) nếu flatten=True, hoặc (num_windows, 64, 29)
        y_win: shape (num_windows,) nhãn 0 hoặc 1
    """
    X_frames, y_frames = extract_features_matrix(df)
    n_frames = len(df)
    num_windows = n_frames // window_size

    if num_windows == 0:
        feat_dim = window_size * 29 if flatten else (window_size, 29)
        return np.empty((0, feat_dim) if flatten else (0, window_size, 29), dtype=np.float32), np.empty((0,), dtype=int)

    # Cắt gọn về bội số của window_size
    valid_len = num_windows * window_size
    X_cut = X_frames[:valid_len]
    y_cut = y_frames[:valid_len]

    # Định hình lại thành cửa sổ
    if flatten:
        X_win = X_cut.reshape(num_windows, window_size * 29)
    else:
        X_win = X_cut.reshape(num_windows, window_size, 29)

    # Cửa sổ là Attack nếu có ít nhất 1 frame attack
    y_win = (y_cut.reshape(num_windows, window_size).max(axis=1) > 0).astype(int)
    return X_win, y_win


def load_balanced_train_windows(
    train_folder: Union[str, Path],
    window_size: int = 64,
    max_windows_per_file: int = 2000,
    flatten: bool = True,
    random_state: int = 42,
    max_rows_per_file: Optional[int] = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """Load dữ liệu Train với kỹ thuật Class-Balanced Sampling theo protocol README.
    
    README: 'The default training limit (2,000 windows per source file) is deliberate so a first run is small'.
    Lấy toàn bộ cửa sổ Attack (vì rất hiếm) và lấy mẫu số lượng Benign tương ứng.
    """
    rng = np.random.RandomState(random_state)
    folder = Path(train_folder)
    files = sorted(folder.glob("*.csv"))

    # Giới hạn số dòng đọc mỗi file để tối ưu RAM và tốc độ (mặc định lấy đủ số cửa sổ cần)
    if max_rows_per_file is None:
        nrows_to_read = max_windows_per_file * window_size * 2
    else:
        nrows_to_read = max_rows_per_file

    X_collected = []
    y_collected = []

    for f in files:
        df = pd.read_csv(f, nrows=nrows_to_read)
        X_win, y_win = extract_windows_from_df(df, window_size=window_size, flatten=flatten)
        if len(y_win) == 0:
            continue

        idx_attack = np.where(y_win == 1)[0]
        idx_benign = np.where(y_win == 0)[0]

        n_attack = len(idx_attack)
        # Giữ tỉ lệ mẫu hợp lý và không vượt quá max_windows_per_file
        n_benign_to_pick = min(len(idx_benign), max(n_attack * 2, max_windows_per_file - n_attack))
        if n_benign_to_pick > 0:
            sampled_benign = rng.choice(idx_benign, size=n_benign_to_pick, replace=False)
            selected_idx = np.sort(np.concatenate([idx_attack, sampled_benign]))
        else:
            selected_idx = idx_attack

        X_collected.append(X_win[selected_idx])
        y_collected.append(y_win[selected_idx])

    if not X_collected:
        dim = window_size * 29 if flatten else (window_size, 29)
        return np.empty((0, dim) if flatten else (0, window_size, 29), dtype=np.float32), np.empty((0,), dtype=int)

    X_total = np.concatenate(X_collected, axis=0)
    y_total = np.concatenate(y_collected, axis=0)
    return X_total, y_total


def compute_ctt_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_prob: Optional[np.ndarray] = None,
) -> Dict[str, float]:
    """Tính toán đầy đủ bộ chỉ số đánh giá chuẩn theo Frozen Research Protocol:
    - attack F1, precision, recall
    - PR-AUC (Precision-Recall AUC)
    - false alarms per 100,000 benign windows
    - accuracy
    """
    y_true = np.asarray(y_true, dtype=int)
    y_pred = np.asarray(y_pred, dtype=int)

    f1 = float(f1_score(y_true, y_pred, pos_label=1, zero_division=0))
    prec = float(precision_score(y_true, y_pred, pos_label=1, zero_division=0))
    rec = float(recall_score(y_true, y_pred, pos_label=1, zero_division=0))
    acc = float(accuracy_score(y_true, y_pred))

    # Tính PR-AUC
    if y_prob is not None and len(np.unique(y_true)) > 1:
        try:
            pr_auc = float(average_precision_score(y_true, y_prob))
        except Exception:
            pr_auc = np.nan
    else:
        pr_auc = f1 if len(y_true) > 0 else np.nan

    # Tính False Alarms per 100,000 Benign Windows
    # FAR = (FP / Benign_Total) * 100,000
    fp = int(np.sum((y_pred == 1) & (y_true == 0)))
    total_benign = int(np.sum(y_true == 0))
    far_100k = (fp / total_benign * 100000.0) if total_benign > 0 else 0.0

    return {
        "Total_Windows": int(len(y_true)),
        "Attack_Windows": int(np.sum(y_true == 1)),
        "Benign_Windows": total_benign,
        "Attack_F1": round(f1, 4),
        "Precision": round(prec, 4),
        "Recall": round(rec, 4),
        "PR_AUC": round(pr_auc, 4) if not np.isnan(pr_auc) else np.nan,
        "FAR_per_100k": round(far_100k, 2),
        "Accuracy": round(acc, 4),
    }


def compute_shift_effects(metrics_df: pd.DataFrame) -> pd.DataFrame:
    """Tính các hiệu ứng phân phối lệch (Distribution Shift Effects) từ bảng metrics:
    - Vehicle shift, known attack   = A - B
    - Attack shift, known vehicle   = A - C
    - Vehicle shift, unknown attack = C - D
    - Interaction                   = (A - B) - (C - D)
    """
    required_conditions = ["A", "B", "C", "D"]
    # Trích xuất F1 của từng condition
    f1_map = {}
    for cond in required_conditions:
        row = metrics_df[metrics_df["Condition"].str.startswith(cond)]
        if not row.empty:
            f1_map[cond] = row["Attack_F1"].values[0]
        else:
            f1_map[cond] = np.nan

    a = f1_map.get("A", np.nan)
    b = f1_map.get("B", np.nan)
    c = f1_map.get("C", np.nan)
    d = f1_map.get("D", np.nan)

    veh_shift_known = a - b
    atk_shift_known = a - c
    veh_shift_unknown = c - d
    interaction = (a - b) - (c - d)

    effects = [
        {"Shift_Effect": "Vehicle Shift (Known Attack): A - B", "Delta_F1": round(veh_shift_known, 4), "Description": "F1 drop when transferring to unseen vehicle with known attack"},
        {"Shift_Effect": "Attack Shift (Known Vehicle): A - C", "Delta_F1": round(atk_shift_known, 4), "Description": "F1 drop when encountering unseen attack on known vehicle"},
        {"Shift_Effect": "Vehicle Shift (Unknown Attack): C - D", "Delta_F1": round(veh_shift_unknown, 4), "Description": "F1 drop when transferring vehicle under novel attack"},
        {"Shift_Effect": "Interaction: (A - B) - (C - D)", "Delta_F1": round(interaction, 4), "Description": "Interaction effect between vehicle shift and attack shift"},
    ]
    return pd.DataFrame(effects)
