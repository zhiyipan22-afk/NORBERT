import pymupdf
pdf = r'C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\src\_en_preview.pdf'
doc = pymupdf.open(pdf)
for i in [2,3]:
    doc[i].get_pixmap(matrix=pymupdf.Matrix(2,2)).save(rf'C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\src\_en_q_p{i+1}.png')
print("done")
