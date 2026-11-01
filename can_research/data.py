"""Dataset adapters and audit utilities for CAN distribution-shift experiments.

All adapters return the same canonical dataframe.  The raw datasets are kept
unchanged; generated manifests are separate research artefacts.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Mapping, Optional

import numpy as np
import pandas as pd


CTT_SCENARIOS: Dict[str, str] = {
    "train_01": "source_train",
    "test_01_known_vehicle_known_attack": "known_vehicle_known_attack",
    "test_02_unknown_vehicle_known_attack": "unknown_vehicle_known_attack",
    "test_03_known_vehicle_unknown_attack": "known_vehicle_unknown_attack",
    "test_04_unknown_vehicle_unknown_attack": "unknown_vehicle_unknown_attack",
}

CTT_VEHICLES: Dict[str, Dict[str, Dict[str, str]]] = {
    "set_01": {
        "known": {"vehicle": "chevrolet_impala_2011", "manufacturer": "Chevrolet"},
        "unknown": {"vehicle": "chevrolet_silverado_2016", "manufacturer": "Chevrolet"},
    },
    "set_02": {
        "known": {"vehicle": "chevrolet_traverse_2011", "manufacturer": "Chevrolet"},
        "unknown": {"vehicle": "subaru_forester_2017", "manufacturer": "Subaru"},
    },
    "set_03": {
        "known": {"vehicle": "chevrolet_silverado_2016", "manufacturer": "Chevrolet"},
        "unknown": {"vehicle": "subaru_forester_2017", "manufacturer": "Subaru"},
    },
    "set_04": {
        "known": {"vehicle": "subaru_forester_2017", "manufacturer": "Subaru"},
        "unknown": {"vehicle": "chevrolet_traverse_2011", "manufacturer": "Chevrolet"},
    },
}

BYTE_COLUMNS = [f"byte_{index}" for index in range(8)]
MASK_COLUMNS = [f"mask_{index}" for index in range(8)]
ID_BIT_COLUMNS = [f"id_bit_{index}" for index in range(11)]
CANONICAL_COLUMNS = [
    "timestamp",
    "can_id",
    "can_id_token",
    "dlc",
    *BYTE_COLUMNS,
    *MASK_COLUMNS,
    *ID_BIT_COLUMNS,
    "attack_binary",
    "attack_mechanism",
    "dataset",
    "vehicle_id",
    "manufacturer",
    "capture_id",
    "source_file",
    "scenario",
    "split_role",
]

_CANDUMP = re.compile(
    r"^\((?P<timestamp>[0-9]+(?:\.[0-9]+)?)\)\s+"
    r"(?P<interface>\S+)\s+(?P<can_id>[0-9A-Fa-f]+)#"
    r"(?P<payload>[0-9A-Fa-f]*)\s*(?P<label>[01])?\s*$"
)


def safe_hex_int(value: Any) -> int:
    """Parse a CAN identifier or byte without treating a missing value as text."""
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return 0
    text = str(value).strip().replace("0x", "").replace("0X", "")
    text = re.sub(r"[^0-9A-Fa-f]", "", text)
    return int(text, 16) if text else 0


def payload_to_bytes(value: Any, dlc: Optional[int] = None) -> tuple[List[int], List[int], int]:
    """Return fixed-width CAN payload values, masks, and DLC."""
    text = "" if value is None else str(value).strip()
    text = re.sub(r"[^0-9A-Fa-f]", "", text)
    if len(text) % 2:
        text = "0" + text
    inferred_dlc = min(len(text) // 2, 8)
    parsed_dlc = inferred_dlc if dlc is None else max(0, min(int(dlc), 8))
    values = [safe_hex_int(text[offset:offset + 2]) for offset in range(0, len(text), 2)][:8]
    values += [0] * (8 - len(values))
    masks = [1 if index < parsed_dlc else 0 for index in range(8)]
    return values, masks, parsed_dlc


def parse_dlc(value: Any, default: int = 8) -> int:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return default
    match = re.search(r"\d+", str(value))
    return max(0, min(int(match.group()) if match else default, 8))


def id_bits(can_id: int) -> List[int]:
    return [int((can_id >> bit) & 1) for bit in range(10, -1, -1)]


def attack_mechanism_from_text(text: str) -> str:
    normalized = text.lower().replace("_", "-")
    if "attack-free" in normalized or "benign" in normalized or "normal" in normalized:
        return "benign"
    if "dos" in normalized or "denial" in normalized or "flood" in normalized:
        return "flooding_dos"
    if "masquerade" in normalized:
        return "masquerade"
    if "suspension" in normalized or "suppress" in normalized:
        return "suspension"
    if "replay" in normalized:
        return "replay"
    if "fuzz" in normalized:
        return "fuzzing"
    if any(token in normalized for token in ("rpm", "speed", "triple", "double", "force-neutral", "spoof", "flam", "gear", "steering", "gas")):
        return "injection_spoofing"
    return "other_attack"


def _base_metadata(path: Optional[Path], context: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    metadata: Dict[str, Any] = {
        "dataset": "unknown",
        "vehicle_id": "unknown",
        "manufacturer": "unknown",
        "capture_id": path.stem if path else "unknown",
        "source_file": path.name if path else "unknown",
        "scenario": "unknown",
        "split_role": "unknown",
    }
    if context:
        metadata.update({key: value for key, value in context.items() if value is not None})
    return metadata


def _context_from_ctt_path(path: Path, ctt_root: Optional[Path] = None) -> Dict[str, Any]:
    parts = path.parts
    set_name = next((part for part in parts if re.fullmatch(r"set_0[1-4]", part)), "unknown")
    subset = next((part for part in parts if part in CTT_SCENARIOS), "unknown")
    scenario = CTT_SCENARIOS.get(subset, "unknown")
    vehicle_role = "unknown" if "unknown_vehicle" in scenario else "known"
    if subset == "train_01":
        vehicle_role = "known"
    vehicle = CTT_VEHICLES.get(set_name, {}).get(vehicle_role, {})
    return {
        "dataset": "can-train-and-test",
        "vehicle_id": vehicle.get("vehicle", "unknown"),
        "manufacturer": vehicle.get("manufacturer", "unknown"),
        "capture_id": f"{set_name}:{path.stem}",
        "source_file": path.name,
        "scenario": scenario,
        "split_role": subset,
    }


def _canonical_from_rows(
    timestamps: Iterable[Any],
    can_ids: Iterable[Any],
    payloads: Iterable[Any],
    labels: Iterable[Any],
    dlcs: Optional[Iterable[Any]] = None,
    mechanisms: Optional[Iterable[str]] = None,
    metadata: Optional[Mapping[str, Any]] = None,
) -> pd.DataFrame:
    timestamps = list(timestamps)
    can_ids = list(can_ids)
    payloads = list(payloads)
    labels = list(labels)
    dlcs = list(dlcs) if dlcs is not None else [None] * len(can_ids)
    mechanisms = list(mechanisms) if mechanisms is not None else ["other_attack"] * len(can_ids)
    rows: List[Dict[str, Any]] = []
    common = _base_metadata(None, metadata)

    def as_float_or_nan(value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return np.nan

    def as_binary_or_nan(value: Any) -> float:
        numeric = as_float_or_nan(value)
        return np.nan if np.isnan(numeric) else int(numeric > 0)

    for timestamp, can_id_raw, payload, label, dlc_raw, mechanism in zip(
        timestamps, can_ids, payloads, labels, dlcs, mechanisms
    ):
        can_id = safe_hex_int(can_id_raw)
        dlc = parse_dlc(dlc_raw, default=min(len(re.sub(r"[^0-9A-Fa-f]", "", str(payload))) // 2, 8))
        values, masks, dlc = payload_to_bytes(payload, dlc)
        attack = as_binary_or_nan(label)
        row = {
            "timestamp": as_float_or_nan(timestamp),
            "can_id": can_id,
            "can_id_token": f"{can_id:03X}",
            "dlc": dlc,
            "attack_binary": attack,
            "attack_mechanism": mechanism,
            **common,
        }
        row.update(dict(zip(BYTE_COLUMNS, values)))
        row.update(dict(zip(MASK_COLUMNS, masks)))
        row.update(dict(zip(ID_BIT_COLUMNS, id_bits(can_id))))
        rows.append(row)
    return pd.DataFrame(rows, columns=CANONICAL_COLUMNS)


def canonicalize_ctt(raw: pd.DataFrame, path: Optional[Path] = None) -> pd.DataFrame:
    """Canonicalize one can-train-and-test CSV dataframe."""
    required = {"timestamp", "arbitration_id", "data_field", "attack"}
    missing = required.difference(raw.columns)
    if missing:
        raise ValueError(f"CTT file is missing columns: {sorted(missing)}")
    context = _context_from_ctt_path(path) if path else {"dataset": "can-train-and-test"}
    mechanism = attack_mechanism_from_text(path.stem if path else "other_attack")
    mechanisms = ["benign" if int(label) == 0 else mechanism for label in pd.to_numeric(raw["attack"], errors="coerce").fillna(0)]
    return _canonical_from_rows(
        raw["timestamp"], raw["arbitration_id"], raw["data_field"], raw["attack"],
        mechanisms=mechanisms, metadata=context,
    )


def canonicalize_can_ml(raw: pd.DataFrame, path: Optional[Path] = None) -> pd.DataFrame:
    """Canonicalize a labeled can-ml CSV without borrowing CTT test context."""
    required = {"timestamp", "arbitration_id", "data_field", "attack"}
    missing = required.difference(raw.columns)
    if missing:
        raise ValueError(f"can-ml file is missing columns: {sorted(missing)}")
    path = Path(path) if path else None
    path_text = str(path).lower() if path else ""
    vehicle_map = {
        "impala": ("chevrolet_impala_2011", "Chevrolet"),
        "traverse": ("chevrolet_traverse_2011", "Chevrolet"),
        "silverado": ("chevrolet_silverado_2016", "Chevrolet"),
        "forester": ("subaru_forester_2017", "Subaru"),
    }
    vehicle_id, manufacturer = next((pair for marker, pair in vehicle_map.items() if marker in path_text), ("unknown", "unknown"))
    mechanism = attack_mechanism_from_text(path.stem if path else "other_attack")
    labels = pd.to_numeric(raw["attack"], errors="coerce").fillna(0)
    mechanisms = ["benign" if int(label) == 0 else mechanism for label in labels]
    context = {
        "dataset": "can-ml",
        "vehicle_id": vehicle_id,
        "manufacturer": manufacturer,
        "capture_id": f"{vehicle_id}:{path.stem if path else 'unknown'}",
        "source_file": path.name if path else "unknown",
        "scenario": "multisource_pool",
        "split_role": "unassigned",
    }
    return _canonical_from_rows(
        raw["timestamp"], raw["arbitration_id"], raw["data_field"], raw["attack"],
        mechanisms=mechanisms, metadata=context,
    )


def canonicalize_cici_hex(raw: pd.DataFrame, path: Optional[Path] = None) -> pd.DataFrame:
    """Canonicalize hexadecimal CICIoV2024 frames.

    CICIoV2024 has no timestamp in its supplied CSVs.  Timestamp-dependent
    feature tiers must therefore reject this output.
    """
    required = {"ID", "label"}
    missing = required.difference(raw.columns)
    if missing:
        raise ValueError(f"CICIoV2024 hexadecimal file is missing columns: {sorted(missing)}")
    byte_columns = [f"DATA_{index}" for index in range(8)]
    missing_bytes = [column for column in byte_columns if column not in raw.columns]
    if missing_bytes:
        raise ValueError(f"CICIoV2024 hexadecimal file is missing bytes: {missing_bytes}")
    dlcs = raw["DLC"] if "DLC" in raw.columns else [8] * len(raw)
    payloads = raw[byte_columns].astype(str).agg("".join, axis=1)
    labels = raw["label"].astype(str).str.upper().ne("BENIGN").astype(int)
    mechanism = attack_mechanism_from_text(path.stem if path else "other_attack")
    mechanisms = ["benign" if label == 0 else mechanism for label in labels]
    context = {
        "dataset": "CICIoV2024",
        "vehicle_id": "ford_2019",
        "manufacturer": "Ford",
        "capture_id": f"CICIoV2024:{path.stem if path else 'unknown'}",
        "source_file": path.name if path else "unknown",
        "scenario": "external_dataset",
        "split_role": "external_test",
    }
    return _canonical_from_rows(
        [np.nan] * len(raw), raw["ID"], payloads, labels, dlcs,
        mechanisms=mechanisms, metadata=context,
    )


def parse_candump_log(
    path: Path,
    dataset: str,
    vehicle_id: str,
    manufacturer: str = "unknown",
    limit: Optional[int] = None,
) -> pd.DataFrame:
    """Parse candump-like logs used by CAN-MIRGU and Automotive CAN v2.

    CAN-MIRGU has a trailing 0/1 label. Automotive CAN v2 does not, so its
    ``attack_binary`` remains missing until a verified interval ledger exists.
    """
    timestamps: List[float] = []
    can_ids: List[str] = []
    payloads: List[str] = []
    labels: List[float] = []
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            match = _CANDUMP.match(line.strip())
            if not match:
                continue
            timestamps.append(float(match.group("timestamp")))
            can_ids.append(match.group("can_id"))
            payloads.append(match.group("payload"))
            label = match.group("label")
            labels.append(float(label) if label is not None else np.nan)
            if limit is not None and len(timestamps) >= limit:
                break
    mechanism = attack_mechanism_from_text(path.stem)
    mechanisms = [
        "benign" if not pd.isna(label) and int(label) == 0 else mechanism
        for label in labels
    ]
    context = {
        "dataset": dataset,
        "vehicle_id": vehicle_id,
        "manufacturer": manufacturer,
        "capture_id": f"{vehicle_id}:{path.stem}",
        "source_file": path.name,
        "scenario": "external_dataset",
        "split_role": "external_test",
    }
    return _canonical_from_rows(
        timestamps, can_ids, payloads, labels, mechanisms=mechanisms, metadata=context
    )


def _infer_log_context(path: Path) -> Dict[str, str]:
    text = str(path).replace("\\", "/")
    if "CAN-MIRGU" in text:
        return {"dataset": "CAN-MIRGU", "vehicle_id": "can_mirgu_vehicle", "manufacturer": "unknown"}
    if "Automotive CAN Bus Intrusion Dataset v2-" in text:
        vehicle_folder = next((part for part in path.parts if part in {"OpelAstra", "RenaultClio", "Prototype"}), "unknown")
        return {
            "dataset": "Automotive_CAN_v2",
            "vehicle_id": vehicle_folder.lower(),
            "manufacturer": "Opel" if vehicle_folder == "OpelAstra" else "Renault" if vehicle_folder == "RenaultClio" else "prototype",
        }
    return {"dataset": "unknown", "vehicle_id": "unknown", "manufacturer": "unknown"}


def read_canonical_file(path: Path, nrows: Optional[int] = None) -> pd.DataFrame:
    """Dispatch a supported local file to its canonical adapter."""
    path = Path(path)
    normalized = str(path).replace("\\", "/")
    if "can-train-and-test" in normalized and path.suffix.lower() == ".csv":
        return canonicalize_ctt(pd.read_csv(path, nrows=nrows), path)
    if "CICIoV2024/hexadecimal" in normalized and path.suffix.lower() == ".csv":
        return canonicalize_cici_hex(pd.read_csv(path, nrows=nrows), path)
    if "can-ml" in normalized and path.suffix.lower() == ".csv":
        return canonicalize_can_ml(pd.read_csv(path, nrows=nrows), path)
    if path.suffix.lower() == ".log":
        return parse_candump_log(path, limit=nrows, **_infer_log_context(path))
    raise ValueError(f"Unsupported CAN source file: {path}")


def _sha256_prefix(path: Path, block_size: int = 1_048_576) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        digest.update(handle.read(block_size))
    return digest.hexdigest()


def _count_csv_rows(path: Path, chunksize: int = 250_000) -> int:
    count = 0
    for chunk in pd.read_csv(path, usecols=[0], chunksize=chunksize):
        count += len(chunk)
    return count


def _count_log_rows(path: Path) -> int:
    count = 0
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if _CANDUMP.match(line.strip()):
                count += 1
    return count


def _iter_dataset_files(workspace: Path) -> Iterator[Path]:
    ctt = workspace / "can-train-and-test"
    if ctt.exists():
        yield from sorted(ctt.glob("set_*/*/*.csv"))
    cici = workspace / "CICIoV2024" / "hexadecimal"
    if cici.exists():
        yield from sorted(cici.glob("*.csv"))
    mirgu = workspace / "CAN-MIRGU"
    if mirgu.exists():
        yield from sorted(mirgu.rglob("*.log"))
    automotive = workspace / "Automotive CAN Bus Intrusion Dataset v2-"
    if automotive.exists():
        yield from sorted(automotive.rglob("*.log"))
    can_ml = workspace / "can-ml"
    if can_ml.exists():
        yield from sorted(can_ml.rglob("*.csv"))


def _infer_manifest_context(path: Path) -> Dict[str, Any]:
    normalized = str(path).replace("\\", "/")
    if "can-train-and-test" in normalized:
        return _context_from_ctt_path(path)
    if "CICIoV2024/hexadecimal" in normalized:
        return {
            "dataset": "CICIoV2024", "vehicle_id": "ford_2019", "manufacturer": "Ford",
            "scenario": "external_dataset", "split_role": "external_test",
        }
    if "CAN-MIRGU" in normalized:
        parts = path.parts
        day = next((part for part in parts if part.startswith("Day_")), "attack")
        return {
            "dataset": "CAN-MIRGU", "vehicle_id": "can_mirgu_vehicle", "manufacturer": "unknown",
            "scenario": "external_dataset", "split_role": day,
        }
    if "Automotive CAN Bus Intrusion Dataset v2-" in normalized:
        return {**_infer_log_context(path), "scenario": "external_dataset", "split_role": "external_test"}
    if "can-ml" in normalized:
        vehicle = next((part for part in path.parts if any(token in part.lower() for token in ("impala", "traverse", "silverado", "forester"))), "unknown")
        return {
            "dataset": "can-ml", "vehicle_id": vehicle.lower().replace(" ", "_"), "manufacturer": "unknown",
            "scenario": "multisource_pool", "split_role": "unassigned",
        }
    return {"dataset": "unknown", "vehicle_id": "unknown", "manufacturer": "unknown", "scenario": "unknown", "split_role": "unknown"}


def _sample_file_summary(path: Path, sample_rows: int) -> Dict[str, Any]:
    try:
        frame = read_canonical_file(path, nrows=sample_rows)
        return {
            "parser_status": "ok",
            "schema_columns": ";".join(frame.columns),
            "sample_rows": len(frame),
            "sample_positive_ratio": float(frame["attack_binary"].dropna().mean()) if frame["attack_binary"].notna().any() else np.nan,
            "sample_unique_can_ids": int(frame["can_id_token"].nunique()),
            "sample_timestamp_monotonic": bool(frame["timestamp"].dropna().is_monotonic_increasing) if frame["timestamp"].notna().any() else np.nan,
        }
    except Exception as error:  # record bad input rather than aborting a full audit
        return {
            "parser_status": f"error: {type(error).__name__}: {error}",
            "schema_columns": "",
            "sample_rows": 0,
            "sample_positive_ratio": np.nan,
            "sample_unique_can_ids": np.nan,
            "sample_timestamp_monotonic": np.nan,
        }


def normalize_can_mirgu_metadata(metadata_path: Path) -> pd.DataFrame:
    """Recover CAN-MIRGU's JSON-with-trailing-commas without changing the source."""
    text = metadata_path.read_text(encoding="utf-8", errors="replace")
    cleaned = re.sub(r",\s*([}\]])", r"\1", text)
    data = json.loads(cleaned)
    rows: List[Dict[str, Any]] = []
    for attack_name, metadata in data.items():
        for key, interval in metadata.items():
            if "interval" not in key or not isinstance(interval, list) or len(interval) != 2:
                continue
            rows.append({
                "attack_name": attack_name,
                "interval_field": key,
                "start_timestamp": interval[0],
                "end_timestamp": interval[1],
                "attack_type": metadata.get("attack_type", "unknown"),
                "attack_technique": metadata.get(key.replace("interval", "technique"), metadata.get("attack_technique", "unknown")),
                "attack_mechanism": attack_mechanism_from_text(f"{attack_name} {metadata.get('attack_technique', '')}"),
                "label_source": "CAN-MIRGU Attack/Attacks_metadata.json",
            })
    return pd.DataFrame(rows)


def automotive_label_template(root: Path) -> pd.DataFrame:
    """Create a ledger that must be verified before Automotive CAN v2 scoring."""
    rows: List[Dict[str, Any]] = []
    normal_stems = {"training", "testing", "full_data_capture", "data_capture_70", "data_capture_30"}
    for path in sorted(root.rglob("*.log")):
        if path.stem in normal_stems:
            continue
        vehicle = _infer_log_context(path)["vehicle_id"]
        rows.append({
            "dataset": "Automotive_CAN_v2",
            "vehicle_id": vehicle,
            "source_file": str(path.relative_to(root)).replace("\\", "/"),
            "attack_mechanism": attack_mechanism_from_text(path.stem),
            "start_timestamp": np.nan,
            "end_timestamp": np.nan,
            "label_source": "README interval required",
            "verification_status": "NEEDS_MANUAL_VERIFICATION",
        })
    return pd.DataFrame(rows)


def audit_workspace(
    workspace: Path | str,
    output_dir: Path | str,
    *,
    count_rows: bool = False,
    sample_rows: int = 2_000,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Scan local datasets and write reproducible audit artefacts.

    ``count_rows=False`` is fast and intended for Colab development.  Set it to
    true for the final audit; row counting is streamed and does not load a full
    source file into RAM.
    """
    workspace = Path(workspace)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    records: List[Dict[str, Any]] = []
    for path in _iter_dataset_files(workspace):
        context = _infer_manifest_context(path)
        summary = _sample_file_summary(path, sample_rows)
        if count_rows:
            try:
                row_count = _count_csv_rows(path) if path.suffix.lower() == ".csv" else _count_log_rows(path)
            except Exception as error:
                row_count = np.nan
                summary["parser_status"] = f"{summary['parser_status']}; count error: {error}"
        else:
            row_count = np.nan
        records.append({
            "file_path": str(path.relative_to(workspace)).replace("\\", "/"),
            "file_bytes": path.stat().st_size,
            "row_count": row_count,
            "sha256_prefix_1mb": _sha256_prefix(path),
            "capture_id": context.get("capture_id", path.stem),
            "source_file": path.name,
            "attack_mechanism": attack_mechanism_from_text(path.stem),
            "has_timestamp": "CICIoV2024" not in str(path),
            "has_dlc": "CICIoV2024/hexadecimal" in str(path).replace("\\", "/") or path.suffix.lower() == ".log",
            "label_source": "frame_column" if "can-train-and-test" in str(path) or "CAN-MIRGU" in str(path) or "CICIoV2024" in str(path) else "requires_interval_ledger",
            **context,
            **summary,
        })
    manifest = pd.DataFrame(records)
    if manifest.empty:
        raise FileNotFoundError(f"No supported dataset files found below {workspace}")
    manifest.to_csv(output_dir / "dataset_manifest.csv", index=False)
    dataset_summary = (
        manifest.groupby(["dataset", "vehicle_id", "scenario", "split_role"], dropna=False)
        .agg(files=("file_path", "count"), bytes=("file_bytes", "sum"), rows=("row_count", "sum"), parser_errors=("parser_status", lambda values: sum(not str(value).startswith("ok") for value in values)))
        .reset_index()
    )
    dataset_summary.to_csv(output_dir / "dataset_audit_summary.csv", index=False)
    metadata_path = workspace / "CAN-MIRGU" / "Attack" / "Attacks_metadata.json"
    if metadata_path.exists():
        normalize_can_mirgu_metadata(metadata_path).to_csv(output_dir / "can_mirgu_attack_intervals.csv", index=False)
    automotive_root = workspace / "Automotive CAN Bus Intrusion Dataset v2-"
    if automotive_root.exists():
        automotive_label_template(automotive_root).to_csv(output_dir / "automotive_label_template.csv", index=False)
    return manifest, dataset_summary
