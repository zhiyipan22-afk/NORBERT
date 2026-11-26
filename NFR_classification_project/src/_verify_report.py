from docx import Document
import zipfile
path = r'C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\NoRBERT_Project_Report.docx'
z = zipfile.ZipFile(path)
media = [n for n in z.namelist() if 'media' in n]
print("=== EMBEDDED IMAGES ===")
for m in media:
    info = z.getinfo(m)
    print(f"  {m}  ({info.file_size} bytes)")

doc = Document(path)
print(f"\nParagraphs: {len(doc.paragraphs)}, Tables: {len(doc.tables)}")
# check new section
found = False
for i,p in enumerate(doc.paragraphs):
    if '8.1' in p.text and '统计分析前后' in p.text:
        found = True
        print(f"\nNew section found at para [{i}]: {p.text}")
print("\nFigures present:", len(media) == 4)
