import torch
import random
import model
import numpy as np
from tqdm import tqdm
from glob import glob
from torch.optim import Adam, AdamW
from lightning import LightningModule
from config import TOKENIZER, VOCAB_SIZES, SEED
from transformers import get_linear_schedule_with_warmup
import sys

from model.bert import *
from model.pretrain_tasks import *

random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
torch.cuda.manual_seed_all(SEED)

torch.multiprocessing.set_sharing_strategy('file_system')

class CanLMModule(LightningModule):
    def __init__(self, total_steps, warmup_steps_ratio=0.01, lr: float = 3e-5, betas=(0.9, 0.999), weight_decay: float = 0.01):
        super().__init__()
        self.total_steps = total_steps
        self.lr = lr
        self.betas = betas
        self.weight_decay = weight_decay
        self.warmup_steps_ratio = warmup_steps_ratio
        self.tokenizer = TOKENIZER

        #original
        self.bert = BERT(VOCAB_SIZES, hidden=768, n_layers=6, attn_heads=12, dropout=0.1)

        #bert-small
        #self.bert = BERT(VOCAB_SIZES, hidden=60, n_layers=2, attn_heads=12, dropout=0.1)

        #bert-tiny
        #self.bert = BERT(VOCAB_SIZES, hidden=12, n_layers=2, attn_heads=4, dropout=0.1)

        self.model = BERTLM(self.bert, VOCAB_SIZES['canid_vocab'])

        self.masked_criterion = torch.nn.NLLLoss(ignore_index=0)

        self.train_losses = []
        self.train_mlm_losses = []
        self.train_entity_mlm_losses = []
        self.eval_losses = []
        self.eval_mlm_losses = []
        self.eval_entity_mlm_losses = []

    def forward(self, x, datalen, data0, data1, data2, data3, data4, data5, data6, data7):
        return self.model.forward(x, datalen, data0, data1, data2, data3, data4, data5, data6, data7)

    def training_step(self, batch, batch_idx):
        results = {}

        mlm_output = self.forward(
            #batch['canid_ids'],
            batch['mask_canid_ids'],
            batch['datalen_ids'],
            batch['data0_ids'],
            batch['data1_ids'],
            batch['data2_ids'],
            batch['data3_ids'],
            batch['data4_ids'],
            batch['data5_ids'],
            batch['data6_ids'],
            batch['data7_ids']
        )

        mlm_loss = self.masked_criterion(mlm_output.transpose(1, 2), batch['mask_canid_label'])
        loss = mlm_loss

        results['loss'] = loss

        self.train_losses.append(loss.item())

        self.log("train_loss", loss, on_step=True, on_epoch=False, prog_bar=False, logger=True, sync_dist=True)
        self.log("train_loss_mask", mlm_loss, on_step=True, on_epoch=False, prog_bar=False, logger=True, sync_dist=True)

        self.log("lr", self.lr_schedulers().get_last_lr()[0], on_step=True, on_epoch=False, prog_bar=True, logger=True, sync_dist=True)

        return loss


    def on_train_epoch_end(self):
        self.log("train_mean_loss", np.mean(self.train_losses), on_step=False, on_epoch=True, prog_bar=True, logger=True, sync_dist=True)

    def validation_step(self, batch, batch_idx):
        results = {}

        mlm_output = self.forward(
            #batch['canid_token_ids'],
            batch['mask_canid_ids'],
            batch['datalen_ids'],
            batch['data0_ids'],
            batch['data1_ids'],
            batch['data2_ids'],
            batch['data3_ids'],
            batch['data4_ids'],
            batch['data5_ids'],
            batch['data6_ids'],
            batch['data7_ids']
        )


        mlm_loss = self.masked_criterion(mlm_output.transpose(1, 2), batch['mask_canid_label'])
        loss = mlm_loss

        results['loss'] = loss

        self.eval_losses.append(loss.item())

        self.log("eval_loss", loss, on_step=True, on_epoch=False, prog_bar=False, logger=True, sync_dist=True)
        return loss

    def on_validation_epoch_end(self):
        mean_mask_loss = np.mean(self.eval_mlm_losses)
        perplexity = np.exp(mean_mask_loss)

        self.log("eval_mean_loss", np.mean(self.eval_losses), on_step=False, on_epoch=True, prog_bar=True, logger=True, sync_dist=True)
        self.log("eval_mean_mask_loss", mean_mask_loss, on_step=False, on_epoch=True, prog_bar=False, logger=True, sync_dist=True)
        self.log("eval_perplexity", perplexity, on_step=False, on_epoch=True, prog_bar=True, logger=True, sync_dist=True)

    def test_step(self, batch, batch_idx):
        results = {}

        embs = self.forward(
            batch['mask_canid_ids'],
            batch['datalen_ids'],
            batch['data0_ids'],
            batch['data1_ids'],
            batch['data2_ids'],
            batch['data3_ids'],
            batch['data4_ids'],
            batch['data5_ids'],
            batch['data6_ids'],
            batch['data7_ids']
        )

        results['embeddings'] = embs

        return results

    def on_before_optimizer_step(self, optimizer) -> None:
        for name,p in self.named_parameters():
            if p.grad is None:
                continue

    def configure_optimizers(self):
        optim = AdamW(self.model.parameters(), lr=self.lr, betas=self.betas, weight_decay=self.weight_decay)
        optim_schedule = get_linear_schedule_with_warmup(optim, int(self.warmup_steps_ratio*self.total_steps), self.trainer.estimated_stepping_batches)

        return [optim], [{"scheduler": optim_schedule, "interval": "step"}]
