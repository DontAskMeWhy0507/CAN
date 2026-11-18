"""Recursive file inventory and schema spot checks, not a full-file preflight."""
import argparse,sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1] / 'src'))
import pandas as pd
from can_research.experiment import external_specs
from can_research.io import read_frames,CONDITIONS
from can_research.features import WindowExtractor

def inventory(root,output):
 root,output=Path(root).resolve(),Path(output)
 output.mkdir(parents=True,exist_ok=True)
 ledger=json.loads((Path(__file__).resolve().parents[1]/'configs/external_datasets.json').read_text())
 specs,excluded=external_specs(root,ledger,'content')
 for path in sorted((root/'data/can-train-and-test').glob('set_*/*/*.csv')):
  specs.append(dict(path=str(path),kind='ctt',name='CTT'))
 records=[]
 for spec in specs:
  p=Path(spec['path']);r=dict(dataset=spec['name'],path=str(p.relative_to(root)),bytes=p.stat().st_size)
  try:
   stream=read_frames(p,spec['kind'],128,spec.get('label_policy'))
   df=next(stream)
   stream.close()
   extractor=WindowExtractor(64,'content' if spec['kind']=='ciciov' else 'timed')
   extractor.feed(df)
   r.update(status='PREFIX_SCHEMA_PASS',checked_frames=len(df),label_values=','.join(map(str,sorted(df.attack.unique()))))
  except Exception as e:r.update(status='FAIL',error=repr(e))
  records.append(r)
 pd.DataFrame(records).to_csv(output/'inventory.csv',index=False)
 (output/'exclusions.json').write_text(json.dumps(excluded,indent=2),encoding='utf-8')
 report={'scope':'First 128 frames only; does not certify complete chronology, labels or payloads.',
  'files':len(records),'failures':sum(r['status']=='FAIL' for r in records),
  'counts_by_dataset':pd.Series([r['dataset'] for r in records]).value_counts().to_dict()}
 (output/'scope.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
 print(json.dumps(report,indent=2))
 if report['failures']:raise ValueError('Inspect inventory failures before a full preflight.')

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',default='.');p.add_argument('--output',required=True)
 a=p.parse_args();inventory(a.root,a.output)
