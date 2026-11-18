"""Preserve native KMeans fits/predict calls, cache repeated work and batch bookkeeping.

Each distinct payload is still predicted with the same one-row sklearn call as
upstream. No approximate clustering, reduced sample counts or changed thresholds.
"""
from collections import OrderedDict
import numpy as np
import pandas as pd
from comparison.adapters import assoc_class,AssocRules,frame_table

NativeAssocRules=assoc_class()
from unified_ids.dataio.windowing import windows_fixed_msgs


class FastAssocRulesIDS(NativeAssocRules):
    def _init_codec(self):
        self._names=[];self._lookup={};self._cache=OrderedDict()
        for cid,km in self.cla.models.items():
            mins,maxs=self.cla.bounds[cid];tokens=[]
            for cluster,center in enumerate(km.cluster_centers_):
                region=self.region_cluster_labels.get((cid,cluster),cluster) if self.region_cluster_labels else cluster
                # Deliberately retain upstream's scalar predict and bin arithmetic.
                q=int(self.centroid_quantizer.predict(center.reshape(1,-1))[0])
                lo=min(99,max(0,int(np.digitize(mins[cluster],self.bound_bins))-1))
                hi=min(99,max(0,int(np.digitize(maxs[cluster],self.bound_bins))-1))
                tokens.append(len(self._names));self._names.append(f'R{region}_Q{q}_B{lo}_{hi}')
            self._lookup[int(cid)]=np.asarray(tokens,np.int32)

    def _encode(self,frame):
        if not hasattr(self,'_lookup'):self._init_codec()
        ids=frame['can_id'].to_numpy(dtype=np.int64)
        data=frame[[f'data{i}' for i in range(8)]].to_numpy(dtype=np.float64)
        result=np.full(len(frame),-1,np.int32)
        for cid in np.unique(ids):
            if cid not in self.cla.models:continue
            positions=np.flatnonzero(ids==cid)
            unique,inverse=np.unique(data[positions],axis=0,return_inverse=True)
            mapped=[];km=self.cla.models[cid]
            for payload in unique:
                key=(int(cid),payload.tobytes())
                if key in self._cache:
                    token=self._cache.pop(key);self._cache[key]=token
                else:
                    cluster=int(km.predict(payload.reshape(1,-1))[0])
                    token=int(self._lookup[int(cid)][cluster]);self._cache[key]=token
                    if len(self._cache)>100000:self._cache.popitem(last=False)
                mapped.append(token)
            result[positions]=np.asarray(mapped,np.int32)[inverse]
        return result

    def _extract_window_items(self,window_df):
        if getattr(self,'_fit_frame',None) is not None:
            if getattr(self,'_fit_tokens',None) is None:self._fit_tokens=self._encode(self._fit_frame)
            tokens=self._fit_tokens[window_df.index.to_numpy(dtype=np.int64)]
        else:tokens=self._encode(window_df)
        # Same insertion sequence and native item strings, including duplicate names.
        return list(set(self._names[int(t)] for t in tokens if t>=0))

    def fit(self,df_train):
        if self.window_size!=64 or self.stride!=64:raise ValueError('Fast backend requires W64/stride64')
        if not df_train.index.equals(pd.RangeIndex(len(df_train))):
            raise ValueError('Training frame index must be contiguous')
        for name in ['_lookup','_names','_cache']:
            if hasattr(self,name):delattr(self,name)
        self._fit_frame=df_train;self._fit_tokens=None
        try:return super().fit(df_train)
        finally:self._fit_frame=None;self._fit_tokens=None

    def score_windows(self,frame):
        if self.legal_itemsets is None:raise RuntimeError('Model not fitted')
        w=self.window_size
        if w!=64 or self.stride!=64 or len(frame)%w:raise ValueError('Complete non-overlapping W64 required')
        if not frame.index.equals(pd.RangeIndex(len(frame))):raise ValueError('Reset frame index before scoring')
        windows=list(windows_fixed_msgs(frame,w,w))
        if len(windows)!=len(frame)//w:raise ValueError('Cross-capture windows unsupported')
        ids=frame['can_id'].to_numpy(np.int64).reshape(-1,w)
        known=list(self.known_ids);n=len(windows)
        unknown=~np.isin(ids,known).all(1)
        chi=np.zeros(n)
        # Accumulate in exactly the native known_ids iteration order.
        for cid in known:
            observed=(ids==cid).sum(1);expected=self.baseline_distributions[cid]*w
            if expected>0:chi+=(observed-expected)**2/expected
        cutoff=3.84*(len(known)-1 if len(known)>1 else 1)
        changed=chi>cutoff
        near=np.flatnonzero(np.isclose(chi,cutoff,rtol=1e-12,atol=1e-12))
        for index in near:changed[index]=super()._check_distribution(frame.iloc[index*w:(index+1)*w])
        active=np.flatnonzero(~(unknown|changed));scores=np.ones(n,float)
        if len(active):
            rows=(active[:,None]*w+np.arange(w)).ravel()
            tokens=self._encode(frame.iloc[rows]).reshape(len(active),w)
            for i,sequence in zip(active,tokens):
                items=list(set(self._names[int(t)] for t in sequence if t>=0))
                itemsets=self._all_itemsets(items,max_k=2)
                scores[i]=sum(item not in self.legal_itemsets for item in itemsets)/len(itemsets) if itemsets else 0.
        yield from zip(windows,scores)

    def __getstate__(self):
        state=self.__dict__.copy()
        state['_cache']=OrderedDict();state['_fit_frame']=None;state['_fit_tokens']=None
        return state


class FastAssocRulesAdapter(AssocRules):
    def fit(self,b,config,seed,device):
        params=dict(window_size=64,stride=64,random_state=seed,**config.get('assoc_params',{}))
        self.model=FastAssocRulesIDS(**params)
        benign=b['y']==0
        self.model.fit(frame_table({k:v[benign] for k,v in b.items()}));self.history=[]
