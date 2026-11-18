import torch.nn as nn
import torch.nn.functional as F
import torch
import math

class Attention(nn.Module):
    def forward(self, query, key, value, mask=None, dropout=None):
        scores = torch.matmul(query, key.transpose(-2, -1)) \
                 / math.sqrt(query.size(-1))

        if mask is not None:
            scores = scores.masked_fill(mask, float("-inf"))

        p_attn = F.softmax(scores, dim=-1)

        if dropout is not None:
            p_attn = dropout(p_attn)

        return torch.matmul(p_attn, value), p_attn

class MultiHeadedAttention(nn.Module):
    def __init__(self, h, d_model, dropout=0.1):
        super().__init__()
        assert d_model % h == 0

        self.d_k = d_model // h
        self.h = h

        self.linear_layers = nn.ModuleList([nn.Linear(d_model, d_model) for _ in range(3)])
        self.output_linear = nn.Linear(d_model, d_model)
        self.attention = Attention()

        self.dropout = nn.Dropout(p=dropout)

    def forward(self, query, key, value, mask=None):
        batch_size = query.size(0)

        query, key, value = [l(x).view(batch_size, -1, self.h, self.d_k).transpose(1, 2)
                             for l, x in zip(self.linear_layers, (query, key, value))]

        x, attn = self.attention(query, key, value, mask=mask, dropout=self.dropout)

        x = x.transpose(1, 2).contiguous().view(batch_size, -1, self.h * self.d_k)
        temp = self.output_linear(x)
        return self.output_linear(x)

class PositionwiseFeedForward(nn.Module):
    def __init__(self, d_model, d_ff, dropout=0.1):
        super(PositionwiseFeedForward, self).__init__()
        self.w_1 = nn.Linear(d_model, d_ff)
        self.w_2 = nn.Linear(d_ff, d_model)
        self.dropout = nn.Dropout(dropout)
        self.activation = GELU()

    def forward(self, x):
        return self.w_2(self.dropout(self.activation(self.w_1(x))))

class GELU(nn.Module):
    def forward(self, x):
        return 0.5 * x * (1 + torch.tanh(math.sqrt(2 / math.pi) * (x + 0.044715 * torch.pow(x, 3))))

class LayerNorm(nn.Module):
    def __init__(self, features, eps=1e-6):
        super(LayerNorm, self).__init__()
        self.a_2 = nn.Parameter(torch.ones(features))
        self.b_2 = nn.Parameter(torch.zeros(features))
        self.eps = eps

    def forward(self, x):
        mean = x.mean(-1, keepdim=True)
        std = x.std(-1, keepdim=True)
        return self.a_2 * (x - mean) / (std + self.eps) + self.b_2

class SublayerConnection(nn.Module):
    def __init__(self, size, dropout):
        super(SublayerConnection, self).__init__()
        self.norm = LayerNorm(size)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x, sublayer):
        return x + self.dropout(sublayer(self.norm(x)))

class TransformerBlock(nn.Module):
    def __init__(self, hidden, attn_heads, feed_forward_hidden, dropout):
        super().__init__()
        self.attention = MultiHeadedAttention(h=attn_heads, d_model=hidden)
        self.feed_forward = PositionwiseFeedForward(d_model=hidden, d_ff=feed_forward_hidden, dropout=dropout)
        self.input_sublayer = SublayerConnection(size=hidden, dropout=dropout)
        self.output_sublayer = SublayerConnection(size=hidden, dropout=dropout)
        self.dropout = nn.Dropout(p=dropout)

    def forward(self, x, mask):
        x = self.input_sublayer(x, lambda _x: self.attention.forward(_x, _x, _x, mask=mask))
        x = self.output_sublayer(x, self.feed_forward)
        return self.dropout(x)

class TokenEmbedding(nn.Embedding):
    def __init__(self, vocab_size, embed_size=512):
        super().__init__(vocab_size, embed_size, padding_idx=0)


class PositionalEmbedding(nn.Module):

    def __init__(self, d_model, max_len=512):
        super().__init__()

        pe = torch.zeros(max_len, d_model).float()
        pe.require_grad = False

        position = torch.arange(0, max_len).float().unsqueeze(1)
        div_term = (torch.arange(0, d_model, 2).float() * -(math.log(10000.0) / d_model)).exp()

        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)

        pe = pe.unsqueeze(0)
        self.register_buffer('pe', pe)

    def forward(self, x):
        return self.pe[:, :x.size(1)]

class BERTEmbedding(nn.Module):
    def __init__(self, vocab_sizes, embed_size, dropout=0.1):
        super().__init__()
        self.token = TokenEmbedding(vocab_size=vocab_sizes['canid_vocab'], embed_size=embed_size)
        self.datalen = TokenEmbedding(vocab_size=vocab_sizes['datalen_vocab'], embed_size=embed_size)
        self.data0 = TokenEmbedding(vocab_size=vocab_sizes['data_vocab'], embed_size=embed_size)
        self.data1 = TokenEmbedding(vocab_size=vocab_sizes['data_vocab'], embed_size=embed_size)
        self.data2 = TokenEmbedding(vocab_size=vocab_sizes['data_vocab'], embed_size=embed_size)
        self.data3 = TokenEmbedding(vocab_size=vocab_sizes['data_vocab'], embed_size=embed_size)
        self.data4 = TokenEmbedding(vocab_size=vocab_sizes['data_vocab'], embed_size=embed_size)
        self.data5 = TokenEmbedding(vocab_size=vocab_sizes['data_vocab'], embed_size=embed_size)
        self.data6 = TokenEmbedding(vocab_size=vocab_sizes['data_vocab'], embed_size=embed_size)
        self.data7 = TokenEmbedding(vocab_size=vocab_sizes['data_vocab'], embed_size=embed_size)

        self.position = PositionalEmbedding(d_model=self.token.embedding_dim)

        self.dropout = nn.Dropout(p=dropout)
        self.embed_size = embed_size


    def forward(self, token_seq, datalen_seq, data0_seq, data1_seq, data2_seq, data3_seq, data4_seq, data5_seq, data6_seq, data7_seq):
        x = self.token(token_seq) + self.position(token_seq)

        x += self.datalen(datalen_seq)
        x += self.data0(data0_seq)
        x += self.data1(data1_seq)
        x += self.data2(data2_seq)
        x += self.data3(data3_seq)
        x += self.data4(data4_seq)
        x += self.data5(data5_seq)
        x += self.data6(data6_seq)
        x += self.data7(data7_seq)
        return self.dropout(x)


class BERT(nn.Module):
    def __init__(self, vocab_sizes, hidden=768, n_layers=12, attn_heads=12, dropout=0.1):
        super().__init__()
        self.hidden = hidden
        self.n_layers = n_layers
        self.attn_heads = attn_heads

        self.feed_forward_hidden = hidden * 4

        self.embedding = BERTEmbedding(vocab_sizes=vocab_sizes, embed_size=hidden)

        self.transformer_blocks = nn.ModuleList(
            [TransformerBlock(hidden, attn_heads, hidden * 4, dropout) for _ in range(n_layers)])


    def forward(self, x, datalen, data0, data1, data2, data3, data4, data5, data6, data7):
        mask = (x == 0).unsqueeze(1).repeat(1, x.size(1), 1).unsqueeze(1)

        x = self.embedding(x, datalen, data0, data1, data2, data3, data4, data5, data6, data7)

        for transformer in self.transformer_blocks:
            x = transformer.forward(x, mask)

        return x

    def encode(self, x):

        mask = (x == 0).unsqueeze(1).repeat(1, x.size(1), 1).unsqueeze(1)

        x = self.embedding(x)

        for transformer in self.transformer_blocks[:-1]:
            x = transformer.forward(x, mask)

        return x
