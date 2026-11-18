"""Finalize this local notebook execution after all three saved kernels finish."""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import hashlib
import json
import os
import time
import zipfile

ROOT = Path(__file__).resolve().parents[2]
CODE = ROOT / 'code'
NAMES = ('07_gpu_four_models_executed', '09_assoc_cpu_acceleration',
         '08_merged_results_executed')
PARTS = {'gpu': ('comparison_gpu4_reuse_v1', 48),
         'cpu': ('assoc_exact_fast_v1', 12)}


def write_json(path, value):
    tmp = path.with_suffix(path.suffix + '.saving')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    tmp.replace(path)


def snapshot():
    value = {'utc': datetime.now(timezone.utc).isoformat(), 'status': 'RUNNING',
             'finalizer_pid': os.getpid()}
    for key, (folder, total) in PARTS.items():
        manifests = [json.loads(p.read_text(encoding='utf-8')) for p in
                     (CODE / 'results' / folder).glob('set_*/seed_*/*/attempt_*/manifest.json')]
        value[key] = {'total': total, 'counts': dict(Counter(m['status'] for m in manifests))}
    states = []
    for name in NAMES:
        path = CODE / 'notebooks' / (name + '.execution.json')
        state = json.loads(path.read_text(encoding='utf-8'))
        value[name] = state
        states.append(state['status'])
    if 'FAILED' in states:
        value['status'] = 'FAILED'
    elif all(s == 'COMPLETE' for s in states):
        value['status'] = 'COMPLETE'
    else:
        now = datetime.now(timezone.utc)
        for name in NAMES:
            state = value[name]
            if state['status'] == 'RUNNING' and (now - datetime.fromisoformat(state['heartbeat_utc'])).total_seconds() > 300:
                value['status'] = 'HEARTBEAT_STALE'
                value['error'] = 'Notebook heartbeat older than five minutes: ' + name
    return value


def finalize(value):
    for key, (_, total) in PARTS.items():
        assert value[key]['counts'].get('COMPLETE') == total, value[key]
    merged = CODE / 'results/comparison_merged_fast'
    coverage = json.loads((merged / 'coverage.json').read_text())
    assert coverage['status'] == 'COMPLETE_MATRIX' and coverage['cells'] == 60
    # Actual saved kernel execution is required; no fabricated execution metadata.
    for name in NAMES:
        nb = json.loads((CODE / 'notebooks' / (name + '.ipynb')).read_text(encoding='utf-8'))
        for cell in nb['cells']:
            if cell['cell_type'] != 'code' or not ''.join(cell['source']).strip():
                continue
            assert cell['execution_count'] is not None, name
            assert not any(o.get('output_type') == 'error' for o in cell.get('outputs', [])), name
    value['coverage'] = coverage
    value['log_note'] = 'Subprocess console log files contain monitored excerpts; full per-cell metrics, checkpoints and manifests remain in their result roots.'
    archive = CODE / 'output/notebook_comparison_executed_2026-11-08.zip'
    archive.parent.mkdir(parents=True, exist_ok=True)
    files = []
    for name in NAMES:
        files += [CODE / 'notebooks' / (name + ext) for ext in ('.ipynb', '.execution.json')]
    files += [p for p in merged.rglob('*') if p.is_file()]
    files += [p for p in (CODE / 'results').glob('*notebook_subprocess.log')]
    lineage = CODE / 'results/comparison_gpu4_reuse_v1/reuse_lineage.json'
    if lineage.exists():
        files.append(lineage)
    tmp = archive.with_suffix('.zip.saving')
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as z:
        for path in files:
            z.write(path, path.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(tmp) as z:
        assert z.testzip() is None
    tmp.replace(archive)
    value['archive'] = str(archive)
    value['archive_sha256'] = hashlib.sha256(archive.read_bytes()).hexdigest()


def main():
    target = CODE / 'results/notebook_execution_progress.json'
    while True:
        value = snapshot()
        if value['status'] == 'COMPLETE':
            try:
                finalize(value)
            except Exception as exc:
                value.update(status='FINALIZATION_FAILED', error=repr(exc))
        write_json(target, value)
        complete = sum(value[k]['counts'].get('COMPLETE', 0) for k in PARTS)
        text = (f"TRANG THAI NOTEBOOK: {value['status']}\n"
                f"Cap nhat UTC: {value['utc']}\n"
                f"Hoan tat {complete}/60 luot (GPU {value['gpu']['counts'].get('COMPLETE', 0)}/48; "
                f"AssocRules {value['cpu']['counts'].get('COMPLETE', 0)}/12).\n"
                "Notebook va dau ra duoc tu luu moi 15 giay.\n"
                "Ket qua gop: code/results/comparison_merged_fast (chi sau khi du 60 luot).\n"
                "Goi ZIP sau khi thanh cong: code/output/notebook_comparison_executed_2026-11-08.zip\n"
                "Giua cac luot, giu may chay va tranh che do ngu.\n"
                "Xem chi tiet loi/trang thai: code/results/notebook_execution_progress.json\n")
        (ROOT / 'TRANG_THAI_CHAY_NOTEBOOK.txt').write_text(text, encoding='utf-8')
        if value['status'] != 'RUNNING':
            return
        time.sleep(15)


if __name__ == '__main__':
    main()
