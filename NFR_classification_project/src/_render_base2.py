import pymupdf
pdf = r'C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\src\_preview_report.pdf'
doc = pymupdf.open(pdf)
for i,page in enumerate(doc):
    t = page.get_text().replace('\n',' ')
    if 'LR + TF-IDF' in t or '全量预测' in t or '仅略高于LR' in t or '预训练模型复现' in t:
        print(f"page {i+1} hits")
        pix = page.get_pixmap(matrix=pymupdf.Matrix(2,2))
        pix.save(rf'C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\src\_rpB_p{i+1}.png')
