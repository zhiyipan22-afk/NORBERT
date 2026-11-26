"""
Task 2/3 improvement experiments with statistical significance tests.
- Baseline: BERT-base (no weighting)
- Improved: BERT-base + class weighting + oversampling
- 5-fold stratified cross-validation
- Paired t-test + Wilcoxon signed-rank test
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score, f1_score, classification_report
from sklearn.utils.class_weight import compute_class_weight
from scipy import stats
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from transformers import BertTokenizer, BertForSequenceClassification, get_linear_schedule_with_warmup
from torch.optim import AdamW
import warnings
warnings.filterwarnings('ignore')

# === Config ===
MAX_LEN = 128
BATCH_SIZE = 16
EPOCHS = 3
LR = 2e-5
RANDOM_STATE = 42
MODEL_NAME = 'bert-base-uncased'

# === Load data ===
data_path = r"C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\data\Code\Task1_to_3_original_Promise_NFR_dataset\promise_nfr.csv"
df = pd.read_csv(data_path)

nfr_subcols = ['A', 'FT', 'L', 'LF', 'MN', 'O', 'PE', 'PO', 'SC', 'SE', 'US']

def get_nfr_label(row):
    if row['NFR'] == 0:
        return None  # FR, skip
    for col in nfr_subcols:
        if row[col] == 1:
            return col
    return None

df['label'] = df.apply(get_nfr_label, axis=1)
nfr_df = df[df['label'].notna()].copy()

# Encode labels
labels_list = sorted(nfr_df['label'].unique().tolist())
label2idx = {l: i for i, l in enumerate(labels_list)}
idx2label = {i: l for l, i in label2idx.items()}
nfr_df['label_idx'] = nfr_df['label'].map(label2idx)

print(f"Dataset: {len(nfr_df)} samples, {len(labels_list)} classes")
print(f"Classes: {labels_list}")
print(f"\nLabel distribution:")
print(nfr_df['label'].value_counts())

X = nfr_df['RequirementText'].tolist()
y = nfr_df['label_idx'].values

# === Dataset ===
tokenizer = BertTokenizer.from_pretrained(MODEL_NAME)

class NFRDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_len):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = max_len
    def __len__(self):
        return len(self.texts)
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        encoding = self.tokenizer(
            text,
            max_length=self.max_len,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(self.labels[idx], dtype=torch.long)
        }

# === Training function ===
def train_fold(X_train, y_train, X_test, y_test, use_weighting=False, use_oversample=False):
    # Optional oversampling for minority classes
    if use_oversample:
        from collections import Counter
        from sklearn.utils import resample
        train_df = pd.DataFrame({'text': X_train, 'label': y_train})
        max_count = train_df['label'].value_counts().max()
        resampled = []
        for label in train_df['label'].unique():
            class_df = train_df[train_df['label'] == label]
            if len(class_df) < max_count:
                class_df = resample(class_df, replace=True, n_samples=max_count, random_state=RANDOM_STATE)
            resampled.append(class_df)
        train_df = pd.concat(resampled).sample(frac=1, random_state=RANDOM_STATE).reset_index(drop=True)
        X_train = train_df['text'].tolist()
        y_train = train_df['label'].values

    train_ds = NFRDataset(X_train, y_train, tokenizer, MAX_LEN)
    test_ds = NFRDataset(X_test, y_test, tokenizer, MAX_LEN)
    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
    test_loader = DataLoader(test_ds, batch_size=BATCH_SIZE, shuffle=False)

    device = torch.device('cpu')
    model = BertForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=len(labels_list))
    model = model.to(device)

    # Class weights
    if use_weighting:
        class_weights = compute_class_weight('balanced', classes=np.unique(y_train), y=y_train)
        class_weights = torch.tensor(class_weights, dtype=torch.float).to(device)
        criterion = nn.CrossEntropyLoss(weight=class_weights)
    else:
        criterion = nn.CrossEntropyLoss()

    optimizer = AdamW(model.parameters(), lr=LR, eps=1e-8)
    total_steps = len(train_loader) * EPOCHS
    scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=0, num_training_steps=total_steps)

    # Train
    model.train()
    for epoch in range(EPOCHS):
        for batch in train_loader:
            optimizer.zero_grad()
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)
            outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
            loss = criterion(outputs.logits, labels)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            scheduler.step()

    # Evaluate
    model.eval()
    all_preds = []
    all_labels = []
    with torch.no_grad():
        for batch in test_loader:
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)
            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            _, preds = torch.max(outputs.logits, dim=1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

    acc = accuracy_score(all_labels, all_preds)
    f1 = f1_score(all_labels, all_preds, average='weighted')
    return acc, f1, all_preds, all_labels

# === 5-fold CV ===
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

baseline_accs = []
baseline_f1s = []
improved_accs = []
improved_f1s = []

print("\n" + "="*60)
print("Running 5-fold CV: Baseline vs Improved")
print("="*60)

for fold, (train_idx, test_idx) in enumerate(skf.split(X, y)):
    print(f"\n--- Fold {fold+1}/5 ---")
    X_train, X_test = [X[i] for i in train_idx], [X[i] for i in test_idx]
    y_train, y_test = y[train_idx], y[test_idx]

    # Baseline (no weighting, no oversample)
    print("  Baseline training...")
    b_acc, b_f1, _, _ = train_fold(X_train, y_train, X_test, y_test, use_weighting=False, use_oversample=False)
    baseline_accs.append(b_acc)
    baseline_f1s.append(b_f1)
    print(f"    Baseline: Acc={b_acc:.4f}, Weighted F1={b_f1:.4f}")

    # Improved (weighting + oversample)
    print("  Improved training...")
    i_acc, i_f1, _, _ = train_fold(X_train, y_train, X_test, y_test, use_weighting=True, use_oversample=True)
    improved_accs.append(i_acc)
    improved_f1s.append(i_f1)
    print(f"    Improved: Acc={i_acc:.4f}, Weighted F1={i_f1:.4f}")

# === Results ===
print("\n" + "="*60)
print("Task 2/3 Results Summary (5-fold CV)")
print("="*60)

print(f"\nBaseline (BERT-base):")
print(f"  Mean Acc: {np.mean(baseline_accs):.4f} (+/-{np.std(baseline_accs):.4f})")
print(f"  Mean Weighted F1: {np.mean(baseline_f1s):.4f} (+/-{np.std(baseline_f1s):.4f})")

print(f"\nImproved (BERT + Weighting + Oversample):")
print(f"  Mean Acc: {np.mean(improved_accs):.4f} (+/-{np.std(improved_accs):.4f})")
print(f"  Mean Weighted F1: {np.mean(improved_f1s):.4f} (+/-{np.std(improved_f1s):.4f})")

# Improvement
delta_f1 = np.mean(improved_f1s) - np.mean(baseline_f1s)
print(f"\nImprovement: {delta_f1*100:+.2f}% Weighted F1")

# === Statistical tests ===
print("\n" + "="*60)
print("Statistical Significance Tests")
print("="*60)

# Paired t-test
t_stat, p_value_t = stats.ttest_rel(improved_f1s, baseline_f1s)
print(f"\nPaired t-test:")
print(f"  t = {t_stat:.4f}, p = {p_value_t:.4f}")
print(f"  Significant (p<0.05): {'Yes' if p_value_t < 0.05 else 'No'}")

# Wilcoxon signed-rank test
w_stat, p_value_w = stats.wilcoxon(improved_f1s, baseline_f1s)
print(f"\nWilcoxon signed-rank test:")
print(f"  W = {w_stat:.4f}, p = {p_value_w:.4f}")
print(f"  Significant (p<0.05): {'Yes' if p_value_w < 0.05 else 'No'}")

# Cohen's d
diff = np.array(improved_f1s) - np.array(baseline_f1s)
cohens_d = np.mean(diff) / np.std(diff)
print(f"\nCohen's d: {cohens_d:.4f}")
print(f"  Effect size: {'small' if abs(cohens_d)<0.2 else 'medium' if abs(cohens_d)<0.5 else 'large'}")

# Save results
results_df = pd.DataFrame({
    'fold': range(1, 6),
    'baseline_acc': baseline_accs,
    'baseline_f1': baseline_f1s,
    'improved_acc': improved_accs,
    'improved_f1': improved_f1s,
})
results_df.to_csv(r"C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\data\task2_improvement_cv_results.csv", index=False)
print("\nResults saved to data/task2_improvement_cv_results.csv")
