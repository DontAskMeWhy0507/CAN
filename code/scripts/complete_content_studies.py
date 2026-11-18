"""Execute post-hoc content studies without changing the completed runner."""
from pathlib import Path
import argparse,hashlib,json,sys,time,gzip,platform,importlib.metadata
CODE=Path(__file__).resolve().parents[1];sys.path[:0]=[str(CODE),str(CODE/'src')]
import numpy as np
import pandas as pd
import torch
from extensions.content import Features,VARIANTS,select,batches,content_records
from comparison.data import load_manifest,partitions,mapped,records
from comparison.adapters import load_checkpoint
from can_research.models import train_transformer,predict_scores
from can_research.metrics import compute_binary_metrics,choose_threshold_on_validation
from can_research.io import sha256_file,json_write,read_frames
from can_research.provenance import json_safe
from can_research.probes import balanced_cells,evaluate_controls

CACHE=CODE/'results/comparison_data_v1'
OUT=CODE/'results/content_completion_2026-11-09'
BASE=CODE/'results/comparison_gpu4_reuse_v1'
CFG=json.loads((CODE/'comparison/config.json').read_text())


def write(p,v):json_write(p,json_safe(v))
def fingerprint():
    ps=[Path(__file__),*list((CODE/'extensions').glob('*.py')),
        CODE/'comparison/config.json',CODE/'configs/external_datasets.json']
    ps+=list((CODE/'comparison').glob('*.py'))+list((CODE/'src/can_research').glob('*.py'))
    ps+=list(BASE.glob('set_*/seed_*/*/attempt_001/manifest.json'))
    result={str(p.relative_to(CODE)):sha256_file(p) for p in ps}
    result['environment']={'python':platform.python_version(),'packages':{n:importlib.metadata.version(n) for n in ['torch','numpy','pandas','scikit-learn']},'gpu':torch.cuda.get_device_name(0)}
    return result


def baseline(s,seed,rep,device='cuda'):
    p=BASE/s/f'seed_{seed}'/(rep+'_transformer')/'attempt_001'
    m=json.loads((p/'manifest.json').read_text());assert m['status']=='COMPLETE'
    cp=p/'checkpoint.pt';a=load_checkpoint(cp,m['artifact_hashes']['checkpoint.pt'],device)
    return a.model,json.loads((p/'calibration.json').read_text())['threshold'],str(p/'manifest.json')


def selection(entries,w,cap):
    out={}
    for e in entries:
        y=mapped(CACHE,e)['label'][:e['frames']//w*w].reshape(-1,w).max(1)
        fs=int.from_bytes(hashlib.sha256(f"{CFG['sampling_seed']}:{Path(e['source']).name}".encode()).digest()[:8],'little')
        take=[]
        for cls in [0,1]:
            ix=np.flatnonzero(y==cls);rng=np.random.default_rng(np.random.SeedSequence([fs,cls]))
            take.extend(ix[np.argsort(rng.random(len(ix)),kind='stable')[:cap]].tolist())
        out[e['source']]=sorted(take)
    return out


def pool(entries,w,chosen):
    parts=[b for e in entries for b in batches(CACHE,e,w,selected=chosen[e['source']])]
    return tuple(np.concatenate([p[j] for p in parts]) for j in range(4))


def newrun(folder,signature):
    folder.mkdir(parents=True,exist_ok=True)
    for p in sorted(folder.glob('attempt_*/manifest.json')):
        m=json.loads(p.read_text())
        if m['status']=='COMPLETE':
            assert m['signature']==signature,'Changed study; select a new output root'
            for name,h in m['artifacts'].items():assert sha256_file(p.parent/name)==h
            return None
    dest=folder/f'attempt_{len(list(folder.glob("attempt_*")))+1:03}'
    dest.mkdir();write(dest/'manifest.json',{'status':'RUNNING','signature':signature});return dest


def finish(dest,sig,**extra):
    hashes={p.relative_to(dest).as_posix():sha256_file(p) for p in dest.rglob('*') if p.is_file() and p.name!='manifest.json'}
    write(dest/'manifest.json',dict(status='COMPLETE',signature=sig,artifacts=hashes,**extra))


def score_entries(entries,w,models,dest,condition,thresholds=None):
    all_y=[];all_scores={r:[] for r in models};rows=[]
    for e in entries:
        ys=[];scores={r:[] for r in models}
        for raw,st,y,ix in batches(CACHE,e,w):
            ys.append(y)
            for rep,model in models.items():scores[rep].append(predict_scores(model,select(raw,st,rep),'cuda',128))
        y=np.concatenate(ys);all_y.append(y);out={'y':y,'window_index':np.arange(len(y))}
        assert len(y)==e['frames']//w
        for rep,ps in scores.items():
            s=np.concatenate(ps);assert np.isfinite(s).all();out[rep]=s;all_scores[rep].append(s)
            if thresholds is not None:
                for op,t in [('source_calibrated',thresholds[rep]),('default_0.5',.5)]:
                    rows.append(dict(condition=condition,file=e['source'],method=rep,operating_point=op,threshold=t,
                                     **compute_binary_metrics(y,y_score=s,threshold=t)))
        token=hashlib.sha256(e['source'].encode()).hexdigest()[:20]
        np.savez_compressed(dest/(condition+'_'+token+'.npz'),**out)
        print(condition,e['source'],len(y),flush=True)
    yy=np.concatenate(all_y);ss={r:np.concatenate(v) for r,v in all_scores.items()}
    if thresholds is not None:
        for rep,s in ss.items():
            for op,t in [('source_calibrated',thresholds[rep]),('default_0.5',.5)]:
                rows.append(dict(condition=condition,file='ALL',method=rep,operating_point=op,threshold=t,**compute_binary_metrics(yy,y_score=s,threshold=t)))
    return yy,ss,rows


def study(manifest,stage):
    ws=[64] if stage=='ablation' else [32,128]
    for w in ws:
        variants=VARIANTS if w==64 else ['raw','structural']
        for s in CFG['sets']:
            split=partitions(manifest,s);chosen=selection(split['train'],w,1000)
            train=None
            for seed in CFG['seeds']:
                unitcfg=dict(CFG,window_size=w,methods=variants,protocol='content-posthoc-completion-2026-11-09')
                sig={'stage':stage,'set':s,'seed':seed,'w':w,'variants':variants,'config':unitcfg,
                     'cache_sha256':sha256_file(CACHE/'manifest.json'),'code':fingerprint(),'post_hoc':True}
                dest=newrun(OUT/stage/f'w{w}'/s/f'seed_{seed}',sig)
                if dest is None:continue
                try:
                    if train is None:train=pool(split['train'],w,chosen)
                    raw,st,y,_=train;models={};refs={};timing={}
                    write(dest/'selected_source_windows.json',chosen);write(dest/'split.json',split)
                    for rep in variants:
                        if w==64 and rep in ['raw','structural']:
                            models[rep],_,refs[rep]=baseline(s,seed,rep)
                        else:
                            start=time.perf_counter()
                            models[rep],history=train_transformer(select(raw,st,rep),y,unitcfg,seed,'cuda')
                            timing[rep]={'seconds':time.perf_counter()-start,'history':history}
                            torch.save({'state_dict':models[rep].state_dict(),'input_dim':select(raw,st,rep).shape[-1],'window_size':w},dest/(rep+'.pt'))
                        print('MODEL',stage,w,s,seed,rep,flush=True)
                    vy,vs,_=score_entries(split['validation'],w,models,dest,'validation')
                    thresholds={r:choose_threshold_on_validation(vy,v,CFG['far_budget_per_100k']) for r,v in vs.items()}
                    for rep in refs:
                        _,original,_=baseline(s,seed,rep)
                        assert thresholds[rep]==original,'Reused baseline calibration mismatch'
                    write(dest/'thresholds.json',thresholds);write(dest/'training.json',timing);write(dest/'baseline_lineage.json',refs)
                    rows=[]
                    for c in 'ABCD':rows.extend(score_entries(split[c],w,models,dest,c,thresholds)[2])
                    pd.DataFrame(rows).assign(set=s,seed=seed,window_size=w,stage=stage).to_csv(dest/'metrics.csv',index=False)
                    finish(dest,sig);del models;torch.cuda.empty_cache()
                except BaseException as exc:
                    write(dest/'manifest.json',dict(status='FAILED',signature=sig,error=repr(exc)));raise


def probes(manifest):
    sig={'stage':'probes','cap':200,'balanced_vehicle_attack':True,'controls_repeats':5,'code':fingerprint()}
    dest=newrun(OUT/'probes',sig)
    if dest is None:return
    data={};windows=[];selected_windows=[];hashes=set()
    for role in ['train','validation']:
        pools=[]
        for vehicle,s in enumerate(CFG['sets']):
            es=partitions(manifest,s)[role]
            for e in es:
                if e['source_sha256'] in hashes:raise ValueError('Duplicate whole probe capture')
                hashes.add(e['source_sha256'])
            chosen=selection(es,64,200);raw,st,y,ix=pool(es,64,chosen)
            pools.append((raw,st,y,np.full(len(y),vehicle)))
            windows.extend(dict(role=role,set=s,file=e['source'],window=i) for e in es for i in chosen[e['source']])
        arrays=tuple(np.concatenate([p[j] for p in pools]) for j in range(4));ix=balanced_cells(arrays[2],arrays[3],42)
        data[role]=tuple(v[ix] for v in arrays)
        role_windows=[v for v in windows if v['role']==role]
        assert len(role_windows)==len(arrays[2])
        selected_windows.extend(role_windows[i] for i in ix)
    pd.DataFrame(windows).to_csv(dest/'available_probe_windows.csv.gz',index=False)
    pd.DataFrame(selected_windows).to_csv(dest/'selected_probe_windows.csv.gz',index=False)
    rows=[]
    for s in CFG['sets']:
        for seed in CFG['seeds']:
            for rep in ['raw','structural']:
                model,_,ref=baseline(s,seed,rep);emb={}
                for role,(raw,st,y,v) in data.items():emb[role]=predict_scores(model,select(raw,st,rep),'cuda',128,True)[1]
                for target,col in [('attack',2),('vehicle',3)]:
                    rows.extend(dict(x,encoder_set=s,model_seed=seed,representation=rep,target=target,checkpoint_manifest=ref) for x in evaluate_controls(emb['train'],emb['validation'],data['train'][col],data['validation'][col],5))
                print('PROBE',s,seed,rep,flush=True)
    pd.DataFrame(rows).to_csv(dest/'probe_results.csv',index=False)
    finish(dest,sig,limitation='Balanced post-hoc linear decodability with recording-round holdout; encoder saw its own source training captures. No proof of independence or unseen-session generalization.')


def runtime(manifest):
    sig={'stage':'runtime','warmup':20,'windows':300,'repeats':3,'code':fingerprint()}
    dest=newrun(OUT/'runtime',sig)
    if dest is None:return
    e=partitions(manifest,'set_01')['validation'][0];path=CODE/e['source'];rows=[]
    for device in ['cpu','cuda']:
        for rep in ['raw','structural']:
            model,_,ref=baseline('set_01',42,rep,device);samples=[]
            for repeat in range(3):
                f=Features();chunks=iter(read_frames(path,'ctt',64))
                for i in range(320):
                    if device=='cuda':torch.cuda.synchronize()
                    start=time.perf_counter();r=records(next(chunks));raw,st=f.feed(r)
                    predict_scores(model,select(raw,st,rep),device,1)
                    if device=='cuda':torch.cuda.synchronize()
                    if i>=20:samples.append((time.perf_counter()-start)*1000)
            rows.append(dict(device=device,representation=rep,n=len(samples),p50_ms=float(np.quantile(samples,.5)),p95_ms=float(np.quantile(samples,.95)),mean_ms=float(np.mean(samples)),checkpoint_manifest=ref))
    pd.DataFrame(rows).to_csv(dest/'runtime.csv',index=False)
    finish(dest,sig,source=e,scope='Batch-one CSV parsing + conversion + both content representations + inference; cached repeated reads. No acquisition span/event latency/ECU deadline claim. Run before background GPU studies.')


def external():
    sig={'stage':'external','ledger_sha':sha256_file(CODE/'configs/external_datasets.json'),'code':fingerprint()}
    dest=newrun(OUT/'external',sig)
    if dest is None:return
    models={(seed,rep):baseline('set_01',seed,rep) for seed in CFG['seeds'] for rep in ['raw','structural']}
    ledger=json.loads((CODE/'configs/external_datasets.json').read_text());rows=[];coverage=[]
    for d in ledger['datasets']:
        paths=sorted(CODE.glob(d['glob']))
        if not d['enabled']:
            coverage.append(dict(dataset=d['name'],status='EXCLUDED',reason=d['reason']));continue
        if not paths:coverage.append(dict(dataset=d['name'],status='MISSING'));continue
        for path in paths:
            if path.name in d.get('excluded_files',{}):
                coverage.append(dict(dataset=d['name'],file=str(path),status='QUARANTINED',reason=d['excluded_files'][path.name]));continue
            f=Features();pending=None;ys=[];scores={k:[] for k in models};frames=0;inversions=0;last=None
            try:
                for chunk in read_frames(path,d['kind'],65536,d.get('label_policy')):
                    ts=chunk.timestamp.to_numpy(float)
                    if np.isfinite(ts).all():
                        inversions+=int((np.diff(ts)<0).sum())+int(last is not None and len(ts)>0 and ts[0]<last)
                        if len(ts):last=ts[-1]
                    # Use strict byte/ID/label validation; timestamp remains absent for content-only inputs.
                    r=content_records(chunk)
                    frames+=len(r);r=np.concatenate([pending,r]) if pending is not None else r
                    n=len(r)//64*64;pending=r[n:].copy()
                    if not n:continue
                    raw,st=f.feed(r[:n]);ys.append(r['label'][:n].reshape(-1,64).max(1))
                    for k,(model,t,ref) in models.items():scores[k].append(predict_scores(model,select(raw,st,k[1]),'cuda',128))
                y=np.concatenate(ys);out={'y':y,'window_index':np.arange(len(y))}
                for (seed,rep),ss in scores.items():
                    score=np.concatenate(ss);out[f'{rep}_{seed}']=score;t=models[(seed,rep)][1]
                    rows.append(dict(dataset=d['name'],file=str(path),seed=seed,representation=rep,threshold=t,**compute_binary_metrics(y,y_score=score,threshold=t)))
                np.savez_compressed(dest/(hashlib.sha256(str(path).encode()).hexdigest()[:20]+'.npz'),**out)
                coverage.append(dict(dataset=d['name'],file=str(path),sha256=sha256_file(path),status='COMPLETE',frames=frames,windows=len(y),tail=len(pending),timestamp_inversions=inversions))
            except (ValueError,StopIteration) as exc:
                coverage.append(dict(dataset=d['name'],file=str(path),status='EXCLUDED_SCHEMA_OR_LABEL',reason=str(exc)))
            print('EXTERNAL',path,coverage[-1]['status'],flush=True)
    pd.DataFrame(rows).to_csv(dest/'external_metrics.csv',index=False);write(dest/'coverage.json',coverage)
    finish(dest,sig,scope='Frozen Set1 source models, no target calibration. Content/file-order only; missing timestamps not used. Benign-only captures provide FAR, not attack discrimination; full exclusions retained. Automotive benign/DoS recordings share background traffic.')


def main():
    p=argparse.ArgumentParser();p.add_argument('--stage',choices=['runtime','probes','external','ablation','sensitivity','all'],default='all');a=p.parse_args()
    assert torch.cuda.is_available(),'Full study requires GPU';torch.set_num_threads(4);OUT.mkdir(parents=True,exist_ok=True)
    m=load_manifest(CACHE,verify=True)
    write(OUT/'protocol.json',dict(protocol='content-posthoc-completion-2026-11-09',post_hoc=True,code=fingerprint(),config=CFG,
          matrix='W64: 96 new ablation fits + 24 reused baselines; W32/W128: 48 new fits',aliases={'payload_only':'raw_no_id','structural_no_timing':'structural'},
          scope='Additional evidence after original targets were inspected. Same source-only threshold policy. Never replace the original primary result or select variants by target score.'))
    for stage in (['runtime','probes','external','ablation','sensitivity'] if a.stage=='all' else [a.stage]):
        write(OUT/'progress.json',dict(stage=stage,status='RUNNING',pid=__import__('os').getpid()))
        if stage=='runtime':runtime(m)
        elif stage=='probes':probes(m)
        elif stage=='external':external()
        else:study(m,stage)
    write(OUT/'progress.json',dict(status='COMPLETE',scope=a.stage))


if __name__=='__main__':main()
