"""Create a source/thesis/PDF bundle. Raw captures and environments excluded."""
from pathlib import Path
import argparse,hashlib,json,zipfile

ROOT=Path(__file__).resolve().parents[1]
PROJECT_ROOT=ROOT.parent
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',default='code/output/thesis_revision_2026-11-06.zip')
 a=p.parse_args();dest=Path(a.output);dest.parent.mkdir(parents=True,exist_ok=True)
 files=[PROJECT_ROOT/name for name in ['README.md','RERUN_GUIDE_VI.md','VIEC_BAN_CAN_LAM.txt','KE_HOACH_SO_SANH.txt','pytest.ini','code/README.md','code/notes/REVISION_STATUS.csv','code/requirements.txt','code/requirements-tested.txt',
  'code/run_experiments.py','code/run_baseline.py','thesis/en/main.tex','thesis/vi/main.tex',
  'thesis/en/refs.bib','thesis/vi/refs.bib',
  'code/output/thesis_compile_check/vi/main.pdf','code/output/thesis_compile_check/en/main.pdf',
  'code/notes/AUDIT_THESIS_2026-11-03.txt','code/notes/REFERENCE_VERIFICATION_2026-11-04.txt',
  'code/results/phase3_method_comparison.csv','code/results/phase4_external_metrics.csv','code/results/master_all_datasets_benchmark.csv',
  'code/results/published_metric_audit.csv','code/results/data_quality_automotive_v2.csv','code/results/ciciov_speed_format_verification.json',
  'code/results/manuscript_structure_check.json','code/results/pdf_build_checks.json','code/results/verification_report.json','code/results/revision_v21_checks.json',
  'code/results/LEGACY_RESULTS_NOTICE.txt']]
 required=[p for p in files if p.suffix in {'.tex','.bib','.pdf'} or p.name in
           {'VIEC_BAN_CAN_LAM.txt','pytest.ini','revision_v21_checks.json','pdf_build_checks.json'}]
 missing=[str(p) for p in required if not p.is_file()]
 if missing: raise FileNotFoundError('Missing required revision artifact: '+', '.join(missing))
 for pattern in ['code/notebooks/*.ipynb','code/src/can_research/*.py','code/configs/*.json','code/scripts/*.py','code/tests/*.py',
                 'thesis/vi/figs/**/*','thesis/en/figs/**/*','code/results/inventory_v2/*','code/notes/doi_thu_2026-11-06/**/*']:
  files.extend(PROJECT_ROOT.glob(pattern))
 files=sorted(set(p for p in files if p.is_file()))
 manifest={'date':'2026-11-06','purpose':'Protocol v2.1 bilingual thesis sources/PDFs and implementation; confirmatory runs pending',
  'excluded':'Raw datasets, Python environment, pretrained weights, original-version backup and temporary renders',
  'files':[dict(path=str(p.relative_to(PROJECT_ROOT)).replace('\\','/'),bytes=p.stat().st_size,sha256=digest(p)) for p in files]}
 with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
  for p in files:z.write(p,str(p.relative_to(PROJECT_ROOT)).replace('\\','/'))
  for folder in ['thesis/vi/slide/','thesis/en/slide/']:
   z.writestr(folder,b'')
  z.writestr('BUNDLE_MANIFEST.json',json.dumps(manifest,ensure_ascii=False,indent=2))
 with zipfile.ZipFile(dest) as z:
  assert z.testzip() is None
  for r in manifest['files']:assert hashlib.sha256(z.read(r['path'])).hexdigest()==r['sha256']
 print(json.dumps({'path':str(dest.resolve()),'files':len(files),'bytes':dest.stat().st_size,'sha256':digest(dest)},indent=2))
