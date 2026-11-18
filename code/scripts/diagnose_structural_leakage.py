"""Diagnose vehicle identity leakage across structural feature groups and ablation encoders.

Reuses the exact balanced probe protocol from content_completion_2026-11-09.
"""
from pathlib import Path
import argparse
import hashlib
import json
import sys
import time
import numpy as np
import pandas as pd
import torch
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

CODE = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(CODE), str(CODE / 'src')]

from extensions.content import VARIANTS, select
from comparison.data import load_manifest, partitions
from comparison.adapters import load_checkpoint
from can_research.models import CANTransformer, predict_scores
from can_research.probes import balanced_cells, evaluate_controls
from scripts.complete_content_studies import (
    CFG, CACHE, selection, pool, baseline
)

OUT = CODE / 'results/structural_leakage_diagnosis_2026-11-11'
ABLATION_ROOT = CODE / 'results/content_completion_2026-11-09/ablation/w64'
PROBE_CACHE_FILE = OUT / 'cached_probe_data.npz'


def get_probe_dataset():
    """Extract or load cached balanced probe windows."""
    OUT.mkdir(parents=True, exist_ok=True)
    if PROBE_CACHE_FILE.exists():
        print(f"Loading cached probe dataset from {PROBE_CACHE_FILE}...", flush=True)
        d = np.load(PROBE_CACHE_FILE)
        data = {
            'train': (d['train_raw'], d['train_st'], d['train_y'], d['train_v']),
            'validation': (d['val_raw'], d['val_st'], d['val_y'], d['val_v'])
        }
        return data

    print("Building probe dataset from comparison_data_v1 cache...", flush=True)
    t0 = time.time()
    manifest = load_manifest(CACHE, verify=False)
    data = {}
    for role in ['train', 'validation']:
        pools = []
        for vehicle, s in enumerate(CFG['sets']):
            es = partitions(manifest, s)[role]
            chosen = selection(es, 64, 200)
            raw, st, y, ix = pool(es, 64, chosen)
            pools.append((raw, st, y, np.full(len(y), vehicle)))
        arrays = tuple(np.concatenate([p[j] for p in pools]) for j in range(4))
        ix = balanced_cells(arrays[2], arrays[3], 42)
        data[role] = tuple(v[ix] for v in arrays)
    
    np.savez_compressed(
        PROBE_CACHE_FILE,
        train_raw=data['train'][0], train_st=data['train'][1], train_y=data['train'][2], train_v=data['train'][3],
        val_raw=data['validation'][0], val_st=data['validation'][1], val_y=data['validation'][2], val_v=data['validation'][3]
    )
    print(f"Probe dataset built and cached in {time.time() - t0:.2f}s", flush=True)
    return data


def run_input_feature_group_probes(data):
    """Probe directly on raw input structural features before encoder."""
    print("\n=== [1] INPUT STRUCTURAL FEATURE-GROUP PROBES ===", flush=True)
    train_st = data['train'][1]  # (N, 64, 30)
    val_st = data['validation'][1]
    
    train_y_atk = data['train'][2]
    val_y_atk = data['validation'][2]
    train_y_veh = data['train'][3]
    val_y_veh = data['validation'][3]

    # Define feature groups within the 30 structural columns
    # st:
    # 0: dlc/8
    # 1..8: payload bytes (normalized by 255)
    # 9..16: mask
    # 17..24: delta (diff from previous same ID)
    # 25: has_previous
    # 26: counts / 64
    # 27: rank / num_ids
    # 28: rank / 64
    # 29: pair transition / 63
    groups = {
        'all_30_features': list(range(30)),
        'only_payload (b0-b7)': list(range(1, 9)),
        'only_delta (d0-d7)': list(range(17, 25)),
        'only_dlc_and_masks': [0] + list(range(9, 17)) + [25],
        'only_local_stats (count,rank_id,rank_w)': [26, 27, 28],
        'only_transition': [29],
        'only_counts_and_transition': [26, 29],
        'no_payload': [i for i in range(30) if i not in range(1, 9)],
        'no_delta': [i for i in range(30) if i not in range(17, 25)],
        'no_local_stats': [i for i in range(30) if i not in [26, 27, 28]],
        'no_transition': [i for i in range(30) if i != 29],
        'relative_features (no payload, no abs delta)': [0] + list(range(9, 17)) + [25, 26, 27, 28, 29],
    }

    rows = []
    for gname, cols in groups.items():
        tr_x = train_st[..., cols].reshape(len(train_st), -1)
        val_x = val_st[..., cols].reshape(len(val_st), -1)

        # Vehicle probe
        veh_ctrl = evaluate_controls(tr_x, val_x, train_y_veh, val_y_veh, repeats=1)
        veh_learned = next(r['balanced_accuracy'] for r in veh_ctrl if r['control'] == 'learned')

        # Attack probe
        atk_ctrl = evaluate_controls(tr_x, val_x, train_y_atk, val_y_atk, repeats=1)
        atk_learned = next(r['balanced_accuracy'] for r in atk_ctrl if r['control'] == 'learned')

        rows.append({
            'feature_group': gname,
            'dims_per_frame': len(cols),
            'input_dims_total': tr_x.shape[-1],
            'vehicle_probe_ba': veh_learned,
            'attack_probe_ba': atk_learned
        })
        print(f"Group: {gname:<45} | Dims: {len(cols):2d} | Veh Probe: {veh_learned*100:6.2f}% | Atk Probe: {atk_learned*100:6.2f}%", flush=True)

    df_groups = pd.DataFrame(rows)
    df_groups.to_csv(OUT / 'input_feature_group_probes.csv', index=False)
    return df_groups


def run_ablation_encoder_probes(data):
    """Probe all 96 ablation checkpoints to see how encoder embeddings behave."""
    print("\n=== [2] ABLATION ENCODER EMBEDDING PROBES ===", flush=True)
    raw_tr, st_tr, y_tr, v_tr = data['train']
    raw_val, st_val, y_val, v_val = data['validation']

    rows = []
    for rep in VARIANTS:
        print(f"--> Probing representation: {rep}", flush=True)
        for s in CFG['sets']:
            for seed in CFG['seeds']:
                if rep in ['raw', 'structural']:
                    model, _, ref = baseline(s, seed, rep)
                else:
                    cp_path = ABLATION_ROOT / s / f'seed_{seed}' / 'attempt_001' / f'{rep}.pt'
                    if not cp_path.exists():
                        print(f"Warning: {cp_path} not found, skipping", flush=True)
                        continue
                    checkpoint = torch.load(cp_path, map_location='cuda', weights_only=True)
                    dim = checkpoint['input_dim']
                    model = CANTransformer(dim, window_size=64).to('cuda').eval()
                    model.load_state_dict(checkpoint['state_dict'])
                    ref = str(cp_path)

                # Predict latent embeddings
                x_tr = select(raw_tr, st_tr, rep)
                x_val = select(raw_val, st_val, rep)
                z_tr = predict_scores(model, x_tr, 'cuda', 128, True)[1]
                z_val = predict_scores(model, x_val, 'cuda', 128, True)[1]

                for target, ytr, yte in [('vehicle', v_tr, v_val), ('attack', y_tr, y_val)]:
                    controls = evaluate_controls(z_tr, z_val, ytr, yte, repeats=1)
                    learned_ba = next(c['balanced_accuracy'] for c in controls if c['control'] == 'learned')
                    const_ba = next(c['balanced_accuracy'] for c in controls if c['control'] == 'constant')
                    perm_ba = next(c['balanced_accuracy'] for c in controls if c['control'] == 'permuted_train_labels')
                    rows.append({
                        'representation': rep,
                        'encoder_set': s,
                        'seed': seed,
                        'target': target,
                        'learned_ba': learned_ba,
                        'constant_ba': const_ba,
                        'permuted_ba': perm_ba
                    })

    df_enc = pd.DataFrame(rows)
    df_enc.to_csv(OUT / 'ablation_encoder_probes.csv', index=False)
    return df_enc


def compile_synthesis(df_enc):
    """Merge encoder probe results with Condition B/D performance from equal_set_means.csv."""
    means_file = CODE / 'results/content_completion_2026-11-09/equal_set_means.csv'
    df_perf = pd.read_csv(means_file)
    df_perf_w64 = df_perf[df_perf['window_size'] == 64]

    # Aggregate probes by representation and target
    probe_agg = df_enc.groupby(['representation', 'target'])['learned_ba'].mean().unstack()
    probe_agg = probe_agg.rename(columns={'vehicle': 'vehicle_probe_ba', 'attack': 'attack_probe_ba'})

    # Aggregate performance for Condition B and Condition D
    perf_b = df_perf_w64[df_perf_w64['condition'] == 'B'].set_index('method')[['Recall', 'FAR_per_100k', 'AP', 'Attack_F1']]
    perf_b.columns = [f'{c}_condB' for c in perf_b.columns]
    perf_b['FAR_percent_condB'] = perf_b['FAR_per_100k_condB'] / 1000.0

    perf_d = df_perf_w64[df_perf_w64['condition'] == 'D'].set_index('method')[['Recall', 'FAR_per_100k', 'AP', 'Attack_F1']]
    perf_d.columns = [f'{c}_condD' for c in perf_d.columns]
    perf_d['FAR_percent_condD'] = perf_d['FAR_per_100k_condD'] / 1000.0

    synthesis = pd.concat([probe_agg, perf_b, perf_d], axis=1).sort_values(by='AP_condB', ascending=False)
    synthesis.to_csv(OUT / 'synthesis_probe_vs_performance.csv')
    
    print("\n" + "=" * 110)
    print("=== TỔNG HỢP: VEHICLE PROBE vs. CHẤT LƯỢNG PHÁT HIỆN TẤN CÔNG (ĐIỀU KIỆN B: XE ĐÍCH MỚI) ===")
    print("=" * 110)
    cols_show = ['vehicle_probe_ba', 'attack_probe_ba', 'AP_condB', 'Recall_condB', 'FAR_percent_condB', 'AP_condD']
    display_df = synthesis[cols_show].copy()
    display_df['vehicle_probe_ba'] = display_df['vehicle_probe_ba'] * 100
    display_df['attack_probe_ba'] = display_df['attack_probe_ba'] * 100
    display_df['Recall_condB'] = display_df['Recall_condB'] * 100
    display_df.columns = ['Veh Probe (%)', 'Atk Probe (%)', 'AP (B)', 'Recall (B) %', 'FAR (B) %', 'AP (D)']
    print(display_df.round(4).to_string())
    print("=" * 110 + "\n")
    return synthesis


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    data = get_probe_dataset()
    df_groups = run_input_feature_group_probes(data)
    df_enc = run_ablation_encoder_probes(data)
    synthesis = compile_synthesis(df_enc)
    print(f"All diagnostic results written to: {OUT}")


if __name__ == '__main__':
    main()
