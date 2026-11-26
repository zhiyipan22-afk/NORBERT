from pptx import Presentation
p = r'C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\NoRBERT_Presentation.pptx'
prs = Presentation(p)
print("slides:", len(prs.slides))
found = []
for i, s in enumerate(prs.slides):
    txt = ""
    for sh in s.shapes:
        if sh.has_text_frame:
            txt += sh.text_frame.text + " "
        if sh.has_table:
            for row in sh.table.rows:
                for c in row.cells:
                    txt += c.text + " "
    if "97.4" in txt or ("89.6" in txt) or "Reproduction" in txt:
        found.append((i+1, "97.4" in txt, "89.6" in txt))
for f in found:
    print("slide", f[0], "| has97.4:", f[1], "| has89.6:", f[2])
