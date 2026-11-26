import os
import pandas as pd
import numpy as np
import torch
_original_torch_load = torch.load
def _patched_torch_load(*a, **k):
    k['weights_only'] = False
    return _original_torch_load(*a, **k)
torch.load = _patched_torch_load

from fastai import *
from fastai.text import *
from fastai.basic_train import load_learner
from pytorch_transformers import BertTokenizer, BertPreTrainedModel, BertModel, BertConfig
from sklearn.metrics import accuracy_score, f1_score

bert_tok = BertTokenizer.from_pretrained('bert-base-cased')
class FastAiBertTokenizer(BaseTokenizer):
    def __init__(self, tokenizer, max_seq_len=512, **kw):
        self._pretrained_tokenizer = tokenizer; self.max_seq_len = max_seq_len
    def __call__(self, *a, **k): return self
    def tokenizer(self, t):
        return ["[CLS]"] + self._pretrained_tokenizer.tokenize(t)[:self.max_seq_len-2] + ["[SEP]"]
class BertTokenizeProcessor(TokenizeProcessor):
    def __init__(self, tokenizer): super().__init__(tokenizer=tokenizer, include_bos=False, include_eos=False)
class BertNumericalizeProcessor(NumericalizeProcessor):
    def __init__(self, *a, **k): super().__init__(*a, vocab=Vocab(list(bert_tok.vocab.keys())), **k)
def get_bert_processor(tokenizer=None, vocab=None):
    return [BertTokenizeProcessor(tokenizer=tokenizer), NumericalizeProcessor(vocab=vocab)]
class BertDataBunch(TextDataBunch):
    @classmethod
    def from_df(cls, path, train_df, valid_df, test_df=None, tokenizer=None, vocab=None,
                classes=None, text_cols=1, label_cols=0, **kw):
        p_kw, kw = split_kwargs_by_func(kw, get_bert_processor)
        processor = get_bert_processor(tokenizer=tokenizer, vocab=vocab, **p_kw)
        if classes is None and is_listy(label_cols) and len(label_cols)>1: classes=label_cols
        src = ItemLists(path, TextList.from_df(train_df,path,cols=text_cols,processor=processor),
                        TextList.from_df(valid_df,path,cols=text_cols,processor=processor))
        src = src.label_for_lm() if cls==TextLMDataBunch else src.label_from_df(cols=label_cols, classes=classes)
        if test_df is not None: src.add_test(TextList.from_df(test_df,path,cols=text_cols))
        return src.databunch(**kw)
class BertTextClassifier(BertPreTrainedModel):
    def __init__(self, model_name, num_labels):
        config = BertConfig.from_pretrained(model_name); super().__init__(config)
        self.num_labels=num_labels; self.bert=BertModel.from_pretrained(model_name,config=config)
        self.dropout=nn.Dropout(config.hidden_dropout_prob); self.classifier=nn.Linear(config.hidden_size,num_labels)
    def forward(self, tokens, labels=None, position_ids=None, token_type_ids=None, attention_mask=None, head_mask=None):
        outputs=self.bert(tokens,position_ids=position_ids,token_type_ids=token_type_ids,attention_mask=attention_mask,head_mask=head_mask)
        return self.classifier(self.dropout(outputs[1]))

model_dir = r"C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NoRBERT_pretrained_models\Code\Apply_Pretrained_Model\models"
data = r"C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\data\Code\Task1_to_3_original_Promise_NFR_dataset\promise_nfr.csv"

print("Loading Task1 model...")
learn = load_learner(model_dir, "NoRBERT_Task1_NFR_e10_NoSampling.pkl")
print("Classes:", learn.data.classes)

df = pd.read_csv(data)
texts = df['RequirementText'].tolist()
nfr = df['NFR'].values  # 1 = NFR, 0 = FR

pred_idx = []
for i,t in enumerate(texts):
    cat, idx, probs = learn.predict(t)
    pred_idx.append(int(idx))
    if i < 5:
        print(f"  sample {i}: cat={cat}, idx={int(idx)}, NFR={int(nfr[i])}")
    if (i+1)%100==0: print(f"  {i+1}/{len(texts)}")

pred_idx = np.array(pred_idx)
print("pred idx distribution:", np.bincount(pred_idx))
print("true NFR distribution:", np.bincount(nfr))

# True binary: NFR=1. Try both orientations of model index -> NFR flag
for orient in ['idx_is_NFR', 'idx_is_FR']:
    if orient=='idx_is_NFR':
        yp = pred_idx
    else:
        yp = 1-pred_idx
    f1 = f1_score(nfr, yp, average='weighted')
    acc = accuracy_score(nfr, yp)
    print(f"[{orient}] Acc={acc*100:.2f}% WeightedF1={f1*100:.2f}%")
