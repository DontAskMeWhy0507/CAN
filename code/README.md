# Code

`configs/` stores frozen experiment protocols. `notebooks/` contains exploratory
and reproducibility notebooks. `notes/` stores audit notes and revision status.

Commands work from the project root or this directory when the shown paths match.
The root `pytest.ini` exposes `code/src` to tests. Script entry points resolve their
own imports. Start with `../VIEC_BAN_CAN_LAM.txt`; the reproducible study launcher
is `scripts/run_study.py`. Its default paths resolve relative to the code directory,
not the current shell directory. No confirmatory model results are bundled.
