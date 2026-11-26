from docx import Document
doc = Document(r'C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\NoRBERT_Project_Report.docx')
out = []
for i in range(38, 105):
    if i < len(doc.paragraphs):
        t = doc.paragraphs[i].text
        if t.strip():
            out.append(f"[{i}] {t}")
with open(r'C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\src\_report_mid.txt','w',encoding='utf-8') as f:
    f.write("\n".join(out))
print("done")
