"""Create separate portable code and full prepared-CTT archives."""
from pathlib import Path
import argparse
import hashlib
import json
import zipfile

ROOT=Path(__file__).resolve().parents[2]


def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for data in iter(lambda:f.read(8*1024*1024),b''):h.update(data)
    return h.hexdigest()


def main():
    p=argparse.ArgumentParser();p.add_argument('--kind',choices=['code','data'],required=True)
    a=p.parse_args();out=ROOT/'code/output';out.mkdir(exist_ok=True)
    if a.kind=='data':
        base=ROOT/'code/results/comparison_data_v1'
        manifest=json.loads((base/'manifest.json').read_text())
        if manifest['status']!='COMPLETE' or len(manifest['files'])!=236:raise ValueError('Full CTT cache required')
        files=[base/'manifest.json']+[base/e['cache'] for e in manifest['files']]
        for e in manifest['files']:
            if digest(base/e['cache'])!=e['cache_sha256']:raise ValueError('Cache integrity failure')
        dest=out/'ctt_comparison_data_v1.zip'
    else:
        base=ROOT
        patterns=['code/comparison/*.py','code/comparison/*.json','code/comparison/*.txt',
                  'code/src/can_research/*.py','code/tests/*.py','code/configs/*.json',
                  'code/notebooks/0[678]_*.ipynb','code/scripts/run_comparison.py','code/scripts/package_comparison.py',
                  'code/requirements*.txt','pytest.ini','VIEC_BAN_CAN_LAM.txt','KE_HOACH_SO_SANH.txt',
                  'code/results/comparison_ready_checks_2026-11-08.json','code/results/comparison_data_audit_2026-11-08.json']
        files=sorted({p for pattern in patterns for p in ROOT.glob(pattern) if p.is_file()})
        dest=out/'comparison_runner_2026-11-08.zip'
    temp=dest.with_suffix('.zip.partial')
    with zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED,compresslevel=1,allowZip64=True) as z:
        for index,path in enumerate(files):
            z.write(path,path.relative_to(base).as_posix())
            if index%20==0:print('Packaged',index+1,'/',len(files),flush=True)
        if a.kind=='code':
            z.writestr('BUNDLE_MANIFEST.json',json.dumps({'date':'2026-11-08','files':{p.relative_to(base).as_posix():digest(p) for p in files},
                         'note':'Raw captures/cache/checkpoints and vendored repositories excluded. Notebook 06 fetches pinned upstream code; use the separate prepared-data archive.'},indent=2))
    with zipfile.ZipFile(temp) as z:
        if z.testzip() is not None:raise ValueError('Archive integrity failure')
    temp.replace(dest)
    info={'file':str(dest),'bytes':dest.stat().st_size,'sha256':digest(dest),'files':len(files)}
    dest.with_suffix('.zip.json').write_text(json.dumps(info,indent=2),encoding='utf-8')
    print(json.dumps(info,indent=2))


if __name__=='__main__':main()
