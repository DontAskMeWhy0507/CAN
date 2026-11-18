from pathlib import Path
import sys
import json
import hashlib
import numpy as np
import pandas as pd
import pytest
CODE=Path(__file__).resolve().parents[1];sys.path[:0]=[str(CODE),str(CODE/'src')]
from acceleration.merge import merge,EXTRA
from can_research.metrics import compute_binary_metrics
from can_research.io import sha256_file


def create(root,method,methods,fast=False):
    out=root/f'set_01/seed_42/{method}/attempt_001';out.mkdir(parents=True)
    rows=[]
    for condition in 'ABCD':
        for name in ['c1','c2','c3','ALL']:
            y=np.array([0,0,1,1]);s=np.array([.1,.2,.8,.9])
            if name=='ALL':y=np.tile(y,3);s=np.tile(s,3)
            rows.append(dict(set='set_01',seed=42,method=method,condition=condition,file=name,operating_point='source_calibrated',
                             **compute_binary_metrics(y,y_score=s,threshold=.5)))
    pd.DataFrame(rows).to_csv(out/'metrics.csv',index=False)
    code={'original_source':'unchanged'}
    if fast:code.update({name:sha256_file(CODE/name) for name in EXTRA})
    sig={'set':'set_01','seed':42,'method':method,'config':{'sets':['set_01'],'seeds':[42],'methods':methods},
         'code':code,'environment':{'device':'fixture'},'cache_manifest_sha256':'same-fixture-data'}
    manifest=out/'manifest.json'
    manifest.write_text(json.dumps({'status':'COMPLETE','software_validation_only':False,'signature':sig,
        'artifact_hashes':{'metrics.csv':sha256_file(out/'metrics.csv')}}))
    return manifest


def test_merge_keeps_original_provenance_and_checks_full_matrix(tmp_path):
    a=tmp_path/'native';b=tmp_path/'fast';dest=tmp_path/'summary'
    originals=[]
    for method in ['raw_transformer','structural_transformer']:
        originals.append(create(a,method,['raw_transformer','structural_transformer']))
    last=create(b,'assoc_rules_crysys',['assoc_rules_crysys'],True);originals.append(last)
    hashes={p:sha256_file(p) for p in originals}
    merge([a,b],dest)
    assert json.loads((dest/'coverage.json').read_text())['cells']==3
    assert {p:sha256_file(p) for p in originals}==hashes
    references=json.loads((dest/'source_references.json').read_text())
    assert {r['execution_backend'] for r in references}=={'native','exact_cached_cpu'}
    m=json.loads(last.read_text());m['status']='FAILED';last.write_text(json.dumps(m))
    # The absent input root still declares no method; use incomplete seeds instead.
    p=originals[0];m=json.loads(p.read_text());m['signature']['config']['seeds']=[42,43];p.write_text(json.dumps(m))
    with pytest.raises(ValueError,match='Incompatible|Missing research'):merge([a,b],dest)


def test_merge_rejects_incompatible_data_or_pilot(tmp_path):
    a=tmp_path/'native';b=tmp_path/'fast'
    create(a,'structural_transformer',['structural_transformer'])
    path=create(b,'assoc_rules_crysys',['assoc_rules_crysys'],True)
    m=json.loads(path.read_text());m['signature']['cache_manifest_sha256']='different';path.write_text(json.dumps(m))
    with pytest.raises(ValueError,match='Incompatible'):merge([a,b],tmp_path/'out')
    m['software_validation_only']=True;path.write_text(json.dumps(m))
    with pytest.raises(ValueError,match='Pilot'):merge([a,b],tmp_path/'out')
