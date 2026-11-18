
import re
from typing import Tuple
# import torch
import numpy as np
from model.CanVocab import CanLMVocab

class CanLMTokenizer:
    def __init__(self, mlm_probability=0.15, max_len=64):

        self.canid_vocab = CanLMVocab()
        self.datalen_vocab = CanLMVocab()
        self.data_vocab = CanLMVocab()

        self.canid_vocab.load('model/canid_vocab.txt')
        self.datalen_vocab.load('model/datalen_vocab.txt')
        self.data_vocab.load('model/data_vocab.txt')


        self.mlm_probability = mlm_probability
        self.max_len = max_len


    def encode_can(self, line):

        canid_token_ids = []
        datalen_token_ids = []
        data0_token_ids = []
        data1_token_ids = []
        data2_token_ids = []
        data3_token_ids = []
        data4_token_ids = []
        data5_token_ids = []
        data6_token_ids = []
        data7_token_ids = []

        for i in line:
            canid_token_ids.append(self.canid_vocab.get_id(str(int(i.split()[0], 16))))
            datalen_token_ids.append(self.datalen_vocab.get_id('L' + str(int(i.split()[1]))))
            data0_token_ids.append(self.data_vocab.get_id('D1' + str(int(i.split()[2], 16))))
            data1_token_ids.append(self.data_vocab.get_id('D2' + str(int(i.split()[3], 16))))
            data2_token_ids.append(self.data_vocab.get_id('D3' + str(int(i.split()[4], 16))))
            data3_token_ids.append(self.data_vocab.get_id('D4' + str(int(i.split()[5], 16))))
            data4_token_ids.append(self.data_vocab.get_id('D5' + str(int(i.split()[6], 16))))
            data5_token_ids.append(self.data_vocab.get_id('D6' + str(int(i.split()[7], 16))))
            data6_token_ids.append(self.data_vocab.get_id('D7' + str(int(i.split()[8], 16))))
            data7_token_ids.append(self.data_vocab.get_id('D8' + str(int(i.split()[9], 16))))

        mask_canid, mask_canid_labels = self.mask_tokens(canid_token_ids)
        mask_canid = mask_canid.tolist()
        mask_canid_labels = mask_canid_labels.tolist()

        outputs =  {
            'canid_ids': canid_token_ids,
            'datalen_ids': datalen_token_ids,
            'data0_ids': data0_token_ids,
            'data1_ids': data1_token_ids,
            'data2_ids': data2_token_ids,
            'data3_ids': data3_token_ids,
            'data4_ids': data4_token_ids,
            'data5_ids': data5_token_ids,
            'data6_ids': data6_token_ids,
            'data7_ids': data7_token_ids,
            'mask_canid_ids': mask_canid,
            'mask_canid_label': mask_canid_labels
        }

        return outputs


    def mask_tokens(self, inputs):
        inputs = np.array(inputs)
        labels = np.copy(inputs)
        probability_matrix = np.full(labels.shape, self.mlm_probability)
        masked_indices = np.random.binomial(1, probability_matrix, size=probability_matrix.shape).astype(bool)
        labels[~masked_indices] = self.canid_vocab.pad_id
        inputs[masked_indices] = self.canid_vocab.mask_id

        return inputs, labels
