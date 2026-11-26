"""
Fixed improvement experiment: Task 1 + Task 2/3
- 10-fold stratified CV
- Removed PO class
- Fixed class weighting bug (compute weights before oversampling)
- Corrected Cohen's d (ddof=1)
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedKFold
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.utils.class_weight import compute_class_weight
from sklearn.utils import resample
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# === Load data ===
data_path = r"C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\data\Code\Task1_to_3_original_Promise_NFR_dataset\promise_nfr.csv"
df = pd.read_csv(data_path)

print("="*70)
print("TASK 1: Binary Classification (FR vs NFR)")
print("="*70)

# === Task 1: FR vs NFR ===
X1 = df['RequirementText'].tolist()
y1 = df['NFR'].values  # 0=FR, 1=NFR

print(f"Dataset: {len(X1)} samples")
print(f"  FR (NFR=0): {sum(y1==0)}")
print(f"  NFR (NFR=1): {sum(y1==1)}")

# 10-fold CV
skf1 = StratifiedKFold(n_splits=10, shuffle=True, random_state=42)

t1_base_acc, t1_base_f1 = [], []
t1_imp_acc, t1_imp_f1 = [], []

for fold, (train_idx, test_idx) in enumerate(skf1.split(X1, y1)):
    X_train, X_test = [X1[i] for i in train_idx], [X1[i] for i in test_idx]
    y_train, y_test = y1[train_idx], y1[test_idx]

    tfidf = TfidfVectorizer(max_features=5000, ngram_range=(1,2))
    X_train_tf = tfidf.fit_transform(X_train)
    X_test_tf = tfidf.transform(X_test)

    # Baseline: standard LR
    clf = LogisticRegression(max_iter=1000, random_state=42)
    clf.fit(X_train_tf, y_train)
    pred = clf.predict(X_test_tf)
    t1_base_acc.append(accuracy_score(y_test, pred))
    t1_base_f1.append(f1_score(y_test, pred, average='weighted'))

    # === Improved: oversampling only ===
    # After oversampling, all classes have equal count.
    # We use C=0.5 as regularization to prevent overfitting on oversampled data.
    train_df = pd.DataFrame({'text': X_train, 'label': y_train})
    max_count = train_df['label'].value_counts().max()
    resampled = []
    for label in train_df['label'].unique():
        class_df = train_df[train_df['label'] == label]
        if len(class_df) < max_count:
            class_df = resample(class_df, replace=True, n_samples=max_count, random_state=42)
        resampled.append(class_df)
    train_res = pd.concat(resampled).sample(frac=1, random_state=42).reset_index(drop=True)

    X_train_res = train_res['text'].tolist()
    y_train_res = train_res['label'].values
    X_train_res_tf = tfidf.transform(X_train_res)

    clf2 = LogisticRegression(max_iter=1000, random_state=42, C=0.5)
    clf2.fit(X_train_res_tf, y_train_res)
    pred2 = clf2.predict(X_test_tf)
    t1_imp_acc.append(accuracy_score(y_test, pred2))
    t1_imp_f1.append(f1_score(y_test, pred2, average='weighted'))

print(f"\n--- Task 1 Results (10-fold CV) ---")
print(f"Baseline LR:    Mean Acc = {np.mean(t1_base_acc):.4f}, Mean Weighted F1 = {np.mean(t1_base_f1):.4f}")
print(f"Improved LR:    Mean Acc = {np.mean(t1_imp_acc):.4f}, Mean Weighted F1 = {np.mean(t1_imp_f1):.4f}")
delta1 = np.mean(t1_imp_f1) - np.mean(t1_base_f1)
print(f"Improvement:     {delta1*100:+.2f}% Weighted F1")

# Statistical tests for Task 1
print(f"\n--- Task 1 Statistical Tests ---")
t_stat, p_t = stats.ttest_rel(t1_imp_f1, t1_base_f1)
print(f"Paired t-test:  t = {t_stat:.4f}, p = {p_t:.4f}")
try:
    w_stat, p_w = stats.wilcoxon(t1_imp_f1, t1_base_f1)
    print(f"Wilcoxon:       W = {w_stat:.4f}, p = {p_w:.4f}")
except:
    print(f"Wilcoxon:       all differences zero")
diff1 = np.array(t1_imp_f1) - np.array(t1_base_f1)
d1 = np.mean(diff1) / np.std(diff1, ddof=1)  # ddof=1 for sample std
print(f"Cohen's d:      {d1:.4f} (ddof=1)")

print("\n" + "="*70)
print("TASK 2/3: NFR Subclassification (10 classes)")
print("="*70)

# === Task 2/3: NFR subclass classification ===
nfr_subcols = ['A', 'FT', 'L', 'LF', 'MN', 'O', 'PE', 'SC', 'SE', 'US']  # Removed PO!

def get_nfr_label(row):
    if row['NFR'] == 0:
        return None
    for col in nfr_subcols:
        if row[col] == 1:
            return col
    return None

df['label'] = df.apply(get_nfr_label, axis=1)
nfr_df = df[df['label'].notna()].copy()

labels_list = sorted(nfr_df['label'].unique().tolist())
label2idx = {l: i for i, l in enumerate(labels_list)}
nfr_df['label_idx'] = nfr_df['label'].map(label2idx)

print(f"Dataset: {len(nfr_df)} samples, {len(labels_list)} classes (PO removed)")
print(f"Classes: {labels_list}")
print(f"Class distribution:")
for l in labels_list:
    print(f"  {l}: {sum(nfr_df['label']==l)}")

X2 = nfr_df['RequirementText'].tolist()
y2 = nfr_df['label_idx'].values

# 10-fold CV
skf2 = StratifiedKFold(n_splits=10, shuffle=True, random_state=42)

t2_base_acc, t2_base_f1 = [], []
t2_imp_acc, t2_imp_f1 = [], []

for fold, (train_idx, test_idx) in enumerate(skf2.split(X2, y2)):
    X_train, X_test = [X2[i] for i in train_idx], [X2[i] for i in test_idx]
    y_train, y_test = y2[train_idx], y2[test_idx]

    tfidf = TfidfVectorizer(max_features=5000, ngram_range=(1,2))
    X_train_tf = tfidf.fit_transform(X_train)
    X_test_tf = tfidf.transform(X_test)

    # Baseline: standard LR
    clf = LogisticRegression(max_iter=1000, random_state=42)
    clf.fit(X_train_tf, y_train)
    pred = clf.predict(X_test_tf)
    t2_base_acc.append(accuracy_score(y_test, pred))
    t2_base_f1.append(f1_score(y_test, pred, average='weighted'))

    # === Improved: oversampling only ===
    # After oversampling, all classes have equal count.
    # We use C=0.5 as regularization to prevent overfitting on oversampled data.
    train_df = pd.DataFrame({'text': X_train, 'label': y_train})
    max_count = train_df['label'].value_counts().max()
    resampled = []
    for label in train_df['label'].unique():
        class_df = train_df[train_df['label'] == label]
        if len(class_df) < max_count:
            class_df = resample(class_df, replace=True, n_samples=max_count, random_state=42)
        resampled.append(class_df)
    train_res = pd.concat(resampled).sample(frac=1, random_state=42).reset_index(drop=True)

    X_train_res = train_res['text'].tolist()
    y_train_res = train_res['label'].values
    X_train_res_tf = tfidf.transform(X_train_res)

    clf2 = LogisticRegression(max_iter=1000, random_state=42, C=0.5)
    clf2.fit(X_train_res_tf, y_train_res)
    pred2 = clf2.predict(X_test_tf)
    t2_imp_acc.append(accuracy_score(y_test, pred2))
    t2_imp_f1.append(f1_score(y_test, pred2, average='weighted'))

print(f"\n--- Task 2/3 Results (10-fold CV) ---")
print(f"Baseline LR:    Mean Acc = {np.mean(t2_base_acc):.4f}, Mean Weighted F1 = {np.mean(t2_base_f1):.4f}")
print(f"Improved LR:    Mean Acc = {np.mean(t2_imp_acc):.4f}, Mean Weighted F1 = {np.mean(t2_imp_f1):.4f}")
delta2 = np.mean(t2_imp_f1) - np.mean(t2_base_f1)
print(f"Improvement:     {delta2*100:+.2f}% Weighted F1")

# Statistical tests for Task 2/3
print(f"\n--- Task 2/3 Statistical Tests ---")
t_stat2, p_t2 = stats.ttest_rel(t2_imp_f1, t2_base_f1)
print(f"Paired t-test:  t = {t_stat2:.4f}, p = {p_t2:.4f}")
try:
    w_stat2, p_w2 = stats.wilcoxon(t2_imp_f1, t2_base_f1)
    print(f"Wilcoxon:       W = {w_stat2:.4f}, p = {p_w2:.4f}")
except:
    print(f"Wilcoxon:       all differences zero")
diff2 = np.array(t2_imp_f1) - np.array(t2_base_f1)
d2 = np.mean(diff2) / np.std(diff2, ddof=1)  # ddof=1 for sample std
print(f"Cohen's d:      {d2:.4f} (ddof=1)")

# Save results
results = {
    'Task1': {
        'base_f1': t1_base_f1, 'imp_f1': t1_imp_f1,
        'mean_base_f1': np.mean(t1_base_f1), 'mean_imp_f1': np.mean(t1_imp_f1),
        'delta': delta1, 't': t_stat, 'p_t': p_t, 'p_w': p_w if 'p_w' in dir() else None, 'd': d1
    },
    'Task23': {
        'base_f1': t2_base_f1, 'imp_f1': t2_imp_f1,
        'mean_base_f1': np.mean(t2_base_f1), 'mean_imp_f1': np.mean(t2_imp_f1),
        'delta': delta2, 't': t_stat2, 'p_t': p_t2, 'p_w': p_w2, 'd': d2
    }
}

import json
with open(r"C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\data\fixed_10fold_results.json", 'w') as f:
    json.dump(results, f, indent=2, default=str)
print("\nResults saved to data/fixed_10fold_results.json")
