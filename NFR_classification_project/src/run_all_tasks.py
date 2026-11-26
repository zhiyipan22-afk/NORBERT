"""
Run all remaining tasks: Task 2 (high-freq NFR 4-class), Task 4, Task 5
using pretrained NoRBERT models.
"""
import os
import pandas as pd
import numpy as np
import torch
import torch.nn as nn

# Monkey-patch torch.load
_original_torch_load = torch.load
def _patched_torch_load(*args, **kwargs):
    kwargs['weights_only'] = False
    return _original_torch_load(*args, **kwargs)
torch.load = _patched_torch_load

# === Import dependencies ===
from fastai import *
from fastai.text import *
from fastai.basic_train import load_learner
from pytorch_transformers import BertTokenizer, BertPreTrainedModel, BertModel, BertConfig
from sklearn.metrics import accuracy_score, f1_score, classification_report

# === Define bert_tok ===
bert_tok = BertTokenizer.from_pretrained('bert-base-cased')

# === Author's custom classes ===
class FastAiBertTokenizer(BaseTokenizer):
    def __init__(self, tokenizer: BertTokenizer, max_seq_len: int=512, **kwargs):
        self._pretrained_tokenizer = tokenizer
        self.max_seq_len = max_seq_len
    def __call__(self, *args, **kwargs):
        return self
    def tokenizer(self, t:str):
        return ["[CLS]"] + self._pretrained_tokenizer.tokenize(t)[:self.max_seq_len - 2] + ["[SEP]"]

class BertTokenizeProcessor(TokenizeProcessor):
    def __init__(self, tokenizer):
        super().__init__(tokenizer=tokenizer, include_bos=False, include_eos=False)

class BertNumericalizeProcessor(NumericalizeProcessor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, vocab=Vocab(list(bert_tok.vocab.keys())), **kwargs)

def get_bert_processor(tokenizer:Tokenizer=None, vocab:Vocab=None):
    return [BertTokenizeProcessor(tokenizer=tokenizer),
            NumericalizeProcessor(vocab=vocab)]

class BertDataBunch(TextDataBunch):
    @classmethod
    def from_df(cls, path:PathOrStr, train_df:DataFrame, valid_df:DataFrame, test_df:Optional[DataFrame]=None,
              tokenizer:Tokenizer=None, vocab:Vocab=None, classes:Collection[str]=None, text_cols:IntsOrStrs=1,
              label_cols:IntsOrStrs=0, **kwargs) -> DataBunch:
        p_kwargs, kwargs = split_kwargs_by_func(kwargs, get_bert_processor)
        processor = get_bert_processor(tokenizer=tokenizer, vocab=vocab, **p_kwargs)
        if classes is None and is_listy(label_cols) and len(label_cols) > 1: classes = label_cols
        src = ItemLists(path, TextList.from_df(train_df, path, cols=text_cols, processor=processor),
                      TextList.from_df(valid_df, path, cols=text_cols, processor=processor))
        src = src.label_for_lm() if cls==TextLMDataBunch else src.label_from_df(cols=label_cols, classes=classes)
        if test_df is not None: src.add_test(TextList.from_df(test_df, path, cols=text_cols))
        return src.databunch(**kwargs)

class BertTextClassifier(BertPreTrainedModel):
    def __init__(self, model_name, num_labels):
        config = BertConfig.from_pretrained(model_name)
        super(BertTextClassifier, self).__init__(config)
        self.num_labels = num_labels
        self.bert = BertModel.from_pretrained(model_name, config=config)
        self.dropout = nn.Dropout(self.config.hidden_dropout_prob)
        self.classifier = nn.Linear(self.config.hidden_size, num_labels)
    def forward(self, tokens, labels=None, position_ids=None, token_type_ids=None, attention_mask=None, head_mask=None):
        outputs = self.bert(tokens, position_ids=position_ids, token_type_ids=token_type_ids, attention_mask=attention_mask, head_mask=head_mask)
        pooled_output = outputs[1]
        dropout_output = self.dropout(pooled_output)
        logits = self.classifier(dropout_output)
        return logits

# === Paths ===
model_dir = r"C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NoRBERT_pretrained_models\Code\Apply_Pretrained_Model\models"
data_dir = r"C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\data\Code"

def load_model(model_name):
    """Load a pretrained fastai learner."""
    print(f"Loading {model_name}...")
    learn = load_learner(model_dir, model_name)
    print(f"  Classes: {learn.data.classes}")
    return learn

def predict_batch(learn, texts, rel_idx_to_name):
    """Predict on a list of texts."""
    preds = []
    for i, text in enumerate(texts):
        pred = learn.predict(text)
        rel_idx = pred[1].item()
        pred_name = rel_idx_to_name.get(rel_idx, f"unknown_{rel_idx}")
        preds.append(pred_name)
        if (i+1) % 50 == 0:
            print(f"    {i+1}/{len(texts)} done...")
    return preds

# ============================================================
# TASK 2: High-frequency NFR subclassification (4 classes)
# ============================================================
print("="*60)
print("TASK 2: High-frequency NFR subclassification (US, SE, O, PE)")
print("="*60)

# Load Task2/3 model
learn_t23 = load_model("NoRBERT_Task2_3_multiclass_all_e32_NoSampling.pkl")

# Build mapping
all_labels_list = ['A', 'FT', 'L', 'LF', 'MN', 'O', 'PE', 'PO', 'SC', 'SE', 'US']
num_to_name = {i: l for i, l in enumerate(all_labels_list)}
classes_list = learn_t23.data.classes
rel_idx_to_name_t23 = {}
for rel_idx, num_label in enumerate(classes_list):
    rel_idx_to_name_t23[rel_idx] = num_to_name[num_label]

# Load dataset
df = pd.read_csv(os.path.join(data_dir, "Task1_to_3_original_Promise_NFR_dataset", "promise_nfr.csv"))
nfr_subcols = ['A', 'FT', 'L', 'LF', 'MN', 'O', 'PE', 'PO', 'SC', 'SE', 'US']

def get_nfr_label(row):
    if row['NFR'] == 0:
        return 'FR'
    for col in nfr_subcols:
        if row[col] == 1:
            return col
    return 'Unknown'

df['true_label'] = df.apply(get_nfr_label, axis=1)
nfr_df = df[df['true_label'] != 'FR'].copy()

# Predict all
print("  Predicting all NFR samples...")
preds = predict_batch(learn_t23, nfr_df['RequirementText'].tolist(), rel_idx_to_name_t23)
nfr_df['pred_label'] = preds

# Filter to 4 high-frequency classes: US, SE, O, PE
high_freq = ['US', 'SE', 'O', 'PE']
t2_df = nfr_df[nfr_df['true_label'].isin(high_freq)].copy()

y_true = t2_df['true_label'].tolist()
y_pred = t2_df['pred_label'].tolist()

acc = accuracy_score(y_true, y_pred)
weighted_f1 = f1_score(y_true, y_pred, average='weighted')

print(f"\n  Task 2 Results (4 classes: US, SE, O, PE):")
print(f"    Samples: {len(t2_df)}")
print(f"    Accuracy: {acc:.4f} ({acc*100:.2f}%)")
print(f"    Weighted F1: {weighted_f1:.4f} ({weighted_f1*100:.2f}%)")
print(classification_report(y_true, y_pred, zero_division=0))

# ============================================================
# TASK 4: Relabeled dataset (F vs Q aspects)
# ============================================================
print("\n" + "="*60)
print("TASK 4: Relabeled dataset - F/Q aspect classification")
print("="*60)

# Load Task4 dataset
df4 = pd.read_csv(os.path.join(data_dir, "Task4_relabeled_Promise_NFR_dataset", "promise-reclass.csv"))
print(f"  Dataset shape: {df4.shape}")
print(f"  Columns: {df4.columns.tolist()}")
print(f"  First few rows:")
print(df4.head())

# Save Task2 results
nfr_df.to_csv(r"C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\data\pretrained_task2_full_results.csv", index=False)
print("\n  Task 2 results saved.")
