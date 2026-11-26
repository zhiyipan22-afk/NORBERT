import pymupdf
pdf = r'C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\src\_preview_report.pdf'
doc = pymupdf.open(pdf)
print("pages:", doc.page_count)
for i,page in enumerate(doc):
    t = page.get_text()
    marks = []
    for k in ['五、基线','预训练模型复现','97.4%','89.6%','结果分析']:
        if k in t: marks.append(k)
    if marks:
        print(f"page {i+1}: {marks}")
        pix = page.get_pixmap(matrix=pymupdf.Matrix(2,2))
        pix.save(rf'C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\src\_rp_p{i+1}.png')
