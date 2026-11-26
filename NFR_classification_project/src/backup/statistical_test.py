"""
统计显著性检验：5折交叉验证 + 配对t检验 + Wilcoxon检验
比较 BERT vs Logistic Regression 在 NFR 分类任务上的差异
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import f1_score, accuracy_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from scipy import stats
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import BertTokenizer, BertForSequenceClassification, get_linear_schedule_with_warmup
import time
import warnings
warnings.filterwarnings("ignore")

# ============================================================
# 加载数据
# ============================================================
print("Loading PROMISE NFR dataset...")
data_path = r"C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\data\Code\Task1_to_3_original_Promise_NFR_dataset\promise_nfr.csv"
df = pd.read_csv(data_path)
df['label'] = df['F'].astype(int)
texts = df['RequirementText'].tolist()
labels = df['label'].tolist()

print(f"Total: {len(df)} samples, FR={sum(labels)}, NFR={len(labels)-sum(labels)}")

# ============================================================
# 5折交叉验证
# ============================================================
N_SPLITS = 5
skf = StratifiedKFold(n_splits=N_SPLITS, shuffle=True, random_state=42)

lr_f1_scores = []
bert_f1_scores = []
lr_acc_scores = []
bert_acc_scores = []

device = torch.device("cpu")
model_name = "bert-base-uncased"
tokenizer = BertTokenizer.from_pretrained(model_name)

MAX_LEN = 128
BATCH_SIZE = 16
EPOCHS = 2  # CPU上跑，减少epoch数

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

print(f"\nStarting {N_SPLITS}-fold cross validation...")
print("=" * 60)

for fold, (train_idx, test_idx) in enumerate(skf.split(texts, labels)):
    fold_start = time.time()
    X_train = [texts[i] for i in train_idx]
    y_train = [labels[i] for i in train_idx]
    X_test = [texts[i] for i in test_idx]
    y_test = [labels[i] for i in test_idx]

    # --- Logistic Regression ---
    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)
    clf = LogisticRegression(max_iter=1000, random_state=42)
    clf.fit(X_train_tfidf, y_train)
    y_pred_lr = clf.predict(X_test_tfidf)
    lr_f1 = f1_score(y_test, y_pred_lr, average='weighted')
    lr_acc = accuracy_score(y_test, y_pred_lr)
    lr_f1_scores.append(lr_f1)
    lr_acc_scores.append(lr_acc)

    # --- BERT ---
    model = BertForSequenceClassification.from_pretrained(model_name, num_labels=2, hidden_dropout_prob=0.2)
    model = model.to(device)
    model.train()

    train_dataset = RequirementsDataset(X_train, y_train, tokenizer, MAX_LEN)
    test_dataset = RequirementsDataset(X_test, y_test, tokenizer, MAX_LEN)
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False)

    optimizer = torch.optim.AdamW(model.parameters(), lr=2e-5, weight_decay=0.01)
    total_steps = len(train_loader) * EPOCHS
    scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=0, num_training_steps=total_steps)

    for epoch in range(EPOCHS):
        model.train()
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

    model.eval()
    y_pred_bert = []
    with torch.no_grad():
        for batch in test_loader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            preds = torch.argmax(outputs.logits, dim=1)
            y_pred_bert.extend(preds.cpu().numpy())

    bert_f1 = f1_score(y_test, y_pred_bert, average='weighted')
    bert_acc = accuracy_score(y_test, y_pred_bert)
    bert_f1_scores.append(bert_f1)
    bert_acc_scores.append(bert_acc)

    fold_time = time.time() - fold_start
    print(f"Fold {fold+1}/{N_SPLITS} | LR F1={lr_f1:.4f} | BERT F1={bert_f1:.4f} | Time: {fold_time:.0f}s")

    # 释放模型内存
    del model
    torch.cuda.empty_cache() if torch.cuda.is_available() else None

# ============================================================
# 统计检验
# ============================================================
print("\n" + "=" * 60)
print("Statistical Significance Test Results")
print("=" * 60)

print(f"\nLogistic Regression:")
print(f"  Mean F1: {np.mean(lr_f1_scores):.4f} (±{np.std(lr_f1_scores):.4f})")
print(f"  Mean Acc: {np.mean(lr_acc_scores):.4f}")

print(f"\nBERT-base:")
print(f"  Mean F1: {np.mean(bert_f1_scores):.4f} (±{np.std(bert_f1_scores):.4f})")
print(f"  Mean Acc: {np.mean(bert_acc_scores):.4f}")

# 配对t检验
t_stat, t_pvalue = stats.ttest_rel(bert_f1_scores, lr_f1_scores)
print(f"\nPaired t-test (BERT vs LR, F1):")
print(f"  t-statistic = {t_stat:.4f}")
print(f"  p-value = {t_pvalue:.4f}")
print(f"  Significant at α=0.05? {'YES' if t_pvalue < 0.05 else 'NO'}")

# Wilcoxon符号秩检验（非参数）
w_stat, w_pvalue = stats.wilcoxon(bert_f1_scores, lr_f1_scores)
print(f"\nWilcoxon signed-rank test (BERT vs LR, F1):")
print(f"  W-statistic = {w_stat:.4f}")
print(f"  p-value = {w_pvalue:.4f}")
print(f"  Significant at α=0.05? {'YES' if w_pvalue < 0.05 else 'NO'}")

# 效应量 (Cohen's d)
diff = np.array(bert_f1_scores) - np.array(lr_f1_scores)
cohens_d = np.mean(diff) / np.std(diff)
print(f"\nEffect size (Cohen's d): {cohens_d:.4f}")
print(f"  Magnitude: {'small' if abs(cohens_d)<0.5 else 'medium' if abs(cohens_d)<0.8 else 'large'}")

# 保存结果
results = pd.DataFrame({
    "fold": list(range(1, N_SPLITS+1)),
    "lr_f1": lr_f1_scores,
    "bert_f1": bert_f1_scores,
    "lr_acc": lr_acc_scores,
    "bert_acc": bert_acc_scores,
})
results.to_csv(r"C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\data\cv_results.csv", index=False)
print(f"\nResults saved to cv_results.csv")
