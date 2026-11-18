"""
Configuration file.
"""
import os
from model.CanTokenizer import CanLMTokenizer

SEED = 42
EPOCH = 3
SAVED_MODEL_PATH = 'saved_models_pl'

VOCAB_PATHS = {
    'canid_vocab_path': 'model/canid_vocab.txt',
    'datalen_vocab_path': 'model/datalen_vocab.txt',
    'data_vocab_path': 'model/data_vocab.txt',
}

TOKENIZER = CanLMTokenizer()

VOCAB_SIZES = {
    'canid_vocab': len(TOKENIZER.canid_vocab),
    'datalen_vocab': len(TOKENIZER.datalen_vocab),
    'data_vocab': len(TOKENIZER.data_vocab),
}

MIN_LENGTH = 1 # minimum length (# insns) of a function
NUM_GPUS = 2
ACCUMULATE_GRAD_BATCHES = 4
