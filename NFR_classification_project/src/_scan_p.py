from pptx import Presentation
import os

path = r"C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\NoRBERT_Presentation.pptx"
prs = Presentation(path)
print("slides:", len(prs.slides))

def scan_tf(tf, where):
    for pi, p in enumerate(tf.paragraphs):
        for ri, run in enumerate(p.runs):
            if "0.0001" in run.text:
                print(f"[{where}] para{pi} run{ri}: {run.text!r}")
        # also paragraph-level text (in case runs split)
    full = tf.text
    if "0.0001" in full:
        print(f"[{where}] PARAGRAPH-TEXT contains: {full!r}")

def walk(shapes, sidx, prefix=""):
    for shi, sh in enumerate(shapes):
        where = f"slide{sidx} {prefix}shape{shi}({sh.shape_type})"
        if sh.shape_type == 6:  # group
            walk(sh.shapes, sidx, prefix=f"grp{shi}/")
            continue
        if sh.has_text_frame:
            scan_tf(sh.text_frame, where)
        if sh.has_table:
            for ri, row in enumerate(sh.table.rows):
                for ci, cell in enumerate(row.cells):
                    scan_tf(cell.text_frame, f"{where} tbl r{ri}c{ci}")

for sidx, slide in enumerate(prs.slides, start=1):
    walk(slide.shapes, sidx)
    if slide.has_notes_slide:
        ns = slide.notes_slide
        for shi, sh in enumerate(ns.shapes):
            if sh.has_text_frame and "0.0001" in sh.text_frame.text:
                print(f"[slide{sidx} NOTES shape{shi}]: {sh.text_frame.text!r}")
