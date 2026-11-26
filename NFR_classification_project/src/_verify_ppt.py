from pptx import Presentation
path = r"C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\NoRBERT_Presentation_updated.pptx"
prs = Presentation(path)

def all_texts(prs):
    texts = []
    def walk(shapes, sidx):
        for sh in shapes:
            if sh.shape_type == 6:
                walk(sh.shapes, sidx); continue
            if sh.has_text_frame: texts.append((sidx,"body",sh.text_frame.text))
            if sh.has_table:
                for row in sh.table.rows:
                    for cell in row.cells: texts.append((sidx,"cell",cell.text_frame.text))
    for i, slide in enumerate(prs.slides, start=1):
        walk(slide.shapes, i)
        if slide.has_notes_slide:
            for sh in slide.notes_slide.shapes:
                if sh.has_text_frame: texts.append((i,"notes",sh.text_frame.text))
    return texts

T = all_texts(prs)
joined = "\n".join(t for _,_,t in T)
print("slides:", len(prs.slides))
print("remaining '0.0001' occurrences:", joined.count("0.0001"))
print("'< 0.001' count:", joined.count("< 0.001"), " '<0.001' count:", joined.count("<0.001"))
print("---- slide9 table rows ----")
for sl in prs.slides[8].shapes:
    if sl.has_table:
        for r in sl.table.rows:
            print(" | ".join(c.text for c in r.cells))
print("---- sanity: other key numbers still present ----")
for k in ["0.002","0.0195","0.0039","0.30","0.23","2.08","6.32","60.4%"]:
    print(k, "->", k in joined)
