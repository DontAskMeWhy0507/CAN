"""Data preparation, source-only pilot, comparable scoring and resumable cells."""
from pathlib import Path
import argparse
import copy
import gzip
import hashlib
import importlib.metadata
import json
import platform
import sys
import time
import subprocess
import zipfile
import numpy as np
import pandas as pd
import torch
from torch import nn
from can_research.io import sha256_file,json_write
from can_research.metrics import compute_binary_metrics,choose_threshold_on_validation
from can_research.provenance import json_safe
from .data import prepare,load_manifest,partitions,sample,training_data,batches
from .adapters import fit_adapter,CODE
from .analysis import paired_counts


def verify_upstream():
    lock=json.loads((CODE/'comparison/upstream.lock.json').read_text())
    for repo in lock:
        base=CODE/'third_party'/repo['name']
        for name,digest in repo['files'].items():
            if not (base/name).is_file() or sha256_file(base/name)!=digest:
                raise ValueError(f'Missing/changed upstream file: {base/name}; run setup')
    return lock


def setup():
    lock=json.loads((CODE/'comparison/upstream.lock.json').read_text())
    sparse={'canbertplus':['/README.md','/*.py','/requirements.txt','/model/'],
            'canlp':['/README.md','/LICENSE','/requirements.txt','/main.ipynb'],
            'crysys':['/README.md','/LICENSE','/requirements.txt','/unified_ids/']}
    for repo in lock:
        dest=CODE/'third_party'/repo['name']
        if not dest.exists():
            dest.parent.mkdir(parents=True,exist_ok=True)
            subprocess.run(['git','clone','--filter=blob:none','--no-checkout',repo['url'],str(dest)],check=True)
        # Never reset an existing modified working tree; verify it first if present.
        if (dest/'README.md').exists():
            for name,digest in repo['files'].items():
                if (dest/name).is_file() and sha256_file(dest/name)!=digest:raise ValueError(f'Locally modified vendor source: {dest/name}')
        subprocess.run(['git','sparse-checkout','set','--no-cone',*sparse[repo['name']]],cwd=dest,check=True)
        subprocess.run(['git','checkout','--detach',repo['commit']],cwd=dest,check=True)
    verify_upstream();print('Pinned upstream files verified.')


def fingerprints():
    paths=list((CODE/'comparison').glob('*.py'))+[CODE/'comparison/upstream.lock.json']
    paths += [CODE/'src/can_research'/n for n in ['features.py','models.py','metrics.py','io.py','provenance.py']]
    return {p.relative_to(CODE).as_posix():sha256_file(p) for p in sorted(paths)}


def environment():
    return {'python':platform.python_version(),'packages':{p:importlib.metadata.version(p) for p in ['torch','numpy','pandas','scipy','scikit-learn']},
            'device':torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}


def evaluate(model,entries,cache,config,out,condition,method,device,limit=None):
    out.mkdir(parents=True,exist_ok=True);files=[];all_y=[];all_s=[]
    for entry in entries:
        token=hashlib.sha256(entry['source'].encode()).hexdigest()[:16]
        target=out/(token+'.csv.gz');frame_target=out/(token+'.frames.f32')
        ys=[];scores=[];first=True;seen=0
        frame_handle=frame_target.open('wb') if config['save_frame_scores'] and method in ['canlp','canbertplus'] else None
        try:
            with gzip.open(target,'wt',encoding='utf-8',newline='') as handle:
                pilot_selected=sample(cache,[entry],cap=4)[entry['source']] if limit is not None else None
                for b in batches(cache,entry,config['eval_batch_windows'],features=method.endswith('_transformer'),tier=config['tier'],selected=pilot_selected):
                    if limit is not None:
                        take=min(len(b['y']),limit-seen)
                        if take<=0:break
                        b={k:v[:take] for k,v in b.items()}
                    s=np.asarray(model.score(b,device,config['batch_size']),float)
                    if s.shape!=b['y'].shape or not np.isfinite(s).all():raise ValueError('Invalid score output')
                    pd.DataFrame({'capture_id':entry['source'],'window_index':b['ix'],'y_true':b['y'],
                                  'start_time':b['times'][:,0],'end_time':b['times'][:,-1],method:s}).to_csv(handle,index=False,header=first)
                    first=False;seen+=len(s);ys.append(b['y']);scores.append(s)
                    if frame_handle is not None:frame_handle.write(np.asarray(model.last_frame_scores,dtype='<f4').tobytes())
        finally:
            if frame_handle is not None:frame_handle.close()
        if not ys:raise ValueError('No evaluation windows')
        y,s=np.concatenate(ys),np.concatenate(scores)
        if limit is None and len(y)!=entry['windows']:raise ValueError('Incomplete evaluation coverage')
        if frame_handle is not None:
            if frame_target.stat().st_size!=len(y)*64*4:raise ValueError('Frame score alignment failed')
        files.append({'file':entry['source'],'y':y,'score':s,'windows':len(y),'tail_frames':entry['tail_frames']})
        all_y.append(y);all_s.append(s)
        print(f'{method} {condition}: {Path(entry["source"]).name}, windows={len(y)}',flush=True)
    return files,np.concatenate(all_y),np.concatenate(all_s)


def valid_complete(path,signature):
    if not (path/'manifest.json').exists():return False
    m=json.loads((path/'manifest.json').read_text())
    if m['status']!='COMPLETE':return False
    if m['signature']!=signature:raise ValueError(f'Completed cell incompatible with current code/config/environment: {path}; use a new output')
    for name,digest in m['artifact_hashes'].items():
        if sha256_file(path/name)!=digest:raise ValueError(f'Changed output: {path/name}')
    return True


def study(cache,output,config,pilot=False):
    validate_config(config)
    verify_upstream();manifest=load_manifest(cache,verify=True)
    if config['tier']=='timed' and any(e['timestamp_inversions'] for e in manifest['files']):
        raise ValueError('Timing blocked: original CTT has timestamp inversions. Use explicit content-only protocol.')
    if config['tier'] not in ['content','timed']:raise ValueError('Invalid tier')
    torch.set_num_threads(config['cpu_threads']);device='cuda' if torch.cuda.is_available() else 'cpu'
    env=environment();code=fingerprints();output=Path(output);output.mkdir(parents=True,exist_ok=True)
    for set_name in config['sets']:
        split=partitions(manifest,set_name)
        if not all(split.values()):raise ValueError('Missing source or A-D folder')
        selected=sample(cache,split['train'],config['train_windows_per_class_per_file'],config['sampling_seed'])
        signature_base={'config':config,'cache_manifest_sha256':sha256_file(Path(cache)/'manifest.json'),
                        'code':code,'environment':env,'set':set_name,'software_validation_only':pilot}
        b=None
        for seed in config['seeds']:
            for method in config['methods']:
                base=output/set_name/f'seed_{seed}'/method
                signature={**signature_base,'seed':seed,'method':method}
                completed=[p for p in sorted(base.glob('attempt_*')) if valid_complete(p,signature)]
                if len(completed)>1:raise ValueError('Duplicate complete cells')
                if completed:print('VERIFIED',completed[0],flush=True);continue
                i=1
                while (base/f'attempt_{i:03}').exists():i+=1
                out=base/f'attempt_{i:03}';out.mkdir(parents=True)
                m={'status':'RUNNING','signature':signature,'method':method,'software_validation_only':pilot}
                json_write(out/'manifest.json',m)
                start=time.perf_counter()
                try:
                    if b is None:
                        b=training_data(cache,split['train'],selected,features=True,tier=config['tier'])
                        if set(np.unique(b['y']))!={0,1}:raise ValueError('Source sample lacks classes')
                    json_write(out/'selected_source_windows.json',selected)
                    json_write(out/'split.json',{k:[e['source'] for e in es] for k,es in split.items()})
                    print('TRAIN',set_name,seed,method,'source windows',len(b['y']),flush=True)
                    model=fit_adapter(method,b,config,seed,device)
                    train_seconds=time.perf_counter()-start
                    reports=[];limit=8 if pilot else None
                    val,y,s=evaluate(model,split['validation'],cache,config,out/'predictions/validation','validation',method,device,limit)
                    threshold=choose_threshold_on_validation(y,s,config['far_budget_per_100k'])
                    json_write(out/'calibration.json',json_safe({'threshold':threshold,'source_only':True,'benign':int((y==0).sum()),
                                     'attack':int((y==1).sum()),'metrics':compute_binary_metrics(y,y_score=s,threshold=threshold)}))
                    conditions=[('validation',val,y,s)]
                    if not pilot:
                        for condition in 'ABCD':
                            f,yy,ss=evaluate(model,split[condition],cache,config,out/'predictions'/condition,condition,method,device)
                            conditions.append((condition,f,yy,ss))
                    for condition,files,yy,ss in conditions:
                        operating={'source_calibrated':threshold}
                        if method!='assoc_rules_crysys':operating['default_0.5']=.5
                        for op,t in operating.items():
                            for row in [*files,{'file':'ALL','y':yy,'score':ss}]:
                                reports.append({'set':set_name,'seed':seed,'method':method,'condition':condition,
                                    'file':row['file'],'operating_point':op,'threshold':t,
                                    **compute_binary_metrics(row['y'],y_score=row['score'],threshold=t)})
                    pd.DataFrame(reports).to_csv(out/'metrics.csv',index=False)
                    pd.DataFrame([{'condition':c,'file':f['file'],'windows':f['windows'],'tail_frames':f['tail_frames']}
                                  for c,fs,_,_ in conditions for f in fs]).to_csv(out/'coverage.csv',index=False)
                    if isinstance(model.model,nn.Module):model.model.to('cpu')
                    torch.save(model,out/'checkpoint.pt')
                    json_write(out/'training.json',json_safe({'seconds':train_seconds,'history':model.history,
                                                            'window_count':len(b['y']),'frame_count':len(b['y'])*64}))
                    m.update(status='COMPLETE',artifact_hashes={p.relative_to(out).as_posix():sha256_file(p) for p in sorted(out.rglob('*')) if p.is_file() and p.name!='manifest.json'})
                except Exception as exc:
                    m.update(status='FAILED',failure=repr(exc));raise
                finally:json_write(out/'manifest.json',json_safe(m))
                del model
                if torch.cuda.is_available():torch.cuda.empty_cache()
    json_write(output/'invocation.json',{'status':'COMPLETE','software_validation_only':pilot,'config':config})


def summarize(output):
    output=Path(output);paths=sorted(output.glob('set_*/seed_*/*/attempt_*/manifest.json'));frames=[];signatures=[];cells=set()
    for path in paths:
        m=json.loads(path.read_text())
        if m['status']!='COMPLETE':continue
        if m.get('software_validation_only'):raise ValueError('Pilot is software validation only, not research results')
        valid_complete(path.parent,m['signature']);sig=m['signature']
        for k in ['config','cache_manifest_sha256','code','environment']:
            if signatures and sig[k]!=signatures[0][k]:raise ValueError('Incompatible runs')
        signatures.append(sig);cell=(sig['set'],sig['seed'],sig['method'])
        if cell in cells:raise ValueError('Duplicate complete cell')
        cells.add(cell);frames.append(pd.read_csv(path.parent/'metrics.csv'))
    if not frames:raise ValueError('No complete research cells')
    cfg=signatures[0]['config'];expected={(s,i,m) for s in cfg['sets'] for i in cfg['seeds'] for m in cfg['methods']}
    if cells!=expected:raise ValueError(f'Missing research cells: {sorted(expected-cells)}')
    all_rows=pd.concat(frames,ignore_index=True)
    if all_rows.duplicated(['set','seed','method','condition','file','operating_point']).any():raise ValueError('Duplicate metric rows')
    for (s,seed,method),group in all_rows[all_rows.file=='ALL'].groupby(['set','seed','method']):
        if not set('ABCD').issubset(set(group.condition)):raise ValueError('Missing A-D conditions')
    summary=output/'summary';summary.mkdir(exist_ok=True)
    all_rows.to_csv(summary/'all_metrics.csv',index=False)
    pooled=all_rows[all_rows.file=='ALL'];metrics=['Recall','FAR_per_100k','Attack_F1','AP']
    metrics=[m for m in metrics if m in pooled]
    pooled.groupby(['set','method','condition','operating_point'])[metrics].agg(['mean','std','count']).to_csv(summary/'by_seed.csv')
    per_set=pooled.groupby(['set','method','condition','operating_point'])[metrics].mean()
    per_set.groupby(['method','condition','operating_point'])[metrics].agg(['mean','count']).to_csv(summary/'equal_set_mean.csv')
    contrasts=[]
    for (s,seed,c,op),group in pooled.groupby(['set','seed','condition','operating_point']):
        rows=group.set_index('method')
        if 'structural_transformer' not in rows.index:continue
        for method in rows.index:
            if method=='structural_transformer':continue
            a=rows.loc[method];b=rows.loc['structural_transformer']
            if (a['TP']+a['FN']!=b['TP']+b['FN']) or (a['TN']+a['FP']!=b['TN']+b['FP']):raise ValueError('Mismatched evaluation denominators')
            contrasts.append(dict(set=s,seed=seed,condition=c,operating_point=op,opponent=method,
                                  **{metric:b[metric]-a[metric] for metric in metrics}))
    paired=pd.DataFrame(contrasts);paired.to_csv(summary/'paired_by_seed.csv',index=False)
    by_set=paired.groupby(['opponent','condition','operating_point','set'])[metrics].mean()
    by_set.to_csv(summary/'paired_by_set.csv')
    by_set.groupby(['opponent','condition','operating_point'])[metrics].agg(['mean','count']).to_csv(summary/'paired_equal_set_mean.csv')
    intervals=[]
    files=all_rows[all_rows.file!='ALL']
    for (s,seed,c,op),group in files.groupby(['set','seed','condition','operating_point']):
        if c=='validation':continue
        ours=group[group.method=='structural_transformer'].set_index('file').sort_index()
        if ours.empty:continue
        for opponent in sorted(set(group.method)-{'structural_transformer'}):
            other=group[group.method==opponent].set_index('file').sort_index()
            if not ours.index.equals(other.index):raise ValueError('Mismatched captures for paired bootstrap')
            for metric in ['Recall','FAR_per_100k','Attack_F1']:
                intervals.append({'set':s,'seed':seed,'condition':c,'operating_point':op,'opponent':opponent,
                                  **paired_counts(other[['TP','FP','TN','FN']].to_numpy(),ours[['TP','FP','TN','FN']].to_numpy(),metric)})
    json_write(summary/'paired_capture_bootstrap.json',json_safe(intervals))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    means=pooled[pooled.operating_point=='source_calibrated'].groupby(['method','condition'])[metrics].mean()
    for metric in metrics:
        table=means[metric].unstack('method').reindex(list('ABCD'))
        ax=table.plot(kind='bar',figsize=(10,5));ax.set_ylabel(metric);ax.set_xlabel('Condition');ax.legend(fontsize=8)
        ax.figure.tight_layout();ax.figure.savefig(summary/(metric+'.png'),dpi=160);plt.close(ax.figure)
    json_write(summary/'coverage.json',{'status':'COMPLETE_MATRIX','cells':len(cells),'expected':len(expected),
                                     'note':'Seed variability and equal-set differences; no vehicle-population confidence claim.'})
    print('Summary saved:',summary)


def validate_config(config):
    allowed={'raw_transformer','structural_transformer','canbertplus','canlp','assoc_rules_crysys'}
    if config['window_size']!=64 or config['tier'] not in ['content','timed']:raise ValueError('Only W64 content/timed supported')
    if not config['methods'] or not set(config['methods'])<=allowed or len(set(config['methods']))!=len(config['methods']):raise ValueError('Invalid/duplicate methods')
    if not config['sets'] or not set(config['sets'])<={f'set_{i:02}' for i in range(1,5)} or len(set(config['sets']))!=len(config['sets']):raise ValueError('Invalid/duplicate sets')
    if not config['seeds'] or len(set(config['seeds']))!=len(config['seeds']):raise ValueError('Invalid/duplicate seeds')
    for key in ['train_windows_per_class_per_file','epochs','canlp_epochs','bert_pretrain_epochs','bert_finetune_epochs','bert_batch_size','batch_size','eval_batch_windows','bert_hidden','bert_layers','bert_heads']:
        if not isinstance(config[key],int) or config[key]<1:raise ValueError('Invalid '+key)
    if config['bert_hidden']%config['bert_heads'] or config['bert_hidden']%2:raise ValueError('Invalid BERT dimensions')


def main():
    p=argparse.ArgumentParser();p.add_argument('--stage',choices=['setup','prepare','pilot','run','summarize','plan'],required=True)
    p.add_argument('--root',type=Path,default=CODE);p.add_argument('--cache',type=Path,default=CODE/'results/comparison_data_v1')
    p.add_argument('--output',type=Path,default=CODE/'results/comparison_content_v1')
    p.add_argument('--config',type=Path,default=CODE/'comparison/config.json');p.add_argument('--sets',nargs='+');p.add_argument('--seeds',nargs='+',type=int);p.add_argument('--methods',nargs='+')
    a=p.parse_args();config=json.loads(a.config.read_text())
    for key in ['sets','seeds','methods']:
        if getattr(a,key) is not None:config[key]=getattr(a,key)
    if a.stage=='setup':setup()
    elif a.stage=='prepare':prepare(a.root,a.cache)
    elif a.stage=='plan':print(json.dumps(config,indent=2))
    elif a.stage=='summarize':summarize(a.output)
    else:
        if a.stage=='pilot':
            config.update(sets=config['sets'][:1],seeds=config['seeds'][:1],train_windows_per_class_per_file=2,
                          epochs=1,canlp_epochs=1,bert_hidden=12,bert_layers=2,bert_heads=4,bert_pretrain_epochs=1,
                          bert_finetune_epochs=1,bert_batch_size=4,assoc_params={'k_cla':2,'n_knn':2,'n_centroid_clusters':2,'n_bound_bins':2})
        study(a.cache,a.output,config,a.stage=='pilot')


if __name__=='__main__':main()
