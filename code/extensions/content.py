"""Variable-window content features with continuous within-file history."""
import numpy as np
import pandas as pd
from comparison.data import mapped,records,DTYPE


def content_records(frame):
    ts=frame.timestamp.to_numpy(float)
    if np.isfinite(ts).all():return records(frame)
    if not np.isnan(ts).all():raise ValueError('Mixed or infinite timestamps')
    ids=frame.arbitration_id.astype(str).str.strip().str.upper().str.removeprefix('0X')
    text=frame.data_field.astype(str).str.strip().str.upper()
    if not ids.str.fullmatch('[0-9A-F]+').all() or not text.str.fullmatch('(?:[0-9A-F]{2}){0,8}').all():raise ValueError('Invalid identifier/payload')
    cid=ids.map(lambda s:int(s,16)).to_numpy();dlc=(text.str.len()//2).to_numpy()
    if (cid>2047).any() or not np.isin(frame.attack,[0,1]).all():raise ValueError('Unsupported ID/label')
    if 'dlc' in frame and not np.array_equal(frame.dlc.to_numpy(),dlc):raise ValueError('DLC mismatch')
    out=np.empty(len(frame),dtype=DTYPE)
    out['timestamp']=ts;out['cid']=cid;out['dlc']=dlc;out['label']=frame.attack.to_numpy()
    out['payload']=np.frombuffer(bytes.fromhex(''.join(text.str.pad(16,side='right',fillchar='0'))),dtype=np.uint8).reshape(-1,8)
    return out

VARIANTS=['raw','structural','raw_no_id','id_only','raw_plus_structural',
          'structural_no_delta','structural_no_local','structural_no_transition',
          'structural_no_payload','structural_no_rank_w']


class Features:
    def __init__(self,w=64):
        if w<2:raise ValueError(w)
        self.w=w;self.seen=np.zeros(2048,bool)
        self.payload=np.zeros((2048,8),np.float32);self.mask=self.payload.copy()
    def feed(self,r):
        w=self.w;cid=np.asarray(r['cid'],np.int64);n=len(cid)
        if n%w:raise ValueError('Incomplete windows')
        b=r['payload'].astype(np.float32)/255
        mask=(np.arange(8)[None,:]<r['dlc'][:,None]).astype(np.float32)
        prev=pd.Series(np.arange(n)).groupby(cid,sort=False).shift().fillna(-1).to_numpy(np.int64)
        local=prev>=0;has=local|self.seen[cid]
        pb=self.payload[cid].copy();pm=self.mask[cid].copy()
        pb[local]=b[prev[local]];pm[local]=mask[prev[local]]
        delta=np.abs(b-pb)*mask*pm*has[:,None]
        raw=np.concatenate([((cid[:,None]>>np.arange(10,-1,-1))&1).astype(np.float32),
                            (r['dlc']/8).astype(np.float32)[:,None],b,mask],1).reshape(-1,w,28)
        st=np.zeros((n//w,w,30),np.float32);st[...,:17]=raw[...,11:28]
        st[...,17:25]=delta.reshape(-1,w,8);st[...,25]=has.reshape(-1,w)
        for i,row in enumerate(cid.reshape(-1,w)):
            ids,first,inv,counts=np.unique(row,return_index=True,return_inverse=True,return_counts=True)
            rank=np.argsort(np.argsort(first))[inv]
            st[i,:,26]=counts[inv]/w;st[i,:,27]=rank/len(ids);st[i,:,28]=rank/w
            _,pinv,pc=np.unique(row[:-1]*2048+row[1:],return_inverse=True,return_counts=True)
            st[i,1:,29]=pc[pinv]/(w-1)
        ids,last=np.unique(cid[::-1],return_index=True);last=n-1-last
        self.payload[ids]=b[last];self.mask[ids]=mask[last];self.seen[ids]=True
        return raw,st


def select(raw,st,name):
    if name=='raw':return raw
    if name=='raw_no_id':return raw[...,11:]
    if name=='id_only':return raw[...,:11]
    if name=='raw_plus_structural':return np.concatenate([raw,st[...,17:]],-1)
    drop={'structural':[], 'structural_no_delta':list(range(17,26)),
          'structural_no_local':[26,27,28], 'structural_no_transition':[29],
          'structural_no_payload':list(range(1,9)), 'structural_no_rank_w':[28]}
    return st[...,[i for i in range(30) if i not in drop[name]]]


def batches(cache,e,w=64,batch=128,selected=None):
    a=mapped(cache,e);f=Features(w);count=e['frames']//w
    for start in range(0,count,batch):
        end=min(start+batch,count);r=a[start*w:end*w];raw,st=f.feed(r)
        y=np.asarray(r['label']).reshape(-1,w).max(1);ix=np.arange(start,end)
        mask=np.ones(len(y),bool) if selected is None else np.isin(ix,selected)
        if mask.any():yield raw[mask],st[mask],y[mask],ix[mask]
