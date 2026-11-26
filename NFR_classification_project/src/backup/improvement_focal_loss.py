"""
改进实验：Focal Loss 处理类别不平衡
对比标准 CrossEntropyLoss vs Focal Loss
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, f1_score, accuracy_score
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from transformers import BertTokenizer, BertForSequenceClassification, get_linear_schedule_with_warmup
import time
import warnings
warnings.filterwarnings("ignore")

# Focal Loss 实现
class FocalLoss(nn.Module):
    def __init__(self, alpha=0.25, gamma=2.0):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma
    def forward(self, logits, targets):
        ce_loss = nn.functional.cross_entropy(logits, targets, reduction='none')
        pt = torch.exp(-ce_loss)
        focal_loss = self.alpha * (1 - pt) ** self.gamma * ce_loss
        return focal_loss.mean()

# 加载数据
print("Loading data...")
data_path = r"C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\data\Code\Task1_to_3_original_Promise_NFR_dataset\promise_nfr.csv"
df = pd.read_csv(data_path)
df['label'] = df['F'].astype(int)
texts = df['RequirementText'].tolist()
labels = df['label'].tolist()

X_train, X_test, y_train, y_test = train_test_split(
    texts, labels, test_size=0.2, random_state=42, stratify=labels
)

device = torch.device("cpu")
model_name = "bert-base-uncased"
tokenizer = BertTokenizer.from_pretrained(model_name)

MAX_LEN = 128
BATCH_SIZE = 16
EPOCHS = 3

class RequirementsDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_len):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = max_len
    def __len__(self):
        return len(self.texts)
    def __getitem__(self, idx):
        encoding = self.tokenizer(
            str(self.texts[idx]), max_length=self.max_len,
            padding="max_length", truncation=True, return_tensors="pt"
        )
        return {
            "input_ids": encoding["input_ids"].flatten(),
            "attention_mask": encoding["attention_mask"].flatten(),
            "labels": torch.tensor(self.labels[idx], dtype=torch.long),
        }

train_dataset = RequirementsDataset(X_train, y_train, tokenizer, MAX_LEN)
test_dataset = RequirementsDataset(X_test, y_test, tokenizer, MAX_LEN)
train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False)

# ============================================================
# 实验1: 标准 CrossEntropyLoss (基线 BERT)
# ============================================================
print("\n" + "=" * 60)
print("Experiment 1: BERT + CrossEntropyLoss (baseline)")
print("=" * 60)

model1 = BertForSequenceClassification.from_pretrained(model_name, num_labels=2, hidden_dropout_prob=0.2)
model1 = model1.to(device)
optimizer1 = torch.optim.AdamW(model1.parameters(), lr=2e-5, weight_decay=0.01)
total_steps = len(train_loader) * EPOCHS
scheduler1 = get_linear_schedule_with_warmup(optimizer1, num_warmup_steps=0, num_training_steps=total_steps)

start = time.time()
for epoch in range(EPOCHS):
    model1.train()
    total_loss = 0
    for batch in train_loader:
        optimizer1.zero_grad()
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels_batch = batch["labels"].to(device)
        outputs = model1(input_ids=input_ids, attention_mask=attention_mask, labels=labels_batch)
        outputs.loss.backward()
        torch.nn.utils.clip_grad_norm_(model1.parameters(), 1.0)
        optimizer1.step()
        scheduler1.step()
        total_loss += outputs.loss.item()
    print(f"  Epoch {epoch+1}/{EPOCHS} | Loss: {total_loss/len(train_loader):.4f}")

model1.eval()
y_pred_ce = []
with torch.no_grad():
    for batch in test_loader:
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        outputs = model1(input_ids=input_ids, attention_mask=attention_mask)
        preds = torch.argmax(outputs.logits, dim=1)
        y_pred_ce.extend(preds.cpu().numpy())

ce_f1 = f1_score(y_test, y_pred_ce, average='weighted')
ce_acc = accuracy_score(y_test, y_pred_ce)
print(f"\n  CrossEntropy Results: Acc={ce_acc:.4f}, Weighted F1={ce_f1:.4f}")

del model1

# ============================================================
# 实验2: Focal Loss (改进版)
# ============================================================
print("\n" + "=" * 60)
print("Experiment 2: BERT + Focal Loss (improved)")
print("=" * 60)

model2 = BertForSequenceClassification.from_pretrained(model_name, num_labels=2, hidden_dropout_prob=0.2)
model2 = model2.to(device)
optimizer2 = torch.optim.AdamW(model2.parameters(), lr=2e-5, weight_decay=0.01)
scheduler2 = get_linear_schedule_with_warmup(optimizer2, num_warmup_steps=0, num_training_steps=total_steps)

focal_loss_fn = FocalLoss(alpha=0.25, gamma=2.0)

for epoch in range(EPOCHS):
    model2.train()
    total_loss = 0
    for batch in train_loader:
        optimizer2.zero_grad()
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels_batch = batch["labels"].to(device)
        outputs = model2(input_ids=input_ids, attention_mask=attention_mask)
        loss = focal_loss_fn(outputs.logits, labels_batch)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model2.parameters(), 1.0)
        optimizer2.step()
        scheduler2.step()
        total_loss += loss.item()
    print(f"  Epoch {epoch+1}/{EPOCHS} | Loss: {total_loss/len(train_loader):.4f}")

model2.eval()
y_pred_focal = []
with torch.no_grad():
    for batch in test_loader:
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        outputs = model2(input_ids=input_ids, attention_mask=attention_mask)
        preds = torch.argmax(outputs.logits, dim=1)
        y_pred_focal.extend(preds.cpu().numpy())

focal_f1 = f1_score(y_test, y_pred_focal, average='weighted')
focal_acc = accuracy_score(y_test, y_pred_focal)
print(f"\n  Focal Loss Results: Acc={focal_acc:.4f}, Weighted F1={focal_f1:.4f}")

# ============================================================
# 对比总结
# ============================================================
print("\n" + "=" * 60)
print("Improvement Summary")
print("=" * 60)
print(f"{'Model':<30} {'Accuracy':>10} {'Weighted F1':>12}")
print("-" * 55)
print(f"{'BERT + CrossEntropy':<30} {ce_acc:>10.4f} {ce_f1:>12.4f}")
print(f"{'BERT + Focal Loss (improved)':<30} {focal_acc:>10.4f} {focal_f1:>12.4f}")
print(f"\nImprovement: F1 +{(focal_f1 - ce_f1)*100:.2f}%")

# 保存
pd.DataFrame({
    "y_true": y_test,
    "y_pred_ce": y_pred_ce,
    "y_pred_focal": y_pred_focal,
}).to_csv(r"C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\data\improvement_results.csv", index=False)
print("\nResults saved.")
