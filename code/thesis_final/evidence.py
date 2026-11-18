from pathlib import Path
import hashlib,json
import numpy as np
import pandas as pd
from can_research.metrics import compute_binary_metrics
from comparison.analysis import paired_counts

CODE=Path(__file__).resolve().parents[1]
BASE=CODE/'results/comparison_gpu4_reuse_v1'
FAST=CODE/'results/assoc_exact_fast_v1'
EXT=CODE/'results/content_completion_2026-11-09'
SETS=[f'set_0{i}' for i in range(1,5)]
SEEDS=[42,43,44]
METHODS=['raw_transformer','structural_transformer','canbertplus','canlp','assoc_rules_crysys']
VARIANTS=['raw','structural','raw_no_id','id_only','raw_plus_structural','structural_no_delta','structural_no_local','structural_no_transition','structural_no_payload','structural_no_rank_w']
METRICS=['Recall','FAR_per_100k','Attack_F1','AP']

def effect_label(delta_recall,delta_far):
 if not np.isfinite([delta_recall,delta_far]).all():return 'UNDEFINED'
 if delta_recall<0:return 'RECALL_DECREASE'
 if delta_far>0:return 'INCREASED_FALSE_ALARMS_TRADEOFF'
 if delta_recall>0:return 'RECALL_GAIN_WITHOUT_FAR_INCREASE'
 return 'NO_RECALL_GAIN'

def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()

def valid_manifest(p):
 m=json.loads(Path(p).read_text(encoding='utf-8'))
 if m.get('status')!='COMPLETE':raise ValueError(f'Incomplete run: {p}')
 hashes=m.get('artifact_hashes',m.get('artifacts'))
 if not hashes:raise ValueError(f'Missing artifact hashes: {p}')
 for name,digest in hashes.items():
  if sha(Path(p).parent/name)!=digest:raise ValueError(f'Changed artifact: {Path(p).parent/name}')
 return m

def check_metrics(d):
 keys=['set','seed','method','condition','file','operating_point']
 if 'window_size' in d:keys=['window_size']+keys
 if d.duplicated(keys).any():raise ValueError('Duplicate metric cell')
 for _,r in d.iterrows():
  if any(not np.isfinite(r[k]) or r[k]!=int(r[k]) for k in ['TP','FP','TN','FN','Total_Windows','Attack_Windows','Benign_Windows']):raise ValueError('Counts must be finite integers')
  tp,fp,tn,fn=[int(r[k]) for k in ['TP','FP','TN','FN']]
  if min(tp,fp,tn,fn)<0:raise ValueError('Negative confusion count')
  pos,neg=tp+fn,fp+tn
  if pos!=r.Attack_Windows or neg!=r.Benign_Windows or pos+neg!=r.Total_Windows:raise ValueError('Inconsistent denominator')
  expected={'Recall':tp/pos if pos else np.nan,'FAR_per_100k':100000*fp/neg if neg else np.nan,'Attack_F1':2*tp/(2*tp+fp+fn) if pos else np.nan}
  for k,v in expected.items():
   if not np.isclose(r[k],v,equal_nan=True,rtol=1e-10,atol=1e-10):raise ValueError(f'Incorrect {k}')
  if not pos or not neg:
   if pd.notna(r.AP):raise ValueError('AP requires both classes')
  elif pd.isna(r.AP) or not -1e-12<=r.AP<=1+1e-12:raise ValueError('Missing or invalid AP for scored two-class run')
  extras={'Accuracy':(tp+tn)/(pos+neg) if pos+neg else np.nan,'Attack_Prevalence':pos/(pos+neg) if pos+neg else np.nan,'Precision':tp/(tp+fp) if pos and tp+fp else np.nan}
  for k,v in extras.items():
   if k in r and not np.isclose(r[k],v,equal_nan=True,rtol=1e-10,atol=1e-10):raise ValueError(f'Incorrect {k}')
  if 'PR_AUC' in r and not np.isclose(r.PR_AUC,r.AP,equal_nan=True):raise ValueError('PR_AUC alias differs from AP')
 for _,g in d.groupby([k for k in keys if k!='method']):
  if g.Attack_Windows.nunique()!=1 or g.Benign_Windows.nunique()!=1:raise ValueError('Mismatched method denominators')
 # Pooled ALL rows must equal sums of capture counts, never an average.
 group=[k for k in keys if k!='file']
 for _,g in d.groupby(group):
  allrow=g[g.file=='ALL'];files=g[g.file!='ALL']
  if len(allrow)!=1:raise ValueError('Missing pooled row')
  for k in ['TP','FP','TN','FN','Total_Windows','Attack_Windows','Benign_Windows']:
   if int(allrow.iloc[0][k])!=int(files[k].sum()):raise ValueError('Pooled capture counts differ')

def equal_set(d):
 p=d[(d.file=='ALL')&(d.operating_point=='source_calibrated')&d.condition.isin(list('ABCD'))]
 keys=(['window_size'] if 'window_size' in p else [])+['set','method','condition']
 per=p.groupby(keys)[METRICS].agg(lambda x:x.mean() if x.notna().all() else np.nan)
 mean=per.groupby([k for k in keys if k!='set'])[METRICS].agg(lambda x:x.mean() if x.notna().all() else np.nan)
 return per,mean

def verify_npz(p,y_key='y'):
 with np.load(p) as z:
  y=z[y_key]
  if not np.isin(y,[0,1]).all():raise ValueError('Invalid prediction labels')
  for k in z.files:
   if k in [y_key,'window_index']:continue
   if z[k].shape!=y.shape or not np.isfinite(z[k]).all():raise ValueError('Invalid prediction scores')

def capture_intervals(d,reference,extra=False):
 p=d[(d.file!='ALL')&(d.operating_point=='source_calibrated')&d.condition.isin(list('ABCD'))]
 keys=(['window_size'] if extra else [])+['set','seed','condition'];result=[]
 for key,g in p.groupby(keys):
  a=g[g.method==reference].set_index('file').sort_index()
  for method,b in g.groupby('method'):
   if method==reference:continue
   b=b.set_index('file').sort_index()
   if not a.index.equals(b.index):raise ValueError('Unpaired captures')
   for metric in METRICS[:3]:
    # Primary: Structural minus opponent. Extra: variant minus Structural.
    first,second=(a,b) if extra else (b,a)
    result.append(dict(zip(keys,key),**{'variant' if extra else 'opponent':method},**paired_counts(first[['TP','FP','TN','FN']].to_numpy(),second[['TP','FP','TN','FN']].to_numpy(),metric)))
 return result

def check_external(d,coverage,folder,recompute=True):
 keys=['dataset','file','seed','representation']
 if d.duplicated(keys).any():raise ValueError('Duplicate external cell')
 completed=[c for c in coverage if c['status']=='COMPLETE']
 expected={(c['dataset'],c['file'],s,r) for c in completed for s in SEEDS for r in ['raw','structural']}
 if set(d[keys].itertuples(index=False,name=None))!=expected:raise ValueError('External coverage mismatch')
 for c in completed:
  rows=d[(d.dataset==c['dataset'])&(d.file==c['file'])]
  if not (rows.Total_Windows==c['windows']).all() or c['frames']!=64*c['windows']+c['tail']:raise ValueError('External denominator mismatch')
  token=hashlib.sha256(c['file'].encode()).hexdigest()[:20]
  with np.load(folder/(token+'.npz')) as z:
   if len(z['y'])!=c['windows'] or not np.array_equal(z['window_index'],np.arange(c['windows'])):raise ValueError('External prediction alignment')
   for _,row in rows.iterrows():
    if recompute:
     m=compute_binary_metrics(z['y'],y_score=z[f'{row.representation}_{row.seed}'],threshold=row.threshold)
     for k,v in m.items():
      if isinstance(v,(int,float,np.number)) and not np.isclose(v,row[k],equal_nan=True,rtol=1e-9,atol=1e-9):raise ValueError(f'External prediction/metric mismatch: {k}')
 # Reuse the count and undefined-value checks, with one capture per condition.
 shaped=d.rename(columns={'dataset':'set','representation':'method'}).copy()
 shaped['condition']=shaped['file'];shaped['operating_point']='source_calibrated'
 pooled=shaped.copy();pooled['file']='ALL'
 check_metrics(pd.concat([shaped,pooled],ignore_index=True))

def verify_inputs(out,manifests,coverage,full=True):
 """Audit frozen source bytes and prepared records, separately from model outputs."""
 cache=CODE/'results/comparison_data_v1';mp=cache/'manifest.json';m=json.loads(mp.read_text())
 expected=sha(mp);rows={str(mp):expected}
 if m['status']!='COMPLETE' or len(m['files'])!=236:raise ValueError('Incomplete CTT cache')
 for path,digest in manifests:
  sig=json.loads(Path(path).read_text())['signature']
  if sig.get('cache_manifest_sha256',sig.get('cache_sha256',expected))!=expected:raise ValueError('Changed source cache manifest')
  for rel,h in sig.get('code',{}).items():
   if rel=='environment' and isinstance(h,dict):continue
   if not isinstance(h,str) or len(h)!=64:raise ValueError('Malformed experimental source digest')
   p=CODE/rel
   if sha(p)!=h:raise ValueError('Frozen experimental source changed: '+str(p))
   rows[str(p)]=h
 for e in m['files']:
  if e['frames']!=64*e['windows']+e['tail_frames']:raise ValueError('CTT frame/window mismatch')
  for p,h in [(CODE/e['source'],e['source_sha256']),(cache/e['cache'],e['cache_sha256'])]:
   if full and sha(p)!=h:raise ValueError('Frozen input changed: '+str(p))
   rows[str(p)]=h
 for e in coverage:
  if e['status']=='COMPLETE':
   if full and sha(e['file'])!=e['sha256']:raise ValueError('External input changed')
   rows[e['file']]=e['sha256']
 totals={k:sum(e[k] for e in m['files']) for k in ['frames','windows','timestamp_inversions']}
 if totals!={'frames':193240845,'windows':3019271,'timestamp_inversions':12527}:raise ValueError('Changed CTT totals')
 result=dict(status='PASS',mode='FULL_INPUT_BYTE_HASHES' if full else 'FROZEN_DIGEST_LEDGER_AND_CURRENT_CODE',totals=totals,files=rows)
 (Path(out)/'input_hash_audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
 if full:(Path(out)/'input_hash_audit_full.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
 return result

def load_verified(out,verify_hashes=True):
 out=Path(out);out.mkdir(parents=True,exist_ok=True)
 primary=[];refs=[];cells=set();assoc=[];verified=[]
 for root in [BASE,FAST]:
  for p in sorted(root.glob('set_*/seed_*/*/attempt_*/manifest.json')):
   m=json.loads(p.read_text());
   if m['status']!='COMPLETE':raise ValueError(f'Unfinished attempt in selected root: {p}')
   if verify_hashes:m=valid_manifest(p)
   s=m['signature'];key=(s['set'],s['seed'],s['method'])
   if key in cells:raise ValueError('Duplicate completed model')
   cells.add(key);primary.append(pd.read_csv(p.parent/'metrics.csv'));refs.append({'manifest':str(p.resolve()),'sha256':sha(p)})
   if key[2]=='assoc_rules_crysys':
    ys=[];ss=[]
    for pred in sorted((p.parent/'predictions/validation').glob('*.csv.gz')):
     a=pd.read_csv(pred);ys.append(a.y_true.to_numpy());ss.append(a.assoc_rules_crysys.to_numpy())
    y=np.concatenate(ys);scores=np.concatenate(ss);cal=json.loads((p.parent/'calibration.json').read_text());t=cal['threshold']
    for cls in [0,1]:
     v=scores[y==cls]
     assoc.append(dict(set=key[0],seed=key[1],class_label=cls,n=len(v),minimum=float(v.min()),p50=float(np.median(v)),p95=float(np.quantile(v,.95)),maximum=float(v.max()),at_global_max=int((v==scores.max()).sum()),threshold=t,alerts=int((v>=t).sum()),far_at_global_max=100000*int(((scores>=scores.max())&(y==0)).sum())/int((y==0).sum())))
   verified.append((str(p),sha(p)))
 if cells!={(s,i,m) for s in SETS for i in SEEDS for m in METHODS}:raise ValueError('Incomplete 60-cell matrix')
 if len(assoc)!=24 or any(r['maximum']!=1 or r['threshold']!=np.nextafter(1.,np.inf) or r['alerts']!=0 or (r['class_label']==0 and r['far_at_global_max']<=100) for r in assoc):raise ValueError('AssocRules narrative no longer matches frozen evidence')
 primary=pd.concat(primary,ignore_index=True);check_metrics(primary)
 ext=[];expcells=set()
 for stage in ['ablation','sensitivity']:
  for p in sorted((EXT/stage).glob('**/manifest.json')):
   m=valid_manifest(p) if verify_hashes else json.loads(p.read_text())
   if m['status']!='COMPLETE':raise ValueError('Incomplete extension')
   s=m['signature'];key=(s['set'],s['seed'],s['w'])
   if key in expcells:raise ValueError('Duplicate extension unit')
   expcells.add(key);a=pd.read_csv(p.parent/'metrics.csv');ext.append(a)
   for z in p.parent.glob('*.npz'):verify_npz(z)
   verified.append((str(p),sha(p)))
 if expcells!={(s,i,w) for s in SETS for i in SEEDS for w in [32,64,128]}:raise ValueError('Incomplete 36 extension units')
 ext=pd.concat(ext,ignore_index=True);check_metrics(ext)
 pooled=ext[(ext.file=='ALL')&(ext.operating_point=='source_calibrated')]
 expected={(s,i,w,r,c) for s in SETS for i in SEEDS for w in [32,64,128] for r in (VARIANTS if w==64 else ['raw','structural']) for c in 'ABCD'}
 if set(pooled[['set','seed','window_size','method','condition']].itertuples(index=False,name=None))!=expected:raise ValueError('Incomplete 168 model-cell evaluation')
 # W64 reused baselines must reproduce original confusion counts and metrics.
 old=primary[primary.method.isin(['raw_transformer','structural_transformer'])].copy();old['method']=old.method.str.replace('_transformer','',regex=False)
 new=ext[(ext.window_size==64)&ext.method.isin(['raw','structural'])]
 cols=['set','seed','method','condition','file','operating_point'];num=['TP','FP','TN','FN',*METRICS]
 a=old[old.condition.isin(list('ABCD'))][cols+num].sort_values(cols).reset_index(drop=True)
 b=new[cols+num].sort_values(cols).reset_index(drop=True)
 pd.testing.assert_frame_equal(a,b,check_dtype=False,rtol=1e-7,atol=1e-9)
 supplemental={}
 for name in ['probes','runtime','external']:
  ps=list((EXT/name).glob('attempt_*/manifest.json'))
  if len(ps)!=1:raise ValueError('Ambiguous supplemental attempt')
  m=valid_manifest(ps[0]) if verify_hashes else json.loads(ps[0].read_text());verified.append((str(ps[0]),sha(ps[0])))
  if m['status']!='COMPLETE':raise ValueError('Incomplete supplemental study')
  supplemental[name]=ps[0].parent
 probes=pd.read_csv(supplemental['probes']/'probe_results.csv');runtime=pd.read_csv(supplemental['runtime']/'runtime.csv');external=pd.read_csv(supplemental['external']/'external_metrics.csv');coverage=json.loads((supplemental['external']/'coverage.json').read_text())
 for z in supplemental['external'].glob('*.npz'):verify_npz(z)
 if len(probes)!=576 or len(runtime)!=4:raise ValueError('Incomplete probe/runtime results')
 if sum(r['status']=='COMPLETE' for r in coverage)!=57:raise ValueError('Unexpected external coverage')
 check_external(external,coverage,supplemental['external'],recompute=verify_hashes)
 pd.DataFrame(assoc).to_csv(out/'assoc_source_distribution.csv',index=False)
 primary.to_csv(out/'primary_metrics_verified.csv',index=False);ext.to_csv(out/'extension_metrics_verified.csv',index=False)
 for name,d in [('primary',primary),('extension',ext)]:
  per,mean=equal_set(d);per.to_csv(out/(name+'_by_set.csv'));mean.to_csv(out/(name+'_equal_set.csv'))
  keys=(['window_size'] if 'window_size' in d else [])+['set','method','condition']
  d[(d.file=='ALL')&(d.operating_point=='source_calibrated')].groupby(keys)[METRICS].agg(['mean','std','count']).to_csv(out/(name+'_seed_variability.csv'))
  intervals=capture_intervals(d,'structural' if name=='extension' else 'structural_transformer',name=='extension')
  (out/(name+'_capture_intervals.json')).write_text(json.dumps(intervals,indent=2),encoding='utf-8')
 (out/'external_exclusion_ledger.json').write_text(json.dumps(coverage,ensure_ascii=False,indent=2),encoding='utf-8')
 report=dict(status='PASS',verification_mode='FULL_ARTIFACT_HASHES_AND_EXTERNAL_PREDICTION_RECOMPUTATION' if verify_hashes else 'LAYOUT_REBUILD_USING_PREVIOUS_FULL_HASH_AUDIT',primary_cells=60,extension_model_cells=168,new_fits=144,reused_baselines=24,external_captures=57,checks=['artifact hashes (full mode)','matrix coverage and duplicates','counts and denominators','pooled capture sums','W64 baseline equality','finite and aligned extension predictions','undefined metrics','equal-set aggregation','probe/runtime coverage','recomputed paired capture intervals','external coverage, counts and predictions (full mode)'],manifest_snapshot=verified)
 (out/'evidence_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 if verify_hashes:(out/'evidence_audit_full.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 return dict(primary=primary,extension=ext,probes=probes,runtime=runtime,external=external,coverage=coverage,assoc=pd.DataFrame(assoc),report=report)
