import math
import numpy as np
import torch
from torch import nn
from can_research.models import CANTransformer, set_seed


class Reverse(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x, strength):
        ctx.strength = strength
        return x.view_as(x)

    @staticmethod
    def backward(ctx, grad):
        return -ctx.strength * grad, None


class VehicleAdversary(nn.Module):
    """Separate source-domain predictors for benign and attack windows."""
    def __init__(self):
        super().__init__()
        self.heads = nn.ModuleList([
            nn.Sequential(nn.LayerNorm(64), nn.Linear(64, 64), nn.ReLU(), nn.Linear(64, 3))
            for _ in range(2)])

    def loss(self, z, labels, domains, strength):
        reversed_z = Reverse.apply(z, strength)
        return torch.stack([nn.functional.cross_entropy(
            self.heads[c](reversed_z[labels == c]), domains[labels == c])
            for c in (0, 1)]).mean()


def balanced_indices(y, domains, steps, seed, per_cell=21):
    rng = np.random.default_rng(seed)
    cells = [np.flatnonzero((domains == d) & (y == c)) for d in range(3) for c in (0, 1)]
    if any(len(ix) == 0 for ix in cells):
        raise ValueError('Every source vehicle x binary label must be present')
    for _ in range(steps):
        ix = np.concatenate([rng.choice(cell, per_cell, replace=True) for cell in cells])
        yield ix[rng.permutation(len(ix))]


def train(x, y, domains, seed, cfg, adversarial, progress):
    set_seed(seed)
    model = CANTransformer(x.shape[-1]).cuda()
    adv = VehicleAdversary().cuda() if adversarial else None
    parameters = list(model.parameters()) + ([] if adv is None else list(adv.parameters()))
    optimizer = torch.optim.AdamW(parameters, lr=cfg['learning_rate'], weight_decay=cfg['weight_decay'])
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, cfg['epochs'])
    # Fixed mixed precision is shared by all four methods in this new protocol.
    scaler = torch.amp.GradScaler('cuda')
    xx = torch.as_tensor(x, device='cuda')
    yy = torch.as_tensor(y, dtype=torch.long, device='cuda')
    dd = torch.as_tensor(domains, dtype=torch.long, device='cuda')
    steps = math.ceil(len(y) / 126)
    logs = []
    for epoch in range(cfg['epochs']):
        model.train()
        if adv is not None:
            adv.train()
        loss_sum = np.zeros(2)
        for step, ix in enumerate(balanced_indices(y, domains, steps, seed * 1000 + epoch)):
            idx = torch.as_tensor(ix, device='cuda')
            strength = cfg['lambda_max'] * (2 / (1 + math.exp(-10 * (epoch * steps + step) / (cfg['epochs'] * steps))) - 1)
            optimizer.zero_grad(set_to_none=True)
            with torch.autocast('cuda', dtype=torch.float16):
                logits, z = model(xx[idx])
                task_loss = nn.functional.cross_entropy(logits, yy[idx])
                domain_loss = adv.loss(z, yy[idx], dd[idx], strength) if adv is not None else task_loss.new_zeros(())
                loss = task_loss + domain_loss
            if not torch.isfinite(loss):
                raise ValueError('Non-finite training objective')
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(parameters, 5., error_if_nonfinite=True)
            scaler.step(optimizer)
            scaler.update()
            loss_sum += [float(task_loss.detach()), float(domain_loss.detach())]
        scheduler.step()
        row = dict(epoch=epoch + 1, task_loss=loss_sum[0] / steps,
                   domain_loss=loss_sum[1] / steps, grl_strength=strength)
        logs.append(row)
        progress(row)
    return model.eval(), adv, logs


@torch.inference_mode()
def infer(model, x, batch=256, embedding=False):
    model.eval()
    scores, zs = [], []
    for start in range(0, len(x), batch):
        # Copy read-only memmaps; input values stay float32 until autocast.
        bx = torch.as_tensor(np.array(x[start:start + batch], copy=True), device='cuda')
        with torch.autocast('cuda', dtype=torch.float16):
            logits, z = model(bx)
        scores.append(logits.float().softmax(1)[:, 1].cpu().numpy())
        if embedding:
            zs.append(z.float().cpu().numpy())
    s = np.concatenate(scores)
    if not np.isfinite(s).all():
        raise ValueError('Non-finite predictions')
    return (s, np.concatenate(zs)) if embedding else s
