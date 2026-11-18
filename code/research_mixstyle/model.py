"""Temporal, same-label adaptation of Zhou et al. (ICLR 2021) MixStyle.

This independently written adaptation is not a reproduction of the CNN paper.
Only source training labels are used; inference never needs labels or mixing.
"""
import math
import numpy as np
import torch
from torch import nn
from can_research.models import CANTransformer, set_seed


class TemporalMixStyle(nn.Module):
    def __init__(self, p=.5, alpha=.1, eps=1e-6):
        super().__init__()
        if not (math.isfinite(p) and 0 <= p <= 1):
            raise ValueError('p must be in [0, 1]')
        if not (math.isfinite(alpha) and alpha > 0 and math.isfinite(eps) and eps > 0):
            raise ValueError('alpha and eps must be positive and finite')
        self.p, self.alpha, self.eps = p, alpha, eps

    @staticmethod
    def permutation(labels):
        perm = torch.arange(len(labels), device=labels.device)
        for label in (0, 1):
            ix = torch.where(labels == label)[0]
            perm[ix] = ix[torch.randperm(len(ix), device=labels.device)]
        return perm

    def forward(self, h, labels=None):
        if not self.training or self.p == 0:
            return h
        if h.ndim != 3 or h.shape[1] < 2:
            raise ValueError('Expected [batch, time >= 2, channels]')
        if labels is None or labels.shape != (len(h),) or labels.device != h.device:
            raise ValueError('Aligned source labels required during training')
        if not torch.all((labels == 0) | (labels == 1)):
            raise ValueError('Binary labels required')
        if len(h) < 2 or torch.rand((), device=h.device) >= self.p:
            return h
        perm = self.permutation(labels)
        mean = h.mean(1, keepdim=True).detach()
        std = (h.var(1, keepdim=True, correction=0) + self.eps).sqrt().detach()
        concentration = h.new_tensor(self.alpha)
        weight = torch.distributions.Beta(concentration, concentration).sample((len(h), 1, 1))
        mixed = ((h - mean) / std) * (weight * std + (1-weight) * std[perm])
        mixed = mixed + weight * mean + (1-weight) * mean[perm]
        # Identity for singleton classes and randomly self-paired examples.
        return torch.where((perm == torch.arange(len(h), device=h.device))[:, None, None], h, mixed)


class MixStyleTransformer(CANTransformer):
    def __init__(self, p=.5, alpha=.1, eps=1e-6):
        super().__init__(in_features=30, window_size=64)
        self.mixstyle = TemporalMixStyle(p, alpha, eps)

    def forward(self, x, labels=None):
        h = self.mixstyle(self.input_proj(x), labels)
        z = self.transformer(h + self.pos_encoder).mean(1)
        return self.classifier(z), z


def train(x, y, config, seed, device, p=.5, alpha=.1, eps=1e-6):
    from torch.utils.data import DataLoader, TensorDataset
    if x.ndim != 3 or x.shape[1:] != (64, 30) or len(x) != len(y):
        raise ValueError('Expected aligned W64/30-dimensional source data')
    if set(np.unique(y)) != {0, 1} or not np.isfinite(x).all():
        raise ValueError('Finite source features and both labels required')
    set_seed(seed)
    model = MixStyleTransformer(p, alpha, eps).to(device)
    loader = DataLoader(TensorDataset(torch.from_numpy(x), torch.from_numpy(y).long()),
                        batch_size=config['batch_size'], shuffle=True,
                        generator=torch.Generator().manual_seed(seed))
    optimizer = torch.optim.AdamW(model.parameters(), lr=config['learning_rate'],
                                 weight_decay=config['weight_decay'])
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, config['epochs'])
    history = []
    for epoch in range(config['epochs']):
        model.train()
        total = 0.
        for bx, by in loader:
            bx, by = bx.to(device), by.to(device)
            optimizer.zero_grad(set_to_none=True)
            logits, _ = model(bx, by)
            loss = nn.functional.cross_entropy(logits, by)
            if not torch.isfinite(loss):
                raise ValueError('Nonfinite training loss')
            loss.backward()
            if any(p.grad is not None and not torch.isfinite(p.grad).all() for p in model.parameters()):
                raise ValueError('Nonfinite gradient')
            optimizer.step()
            total += float(loss.detach()) * len(by)
        scheduler.step()
        history.append(dict(epoch=epoch+1, loss=total/len(y)))
        print('epoch', epoch+1, 'loss', history[-1]['loss'], flush=True)
    model.eval()
    return model, history
