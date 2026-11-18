"""Measure exact agreement and CPU time on sampled real source windows."""
from pathlib import Path
import argparse
import sys
import json
import time
import statistics
import warnings
from collections import OrderedDict
import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits
CODE=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(CODE),str(CODE/'src')]
from acceleration.assoc import FastAssocRulesIDS,NativeAssocRules
from comparison.adapters import frame_table
from comparison.data import load_manifest,partitions,sample,training_data,batches
from can_research.io import json_write,sha256_file


def main():
    p=argparse.ArgumentParser();p.add_argument('--cache',type=Path,default=CODE/'results/comparison_data_v1')
    p.add_argument('--output',type=Path,default=CODE/'results/assoc_speed_check_2026-11-08.json')
    a=p.parse_args();manifest=load_manifest(a.cache,verify=False);split=partitions(manifest,'set_01')
    selected=sample(a.cache,split['train'],cap=2)
    b=training_data(a.cache,split['train'],selected,features=False)
    train=frame_table({k:v[b['y']==0] for k,v in b.items()})
    pieces=[]
    for e in split['validation']:
        chosen=sample(a.cache,[e],cap=8)[e['source']]
        pieces.extend(batches(a.cache,e,selected=chosen))
    validation={k:np.concatenate([part[k] for part in pieces]) for k in pieces[0]}
    test=frame_table(validation)
    parameters=dict(window_size=64,stride=64,k_cla=2,n_knn=2,n_centroid_clusters=2,n_bound_bins=2,random_state=42)
    models={};fit_times={};warning_counts={}
    with threadpool_limits(limits=4):
        for name,cls in [('native',NativeAssocRules),('fast',FastAssocRulesIDS)]:
            with warnings.catch_warnings(record=True) as caught:
                start=time.perf_counter();models[name]=cls(**parameters).fit(train)
                fit_times[name]=time.perf_counter()-start;warning_counts[name]=len(caught)
        native,fast=models['native'],models['fast']
        assert native.legal_itemsets==fast.legal_itemsets
        for cid in native.cla.models:
            np.testing.assert_array_equal(native.cla.models[cid].cluster_centers_,fast.cla.models[cid].cluster_centers_)
        times={};scores={}
        for name,model in models.items():
            times[name]=[]
            for _ in range(3):
                if name=='fast':model._cache=OrderedDict()
                start=time.perf_counter();values=[s for _,s in model.score_windows(test)]
                times[name].append(time.perf_counter()-start);scores[name]=np.array(values)
        np.testing.assert_array_equal(scores['native'],scores['fast'])
    report={'date':'2026-11-08','purpose':'software_runtime_validation_only','parameters':parameters,
            'source_training_frames':len(train),'source_validation_windows':len(scores['native']),
            'exact_rule_set_match':True,'exact_centroid_match':True,'exact_score_match':True,
            'max_absolute_score_error':float(np.abs(scores['native']-scores['fast']).max()),
            'fit_seconds':fit_times,'score_seconds_three_repeats':times,
            'score_speedup':statistics.median(times['native'])/statistics.median(times['fast']),
            'fit_speedup':fit_times['native']/fit_times['fast'],'clustering_warning_counts':warning_counts,
            'cache_manifest_sha256':sha256_file(a.cache/'manifest.json'),
            'backend_sha256':sha256_file(CODE/'acceleration/assoc.py'),
            'scope':'Small source-only k=2 pilot. No claim of equal speedup on full k=300 study; no accuracy result.'}
    json_write(a.output,report);print(json.dumps(report,indent=2))


if __name__=='__main__':main()
