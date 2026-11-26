import pandas as pd
p = r'C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\data\Code\Task1_to_3_original_Promise_NFR_dataset\promise_nfr.csv'
df = pd.read_csv(p)
print("shape:", df.shape)
print("cols:", list(df.columns))
cols = ['A','FT','L','LF','MN','O','PE','PO','SC','SE','US']
nfr = df[df['NFR']==1]
print("NFR total:", len(nfr))
print("F (FR) total:", (df['NFR']==0).sum())
counts = {c: int(df[c].sum()) for c in cols}
for c in sorted(counts, key=lambda x:-counts[x]):
    print(f"  {c}: {counts[c]}")
print("sum of subclass flags:", sum(counts.values()))
