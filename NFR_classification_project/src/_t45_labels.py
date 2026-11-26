import pandas as pd
base = r'C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\data\Code'

# Task 4
df4 = pd.read_csv(base + r'\Task4_relabeled_Promise_NFR_dataset\promise-reclass.csv')
print("TASK4 columns:", list(df4.columns))
print("TASK4 raw rows:", len(df4))
d4 = df4[df4['NotR']==0]
print("TASK4 valid (NotR==0):", len(d4))
for c in ['IsFunctional','IsQuality','IsOnlyFunctional','IsOnlyQuality']:
    print(f"  {c}: pos={int(d4[c].sum())}")
print("  TASK4 sample text:", d4['RequirementText'].iloc[0])

# Task 5
df5 = pd.read_csv(base + r'\Task5_func_concerns_dataset\func_concerns.csv', sep=None, engine='python')
print("\nTASK5 columns:", list(df5.columns))
print("TASK5 rows:", len(df5))
for c in ['Function','Data','Behavior']:
    print(f"  {c}: pos={int(df5[c].sum())} ({df5[c].mean()*100:.1f}%)")

# examples for each Task5 label (one positive example each)
for c in ['Function','Data','Behavior']:
    pos = df5[df5[c]==1]['RequirementText'].head(2).tolist()
    print(f"\n[{c}] examples:")
    for t in pos: print("   -", t[:140])
