import re
p = r'C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\ppt_slides\audit_v4.xml'
with open(p,'r',encoding='utf-8') as f:
    xml = f.read()

# Check for stale content
stale_patterns = ['Focal Loss','5-fold','5 fold','Compatibility','(Portability)','(Maintainability)','4.45','0.0009','370 functional','255 non-functional','d=4.']
print("=== STALE CONTENT SCAN ===")
for pat in stale_patterns:
    idxs = [m.start() for m in re.finditer(re.escape(pat), xml)]
    if idxs:
        for i in idxs:
            # find which slide
            slide_ids = list(re.finditer(r'<slide id="([^"]+)"', xml))
            sid = '?'
            for sm in slide_ids:
                if sm.start() < i:
                    sid = sm.group(1)
                else:
                    break
            ctx = xml[max(0,i-40):i+50].replace('\n',' ')
            print(f"  [{pat}] in {sid}: ...{ctx}...")
    else:
        print(f"  clean: {pat}")

# Count slides
slides = re.findall(r'<slide id="([^"]+)"', xml)
print(f"\nTotal slides: {len(slides)}")
print("Order:", slides)
