from pathlib import Path
import sys,importlib.util,json
sys.path[:0]=[str(Path(__file__).resolve().parents[1]),str(Path(__file__).resolve().parents[1]/'src')]
import numpy as np
import pandas as pd
import pytest
from thesis_final.evidence import check_metrics,equal_set,valid_manifest,sha
from thesis_final.render import exact_block,table,render
from can_research.metrics import compute_binary_metrics
from thesis_final.evidence import effect_label,check_external

@pytest.mark.parametrize('dr,df,label',[(-.1,-10,'RECALL_DECREASE'),(.1,10,'INCREASED_FALSE_ALARMS_TRADEOFF'),(.1,-10,'RECALL_GAIN_WITHOUT_FAR_INCREASE'),(np.nan,0,'UNDEFINED')])
def test_effect_direction_never_calls_a_tradeoff_a_joint_gain(dr,df,label):
 assert effect_label(dr,df)==label

def test_external_requires_exact_coverage_and_denominators(tmp_path):
 d=pd.DataFrame([dict(dataset='x',file='capture',seed=42,representation='raw',Total_Windows=3)])
 with pytest.raises(ValueError,match='coverage mismatch'):
  check_external(d,[dict(status='COMPLETE',dataset='x',file='capture',windows=3,frames=192,tail=0)],tmp_path)

def fixture(y=(0,0,1,1),s=(.1,.2,.8,.9)):
 m=compute_binary_metrics(np.array(y),y_score=np.array(s),threshold=.5)
 return pd.DataFrame([dict(set='set_01',seed=42,method='raw',condition='B',file=f,operating_point='source_calibrated',**m) for f in ['capture','ALL']])

@pytest.mark.parametrize('y,s,recall,far',[
 ([0,0,1,1],[0,0,0,0],0,0),([0,0,1,1],[1,1,1,1],1,100000),
 ([0,0],[.1,.9],np.nan,50000),([1,1],[.1,.9],.5,np.nan)])
def test_degenerate_and_single_class_are_not_success_by_accuracy(y,s,recall,far):
 d=fixture(y,s);check_metrics(d)
 assert np.isclose(d.Recall.iloc[0],recall,equal_nan=True)
 assert np.isclose(d.FAR_per_100k.iloc[0],far,equal_nan=True)
 if len(set(y))==1:assert d.AP.isna().all()

@pytest.mark.parametrize('kind',['duplicate','denominator','metric','pooled','fraction','undefined_ap'])
def test_reject_invalid_metric_reports(kind):
 d=fixture()
 if kind=='duplicate':d=pd.concat([d,d.iloc[:1]],ignore_index=True)
 elif kind=='denominator':d.loc[0,'Benign_Windows']=3
 elif kind=='metric':d.loc[0,'Recall']=.7
 elif kind=='pooled':d=d[d.file=='ALL']
 elif kind=='fraction':d['TP']=d['TP'].astype(float);d.loc[0,'TP']=1.5
 else:d=fixture([0,0],[.1,.2]);d['AP']=0
 with pytest.raises(ValueError):check_metrics(d)

def test_equal_set_weighting_not_window_weighting():
 rows=[]
 for set_name,recall,total in [('set_01',.2,10000),('set_02',.8,100)]:
  for seed in [42,43,44]:
   rows.append(dict(set=set_name,seed=seed,method='raw',condition='B',file='ALL',operating_point='source_calibrated',Total_Windows=total,Recall=recall,FAR_per_100k=0,Attack_F1=recall,AP=recall))
 _,mean=equal_set(pd.DataFrame(rows));assert mean.loc[('raw','B'),'Recall']==pytest.approx(.5)

def test_exact_blocks_keep_prefix_collisions_and_are_idempotent():
 text='ANCHOR\n'
 for key in ['POSTHOC','POSTHOC_ABSTRACT_VI','POSTHOC_CONCLUSION']:text=exact_block(text,key,key,'ANCHOR')
 changed=exact_block(text,'POSTHOC','NEW','ANCHOR')
 assert 'POSTHOC_ABSTRACT_VI' in changed and 'POSTHOC_CONCLUSION' in changed
 assert exact_block(changed,'POSTHOC','NEW','ANCHOR')==changed
 assert r'\toprule'+'\nĐiều kiện' in table('cap','lab',['Điều kiện'],[['A']],[4])

def test_manifest_rejects_incomplete_or_changed_artifact(tmp_path):
 p=tmp_path/'manifest.json';a=tmp_path/'x';a.write_text('a')
 m={'status':'RUNNING','artifacts':{'x':sha(a)}};p.write_text(json.dumps(m))
 with pytest.raises(ValueError,match='Incomplete'):valid_manifest(p)
 m['status']='COMPLETE';p.write_text(json.dumps(m));valid_manifest(p)
 a.write_text('b')
 with pytest.raises(ValueError,match='Changed'):valid_manifest(p)

@pytest.mark.parametrize('duplicate',[False,True])
def test_full_loader_rejects_missing_or_duplicate_cells(tmp_path,monkeypatch,duplicate):
 import thesis_final.evidence as ev
 a=tmp_path/'a';b=tmp_path/'b';b.mkdir()
 for root in ([a,b] if duplicate else [a]):
  unit=root/'set_01/seed_42/raw_transformer/attempt_001';unit.mkdir(parents=True)
  fixture().to_csv(unit/'metrics.csv',index=False)
  m={'status':'COMPLETE','signature':{'set':'set_01','seed':42,'method':'raw_transformer'},'artifact_hashes':{'metrics.csv':sha(unit/'metrics.csv')}}
  (unit/'manifest.json').write_text(json.dumps(m))
 monkeypatch.setattr(ev,'BASE',a);monkeypatch.setattr(ev,'FAST',b)
 with pytest.raises(ValueError,match='Duplicate completed|Incomplete 60-cell'):ev.load_verified(tmp_path/'audit')

def test_import_legacy_top_level_writers_does_not_restore_old_sources():
 import runpy
 code=Path(__file__).resolve().parents[1];root=code.parent
 ps=[root/'thesis'/l/'main.tex' for l in ['vi','en']];before=[sha(p) for p in ps]
 for name in ['prepare_thesis_for_advisor.py','rebuild_manuscript.py']:
  runpy.run_path(str(code/'scripts'/name),run_name='import_only')
 assert before==[sha(p) for p in ps]

def test_real_generation_is_repeatable_and_does_not_modify_sources():
 code=Path(__file__).resolve().parents[1];root=code.parent;a=code/'output/thesis_supervisor_final_2026-11-09/audit'
 if not (a/'evidence_audit.json').exists():pytest.skip('Full evidence audit not available')
 ext=code/'results/content_completion_2026-11-09'
 data={'primary':pd.read_csv(a/'primary_metrics_verified.csv'),'extension':pd.read_csv(a/'extension_metrics_verified.csv'),
       'probes':pd.read_csv(ext/'probes/attempt_001/probe_results.csv'),'runtime':pd.read_csv(ext/'runtime/attempt_001/runtime.csv'),
       'external':pd.read_csv(ext/'external/attempt_001/external_metrics.csv'),'assoc':pd.read_csv(a/'assoc_source_distribution.csv')}
 ps=[root/'thesis'/l/'main.tex' for l in ['vi','en']];before={str(p):sha(p) for p in ps}
 for lang in ['vi','en']:
  old=(code/'thesis_final/templates'/lang/'main.tex').read_text(encoding='utf-8')
  first=render(old,data,lang);assert render(old,data,lang)==first
  assert first.count(r'\label{chap:results}')==1
  assert ('Chưa có kết quả full GPU' not in first)
  assert ('-11.59' in first and '94' in first) or lang=='vi'
 assert before=={str(p):sha(p) for p in ps}
