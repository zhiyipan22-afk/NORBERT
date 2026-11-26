import pymupdf, os
pdf = r'C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\src\_preview_report.pdf'
outdir = r'C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\src'
doc = pymupdf.open(pdf)
print("pages:", doc.page_count)
# Find pages with images
for i,page in enumerate(doc):
    imgs = page.get_images()
    txt = page.get_text("text")
    marker = ""
    if imgs: marker += f" [IMAGES x{len(imgs)}]"
    if "8.1" in txt and "对比" in txt: marker += " [SEC8.1]"
    if "图1" in txt or "图2" in txt or "图3" in txt or "图4" in txt: marker += " [FIGCAP]"
    if marker:
        print(f"page {i+1}:{marker}")
# Render pages with images and 8.1
for i,page in enumerate(doc):
    imgs = page.get_images()
    txt = page.get_text("text")
    if imgs or ("8.1" in txt and "对比" in txt):
        pix = page.get_pixmap(matrix=pymupdf.Matrix(1.6,1.6))
        pix.save(os.path.join(outdir, f"_rp_p{i+1}.png"))
print("rendered")
