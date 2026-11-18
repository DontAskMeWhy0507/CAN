"""Persist progress and package the current local execution, without scheduling."""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import json,time,zipfile
ROOT=Path(__file__).resolve().parents[2];CODE=ROOT/'code';OUT=CODE/'results/content_completion_2026-11-09'


def main():
    while True:
        states={}
        for name in ('10_complete_thesis_evidence','11_import_complete_thesis_evidence'):
            p=CODE/'notebooks'/(name+'.execution.json')
            states[name]=json.loads(p.read_text()) if p.exists() else {'status':'WAITING'}
        manifests=[json.loads(p.read_text()) for p in OUT.glob('**/manifest.json')]
        completed=[m for m in manifests if m['status']=='COMPLETE']
        newfits=sum((len(m['signature']['variants'])-2 if m['signature']['w']==64 else 2) for m in completed if m['signature']['stage'] in ['ablation','sensitivity'])
        stage=json.loads((OUT/'progress.json').read_text()) if (OUT/'progress.json').exists() else {}
        status='FAILED' if any(s['status']=='FAILED' for s in states.values()) else 'RUNNING'
        if all(s['status']=='COMPLETE' for s in states.values()):status='STUDIES_COMPLETE_PDF_REVIEW_PENDING'
        report=dict(utc=datetime.now(timezone.utc).isoformat(),status=status,stage=stage,completed_new_fits=newfits,planned_new_fits=144,manifest_counts=dict(Counter(m['status'] for m in manifests)),notebooks=states)
        if status=='STUDIES_COMPLETE_PDF_REVIEW_PENDING':
            dest=CODE/'output/content_completion_2026-11-09.zip';tmp=dest.with_suffix('.zip.saving')
            paths=[p for p in OUT.rglob('*') if p.is_file() and p.name not in ['live_status.json','execution.log']]
            paths += [p for p in (CODE/'output/thesis_completion_2026-11-09').glob('*/main.pdf')]
            paths += list((CODE/'extensions').glob('*.py'))
            paths += [CODE/'scripts'/n for n in ['complete_content_studies.py','analyze_content_completion.py','monitor_content_completion.py']]
            paths += [CODE/'tests/test_content_completion.py',ROOT/'HOAN_THIEN_THESIS_2026-11-09.txt']
            for lang in ['vi','en']:
                paths += [ROOT/'thesis'/lang/n for n in ['main.tex','refs.bib']]
                paths += [p for p in (ROOT/'thesis'/lang/'figs').glob('*') if p.is_file()]
            for name in states:
                paths += [CODE/'notebooks'/(name+ext) for ext in ['.ipynb','.execution.json']]
            with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as z:
                for p in sorted(set(paths)):
                    z.write(p,p.relative_to(ROOT).as_posix())
            with zipfile.ZipFile(tmp) as z:assert z.testzip() is None
            tmp.replace(dest);report['archive']=str(dest)
            final=json.loads((OUT/'completion_report.json').read_text())
            if final.get('status')=='THESIS_READY_FOR_SUPERVISOR_REVIEW':
                status='THESIS_READY_FOR_SUPERVISOR_REVIEW';report['status']=status
        (OUT/'live_status.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        (ROOT/'TRANG_THAI_HOAN_THIEN_THESIS.txt').write_text(f"{report['utc']}\nStatus: {status}\nStage: {stage.get('stage',stage.get('status','starting'))}\nNew fits complete: {newfits}/144; plus 24 reused W64 baseline cells\nRuntime/probe/external manifests: {len([m for m in completed if m['signature']['stage'] not in ['ablation','sensitivity']])}/3\nDetails: code/results/content_completion_2026-11-09/live_status.json\nFinal PDF visual review and academic review are distinct from run completion.\n",encoding='utf-8')
        if status!='RUNNING':return
        time.sleep(15)


if __name__=='__main__':main()
