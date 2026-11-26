"""
Load pretrained NoRBERT Task 2/3 model and evaluate on PROMISE NFR dataset.
Fixed class index mapping.
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

# === Load model ===
model_path = r"C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NoRBERT_pretrained_models\Code\Apply_Pretrained_Model\models"
model_name = "NoRBERT_Task2_3_multiclass_all_e32_NoSampling.pkl"

print("Loading model...")
learn = load_learner(model_path, model_name)
print("Model loaded!")

# Get the actual classes from the model
print(f"Model data.classes: {learn.data.classes}")
# classes are numeric labels: [0, 1, 2, 3, 4, 5, 6, 8, 9, 10]
# We need to map these to class names
# From notebook: labels = ['A', 'FT', 'L', 'LF', 'MN', 'O', 'PE', 'PO', 'SC', 'SE', 'US']
# Index 0=A, 1=FT, ..., 6=PE, 7=PO, 8=SC, 9=SE, 10=US
all_labels_list = ['A', 'FT', 'L', 'LF', 'MN', 'O', 'PE', 'PO', 'SC', 'SE', 'US']
num_to_name = {i: l for i, l in enumerate(all_labels_list)}

# Build mapping: relative index (0-9) -> class name
# data.classes = [0, 1, 2, 3, 4, 5, 6, 8, 9, 10]
# relative_idx=0 -> classes[0]=0 -> A
# relative_idx=7 -> classes[7]=8 -> SC
classes_list = learn.data.classes
rel_idx_to_name = {}
for rel_idx, num_label in enumerate(classes_list):
    rel_idx_to_name[rel_idx] = num_to_name[num_label]

print(f"Relative index to name mapping: {rel_idx_to_name}")

# === Load dataset ===
data_path = r"C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\data\Code\Task1_to_3_original_Promise_NFR_dataset\promise_nfr.csv"
df = pd.read_csv(data_path)

# NFR subclass columns
nfr_subcols = ['A', 'FT', 'L', 'LF', 'MN', 'O', 'PE', 'PO', 'SC', 'SE', 'US']

def get_nfr_label(row):
    if row['NFR'] == 0:
        return 'FR'
    for col in nfr_subcols:
        if row[col] == 1:
            return col
    return 'Unknown'

df['true_label'] = df.apply(get_nfr_label, axis=1)

# Filter NFR samples only
nfr_df = df[df['true_label'] != 'FR'].copy()
print(f"\nNFR samples: {len(nfr_df)}")

# === Predict on all NFR samples ===
print("\nRunning predictions...")
predictions = []
for i, (idx, row) in enumerate(nfr_df.iterrows()):
    req = row['RequirementText']
    pred = learn.predict(req)
    # pred[1] is relative index (0-9) into data.classes
    pred_rel_idx = pred[1].item()
    pred_name = rel_idx_to_name[pred_rel_idx]
    predictions.append(pred_name)
    if (i+1) % 50 == 0:
        print(f"  {i+1}/{len(nfr_df)} done...")

nfr_df['pred_label'] = predictions

# === Evaluate ===
print("\n" + "="*60)
print("Task 2/3 Pretrained NoRBERT Results")
print("="*60)

# Remove PO samples (only 1 sample, excluded from training)
eval_df = nfr_df[nfr_df['true_label'] != 'PO']
y_true = eval_df['true_label'].tolist()
y_pred = eval_df['pred_label'].tolist()

acc = accuracy_score(y_true, y_pred)
weighted_f1 = f1_score(y_true, y_pred, average='weighted')
macro_f1 = f1_score(y_true, y_pred, average='macro')

print(f"Test samples: {len(eval_df)}")
print(f"Accuracy: {acc:.4f} ({acc*100:.2f}%)")
print(f"Weighted F1: {weighted_f1:.4f} ({weighted_f1*100:.2f}%)")
print(f"Macro F1: {macro_f1:.4f} ({macro_f1*100:.2f}%)")
print("\nClassification Report:")
print(classification_report(y_true, y_pred, zero_division=0))

# Save results
eval_df.to_csv(r"C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\data\pretrained_task2_results.csv", index=False)
print("\nResults saved to data/pretrained_task2_results.csv")
