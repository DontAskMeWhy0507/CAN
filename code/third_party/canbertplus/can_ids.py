import os
import pickle
import csv
from argparse import ArgumentParser
from torch.utils.data import DataLoader
from model import *
import torch
from tqdm import *
from config import TOKENIZER, VOCAB_SIZES, SEED
import lightning as L
from canlm import *

class CanDataset(torch.utils.data.Dataset):
    def __init__(self, path):
        self.path = path
        assert os.path.exists(self.path), "Dataset Path Not Exists"

        self.datas = []
        with open(path, 'r') as f:
            load = csv.DictReader(f)

            data = []
            for line in tqdm(load, desc='Loading file %s' % path, ncols=80, ascii=' #'):
                data.append(line['text'])
                if len(data) == TOKENIZER.max_len:
                    encodings = TOKENIZER.encode_can(data)
                    encodings = {key: torch.tensor(value) for key, value in encodings.items()}
                    self.datas.append(encodings)
                    data = []

    def __getitem__(self, idx):
        return self.datas[idx]

    def __len__(self):
        return len(self.datas)


if __name__ == "__main__":

    parser = ArgumentParser(description="Can IDS dataset")
    parser.add_argument("-i", "--input_file", help="Input dir of pregen pairs", nargs='?')
    parser.add_argument("-n", "--num_process", help="num of workers for dataloader", default=64, nargs='?')
    parser.add_argument("-bs", "--batch_size", help="batch size", default=32, nargs='?')
    args = parser.parse_args()

    dataset = CanDataset(args.input_file)
    dl = DataLoader(dataset, batch_size=int(args.batch_size), shuffle=False, num_workers=int(args.num_process))

    pl_model = CanLMModule(0)

    trainer = L.Trainer(accelerator="auto", devices="auto", strategy="auto", max_epochs=200)
    trainer.fit(pl_model, dl)
    trainer.save_checkpoint("orig_ids.ckpt")

