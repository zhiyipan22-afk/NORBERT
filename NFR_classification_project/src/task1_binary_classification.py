"""
NoRBERT 复现：Task 1 - Binary F/NFR Classification
基于 PROMISE NFR 数据集
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.metrics import classification_report, f1_score, accuracy_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import BertTokenizer, BertForSequenceClassification, get_linear_schedule_with_warmup
import time
import warnings
warnings.filterwarnings("ignore")

# ============================================================
# 1. 加载数据
# ============================================================
print("=" * 60)
print("Step 1: Loading PROMISE NFR dataset")
print("=" * 60)

data_path = r"C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\data\Code\Task1_to_3_original_Promise_NFR_dataset\promise_nfr.csv"
df = pd.read_csv(data_path)

print(f"Total samples: {len(df)}")
print(f"FR (Functional): {len(df[df['F'] == 1])}")
print(f"NFR (Non-functional): {len(df[df['NFR'] == 1])}")
print(f"\nNFR sub-class distribution:")
nfr_cols = ['A', 'FT', 'L', 'LF', 'MN', 'O', 'PE', 'PO', 'SC', 'SE', 'US']
for col in nfr_cols:
    count = df[col].sum()
    if count > 0:
        print(f"  {col}: {count}")

# 二分类任务：FR vs NFR
df['label'] = df['F'].astype(int)  # 1 = Functional, 0 = NFR
texts = df['RequirementText'].tolist()
labels = df['label'].tolist()

print(f"\nBinary classification: FR (1)={sum(labels)}, NFR (0)={len(labels)-sum(labels)}")

# ============================================================
# 2. 传统ML Baseline (TF-IDF + Logistic Regression)
# ============================================================
print("\n" + "=" * 60)
print("Step 2: Baseline - TF-IDF + Logistic Regression")
print("=" * 60)

X_train, X_test, y_train, y_test = train_test_split(
    texts, labels, test_size=0.2, random_state=42, stratify=labels
)

vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

clf = LogisticRegression(max_iter=1000, random_state=42)
clf.fit(X_train_tfidf, y_train)
y_pred_lr = clf.predict(X_test_tfidf)

print(f"Logistic Regression Results:")
print(f"  Accuracy: {accuracy_score(y_test, y_pred_lr):.4f}")
print(f"  F1 (weighted): {f1_score(y_test, y_pred_lr, average='weighted'):.4f}")
print(classification_report(y_test, y_pred_lr, target_names=['NFR', 'FR']))

# ============================================================
# 3. BERT 微调
# ============================================================
print("\n" + "=" * 60)
print("Step 3: Fine-tuning BERT-base-uncased")
print("=" * 60)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# 加载 tokenizer 和模型
model_name = "bert-base-uncased"
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertForSequenceClassification.from_pretrained(
    model_name, num_labels=2, hidden_dropout_prob=0.2
)
model = model.to(device)

# 超参数（参考 NoRBERT 论文）
MAX_LEN = 128
BATCH_SIZE = 8
EPOCHS = 4
LEARNING_RATE = 2e-5

# 自定义 Dataset
class RequirementsDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_len):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]
        encoding = self.tokenizer(
            text,
            max_length=self.max_len,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )
        return {
            "input_ids": encoding["input_ids"].flatten(),
            "attention_mask": encoding["attention_mask"].flatten(),
            "labels": torch.tensor(label, dtype=torch.long),
        }

# 划分数据集
X_train, X_test, y_train, y_test = train_test_split(
    texts, labels, test_size=0.2, random_state=42, stratify=labels
)

train_dataset = RequirementsDataset(X_train, y_train, tokenizer, MAX_LEN)
test_dataset = RequirementsDataset(X_test, y_test, tokenizer, MAX_LEN)

train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False)

# 优化器和调度器
optimizer = torch.optim.AdamW(model.parameters(), lr=LEARNING_RATE, weight_decay=0.01)
total_steps = len(train_loader) * EPOCHS
scheduler = get_linear_schedule_with_warmup(
    optimizer, num_warmup_steps=0, num_training_steps=total_steps
)

# 训练循环
print(f"\nTraining BERT for {EPOCHS} epochs...")
print(f"Train samples: {len(train_dataset)}, Test samples: {len(test_dataset)}")
start_time = time.time()

for epoch in range(EPOCHS):
    model.train()
    total_loss = 0
    for batch in train_loader:
        optimizer.zero_grad()
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels_batch = batch["labels"].to(device)

        outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels_batch)
        loss = outputs.loss
        total_loss += loss.item()

        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        scheduler.step()

    avg_train_loss = total_loss / len(train_loader)

    # 验证
    model.eval()
    y_pred = []
    y_true = []
    with torch.no_grad():
        for batch in test_loader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels_batch = batch["labels"].to(device)

            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            preds = torch.argmax(outputs.logits, dim=1)

            y_pred.extend(preds.cpu().numpy())
            y_true.extend(labels_batch.cpu().numpy())

    f1 = f1_score(y_true, y_pred, average="weighted")
    acc = accuracy_score(y_true, y_pred)
    elapsed = time.time() - start_time

    print(f"Epoch {epoch+1}/{EPOCHS} | Loss: {avg_train_loss:.4f} | Acc: {acc:.4f} | F1: {f1:.4f} | Time: {elapsed:.1f}s")

# 最终评估
print("\n" + "=" * 60)
print("Final BERT Results")
print("=" * 60)
print(f"Accuracy: {accuracy_score(y_true, y_pred):.4f}")
print(f"F1 (weighted): {f1_score(y_true, y_pred, average='weighted'):.4f}")
print(classification_report(y_true, y_pred, target_names=['NFR', 'FR']))

# ============================================================
# 4. 保存结果
# ============================================================
results = {
    "model": ["Logistic Regression", "BERT-base"],
    "accuracy": [accuracy_score(y_test, y_pred_lr), accuracy_score(y_true, y_pred)],
    "weighted_f1": [f1_score(y_test, y_pred_lr, average="weighted"), f1_score(y_true, y_pred, average="weighted")],
}
results_df = pd.DataFrame(results)
print("\nComparison Summary:")
print(results_df)

# 保存预测结果（用于后续统计检验）
pd.DataFrame({
    "y_true": y_true,
    "y_pred_bert": y_pred,
}).to_csv(r"C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\data\bert_predictions.csv", index=False)

print("\nDone! Predictions saved for statistical testing.")
