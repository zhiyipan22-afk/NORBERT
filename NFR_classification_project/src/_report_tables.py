from docx import Document
doc = Document(r'C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\NoRBERT_Project_Report.docx')
out = []
for ti, t in enumerate(doc.tables):
    out.append(f"\n##### TABLE {ti} ({len(t.rows)}x{len(t.columns)}) #####")
    for r in t.rows:
        cells = [c.text.strip().replace('\n',' ') for c in r.cells]
        out.append(" | ".join(cells))
with open(r'C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\src\_report_tables.txt','w',encoding='utf-8') as f:
    f.write("\n".join(out))
print("done")
