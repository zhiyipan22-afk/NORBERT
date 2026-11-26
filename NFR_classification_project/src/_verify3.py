from docx import Document
path = r'C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\NoRBERT_Project_Report.docx'
doc = Document(path)
print("total tables:", len(doc.tables))
full = "\n".join(p.text for p in doc.paragraphs)
for t in doc.tables:
    for r in t.rows:
        full += "\n" + " | ".join(c.text for c in r.cells)
checks = ['Portability（可移植性）','A function that a system shall perform',
          'data item or data structure','triggered by one or more stimuli',
          'Krippendorff','IsOnlyFunctional（OnlyF）','既功能又质量','纯功能230']
for c in checks:
    print(("OK " if c in full else "MISSING ")+c)
# print the two Task4/5 tables
for ti,t in enumerate(doc.tables):
    head = t.rows[0].cells[0].text
    if head in ('标签',):
        print(f"\n=== TABLE {ti} (first cell '{head}') ===")
        for r in t.rows:
            print(" | ".join(c.text for c in r.cells))
