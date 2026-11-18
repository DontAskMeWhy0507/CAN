"""Matched models. Input dimension is the only Transformer variant difference."""
from __future__ import annotations
import random
import numpy as np
import torch
from torch import nn


def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    torch.use_deterministic_algorithms(True, warn_only=True)


class CANTransformer(nn.Module):
    def __init__(self, in_features=32, d_model=64, nhead=4, num_layers=2,
                 dim_feedforward=128, dropout=.1, window_size=64):
        super().__init__()
        self.input_proj = nn.Linear(in_features, d_model)
        self.pos_encoder = nn.Parameter(torch.randn(1, window_size, d_model) * .02)
        layer = nn.TransformerEncoderLayer(d_model, nhead, dim_feedforward,
                                           dropout, activation='gelu', batch_first=True)
        self.transformer = nn.TransformerEncoder(layer, num_layers, enable_nested_tensor=False)
        self.classifier = nn.Sequential(nn.LayerNorm(d_model), nn.Linear(d_model, 32),
                                        nn.ReLU(), nn.Linear(32, 2))

    def forward(self, x):
        z = self.transformer(self.input_proj(x) + self.pos_encoder).mean(1)
        return self.classifier(z), z


def train_transformer(x, y, config, seed, device):
    from torch.utils.data import DataLoader, TensorDataset
    if set(np.unique(y)) != {0, 1}:
        raise ValueError('Training requires both classes.')
    set_seed(seed)
    model = CANTransformer(x.shape[-1], window_size=x.shape[1]).to(device)
    generator = torch.Generator().manual_seed(seed)
    loader = DataLoader(TensorDataset(torch.from_numpy(x), torch.from_numpy(y).long()),
                        batch_size=config['batch_size'], shuffle=True, generator=generator)
    optimizer = torch.optim.AdamW(model.parameters(), lr=config['learning_rate'],
                                  weight_decay=config['weight_decay'])
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, config['epochs'])
    loss_fn, log = nn.CrossEntropyLoss(), []
    for epoch in range(config['epochs']):
        model.train()
        total = 0.
        for bx, by in loader:
            bx, by = bx.to(device), by.to(device)
            optimizer.zero_grad(set_to_none=True)
            logits, _ = model(bx)
            loss = loss_fn(logits, by)
            loss.backward()
            optimizer.step()
            total += float(loss.detach()) * len(by)
        scheduler.step()
        log.append(dict(epoch=epoch + 1, loss=total / len(y)))
    model.eval()
    return model, log


def predict_scores(model, x, device='cpu', batch_size=256, embeddings=False):
    if not isinstance(model, nn.Module):
        return model.predict_proba(x.reshape(len(x), -1))[:, 1]
    scores, latent = [], []
    model.eval()
    with torch.inference_mode():
        for i in range(0, len(x), batch_size):
            logits, z = model(torch.as_tensor(x[i:i+batch_size], dtype=torch.float32, device=device))
            scores.append(logits.softmax(1)[:, 1].cpu().numpy())
            if embeddings:
                latent.append(z.cpu().numpy())
    s = np.concatenate(scores) if scores else np.empty(0)
    return (s, np.concatenate(latent)) if embeddings else s
