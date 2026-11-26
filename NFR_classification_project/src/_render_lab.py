import pymupdf
pdf = r'C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\src\_preview_report.pdf'
doc = pymupdf.open(pdf)
print("pages:", doc.page_count)
for i in range(doc.page_count):
    t = doc[i].get_text()
    if 'A function that a system shall perform' in t:
        doc[i].get_pixmap(matrix=pymupdf.Matrix(2,2)).save(rf'C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\src\_lab_t5_p{i+1}.png')
        print("task5 page:", i+1)
    if 'Portability' in t and ('剔除' in t or '仅1条' in t):
        doc[i].get_pixmap(matrix=pymupdf.Matrix(2,2)).save(rf'C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\src\_lab_nfr_p{i+1}.png')
        print("nfr table page:", i+1)
