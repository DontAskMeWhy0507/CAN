# CAN intrusion detection under vehicle and attack shift

Runnable paper comparisons (2026-11-08): start with `code/notebooks/06_prepare_comparison_data.ipynb`,
then 07 and 08. See `VIEC_BAN_CAN_LAM.txt` and `code/comparison/README.txt`.
The new comparison preserves original CTT file order and uses content-only raw28/structural30
because full-file checks found timestamp inversions. It is separate from the timed v2.1 protocol below.


Protocol v2.1 investigates raw-ID-free structural features against matched raw
inputs under the four can-train-and-test conditions. **The implementation and
manuscripts have been corrected; confirmatory model reruns are pending.**

Start with [the short action note](VIEC_BAN_CAN_LAM.txt) and
[the Vietnamese rerun guide](RERUN_GUIDE_VI.md). They contain exact commands,
remaining experiments, dataset exclusions and additional comparisons.
The source-language thesis is Vietnamese; English is its translation.

## Implemented scope

- Classic CAN, 11-bit identifiers, up to eight payload bytes; strict input checks.
- Non-overlapping completed windows, W=64; never cross file boundaries.
- Continuous within-file history across I/O chunks; no invented timestamps.
- Raw (29 dimensions) and structural (32); content-only tiers use 28 and 30.
- Transformer: d_model=64, two layers, four heads, two-class cross-entropy.
- Matched raw/structural Transformers, structural XGBoost, raw Logistic Regression.
- Full-file source sampling, grouped validation, source-only threshold calibration.
- All official A/B/C/D test windows, three seeds, per-file confusion counts,
  continuous-score AP and explicit N/A metrics for missing denominators.
- Checkpoints, predictions, code/data hashes and manifests for every new run.
- Thirteen ablations, window sensitivity, frozen balanced probes with controls,
  paired file bootstrap of recall/FAR/F1 and equal-set paired summaries.
- Required full-file preflight; output integrity hashes; resumable study units.

ID-renaming invariance is not proof of independence from vehicle identity.
Strict zero-shot excludes target-fitted models, scalers and thresholds; reading
the past of a target capture to compute a feature is permitted input processing.

## Quick start

```powershell
.venv/Scripts/python.exe -m pip install -r code/requirements.txt
.venv/Scripts/python.exe -m pytest -q
.venv/Scripts/python.exe code/scripts/run_study.py --plan
.venv/Scripts/python.exe code/scripts/run_study.py --stage all
```

The launcher runs the planned study in immutable set/seed attempts. Completed
compatible attempts are verified and skipped; incomplete attempts restart in new
directories. See the guide for stages, aggregation and output locations.
`requirements-tested.txt` records the local CPU test environment; use the
compatible requirements with an appropriate CUDA PyTorch build on Colab.

## Dataset roles

| Dataset | Role and restrictions |
|---|---|
| can-train-and-test | Four sets, official A/B/C/D tests; source validation holds out a recording-round group |
| Automotive v2 | Verified DoS intervals and benign traces; do not label an entire attack file positive |
| CAN-MIRGU | Recursive discovery of labelled benign and attack logs; full-file checks required |
| CICIoV2024 | Content-only; local SPEED hex export quarantined due to 4,989 byte disagreements with decimal |
| OTIDS converted/shuffled | Disabled pending chronological captures and reliable frame-label provenance |

Vehicle pairs: Set 1 Impala→Silverado; Set 2 Traverse→Forester;
Set 3 Silverado→Forester; Set 4 Forester→Traverse. File groups do not establish
independent driving sessions. Modified Automotive captures share underlying traffic.

The external ledger is `code/configs/external_datasets.json`. Missing and quarantined
files are written to exclusion reports. COMPLETE means the configured eligible
files finished, not that every originally desired external target was available.

## Repository map

| Path | Purpose |
|---|---|
| `thesis/vi/` | Bản tiếng Việt: `main.tex`, `refs.bib`, `figs/`, `slide/` |
| `thesis/en/` | Bản tiếng Anh: `main.tex`, `refs.bib`, `figs/`, `slide/` |
| `code/src/can_research/` | Shared parsers, features, metrics, models, training and evaluation |
| `code/data/` | Original datasets; keep source files unchanged |
| `code/notebooks/` | Exploratory and reproducibility notebooks |
| `code/configs/` | Frozen experiment protocols |
| `code/scripts/` | Preflight, inventory, summaries, probes and thesis build |
| `code/tests/` | Protocol and synthetic integration checks |
| `code/results/` | Metrics, manifests, reports and checkpoints |
| `code/notes/` | Audit notes and revision status |

Historical `code/results/phase*`, `code/results/master_*` and `code/results/comparison_*` outputs are retained for
traceability. They are not v2.1 research results; see `code/results/LEGACY_RESULTS_NOTICE.txt`.
The original manuscript, notebooks and code are backed up in
`revision_backup/before_repair_2026-11-03.zip`.

No final superiority, deployment-speed or A+ assessment is claimed before the
required reruns and current faculty rubric are available. Published frame-level
results are not ranked directly against 64-frame window results.
