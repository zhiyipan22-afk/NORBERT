import pandas as pd

data_path = r"C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\data\Code\Task1_to_3_original_Promise_NFR_dataset\promise_nfr.csv"
df = pd.read_csv(data_path)

print("=== Dataset Overview ===")
print(f"Total rows: {len(df)}")
print(f"Columns: {df.columns.tolist()}")
print()

# Check NFR column
print("=== NFR Column Distribution ===")
print(df['NFR'].value_counts())
print()

# Check NFR subcolumns
nfr_subcols = ['A', 'FT', 'L', 'LF', 'MN', 'O', 'PE', 'PO', 'SC', 'SE', 'US']
print("=== NFR Subclass Counts ===")
for col in nfr_subcols:
    if col in df.columns:
        count = df[col].sum()
        print(f"  {col}: {count}")

print()
print("=== Verify: FR vs NFR ===")
nfr_count = df['NFR'].sum()
fr_count = len(df) - nfr_count
print(f"NFR=1 count: {nfr_count}")
print(f"NFR=0 count (FR): {fr_count}")
print(f"Total: {len(df)}")
