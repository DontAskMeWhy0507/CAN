import torch
import pickle
from glob import glob
from tqdm import tqdm
from multiprocessing import Manager, Pool
import CanLMTokenizer

class CanLMDataset(torch.utils.data.Dataset):
    def __init__(self, input_file, n_workers=48):
        self.n_workers = n_workers
        print('Initializing tokenizer...')
        self.tokenizer = CanLMTokenizer()

        print('Loading dataset...')
        self.dataset_path = input_file
        self.datas = Manager().list()
        self.load_data()

    def __getitem__(self, idx): # random visit
        return {key: torch.tensor(value) for key, value in self.datas[idx].items()}

    def __len__(self):
        return len(self.datas)

    def worker_load_data(self, csv_file):
        can_datas = []
        with open(csv_file, 'r') as f:
            load = csv.DictReader(f)
            data = []
            for line in load:
                data.append(line['text'])
                if len(data) == self.tokenizer.max_len:

                    can_datas.append(self.tokenizer.encode_can(data))
                    data = []

        self.datas.extend(can_datas)
        del can_datas

    def load_data(self):
        pool = Pool(processes=self.n_workers)
        input_list = []
        for csv_file in tqdm(self.dataset_path):
            input_list.append(csv_file)
        pool.map(self.worker_load_data, input_list)
        pool.close()

        print(len(self.datas))


