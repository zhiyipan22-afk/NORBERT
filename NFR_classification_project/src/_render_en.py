import pymupdf
pdf = r'C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\src\_en_preview.pdf'
doc = pymupdf.open(pdf)
print("pages:", doc.page_count)
for i in range(doc.page_count):
    t = doc[i].get_text()
    if i == 0 or 'A function that a system shall' in t.replace('\n',' '):
        doc[i].get_pixmap(matrix=pymupdf.Matrix(2,2)).save(rf'C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\src\_en_p{i+1}.png')
        print("rendered page", i+1)
