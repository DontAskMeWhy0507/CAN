from pathlib import Path
import sys
sys.path[:0]=[str(Path(__file__).resolve().parents[1]),str(Path(__file__).resolve().parents[1]/'src')]
import numpy as np
import pandas as pd
import pytest
from comparison.data import DTYPE
from comparison.content_features import ContentFeatures
from extensions.content import Features,select,content_records
from can_research.features import WindowExtractor,select_features


def fixture(n=256):
    rng=np.random.default_rng(342);r=np.zeros(n,dtype=DTYPE)
    r['cid']=rng.integers(0,20,n);r['dlc']=rng.integers(0,9,n)
    r['payload']=rng.integers(0,256,(n,8));r['label']=rng.integers(0,2,n)
    r['timestamp']=np.nan
    r['payload']*=np.arange(8)<r['dlc'][:,None]
    return r


@pytest.mark.parametrize('w',[32,64,128])
def test_general_features_match_independent_scalar_extractor_and_chunk_history(w):
    r=fixture();a=Features(w);raw,st=a.feed(r)
    frame=pd.DataFrame({'timestamp':np.nan,'arbitration_id':[f'{i:X}' for i in r['cid']],
                        'data_field':[bytes(v[:d]).hex() for v,d in zip(r['payload'],r['dlc'])],'attack':r['label']})
    old=WindowExtractor(w,'content').feed(frame)
    np.testing.assert_array_equal(raw,select_features(old[0],old[1],'raw','content'))
    np.testing.assert_allclose(st,select_features(old[0],old[1],'structural','content'),atol=0,rtol=0)
    b=Features(w);parts=[b.feed(r[i:i+w]) for i in range(0,len(r),w)]
    np.testing.assert_array_equal(st,np.concatenate([p[1] for p in parts]))
    if w==64:
        reference=ContentFeatures().feed(r)
        np.testing.assert_array_equal(st,reference[1]);np.testing.assert_array_equal(raw,reference[0])
    for name in ['raw_no_id','id_only','raw_plus_structural','structural_no_delta','structural_no_local','structural_no_transition','structural_no_payload','structural_no_rank_w']:
        np.testing.assert_array_equal(select(raw,st,name),select_features(old[0],old[1],name,'content'))


def test_missing_time_remains_missing_and_invalid_input_is_not_repaired():
    f=pd.DataFrame({'timestamp':[np.nan]*2,'arbitration_id':['001','00A'],'data_field':['01','FFFF'],'dlc':[1,2],'attack':[0,1]})
    r=content_records(f);assert np.isnan(r['timestamp']).all();assert list(r['cid'])==[1,10]
    f.loc[0,'timestamp']=1
    with pytest.raises(ValueError,match='Mixed'):content_records(f)
    f['timestamp']=np.nan;f.loc[0,'dlc']=2
    with pytest.raises(ValueError,match='DLC'):content_records(f)
