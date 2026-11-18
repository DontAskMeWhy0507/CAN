"""Execute the corrected analysis notebook without retraining frozen IDS models."""
from pathlib import Path
import json
import sys
import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager
from jupyter_client.kernelspec import KernelSpecManager

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'code/results/mixstyle_posthoc_2026-11-09'
nb = nbformat.v4.new_notebook(cells=[
    nbformat.v4.new_markdown_cell('''# Kiểm chứng và kết luận MixStyle — 10/11/2026

Notebook này hoàn tất phân tích của 12 checkpoint và 57 capture ngoại bộ đã lưu.
Notebook 10 được giữ làm lịch sử: lần tổng hợp đầu lỗi do baseline có thêm dòng
ngưỡng mặc định 0,5. Phân tích hiện tại lọc đúng `source_calibrated`.
Mã runner cũ được khôi phục và đối chiếu đúng SHA256 trong `provenance/`.

Không chọn lại mô hình theo test. Probe và runtime dùng checkpoint đã đóng băng.
Đây là nghiên cứu hậu nghiệm, không thay kết quả chính của khóa luận.
'''),
    nbformat.v4.new_code_cell('''from pathlib import Path
import sys, subprocess, json
ROOT = next(p for p in [Path.cwd().resolve(), *Path.cwd().resolve().parents]
            if (p/'code/scripts/run_mixstyle_study.py').is_file())
OUT = ROOT/'code/results/mixstyle_posthoc_2026-11-09'
def run(*args):
    result = subprocess.run([sys.executable, '-X', 'utf8', *args], cwd=ROOT,
                            text=True, encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(result.stdout)
    result.check_returncode()
run('-m', 'pytest', 'code/tests/test_mixstyle.py', '-q',
    '--junitxml='+str(OUT/'mixstyle_tests_final.xml'))
'''),
    nbformat.v4.new_code_cell('''# Recompute primary metrics and paired intervals from frozen predictions.
run('code/scripts/run_mixstyle_study.py', '--stage', 'summarize', '--output', str(OUT))
'''),
    nbformat.v4.new_code_cell('''# Reuse hash-verified completed secondary work; otherwise execute it.
run('code/scripts/complete_mixstyle_secondary.py')
run('code/scripts/report_mixstyle_results.py')
'''),
    nbformat.v4.new_code_cell('''import pandas as pd
display(pd.read_csv(OUT/'analysis/six_method_equal_set.csv').query("condition == 'B'"))
display(pd.read_csv(OUT/'analysis/probe_means.csv').query("control == 'learned'"))
display(pd.read_csv(OUT/'analysis/runtime_remeasured.csv'))
print(json.loads((OUT/'analysis/final_report.json').read_text(encoding='utf-8')))
print((OUT/'analysis/BAO_CAO_MIXSTYLE.txt').read_text(encoding='utf-8'))
''')
])
nb.metadata['kernelspec'] = dict(name='python3', display_name='Python 3', language='python')
source = ROOT/'code/notebooks/11_mixstyle_analysis.ipynb'
executed = source.with_name('11_mixstyle_analysis_executed.ipynb')
nbformat.write(nb, source)
kernel_root = OUT/'notebook_kernel'
spec = kernel_root/'mixstyle-analysis'
spec.mkdir(parents=True, exist_ok=True)
(spec/'kernel.json').write_text(json.dumps(dict(argv=[sys.executable, '-m', 'ipykernel_launcher', '-f', '{connection_file}'],
                                              display_name='MixStyle analysis', language='python')), encoding='utf-8')
manager = KernelManager(kernel_name='mixstyle-analysis',
                        kernel_spec_manager=KernelSpecManager(kernel_dirs=[str(kernel_root)]))
client = NotebookClient(nb, km=manager, timeout=None, resources={'metadata': {'path': str(ROOT)}})
print('Executing corrected analysis notebook', flush=True)
try: client.execute()
finally:
    nbformat.write(nb, executed)
    print('Saved', executed, flush=True)
