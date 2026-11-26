p = r'C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\ppt_slides\fix_pew.xml'
with open(p, 'r', encoding='utf-8') as f:
    c = f.read()
import xml.dom.minidom as M
for i, line in enumerate(c.split('\n'), 1):
    if 'CLS' in line or 'Explore' in line:
        print(i, repr(line))
# Validate well-formedness (wrap in a root; content uses single slide)
try:
    M.parseString(c)
    print('XML well-formed')
except Exception as e:
    print('XML ERROR:', e)
