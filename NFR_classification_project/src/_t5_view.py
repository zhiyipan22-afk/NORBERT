# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

p = r"C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\data\Code\Task5_func_concerns_dataset\func_concerns.csv"
df = pd.read_csv(p, sep=None, engine='python')

print("rows =", len(df))
print("\n--- 交叉分布 (Function, Data, Behavior) ---")
ct = df[['Function', 'Data', 'Behavior']].value_counts().sort_index()
print(ct.to_string())
print("\n--- 三列总计 ---")
print(df[['Function', 'Data', 'Behavior']].sum().to_string())
print("\n--- Function vs Behavior 交叉表 ---")
print(pd.crosstab(df.Function, df.Behavior).to_string())
r = np.corrcoef(df.Function, df.Behavior)[0, 1]
print("phi(Function, Behavior) = %.4f" % r)
r2 = np.corrcoef(df.Function, df.Data)[0, 1]
r3 = np.corrcoef(df.Behavior, df.Data)[0, 1]
print("phi(Function, Data) = %.4f" % r2)
print("phi(Behavior, Data) = %.4f" % r3)


def show(cond, title, n=12):
    sub = df[cond]
    print("\n=== %s  (count=%d) ===" % (title, len(sub)))
    for t in sub.RequirementText.head(n):
        print("  *", str(t)[:190])


show((df.Function == 1) & (df.Behavior == 0), "只有 Function")
show((df.Behavior == 1) & (df.Function == 0), "只有 Behavior")
show((df.Function == 1) & (df.Behavior == 1), "Function + Behavior 同时")
show((df.Data == 1) & (df.Function == 0) & (df.Behavior == 0), "只有 Data")
