# -*- coding: utf-8 -*-
import os
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn

# colors
DARK = RGBColor(0x1F, 0x23, 0x29)
GRAY = RGBColor(0x55, 0x55, 0x55)
BODY = RGBColor(0x33, 0x33, 0x33)
GAPG = RGBColor(0x78, 0x78, 0x78)
BLUE = RGBColor(0x15, 0x65, 0xC0)
FONT = "Calibri"

prs = Presentation()
prs.slide_width = Emu(12192000)   # 13.333 in
prs.slide_height = Emu(6858000)   # 7.5 in  -> 960 x 540 pt
slide = prs.slides.add_slide(prs.slide_layouts[6])

def emu(pt):
    return Emu(int(pt * 12700))

def add_box(x, y, w, h):
    tb = slide.shapes.add_textbox(emu(x), emu(y), emu(w), emu(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.TOP
    for m in ("margin_left", "margin_right", "margin_top", "margin_bottom"):
        setattr(tf, m, Pt(0))
    return tf

def para(tf, first, runs, align=PP_ALIGN.LEFT, line=1.22):
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.alignment = align
    p.line_spacing = line
    for text, size, bold, italic, color in runs:
        r = p.add_run()
        r.text = text
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.italic = italic
        r.font.name = FONT
        r.font.color.rgb = color
        r.font._rPr.rPr if False else None
    return p

# ---- Title ----
tf = add_box(60, 28, 840, 44)
para(tf, True, [("8. Our Improvement: Three-Layer Strategy", 28, True, False, DARK)])

# ---- Subtitle ----
tf = add_box(60, 82, 840, 24)
para(tf, True, [("Each layer targets one root cause (Gap) with a matched method; every term is defined inline.", 13, False, False, GRAY)])

# column content
def col(x, head, body_paras):
    tf = add_box(x, 112, 270, 26)
    para(tf, True, [(head, 14, True, False, BLUE)])
    tf = add_box(x, 140, 270, 296)
    for i, runs in enumerate(body_paras):
        para(tf, i == 0, runs)

# Layer 1
l1 = [
    [("Gap: word-only features miss unseen / inflected words (availability vs available), worst for rare classes.", 11, False, True, GAPG)],
    [("How — fuse two TF-IDF feature views:", 11, True, False, DARK)],
    [("Word n-gram (1,2): ", 11, True, False, DARK), ("single words + adjacent pairs (system shall).", 11, False, False, BODY)],
    [("Char n-gram (3,5): ", 11, True, False, DARK), ("3–5 letter chunks (avail-, -able) capture root/affix.", 11, False, False, BODY)],
    [("sublinear_tf: ", 11, True, False, DARK), ("use 1+log(count) to damp repeated generic words.", 11, False, False, BODY)],
    [("Recognizes unseen words from morphology → fixes OOV.", 11, False, False, BODY)],
    [("Effect: +11.9% Weighted F1 on Task 2/3.", 11, True, False, BLUE)],
]
col(60, "Layer 1: Feature Engineering", l1)

# Layer 2
l2 = [
    [("Gap: rare classes (FT=10, Data=18%) are ignored — model predicts the majority, giving per-class F1 = 0.", 11, False, True, GAPG)],
    [("How — balance classes, then regularize:", 11, True, False, DARK)],
    [("Random oversampling: ", 11, True, False, DARK), ("duplicate rare samples in the TRAIN fold only.", 11, False, False, BODY)],
    [("Balanced class weight: ", 11, True, False, DARK), ("raise the cost of missing a rare class.", 11, False, False, BODY)],
    [("L2 regularization, C=0.5: ", 11, True, False, DARK), ("smaller C = stronger penalty, stops memorizing copies.", 11, False, False, BODY)],
    [("Test fold untouched → no leakage, no overfitting.", 11, False, False, BODY)],
    [("Effect: +2.8% more; Data per-class F1 0% → 60.4%.", 11, True, False, BLUE)],
]
col(345, "Layer 2: Data Balancing", l2)

# Layer 3
l3 = [
    [("Gap: labels trained independently (Binary Relevance), ignoring label relations — the paper’s Future Work.", 11, False, True, GAPG)],
    [("How — chain models; pass earlier probabilities as features:", 11, True, False, DARK)],
    [("Task 4: ", 11, True, False, DARK), ("F/Q → OnlyF/OnlyQ by logical identity.", 11, False, False, BODY)],
    [("OnlyF = F & not Q (holds on 612/612 cases).", 11, False, False, BODY)],
    [("Task 5: ", 11, True, False, DARK), ("Function → Behavior → Data chain.", 11, False, False, BODY)],
    [("Uses label correlation r = −0.639.", 11, False, False, BODY)],
    [("Turns logical constraints & correlations into explicit features.", 11, False, False, BODY)],
    [("Effect: OnlyF +5.1%; Data Weighted F1 +13.3%.", 11, True, False, BLUE)],
]
col(630, "Layer 3: Classifier Chain", l3)

# ---- Bottom result ----
tf = add_box(60, 446, 840, 56)
para(tf, True, [("Result: validated on the LR+TF-IDF baseline (CPU, 10-fold CV). Significant gains on Task 2/3, Task 4 and Task 5 — largest on rare classes; Task 1 is not significant (already near ceiling).", 12, True, False, BLUE)])

# speaker notes
notes = slide.notes_slide.notes_text_frame
notes.text = ("Our three-layer improvement, each layer fixing one root cause. Layer 1 fuses word and "
              "character n-grams (sublinear_tf) to fix OOV: +11.9% on Task 2/3. Layer 2 oversamples "
              "minority classes in the train fold only, adds balanced class weights and stronger L2 "
              "(C=0.5) to prevent memorizing: Data per-class F1 0 to 60.4%. Layer 3 chains classifiers "
              "(Task 4 logical identity OnlyF = F and not Q; Task 5 Function->Behavior->Data using "
              "r=-0.639), addressing the paper's Future Work. Validated on LR+TF-IDF, CPU, 10-fold CV.")

desktop = r"C:\Users\pzy\Desktop"
out = os.path.join(desktop, "NoRBERT_Slide11_Three-Layer.pptx")
prs.save(out)
print("saved:", out)
print("exists:", os.path.exists(out), "size:", os.path.getsize(out))
