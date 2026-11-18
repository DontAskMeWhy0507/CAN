"""Exact agreement against untouched upstream implementation, including fitted rules."""
from pathlib import Path
import sys
import copy
import pickle
import numpy as np
import pandas as pd
import pytest

CODE=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(CODE),str(CODE/'src')]
from acceleration.assoc import FastAssocRulesIDS,NativeAssocRules


def frame(seed=42,windows=12):
    rng=np.random.default_rng(seed);n=windows*64
    data=rng.integers(0,12,(n,8))
    data[::4]=0
    df=pd.DataFrame({'can_id':np.tile(np.arange(4),n//4),'timestamp':np.arange(n)*.001,
                     'label':np.zeros(n,int),'_source_file':np.repeat(np.arange(windows),64)})
    for j in range(8):df[f'data{j}']=data[:,j]
    return df


@pytest.fixture(scope='module')
def models():
    from threadpoolctl import threadpool_limits
    parameters=dict(window_size=64,stride=64,k_cla=2,n_knn=2,n_centroid_clusters=2,n_bound_bins=2,random_state=42)
    source=frame()
    with threadpool_limits(limits=2):
        native=NativeAssocRules(**parameters).fit(source)
        fast=FastAssocRulesIDS(**parameters).fit(source)
    return native,fast


def test_fit_centroids_quantizers_bounds_and_rules_are_unchanged(models):
    native,fast=models
    assert native.legal_itemsets==fast.legal_itemsets
    assert native.region_cluster_labels==fast.region_cluster_labels
    assert native.baseline_distributions==fast.baseline_distributions
    for cid in native.cla.models:
        np.testing.assert_array_equal(native.cla.models[cid].cluster_centers_,fast.cla.models[cid].cluster_centers_)
        for a,b in zip(native.cla.bounds[cid],fast.cla.bounds[cid]):np.testing.assert_array_equal(a,b)
    np.testing.assert_array_equal(native.centroid_quantizer.cluster_centers_,fast.centroid_quantizer.cluster_centers_)


@pytest.mark.parametrize('kind',['training','new_payload','unknown_id','distribution','all_same_payload'])
def test_scores_and_window_metadata_exactly_match(models,kind):
    native,fast=models;test=frame(42 if kind=='training' else 84)
    if kind=='unknown_id':test.loc[:63,'can_id']=2047
    elif kind=='distribution':test.loc[64:127,'can_id']=0
    elif kind=='all_same_payload':test.loc[:,[f'data{i}' for i in range(8)]]=0
    a=list(native.score_windows(test));b=list(fast.score_windows(test))
    assert [x[0] for x in a]==[x[0] for x in b]
    np.testing.assert_array_equal([x[1] for x in a],[x[1] for x in b])


def test_extraction_is_native_and_prediction_cache_is_bounded(models):
    native,fast=models;test=frame(123,2)
    assert set(native._extract_window_items(test.iloc[:64]))==set(fast._extract_window_items(test.iloc[:64]))
    assert len(fast._cache)<=100000
    restored=pickle.loads(pickle.dumps(fast))
    assert len(restored._cache)==0
    np.testing.assert_array_equal([s for _,s in fast.score_windows(test)],[s for _,s in restored.score_windows(test)])
