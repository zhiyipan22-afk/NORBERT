from pptx import Presentation

path = r"C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\NoRBERT_Presentation.pptx"
prs = Presentation(path)

changes = 0

def fix_tf(tf, where):
    global changes
    for p in tf.paragraphs:
        for run in p.runs:
            old = run.text
            new = old.replace("< 0.0001", "< 0.001").replace("<0.0001", "<0.001")
            if new != old:
                run.text = new
                changes += 1
                print(f"FIXED [{where}]: {old!r} -> {new!r}")

def walk(shapes, sidx, prefix=""):
    for shi, sh in enumerate(shapes):
        where = f"slide{sidx} {prefix}shape{shi}"
        if sh.shape_type == 6:
            walk(sh.shapes, sidx, prefix=f"grp{shi}/")
            continue
        if sh.has_text_frame:
            fix_tf(sh.text_frame, where)
        if sh.has_table:
            for ri, row in enumerate(sh.table.rows):
                for ci, cell in enumerate(row.cells):
                    fix_tf(cell.text_frame, f"{where} r{ri}c{ci}")

for sidx, slide in enumerate(prs.slides, start=1):
    walk(slide.shapes, sidx)
    if slide.has_notes_slide:
        for shi, sh in enumerate(slide.notes_slide.shapes):
            if sh.has_text_frame:
                fix_tf(sh.text_frame, f"slide{sidx} notes{shi}")

out_path = r"C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\NoRBERT_Presentation_updated.pptx"
prs.save(out_path)
print("total run changes:", changes)
print("saved:", out_path)
