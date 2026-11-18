"""Evidence tables with explicit coverage and paired, equally weighted sets."""
from pathlib import Path
import json
import itertools
import numpy as np
import pandas as pd
from .io import json_write, sha256_file
from .provenance import verify_artifact, json_safe
from .features import SCHEMA_VERSION

METRICS = ['Recall', 'FAR_per_100k', 'Attack_F1', 'Precision', 'AP']
KEYS = ['set', 'tier', 'window', 'model', 'condition', 'operating_point']


def load_runs(paths):
    tables, signatures, manifests = [], [], []
    data_hashes = {}
    for path in map(Path, paths):
        path = path.resolve()
        manifest = json.loads((path/'run_manifest.json').read_text(encoding='utf-8'))
        if manifest['status'] != 'COMPLETE' or manifest['schema'] != SCHEMA_VERSION:
            raise ValueError(f'Incomplete or obsolete run: {path}')
        if manifest['config'].get('purpose') == 'software_validation_only':
            raise ValueError('Synthetic software checks are not research results.')
        config = {k: v for k, v in manifest['config'].items() if k not in ['seeds', 'sets']}
        signatures.append((config, manifest['source_hashes'], manifest.get('external_ledger_sha256'), manifest['versions']))
        for name in ['metrics.csv', 'data_manifest.csv']:
            verify_artifact(path/name, path, manifest)
        for record in pd.read_csv(path/'data_manifest.csv').to_dict('records'):
            key = (record['set'], record['role'], record['path'].replace('\\', '/'))
            if key in data_hashes and data_hashes[key] != record['sha256']:
                raise ValueError(f'Dataset changed across runs: {key}')
            data_hashes[key] = record['sha256']
        for file in path.glob('set_*/seed_*/external_manifest.json'):
            verify_artifact(file, path, manifest)
            for record in json.loads(file.read_text(encoding='utf-8')):
                key = ('external', record['name'], record['path'].replace('\\', '/').rsplit('/', 1)[-1])
                if key in data_hashes and data_hashes[key] != record['sha256']:
                    raise ValueError(f'External capture changed: {key}')
                data_hashes[key] = record['sha256']
        df = pd.read_csv(path/'metrics.csv')
        prefix = manifest['root'].replace('\\', '/').rstrip('/') + '/'
        df['file'] = df.file.map(lambda p: str(p).replace('\\', '/').removeprefix(prefix))
        actual = df[df.file.eq('ALL') & df.condition.isin(list('ABCD'))]
        expected = set(itertools.product(manifest['config']['sets'], manifest['config']['seeds'],
                                         manifest['config']['models'], list('ABCD'), ['default_0.5', 'source_calibrated']))
        columns = ['set', 'seed', 'model', 'condition', 'operating_point']
        if actual.duplicated(columns).any() or set(actual[columns].itertuples(index=False, name=None)) != expected:
            raise ValueError(f'Missing/extra model, seed or condition rows in completed run: {path}')
        if (actual['window'] != manifest['config']['window_size']).any() or (actual.tier != manifest['config']['tier']).any():
            raise ValueError('Metrics disagree with feature configuration.')
        tables.append(df)
        manifests.append((path, manifest))
    if not tables or any(s != signatures[0] for s in signatures[1:]):
        raise ValueError('Do not pool different protocols, code, external ledgers or library versions.')
    df = pd.concat(tables, ignore_index=True)
    if df.duplicated(KEYS + ['seed', 'file']).any():
        raise ValueError('Duplicate seed/capture rows: do not double-count runs.')
    return df, manifests


def paired_tables(aggregate):
    index = ['set', 'seed', 'tier', 'window', 'condition', 'operating_point']
    pairs = [('transformer:raw', 'transformer:structural'),
             ('transformer:raw', 'transformer:raw_no_id'),
             ('transformer:raw', 'transformer:raw_plus_structural'),
             ('transformer:raw_plus_structural', 'transformer:structural')]
    pairs += [('transformer:structural', m) for m in aggregate.model.unique()
              if m.startswith('transformer:structural_no_')]
    rows = []
    for reference, variant in pairs:
        a = aggregate[aggregate.model.eq(reference)].set_index(index)
        b = aggregate[aggregate.model.eq(variant)].set_index(index)
        for key in a.index.intersection(b.index):
            if a.loc[key, 'Attack_Windows'] != b.loc[key, 'Attack_Windows'] or a.loc[key, 'Benign_Windows'] != b.loc[key, 'Benign_Windows']:
                raise ValueError('Paired models were not evaluated on matching denominators.')
            row = dict(zip(index, key), reference=reference, variant=variant)
            for metric in METRICS:
                row[metric + '_delta'] = b.loc[key, metric] - a.loc[key, metric]
                row[metric + '_reference'] = a.loc[key, metric]
                row[metric + '_variant'] = b.loc[key, metric]
            rows.append(row)
    return pd.DataFrame(rows)


def summarize(paths, output=None, require_complete=False):
    df, manifests = load_runs(paths)
    config = manifests[0][1]['config']
    planned_sets = config.get('planned_sets', config['sets'])
    planned_seeds = config.get('planned_seeds', config['seeds'])
    expected = set(itertools.product(planned_sets, planned_seeds))
    actual = set(df[['set', 'seed']].itertuples(index=False, name=None))
    missing, unexpected = sorted(expected - actual), sorted(actual - expected)
    if unexpected or (require_complete and missing):
        raise ValueError(f'Incomplete research matrix: missing={missing}; unexpected={unexpected}')
    out = Path(output) if output else Path(paths[0])/'summary'
    out.mkdir(parents=True, exist_ok=True)
    aggregate = df[df.file.eq('ALL') & ~df.condition.eq('validation')].copy()
    aggregate.groupby(KEYS)[METRICS].agg(['mean', 'std', 'count']).to_csv(out/'mean_std_by_seed.csv')
    per_file = df[~df.file.eq('ALL') & ~df.condition.eq('validation')].copy()
    per_file.groupby(KEYS + ['file'])[METRICS].agg(['mean', 'std', 'count']).to_csv(out/'per_capture_mean_std.csv')
    df.to_csv(out/'all_metrics.csv', index=False)
    paired = paired_tables(aggregate[aggregate.condition.isin(list('ABCD'))])
    if len(paired):
        paired.to_csv(out/'paired_by_seed.csv', index=False)
        group = ['set', 'tier', 'window', 'condition', 'operating_point', 'reference', 'variant']
        values = [c for c in paired if c.endswith(('_delta', '_reference', '_variant'))]
        per_set = paired.groupby(group)[values].mean().reset_index()
        per_set.to_csv(out/'paired_by_set.csv', index=False)
        equal_set = per_set.groupby(group[1:])[values].mean()
        for column in values:
            equal_set[column + '_valid_sets'] = per_set.groupby(group[1:])[column].count()
        equal_set['observed_sets'] = per_set.groupby(group[1:])['set'].nunique()
        equal_set['planned_sets'] = len(planned_sets)
        equal_set['complete_matrix'] = not missing
        equal_set.to_csv(out/'paired_equal_set_mean.csv')
    report = dict(status='COMPLETE_MATRIX' if not missing else 'PARTIAL_MATRIX',
                  missing_set_seed=missing, expected_set_seed=len(expected), actual_set_seed=len(actual),
                  runs=[dict(path=str(p), sha256=sha256_file(p/'run_manifest.json')) for p, _ in manifests],
                  reporting_code_sha256=sha256_file(__file__),
                  interpretation='Paired differences average seeds within each set, then weight sets equally. Seeds and reused vehicles are not independent populations. No superiority decision is made automatically. External eligibility is separate from primary matrix completeness.')
    json_write(out/'coverage.json', json_safe(report))
    return out, aggregate
