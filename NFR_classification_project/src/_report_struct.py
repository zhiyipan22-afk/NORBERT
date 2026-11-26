from docx import Document
doc = Document(r'C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\NoRBERT_Project_Report.docx')
out = []
out.append("=== HEADINGS / STRUCTURE ===")
for i, p in enumerate(doc.paragraphs):
    st = p.style.name if p.style else ''
    if 'Heading' in st or 'heading' in st or 'Title' in st or 'title' in st:
        out.append(f"[{i}] ({st}) {p.text}")

# Count images
import zipfile
z = zipfile.ZipFile(r'C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\NoRBERT_Project_Report.docx')
media = [n for n in z.namelist() if 'media' in n]
out.append(f"\n=== EMBEDDED IMAGES ({len(media)}) ===")
for m in media:
    out.append(m)

with open(r'C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\src\_report_struct.txt','w',encoding='utf-8') as f:
    f.write("\n".join(out))
print("done")
