import torch as nn
import random
import model
import numpy as np
from tqdm import tqdm
from glob import glob
from torch.optim import Adam, AdamW
from lightning import LightningModule
from config import TOKENIZER, VOCAB_SIZES, SEED
from transformers import get_linear_schedule_with_warmup
from model.bert import *
from model.pretrain_tasks import *
from canlm import *
from lightning.pytorch.callbacks.early_stopping import EarlyStopping
from lightning.pytorch import loggers as pl_loggers
from lightning.pytorch.callbacks import DeviceStatsMonitor
from lightning.pytorch.profilers import SimpleProfiler, PyTorchProfiler, AdvancedProfiler
import torch
from torch.utils.data import Subset

import statistics
import time
import psutil
import shutil
import os
import sys
import csv
import pathlib
from model import *
import lightning as L
from argparse import ArgumentParser
from torch.utils.data import DataLoader, random_split

from pytorch_lightning import loggers as pl_loggers

random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
torch.cuda.manual_seed_all(SEED)

torch.multiprocessing.set_sharing_strategy('file_system')

class IdsDataset(torch.utils.data.Dataset):
    def __init__(self, path):
        self.path = path
        assert os.path.exists(self.path), "Dataset Path Not Exists"

        self.datas = []
        self.labels = []
        with open(path, 'r') as f:
            load = csv.DictReader(f)
            data = []
            label = []
            for line in tqdm(load, desc='Loading file %s' % path, ncols=80, ascii=' #'):
                data.append(line['text'])
                label.append(int(line['label']))
                if len(data) == TOKENIZER.max_len:
                    encodings = TOKENIZER.encode_can(data)
                    encodings['label'] = label
                    encodings = {key: torch.tensor(value) for key, value in encodings.items()}
                    self.datas.append(encodings)
                    self.labels.append(label)
                    data = []
                    label = []

    def __getitem__(self, idx):
        return self.datas[idx]

    def __len__(self):
        return len(self.datas)


class CanIds(LightningModule):
    def __init__(self, model_name: str, warmup_steps_ratio=0.01, lr: float = 0.001, betas=(0.9, 0.999), weight_decay: float = 0.01):
        super().__init__()
        self.lr = lr
        self.betas = betas
        self.weight_decay = weight_decay
        self.warmup_steps_ratio = warmup_steps_ratio
        self.tokenizer = TOKENIZER
        self.total_steps=0

        self.train_losses = []
        self.eval_losses = []
        self.n_correct = 0
        self.nb_tr_examples = 0
        self.val_n_correct = 0
        self.val_nb_tr_examples = 0
        self.test_nb_tr_examples = 0

        self.tr_tp = 0
        self.tr_fp = 0
        self.tr_tn = 0
        self.tr_fn = 0

        self.val_tp = 0
        self.val_fp = 0
        self.val_tn = 0
        self.val_fn = 0

        self.test_tp = 0
        self.test_fp = 0
        self.test_tn = 0
        self.test_fn = 0

        self.l1 = CanLMModule.load_from_checkpoint(total_steps=self.total_steps, checkpoint_path=model_name)
        self.dropout = nn.Dropout(0.1)
        self.classifier = nn.Linear(VOCAB_SIZES['canid_vocab'], 2)

        self.relu = nn.ReLU()
        self.softmax = nn.Softmax(dim=2)
        self.sigmoid = nn.Sigmoid()
        self.loss_function = torch.nn.CrossEntropyLoss()

    def forward(self, x, datalen, data0, data1, data2, data3, data4, data5, data6, data7):
        output_1 = self.l1(x, datalen, data0, data1, data2, data3, data4, data5, data6, data7)

        pooler = output_1
        pooler = self.dropout(pooler)
        pooler = self.classifier(pooler)
        return pooler

    def calculate_accuracy(self, preds, targets):
        fp = 0
        fn = 0
        tp = 0
        tn = 0
        for i in range(len(preds)):
            for j in range(len(preds[i])):
                if targets[i][j] == 1 and targets[i][j] == preds[i][j]:
                    tp += 1
                elif targets[i][j] == 1 and targets[i][j] != preds[i][j]:
                    fp += 1
                elif targets[i][j] == 0 and targets[i][j] == preds[i][j]:
                    tn += 1
                else:
                    fn += 1
        return tp, fp, tn, fn

    def training_step(self, batch, batch_idx):
        results = {}
        output = self.forward(
            batch['canid_ids'],
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

        loss = self.loss_function(output.transpose(1,2), batch['label'])
        results['loss'] = loss
        self.train_losses.append(loss.detach().item())

        big_val, big_idx = torch.max(output.data, dim=2)
        tp, fp, tn, fn = self.calculate_accuracy(big_idx, batch['label'])
        self.tr_tp += tp
        self.tr_fp += fp
        self.tr_tn += tn
        self.tr_fn += fn
        self.nb_tr_examples += batch['label'].size(0) * batch['label'].size(1)

        accu = ((self.tr_tp + self.tr_tn)*100)/self.nb_tr_examples

        self.log("train accuracy", accu, on_step=True, on_epoch=False, prog_bar=True, logger=True, sync_dist=True)
        return loss

    def on_train_epoch_end(self):
        self.n_correct = 0
        self.tr_tp = 0
        self.tr_fp = 0
        self.tr_tn = 0
        self.tr_fn = 0
        self.nb_tr_examples = 0

        self.log("train_mean_loss", np.mean(self.train_losses), on_step=False, on_epoch=True, prog_bar=True, logger=False, sync_dist=True)

        self.train_losses = []

    def validation_step(self, batch, batch_idx):
        results = {}

        output = self.forward(
            batch['canid_ids'],
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

        loss = self.loss_function(output.transpose(1,2), batch['label'])
        results['loss'] = loss
        val_loss = loss
        self.eval_losses.append(loss.item())


        big_val, big_idx = torch.max(output.data, dim=2)
        tp, fp, tn, fn = self.calculate_accuracy(big_idx, batch['label'])
        self.val_tp += tp
        self.val_fp += fp
        self.val_tn += tn
        self.val_fn += fn
        self.val_nb_tr_examples += batch['label'].size(0) * batch['label'].size(1)

        accu = ((self.val_tp + self.val_tn)*100)/self.val_nb_tr_examples

        return results

    def on_validation_epoch_end(self):
        if self.val_tp + self.val_fp != 0:
            prec = self.val_tp / (self.val_tp + self.val_fp)
        elif self.val_tp + self.val_fp == 0 and self.val_tp == 0:
            prec = 0
        else:
            prec = 0

        if self.val_tp + self.val_fn != 0:
            recall = self.val_tp / (self.val_tp + self.val_fn)
        elif self.val_tp + self.val_fn == 0 and self.val_tp == 0:
            recall = 0
        else:
            recall = 0

        if prec + recall != 0:
            f1 = 2 * prec * recall / (prec + recall)
        else:
            f1 = 0

        accu = ((self.val_tp + self.val_tn)/self.val_nb_tr_examples)*100

        self.log("val_accu", accu, on_step=False, on_epoch=True, prog_bar=False, logger=True, sync_dist=True)
        self.log("prec", prec, on_step=False, on_epoch=True, prog_bar=False, logger=True, sync_dist=True)
        self.log("recall", recall, on_step=False, on_epoch=True, prog_bar=False, logger=True, sync_dist=True)
        self.log("f1", f1, on_step=False, on_epoch=True, prog_bar=False, logger=True, sync_dist=True)

        self.val_n_correct = 0
        self.val_nb_tr_examples = 0
        self.val_tp = 0
        self.val_tn = 0
        self.val_fp = 0
        self.val_fn = 0
        mean_mask_loss = np.mean(self.eval_losses)
        self.log("val_mean_loss", np.mean(self.eval_losses), on_step=False, on_epoch=True, prog_bar=True, logger=False, sync_dist=True)

        self.eval_losses = []

    def test_step(self, batch, batch_idx):
        results = {}

        output = self.forward(
            batch['canid_ids'],
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

        loss = self.loss_function(output.transpose(1,2), batch['label'])
        results['loss'] = loss
        val_loss = loss
        self.eval_losses.append(loss.item())


        big_val, big_idx = torch.max(output.data, dim=2)
        tp, fp, tn, fn = self.calculate_accuracy(big_idx, batch['label'])
        self.test_tp += tp
        self.test_fp += fp
        self.test_tn += tn
        self.test_fn += fn
        self.test_nb_tr_examples += batch['label'].size(0) * batch['label'].size(1)

        accu = ((self.test_tp + self.test_tn)*100)/self.test_nb_tr_examples

        self.log("test_accuracy", accu, on_step=True, on_epoch=False, prog_bar=False, logger=False, sync_dist=True)
        self.log("test_loss", val_loss, on_step=True, on_epoch=False, prog_bar=False, logger=False, sync_dist=True)

        return results

    def on_test_epoch_end(self):
        if self.test_tp + self.test_fp != 0:
            prec = self.test_tp / (self.test_tp + self.test_fp)
        elif self.test_tp + self.test_fp == 0 and self.test_tp == 0:
            prec = 0
        else:
            prec = 0

        if self.test_tp + self.test_fn != 0:
            recall = self.test_tp / (self.test_tp + self.test_fn)
        elif self.test_tp + self.test_fn == 0 and self.test_tp == 0:
            recall = 0
        else:
            recall = 0

        if prec + recall != 0:
            f1 = 2 * prec * recall / (prec + recall)
        else:
            f1 = 0

        accu = ((self.test_tp + self.test_tn)/self.test_nb_tr_examples)*100

        self.log("tp", self.test_tp, on_step=False, on_epoch=True, prog_bar=False, logger=True, sync_dist=True)
        self.log("tn", self.test_tn, on_step=False, on_epoch=True, prog_bar=False, logger=True, sync_dist=True)
        self.log("fp", self.test_fp, on_step=False, on_epoch=True, prog_bar=False, logger=True, sync_dist=True)
        self.log("fn", self.test_fn, on_step=False, on_epoch=True, prog_bar=False, logger=True, sync_dist=True)
        self.log("test_accu", accu, on_step=False, on_epoch=True, prog_bar=False, logger=True, sync_dist=True)
        self.log("prec", prec, on_step=False, on_epoch=True, prog_bar=False, logger=True, sync_dist=True)
        self.log("recall", recall, on_step=False, on_epoch=True, prog_bar=False, logger=True, sync_dist=True)
        self.log("f1", f1, on_step=False, on_epoch=True, prog_bar=False, logger=True, sync_dist=True)

        self.test_nb_tr_examples = 0
        self.test_tp = 0
        self.test_tn = 0
        self.test_fp = 0
        self.test_fn = 0
        mean_mask_loss = np.mean(self.eval_losses)
        self.log("test_mean_loss", np.mean(self.eval_losses), on_step=False, on_epoch=True, prog_bar=True, logger=False, sync_dist=True)

        self.eval_losses = []


    def configure_optimizers(self):
        optim = AdamW(self.parameters(), lr=self.lr, betas=self.betas, weight_decay=self.weight_decay)
        optim_schedule = get_linear_schedule_with_warmup(optim, int(self.warmup_steps_ratio*self.total_steps), self.trainer.estimated_stepping_batches)

        return [optim], [{"scheduler": optim_schedule, "interval": "step"}]


if __name__ == "__main__":
    parser = ArgumentParser(description="Can IDS dataset")
    parser.add_argument("-m", "--model_path", help="path to ids model", default='./orig_ids.ckpt', nargs='?')
    parser.add_argument("-i", "--input_file", help="Input dir of pregen pairs",  nargs='?')
    parser.add_argument("-n", "--num_process", help="num of workers for dataloader", default=64, nargs='?')
    parser.add_argument("-bs", "--batch_size", help="batch size", default=128, nargs='?')
    parser.add_argument("-o", "--output_dir", help="output directory", default='can_finetune', nargs='?')
    args = parser.parse_args()

    profiler = AdvancedProfiler(dirpath=".", filename="perf_logs")

    print (args.input_file)

    full_dataset = IdsDataset(args.input_file)
    dataset_size = len(full_dataset)
    train_size = int(0.8 * dataset_size)

    train_dataset = Subset(full_dataset, range(train_size))
    test_dataset = Subset(full_dataset, range(train_size, dataset_size))

    train_dl = DataLoader(train_dataset, batch_size=int(args.batch_size), shuffle=False, num_workers=int(args.num_process))
    test_dl = DataLoader(test_dataset, batch_size=int(args.batch_size), shuffle=False, num_workers=int(args.num_process))

    new_model = CanIds(args.model_path)

    early_stopping = EarlyStopping(
            monitor="train_mean_loss",
            min_delta=0.0,
            patience=5, #10
            verbose=True
            )

    path = args.input_file.replace('.csv', '')
    folders = path.split('/')

    idx=1
    max_idx = len(folders)

    new_path = 'result'
    while idx < max_idx-1:
        new_path = os.path.join(new_path, folders[idx])
        idx+=1

    pathlib.Path(new_path).mkdir(parents=True, exist_ok=True)

    tb_logger = pl_loggers.CSVLogger(save_dir=new_path, name=None, version=folders[max_idx-1])

    trainer = L.Trainer(callbacks=[early_stopping], logger=tb_logger, accelerator="auto", devices="auto", strategy="auto", max_epochs=200)

    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()

    # When wanting to add validation
    # Also, this can be helpful track how F1 score of test set changes
    #trainer.fit(new_model, train_dl, test_dl)

    trainer.fit(new_model, train_dl)
    trainer.test(new_model, dataloaders=test_dl, ckpt_path='best')
