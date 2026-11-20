"""Evaluate post-hoc unsupervised benign warmup calibration and per-attack breakdown.

Preserves all frozen baselines and existing artifacts.
Outputs to code/results/benign_calibration_posthoc_2026-11-10/
and exports figures to thesis/vi/figs and thesis/en/figs.
"""
from pathlib import Path
import hashlib
import json
import shutil
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

CODE = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(CODE), str(CODE / "src")]
from can_research.metrics import compute_binary_metrics

BASE = CODE / "results/comparison_gpu4_reuse_v1"
MIX = CODE / "results/mixstyle_posthoc_2026-11-09"
MIX_EXT = MIX / "external/attempt_001"
OLD_EXT = CODE / "results/content_completion_2026-11-09/external/attempt_001"
OUT = CODE / "results/benign_calibration_posthoc_2026-11-10"
OUT.mkdir(parents=True, exist_ok=True)

SETS = [f"set_0{i}" for i in range(1, 5)]
SEEDS = [42, 43, 44]
METHODS = ["raw_transformer", "structural_transformer", "structural_mixstyle"]
DISPLAY_NAMES = {
    "raw_transformer": "Raw Transformer",
    "structural_transformer": "Structural Transformer",
    "structural_mixstyle": "Structural + MixStyle",
}

def load_condition_data(set_name, seed, condition):
    mix_unit = MIX / "main" / set_name / "attempt_001"
    cov = json.loads((mix_unit / "coverage.json").read_text())
    entries = [r for r in cov if r["condition"] == condition]
    
    raw_dir = BASE / set_name / f"seed_{seed}" / "raw_transformer" / "attempt_001" / "predictions" / condition
    str_dir = BASE / set_name / f"seed_{seed}" / "structural_transformer" / "attempt_001" / "predictions" / condition
    
    raw_map = {}
    for p in raw_dir.glob("*.csv.gz"):
        df = pd.read_csv(p)
        raw_map[df["capture_id"].iloc[0]] = (df["y_true"].to_numpy(int), df["raw_transformer"].to_numpy(float))
        
    str_map = {}
    for p in str_dir.glob("*.csv.gz"):
        df = pd.read_csv(p)
        str_map[df["capture_id"].iloc[0]] = (df["y_true"].to_numpy(int), df["structural_transformer"].to_numpy(float))
        
    captures = []
    for r in entries:
        f = r["file"]
        with np.load(mix_unit / r["prediction"]) as z:
            y_mix = z["y"].astype(int)
            s_mix = z[f"seed_{seed}"].astype(float)
        y_raw, s_raw = raw_map[f]
        y_str, s_str = str_map[f]
        assert np.array_equal(y_mix, y_raw) and np.array_equal(y_mix, y_str)
        atk_type = Path(f).stem.rsplit("-", 1)[0]
        captures.append({
            "file": f,
            "attack_type": atk_type,
            "y": y_mix,
            "raw_transformer": s_raw,
            "structural_transformer": s_str,
            "structural_mixstyle": s_mix,
        })
    return captures

def evaluate_calibration():
    records = []
    per_attack_records = []
    
    # Warmup sizes and FAR budgets
    warmup_configs = [
        (200, 100), (200, 500), (200, 1000), (200, 2000),
        (500, 100), (500, 500), (500, 1000), (500, 2000),
        (1000, 100), (1000, 500), (1000, 1000), (1000, 2000),
    ]
    
    for cond in ["B", "D"]:
        print(f"Loading data for condition {cond}...", flush=True)
        # Preload once per set and seed
        preloaded = {}
        for s in SETS:
            for seed in SEEDS:
                preloaded[(s, seed)] = load_condition_data(s, seed, cond)
        print(f"Loaded condition {cond}. Computing calibrations...", flush=True)

        for warmup_k, target_far in warmup_configs:
            for s in SETS:
                for seed in SEEDS:
                    caps = preloaded[(s, seed)]
                    
                    # 1. Vehicle-wide calibration
                    for m in METHODS:
                        warmup_pool = []
                        eval_caps = []
                        for c in caps:
                            y = c["y"]
                            sc = c[m]
                            first_atk = np.where(y == 1)[0]
                            prefix_end = first_atk[0] if len(first_atk) > 0 else len(y)
                            k = min(warmup_k, prefix_end // 2)
                            warmup_pool.append(sc[:k])
                            eval_caps.append({
                                "attack_type": c["attack_type"],
                                "file": c["file"],
                                "y": y[k:],
                                "score": sc[k:],
                            })
                            
                        w_pool = np.concatenate(warmup_pool)
                        q = 1.0 - (target_far / 100000.0)
                        tau = float(np.quantile(w_pool, q))
                        
                        all_ey = np.concatenate([ec["y"] for ec in eval_caps])
                        all_es = np.concatenate([ec["score"] for ec in eval_caps])
                        
                        overall_m = compute_binary_metrics(all_ey, y_score=all_es, threshold=tau)
                        records.append({
                            "condition": cond,
                            "warmup_k": warmup_k,
                            "target_far_budget": target_far,
                            "set": s,
                            "seed": seed,
                            "method": m,
                            "threshold": tau,
                            **overall_m,
                        })
                        
                        # Per attack breakdown at k=500 and k=1000, far in [100, 1000]
                        if warmup_k in [500, 1000] and target_far in [100, 1000]:
                            atk_types = sorted(set(ec["attack_type"] for ec in eval_caps))
                            for atk in atk_types:
                                sub_y = np.concatenate([ec["y"] for ec in eval_caps if ec["attack_type"] == atk])
                                sub_s = np.concatenate([ec["score"] for ec in eval_caps if ec["attack_type"] == atk])
                                atk_m = compute_binary_metrics(sub_y, y_score=sub_s, threshold=tau)
                                per_attack_records.append({
                                    "condition": cond,
                                    "warmup_k": warmup_k,
                                    "target_far_budget": target_far,
                                    "set": s,
                                    "seed": seed,
                                    "method": m,
                                    "attack_type": atk,
                                    **atk_m,
                                })
                                
    df_all = pd.DataFrame(records)
    df_atk = pd.DataFrame(per_attack_records)
    
    # Save raw records
    df_all.to_csv(OUT / "calibration_raw_runs.csv", index=False)
    df_atk.to_csv(OUT / "per_attack_raw_runs.csv", index=False)
    
    # Compute Equal Set Means (seed mean per set, then mean across sets)
    grouped = df_all.groupby(["condition", "warmup_k", "target_far_budget", "set", "method"])[
        ["Recall", "FAR_per_100k", "AP", "Attack_F1"]
    ].mean().reset_index()
    
    summary = grouped.groupby(["condition", "warmup_k", "target_far_budget", "method"])[
        ["Recall", "FAR_per_100k", "AP", "Attack_F1"]
    ].mean().reset_index()
    summary["FAR_pct"] = summary["FAR_per_100k"] / 1000.0
    summary.to_csv(OUT / "benign_calibration_summary.csv", index=False)
    
    # Per attack summary
    atk_grouped = df_atk.groupby(["condition", "warmup_k", "target_far_budget", "set", "method", "attack_type"])[
        ["Recall", "FAR_per_100k", "AP", "Attack_F1"]
    ].mean().reset_index()
    atk_summary = atk_grouped.groupby(["condition", "warmup_k", "target_far_budget", "method", "attack_type"])[
        ["Recall", "FAR_per_100k", "AP", "Attack_F1"]
    ].mean().reset_index()
    atk_summary["FAR_pct"] = atk_summary["FAR_per_100k"] / 1000.0
    atk_summary.to_csv(OUT / "per_attack_summary.csv", index=False)
    
    return summary, atk_summary

def evaluate_external():
    coverage = json.loads((MIX_EXT / "coverage.json").read_text())
    complete = [r for r in coverage if r["status"] == "COMPLETE"]
    
    ext_records = []
    for ds in sorted(set(r["dataset"] for r in complete)):
        entries = [r for r in complete if r["dataset"] == ds]
        for target_far in [100, 500, 1000]:
            for seed in SEEDS:
                warmup_pool = {m: [] for m in ["raw", "structural", "structural_mixstyle"]}
                eval_y = []
                eval_s = {m: [] for m in warmup_pool}
                for r in entries:
                    token = hashlib.sha256(r["file"].encode()).hexdigest()[:20] + ".npz"
                    with np.load(MIX_EXT / token) as a, np.load(OLD_EXT / token) as b:
                        y = a["y"].astype(int)
                        s_map = {
                            "raw": b[f"raw_{seed}"].astype(float),
                            "structural": b[f"structural_{seed}"].astype(float),
                            "structural_mixstyle": a[f"seed_{seed}"].astype(float),
                        }
                    benign_idx = np.where(y == 0)[0]
                    k = min(500, len(benign_idx) // 2)
                    if k > 0:
                        w_idx = benign_idx[:k]
                        mask = np.ones(len(y), dtype=bool)
                        mask[w_idx] = False
                        eval_y.append(y[mask])
                        for m in warmup_pool:
                            warmup_pool[m].append(s_map[m][w_idx])
                            eval_s[m].append(s_map[m][mask])
                    else:
                        eval_y.append(y)
                        for m in warmup_pool:
                            eval_s[m].append(s_map[m])
                ey = np.concatenate(eval_y)
                q = 1.0 - (target_far / 100000.0)
                for m in warmup_pool:
                    w_pool = np.concatenate(warmup_pool[m]) if len(warmup_pool[m]) > 0 else np.array([0.5])
                    es = np.concatenate(eval_s[m])
                    tau = float(np.quantile(w_pool, q))
                    metrics = compute_binary_metrics(ey, y_score=es, threshold=tau)
                    ext_records.append({
                        "dataset": ds,
                        "target_far_budget": target_far,
                        "seed": seed,
                        "method": m,
                        **metrics,
                    })
    df_ext = pd.DataFrame(ext_records)
    df_ext.to_csv(OUT / "external_raw_runs.csv", index=False)
    
    ext_summary = df_ext.groupby(["dataset", "target_far_budget", "method"])[
        ["Recall", "FAR_per_100k", "AP", "Attack_F1"]
    ].mean().reset_index()
    ext_summary["FAR_pct"] = ext_summary["FAR_per_100k"] / 1000.0
    ext_summary.to_csv(OUT / "external_benign_calibration_summary.csv", index=False)
    return ext_summary

def format_atk(name):
    mapping = {
        "DoS": "DoS",
        "double": "Double",
        "force-neutral": "Force-Neut.",
        "fuzzing": "Fuzzing",
        "interval": "Interval",
        "rpm": "RPM",
        "rpm-accessory": "RPM-Acc.",
        "speed": "Speed",
        "speed-accessory": "Speed-Acc.",
        "standstill": "Standstill",
        "systematic": "Systematic",
        "triple": "Triple",
    }
    return mapping.get(name, name.capitalize())

def plot_figures(summary, atk_summary):
    # Professional styling for publication & thesis
    plt.rcParams.update({
        "font.family": "serif",
        "font.size": 10,
        "axes.labelsize": 11,
        "axes.titlesize": 12,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.fontsize": 10,
        "figure.titlesize": 13,
    })
    
    fig, axes = plt.subplots(2, 2, figsize=(13, 9.5), dpi=300)
    
    # Colors and markers
    colors = {
        "raw_transformer": "#d95f02",
        "structural_transformer": "#1f78b4",
        "structural_mixstyle": "#2ca02c",
    }
    markers = {
        "raw_transformer": "s",
        "structural_transformer": "o",
        "structural_mixstyle": "^",
    }
    
    # Panel 1: Condition B - Recall vs Target FAR Budget (K=500)
    ax1 = axes[0, 0]
    sub_b = summary[(summary.condition == "B") & (summary.warmup_k == 500)]
    for m in METHODS:
        data = sub_b[sub_b.method == m].sort_values("target_far_budget")
        ax1.plot(data["FAR_pct"], data["Recall"] * 100, marker=markers[m], color=colors[m],
                 linewidth=2.2, markersize=7, label=DISPLAY_NAMES[m])
    ax1.set_title("(a) Condition B (Unseen Vehicle, Known Attack)", pad=10, fontweight="bold")
    ax1.set_xlabel("Empirical Target FAR (%)")
    ax1.set_ylabel("Attack Recall (%)")
    ax1.grid(True, linestyle="--", alpha=0.6)
    
    # Panel 2: Condition D - Recall vs Target FAR Budget (K=500)
    ax2 = axes[0, 1]
    sub_d = summary[(summary.condition == "D") & (summary.warmup_k == 500)]
    for m in METHODS:
        data = sub_d[sub_d.method == m].sort_values("target_far_budget")
        ax2.plot(data["FAR_pct"], data["Recall"] * 100, marker=markers[m], color=colors[m],
                 linewidth=2.2, markersize=7, label=DISPLAY_NAMES[m])
    ax2.set_title("(b) Condition D (Unseen Vehicle, Unseen Attack)", pad=10, fontweight="bold")
    ax2.set_xlabel("Empirical Target FAR (%)")
    ax2.set_ylabel("Attack Recall (%)")
    ax2.grid(True, linestyle="--", alpha=0.6)
    
    # Panel 3: Condition B - Per-Attack Horizontal Bars (K=1000, Budget 1.0%)
    ax3 = axes[1, 0]
    atk_b = atk_summary[(atk_summary.condition == "B") & (atk_summary.warmup_k == 1000) & (atk_summary.target_far_budget == 1000)]
    attacks_b = sorted(atk_b.attack_type.unique(), reverse=True)
    y_pos = np.arange(len(attacks_b))
    bar_h = 0.26
    for i, m in enumerate(METHODS):
        vals = [atk_b[(atk_b.method == m) & (atk_b.attack_type == a)]["Attack_F1"].values[0] for a in attacks_b]
        ax3.barh(y_pos + (i - 1) * bar_h, vals, height=bar_h, label=DISPLAY_NAMES[m], color=colors[m], alpha=0.88)
    ax3.set_title("(c) Condition B: F1-Score by Attack Type", pad=10, fontweight="bold")
    ax3.set_yticks(y_pos)
    ax3.set_yticklabels([format_atk(a) for a in attacks_b], fontsize=9)
    ax3.set_xlabel("Attack F1-Score")
    ax3.set_xlim(0, 1.05)
    ax3.grid(True, linestyle="--", alpha=0.5, axis="x")
    
    # Panel 4: Condition D - Per-Attack Horizontal Bars (K=1000, Budget 1.0%)
    ax4 = axes[1, 1]
    atk_d = atk_summary[(atk_summary.condition == "D") & (atk_summary.warmup_k == 1000) & (atk_summary.target_far_budget == 1000)]
    attacks_d = sorted(atk_d.attack_type.unique(), reverse=True)
    y_pos_d = np.arange(len(attacks_d))
    for i, m in enumerate(METHODS):
        vals = [atk_d[(atk_d.method == m) & (atk_d.attack_type == a)]["Attack_F1"].values[0] for a in attacks_d]
        ax4.barh(y_pos_d + (i - 1) * bar_h, vals, height=bar_h, label=DISPLAY_NAMES[m], color=colors[m], alpha=0.88)
    ax4.set_title("(d) Condition D: F1-Score by Zero-Day Attack Type", pad=10, fontweight="bold")
    ax4.set_yticks(y_pos_d)
    ax4.set_yticklabels([format_atk(a) for a in attacks_d], fontsize=9)
    ax4.set_xlabel("Attack F1-Score")
    ax4.set_xlim(0, 0.75)
    ax4.grid(True, linestyle="--", alpha=0.5, axis="x")
    
    # Unified clean top legend
    handles, labels = ax1.get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 0.995), ncol=3, frameon=True, facecolor="white", edgecolor="#cccccc")

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    fig_path = OUT / "calibration_recovery_comparison.png"
    plt.savefig(fig_path, bbox_inches="tight")
    plt.close()
    
    # Copy to thesis/vi/figs and thesis/en/figs
    for target_dir in [CODE.parent / "thesis/vi/figs", CODE.parent / "thesis/en/figs"]:
        target_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(fig_path, target_dir / "calibration_recovery_comparison.png")
    print(f"Generated and copied clean figure to thesis fig directories.")

def main():
    print("Evaluating Unsupervised Benign Warmup Calibration...", flush=True)
    summary, atk_summary = evaluate_calibration()
    print("Evaluating External Datasets Calibration...", flush=True)
    ext_summary = evaluate_external()
    print("Plotting figures...", flush=True)
    plot_figures(summary, atk_summary)
    
    # Write provenance protocol
    (OUT / "protocol.json").write_text(json.dumps({
        "status": "COMPLETE",
        "description": "Post-hoc unsupervised benign warmup quantile calibration and per-attack breakdown",
        "reused_predictions": "comparison_gpu4_reuse_v1, mixstyle_posthoc_2026-11-09",
        "warmup_k": [200, 500, 1000],
        "target_far_budgets": [100, 500, 1000, 2000],
        "zero_retraining": True,
        "zero_target_attack_labels": True,
    }, indent=2), encoding="utf-8")
    print("Finished evaluating benign warmup calibration successfully!")

if __name__ == "__main__":
    main()
