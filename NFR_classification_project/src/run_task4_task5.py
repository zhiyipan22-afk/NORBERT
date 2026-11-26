"""
Run Task 4 and Task 5 with pretrained NoRBERT models.
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
from sklearn.metrics import accuracy_score, f1_score, classification_report, roc_auc_score

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
results = {}

def load_model(model_name):
    print(f"  Loading {model_name}...")
    learn = load_learner(model_dir, model_name)
    print(f"    Classes: {learn.data.classes}")
    return learn

def predict_binary(learn, texts, positive_class_idx=1):
    """Binary classification: predict 1 if predicted class == positive_class_idx."""
    preds = []
    for i, text in enumerate(texts):
        pred = learn.predict(text)
        # pred[1] is relative index; check if it corresponds to positive class
        rel_idx = pred[1].item()
        # For binary classification, classes are usually [0, 1]
        # positive class is the second one (index 1 in relative terms if classes=[0,1])
        actual_class = learn.data.classes[rel_idx]
        preds.append(actual_class)
        if (i+1) % 50 == 0:
            print(f"      {i+1}/{len(texts)} done...")
    return preds

# ============================================================
# TASK 4: Relabeled dataset (F/Q aspect classification)
# ============================================================
print("="*60)
print("TASK 4: Relabeled dataset - F/Q aspect classification")
print("="*60)

df4 = pd.read_csv(os.path.join(data_dir, "Task4_relabeled_Promise_NFR_dataset", "promise-reclass.csv"))
texts4 = df4['RequirementText'].tolist()
print(f"  Dataset: {len(df4)} samples")

# Task 4 models
task4_models = {
    'IsFunctional': 'NoRBERT_Task4_F_e10_NoSampling.pkl',
    'IsQuality': 'NoRBERT_Task4_Q_e10_NoSampling.pkl',
    'IsOnlyFunctional': 'NoRBERT_Task4_OnlyF_e10_NoSampling.pkl',
    'IsOnlyQuality': 'NoRBERT_Task4_OnlyQ_e10_NoSampling.pkl',
}

for label_col, model_file in task4_models.items():
    print(f"\n  --- {label_col} ---")
    learn = load_model(model_file)
    preds = predict_binary(learn, texts4)
    y_true = df4[label_col].tolist()
    y_pred = preds

    acc = accuracy_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred, average='binary')
    print(f"    Accuracy: {acc:.4f} ({acc*100:.2f}%)")
    print(f"    F1: {f1:.4f} ({f1*100:.2f}%)")
    results[f'Task4_{label_col}'] = {'acc': acc, 'f1': f1}

# ============================================================
# TASK 5: Functional requirement concerns (Function, Data, Behavior)
# ============================================================
print("\n" + "="*60)
print("TASK 5: Functional requirement concerns")
print("="*60)

df5 = pd.read_csv(os.path.join(data_dir, "Task5_func_concerns_dataset", "func_concerns.csv"))
texts5 = df5['RequirementText'].tolist()
print(f"  Dataset: {len(df5)} samples")

# Task 5 models
task5_models = {
    'Function': 'NoRBERT_Task5_Function_e16_OverSampling.pkl',
    'Data': 'NoRBERT_Task5_Data_e16_OverSampling.pkl',
    'Behavior': 'NoRBERT_Task5_Behavior_e16_OverSampling.pkl',
}

for label_col, model_file in task5_models.items():
    print(f"\n  --- {label_col} ---")
    learn = load_model(model_file)
    preds = predict_binary(learn, texts5)
    y_true = df5[label_col].tolist()
    y_pred = preds

    acc = accuracy_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred, average='binary')
    print(f"    Accuracy: {acc:.4f} ({acc*100:.2f}%)")
    print(f"    F1: {f1:.4f} ({f1*100:.2f}%)")
    results[f'Task5_{label_col}'] = {'acc': acc, 'f1': f1}

# ============================================================
# Summary
# ============================================================
print("\n" + "="*60)
print("SUMMARY: All Pretrained Model Results")
print("="*60)
for task, metrics in results.items():
    print(f"  {task}: Acc={metrics['acc']*100:.2f}%, F1={metrics['f1']*100:.2f}%")

# Save summary
pd.DataFrame(results).T.to_csv(r"C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\data\pretrained_all_tasks_summary.csv")
print("\nSummary saved to data/pretrained_all_tasks_summary.csv")
