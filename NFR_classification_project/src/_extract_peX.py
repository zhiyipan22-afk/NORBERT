import re
p = r'C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\ppt_slides\audit_v4.xml'
with open(p,'r',encoding='utf-8') as f:
    xml = f.read()
# extract peX slide
m = re.search(r'<slide id="peX".*?</slide>', xml, re.S)
with open(r'C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\ppt_slides\orig_peX.xml','w',encoding='utf-8') as f:
    f.write(m.group(0))
print("peX extracted, length", len(m.group(0)))
# print lines containing 89.6 or Task 1
for i,line in enumerate(m.group(0).split('\n')):
    if '89.6' in line or '-0.4' in line or 'Match' in line or 'Task 1' in line:
        print(f"L{i}: {line.strip()}")
