"""
Read the report and extract all key numbers for consistency check
"""
from docx import Document

doc = Document(r"C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\NoRBERT_Project_Report.docx")

print("=== ALL PARAGRAPHS WITH KEY NUMBERS ===")
for i, para in enumerate(doc.paragraphs):
    text = para.text
    if any(kw in text for kw in ['%', 'F1', 'p =', 'p<', 'd=', 'Cohen', 'Wilcoxon', 't-test', 'baseline', 'Baseline', '改进']):
        if text.strip():
            print(f"[{i}] {text}")

print("\n=== ALL TABLES ===")
for t_idx, table in enumerate(doc.tables):
    print(f"\n--- Table {t_idx} ---")
    for r_idx, row in enumerate(table.rows):
        cells = [cell.text.strip() for cell in row.cells]
        print(f"  Row {r_idx}: {cells}")
