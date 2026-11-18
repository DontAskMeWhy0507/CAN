"""Part 2 GPU+CPU experiments for journal-grade completeness (R3, R5, R6):
1) Strictly monotonic CTT subset (136/236 files, timestamp_inversions == 0):
   Timed (Raw 29D, Structural 32D with logdt & logdt_id) vs Content (Raw 28D, Structural 30D)
   across 4 sets x 3 seeds, evaluated at both source threshold (100/100k) and K=500 benign warmup.
2) Frame-equated window sensitivity (64,000 frames/file/class):
   W=32 (cap=2000) & W=128 (cap=500) across 4 sets x 3 seeds, with frame-equated K_frames=32,000 warmup calibration.
3) Multi-seed reservoir sampling variance:
   sampling_seed in {20261103, 20261104, 20261105} across 4 sets (model seed=42).
4) Diagnostic CrySyS-AssocRules remediation check on Set 1:
   Saved predictions under K=500/1% target calibration + full contiguous benign stream refit.
"""
from __future__ import annotations
from pathlib import Path
import hashlib
import json
import sys
import time
import numpy as np
import pandas as pd
import torch

CODE = Path(r"F:\00_Research\code")
sys.path[:0] = [str(CODE), str(CODE / "src")]

from comparison.data import load_manifest, partitions, mapped, batches as c_batches, sample as c_sample
from comparison.adapters import AssocRules, frame_table
from extensions.content import Features
from can_research.models import train_transformer, predict_scores
from can_research.metrics import compute_binary_metrics, choose_threshold_on_validation

CACHE = CODE / "results/comparison_data_v1"
BASE = CODE / "results/comparison_gpu4_reuse_v1"
OUT = CODE / "results/journal_grade_completion_2026-11-12"
OUT.mkdir(parents=True, exist_ok=True)

with open(CODE / "comparison/config.json", "r", encoding="utf-8") as fh:
    CFG = json.load(fh)

SETS = ["set_01", "set_02", "set_03", "set_04"]
SEEDS = [42, 43, 44]
W_DEDUP = {"set_01": 1 / 3, "set_02": 1 / 6, "set_03": 1 / 6, "set_04": 1 / 3}


def dedup_mean(series_by_set):
    return sum(W_DEDUP[s] * float(series_by_set[s]) for s in SETS)


def extract_file_features(entry, w: int = 64, tier: str = "content", batch_windows: int = 1024):
    """Exact chronological extraction of (raw, structural, y) for any W and tier."""
    a = mapped(CACHE, entry)
    n_win = int(entry["frames"] // w)
    total_frames = n_win * w
    raw_parts, st_parts, y_parts = [], [], []
    f_ext = Features(w)
    if tier == "timed":
        if entry.get("timestamp_inversions", 0) != 0:
            raise ValueError(f"Non-monotonic file {entry['source']} passed to timed extractor")
        ts = np.asarray(a[:total_frames]["timestamp"], dtype=np.float64)
        cids = np.asarray(a[:total_frames]["cid"], dtype=np.int64)
        dt = np.empty(total_frames, dtype=np.float64)
        dt[0] = 0.0
        dt[1:] = ts[1:] - ts[:-1]
        logdt_all = np.log1p(1000.0 * np.minimum(np.maximum(dt, 0.0), 10.0)).astype(np.float32)
        dt_id = np.zeros(total_frames, dtype=np.float64)
        for cid in np.unique(cids):
            ix = np.flatnonzero(cids == cid)
            if len(ix) > 1:
                dt_id[ix[1:]] = ts[ix[1:]] - ts[ix[:-1]]
        logdt_id_all = np.log1p(1000.0 * np.minimum(np.maximum(dt_id, 0.0), 10.0)).astype(np.float32)

    for start in range(0, n_win, batch_windows):
        end = min(start + batch_windows, n_win)
        r = a[start * w : end * w]
        raw28, st30 = f_ext.feed(r)
        yb = np.asarray(r["label"]).reshape(end - start, w).max(1).astype(np.int64)
        if tier == "timed":
            ldt = logdt_all[start * w : end * w].reshape(end - start, w, 1)
            ldti = logdt_id_all[start * w : end * w].reshape(end - start, w, 1)
            raw_b = np.concatenate([raw28, ldt], axis=-1)
            st_b = np.concatenate([st30[..., :26], ldt, ldti, st30[..., 26:]], axis=-1)
        else:
            raw_b, st_b = raw28, st30
        raw_parts.append(raw_b)
        st_parts.append(st_b)
        y_parts.append(yb)
    return (
        np.concatenate(raw_parts, axis=0),
        np.concatenate(st_parts, axis=0),
        np.concatenate(y_parts, axis=0),
    )


def verify_vectorized_timed(manifest):
    """Cross-verify fast timed extractor against official WindowExtractor(64, 'timed') on first 512 windows."""
    mono_e = next(x for x in partitions(manifest, "set_01")["train"] if x.get("timestamp_inversions", 0) == 0)
    raw_fast, st_fast, y_fast = extract_file_features(mono_e, w=64, tier="timed")
    ref_raw, ref_st, ref_y = [], [], []
    for i, b in enumerate(c_batches(CACHE, mono_e, batch_windows=128, features=True, tier="timed")):
        ref_raw.append(b["raw"])
        ref_st.append(b["structural"])
        ref_y.append(b["y"])
        if i >= 3:
            break
    rr = np.concatenate(ref_raw, axis=0)
    rs = np.concatenate(ref_st, axis=0)
    ry = np.concatenate(ref_y, axis=0)
    n = len(ry)
    d_raw = float(np.max(np.abs(raw_fast[:n] - rr)))
    d_st = float(np.max(np.abs(st_fast[:n] - rs)))
    assert np.array_equal(y_fast[:n], ry), "Label alignment mismatch!"
    assert d_raw < 1e-6 and d_st < 1e-6, f"Timed extractor mismatch: d_raw={d_raw}, d_st={d_st}"
    print(f"[Verified] Vectorized timed extractor bit-exact vs WindowExtractor (max diff raw={d_raw:.2e}, st={d_st:.2e})", flush=True)


def sample_w(entries, w: int = 64, cap: int = 1000, sampling_seed: int = 20261103):
    selected = {}
    for e in entries:
        a = mapped(CACHE, e)
        n_win = int(e["frames"] // w)
        y = np.asarray(a["label"][: n_win * w]).reshape(n_win, w).max(1)
        token = f"{sampling_seed}:{Path(e['source']).name}"
        file_seed = int.from_bytes(hashlib.sha256(token.encode()).digest()[:8], "little")
        take = []
        for cls in [0, 1]:
            indices = np.flatnonzero(y == cls)
            rng = np.random.default_rng(np.random.SeedSequence([file_seed, cls]))
            take.extend(indices[np.argsort(rng.random(len(indices)), kind="stable")[:cap]].tolist())
        selected[e["source"]] = sorted(take)
    return selected


def build_train_pool(entries, w: int, cap: int, tier: str = "content", sampling_seed: int = 20261103):
    sel = sample_w(entries, w=w, cap=cap, sampling_seed=sampling_seed)
    r_list, s_list, y_list = [], [], []
    for e in entries:
        ix = sel[e["source"]]
        if not ix:
            continue
        raw, st, y = extract_file_features(e, w=w, tier=tier)
        r_list.append(raw[ix])
        s_list.append(st[ix])
        y_list.append(y[ix])
    return np.concatenate(r_list, axis=0), np.concatenate(s_list, axis=0), np.concatenate(y_list, axis=0)


def eval_with_warmup(scores_by_file, y_by_file, k_target: int):
    results = {}
    wp, ey, es = [], [], []
    for y_arr, sc_arr in zip(y_by_file, scores_by_file):
        idx = np.where(y_arr == 1)[0]
        prefix_end = int(idx[0]) if len(idx) > 0 else len(y_arr)
        k = min(k_target, prefix_end // 2)
        wp.append(sc_arr[:k])
        ey.append(y_arr[k:])
        es.append(sc_arr[k:])
    warm = np.concatenate(wp)
    ey_all = np.concatenate(ey)
    es_all = np.concatenate(es)
    for label, q in [("cal_0p1", 0.999), ("cal_1p0", 0.99)]:
        tau = float(np.quantile(warm, q))
        m = compute_binary_metrics(ey_all, y_score=es_all, threshold=tau)
        results[label] = m
    return results


def exp_monotonic_timed_vs_content(manifest):
    out_raw = OUT / "monotonic_timed_vs_content_raw.csv"
    if out_raw.exists():
        print("[1/4] Skipping monotonic timed vs content (already exists).", flush=True)
        return
    print("[1/4] Running strictly monotonic (136/236 files) Timed vs Content (4 sets x 3 seeds)...", flush=True)
    verify_vectorized_timed(manifest)
    rows = []
    for s in SETS:
        sp = partitions(manifest, s)
        mono = {k: [e for e in sp[k] if e.get("timestamp_inversions", 0) == 0] for k in ["train", "validation", "A", "B", "C", "D"]}
        counts = {k: len(v) for k, v in mono.items()}
        print(f"  {s} mono files: {counts}", flush=True)
        # Pre-extract content & timed arrays once per set
        cache_eval = {}
        for tier in ["content", "timed"]:
            tr_r, tr_s, tr_y = build_train_pool(mono["train"], w=64, cap=1000, tier=tier, sampling_seed=20261103)
            eval_data = {}
            for cond in ["validation", "A", "B", "C", "D"]:
                eval_data[cond] = [extract_file_features(e, w=64, tier=tier) for e in mono[cond]]
            cache_eval[tier] = (tr_r, tr_s, tr_y, eval_data)

        cfg = dict(CFG, window_size=64)
        for seed in SEEDS:
            for tier in ["content", "timed"]:
                tr_r, tr_s, tr_y, eval_data = cache_eval[tier]
                for rep, x_tr, feat_idx in [("raw", tr_r, 0), ("structural", tr_s, 1)]:
                    t0 = time.perf_counter()
                    model, _ = train_transformer(x_tr, tr_y, cfg, seed, "cuda")
                    fit_s = time.perf_counter() - t0
                    vy = np.concatenate([tpl[2] for tpl in eval_data["validation"]])
                    vs = np.concatenate([predict_scores(model, tpl[feat_idx], "cuda", 256) for tpl in eval_data["validation"]])
                    tau_src = choose_threshold_on_validation(vy, vs, 100.0)
                    for cond in ["A", "B", "C", "D"]:
                        cy_list = [tpl[2] for tpl in eval_data[cond]]
                        cs_list = [predict_scores(model, tpl[feat_idx], "cuda", 256) for tpl in eval_data[cond]]
                        cy = np.concatenate(cy_list)
                        cs = np.concatenate(cs_list)
                        m_src = compute_binary_metrics(cy, y_score=cs, threshold=tau_src)
                        rows.append({
                            "set": s, "seed": seed, "tier": tier, "method": rep, "mode": "source_thresh",
                            "condition": cond, "fit_sec": round(fit_s, 2), **m_src,
                        })
                        if cond in ["B", "D"]:
                            cal = eval_with_warmup(cs_list, cy_list, k_target=500)
                            for cname, cm in cal.items():
                                rows.append({
                                    "set": s, "seed": seed, "tier": tier, "method": rep, "mode": cname,
                                    "condition": cond, "fit_sec": round(fit_s, 2), **cm,
                                })
                    del model
                    torch.cuda.empty_cache()
            print(f"  Completed monotonic {s} seed {seed}", flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(out_raw, index=False)
    set_avg = df.groupby(["tier", "method", "mode", "condition", "set"], as_index=False)[["Recall", "FAR_per_100k", "Attack_F1", "AP"]].mean()
    sum_rows = []
    for (tier, meth, mode, cond), g in set_avg.groupby(["tier", "method", "mode", "condition"]):
        by_s = g.set_index("set")
        sum_rows.append({
            "tier": tier, "method": meth, "mode": mode, "condition": cond,
            "recall_4set": float(g["Recall"].mean()), "recall_3veh": dedup_mean(by_s["Recall"]),
            "far_pct_4set": float(g["FAR_per_100k"].mean() / 1000.0),
            "f1_4set": float(g["Attack_F1"].mean()), "ap_4set": float(g["AP"].mean()),
            "ap_3veh": dedup_mean(by_s["AP"]),
        })
    sdf = pd.DataFrame(sum_rows)
    sdf.to_csv(OUT / "monotonic_timed_vs_content_summary.csv", index=False)
    print(sdf.to_string(index=False), flush=True)


def exp_frame_equated_windows(manifest):
    out_raw = OUT / "frame_equated_windows_raw.csv"
    if out_raw.exists():
        print("[2/4] Skipping frame-equated windows (already exists).", flush=True)
        return
    print("[2/4] Running frame-equated W=32 (cap=2000) & W=128 (cap=500) across 4 sets x 3 seeds...", flush=True)
    rows = []
    for w, cap, k_warm in [(32, 2000, 1000), (128, 500, 250)]:
        cfg = dict(CFG, window_size=w)
        for s in SETS:
            sp = partitions(manifest, s)
            tr_r, tr_s, tr_y = build_train_pool(sp["train"], w=w, cap=cap, tier="content", sampling_seed=20261103)
            eval_data = {cond: [extract_file_features(e, w=w, tier="content") for e in sp[cond]] for cond in ["validation", "A", "B", "C", "D"]}
            for seed in SEEDS:
                for rep, x_tr, feat_idx in [("raw", tr_r, 0), ("structural", tr_s, 1)]:
                    model, _ = train_transformer(x_tr, tr_y, cfg, seed, "cuda")
                    vy = np.concatenate([tpl[2] for tpl in eval_data["validation"]])
                    vs = np.concatenate([predict_scores(model, tpl[feat_idx], "cuda", 256) for tpl in eval_data["validation"]])
                    tau_src = choose_threshold_on_validation(vy, vs, 100.0)
                    for cond in ["A", "B", "C", "D"]:
                        cy_list = [tpl[2] for tpl in eval_data[cond]]
                        cs_list = [predict_scores(model, tpl[feat_idx], "cuda", 256) for tpl in eval_data[cond]]
                        cy = np.concatenate(cy_list)
                        cs = np.concatenate(cs_list)
                        m_src = compute_binary_metrics(cy, y_score=cs, threshold=tau_src)
                        rows.append({
                            "window_size": w, "cap": cap, "set": s, "seed": seed, "method": rep, "mode": "source_thresh",
                            "condition": cond, **m_src,
                        })
                        if cond in ["B", "D"]:
                            cal = eval_with_warmup(cs_list, cy_list, k_target=k_warm)
                            for cname, cm in cal.items():
                                rows.append({
                                    "window_size": w, "cap": cap, "set": s, "seed": seed, "method": rep, "mode": cname,
                                    "condition": cond, **cm,
                                })
                    del model
                    torch.cuda.empty_cache()
            print(f"  Completed frame-equated W={w} {s}", flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(out_raw, index=False)
    set_avg = df.groupby(["window_size", "method", "mode", "condition", "set"], as_index=False)[["Recall", "FAR_per_100k", "Attack_F1", "AP"]].mean()
    sum_rows = []
    for (w, meth, mode, cond), g in set_avg.groupby(["window_size", "method", "mode", "condition"]):
        by_s = g.set_index("set")
        sum_rows.append({
            "window_size": w, "method": meth, "mode": mode, "condition": cond,
            "recall_4set": float(g["Recall"].mean()), "recall_3veh": dedup_mean(by_s["Recall"]),
            "far_pct_4set": float(g["FAR_per_100k"].mean() / 1000.0),
            "f1_4set": float(g["Attack_F1"].mean()), "ap_4set": float(g["AP"].mean()),
            "ap_3veh": dedup_mean(by_s["AP"]),
        })
    sdf = pd.DataFrame(sum_rows)
    sdf.to_csv(OUT / "frame_equated_windows_summary.csv", index=False)
    print(sdf.to_string(index=False), flush=True)


def exp_reservoir_seed_variance(manifest):
    out_raw = OUT / "reservoir_seed_variance_raw.csv"
    if out_raw.exists():
        print("[3/4] Skipping reservoir seed variance (already exists).", flush=True)
        return
    print("[3/4] Running multi-seed reservoir sampling variance (20261103/04/05, W=64, cap=1000, model seed=42)...", flush=True)
    rows = []
    cfg = dict(CFG, window_size=64)
    for s in SETS:
        sp = partitions(manifest, s)
        eval_data = {cond: [extract_file_features(e, w=64, tier="content") for e in sp[cond]] for cond in ["validation", "B", "D"]}
        for rseed in [20261103, 20261104, 20261105]:
            tr_r, tr_s, tr_y = build_train_pool(sp["train"], w=64, cap=1000, tier="content", sampling_seed=rseed)
            for rep, x_tr, feat_idx in [("raw", tr_r, 0), ("structural", tr_s, 1)]:
                model, _ = train_transformer(x_tr, tr_y, cfg, 42, "cuda")
                vy = np.concatenate([tpl[2] for tpl in eval_data["validation"]])
                vs = np.concatenate([predict_scores(model, tpl[feat_idx], "cuda", 256) for tpl in eval_data["validation"]])
                tau_src = choose_threshold_on_validation(vy, vs, 100.0)
                for cond in ["B", "D"]:
                    cy_list = [tpl[2] for tpl in eval_data[cond]]
                    cs_list = [predict_scores(model, tpl[feat_idx], "cuda", 256) for tpl in eval_data[cond]]
                    m_src = compute_binary_metrics(np.concatenate(cy_list), y_score=np.concatenate(cs_list), threshold=tau_src)
                    rows.append({
                        "set": s, "sampling_seed": rseed, "method": rep, "mode": "source_thresh",
                        "condition": cond, **m_src,
                    })
                    cal = eval_with_warmup(cs_list, cy_list, k_target=500)
                    for cname, cm in cal.items():
                        rows.append({
                            "set": s, "sampling_seed": rseed, "method": rep, "mode": cname,
                            "condition": cond, **cm,
                        })
                del model
                torch.cuda.empty_cache()
        print(f"  Completed reservoir variance {s}", flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(out_raw, index=False)
    by_rseed = df.groupby(["sampling_seed", "method", "mode", "condition"], as_index=False)[["Recall", "FAR_per_100k", "Attack_F1", "AP"]].mean()
    summary = by_rseed.groupby(["method", "mode", "condition"], as_index=False)[["Recall", "FAR_per_100k", "Attack_F1", "AP"]].agg(["mean", "std"])
    summary.to_csv(OUT / "reservoir_seed_variance_summary.csv")
    print(by_rseed.to_string(index=False), flush=True)


def exp_crysys_diagnostic(manifest):
    out_csv = OUT / "crysys_diagnostic_summary.csv"
    if out_csv.exists():
        print("[4/4] Skipping CrySyS diagnostic (already exists).", flush=True)
        return
    print("[4/4] Checking saved CrySyS-AssocRules AP/K=500 behavior & non-reservoir full benign fit on Set 1...", flush=True)
    rows = []
    # 1) Saved CrySyS predictions across 4 sets x 3 seeds (check AP + K=500 at 1% budget + max tie fraction)
    ASSOC_BASE = CODE / "results/assoc_exact_fast_v1"
    for s in SETS:
        for seed in SEEDS:
            pred_root = ASSOC_BASE / s / f"seed_{seed}" / "assoc_rules_crysys/attempt_001/predictions"
            for cond in ["A", "B", "C", "D"]:
                cfiles = sorted((pred_root / cond).glob("*.csv.gz"))
                cy, cs, caps = [], [], []
                for csvp in cfiles:
                    df_c = pd.read_csv(csvp)
                    y_arr = df_c["y_true"].to_numpy(int)
                    sc_arr = df_c["assoc_rules_crysys"].to_numpy(float)
                    cy.append(y_arr)
                    cs.append(sc_arr)
                    caps.append((y_arr, sc_arr))
                cy_all = np.concatenate(cy)
                cs_all = np.concatenate(cs)
                m = compute_binary_metrics(cy_all, y_score=cs_all, threshold=1.0000000000000002)
                rows.append({
                    "variant": "saved_reservoir_src", "set": s, "seed": seed, "condition": cond,
                    "frac_score_1": float((cs_all >= 1.0 - 1e-12).mean()), **m,
                })
                if cond in ["B", "D"]:
                    cal = eval_with_warmup([x[1] for x in caps], [x[0] for x in caps], k_target=500)
                    rows.append({
                        "variant": "saved_reservoir_cal500_1pct", "set": s, "seed": seed, "condition": cond,
                        "frac_score_1": float((cs_all >= 1.0 - 1e-12).mean()), **cal["cal_1p0"],
                    })
    # 2) Full contiguous benign source stream refit on Set 1 seed 42 (no reservoir downsampling)
    sp1 = partitions(manifest, "set_01")
    b_parts = []
    for e in sp1["train"]:
        a = mapped(CACHE, e)
        n_win = int(e["windows"])
        r = a[: n_win * 64]
        yb = np.asarray(r["label"]).reshape(n_win, 64).max(1)
        keep = yb == 0
        if keep.any():
            b_parts.append({
                "ids": np.asarray(r["cid"]).reshape(n_win, 64)[keep],
                "data": np.asarray(r["payload"]).reshape(n_win, 64, 8)[keep],
                "dlc": np.asarray(r["dlc"]).reshape(n_win, 64)[keep],
                "times": np.asarray(r["timestamp"]).reshape(n_win, 64)[keep],
                "frame_y": np.asarray(r["label"]).reshape(n_win, 64)[keep],
                "capture": np.full(int(keep.sum()), e["source"]),
                "ix": np.flatnonzero(keep),
                "y": yb[keep],
            })
    full_benign = {k: np.concatenate([p[k] for p in b_parts], axis=0)[:5000] for k in b_parts[0]}
    print(f"  Set 1 contiguous benign windows for AssocRules (first 5k contiguous): {len(full_benign['y'])}", flush=True)
    ar = AssocRules()
    from comparison.adapters import assoc_class
    ar.model = assoc_class()(window_size=64, stride=64, random_state=42)
    ar.model.fit(frame_table(full_benign))
    # Score validation & A/B/C/D
    val_parts = []
    for e in sp1["validation"]:
        for b in c_batches(CACHE, e, batch_windows=512, features=False, tier="content"):
            val_parts.append((b["y"], ar.score(b, "cpu", 128)))
    vy = np.concatenate([p[0] for p in val_parts])
    vs = np.concatenate([p[1] for p in val_parts])
    tau_full = choose_threshold_on_validation(vy, vs, 100.0)
    print(f"  Set 1 full-benign AssocRules threshold={tau_full!r}, val benign frac==1.0: {float((vs[vy==0] >= 1.0 - 1e-12).mean()):.4f}", flush=True)
    for cond in ["A", "B", "C", "D"]:
        cy, cs = [], []
        for e in sp1[cond]:
            for b in c_batches(CACHE, e, batch_windows=512, features=False, tier="content"):
                cy.append(b["y"])
                cs.append(ar.score(b, "cpu", 128))
        cy_all = np.concatenate(cy)
        cs_all = np.concatenate(cs)
        m = compute_binary_metrics(cy_all, y_score=cs_all, threshold=tau_full)
        rows.append({
            "variant": "set1_full_benign_refit", "set": "set_01", "seed": 42, "condition": cond,
            "frac_score_1": float((cs_all >= 1.0 - 1e-12).mean()), **m,
        })

    df = pd.DataFrame(rows)
    df.to_csv(OUT / "crysys_diagnostic_raw.csv", index=False)
    sum_df = df.groupby(["variant", "condition"], as_index=False)[["Recall", "FAR_per_100k", "Attack_F1", "AP", "frac_score_1"]].mean()
    sum_df.to_csv(out_csv, index=False)
    print(sum_df.to_string(index=False), flush=True)


if __name__ == "__main__":
    manifest = load_manifest(CACHE, verify=False)
    exp_monotonic_timed_vs_content(manifest)
    exp_frame_equated_windows(manifest)
    exp_reservoir_seed_variance(manifest)
    exp_crysys_diagnostic(manifest)
    print("ALL PART 2 EXPERIMENTS COMPLETE.", flush=True)
