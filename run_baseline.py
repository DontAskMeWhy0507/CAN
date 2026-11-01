"""Script chạy baseline Phase 1 theo quy chuẩn Frozen Research Protocol (README.md).

Sử dụng:
    python run_baseline.py --set set_01
    python run_baseline.py --all
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

try:
    from xgboost import XGBClassifier
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False

from can_research.preprocess import (
    compute_ctt_metrics,
    compute_shift_effects,
    extract_windows_from_df,
    load_balanced_train_windows,
)


WINDOW_SIZE = 64


def evaluate_on_ctt_windows(
    model,
    test_folder: Path,
    chunksize: int = 128000,
    max_chunks_per_file: int | None = None,
) -> dict:
    """Đọc streaming theo chunk để quét toàn bộ file mà không tràn RAM."""
    y_true_all, y_pred_all, y_prob_all = [], [], []
    files = sorted(test_folder.glob("*.csv"))
    for f in files:
        chunk_idx = 0
        for chunk in pd.read_csv(f, chunksize=chunksize):
            X_w, y_w = extract_windows_from_df(chunk, window_size=WINDOW_SIZE, flatten=True)
            if len(y_w) == 0:
                continue
            preds = model.predict(X_w)
            probs = model.predict_proba(X_w)[:, 1] if hasattr(model, "predict_proba") else preds
            y_true_all.extend(y_w)
            y_pred_all.extend(preds)
            y_prob_all.extend(probs)
            chunk_idx += 1
            if max_chunks_per_file and chunk_idx >= max_chunks_per_file:
                break

    return compute_ctt_metrics(y_true_all, y_pred_all, y_prob_all)


def run_set_benchmark(
    set_name: str,
    data_dir: Path,
    results_dir: Path,
    max_train_windows_per_file: int = 1000,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Chạy toàn bộ thí nghiệm cho 1 set (A, B, C, D) với Logistic Regression và XGBoost."""
    set_dir = data_dir / set_name
    if not set_dir.exists():
        raise FileNotFoundError(f"Không tìm thấy thư mục: {set_dir}")

    print(f"\n{'='*60}")
    print(f"RUNNING BENCHMARK FOR: {set_name.upper()}")
    print(f"{'='*60}")

    train_folder = set_dir / "train_01"
    test_conditions = {
        "A: Known V + Known A": set_dir / "test_01_known_vehicle_known_attack",
        "B: Unknown V + Known A": set_dir / "test_02_unknown_vehicle_known_attack",
        "C: Known V + Unknown A": set_dir / "test_03_known_vehicle_unknown_attack",
        "D: Unknown V + Unknown A": set_dir / "test_04_unknown_vehicle_unknown_attack",
    }

    # 1. Load and normalize train set
    print(f"[{set_name}] Loading train_01 data (Class-balanced sampling)...")
    X_train, y_train = load_balanced_train_windows(
        train_folder,
        window_size=WINDOW_SIZE,
        max_windows_per_file=max_train_windows_per_file,
        flatten=True,
    )
    print(f"[{set_name}] Train shape: {X_train.shape} (Attack windows: {(y_train == 1).sum()})")

    models = {
        "LogisticRegression": LogisticRegression(max_iter=1000, C=1.0, random_state=42),
    }
    if HAS_XGBOOST:
        models["XGBoost"] = XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            eval_metric="logloss",
            random_state=42,
            n_jobs=-1,
        )

    all_metrics_records = []
    all_shift_records = []

    for model_name, model in models.items():
        print(f"\n--- Training model: {model_name} ---")
        model.fit(X_train, y_train)
        print(f"Training {model_name} done. Evaluating streaming on 4 test conditions...")

        model_records = []
        for cond_name, folder_path in test_conditions.items():
            metrics = evaluate_on_ctt_windows(model, folder_path, chunksize=128000)
            metrics["Set"] = set_name
            metrics["Model"] = model_name
            metrics["Condition"] = cond_name
            model_records.append(metrics)
            all_metrics_records.append(metrics)
            print(f"[{set_name} | {model_name}] {cond_name} -> F1: {metrics['Attack_F1']:.4f} | PR-AUC: {metrics['PR_AUC']:.4f} | FAR/100k: {metrics['FAR_per_100k']}")

        df_model_metrics = pd.DataFrame(model_records)
        df_shifts = compute_shift_effects(df_model_metrics)
        df_shifts["Set"] = set_name
        df_shifts["Model"] = model_name
        all_shift_records.append(df_shifts)

    df_all_metrics = pd.DataFrame(all_metrics_records)
    df_all_shifts = pd.concat(all_shift_records, ignore_index=True)

    # Save results
    results_dir.mkdir(parents=True, exist_ok=True)
    df_all_metrics.to_csv(results_dir / f"metrics_{set_name}.csv", index=False)
    df_all_shifts.to_csv(results_dir / f"shifts_{set_name}.csv", index=False)
    print(f"\nSaved results to: {results_dir}/metrics_{set_name}.csv")

    return df_all_metrics, df_all_shifts


def main():
    parser = argparse.ArgumentParser(description="CAN Intrusion Detection Phase 1 Baseline Benchmark")
    parser.add_argument("--set", type=str, default="set_01", choices=["set_01", "set_02", "set_03", "set_04"], help="Name of set to run")
    parser.add_argument("--all", action="store_true", help="Run all 4 sets (set_01 to set_04)")
    parser.add_argument("--data-dir", type=str, default="can-train-and-test", help="Directory containing datasets")
    parser.add_argument("--results-dir", type=str, default="results", help="Directory to save results")
    parser.add_argument("--max-train-windows-per-file", type=int, default=1000, help="Maximum train windows per file")

    args = parser.parse_args()
    data_dir = Path(args.data_dir)
    results_dir = Path(args.results_dir)

    sets_to_run = ["set_01", "set_02", "set_03", "set_04"] if args.all else [args.set]

    total_metrics = []
    total_shifts = []

    for s in sets_to_run:
        df_m, df_s = run_set_benchmark(s, data_dir, results_dir, args.max_train_windows_per_file)
        total_metrics.append(df_m)
        total_shifts.append(df_s)

    if len(sets_to_run) > 1:
        df_master_metrics = pd.concat(total_metrics, ignore_index=True)
        df_master_shifts = pd.concat(total_shifts, ignore_index=True)
        df_master_metrics.to_csv(results_dir / "phase1_master_benchmark.csv", index=False)
        df_master_shifts.to_csv(results_dir / "phase1_master_shifts.csv", index=False)
        print("\n" + "="*60)
        print("COMPLETED ALL 4 SETS FOR PHASE 1!")
        print(f"Master benchmark saved to: {results_dir}/phase1_master_benchmark.csv")
        print("="*60)


if __name__ == "__main__":
    main()
