import importlib.util
import sys
from pathlib import Path
import numpy as np
import torch

CODE = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(CODE), str(CODE / 'src')]
from research_multisource.model import Reverse, balanced_indices, VehicleAdversary


def test_gradient_reversal_changes_only_encoder_gradient():
    x = torch.tensor([2.], requires_grad=True)
    w = torch.tensor([3.], requires_grad=True)
    (Reverse.apply(x, .2) * w).sum().backward()
    torch.testing.assert_close(x.grad, torch.tensor([-.6]))
    torch.testing.assert_close(w.grad, torch.tensor([2.]))


def test_balanced_sampling_and_conditional_heads():
    y = np.tile([0, 1], 9)
    d = np.repeat([0, 1, 2], 6)
    ix = next(balanced_indices(y, d, 1, 42))
    assert len(ix) == 126
    assert all(np.sum((y[ix] == c) & (d[ix] == v)) == 21 for v in range(3) for c in (0, 1))
    z = torch.randn(126, 64, requires_grad=True)
    adv = VehicleAdversary()
    loss = adv.loss(z, torch.tensor(y[ix]), torch.tensor(d[ix]), .1)
    loss.backward()
    assert torch.isfinite(z.grad).all()
    assert all(p.grad is not None for p in adv.parameters())


def test_real_inventory_quarantines_identity_conflicts_and_embargoes_targets():
    spec = importlib.util.spec_from_file_location('lovo', CODE / 'scripts/run_multisource_lovo.py')
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    entries, sources, excluded = runner.inventory(runner.load_manifest(runner.CACHE, verify=False))
    assert len(excluded) == 12
    bad = {r['hash'] for r in excluded}
    assert not bad.intersection(e['cache_sha256'] for e in entries)
    assert len({e['cache_sha256'] for e in entries}) == len(entries)
    for target in range(4):
        split = runner.split_fold(entries, sources, target)
        assert len({e['vehicle'] for e in split['train']}) == 3
        assert {e['vehicle'] for e in split['test']} == {target}
        assert not {e['source'] for e in split['test']}.intersection(e['source'] for e in split['train'])
