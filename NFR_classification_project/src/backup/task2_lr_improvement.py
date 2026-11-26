"""
Task 2/3 improvement experiment with LR + TF-IDF (fast on CPU).
- Baseline: LR (standard)
- Improved: LR + class weighting + oversampling
- 5-fold stratified CV
- Paired t-test + Wilcoxon test + Cohen's d
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

nfr_subcols = ['A', 'FT', 'L', 'LF', 'MN', 'O', 'PE', 'PO', 'SC', 'SE', 'US']

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

print(f"Dataset: {len(nfr_df)} samples, {len(labels_list)} classes")
print(f"Classes: {labels_list}")

X = nfr_df['RequirementText'].tolist()
y = nfr_df['label_idx'].values

# === 10-fold CV (better statistical power) ===
skf = StratifiedKFold(n_splits=10, shuffle=True, random_state=42)

baseline_accs = []
baseline_f1s = []
improved_accs = []
improved_f1s = []

print("\n" + "="*60)
print("Running 10-fold CV: Baseline LR vs Improved LR")
print("="*60)

for fold, (train_idx, test_idx) in enumerate(skf.split(X, y)):
    print(f"\n--- Fold {fold+1}/10 ---")
    X_train, X_test = [X[i] for i in train_idx], [X[i] for i in test_idx]
    y_train, y_test = y[train_idx], y[test_idx]

    # TF-IDF
    tfidf = TfidfVectorizer(max_features=5000, ngram_range=(1,2))
    X_train_tfidf = tfidf.fit_transform(X_train)
    X_test_tfidf = tfidf.transform(X_test)

    # === Baseline: standard LR ===
    clf_base = LogisticRegression(max_iter=1000, random_state=42)
    clf_base.fit(X_train_tfidf, y_train)
    preds_base = clf_base.predict(X_test_tfidf)
    b_acc = accuracy_score(y_test, preds_base)
    b_f1 = f1_score(y_test, preds_base, average='weighted')
    baseline_accs.append(b_acc)
    baseline_f1s.append(b_f1)
    print(f"  Baseline LR: Acc={b_acc:.4f}, Weighted F1={b_f1:.4f}")

    # === Improved: LR + class weighting + oversampling ===
    # Oversample minority classes
    train_df = pd.DataFrame({'text': X_train, 'label': y_train})
    max_count = train_df['label'].value_counts().max()
    resampled = []
    for label in train_df['label'].unique():
        class_df = train_df[train_df['label'] == label]
        if len(class_df) < max_count:
            class_df = resample(class_df, replace=True, n_samples=max_count, random_state=42)
        resampled.append(class_df)
    train_resampled = pd.concat(resampled).sample(frac=1, random_state=42).reset_index(drop=True)

    X_train_res = train_resampled['text'].tolist()
    y_train_res = train_resampled['label'].values

    X_train_res_tfidf = tfidf.transform(X_train_res)

    # Class-weighted LR (only for classes present in training data)
    present_classes = np.unique(y_train_res)
    class_weights = compute_class_weight('balanced', classes=present_classes, y=y_train_res)
    cw_dict = {int(c): w for c, w in zip(present_classes, class_weights)}

    clf_imp = LogisticRegression(max_iter=1000, random_state=42, class_weight=cw_dict, C=0.5)
    clf_imp.fit(X_train_res_tfidf, y_train_res)
    preds_imp = clf_imp.predict(X_test_tfidf)
    i_acc = accuracy_score(y_test, preds_imp)
    i_f1 = f1_score(y_test, preds_imp, average='weighted')
    improved_accs.append(i_acc)
    improved_f1s.append(i_f1)
    print(f"  Improved LR: Acc={i_acc:.4f}, Weighted F1={i_f1:.4f}")

# === Results ===
print("\n" + "="*60)
print("Task 2/3 Results Summary (10-fold CV)")
print("="*60)

print(f"\nBaseline (LR + TF-IDF):")
print(f"  Mean Acc: {np.mean(baseline_accs):.4f} (+/-{np.std(baseline_accs):.4f})")
print(f"  Mean Weighted F1: {np.mean(baseline_f1s):.4f} (+/-{np.std(baseline_f1s):.4f})")

print(f"\nImproved (LR + Weighting + Oversampling):")
print(f"  Mean Acc: {np.mean(improved_accs):.4f} (+/-{np.std(improved_accs):.4f})")
print(f"  Mean Weighted F1: {np.mean(improved_f1s):.4f} (+/-{np.std(improved_f1s):.4f})")

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
try:
    w_stat, p_value_w = stats.wilcoxon(improved_f1s, baseline_f1s)
    print(f"\nWilcoxon signed-rank test:")
    print(f"  W = {w_stat:.4f}, p = {p_value_w:.4f}")
    print(f"  Significant (p<0.05): {'Yes' if p_value_w < 0.05 else 'No'}")
except:
    print("\nWilcoxon test: skipped (all differences are zero)")

# Cohen's d
diff = np.array(improved_f1s) - np.array(baseline_f1s)
cohens_d = np.mean(diff) / np.std(diff)
print(f"\nCohen's d: {cohens_d:.4f}")
print(f"  Effect size: {'small' if abs(cohens_d)<0.2 else 'medium' if abs(cohens_d)<0.5 else 'large'}")

# Save results
results_df = pd.DataFrame({
    'fold': range(1, 11),
    'baseline_acc': baseline_accs,
    'baseline_f1': baseline_f1s,
    'improved_acc': improved_accs,
    'improved_f1': improved_f1s,
})
results_df.to_csv(r"C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\data\task2_lr_improvement_cv.csv", index=False)
print("\nResults saved to data/task2_lr_improvement_cv.csv")
