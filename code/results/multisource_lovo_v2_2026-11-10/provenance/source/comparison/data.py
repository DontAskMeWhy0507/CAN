"""Lossless disk-backed CTT preparation. No prefix sampling in research caches."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd
from can_research.io import read_frames, sha256_file, source_split, CONDITIONS, json_write
from can_research.provenance import ctt_root, ctt_specs
from can_research.features import WindowExtractor
from .content_features import ContentFeatures

DTYPE = np.dtype([('timestamp','<f8'),('cid','<u2'),('dlc','u1'),('payload','u1',(8,)),('label','u1')])
SCHEMA = 'ctt-comparison-2026-11-08-v1'


def records(frame, previous=None):
    ts = frame.timestamp.to_numpy(dtype=np.float64)
    if not np.isfinite(ts).all():raise ValueError('Invalid timestamps')
    ids = frame.arbitration_id.astype(str).str.strip().str.upper().str.removeprefix('0X')
    if not ids.str.fullmatch('[0-9A-F]+').all(): raise ValueError('Invalid identifier')
    cid = ids.map(lambda s:int(s,16)).to_numpy()
    if (cid>2047).any(): raise ValueError('Extended IDs are not supported')
    text = frame.data_field.astype(str).str.strip().str.upper()
    if not text.str.fullmatch('(?:[0-9A-F]{2}){0,8}').all(): raise ValueError('Invalid payload')
    dlc = (text.str.len()//2).to_numpy()
    if 'dlc' in frame and not np.array_equal(frame.dlc.to_numpy(),dlc): raise ValueError('DLC mismatch')
    label = frame.attack.to_numpy()
    if not np.isin(label,[0,1]).all(): raise ValueError('Invalid labels')
    out = np.empty(len(frame),dtype=DTYPE)
    out['timestamp'],out['cid'],out['dlc'],out['label'] = ts,cid,dlc,label
    out['payload'] = np.frombuffer(bytes.fromhex(''.join(text.str.pad(16,side='right',fillchar='0'))),dtype=np.uint8).reshape(-1,8)
    return out


def mapped(cache, entry):
    path = Path(cache)/entry['cache']
    if path.stat().st_size != entry['frames']*DTYPE.itemsize: raise ValueError(f'Invalid cache size: {path}')
    return np.memmap(path,dtype=DTYPE,mode='r',shape=(entry['frames'],))


def load_manifest(cache, verify=True):
    cache = Path(cache)
    m = json.loads((cache/'manifest.json').read_text(encoding='utf-8'))
    if m['status']!='COMPLETE' or m['schema']!=SCHEMA: raise ValueError('Incomplete/obsolete data cache')
    # The versioned binary/validation schema governs compatibility. Retain the
    # actual preparer hash as provenance; unrelated feature/loader edits do not
    # require rewriting 193M unchanged records. Change SCHEMA when semantics change.
    if len(m.get('preparer_sha256',''))!=64 or any('timestamp_inversions' not in e for e in m['files']):
        raise ValueError('Missing data provenance or chronology audit')
    if verify:
        for e in m['files']:
            if sha256_file(cache/e['cache'])!=e['cache_sha256']: raise ValueError(f'Cache bytes changed: {e["source"]}')
    return m


def prepare(root, cache, sets=None):
    root,cache = Path(root).resolve(),Path(cache).resolve()
    sets = sets or [f'set_{i:02}' for i in range(1,5)]
    specs = ctt_specs(root,sets)
    cache.mkdir(parents=True,exist_ok=True)
    old = {}
    if (cache/'manifest.json').exists():
        p = json.loads((cache/'manifest.json').read_text(encoding='utf-8'))
        if p.get('schema')==SCHEMA:
            old = {e['source']:dict(e,prepared_by_sha256=e.get('prepared_by_sha256',p['preparer_sha256']))
                   for e in p['files'] if 'timestamp_inversions' in e}
    manifest = dict(schema=SCHEMA,status='RUNNING',root=str(root),window_size=64,
                    preparer_sha256=sha256_file(Path(__file__)),files=[],sets=sets)
    try:
        for spec in specs:
            path = Path(spec['path']); source = path.relative_to(root).as_posix()
            digest = sha256_file(path)
            existing = old.get(source)
            if existing and existing['source_sha256']==digest and (cache/existing['cache']).exists() and sha256_file(cache/existing['cache'])==existing['cache_sha256']:
                manifest['files'].append(existing)
                print('Verified cached:',source,flush=True)
                continue
            dest = hashlib.sha256(source.encode()).hexdigest()[:20]+'.bin'
            temp = cache/(dest+'.partial'); n=0; previous=None; out_hash=hashlib.sha256();inversions=0
            with temp.open('wb') as handle:
                for chunk in read_frames(path,'ctt',65536):
                    arr = records(chunk,previous)
                    inversions+=int((np.diff(arr['timestamp'])<0).sum())
                    if previous is not None and len(arr):inversions+=int(arr['timestamp'][0]<previous)
                    if len(arr): previous=float(arr['timestamp'][-1])
                    raw=arr.tobytes();handle.write(raw);out_hash.update(raw);n+=len(arr)
            if n<64: raise ValueError(f'No complete window: {path}')
            temp.replace(cache/dest)
            entry=dict(source=source,source_sha256=digest,source_bytes=path.stat().st_size,
                       cache=dest,cache_sha256=out_hash.hexdigest(),frames=n,windows=n//64,tail_frames=n%64,
                       set=path.parent.parent.name,folder=path.parent.name,timestamp_inversions=inversions,
                       prepared_by_sha256=manifest['preparer_sha256'])
            manifest['files'].append(entry)
            json_write(cache/'manifest.json',manifest)
            print('Prepared:',source,'frames=',n,flush=True)
        # No byte-identical train/validation vs test captures inside a set.
        for name in sets:
            entries=[e for e in manifest['files'] if e['set']==name]
            train={e['source_sha256'] for e in entries if e['folder']=='train_01'}
            test={e['source_sha256'] for e in entries if e['folder']!='train_01'}
            if train & test: raise ValueError(f'Identical train/test capture bytes in {name}')
            train_files=[root/e['source'] for e in entries if e['folder']=='train_01']
            tr,va=source_split(train_files)
            if {sha256_file(p) for p in tr}&{sha256_file(p) for p in va}: raise ValueError('Identical train/validation captures')
        manifest['status']='COMPLETE'
        manifest['note']='Full-file bytes/schema/finite timestamps checked; inversions recorded, never sorted or repaired. Content-only file-order comparisons supported. Does not prove physical chronology/session/subsequence independence.'
    except Exception as exc:
        manifest.update(status='FAILED',failure=repr(exc));raise
    finally: json_write(cache/'manifest.json',manifest)
    return manifest


def partitions(manifest, set_name):
    entries=[e for e in manifest['files'] if e['set']==set_name]
    source=[e for e in entries if e['folder']=='train_01']
    tr,va=source_split([Path(e['source']) for e in source])
    tr={p.as_posix() for p in tr};va={p.as_posix() for p in va}
    return {'train':[e for e in source if e['source'] in tr],
            'validation':[e for e in source if e['source'] in va],
            **{c:[e for e in entries if e['folder']==f] for c,f in CONDITIONS.items()}}


def sample(cache, entries, cap=1000, sampling_seed=20261103):
    selected={}
    for e in entries:
        a=mapped(cache,e);y=a['label'][:e['windows']*64].reshape(-1,64).max(1)
        token=f"{sampling_seed}:{Path(e['source']).name}"
        file_seed=int.from_bytes(hashlib.sha256(token.encode()).digest()[:8],'little')
        take=[]
        for cls in [0,1]:
            indices=np.flatnonzero(y==cls)
            rng=np.random.default_rng(np.random.SeedSequence([file_seed,cls]))
            take.extend(indices[np.argsort(rng.random(len(indices)),kind='stable')[:cap]].tolist())
        selected[e['source']]=sorted(take)
    return selected


def batches(cache,entry,batch_windows=128,features=False,selected=None,tier='content'):
    if tier=='timed' and entry.get('timestamp_inversions',0):raise ValueError('Timestamp inversion: timing comparison forbidden')
    a=mapped(cache,entry)
    extractor=(ContentFeatures() if tier=='content' else WindowExtractor(64,tier)) if features else None
    # Full chronological pass preserves feature history even for sampled windows.
    for start in range(0,entry['windows'],batch_windows):
        end=min(start+batch_windows,entry['windows']);r=a[start*64:end*64]
        shape=(end-start,64)
        b={'ids':np.asarray(r['cid']).reshape(shape),'data':np.asarray(r['payload']).reshape(*shape,8),
           'dlc':np.asarray(r['dlc']).reshape(shape),'frame_y':np.asarray(r['label']).reshape(shape),
           'times':np.asarray(r['timestamp']).reshape(shape),'ix':np.arange(start,end)}
        b['y']=b['frame_y'].max(1)
        b['capture']=np.full(end-start,entry['source'])
        if features:
            if tier=='content':raw,st=extractor.feed(r)
            else:
                payload=[''.join(f'{int(v):02X}' for v in row[:int(d)]) for row,d in zip(r['payload'],r['dlc'])]
                frame=pd.DataFrame({'timestamp':r['timestamp'],'arbitration_id':[f'{int(x):03X}' for x in r['cid']],
                                    'data_field':payload,'attack':r['label']})
                raw,st,y,ix,_,_=extractor.feed(frame)
                if not np.array_equal(y,b['y']) or not np.array_equal(ix,b['ix']): raise AssertionError('Feature/byte window alignment')
            b['raw'],b['structural']=raw,st
        if selected is not None:
            mask=np.isin(b['ix'],selected)
            if not mask.any():continue
            b={k:v[mask] for k,v in b.items()}
        yield b


def training_data(cache,entries,selected,features=True,tier='content'):
    parts=[]
    for e in entries:parts.extend(batches(cache,e,features=features,selected=selected[e['source']],tier=tier))
    if not parts:raise ValueError('Empty source sample')
    return {k:np.concatenate([b[k] for b in parts]) for k in parts[0]}
