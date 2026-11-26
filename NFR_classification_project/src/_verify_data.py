import pandas as pd
out = []
df = pd.read_csv(r'C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\data\Code\Task1_to_3_original_Promise_NFR_dataset\promise_nfr.csv')
out.append(str(df['class'].value_counts()))
out.append(f"\nNFR=0 (FR): {(df['NFR']==0).sum()}")
out.append(f"NFR=1 (NFR): {(df['NFR']==1).sum()}")
with open(r'C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\src\_data_check.txt','w',encoding='utf-8') as f:
    f.write("\n".join(out))
