import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from can_research.features import WindowExtractor, extract_windows, select_features
from can_research.io import canonical_csv, read_frames, source_split
from can_research.metrics import compute_binary_metrics, choose_threshold_on_validation, paired_capture_bootstrap


def frames(n=19):
    return pd.DataFrame({'timestamp': np.arange(n) * .002,
                         'arbitration_id': ['001', '00A', '001', '010'] * (n//4) + ['001'] * (n%4),
                         'data_field': [f'{i % 256:02X}01' for i in range(n)],
                         'attack': [int(i % 7 == 0) for i in range(n)]})


def test_metrics_do_not_invent_ap_or_far():
    m = compute_binary_metrics([1, 1], [1, 0])
    assert np.isnan(m['AP']) and np.isnan(m['FAR_per_100k'])
    assert m['Attack_F1'] == pytest.approx(2/3)
    m = compute_binary_metrics([0, 0], [0, 1], [.1, .9])
    assert m['FAR_per_100k'] == 50000 and np.isnan(m['Recall']) and np.isnan(m['AP'])
    m = compute_binary_metrics([0, 1, 0, 1], y_score=[.1, .8, .7, .9])
    assert m['AP'] == 1 and m['TP'] == 2 and m['FP'] == 1


def test_threshold_ties_and_no_target_input():
    y, s = np.array([0, 0, 1, 1]), np.array([.8, .1, .8, .9])
    threshold = choose_threshold_on_validation(y, s, 0)
    m = compute_binary_metrics(y, y_score=s, threshold=threshold)
    assert m['FP'] == 0 and m['TP'] == 1
    with pytest.raises(ValueError):
        choose_threshold_on_validation([1, 1], [.2, .4])


@pytest.mark.parametrize('tier', ['timed', 'content'])
def test_chunk_boundaries_do_not_change_context_or_windows(tier):
    df = frames()
    if tier == 'content':
        df.timestamp = np.nan
    whole = WindowExtractor(4, tier).feed(df)
    stream = WindowExtractor(4, tier)
    outputs = [stream.feed(df.iloc[a:b]) for a, b in [(0, 3), (3, 9), (9, 11), (11, 19)]]
    for col in range(6):
        np.testing.assert_allclose(np.concatenate([o[col] for o in outputs]), whole[col], equal_nan=True)
    assert stream.finish()['tail_frames'] == 3
    if tier == 'timed':
        assert whole[0][1, 0, 28] > 0  # preceding frame across window boundary


def test_consistent_id_renaming_invariance():
    df = frames(16)
    renamed = df.copy()
    renamed.arbitration_id = renamed.arbitration_id.map({'001': '700', '00A': '002', '010': '123'})
    original, _ = extract_windows(df, 4)
    changed, _ = extract_windows(renamed, 4)
    np.testing.assert_array_equal(original, changed)
    raw_a, _ = extract_windows(df, 4, representation='raw')
    raw_b, _ = extract_windows(renamed, 4, representation='raw')
    assert not np.array_equal(raw_a, raw_b)


def test_timestamps_labels_and_extended_ids_fail_loudly():
    df = frames(8)
    df.loc[6, 'timestamp'] = -1
    with pytest.raises(ValueError, match='Non-monotonic'):
        extract_windows(df, 4)
    df = frames(8)
    df.loc[0, 'arbitration_id'] = '1FFFF'
    with pytest.raises(ValueError, match='11-bit'):
        extract_windows(df, 4)
    df = frames(8)
    df['attack'] = np.nan
    with pytest.raises(ValueError, match='ground truth'):
        extract_windows(df, 4)


def test_ciciov_preserves_absent_time_and_hex_padding():
    raw = pd.DataFrame({'ID': ['041'], 'label': ['ATTACK'], **{f'DATA_{j}': ['00'] for j in range(8)}})
    df = canonical_csv(raw, 'ciciov')
    assert pd.isna(df.timestamp.iloc[0]) and df.data_field.iloc[0] == '00' * 8
    with pytest.raises(ValueError, match='timestamps'):
        extract_windows(pd.concat([df] * 4), 4)
    x, y = extract_windows(pd.concat([df] * 4), 4, tier='content')
    assert x.shape == (1, 4, 30) and y.tolist() == [1]


def test_interval_labels_not_file_labels(tmp_path):
    p = tmp_path / 'dosattack.log'
    p.write_text('(1.0) can0 123#0102\n(2.0) can0 000#0000000000000000\n(3.0) can0 123#0102\n')
    df = pd.concat(read_frames(p, 'log', 2, {'mode': 'verified_dos', 'start': 2., 'end': 2.}))
    assert df.attack.tolist() == [0, 1, 0]
    assert df.data_field.iloc[0] == '0102'  # DLC is not padded to eight


def test_ciciov_export_artifact_is_lossless_and_strict():
    from can_research.io import ciciov_byte
    assert ciciov_byte('2.0') == '02'
    assert ciciov_byte('0.0') == '00'
    assert ciciov_byte('a') == '0a'
    for bad in ['10.0', '2.5', 'nan', '256', '-1', 'GG']:
        with pytest.raises(ValueError):
            ciciov_byte(bad)


def test_declared_ctt_dlc_is_preserved_and_checked():
    d=frames(4).astype(str)
    d['DLC']='1'
    c=canonical_csv(d,'ctt')
    assert c.dlc.tolist()==[1]*4
    with pytest.raises(ValueError,match='disagrees'):
        extract_windows(c,4)


def test_discarded_tail_is_still_validated():
    d=frames(7)
    d.loc[6,'data_field']='0G'
    with pytest.raises(ValueError,match='Invalid classic-CAN payload'):
        extract_windows(d,4)


def test_external_quarantine_is_recorded_not_silently_scored(tmp_path):
    from can_research.experiment import external_specs
    (tmp_path/'good.csv').write_text('example')
    (tmp_path/'bad.csv').write_text('example')
    ledger={'datasets':[dict(name='test',enabled=True,tiers=['content'],glob='*.csv',kind='ciciov',
                            label_source='fixture',excluded_files={'bad.csv':'inconsistent export'})]}
    specs,excluded=external_specs(tmp_path,ledger,'content')
    assert [Path(s['path']).name for s in specs]==['good.csv']
    assert excluded[0]['reason']=='inconsistent export'


def test_missing_log_labels_and_shuffled_otids_rejected(tmp_path):
    p = tmp_path / 'capture.log'
    p.write_text('(1.0) can0 123#0102\n')
    with pytest.raises(ValueError, match='missing trailing'):
        list(read_frames(p, 'log', label_policy={'mode': 'trailing'}))
    with pytest.raises(ValueError, match='Shuffled'):
        list(read_frames(tmp_path / 'CAN_HCRL_OTIDS_B.csv', 'otids'))


def test_source_groups_never_split_random_windows():
    files = [Path(x) for x in ['DoS-1.csv', 'DoS-2.csv', 'rpm-1.csv', 'rpm-2.csv']]
    train, val = source_split(files)
    assert [p.name for p in train] == ['DoS-1.csv', 'rpm-1.csv']
    assert [p.name for p in val] == ['DoS-2.csv', 'rpm-2.csv']
    with pytest.raises(ValueError):
        source_split([Path('DoS-1.csv')])


def test_full_file_reservoir_keeps_late_attack(tmp_path):
    from can_research.experiment import sample_source
    df = frames(160)
    df.attack = 0
    df.loc[156:, 'attack'] = 1
    p = tmp_path / 'DoS-1.csv'
    df.to_csv(p, index=False)
    cfg = dict(window_size=4, tier='timed', chunksize=7, sampling_seed=42,
               train_windows_per_class_per_file=2)
    raw, st, y, coverage, selected = sample_source([p], cfg)
    assert y.sum() == 1 and any(s['window_index'] == 39 for s in selected)
    assert sum(r['available_windows'] for r in coverage) == 40
    assert len(y) == 3


def test_bootstrap_insufficient_groups_is_not_fake_interval():
    r = paired_capture_bootstrap([0, 1], [0, 0], [0, 1], ['one', 'one'])
    assert r['status'] == 'insufficient_capture_groups'


def test_end_to_end_checkpoint_calibration_and_streaming(tmp_path):
    from can_research.experiment import run
    from can_research.io import CONDITIONS
    from can_research.models import CANTransformer, predict_scores
    import torch
    source = tmp_path / 'data' / 'can-train-and-test' / 'set_01'
    for i, folder in enumerate(['train_01', *CONDITIONS.values()]):
        (source / folder).mkdir(parents=True)
        for capture in ([1, 2] if folder == 'train_01' else [3]):
            df = frames(64)
            df.timestamp += i * 100 + capture
            df['attack'] = np.repeat([0, 0, 1, 1], 16)
            df.to_csv(source / folder / f'DoS-{capture}.csv', index=False)
    cfg = dict(protocol='can-thesis-v2.1', purpose='software_validation_only', sets=['set_01'], seeds=[42],
               sampling_seed=42, window_size=4, tier='timed', chunksize=7,
               train_windows_per_class_per_file=8, epochs=1, batch_size=8,
               learning_rate=.001, weight_decay=.0001, far_budget_per_100k=100,
               models=['transformer:raw','transformer:structural','lr:raw','xgboost:structural'],external=False)
    out=tmp_path/'run'
    result=run(cfg,tmp_path/'data',out)
    assert (out/'run_manifest.json').exists()
    assert json.loads((out/'run_manifest.json').read_text())['status']=='COMPLETE'
    assert set(result.condition)=={'validation','A','B','C','D'}
    assert len(result[(result.file=='ALL') & (result.condition=='B')])==8
    saved=torch.load(out/'set_01/seed_42/transformer__structural.pt',weights_only=True)
    model=CANTransformer(saved['input_dim'],window_size=4)
    model.load_state_dict(saved['state_dict'])
    x,_=extract_windows(frames(8),4)
    assert np.isfinite(predict_scores(model,x)).all()
    with pytest.raises(FileExistsError):
        run(cfg,tmp_path/'data',out)
