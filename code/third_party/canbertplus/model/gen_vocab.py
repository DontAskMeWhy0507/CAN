import os
import re
import pickle
from glob import glob
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import argparse
from CanVocab import CanLMVocab
import csv

dir_path = os.path.dirname(os.path.realpath(__file__))

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input_csv', type=str, help='input CSV file')
parser.add_argument('-n', '--workers', type=int, nargs='?',
                    help='Max Workers', default=48)
args = parser.parse_args()

def normalize_can(can):
    temp = can.split()
    can_id = int(temp[0], 16)
    data_len = int(temp[1])
    data = []
    for i in range(8):
        data.append(int(temp[2+i], 16))

    return can_id, data_len, data


def gen_vocab_per_file(input_path):
    token_vocab = set()
    canid_vocab = set()
    datalen_vocab = set()
    data_vocab = set()

    for csv_file in tqdm(glob('{}/**/*.csv'.format(input_path), recursive=True)):
        print (csv_file)
        with open(csv_file, 'r') as f:
            load = csv.DictReader(f)
            for line in load:
                line =  line['text']
                can_id, data_len, data = normalize_can(line)

                canid_vocab.add(str(can_id))
                datalen_vocab.add(str(data_len))
                for i in range(8):
                    data_vocab.add("D" + str(i) + str(data[i]))

    with open('canid_vocab', 'w') as f:
        f.write(' '.join(list(canid_vocab)))
    with open('datalen_vocab', 'w') as f:
        f.write(' '.join(list(datalen_vocab)))
    with open('data_vocab', 'w') as f:
        f.write(' '.join(list(data_vocab)))


def merge_vocab(vocab_file):
    vocab = set()
    with open(vocab_file, 'r') as f:
        vocab.update(set(f.read().split()))

    print(len(vocab))
    vocab = list(vocab)
    vocab.sort()
    vocab = CanLMVocab(vocab)
    vocab.save(f'{vocab_file}.txt')


def gen_vocab(input_file):
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        executor.submit(gen_vocab_per_file, input_file)

    merge_vocab('canid_vocab')
    merge_vocab('datalen_vocab')
    merge_vocab('data_vocab')


if __name__ == '__main__':
    gen_vocab(args.input_csv)
