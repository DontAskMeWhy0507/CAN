"""Execute four GPU methods, retaining completed cells from the five-method plan.

Only the method list differs: it schedules independent fits, whose algorithms,
hyperparameters, source samples, seed, evaluation and native source hashes match.
Original execution manifests are copied verbatim and retained as provenance.
"""
from pathlib import Path
import sys
import json
import shutil
CODE=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(CODE),str(CODE/'src')]
import torch
import comparison.run as runner
from can_research.io import sha256_file,json_write

METHODS=['raw_transformer','structural_transformer','canbertplus','canlp']
original_valid=runner.valid_complete


def compatible_complete(path,signature):
    p=path/'manifest.json'
    if not p.exists():return False
    actual=json.loads(p.read_text())
    if actual['status']!='COMPLETE':return False
    old=actual['signature']
    if old==signature:return original_valid(path,signature)
    if old['method'] not in METHODS:raise ValueError('Cannot reuse a different algorithm')
    a={k:v for k,v in old.items() if k!='config'};b={k:v for k,v in signature.items() if k!='config'}
    ca={k:v for k,v in old['config'].items() if k!='methods'}
    cb={k:v for k,v in signature['config'].items() if k!='methods'}
    if a!=b or ca!=cb:raise ValueError(f'Completed GPU cell has incompatible source/data/config/environment: {path}')
    if not set(signature['config']['methods'])<=set(old['config']['methods']):raise ValueError('Invalid reuse method selection')
    return original_valid(path,old)


def main():
    if not torch.cuda.is_available():raise RuntimeError('GPU launcher requires CUDA; refusing an accidental CPU full run')
    args=sys.argv[1:];reuse=Path(args[args.index('--reuse-from')+1]).resolve()
    i=args.index('--reuse-from');del args[i:i+2]
    output=Path(args[args.index('--output')+1]).resolve()
    records=[]
    for source in sorted(reuse.glob('set_*/seed_*/*/attempt_*')):
        if not (source/'manifest.json').exists():continue
        m=json.loads((source/'manifest.json').read_text())
        if m['status']!='COMPLETE' or m['method'] not in METHODS:continue
        if m.get('software_validation_only'):raise ValueError('Cannot reuse pilot')
        if m['signature']['code']!=runner.fingerprints() or m['signature']['environment']!=runner.environment():
            raise ValueError('Source baseline code or environment changed')
        original_valid(source,m['signature'])
        target=output/source.relative_to(reuse)
        if target.exists():
            if sha256_file(target/'manifest.json')!=sha256_file(source/'manifest.json'):raise ValueError('Reuse target exists with different content')
        else:shutil.copytree(source,target)
        records.append({'source':str(source),'target':str(target),'manifest_sha256':sha256_file(source/'manifest.json')})
    output.mkdir(parents=True,exist_ok=True)
    json_write(output/'reuse_lineage.json',{'driver_sha256':sha256_file(Path(__file__)),'source_cells':records,
               'policy':'Original manifests unchanged; only independent-method scheduling differs. Full native code/data/config/seed/environment verified.'})
    runner.valid_complete=compatible_complete
    if '--methods' in args:raise ValueError('Dedicated four-method launcher; omit --methods')
    sys.argv=[sys.argv[0],*args,'--methods',*METHODS]
    runner.main()


if __name__=='__main__':main()
