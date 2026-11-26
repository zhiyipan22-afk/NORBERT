"""
NoRBERT Task 2: NFR Sub-classification (11 classes)
只用NFR样本，分类到11个子类
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, f1_score, accuracy_score
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import BertTokenizer, BertForSequenceClassification, get_linear_schedule_with_warmup
import warnings
warnings.filterwarnings("ignore")

# 加载数据
print("Loading PROMISE NFR dataset...")
data_path = r"C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\data\Code\Task1_to_3_original_Promise_NFR_dataset\promise_nfr.csv"
df = pd.read_csv(data_path)

# 只取NFR样本（Task 2），去掉PO类（只有1个样本，无法分类）
nfr_cols = ['A', 'FT', 'L', 'LF', 'MN', 'O', 'PE', 'SC', 'SE', 'US']  # 去掉PO
df_nfr = df[df['NFR'] == 1].copy()
# 过滤掉PO类样本（PO=1的行）
df_nfr = df_nfr[df_nfr['PO'] == 0].copy()
print(f"NFR samples (excl. PO): {len(df_nfr)}")

# 找到每行的子类标签
df_nfr['subclass'] = df_nfr[nfr_cols].values.argmax(axis=1)
class_names = nfr_cols

print(f"\nClass distribution:")
for i, col in enumerate(nfr_cols):
    count = (df_nfr['subclass'] == i).sum()
    print(f"  {col}: {count}")

texts = df_nfr['RequirementText'].tolist()
labels = df_nfr['subclass'].tolist()

# 划分数据集
X_train, X_test, y_train, y_test = train_test_split(
    texts, labels, test_size=0.2, random_state=42, stratify=labels
)

print(f"\nTrain: {len(X_train)}, Test: {len(X_test)}")

device = torch.device("cpu")
model_name = "bert-base-uncased"
tokenizer = BertTokenizer.from_pretrained(model_name)

MAX_LEN = 128
BATCH_SIZE = 16
EPOCHS = 4

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

# 类别权重（处理极度不平衡）
counts = np.bincount(y_train)
class_weights = len(y_train) / (len(nfr_cols) * counts)
print(f"Class weights: {dict(zip(nfr_cols, class_weights.round(2)))}")

# ============================================================
# 实验1: 标准 BERT 微调
# ============================================================
print("\n" + "=" * 60)
print("Task 2: NFR Sub-classification (11 classes)")
print("=" * 60)

model = BertForSequenceClassification.from_pretrained(
    model_name, num_labels=len(nfr_cols), hidden_dropout_prob=0.3
)
model = model.to(device)

optimizer = torch.optim.AdamW(model.parameters(), lr=2e-5, weight_decay=0.01)
total_steps = len(train_loader) * EPOCHS
scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=0, num_training_steps=total_steps)

for epoch in range(EPOCHS):
    model.train()
    total_loss = 0
    for batch in train_loader:
        optimizer.zero_grad()
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels_batch = batch["labels"].to(device)
        outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels_batch)
        outputs.loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        scheduler.step()
        total_loss += outputs.loss.item()
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
print("Task 2 Results:")
print("=" * 60)
print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
print(f"Weighted F1: {f1_score(y_test, y_pred, average='weighted'):.4f}")
print(f"Macro F1: {f1_score(y_test, y_pred, average='macro'):.4f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=class_names, zero_division=0))

# 保存结果
pd.DataFrame({
    "y_true": y_test,
    "y_pred": y_pred,
}).to_csv(r"C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\data\task2_results.csv", index=False)
print("\nResults saved.")
