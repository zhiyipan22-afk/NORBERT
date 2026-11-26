# -*- coding: utf-8 -*-
import os, datetime
from pptx import Presentation
f = r"C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\NoRBERT_Presentation_updated.pptx"
print("mtime:", datetime.datetime.fromtimestamp(os.path.getmtime(f)))
p = Presentation(f)
s = p.slides[10]
t = "\n".join(sh.text_frame.text for sh in s.shapes if sh.has_text_frame)
print("NEW_MARKER_PRESENT:", "targets one root cause" in t)
print("OLD_MARKER_PRESENT:", "address three gaps in the original paper" in t)
