from docx import Document
import zipfile
path = r'C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\NoRBERT_Project_Report.docx'
doc = Document(path)
full = "\n".join(p.text for p in doc.paragraphs)
for t in doc.tables:
    for r in t.rows:
        full += "\n" + " | ".join(c.text for c in r.cells)
print("Tables:", len(doc.tables))
z = zipfile.ZipFile(path)
print("Images:", len([n for n in z.namelist() if 'media' in n]))
print("75.4 present:", "75.4" in full)
print("从头训练 present:", "从头训练" in full)
print("89.6 present:", "89.6" in full)
print("97.4 present:", "97.4" in full)
# print table 1 and repro table
for ti,t in enumerate(doc.tables):
    first = t.rows[0].cells[0].text
    if first in ('模型','任务'):
        print(f"\n=== TABLE {ti} ===")
        for r in t.rows:
            print(" | ".join(c.text for c in r.cells))
