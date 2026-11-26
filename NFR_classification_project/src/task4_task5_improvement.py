"""
Task 4 & Task 5 Improvement Experiment (10-Fold CV + Statistical Significance Tests)
- Fixes Task 4 data filtering (NotR == 0 -> 612 valid requirements, matching Table II of paper)
- Addresses the paper's Section IX-A & Section XI Future Work gap:
  Multi-Label Classifier Chains + Cost-Sensitive Regularized Balancing
"""

import json
import os
import warnings
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import KFold, StratifiedKFold

warnings.filterwarnings("ignore")

data_dir = r"C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\data\Code"

# ==============================================================================
# TASK 4: Functional & Quality Aspects (612 valid samples, Logical Classifier Chain)
# ==============================================================================
print("=" * 70)
print(
    "TASK 4: Relabeled PROMISE Dataset (612 valid samples, Logical Classifier"
    " Chain)"
)
print("=" * 70)

df4 = pd.read_csv(
    os.path.join(
        data_dir, "Task4_relabeled_Promise_NFR_dataset", "promise-reclass.csv"
    )
)
df4 = df4[df4["NotR"] == 0].reset_index(
    drop=True
)  # Match paper Table II (612 samples)
texts4 = df4["RequirementText"].tolist()
cols4 = ["IsFunctional", "IsQuality", "IsOnlyFunctional", "IsOnlyQuality"]
y4 = {col: df4[col].astype(int).values for col in cols4}

print(f"Samples: {len(texts4)}")
for col in cols4:
    print(f"  {col}: {y4[col].sum()} positive")

kf4 = KFold(n_splits=10, shuffle=True, random_state=42)
base4_wf1, imp4_wf1 = {c: [] for c in cols4}, {c: [] for c in cols4}
base4_bf1, imp4_bf1 = {c: [] for c in cols4}, {c: [] for c in cols4}

for fold, (tr_idx, te_idx) in enumerate(kf4.split(texts4)):
  X_tr_raw = [texts4[i] for i in tr_idx]
  X_te_raw = [texts4[i] for i in te_idx]
  tfidf = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
  X_tr = tfidf.fit_transform(X_tr_raw).toarray()
  X_te = tfidf.transform(X_te_raw).toarray()

  # 1. Baseline: Independent standard LR (Binary Relevance)
  for col in cols4:
    clf_b = LogisticRegression(max_iter=1000, random_state=42, C=1.0)
    clf_b.fit(X_tr, y4[col][tr_idx])
    pred_b = clf_b.predict(X_te)
    base4_wf1[col].append(f1_score(y4[col][te_idx], pred_b, average="weighted"))
    base4_bf1[col].append(f1_score(y4[col][te_idx], pred_b, average="binary"))

  # 2. Improved: Cost-Sensitive LR + Logical Classifier Chain (F, Q -> OnlyF, OnlyQ)
  probs_tr, probs_te = {}, {}
  for col in ["IsFunctional", "IsQuality"]:
    clf_i = LogisticRegression(
        max_iter=1000, random_state=42, class_weight="balanced", C=2.0
    )
    clf_i.fit(X_tr, y4[col][tr_idx])
    probs_tr[col] = clf_i.predict_proba(X_tr)[:, 1]
    probs_te[col] = clf_i.predict_proba(X_te)[:, 1]
    pred_i = (probs_te[col] >= 0.5).astype(int)
    imp4_wf1[col].append(f1_score(y4[col][te_idx], pred_i, average="weighted"))
    imp4_bf1[col].append(f1_score(y4[col][te_idx], pred_i, average="binary"))

  # Construct logical interaction features: P(F), P(Q), P(F)*(1-P(Q)), P(Q)*(1-P(F))
  meta_tr = (
      np.column_stack([
          probs_tr["IsFunctional"],
          probs_tr["IsQuality"],
          probs_tr["IsFunctional"] * (1 - probs_tr["IsQuality"]),
          probs_tr["IsQuality"] * (1 - probs_tr["IsFunctional"]),
      ])
      * 0.5
  )
  meta_te = (
      np.column_stack([
          probs_te["IsFunctional"],
          probs_te["IsQuality"],
          probs_te["IsFunctional"] * (1 - probs_te["IsQuality"]),
          probs_te["IsQuality"] * (1 - probs_te["IsFunctional"]),
      ])
      * 0.5
  )
  X_tr_chain = np.hstack([X_tr, meta_tr])
  X_te_chain = np.hstack([X_te, meta_te])

  for col in ["IsOnlyFunctional", "IsOnlyQuality"]:
    clf_i = LogisticRegression(
        max_iter=1000, random_state=42, class_weight="balanced", C=2.0
    )
    clf_i.fit(X_tr_chain, y4[col][tr_idx])
    pred_i = clf_i.predict(X_te_chain)
    imp4_wf1[col].append(f1_score(y4[col][te_idx], pred_i, average="weighted"))
    imp4_bf1[col].append(f1_score(y4[col][te_idx], pred_i, average="binary"))

print("\n--- Task 4 Results ---")
task4_results = {}
for col in cols4:
  b_mean, i_mean = np.mean(base4_wf1[col]), np.mean(imp4_wf1[col])
  b_pos, i_pos = np.mean(base4_bf1[col]), np.mean(imp4_bf1[col])
  diff = np.array(imp4_wf1[col]) - np.array(base4_wf1[col])
  t_s, p_t = stats.ttest_rel(imp4_wf1[col], base4_wf1[col])
  try:
    _, p_w = stats.wilcoxon(imp4_wf1[col], base4_wf1[col])
  except:
    p_w = 1.0
  d = np.mean(diff) / np.std(diff, ddof=1)
  task4_results[col] = {
      'base_wf1': float(b_mean),
      'imp_wf1': float(i_mean),
      'base_pos_f1': float(b_pos),
      'imp_pos_f1': float(i_pos),
      'delta': float(i_mean - b_mean),
      't': float(t_s),
      'p_t': float(p_t),
      'p_w': float(p_w),
      'd': float(d)
  }
  print(
      f"{col:18s} | Base WF1={b_mean*100:.2f}% -> Imp WF1={i_mean*100:.2f}%"
      f" ({(i_mean-b_mean)*100:+.2f}%) | Pos F1: {b_pos*100:.2f}%->{i_pos*100:.2f}% | t={t_s:.2f}, p={p_t:.4f}, wilcox_p={p_w:.4f}, d={d:.2f}"
  )

# ==============================================================================
# TASK 5: Functional Concerns (309 samples, Multi-Label Classifier Chain + Balancing)
# ==============================================================================
print("\n" + "=" * 70)
print(
    "TASK 5: Functional Concerns (309 samples, Classifier Chain + Cost"
    " Balancing)"
)
print("=" * 70)

func_path = os.path.join(
    data_dir, "Task5_func_concerns_dataset", "func_concerns.csv"
)
df5 = pd.read_csv(func_path, sep=None, engine="python")
texts5 = df5["RequirementText"].tolist()
cols5 = ["Function", "Data", "Behavior"]
y5 = {col: df5[col].astype(int).values for col in cols5}

print(f"Samples: {len(texts5)}")
for col in cols5:
    print(f"  {col}: {y5[col].sum()} positive")

kf5 = KFold(n_splits=10, shuffle=True, random_state=42)
base5_wf1, imp5_wf1 = {c: [] for c in cols5}, {c: [] for c in cols5}
base5_bf1, imp5_bf1 = {c: [] for c in cols5}, {c: [] for c in cols5}

for fold, (tr_idx, te_idx) in enumerate(kf5.split(texts5)):
  X_tr_raw = [texts5[i] for i in tr_idx]
  X_te_raw = [texts5[i] for i in te_idx]
  tfidf = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
  X_tr = tfidf.fit_transform(X_tr_raw).toarray()
  X_te = tfidf.transform(X_te_raw).toarray()

  # 1. Baseline: Independent standard LR
  for col in cols5:
    clf_b = LogisticRegression(max_iter=1000, random_state=42, C=1.0)
    clf_b.fit(X_tr, y5[col][tr_idx])
    pred_b = clf_b.predict(X_te)
    base5_wf1[col].append(f1_score(y5[col][te_idx], pred_b, average="weighted"))
    base5_bf1[col].append(
        f1_score(y5[col][te_idx], pred_b, average="binary", zero_division=0)
    )

  # 2. Improved: Classifier Chain (Function -> Behavior -> Data) + Cost-Sensitive Balancing
  # Step A: Function
  clf_f = LogisticRegression(
      max_iter=1000, random_state=42, class_weight="balanced", C=2.0
  )
  clf_f.fit(X_tr, y5["Function"][tr_idx])
  pf_tr = clf_f.predict_proba(X_tr)[:, 1]
  pf_te = clf_f.predict_proba(X_te)[:, 1]
  pred_f = (pf_te >= 0.5).astype(int)
  imp5_wf1["Function"].append(
      f1_score(y5["Function"][te_idx], pred_f, average="weighted")
  )
  imp5_bf1["Function"].append(
      f1_score(y5["Function"][te_idx], pred_f, average="binary")
  )

  # Step B: Behavior (chained with Function, leveraging r = -0.639 negative correlation)
  X_tr_b = np.hstack([X_tr, pf_tr[:, None] * 0.5])
  X_te_b = np.hstack([X_te, pf_te[:, None] * 0.5])
  clf_b2 = LogisticRegression(
      max_iter=1000, random_state=42, class_weight="balanced", C=2.0
  )
  clf_b2.fit(X_tr_b, y5["Behavior"][tr_idx])
  pb_tr = clf_b2.predict_proba(X_tr_b)[:, 1]
  pb_te = clf_b2.predict_proba(X_te_b)[:, 1]
  pred_b2 = (pb_te >= 0.5).astype(int)
  imp5_wf1["Behavior"].append(
      f1_score(y5["Behavior"][te_idx], pred_b2, average="weighted")
  )
  imp5_bf1["Behavior"].append(
      f1_score(y5["Behavior"][te_idx], pred_b2, average="binary")
  )

  # Step C: Data (rare class, 18.4% positive, chained with Function & Behavior)
  X_tr_d = np.hstack([X_tr, pf_tr[:, None] * 0.3, pb_tr[:, None] * 0.3])
  X_te_d = np.hstack([X_te, pf_te[:, None] * 0.3, pb_te[:, None] * 0.3])
  clf_d = LogisticRegression(
      max_iter=1000, random_state=42, class_weight="balanced", C=2.0
  )
  clf_d.fit(X_tr_d, y5["Data"][tr_idx])
  pred_d = clf_d.predict(X_te_d)
  imp5_wf1["Data"].append(
      f1_score(y5["Data"][te_idx], pred_d, average="weighted")
  )
  imp5_bf1["Data"].append(
      f1_score(y5["Data"][te_idx], pred_d, average="binary")
  )

print("\n--- Task 5 Results ---")
task5_results = {}
for col in cols5:
  b_mean, i_mean = np.mean(base5_wf1[col]), np.mean(imp5_wf1[col])
  b_pos, i_pos = np.mean(base5_bf1[col]), np.mean(imp5_bf1[col])
  diff = np.array(imp5_wf1[col]) - np.array(base5_wf1[col])
  t_s, p_t = stats.ttest_rel(imp5_wf1[col], base5_wf1[col])
  try:
    _, p_w = stats.wilcoxon(imp5_wf1[col], base5_wf1[col])
  except:
    p_w = 1.0
  d = np.mean(diff) / np.std(diff, ddof=1)
  task5_results[col] = {
      'base_wf1': float(b_mean),
      'imp_wf1': float(i_mean),
      'base_pos_f1': float(b_pos),
      'imp_pos_f1': float(i_pos),
      'delta': float(i_mean - b_mean),
      't': float(t_s),
      'p_t': float(p_t),
      'p_w': float(p_w),
      'd': float(d)
  }
  print(
      f"{col:10s} | Pos F1: {b_pos*100:.2f}%->{i_pos*100:.2f}% | WF1:"
      f" {b_mean*100:.2f}%->{i_mean*100:.2f}% ({(i_mean-b_mean)*100:+.2f}%) |"
      f" t={t_s:.2f}, p={p_t:.4f}, wilcox_p={p_w:.4f}, d={d:.2f}"
  )

# Save results
all_results = {
    'Task4': task4_results,
    'Task5': task5_results
}
output_path = r"C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\data\task4_task5_improvement_results.json"
with open(output_path, 'w') as f:
    json.dump(all_results, f, indent=2)
print(f"\nResults saved to {output_path}")
