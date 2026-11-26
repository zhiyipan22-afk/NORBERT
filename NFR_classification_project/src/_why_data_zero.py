import os, warnings
import numpy as np, pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import KFold
from sklearn.metrics import f1_score, confusion_matrix, precision_score, recall_score
warnings.filterwarnings("ignore")

data_dir = r"C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\data\Code"
df = pd.read_csv(os.path.join(data_dir, "Task5_func_concerns_dataset", "func_concerns.csv"),
                 sep=None, engine="python")
texts = df["RequirementText"].tolist()
y = df["Data"].astype(int).values
print("total =", len(y), " positives(Data=1) =", y.sum(), " negatives =", (y==0).sum(),
      " pos% =", round(100*y.mean(),1))

kf = KFold(n_splits=10, shuffle=True, random_state=42)
all_true, all_pred = [], []
for fold,(tr,te) in enumerate(kf.split(texts)):
    tf = TfidfVectorizer(max_features=5000, ngram_range=(1,2))
    Xtr = tf.fit_transform([texts[i] for i in tr]).toarray()
    Xte = tf.transform([texts[i] for i in te]).toarray()
    clf = LogisticRegression(max_iter=1000, random_state=42, C=1.0)  # baseline: no class_weight
    clf.fit(Xtr, y[tr])
    pred = clf.predict(Xte)
    all_true.extend(y[te]); all_pred.extend(pred)
    n_pred_pos = pred.sum()
    print(f"fold {fold+1}: test n={len(te)}, true pos={y[te].sum()}, predicted pos={n_pred_pos}")

all_true=np.array(all_true); all_pred=np.array(all_pred)
tn,fp,fn,tp = confusion_matrix(all_true, all_pred, labels=[0,1]).ravel()
print("\n==== Pooled 10-fold OOF baseline (Data) ====")
print(f"TP={tp}  FP={fp}  FN={fn}  TN={tn}")
print(f"total predicted as Data=1 (positive): {all_pred.sum()}")
print(f"per-class precision = {precision_score(all_true,all_pred,zero_division=0):.4f}")
print(f"per-class recall    = {recall_score(all_true,all_pred,zero_division=0):.4f}")
print(f"per-class F1        = {f1_score(all_true,all_pred,zero_division=0):.4f}")
print(f"weighted F1         = {f1_score(all_true,all_pred,average='weighted'):.4f}")
print(f"accuracy            = {(all_true==all_pred).mean():.4f}")
