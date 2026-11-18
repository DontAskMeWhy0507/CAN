from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import pytest
import torch
from can_research.models import CANTransformer, set_seed, train_transformer
from research_mixstyle.model import TemporalMixStyle, MixStyleTransformer, train

torch.set_num_threads(2)


def test_eval_identity_without_labels_or_rng_consumption():
    x = torch.randn(6, 64, 64)
    layer = TemporalMixStyle().eval()
    rng = torch.get_rng_state().clone()
    assert layer(x) is x
    assert torch.equal(rng, torch.get_rng_state())


def test_pairing_preserves_labels_and_is_permutation():
    labels = torch.tensor([0, 1, 1, 0, 0, 1, 0])
    for seed in range(20):
        torch.manual_seed(seed)
        perm = TemporalMixStyle.permutation(labels)
        assert torch.equal(labels[perm], labels)
        assert sorted(perm.tolist()) == list(range(len(labels)))


def test_constant_features_finite_gradient_and_no_mutation():
    x = torch.ones(4, 64, 3, requires_grad=True)
    before = x.detach().clone()
    out = TemporalMixStyle(p=1)(x, torch.tensor([0, 0, 1, 1]))
    out.sum().backward()
    assert torch.isfinite(out).all() and torch.isfinite(x.grad).all()
    assert torch.equal(x.detach(), before)


def test_singletons_remain_exactly_unchanged():
    x = torch.randn(2, 64, 3)
    assert torch.equal(TemporalMixStyle(p=1)(x, torch.tensor([0, 1])), x)


def test_mixing_changes_features_and_preserves_normalized_pattern():
    torch.manual_seed(42)
    x = torch.randn(10, 64, 4) * torch.arange(1, 11)[:, None, None]
    layer = TemporalMixStyle(p=1)
    out = layer(x, torch.zeros(10, dtype=torch.long))
    assert not torch.allclose(x, out)
    def normalize(v):
        return (v-v.mean(1, keepdim=True))/v.std(1, keepdim=True, correction=0)
    torch.testing.assert_close(normalize(x), normalize(out), atol=2e-5, rtol=2e-5)


@pytest.mark.parametrize('labels', [None, torch.tensor([0]), torch.tensor([0, 2])])
def test_training_rejects_missing_or_invalid_labels(labels):
    with pytest.raises(ValueError):
        TemporalMixStyle(p=1)(torch.randn(2, 64, 3), labels)


def test_same_weights_exact_baseline_inference_and_reload(tmp_path):
    set_seed(42)
    baseline = CANTransformer(30, window_size=64).eval()
    model = MixStyleTransformer().eval()
    model.load_state_dict(baseline.state_dict(), strict=True)
    x = torch.randn(4, 64, 30)
    with torch.no_grad():
        expected = baseline(x)
        actual = model(x)
    for a, b in zip(actual, expected):
        torch.testing.assert_close(a, b, rtol=0, atol=0)
    checkpoint = tmp_path/'model.pt'
    torch.save(model.state_dict(), checkpoint)
    restored = MixStyleTransformer().eval()
    restored.load_state_dict(torch.load(checkpoint, weights_only=True))
    with torch.no_grad():
        torch.testing.assert_close(restored(x)[0], actual[0], rtol=0, atol=0)


def test_disabled_mixstyle_matches_entire_baseline_training():
    torch.set_num_threads(2)
    rng = np.random.default_rng(40)
    x = rng.random((8, 64, 30), dtype=np.float32)
    y = np.array([0, 1]*4)
    cfg = dict(epochs=2, batch_size=4, learning_rate=.001, weight_decay=.0001)
    a, ha = train_transformer(x, y, cfg, 42, 'cpu')
    b, hb = train(x, y, cfg, 42, 'cpu', p=0)
    assert ha == hb
    for key, value in a.state_dict().items():
        torch.testing.assert_close(value, b.state_dict()[key], rtol=0, atol=0)


def test_analysis_excludes_historical_default_threshold_rows(tmp_path, monkeypatch):
    """Regression: extra baseline operating points must not inflate the matrix."""
    import json
    import pandas as pd
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
    import run_mixstyle_study as study
    from can_research.metrics import compute_binary_metrics
    base, out = tmp_path/'baseline', tmp_path/'new'
    monkeypatch.setattr(study, 'BASE', base)
    monkeypatch.setattr(study, 'complete_unit', lambda output, s: out/s)
    y = np.array([0, 1]*4)
    score = np.array([.1, .2, .3, .4, .6, .7, .8, .9])
    for s in study.SETS:
        unit = out/s
        unit.mkdir(parents=True)
        split, coverage, candidate = {'train': []}, [], []
        for condition in ['validation', *'ABCD']:
            file = s+'/'+condition+'.csv'
            split[condition] = [file]
            prediction = condition+'.npz'
            np.savez(unit/prediction, y=y, window_index=np.arange(len(y)),
                     **{f'seed_{seed}': score for seed in study.SEEDS})
            coverage.append(dict(condition=condition, file=file, prediction=prediction, windows=len(y)))
            for seed in study.SEEDS:
                for name in [file, 'ALL']:
                    candidate.append(dict(set=s, seed=seed, method=study.METHOD, condition=condition,
                        file=name, operating_point='source_calibrated', threshold=.7,
                        **compute_binary_metrics(y, y_score=score, threshold=.7)))
        (unit/'split.json').write_text(json.dumps(split))
        (unit/'coverage.json').write_text(json.dumps(coverage))
        pd.DataFrame(candidate).to_csv(unit/'metrics.csv', index=False)
        for seed in study.SEEDS:
            for rep in ['raw', 'structural']:
                rows = []
                for condition in ['validation', *'ABCD']:
                    for op, threshold in [('source_calibrated', .7), ('default_0.5', .5)]:
                        for name in [split[condition][0], 'ALL']:
                            rows.append(dict(set=s, seed=seed, method=rep+'_transformer', condition=condition,
                                file=name, operating_point=op, threshold=threshold,
                                **compute_binary_metrics(y, y_score=score, threshold=threshold)))
                folder = base/s/f'seed_{seed}'/(rep+'_transformer')/'attempt_001'
                folder.mkdir(parents=True)
                pd.DataFrame(rows).to_csv(folder/'metrics.csv', index=False)
    study.summarize(out)
    verified = pd.read_csv(out/'analysis/metrics_verified.csv')
    assert set(verified.operating_point) == {'source_calibrated'}
    assert len(verified[verified.file.eq('ALL') & verified.condition.isin(list('ABCD'))]) == 144
    intervals = json.loads((out/'analysis/capture_intervals.json').read_text())
    assert len(intervals) == 288
    assert all(row['estimate'] == 0 for row in intervals)
