import pymupdf, os
pdf = r'C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\src\_preview_report.pdf'
outdir = r'C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\src'
doc = pymupdf.open(pdf)
for i in [11]:
    page = doc[i]
    pix = page.get_pixmap(matrix=pymupdf.Matrix(1.6,1.6))
    pix.save(os.path.join(outdir, f"_rp_p{i+1}.png"))
print("done")
