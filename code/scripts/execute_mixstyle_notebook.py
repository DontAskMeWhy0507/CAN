"""Create and execute a saved notebook in this exact Python environment."""
from pathlib import Path
import json
import sys
import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager
from jupyter_client.kernelspec import KernelSpecManager

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'code/results/mixstyle_posthoc_2026-11-09'
OUT.mkdir(parents=True, exist_ok=True)
notebook = ROOT/'code/notebooks/10_mixstyle_posthoc.ipynb'
executed = notebook.with_name('10_mixstyle_posthoc_executed.ipynb')
nb = nbformat.v4.new_notebook(cells=[
    nbformat.v4.new_markdown_cell('''# Thử nghiệm bổ sung: Structural Transformer + MixStyle

Thí nghiệm hậu nghiệm, một cấu hình cố định, W64, nguồn duy nhất cho mỗi set.
12 fit mới; tái sử dụng 24 baseline; không đổi kết quả chính của khóa luận.
MixStyle theo lớp trên chuỗi là bản thích ứng đề xuất, chưa phải tái lập bài CNN.
Phải đọc kết quả cùng FAR, không kết luận từ recall/AP đơn lẻ.

Nguồn: [Zhou et al., ICLR 2021](https://arxiv.org/abs/2104.02008).
Xem `code/notes/PHUONG_PHAP_BO_SUNG_MIXSTYLE_2026-11-09.txt`.
'''),
    nbformat.v4.new_code_cell('''from pathlib import Path
import sys, subprocess, json
ROOT = next(p for p in [Path.cwd().resolve(), *Path.cwd().resolve().parents]
            if (p / 'code/scripts/run_mixstyle_study.py').is_file())
OUT = ROOT / 'code/results/mixstyle_posthoc_2026-11-09'
OUT.mkdir(parents=True, exist_ok=True)
import torch
print('Python:', sys.executable)
assert torch.cuda.is_available(), 'CUDA required'
print('GPU:', torch.cuda.get_device_name(0))
result = subprocess.run([sys.executable, '-m', 'pytest', 'code/tests/test_mixstyle.py', '-q',
                         '--junitxml=' + str(OUT/'mixstyle_tests.xml')],
                        cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
print(result.stdout)
result.check_returncode()
'''),
    nbformat.v4.new_code_cell('''# Each completed set is hash-verified and resumable; failed attempts are preserved.
command = [sys.executable, '-u', 'code/scripts/run_mixstyle_study.py', '--stage', 'all', '--output', str(OUT)]
with (OUT/'execution.log').open('w', encoding='utf-8') as log:
    process = subprocess.Popen(command, cwd=ROOT, text=True, encoding='utf-8', errors='replace',
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in process.stdout:
        log.write(line); log.flush()
        print(line, end='', flush=True)
    status = process.wait()
if status:
    raise RuntimeError(f'Study failed with exit code {status}; see execution.log')
'''),
    nbformat.v4.new_code_cell('''import pandas as pd
display(pd.read_csv(OUT/'analysis/equal_set.csv'))
print(json.loads((OUT/'analysis/audit.json').read_text()))
print('Primary result preserved. External results require the companion verification report.')
''')
])
nb.metadata['kernelspec'] = dict(name='python3', display_name='Python 3', language='python')
nbformat.write(nb, notebook)
kernel_root = OUT/'notebook_kernel'
spec_dir = kernel_root/'mixstyle-study'
spec_dir.mkdir(parents=True, exist_ok=True)
(spec_dir/'kernel.json').write_text(json.dumps(dict(
    argv=[sys.executable, '-m', 'ipykernel_launcher', '-f', '{connection_file}'],
    display_name='MixStyle study environment', language='python')), encoding='utf-8')
manager = KernelManager(kernel_name='mixstyle-study',
                        kernel_spec_manager=KernelSpecManager(kernel_dirs=[str(kernel_root)]))
client = NotebookClient(nb, km=manager, timeout=None, resources={'metadata': {'path': str(ROOT)}})
print('Executing notebook:', notebook, flush=True)
try:
    client.execute()
finally:
    nbformat.write(nb, executed)
    print('Saved executed notebook:', executed, flush=True)
