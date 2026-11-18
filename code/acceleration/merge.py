"""Analyze separate native and accelerated runs without rewriting their manifests."""
from pathlib import Path
import json
import pandas as pd
from comparison.run import valid_complete
from comparison.analysis import paired_counts
from can_research.io import sha256_file,json_write
from can_research.provenance import json_safe

EXTRA={'acceleration/assoc.py','acceleration/__init__.py','scripts/run_comparison_fast.py'}


def merge(inputs,output):
    references=[];frames=[];base=None;methods=set();cells=set()
    for root in map(Path,inputs):
        if not root.is_dir():raise FileNotFoundError(root)
        before=len(references)
        for path in sorted(root.glob('set_*/seed_*/*/attempt_*/manifest.json')):
            m=json.loads(path.read_text())
            if m['status']!='COMPLETE':continue
            if m.get('software_validation_only'):raise ValueError('Pilot is not research')
            sig=m['signature'];valid_complete(path.parent,sig)
            common={k:v for k,v in sig['config'].items() if k!='methods'}
            core={k:v for k,v in sig['code'].items() if k not in EXTRA}
            compatibility={'config':common,'code':core,'cache':sig['cache_manifest_sha256'],'environment':sig['environment']}
            if base is None:base=compatibility
            elif base!=compatibility:raise ValueError('Incompatible config, native code, data or environment')
            extras=set(sig['code'])&EXTRA
            if extras:
                if extras!=EXTRA:raise ValueError('Incomplete accelerator provenance')
                code=Path(__file__).resolve().parents[1]
                for name in extras:
                    if sha256_file(code/name)!=sig['code'][name]:raise ValueError('Unknown accelerator revision')
            methods.update(sig['config']['methods'])
            cell=(sig['set'],sig['seed'],sig['method'])
            if cell in cells:raise ValueError(f'Duplicate complete cell: {cell}; select one baseline root')
            cells.add(cell)
            table=pd.read_csv(path.parent/'metrics.csv');table['execution_backend']='exact_cached_cpu' if extras else 'native'
            frames.append(table)
            references.append({'manifest':str(path.resolve()),'sha256':sha256_file(path),'cell':cell,
                               'execution_signature':sig,'execution_backend':'exact_cached_cpu' if extras else 'native'})
        if len(references)==before:raise ValueError(f'Missing completed research cells in input: {root}')
    if base is None:raise ValueError('No completed research cells')
    config=base['config'];expected={(s,i,m) for s in config['sets'] for i in config['seeds'] for m in methods}
    if cells!=expected:raise ValueError(f'Missing research cells: {sorted(expected-cells)}')
    data=pd.concat(frames,ignore_index=True)
    if data.duplicated(['set','seed','method','condition','file','operating_point']).any():raise ValueError('Duplicate metrics')
    pooled=data[(data.file=='ALL')&(data.operating_point=='source_calibrated')]
    for _,g in pooled.groupby(['set','seed','method']):
        if not set('ABCD')<=set(g.condition):raise ValueError('Missing A-D evaluations')
    metrics=['Recall','FAR_per_100k','Attack_F1','AP'];contrasts=[];intervals=[]
    for (s,seed,condition),group in pooled.groupby(['set','seed','condition']):
        rows=group.set_index('method')
        if 'structural_transformer' not in rows.index:raise ValueError('Structural comparator required')
        ours=rows.loc['structural_transformer']
        for opponent in set(rows.index)-{'structural_transformer'}:
            other=rows.loc[opponent]
            if other.TP+other.FN!=ours.TP+ours.FN or other.TN+other.FP!=ours.TN+ours.FP:raise ValueError('Mismatched denominators')
            contrasts.append({'set':s,'seed':seed,'condition':condition,'opponent':opponent,
                              **{metric:ours[metric]-other[metric] for metric in metrics}})
            if condition=='validation':continue
            f=data[(data['set']==s)&(data.seed==seed)&(data.condition==condition)&
                   (data.file!='ALL')&(data.operating_point=='source_calibrated')]
            a=f[f.method==opponent].set_index('file').sort_index();b=f[f.method=='structural_transformer'].set_index('file').sort_index()
            if not a.index.equals(b.index):raise ValueError('Mismatched capture identities')
            for metric in metrics[:3]:
                intervals.append({'set':s,'seed':seed,'condition':condition,'opponent':opponent,
                                  **paired_counts(a[['TP','FP','TN','FN']].to_numpy(),b[['TP','FP','TN','FN']].to_numpy(),metric)})
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    data.to_csv(out/'all_metrics.csv',index=False)
    pooled.groupby(['set','method','condition'])[metrics].agg(['mean','std','count']).to_csv(out/'by_seed.csv')
    paired=pd.DataFrame(contrasts);paired.to_csv(out/'paired_by_seed.csv',index=False)
    per_set=paired.groupby(['opponent','condition','set'])[metrics].mean();per_set.to_csv(out/'paired_by_set.csv')
    per_set.groupby(['opponent','condition'])[metrics].agg(['mean','count']).to_csv(out/'paired_equal_set_mean.csv')
    json_write(out/'paired_capture_bootstrap.json',json_safe(intervals))
    json_write(out/'coverage.json',{'status':'COMPLETE_MATRIX','cells':len(cells),'methods':sorted(methods),
               'analysis_code_sha256':sha256_file(Path(__file__)),
               'note':'Original execution manifests retained. Native code/data/config/environment must match; only declared exact-call caching backend may differ.'})
    json_write(out/'source_references.json',references)
    print('Merged analysis saved:',out)
