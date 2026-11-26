import re
p = r'C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\ppt_slides\audit_v4.xml'
with open(p,'r',encoding='utf-8') as f:
    xml = f.read()

# Split by slide, extract text
slides = re.split(r'(?=<slide id=")', xml)
out = []
for s in slides:
    m = re.search(r'<slide id="([^"]+)"', s)
    if not m: continue
    sid = m.group(1)
    texts = re.findall(r'<p[^>]*>(.*?)</p>', s, re.S)
    clean = []
    for t in texts:
        t = re.sub(r'<[^>]+>','',t)
        t = t.replace('&lt;','<').replace('&gt;','>').replace('&amp;','&').strip()
        if t: clean.append(t)
    out.append(f"===== {sid} =====")
    out.extend(clean)
    out.append("")
with open(r'C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\src\_ppt_text_final.txt','w',encoding='utf-8') as f:
    f.write("\n".join(out))
print("done")
