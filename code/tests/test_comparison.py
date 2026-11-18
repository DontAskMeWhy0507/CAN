"""Meaningful invariants for new file-order comparison adapters and data cache."""
import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
import torch

CODE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(CODE))
from comparison.data import records,DTYPE,batches,sample
from comparison.content_features import ContentFeatures
from comparison.adapters import CANBERT,CANLP,fit_adapter,upstream_bert,load_checkpoint
from comparison.run import summarize
from comparison.analysis import paired_counts
from can_research.features import WindowExtractor
from can_research.experiment import sample_source
from can_research.metrics import compute_binary_metrics


def fixture_frames(n=64*8+3):
    rng=np.random.default_rng(73);cid=rng.integers(0,12,n);dlc=rng.integers(0,9,n)
    data=rng.integers(0,256,(n,8),dtype=np.uint8)
    return pd.DataFrame({'timestamp':np.arange(n)*.001,'arbitration_id':[f'{i:03X}' for i in cid],
                         'data_field':[''.join(f'{int(x):02X}' for x in row[:d]) for row,d in zip(data,dlc)],
                         'attack':(np.arange(n)%137==0).astype(np.int8)})


def test_vectorized_content_matches_shared_history():
    frame=fixture_frames();r=records(frame);f=ContentFeatures();shared=WindowExtractor(64,'content')
    reference=frame.copy();reference['timestamp']=np.nan
    raw,st,*_=shared.feed(reference)
    pieces=[f.feed(r[:128]),f.feed(r[128:320]),f.feed(r[320:512])]
    np.testing.assert_allclose(np.concatenate([p[0] for p in pieces]),raw[...,:28],rtol=0,atol=1e-7)
    np.testing.assert_allclose(np.concatenate([p[1] for p in pieces]),st[...,[i for i in range(32) if i not in (26,27)]],rtol=0,atol=1e-7)


def test_cache_labels_sampling_matches_original(tmp_path):
    frame=fixture_frames(64*20+3);frame.loc[:,'attack']=0;frame.loc[64*5:64*6,'attack']=1
    path=tmp_path/'capture-1.csv';frame.to_csv(path,index=False)
    r=records(frame);r.tofile(tmp_path/'one.bin')
    e=dict(source='capture-1.csv',cache='one.bin',frames=len(r),windows=len(r)//64,tail_frames=len(r)%64,timestamp_inversions=0)
    cfg=dict(window_size=64,tier='timed',chunksize=113,train_windows_per_class_per_file=3,sampling_seed=20261103)
    _,_,_,_,chosen=sample_source([path],cfg)
    expected=sorted(x['window_index'] for x in chosen)
    assert sample(tmp_path,[e],cap=3)['capture-1.csv']==expected
    b=list(batches(tmp_path,e,batch_windows=3,features=True))
    assert sum(len(p['y']) for p in b)==20
    assert all(np.array_equal(p['y'],p['frame_y'].max(1)) for p in b)


def test_inversion_is_recorded_not_silently_sorted(tmp_path):
    f=fixture_frames(128);f.loc[5,'timestamp']=-1
    a=records(f);assert a['timestamp'][5]==-1
    a.tofile(tmp_path/'one.bin')
    e=dict(source='one',cache='one.bin',frames=128,windows=2,tail_frames=0,timestamp_inversions=1)
    assert len(list(batches(tmp_path,e,features=True,tier='content')))==1
    with pytest.raises(ValueError,match='timing comparison forbidden'):list(batches(tmp_path,e,tier='timed'))


def batch_fixture():
    frame=fixture_frames(64*8);r=records(frame);raw,st=ContentFeatures().feed(r)
    y=np.zeros((8,64),np.uint8);y[4:,::3]=1
    return dict(ids=r['cid'].reshape(8,64),dlc=r['dlc'].reshape(8,64),data=r['payload'].reshape(8,64,8),
                times=r['timestamp'].reshape(8,64),frame_y=y,y=y.max(1),ix=np.arange(8),
                capture=np.full(8,'synthetic-only'),raw=raw,structural=st)


def test_source_vocab_unk_and_canonical_tokens():
    b=batch_fixture();model=CANBERT();x=model.encode(b,True)
    before=dict(model.id_vocab);other={k:v.copy() for k,v in b.items()}
    other['ids'][:]=2047
    encoded=model.encode(other)
    assert (encoded[...,0]==3).all() and model.id_vocab==before
    assert x.shape==(8,64,10)


@pytest.mark.parametrize('method',['raw_transformer','structural_transformer','canbertplus','canlp','assoc_rules_crysys'])
def test_all_five_adapters_train_score_and_serialize(method,tmp_path):
    config=json.loads((CODE/'comparison/config.json').read_text())
    config.update(epochs=1,canlp_epochs=1,bert_hidden=12,bert_layers=2,bert_heads=4,bert_batch_size=4,
                  bert_pretrain_epochs=1,bert_finetune_epochs=1,assoc_params={'k_cla':2,'n_knn':2,'n_centroid_clusters':2,'n_bound_bins':2})
    torch.set_num_threads(2);b=batch_fixture()
    model=fit_adapter(method,b,config,42,'cpu');s=model.score(b,'cpu',4)
    assert s.shape==(8,) and np.isfinite(s).all()
    if method in ['canbertplus','canlp']:
        assert model.last_frame_scores.shape==(8,64)
        np.testing.assert_equal(s,model.last_frame_scores.max(1))
    target=tmp_path/'checkpoint.pt';torch.save(model,target)
    if method=='canbertplus':
        for name in list(sys.modules):
            if name.startswith('comparison_upstream_canbert'):del sys.modules[name]
    from can_research.io import sha256_file
    restored=load_checkpoint(target,sha256_file(target))
    np.testing.assert_allclose(restored.score(b,'cpu',4),s,rtol=1e-6,atol=1e-6)


def test_pilot_cannot_be_reported_as_research(tmp_path):
    p=tmp_path/'set_01/seed_42/canlp/attempt_001';p.mkdir(parents=True)
    (p/'manifest.json').write_text(json.dumps({'status':'COMPLETE','software_validation_only':True}))
    with pytest.raises(ValueError,match='software validation'):summarize(tmp_path)


def test_paired_capture_count_intervals_and_direction():
    a=np.array([[2,3,17,8],[1,4,16,9],[3,2,18,7]])
    b=np.array([[5,1,19,5],[7,1,19,3],[8,0,20,2]])
    recall=paired_counts(a,b,'Recall',100)
    far=paired_counts(a,b,'FAR_per_100k',100)
    assert recall['estimate']>0 and far['estimate']<0
    assert recall['ci95'][0]>0 and recall['valid_replicates']==100
    assert paired_counts(a[:1],b[:1],'Recall')['ci95'] is None
    with pytest.raises(ValueError,match='denominators'):paired_counts(a,b+1,'Recall')


def test_summary_requires_complete_matrix_and_writes_paired_outputs(tmp_path):
    import hashlib
    methods=['raw_transformer','structural_transformer','assoc_rules_crysys']
    config={'sets':['set_01'],'seeds':[42],'methods':methods}
    last=None
    for method in methods:
        p=tmp_path/f'set_01/seed_42/{method}/attempt_001';p.mkdir(parents=True)
        rows=[]
        for condition in 'ABCD':
            y=np.array([0,0,1,1]);scores=np.array([.1,.2,.8,.9])
            for file in ['c1','c2','c3','ALL']:
                yy=np.tile(y,3) if file=='ALL' else y
                ss=np.tile(scores,3) if file=='ALL' else scores
                rows.append({'set':'set_01','seed':42,'method':method,'condition':condition,
                             'file':file,'operating_point':'source_calibrated','threshold':.5,
                             **compute_binary_metrics(yy,y_score=ss,threshold=.5)})
        pd.DataFrame(rows).to_csv(p/'metrics.csv',index=False)
        sig={'config':config,'cache_manifest_sha256':'fixture','code':{},'environment':{},'set':'set_01','seed':42,'method':method}
        m={'status':'COMPLETE','software_validation_only':False,'signature':sig,
           'artifact_hashes':{'metrics.csv':hashlib.sha256((p/'metrics.csv').read_bytes()).hexdigest()}}
        (p/'manifest.json').write_text(json.dumps(m));last=p/'manifest.json'
    original=last.read_text();m=json.loads(original);m['status']='FAILED';last.write_text(json.dumps(m))
    with pytest.raises(ValueError,match='Missing research cells'):summarize(tmp_path)
    last.write_text(original);summarize(tmp_path)
    result=json.loads((tmp_path/'summary/coverage.json').read_text())
    assert result['cells']==3 and result['status']=='COMPLETE_MATRIX'
    assert (tmp_path/'summary/Recall.png').is_file()
    paired=pd.read_csv(tmp_path/'summary/paired_equal_set_mean.csv',header=[0,1])
    assert not paired.empty
    intervals=json.loads((tmp_path/'summary/paired_capture_bootstrap.json').read_text())
    assert len(intervals)==24 and all(row['estimate']==0 for row in intervals)
