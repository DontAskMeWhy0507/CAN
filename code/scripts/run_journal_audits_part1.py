"""Part 1 CPU audits for journal-grade completeness:
1) CANBERT+/CANLP frame-pooling ablation (max vs top-k vs mean) on saved .frames.f32 scores.
2) Exact model complexity (params, MACs/window, FLOPs/window, checkpoint FP32 MB, H_k state RAM).
3) Unsupervised target-only K=500 comparators (Raw/Structural window-mean Mahalanobis & IsolationForest).
4) Per-file positive/negative window counts and recording-round summary for Condition B & D.
5) Linear probe C-scaling sensitivity across feature groups + full 96-checkpoint probe summary.
"""
from __future__ import annotations
from pathlib import Path
import json
import sys
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest

CODE = Path(r"F:\00_Research\code")
sys.path[:0] = [str(CODE), str(CODE / "src")]

from can_research.metrics import compute_binary_metrics, choose_threshold_on_validation
from can_research.models import CANTransformer
from comparison.data import load_manifest, partitions, mapped
from comparison.adapters import CANLP, CANBERTNetwork
from extensions.content import Features

BASE = CODE / "results/comparison_gpu4_reuse_v1"
CACHE = CODE / "results/comparison_data_v1"
OUT = CODE / "results/journal_grade_completion_2026-11-12"
OUT.mkdir(parents=True, exist_ok=True)

SETS = ["set_01", "set_02", "set_03", "set_04"]
SEEDS = [42, 43, 44]
W_DEDUP = {"set_01": 1 / 3, "set_02": 1 / 6, "set_03": 1 / 6, "set_04": 1 / 3}


def dedup_mean(series_by_set):
    return sum(W_DEDUP[s] * float(series_by_set[s]) for s in SETS)


def pool_scores(frame_scores_2d: np.ndarray, mode: str) -> np.ndarray:
    if mode == "max":
        return frame_scores_2d.max(axis=1)
    if mode == "mean":
        return frame_scores_2d.mean(axis=1)
    if mode == "top8_mean":
        k = min(8, frame_scores_2d.shape[1])
        part = np.partition(frame_scores_2d, -k, axis=1)[:, -k:]
        return part.mean(axis=1)
    raise ValueError(mode)


def run_baseline_pooling_ablation():
    print("[1/5] Running CANBERT+/CANLP frame-pooling ablation from saved .frames.f32...", flush=True)
    raw_csv = OUT / "baseline_pooling_ablation_raw.csv"
    if raw_csv.exists():
        df = pd.read_csv(raw_csv)
    else:
        rows = []
        for method in ["canbertplus", "canlp"]:
            for s in SETS:
                for seed in SEEDS:
                    pred_root = BASE / s / f"seed_{seed}" / method / "attempt_001/predictions"
                    val_files = sorted((pred_root / "validation").glob("*.csv.gz"))
                    val_y, val_frames = [], []
                    for csvp in val_files:
                        df_v = pd.read_csv(csvp)
                        f32p = csvp.with_name(csvp.name.replace(".csv.gz", ".frames.f32"))
                        fs = np.fromfile(f32p, dtype=np.float32).reshape(len(df_v), 64)
                        val_y.append(df_v["y_true"].to_numpy(int))
                        val_frames.append(fs)
                    vy = np.concatenate(val_y)
                    vf = np.concatenate(val_frames, axis=0)

                    cond_data = {}
                    for cond in ["A", "B", "C", "D"]:
                        cfiles = sorted((pred_root / cond).glob("*.csv.gz"))
                        cy, cf, caps = [], [], []
                        for csvp in cfiles:
                            df_c = pd.read_csv(csvp)
                            f32p = csvp.with_name(csvp.name.replace(".csv.gz", ".frames.f32"))
                            fs = np.fromfile(f32p, dtype=np.float32).reshape(len(df_c), 64)
                            y_arr = df_c["y_true"].to_numpy(int)
                            cy.append(y_arr)
                            cf.append(fs)
                            caps.append((y_arr, fs))
                        cond_data[cond] = (np.concatenate(cy), np.concatenate(cf, axis=0), caps)

                    for mode in ["max", "top8_mean", "mean"]:
                        vs = pool_scores(vf, mode)
                        tau = choose_threshold_on_validation(vy, vs, 100.0)
                        for cond in ["A", "B", "C", "D"]:
                            cy, cf, caps = cond_data[cond]
                            cs = pool_scores(cf, mode)
                            m = compute_binary_metrics(cy, y_score=cs, threshold=tau)
                            rows.append({
                                "method": method, "pool": mode, "set": s, "seed": seed,
                                "condition": cond, "threshold": tau, **m,
                            })
                        if mode in ["max", "mean"]:
                            for cond in ["B", "D"]:
                                _, _, caps = cond_data[cond]
                                wp, ey, es = [], [], []
                                for y_arr, fs in caps:
                                    sc = pool_scores(fs, mode)
                                    idx = np.where(y_arr == 1)[0]
                                    prefix_end = int(idx[0]) if len(idx) > 0 else len(y_arr)
                                    k = min(500, prefix_end // 2)
                                    wp.append(sc[:k])
                                    ey.append(y_arr[k:])
                                    es.append(sc[k:])
                                tau_k = float(np.quantile(np.concatenate(wp), 0.99))
                                m_k = compute_binary_metrics(np.concatenate(ey), y_score=np.concatenate(es), threshold=tau_k)
                                rows.append({
                                    "method": f"{method}_cal500_1pct", "pool": mode, "set": s, "seed": seed,
                                    "condition": cond, "threshold": tau_k, **m_k,
                                })
        df = pd.DataFrame(rows)
        df.to_csv(raw_csv, index=False)
    set_avg = df.groupby(["method", "pool", "condition", "set"], as_index=False)[["Recall", "FAR_per_100k", "Attack_F1", "AP"]].mean()
    summary = set_avg.groupby(["method", "pool", "condition"], as_index=False)[["Recall", "FAR_per_100k", "Attack_F1", "AP"]].mean()
    summary.to_csv(OUT / "baseline_pooling_ablation_summary.csv", index=False)
    print(summary.to_string(index=False), flush=True)


def transformer_macs_per_window(input_dim: int, w: int = 64, d_model: int = 64, n_layers: int = 2, n_heads: int = 4, ff_dim: int = 128) -> dict:
    m = CANTransformer(in_features=input_dim, window_size=w, d_model=d_model, num_layers=n_layers, nhead=n_heads, dim_feedforward=ff_dim)
    params = sum(p.numel() for p in m.parameters())
    # Exact analytical MACs for forward pass of batch=1 window length W:
    # 1) Input linear projection: W * input_dim * d_model
    macs = w * input_dim * d_model
    # 2) Per TransformerEncoderLayer (PyTorch MultiheadAttention + 2-layer FFN):
    #    - In-proj (Q,K,V): W * d_model * (3 * d_model)
    #    - Q*K^T: n_heads * (W * W * (d_model // n_heads)) = W^2 * d_model
    #    - Attn * V: n_heads * (W * W * (d_model // n_heads)) = W^2 * d_model
    #    - Out-proj: W * d_model * d_model
    #    - FFN (d_model -> ff_dim -> d_model): W * d_model * ff_dim + W * ff_dim * d_model
    per_layer = w * d_model * (3 * d_model) + 2 * (w * w * d_model) + w * d_model * d_model + 2 * w * d_model * ff_dim
    macs += n_layers * per_layer
    # 3) Classifier head: Linear(64, 32) + Linear(32, 2)
    macs += d_model * 32 + 32 * 2
    return {
        "params": int(params),
        "macs_per_window": int(macs),
        "flops_per_window": int(2 * macs),
        "fp32_weights_kb": round(params * 4 / 1024.0, 2),
    }


def run_complexity_audit():
    print("[2/5] Computing exact params, MACs/FLOPs, weights MB, and H_k RAM...", flush=True)
    variants = [
        ("Raw Transformer", 28, False),
        ("Structural Transformer", 30, True),
        ("Raw-no-ID", 17, False),
        ("ID-only", 11, False),
        ("Raw + Structural", 41, True),
        ("Structural-no-payload", 22, True),
        ("Structural-no-delta", 21, False),
        ("Structural-no-local", 27, True),
        ("Structural-no-rank-W", 29, True),
        ("Structural-no-transition", 29, True),
    ]
    rows = []
    # H_k memory per tracked ID in classic 11-bit CAN (2048 max active IDs):
    # bool seen[2048] (2 KB) + float32 payload[2048,8] (64 KB) + float32 mask[2048,8] (64 KB) = 130 KB fixed table
    hk_fixed_kb = round((2048 * (1 + 8 * 4 + 8 * 4)) / 1024.0, 2)
    for name, dim, uses_hk in variants:
        stats = transformer_macs_per_window(dim, w=64)
        rows.append({
            "model": name,
            "input_dim": dim,
            **stats,
            "hk_state_kb": hk_fixed_kb if uses_hk else 0.0,
        })

    # CANLP: empirical dims across 4 sets (check checkpoint in comparison_gpu4_reuse_v1)
    canlp_dims = []
    canlp_params = []
    for s in SETS:
        cp = torch.load(BASE / s / "seed_42/canlp/attempt_001/checkpoint.pt", map_location="cpu", weights_only=False)
        mod = cp["model"] if isinstance(cp, dict) and "model" in cp else cp.model if hasattr(cp, "model") else cp
        first_lin = next(m for m in mod.modules() if isinstance(m, nn.Linear))
        d_in = first_lin.in_features
        p_cnt = sum(p.numel() for p in mod.parameters())
        canlp_dims.append(d_in)
        canlp_params.append(p_cnt)
    mean_d = int(round(np.mean(canlp_dims)))
    mean_p = int(round(np.mean(canlp_params)))
    # 64 frames passed through Linear(d_in,128)->Linear(128,64)->Linear(64,2)
    canlp_macs = 64 * (mean_d * 128 + 128 * 64 + 64 * 2)
    rows.append({
        "model": f"CANLP-char-DNN adapted (range d={min(canlp_dims)}-{max(canlp_dims)})",
        "input_dim": mean_d,
        "params": mean_p,
        "macs_per_window": int(canlp_macs),
        "flops_per_window": int(2 * canlp_macs),
        "fp32_weights_kb": round(mean_p * 4 / 1024.0, 2),
        "hk_state_kb": 0.0,
    })

    # CANBERT+: inspect checkpoint Set 1 seed 42
    from comparison.adapters import upstream_bert
    upstream_bert()
    cb = torch.load(BASE / "set_01/seed_42/canbertplus/attempt_001/checkpoint.pt", map_location="cpu", weights_only=False)
    cb_mod = cb.model
    cb_params = sum(p.numel() for p in cb_mod.parameters())
    # Per-frame BERT (seq_len=10 tokens per CAN frame), evaluated over W=64 frames/window:
    d_b, ff_b, L_b, S_tok, W_b = 768, 3072, 6, 10, 64
    v_id = cb_mod.classifier.in_features
    per_frame_macs = L_b * (S_tok * d_b * (3 * d_b) + 2 * (S_tok * S_tok * d_b) + S_tok * d_b * d_b + 2 * S_tok * d_b * ff_b) + d_b * v_id + v_id * 2
    cb_macs = W_b * per_frame_macs
    rows.append({
        "model": "CANBERT+ adapted (Set 1 vocab)",
        "input_dim": 10,
        "params": int(cb_params),
        "macs_per_window": int(cb_macs),
        "flops_per_window": int(2 * cb_macs),
        "fp32_weights_kb": round(cb_params * 4 / 1024.0, 2),
        "hk_state_kb": 0.0,
    })
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "model_complexity_audit.csv", index=False)
    print(df.to_string(index=False), flush=True)


def run_target_only_k500_comparator():
    print("[3/5] Running target-only K=500 unsupervised comparators (0 source training)...", flush=True)
    manifest = load_manifest(CACHE, verify=False)
    rows = []
    for s in SETS:
        sp = partitions(manifest, s)
        for cond in ["B", "D"]:
            caps = []
            for e in sp[cond]:
                a = mapped(CACHE, e)
                w = 64
                n = (e["frames"] // w) * w
                a_w = a[:n]
                f = Features(64)
                raw, st = f.feed(a_w)
                y = np.asarray(a_w["label"]).reshape(-1, 64).max(1)
                # Window-level summary vectors (mean + std = 60D structural, 56D raw)
                x_st = np.concatenate([st.mean(axis=1), st.std(axis=1)], axis=1)
                x_raw = np.concatenate([raw.mean(axis=1), raw.std(axis=1)], axis=1)
                idx = np.where(y == 1)[0]
                prefix_end = int(idx[0]) if len(idx) > 0 else len(y)
                k = min(500, prefix_end // 2)
                caps.append({"file": e["source"], "k": k, "y": y, "x_st": x_st, "x_raw": x_raw})

            for rep_name, key in [("target_only_mahal_raw56", "x_raw"), ("target_only_mahal_st60", "x_st")]:
                w_pool = np.concatenate([c[key][:c["k"]] for c in caps], axis=0)
                mu = w_pool.mean(axis=0)
                sd = np.maximum(w_pool.std(axis=0), 1e-4)
                z_w = np.clip((w_pool - mu) / sd, -10.0, 10.0)
                cov = np.cov(z_w, rowvar=False)
                cov = 0.9 * cov + 0.1 * np.eye(cov.shape[0])
                inv_cov = np.linalg.pinv(cov)
                # Score warmup using leave-half or in-sample? Mirror exact quantile convention on warmup energy
                e_warm = np.einsum("ij,jk,ik->i", z_w, inv_cov, z_w)
                # Evaluate strictly on post-warmup slices
                ey = np.concatenate([c["y"][c["k"]:] for c in caps])
                ex = np.concatenate([c[key][c["k"]:] for c in caps], axis=0)
                z_e = np.clip((ex - mu) / sd, -10.0, 10.0)
                es = np.einsum("ij,jk,ik->i", z_e, inv_cov, z_e)
                for budget, q in [(100, 0.999), (1000, 0.99)]:
                    tau = float(np.quantile(e_warm, q))
                    m = compute_binary_metrics(ey, y_score=es, threshold=tau)
                    rows.append({"method": rep_name, "condition": cond, "set": s, "budget_far_100k": budget, **m})

            # IsolationForest on Structural 60D window summary fit purely on target warmup K=500
            w_st = np.concatenate([c["x_st"][:c["k"]] for c in caps], axis=0)
            mu = w_st.mean(axis=0); sd = np.maximum(w_st.std(axis=0), 1e-4)
            iso = IsolationForest(n_estimators=200, random_state=42, n_jobs=-1)
            iso.fit((w_st - mu) / sd)
            warm_score = -iso.score_samples((w_st - mu) / sd)
            ey = np.concatenate([c["y"][c["k"]:] for c in caps])
            ex = np.concatenate([c["x_st"][c["k"]:] for c in caps], axis=0)
            es = -iso.score_samples((ex - mu) / sd)
            for budget, q in [(100, 0.999), (1000, 0.99)]:
                tau = float(np.quantile(warm_score, q))
                m = compute_binary_metrics(ey, y_score=es, threshold=tau)
                rows.append({"method": "target_only_isoforest_st60", "condition": cond, "set": s, "budget_far_100k": budget, **m})

    df = pd.DataFrame(rows)
    df.to_csv(OUT / "target_only_k500_per_set.csv", index=False)
    sum_rows = []
    for (meth, cond, bud), g in df.groupby(["method", "condition", "budget_far_100k"]):
        by_s = g.set_index("set")
        sum_rows.append({
            "method": meth, "condition": cond, "budget_pct": bud / 1000.0,
            "recall_4set": float(g["Recall"].mean()),
            "recall_3veh": dedup_mean(by_s["Recall"]),
            "far_pct_4set": float(g["FAR_per_100k"].mean() / 1000.0),
            "f1_4set": float(g["Attack_F1"].mean()),
            "ap_4set": float(g["AP"].mean()),
            "ap_3veh": dedup_mean(by_s["AP"]),
        })
    sdf = pd.DataFrame(sum_rows)
    sdf.to_csv(OUT / "target_only_k500_summary.csv", index=False)
    print(sdf.to_string(index=False), flush=True)


def run_per_file_and_probe_audits():
    print("[4/5] Extracting per-file B/D counts and C-scaling linear probes...", flush=True)
    # Per-file counts in Condition B & D
    manifest = load_manifest(CACHE, verify=False)
    f_rows = []
    for s in SETS:
        sp = partitions(manifest, s)
        for cond in ["B", "D"]:
            for e in sp[cond]:
                a = mapped(CACHE, e)
                w_tot = e["frames"] // 64
                y = np.asarray(a[:w_tot * 64]["label"]).reshape(-1, 64).max(1)
                n_pos = int((y == 1).sum())
                n_neg = int((y == 0).sum())
                f_rows.append({
                    "set": s, "condition": cond, "file": Path(e["source"]).name,
                    "windows": int(w_tot), "pos_windows": n_pos, "neg_windows": n_neg,
                    "pos_rate_pct": round(100.0 * n_pos / w_tot, 2),
                })
    fdf = pd.DataFrame(f_rows)
    fdf.to_csv(OUT / "bd_per_file_counts.csv", index=False)
    print(fdf.groupby(["set", "condition"])[["windows", "pos_windows", "neg_windows"]].agg(["count", "sum", "min", "median", "max"]), flush=True)

    # C-scaling on cached_probe_data.npz
    d = np.load(CODE / "results/structural_leakage_diagnosis_2026-11-11/cached_probe_data.npz")
    tr_st, va_st = d["train_st"], d["val_st"]
    tr_yv, va_yv = d["train_v"], d["val_v"]
    tr_ya, va_ya = d["train_y"], d["val_y"]
    groups = {
        "all_30D (1920)": list(range(30)),
        "dlc_and_masks_10D (640)": [0] + list(range(9, 17)) + [25],
        "dlc_masks_9D (576)": [0] + list(range(9, 17)),
        "has_prev_1D (64)": [25],
        "local_stats_3D (192)": [26, 27, 28],
        "payload_8D (512)": list(range(1, 9)),
        "delta_8D (512)": list(range(17, 25)),
        "transition_1D (64)": [29],
    }
    from sklearn.metrics import balanced_accuracy_score
    c_rows = []
    for gname, cols in groups.items():
        Xtr = tr_st[:, :, cols].reshape(len(tr_st), -1)
        Xva = va_st[:, :, cols].reshape(len(va_st), -1)
        for C in [0.01, 0.1, 1.0, 10.0]:
            row = {"group": gname, "flat_dim": Xtr.shape[1], "C": C}
            for tname, ytr, yva in [("vehicle_ba", tr_yv, va_yv), ("attack_ba", tr_ya, va_ya)]:
                clf = make_pipeline(StandardScaler(), LogisticRegression(C=C, max_iter=2000, random_state=42))
                clf.fit(Xtr, ytr)
                row[tname] = float(balanced_accuracy_score(yva, clf.predict(Xva)))
            c_rows.append(row)
    cdf = pd.DataFrame(c_rows)
    cdf.to_csv(OUT / "probe_c_scaling.csv", index=False)
    print(cdf.pivot(index="group", columns="C", values="vehicle_ba").round(4), flush=True)

    # Full 96+24 checkpoint probe summary
    df_p = pd.read_csv(CODE / "results/structural_leakage_diagnosis_2026-11-11/ablation_encoder_probes.csv")
    p_piv = df_p.pivot_table(index="representation", columns="target", values="learned_ba", aggfunc=["mean", "std"]).round(4)
    p_piv.to_csv(OUT / "ablation_96ckpt_probe_summary.csv")
    print("[5/5] Saved 96+24 checkpoint probe summary.", flush=True)


if __name__ == "__main__":
    run_baseline_pooling_ablation()
    run_complexity_audit()
    run_target_only_k500_comparator()
    run_per_file_and_probe_audits()
    print("ALL PART 1 AUDITS COMPLETE.", flush=True)
