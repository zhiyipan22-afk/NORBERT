p = r'C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\ppt_slides\fix_pew.xml'
with open(p, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if 'Explore BERT' in line:
        indent = line[:len(line)-len(line.lstrip())]
        line = indent + '<p>- Explore BERT embeddings fused with TF-IDF, and other imbalance methods</p>\n'
    new_lines.append(line)

c = ''.join(new_lines)
with open(p, 'w', encoding='utf-8') as f:
    f.write(c)

import xml.dom.minidom as M
try:
    M.parseString(c)
    print('XML well-formed now')
except Exception as e:
    print('XML ERROR:', e)
