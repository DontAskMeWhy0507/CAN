"""Regenerate numeric LaTeX rows and update the two standalone thesis files."""

def legacy_main():
    from pathlib import Path
    import re

    import pandas as pd

    CODE = Path(__file__).resolve().parents[1]
    PROJECT = CODE.parent
    TABLES = CODE / "results" / "latex_tables"
    TABLES.mkdir(parents=True, exist_ok=True)


    def write_rows(name: str, rows: list[str]) -> None:
        (TABLES / name).write_text("\n".join(rows) + "\n\\bottomrule\n", encoding="utf-8")


    historical = pd.read_csv(CODE / "results" / "phase3_method_comparison.csv")
    rows = []
    for _, row in historical.iterrows():
        label = ("Raw TF" if row.Model.startswith("Raw") else
                 "Structural TF" if "Transformer" in row.Model else "Structural XGB")
        rows.append(f"{row.Condition[0]} & {label} & {row.Attack_F1:.4f} & "
                    f"{row.Precision:.4f} & {row.Recall:.4f} & {row.PR_AUC:.4f} & "
                    f"{row.FAR_per_100k:.2f} \\\\")
    write_rows("historical_rows.tex", rows)

    quality = pd.read_csv(CODE / "results" / "data_quality_automotive_v2.csv")
    rows = []
    for _, row in quality.iterrows():
        label = ("Opel" if "Opel" in row.path else "Renault") + (
            " DoS" if "dosattack" in row.path else " benign")
        rows.append(f"{label} & {row.frames:,} & {row.attack_frames:,} & "
                    f"{row.benign_windows:,} & {row.attack_windows:,} \\\\")
    write_rows("quality_rows.tex", rows)

    published = pd.read_csv(CODE / "results" / "published_metric_audit.csv")
    rows = []
    for _, row in published.iterrows():
        rows.append(f"{row.model} & {row.source_table} & {row.source_f1:.4f} & "
                    f"{row.attack_f1:.4f} & {row.weighted_f1:.4f} \\\\")
    write_rows("published_rows.tex", rows)

    for lang in ("vi", "en"):
        main = PROJECT / "thesis" / lang / "main.tex"
        body = main.read_text(encoding="utf-8")
        for name in ("quality_rows.tex", "historical_rows.tex", "published_rows.tex"):
            source = f"../../code/results/latex_tables/{name}"
            pattern = (r"(?<=% Begin inlined " + re.escape(source) + r"\n).*?"
                       r"(?=% End inlined " + re.escape(source) + r")")
            replacement = (TABLES / name).read_text(encoding="utf-8")
            body, count = re.subn(pattern, lambda _: replacement, body, count=1, flags=re.S)
            if count != 1:
                raise ValueError(f"Missing or repeated inlined table in {main}: {name}")
        main.write_text(body, encoding="utf-8")
        print(f"Updated numeric tables in {main}")


if __name__ == '__main__':
    import sys
    if '--legacy-manuscript' in sys.argv:
        sys.argv.remove('--legacy-manuscript')
        legacy_main()
    else:
        from pathlib import Path
        import subprocess
        args=sys.argv[1:]
        if not any(a in args for a in ['--check','--build']):args=['--build',*args]
        raise SystemExit(subprocess.call([sys.executable,str(Path(__file__).with_name('finalize_thesis_for_supervisor.py')),*args]))
