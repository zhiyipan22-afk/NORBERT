from docx import Document
import zipfile, re
path = r'C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\NoRBERT_Project_Report_EN.docx'
doc = Document(path)
print("paragraphs:", len(doc.paragraphs), "tables:", len(doc.tables))
z = zipfile.ZipFile(path)
print("images:", len([n for n in z.namelist() if 'media' in n]))
full = "\n".join(p.text for p in doc.paragraphs)
for t in doc.tables:
    for r in t.rows:
        full += "\n" + " | ".join(c.text for c in r.cells)
# detect CJK characters
cjk = re.findall(r'[\u4e00-\u9fff]+', full)
print("CJK runs found:", len(cjk))
for c in sorted(set(cjk))[:20]:
    print("  CJK:", c)
# key English checks
for k in ['A function that a system shall perform','Portability','97.4%','classifier chain','Statistical Conclusion','0% → 60.4%']:
    print(("OK " if k in full else "MISSING ")+k)
