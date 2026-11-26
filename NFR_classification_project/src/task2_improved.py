"""
Task 2 改进版：类别加权 CrossEntropyLoss + 少数类过采样
解决NFR子类分类的类别不平衡问题
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, f1_score, accuracy_score
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from transformers import BertTokenizer, BertForSequenceClassification, get_linear_schedule_with_warmup
import warnings
warnings.filterwarnings("ignore")

# 加载数据
print("Loading PROMISE NFR dataset...")
data_path = r"C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\data\Code\Task1_to_3_original_Promise_NFR_dataset\promise_nfr.csv"
df = pd.read_csv(data_path)

# 只取NFR样本，去掉PO类（只有1个样本）
nfr_cols = ['A', 'FT', 'L', 'LF', 'MN', 'O', 'PE', 'SC', 'SE', 'US']
df_nfr = df[(df['NFR'] == 1) & (df['PO'] == 0)].copy()
df_nfr['subclass'] = df_nfr[nfr_cols].values.argmax(axis=1)
class_names = nfr_cols

print(f"NFR samples (excl. PO): {len(df_nfr)}")
for i, col in enumerate(nfr_cols):
    print(f"  {col}: {(df_nfr['subclass'] == i).sum()}")

texts = df_nfr['RequirementText'].tolist()
labels = df_nfr['subclass'].tolist()

X_train, X_test, y_train, y_test = train_test_split(
    texts, labels, test_size=0.2, random_state=42, stratify=labels
)

# 少数类过采样：把样本数少于30的类复制到30条
print("\nOversampling minority classes...")
X_train_aug = list(X_train)
y_train_aug = list(y_train)
counts = np.bincount(y_train_aug)
for cls_idx in range(len(nfr_cols)):
    cls_count = counts[cls_idx]
    if cls_count < 25:
        # 找这个类的所有样本
        cls_samples = [(t, l) for t, l in zip(X_train_aug, y_train_aug) if l == cls_idx]
        # 复制到至少25条
        needed = 25 - cls_count
        for i in range(needed):
            sample = cls_samples[i % len(cls_samples)]
            X_train_aug.append(sample[0])
            y_train_aug.append(sample[1])

print(f"Train before: {len(X_train)}, after oversampling: {len(X_train_aug)}")
new_counts = np.bincount(y_train_aug)
for i, col in enumerate(nfr_cols):
    print(f"  {col}: {new_counts[i]}")

device = torch.device("cpu")
model_name = "bert-base-uncased"
tokenizer = BertTokenizer.from_pretrained(model_name)

MAX_LEN = 128
BATCH_SIZE = 16
EPOCHS = 5

# 类别权重
class_weights = len(y_train_aug) / (len(nfr_cols) * new_counts)
weight_tensor = torch.tensor(class_weights, dtype=torch.float).to(device)
print(f"\nClass weights: {dict(zip(nfr_cols, class_weights.round(2)))}")

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

train_dataset = RequirementsDataset(X_train_aug, y_train_aug, tokenizer, MAX_LEN)
test_dataset = RequirementsDataset(X_test, y_test, tokenizer, MAX_LEN)
train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False)

# ============================================================
# 跑模型
# ============================================================
print("\n" + "=" * 60)
print("Task 2 Improved: Weighted CE + Oversampling")
print("=" * 60)

model = BertForSequenceClassification.from_pretrained(
    model_name, num_labels=len(nfr_cols), hidden_dropout_prob=0.3
)
model = model.to(device)

optimizer = torch.optim.AdamW(model.parameters(), lr=3e-5, weight_decay=0.01)
total_steps = len(train_loader) * EPOCHS
scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=0, num_training_steps=total_steps)

ce_loss_fn = nn.CrossEntropyLoss(weight=weight_tensor)

for epoch in range(EPOCHS):
    model.train()
    total_loss = 0
    for batch in train_loader:
        optimizer.zero_grad()
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels_batch = batch["labels"].to(device)
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        loss = ce_loss_fn(outputs.logits, labels_batch)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        scheduler.step()
        total_loss += loss.item()
    print(f"  Epoch {epoch+1}/{EPOCHS} | Loss: {total_loss/len(train_loader):.4f}")

# 评估
model.eval()
y_pred = []
with torch.no_grad():
    for batch in test_loader:
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        preds = torch.argmax(outputs.logits, dim=1)
        y_pred.extend(preds.cpu().numpy())

print("\n" + "=" * 60)
print("Task 2 Improved Results:")
print("=" * 60)
print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
print(f"Weighted F1: {f1_score(y_test, y_pred, average='weighted'):.4f}")
print(f"Macro F1: {f1_score(y_test, y_pred, average='macro'):.4f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=class_names, zero_division=0))

pd.DataFrame({
    "y_true": y_test,
    "y_pred": y_pred,
}).to_csv(r"C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\data\task2_improved_results.csv", index=False)
print("\nResults saved.")
