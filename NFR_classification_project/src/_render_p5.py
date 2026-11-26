import pymupdf
pdf = r'C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\src\_preview_report.pdf'
doc = pymupdf.open(pdf)
for i in [4,5]:
    page = doc[i]
    pix = page.get_pixmap(matrix=pymupdf.Matrix(2,2))
    pix.save(rf'C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\src\_rpC_p{i+1}.png')
print("done")
