import torch.nn as nn
import torch

from .bert import BERT


class BERTLM(nn.Module):
    def __init__(self, bert: BERT, token_vocab_size):
        super().__init__()
        self.bert = bert
        self.MLM = MaskedLanguageModel(self.bert.hidden, token_vocab_size)


    def forward(self, x, datalen, data0, data1, data2, data3, data4, data5, data6, data7):
        x = self.bert.forward(x, datalen, data0, data1, data2, data3, data4, data5, data6, data7)

        return self.MLM(x)


class NextSentencePrediction(nn.Module):
    def __init__(self, hidden):
        super().__init__()
        self.linear = nn.Linear(hidden, 2)
        self.softmax = nn.LogSoftmax(dim=-1)

    def forward(self, x):
        return self.softmax(self.linear(x[:, 0]))


class MaskedLanguageModel(nn.Module):
    def __init__(self, hidden, token_vocab_size):
        super().__init__()
        self.linear = nn.Linear(hidden, token_vocab_size)
        self.softmax = nn.LogSoftmax(dim=-1)

    def forward(self, x):
        return self.softmax(self.linear(x))
