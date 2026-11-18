"""Vectorized content-tier features, checked against the shared WindowExtractor.

Preserves file-order same-ID history; does not assert physical time ordering.
"""
import numpy as np
import pandas as pd


class ContentFeatures:
    def __init__(self):
        self.seen=np.zeros(2048,bool)
        self.payload=np.zeros((2048,8),np.float32)
        self.mask=np.zeros((2048,8),np.float32)

    def feed(self,r):
        cid=np.asarray(r['cid'],np.int64);n=len(cid)
        if n%64:raise ValueError('Only complete windows')
        b=r['payload'].astype(np.float32)/255.
        mask=(np.arange(8)[None,:]<r['dlc'][:,None]).astype(np.float32)
        previous=pd.Series(np.arange(n)).groupby(cid,sort=False).shift().fillna(-1).to_numpy(np.int64)
        local=previous>=0;has=local|self.seen[cid]
        pb=self.payload[cid].copy();pm=self.mask[cid].copy()
        pb[local]=b[previous[local]];pm[local]=mask[previous[local]]
        delta=np.abs(b-pb)*mask*pm*has[:,None]
        raw=np.concatenate([((cid[:,None]>>np.arange(10,-1,-1))&1).astype(np.float32),
                            (r['dlc']/8).astype(np.float32)[:,None],b,mask],axis=1).reshape(-1,64,28)
        st=np.zeros((n//64,64,30),np.float32)
        st[...,:17]=raw[...,11:28]
        st[...,17:25]=delta.reshape(-1,64,8);st[...,25]=has.reshape(-1,64)
        for i,row in enumerate(cid.reshape(-1,64)):
            ids,first,inv,counts=np.unique(row,return_index=True,return_inverse=True,return_counts=True)
            rank=np.argsort(np.argsort(first))[inv]
            st[i,:,26]=counts[inv]/64.
            st[i,:,27]=rank/len(ids);st[i,:,28]=rank/64.
            pairs=row[:-1]*2048+row[1:]
            _,pinv,pc=np.unique(pairs,return_inverse=True,return_counts=True)
            st[i,1:,29]=pc[pinv]/63.
        ids,last=np.unique(cid[::-1],return_index=True);last=n-1-last
        self.payload[ids]=b[last];self.mask[ids]=mask[last];self.seen[ids]=True
        return raw,st
