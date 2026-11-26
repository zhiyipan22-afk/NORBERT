# -*- coding: utf-8 -*-
import pandas as pd, numpy as np
from scipy import stats

p = r"C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\data\Code\Task5_func_concerns_dataset\func_concerns.csv"
df = pd.read_csv(p, sep=None, engine="python")
print("cols:", list(df.columns))
print("n:", len(df))
cols = ["Function", "Data", "Behavior"]
for c in cols:
    print(c, "pos=", int(df[c].astype(int).sum()))

print("\n-- Pearson (phi) correlation --")
for i in range(len(cols)):
    for j in range(i+1, len(cols)):
        a = df[cols[i]].astype(int).values
        b = df[cols[j]].astype(int).values
        r, pval = stats.pearsonr(a, b)
        rs, ps = stats.spearmanr(a, b)
        print(f"{cols[i]:9s} - {cols[j]:9s}: Pearson r={r:.4f} (p={pval:.4f})  Spearman={rs:.4f}")
