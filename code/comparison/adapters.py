"""Explicit shared-protocol adaptations, not claimed original-paper reproductions.

CANBERT+ imports the pinned author's BERT/MLM modules unchanged. CANLP ports
the author's TF-IDF + 128/64 DNN architecture to PyTorch. AssocRules imports
the pinned CrySyS benchmark implementation unchanged (including its heuristics).
"""
from pathlib import Path
import importlib.util
import sys
import types
import numpy as np
import pandas as pd
import torch
from torch import nn
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import hstack,csr_matrix
from can_research.models import train_transformer,predict_scores,set_seed

CODE=Path(__file__).resolve().parents[1]


def upstream_bert():
    name='comparison_upstream_canbert'
    if name not in sys.modules:
        package=types.ModuleType(name);package.__path__=[str(CODE/'third_party/canbertplus/model')]
        sys.modules[name]=package
    from importlib import import_module
    return import_module(name+'.bert'),import_module(name+'.pretrain_tasks')


def assoc_class():
    path=str(CODE/'third_party/crysys')
    if path not in sys.path:sys.path.insert(0,path)
    from unified_ids.methods.assoc_rules_D_ANGELO_2023 import AssocRulesIDS
    return AssocRulesIDS


def frame_table(b):
    n,w=b['ids'].shape
    out=pd.DataFrame({'timestamp':b['times'].ravel(),'can_id':b['ids'].ravel(),
                      'label':b['frame_y'].ravel(),
                      '_source_file':np.repeat([f'{f}:window_{i}' for f,i in zip(b['capture'],b['ix'])],w)})
    for j in range(8):out[f'data{j}']=b['data'][...,j].ravel()
    return out


def tensor_fit(model,x,y,epochs,batch_size,lr,seed,device,eps=1e-8):
    set_seed(seed);model.to(device);opt=torch.optim.Adam(model.parameters(),lr=lr,eps=eps)
    rng=np.random.default_rng(seed);history=[]
    for epoch in range(epochs):
        model.train();total=0.;count=0
        for indices in np.array_split(rng.permutation(len(y)),max(1,int(np.ceil(len(y)/batch_size)))):
            xx=x[indices];xx=xx.toarray() if hasattr(xx,'toarray') else xx
            xx=torch.as_tensor(np.asarray(xx),dtype=torch.float32,device=device)
            yy=torch.as_tensor(y[indices],dtype=torch.long,device=device)
            opt.zero_grad();loss=nn.functional.cross_entropy(model(xx),yy);loss.backward();opt.step()
            total+=float(loss.detach())*len(indices);count+=len(indices)
        history.append(total/count);print(f'DNN epoch {epoch+1}/{epochs}: loss={history[-1]:.5f}',flush=True)
    model.eval();return history


class MatchedTransformer:
    def __init__(self,representation):self.representation=representation
    def fit(self,b,config,seed,device):
        self.model,self.history=train_transformer(b[self.representation],b['y'],config,seed,device)
    def score(self,b,device,batch_size):return predict_scores(self.model,b[self.representation],device,batch_size)


class CANLP:
    """Char unigrams + up to 256 bigrams; source fit; frame scores -> max/window."""
    @staticmethod
    def documents(b):
        return [''.join(f'{int(v):02X}' for v in row[:int(d)])
                for row,d in zip(b['data'].reshape(-1,8),b['dlc'].ravel())]
    def features(self,b,fit=False):
        docs=self.documents(b)
        if fit:
            self.vectorizers=[TfidfVectorizer(analyzer='char',ngram_range=(1,1),lowercase=False),
                              TfidfVectorizer(analyzer='char',ngram_range=(2,2),max_features=256,lowercase=False)]
        matrices=[]
        for v in self.vectorizers:
            matrices.append(v.fit_transform(docs) if fit else v.transform(docs))
        matrices.append(csr_matrix(b['ids'].reshape(-1,1)/2048.))
        return hstack(matrices,format='csr',dtype=np.float32)
    def fit(self,b,config,seed,device):
        x=self.features(b,True);set_seed(seed)
        self.model=nn.Sequential(nn.Linear(x.shape[1],128),nn.ReLU(),nn.Dropout(.15),
                                 nn.Linear(128,64),nn.ReLU(),nn.Linear(64,2))
        self.history=tensor_fit(self.model,x,b['frame_y'].ravel(),config['canlp_epochs'],512,.001,seed,device,1e-7)
    def score(self,b,device,batch_size):
        x=self.features(b);scores=[];self.model.eval()
        with torch.no_grad():
            for start in range(0,x.shape[0],512):
                xx=torch.as_tensor(x[start:start+512].toarray(),device=device)
                scores.append(self.model(xx).softmax(-1)[:,1].cpu().numpy())
        self.last_frame_scores=np.concatenate(scores).reshape(len(b['y']),-1)
        return self.last_frame_scores.max(1)


class CANBERTNetwork(nn.Module):
    def __init__(self,sizes,config):
        super().__init__();bert,tasks=upstream_bert()
        self.lm=tasks.BERTLM(bert.BERT(sizes,hidden=config['bert_hidden'],n_layers=config['bert_layers'],
                                     attn_heads=config['bert_heads'],dropout=.1),sizes['canid_vocab'])
        self.dropout=nn.Dropout(.1);self.classifier=nn.Linear(sizes['canid_vocab'],2)
    def language(self,x):return self.lm(*[x[...,j] for j in range(10)])
    def forward(self,x):return self.classifier(self.dropout(self.language(x)))


class CANBERT:
    @staticmethod
    def strings(b):
        # Same token definitions as the author's CanTokenizer, including byte positions.
        return [b['ids'].astype(str),np.char.add('L',b['dlc'].astype(str)),
                *[np.char.add(f'D{j+1}',b['data'][...,j].astype(str)) for j in range(8)]]
    def encode(self,b,fit=False):
        fields=self.strings(b)
        if fit:
            self.id_vocab={v:i+5 for i,v in enumerate(sorted(set(fields[0].ravel())))}
            self.dlc_vocab={v:i+5 for i,v in enumerate(sorted(set(fields[1].ravel())))}
            self.data_vocab={v:i+5 for i,v in enumerate(sorted(set(np.concatenate([v.ravel() for v in fields[2:]]))))}
        vocabs=[self.id_vocab,self.dlc_vocab]+[self.data_vocab]*8
        return np.stack([np.array([vocab.get(str(x),3) for x in field.ravel()],dtype=np.int64).reshape(field.shape)
                         for field,vocab in zip(fields,vocabs)],axis=-1)
    def fit(self,b,config,seed,device):
        set_seed(seed);x=self.encode(b,True)
        sizes=dict(canid_vocab=len(self.id_vocab)+5,datalen_vocab=len(self.dlc_vocab)+5,data_vocab=len(self.data_vocab)+5)
        self.model=CANBERTNetwork(sizes,config).to(device);self.history=[]
        benign=np.flatnonzero(b['y']==0)
        if not len(benign):raise ValueError('CANBERT+ needs benign source windows for pretraining')
        rng=np.random.default_rng(seed);batch=config['bert_batch_size']
        for phase,epochs,lr in [('pretrain',config['bert_pretrain_epochs'],3e-5),('finetune',config['bert_finetune_epochs'],.001)]:
            opt=torch.optim.AdamW(self.model.parameters(),lr=lr,betas=(.9,.999),weight_decay=.01)
            order_base=benign if phase=='pretrain' else np.arange(len(x))
            total_steps=epochs*int(np.ceil(len(order_base)/batch));step=0
            warmup=max(1,int(total_steps*.01))
            for epoch in range(epochs):
                self.model.train();order=rng.permutation(order_base);total=0.;count=0
                for start in range(0,len(order),batch):
                    indices=order[start:start+batch]
                    xx=torch.as_tensor(x[indices].copy(),device=device)
                    if phase=='pretrain':
                        labels=xx[...,0].clone();mask=torch.rand(labels.shape,device=device)<.15
                        # Make NLL well-defined when the random batch contains no masked token.
                        if not mask.any():mask[0,0]=True
                        labels[~mask]=0;xx[...,0][mask]=4
                        pred=self.model.language(xx)
                        loss=nn.functional.nll_loss(pred.transpose(1,2),labels,ignore_index=0)
                    else:
                        yy=torch.as_tensor(b['frame_y'][indices].astype(np.int64),device=device)
                        loss=nn.functional.cross_entropy(self.model(xx).transpose(1,2),yy)
                    factor=min((step+1)/warmup,max(0.,(total_steps-step)/max(1,total_steps-warmup)))
                    for group in opt.param_groups:group['lr']=lr*factor
                    opt.zero_grad();loss.backward();opt.step();step+=1
                    total+=float(loss.detach())*len(indices);count+=len(indices)
                self.history.append(dict(phase=phase,epoch=epoch+1,loss=total/count))
                print(f'CANBERT+ {phase} {epoch+1}/{epochs}: loss={total/count:.5f}',flush=True)
        self.model.eval()
    def score(self,b,device,batch_size):
        x=self.encode(b);scores=[];self.model.eval()
        with torch.no_grad():
            for start in range(0,len(x),self.batch_size):
                xx=torch.as_tensor(x[start:start+self.batch_size],device=device)
                scores.append(self.model(xx).softmax(-1)[...,1].cpu().numpy())
        self.last_frame_scores=np.concatenate(scores)
        return self.last_frame_scores.max(1)


class AssocRules:
    def fit(self,b,config,seed,device):
        params=dict(window_size=64,stride=64,random_state=seed,**config.get('assoc_params',{}))
        self.model=assoc_class()(**params)
        benign=b['y']==0
        self.model.fit(frame_table({k:v[benign] for k,v in b.items()}));self.history=[]
    def score(self,b,device,batch_size):
        values=[score for _,score in self.model.score_windows(frame_table(b))]
        if len(values)!=len(b['y']):raise ValueError('AssocRules window alignment failed')
        return np.asarray(values,float)


def fit_adapter(name,b,config,seed,device):
    if name in ['raw_transformer','structural_transformer']:
        model=MatchedTransformer('raw' if name.startswith('raw') else 'structural')
    else:model={'canbertplus':CANBERT,'canlp':CANLP,'assoc_rules_crysys':AssocRules}[name]()
    if name=='canbertplus':model.batch_size=config['bert_batch_size']
    model.fit(b,config,seed,device);return model


def load_checkpoint(path,expected_sha256,device='cpu'):
    """Load this study's trusted, hash-verified checkpoints in a new process."""
    from can_research.io import sha256_file
    if sha256_file(path)!=expected_sha256:raise ValueError('Checkpoint hash mismatch')
    upstream_bert();assoc_class()
    model=torch.load(path,map_location=device,weights_only=False)
    if isinstance(model.model,nn.Module):model.model.to(device).eval()
    return model
