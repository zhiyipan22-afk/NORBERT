# -*- coding: utf-8 -*-
from pptx import Presentation
from pptx.util import Emu
f = r"C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\NoRBERT_Presentation_updated.pptx"
p = Presentation(f)
s = p.slides[10]
print("slide size emu:", p.slide_width, p.slide_height)
for i, sh in enumerate(s.shapes):
    txt = sh.text_frame.text[:60].replace("\n", " | ") if sh.has_text_frame else "(no text)"
    print(i, sh.shape_id, sh.shape_type,
          "x=%d y=%d w=%d h=%d" % (sh.left/9525 if sh.left else -1,
                                    sh.top/9525 if sh.top else -1,
                                    sh.width/9525 if sh.width else -1,
                                    sh.height/9525 if sh.height else -1),
          "::", txt)
