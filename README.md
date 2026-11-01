# Learning Robust CAN Intrusion Representations under Distribution Shift

## Research goal

This project studies a practical question:

> Why do CAN intrusion-detection models fail when the vehicle, attack type, or dataset changes, and can a structural representation generalize without learning vehicle-specific CAN-ID semantics?

The goal is not to maximize an in-distribution accuracy score. The goal is to produce evidence about **when**, **why**, and **how** CAN IDS models transfer across vehicle and dataset shifts.

## Research story

```text
Observation
  CAN IDS performance may drop under vehicle / attack / dataset shift
        ↓
Analysis
  Existing encoders may retain vehicle-specific CAN-ID, payload, or timing information
        ↓
Hypothesis
  A structural CAN representation should transfer better than a raw vehicle-specific representation
        ↓
Method
  Learn from relative ID behavior, payload changes, timing, and message transitions
        ↓
Evaluation
  Unseen vehicle + unseen attack + external datasets
```

## Datasets and their roles

| Dataset | Role | Important constraint |
|---|---|---|
| `can-train-and-test` | Primary controlled benchmark | Use the provided train/test protocol; never use a random 80/20 split for the main result. |
| `can-ml` *(to download)* | Multi-source leave-one-vehicle-out experiment | Needed for a valid vehicle-adversarial/domain-generalization experiment. |
| `CAN-MIRGU` | External and temporal/environment shift | One vehicle domain; use for external transfer, not as a multi-vehicle source benchmark. |
| `CICIoV2024` | External Ford 2019 validation | Supplied CSV schema has no timestamp, so timing features cannot be evaluated fairly here. Use hexadecimal files only. |
| `Automotive CAN Bus Intrusion Dataset v2-` | Attack-mechanism stress test | Opel/Renault attack logs are modified copies of normal test captures; do not treat an entire file as malicious. |

### `can-train-and-test` official protocol

Each `set_01`–`set_04` contains one source training folder and four test conditions:

| Symbol | Folder | Meaning |
|---|---|---|
| A | `test_01_known_vehicle_known_attack` | Known vehicle + known attack |
| B | `test_02_unknown_vehicle_known_attack` | Unknown vehicle + known attack |
| C | `test_03_known_vehicle_unknown_attack` | Known vehicle + unknown attack |
| D | `test_04_unknown_vehicle_unknown_attack` | Unknown vehicle + unknown attack |

Vehicle mapping:

| Set | Known vehicle | Unknown vehicle |
|---|---|---|
| `set_01` | Chevrolet Impala | Chevrolet Silverado |
| `set_02` | Chevrolet Traverse | Subaru Forester |
| `set_03` | Chevrolet Silverado | Subaru Forester |
| `set_04` | Subaru Forester | Chevrolet Traverse |

## Frozen research protocol

### Primary task

- Binary prediction: `benign` versus `attack`.
- Attack mechanism is retained for stratification and per-mechanism diagnostics, not used as the primary target.
- Strict zero-shot means that target vehicle/dataset data must not fit a scaler, threshold, vocabulary, calibration model, or representation normalizer.

### Window definition

- Use 64-message non-overlapping windows for the primary study.
- A window is positive when it contains one or more attack frames.
- Never cross a source-file boundary.
- Test all official CTT windows by streaming; training may use deterministic class-balanced sampling.
- Run a sensitivity check with 32 and 128 messages only for the strongest model.

### Baselines

All baselines receive the same window and training budget:

1. Logistic Regression
2. XGBoost
3. MLP
4. CNN-1D
5. BiLSTM
6. Transformer

The raw baseline representation contains CAN-ID bits, DLC, payload bytes, payload masks, and log inter-arrival time. Raw decimal CAN-ID must not be treated as a continuous number.

### Metrics

For every model × set × A/B/C/D report:

- attack F1
- precision and recall
- PR-AUC
- false alarms per 100,000 benign windows
- detection latency where timestamps exist
- macro F1 across attack mechanisms
- 95% bootstrap confidence intervals by capture/file or attack episode

Report shift effects directly:

```text
vehicle shift, known attack   = A - B
attack shift, known vehicle   = A - C
vehicle shift, unknown attack = C - D
interaction                   = (A - B) - (C - D)
```

## Implementation roadmap

### Phase 0 — Audit and manifest

Create a reproducible manifest for every source file:

```text
dataset, vehicle_id, manufacturer, capture_id, file_path,
split_role, scenario, attack_binary, attack_mechanism,
label_source, has_timestamp, has_dlc, schema_version
```

Normalize data into one canonical frame schema:

```text
timestamp | can_id_token | can_id_bits | dlc | payload[8] |
payload_mask[8] | attack_binary | attack_mechanism |
vehicle_id | capture_id | source_file
```

Required quality checks:

- CSV/log parser validity
- timestamp monotonicity
- payload/DLC validity
- class ratio and unique CAN-ID counts
- duplicate/overlapping captures
- verified label provenance for every external evaluation file

### Phase 1 — Establish the problem

Run all six baselines on all four CTT sets. Hyperparameters are selected only from a grouped validation split inside `train_01`, then frozen for every official test.

This phase is successful if it creates a trustworthy A/B/C/D benchmark table. A performance collapse is a result to test, not an assumption to force.

### Phase 2 — Explain failure

For MLP/CNN/LSTM/Transformer, freeze the encoder and extract representation `z`.

- Train attack and vehicle linear probes using capture-group splits.
- Balance attack and vehicle labels before a vehicle probe.
- Compare ID-only, payload-only, timing-only, full raw, and structural features.
- Use UMAP only for visualization; use probes and ablations as evidence.

Vehicle leakage is only claimed if a vehicle probe is above chance and structural/ID-removal ablations reduce vehicle separability while preserving or improving unseen-vehicle performance.

### Phase 3 — Structural ID-agnostic method

The proposed representation must not use a globally meaningful raw CAN-ID.

Use:

- DLC and payload bytes/masks
- payload difference from the previous message with the same local ID
- local ID frequency and local first-occurrence rank
- gap since the same local ID appeared
- local message-transition statistics
- causal inter-arrival features

The model is a Structural CAN Encoder with a Transformer attack head. Train it with binary cross-entropy plus an optional contrastive invariance term using ID-permuted structural views.

Required comparisons:

```text
Raw Transformer
Structural Transformer + BCE
Structural Transformer + BCE + contrastive invariance loss
```

### Phase 4 — Multi-source and external validation

After downloading `can-ml`, build a separate leave-one-vehicle-out protocol. Do not train on `can-ml` captures that overlap official CTT tests.

Use DANN and supervised contrastive learning only as multi-source baselines. They are not valid as the primary strict single-source solution.

External targets:

```text
CTT → CAN-MIRGU       strict zero-shot external transfer
CTT → CICIoV2024      content/structural tier only, no timing
CTT → Automotive v2   attack-mechanism stress test with verified intervals
```

Never combine incompatible feature schemas blindly. Report results by tier:

```text
Tier 1: common payload + structural features
Tier 2: timestamped structural features
Tier 3: raw vehicle-specific features
```

## Success gates

The method claim proceeds only if:

1. Vehicle probes are meaningfully above chance under capture-group evaluation.
2. Structural features reduce vehicle separability.
3. The proposed model improves `D` (unknown vehicle + unknown attack) by at least 3 F1 points over a capacity-matched raw Transformer, with paired bootstrap CI excluding zero.
4. Known vehicle/known attack performance does not decrease by more than 2 F1 points.
5. Results appear in at least 3 of 4 CTT sets.

If the method does not pass these gates, the project remains a valid analysis-first paper on failure modes and transfer boundaries of CAN IDS models.

## Planned artefacts

```text
00_audit_and_manifest.ipynb
01_ctt_strict_baselines.ipynb
02_shift_and_representation_analysis.ipynb
03_structural_id_agnostic_method.ipynb
04_external_validation.ipynb

dataset_manifest.csv
attack_taxonomy.yaml
splits.yaml
results/metrics.csv
results/embeddings.parquet
```

## Timeline

| Weeks | Deliverable |
|---|---|
| 1–2 | Audit, manifest, taxonomy, `can-ml` download, parser QA |
| 3–6 | CTT baselines and A/B/C/D tables |
| 7–8 | Shift analysis and representation probes |
| 9–12 | Structural model and ablations |
| 13–16 | Multi-source and external validation |
| 17–24 | Preprint, figures, reproducibility cleanup, revisions |

## Current implementation status

- [x] Dataset structure audited.
- [x] Strict CTT A/B/C/D protocol documented.
- [x] Shared taxonomy file created: `attack_taxonomy.yaml`.
- [ ] Download and register `can-ml`.
- [ ] Generate dataset manifest.
- [ ] Run strict baselines.
- [ ] Run representation analysis.
- [ ] Train structural method.
- [ ] Run external validation.

## Quick start: simple strict baseline

This repository includes one small runnable baseline for Phase 1. It trains a
Logistic Regression model on `train_01` only, uses 64-frame non-overlapping
windows, and evaluates all official A/B/C/D folders without a random split.

```powershell
python -m pip install -r requirements.txt
python run_baseline.py --set set_01
```

The result is written to `results/metrics_set_01.csv`. The default training
limit (`2,000` windows per source file) is deliberate so a first run is small;
raise `--max-train-windows-per-file` for a larger experiment. Repeat with
`set_02`, `set_03`, and `set_04` for the complete primary table.
