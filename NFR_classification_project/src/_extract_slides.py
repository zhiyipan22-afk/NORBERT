"""
Extract specific slides to individual files for reference
"""
import re

with open(r"C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\ppt_slides\audit_latest.xml", 'r', encoding='utf-8') as f:
    xml = f.read()

# Split by slide
slides = re.findall(r'(  <slide id="[^"]+">.*?</slide>)', xml, re.DOTALL)

targets = ['peV', 'peE', 'pei', 'peH', 'pew']
for s in slides:
    m = re.search(r'<slide id="([^"]+)"', s)
    if m and m.group(1) in targets:
        sid = m.group(1)
        out = rf"C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\ppt_slides\orig_{sid}.xml"
        with open(out, 'w', encoding='utf-8') as f:
            f.write(s)
        print(f"Saved {sid}: {len(s)} chars")
