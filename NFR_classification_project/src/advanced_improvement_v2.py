"""
V2: Better strategy - Feature engineering is the main improvement.
Task 1: just use better features (word + char n-gram), no weighting/oversampling
Task 2/3: better features + oversampling
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedKFold
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.pipeline import FeatureUnion
from sklearn.utils import resample
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

data_path = r"C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\data\Code\Task1_to_3_original_Promise_NFR_dataset\promise_nfr.csv"
df = pd.read_csv(data_path)

print("="*70)
print("TASK 1: FR vs NFR Binary Classification")
print("="*70)

X1 = df['RequirementText'].tolist()
y1 = df['NFR'].values

skf1 = StratifiedKFold(n_splits=10, shuffle=True, random_state=42)

# Compare 3 settings:
# 1. Baseline: word n-gram (1,2) only
# 2. Feature fusion: word (1,2) + char (3,5) n-gram
# 3. Feature fusion + oversampling + smooth weighting

base_acc, base_f1 = [], []
feat_acc, feat_f1 = [], []
imp_acc, imp_f1 = [], []

for fold, (train_idx, test_idx) in enumerate(skf1.split(X1, y1)):
    X_train, X_test = [X1[i] for i in train_idx], [X1[i] for i in test_idx]
    y_train, y_test = y1[train_idx], y1[test_idx]

    # === 1. Baseline: word n-gram only ===
    vec_base = TfidfVectorizer(max_features=5000, ngram_range=(1,2), sublinear_tf=True)
    X_train_b = vec_base.fit_transform(X_train)
    X_test_b = vec_base.transform(X_test)
    clf = LogisticRegression(max_iter=1000, random_state=42)
    clf.fit(X_train_b, y_train)
    pred = clf.predict(X_test_b)
    base_acc.append(accuracy_score(y_test, pred))
    base_f1.append(f1_score(y_test, pred, average='weighted'))

    # === 2. Feature fusion: word + char n-gram ===
    word_vec = TfidfVectorizer(max_features=3000, ngram_range=(1,2), sublinear_tf=True)
    char_vec = TfidfVectorizer(max_features=2000, ngram_range=(3,5), analyzer='char_wb', sublinear_tf=True)
    union = FeatureUnion([('word', word_vec), ('char', char_vec)])
    X_train_f = union.fit_transform(X_train)
    X_test_f = union.transform(X_test)
    clf2 = LogisticRegression(max_iter=1000, random_state=42)
    clf2.fit(X_train_f, y_train)
    pred2 = clf2.predict(X_test_f)
    feat_acc.append(accuracy_score(y_test, pred2))
    feat_f1.append(f1_score(y_test, pred2, average='weighted'))

    # === 3. Feature fusion + oversampling + smooth weighting ===
    class_counts = np.bincount(y_train)
    max_count = class_counts.max()
    alpha = 0.5
    smooth_weights = (max_count / class_counts) ** alpha
    cw_dict = {i: smooth_weights[i] for i in range(len(class_counts))}

    train_df = pd.DataFrame({'text': X_train, 'label': y_train})
    max_count_train = train_df['label'].value_counts().max()
    resampled = []
    for label in train_df['label'].unique():
        class_df = train_df[train_df['label'] == label]
        if len(class_df) < max_count_train:
            class_df = resample(class_df, replace=True, n_samples=max_count_train, random_state=42)
        resampled.append(class_df)
    train_res = pd.concat(resampled).sample(frac=1, random_state=42).reset_index(drop=True)
    X_train_res = train_res['text'].tolist()
    y_train_res = train_res['label'].values
    X_train_res_f = union.transform(X_train_res)
    clf3 = LogisticRegression(max_iter=1000, random_state=42, class_weight=cw_dict, C=0.5)
    clf3.fit(X_train_res_f, y_train_res)
    pred3 = clf3.predict(X_test_f)
    imp_acc.append(accuracy_score(y_test, pred3))
    imp_f1.append(f1_score(y_test, pred3, average='weighted'))

print(f"\n--- Task 1 Results (10-fold CV) ---")
print(f"1. Baseline (word n-gram only):")
print(f"   Mean Acc = {np.mean(base_acc):.4f}, Mean F1 = {np.mean(base_f1):.4f}")
print(f"2. Feature fusion (word + char n-gram):")
print(f"   Mean Acc = {np.mean(feat_acc):.4f}, Mean F1 = {np.mean(feat_f1):.4f}")
print(f"   Improvement vs baseline: {(np.mean(feat_f1)-np.mean(base_f1))*100:+.2f}%")
print(f"3. Feature fusion + oversampling + smooth weighting:")
print(f"   Mean Acc = {np.mean(imp_acc):.4f}, Mean F1 = {np.mean(imp_f1):.4f}")
print(f"   Improvement vs baseline: {(np.mean(imp_f1)-np.mean(base_f1))*100:+.2f}%")

# Statistical test: baseline vs feature fusion
print(f"\n--- Task 1: Baseline vs Feature Fusion ---")
t_stat, p_t = stats.ttest_rel(feat_f1, base_f1)
print(f"Paired t-test: t = {t_stat:.4f}, p = {p_t:.4f}")
try:
    w_stat, p_w = stats.wilcoxon(feat_f1, base_f1)
    print(f"Wilcoxon: p = {p_w:.4f}")
except:
    print(f"Wilcoxon: all differences zero")
diff = np.array(feat_f1) - np.array(base_f1)
d = np.mean(diff) / np.std(diff, ddof=1)
print(f"Cohen's d: {d:.4f}")

print("\n" + "="*70)
print("TASK 2/3: NFR Subclassification (10 classes)")
print("="*70)

nfr_subcols = ['A', 'FT', 'L', 'LF', 'MN', 'O', 'PE', 'SC', 'SE', 'US']
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

X2 = nfr_df['RequirementText'].tolist()
y2 = nfr_df['label_idx'].values

skf2 = StratifiedKFold(n_splits=10, shuffle=True, random_state=42)

base2_acc, base2_f1 = [], []
feat2_acc, feat2_f1 = [], []
imp2_acc, imp2_f1 = [], []

for fold, (train_idx, test_idx) in enumerate(skf2.split(X2, y2)):
    X_train, X_test = [X2[i] for i in train_idx], [X2[i] for i in test_idx]
    y_train, y_test = y2[train_idx], y2[test_idx]

    # === 1. Baseline: word n-gram only ===
    vec_base = TfidfVectorizer(max_features=5000, ngram_range=(1,2), sublinear_tf=True)
    X_train_b = vec_base.fit_transform(X_train)
    X_test_b = vec_base.transform(X_test)
    clf = LogisticRegression(max_iter=1000, random_state=42)
    clf.fit(X_train_b, y_train)
    pred = clf.predict(X_test_b)
    base2_acc.append(accuracy_score(y_test, pred))
    base2_f1.append(f1_score(y_test, pred, average='weighted'))

    # === 2. Feature fusion: word + char n-gram ===
    word_vec = TfidfVectorizer(max_features=3000, ngram_range=(1,2), sublinear_tf=True)
    char_vec = TfidfVectorizer(max_features=2000, ngram_range=(3,5), analyzer='char_wb', sublinear_tf=True)
    union = FeatureUnion([('word', word_vec), ('char', char_vec)])
    X_train_f = union.fit_transform(X_train)
    X_test_f = union.transform(X_test)
    clf2 = LogisticRegression(max_iter=1000, random_state=42)
    clf2.fit(X_train_f, y_train)
    pred2 = clf2.predict(X_test_f)
    feat2_acc.append(accuracy_score(y_test, pred2))
    feat2_f1.append(f1_score(y_test, pred2, average='weighted'))

    # === 3. Feature fusion + oversampling ===
    train_df = pd.DataFrame({'text': X_train, 'label': y_train})
    max_count_train = train_df['label'].value_counts().max()
    resampled = []
    for label in train_df['label'].unique():
        class_df = train_df[train_df['label'] == label]
        if len(class_df) < max_count_train:
            class_df = resample(class_df, replace=True, n_samples=max_count_train, random_state=42)
        resampled.append(class_df)
    train_res = pd.concat(resampled).sample(frac=1, random_state=42).reset_index(drop=True)
    X_train_res = train_res['text'].tolist()
    y_train_res = train_res['label'].values
    X_train_res_f = union.transform(X_train_res)
    clf3 = LogisticRegression(max_iter=1000, random_state=42, C=0.5)
    clf3.fit(X_train_res_f, y_train_res)
    pred3 = clf3.predict(X_test_f)
    imp2_acc.append(accuracy_score(y_test, pred3))
    imp2_f1.append(f1_score(y_test, pred3, average='weighted'))

print(f"\n--- Task 2/3 Results (10-fold CV) ---")
print(f"1. Baseline (word n-gram only):")
print(f"   Mean Acc = {np.mean(base2_acc):.4f}, Mean F1 = {np.mean(base2_f1):.4f}")
print(f"2. Feature fusion (word + char n-gram):")
print(f"   Mean Acc = {np.mean(feat2_acc):.4f}, Mean F1 = {np.mean(feat2_f1):.4f}")
print(f"   Improvement vs baseline: {(np.mean(feat2_f1)-np.mean(base2_f1))*100:+.2f}%")
print(f"3. Feature fusion + oversampling:")
print(f"   Mean Acc = {np.mean(imp2_acc):.4f}, Mean F1 = {np.mean(imp2_f1):.4f}")
print(f"   Improvement vs baseline: {(np.mean(imp2_f1)-np.mean(base2_f1))*100:+.2f}%")

# Statistical test: baseline vs improved (feature fusion + oversampling)
print(f"\n--- Task 2/3: Baseline vs Improved ---")
t_stat2, p_t2 = stats.ttest_rel(imp2_f1, base2_f1)
print(f"Paired t-test: t = {t_stat2:.4f}, p = {p_t2:.4f}")
try:
    w_stat2, p_w2 = stats.wilcoxon(imp2_f1, base2_f1)
    print(f"Wilcoxon: p = {p_w2:.4f}")
except:
    print(f"Wilcoxon: all differences zero")
diff2 = np.array(imp2_f1) - np.array(base2_f1)
d2 = np.mean(diff2) / np.std(diff2, ddof=1)
print(f"Cohen's d: {d2:.4f}")

# === Save reproducible results to JSON ===
import json
def summarize(base_f1, imp_f1, base_acc, imp_acc, t_stat, p_t, p_w, d):
    return {
        "fold_base_f1": [float(x) for x in base_f1],
        "fold_imp_f1": [float(x) for x in imp_f1],
        "mean_base_acc": float(np.mean(base_acc)),
        "mean_imp_acc": float(np.mean(imp_acc)),
        "mean_base_f1": float(np.mean(base_f1)),
        "mean_imp_f1": float(np.mean(imp_f1)),
        "delta": float(np.mean(imp_f1) - np.mean(base_f1)),
        "t": float(t_stat),
        "p_t": float(p_t),
        "p_w": float(p_w),
        "d": float(d),
    }

# Task 1: baseline vs feature fusion (the recommended Task 1 setting)
t1 = summarize(base_f1, feat_f1, base_acc, feat_acc, t_stat, p_t, p_w, d)
# Task 2/3: baseline vs feature fusion + oversampling
t23 = summarize(base2_f1, imp2_f1, base2_acc, imp2_acc, t_stat2, p_t2, p_w2, d2)
t23["feature_fusion_only_f1"] = float(np.mean(feat2_f1))

results = {
    "description": "Three-layer improvement (word+char N-gram fusion, fold-wise oversampling + L2 C=0.5, 10-fold Stratified CV, random_state=42)",
    "Task1_base_vs_feature_fusion": t1,
    "Task1_full_improvement_f1": float(np.mean(imp_f1)),
    "Task23_base_vs_featFusion_oversampling": t23,
}
out_json = r"C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\data\advanced_improvement_v2_results.json"
with open(out_json, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nSaved reproducible results to {out_json}")
