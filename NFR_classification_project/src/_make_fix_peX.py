p_in = r'C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\ppt_slides\orig_peX.xml'
p_out = r'C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\ppt_slides\fix_peX.xml'
with open(p_in,'r',encoding='utf-8') as f:
    x = f.read()
# Only the Task 1 row cells are 89.6 / -0.4 / Match (all unique)
x = x.replace('<p>89.6%</p>', '<p>97.4%</p>')
x = x.replace('<p>-0.4%</p>', '<p>+7.4%</p>')
x = x.replace('<p>Match</p>', '<p>Better</p>')
with open(p_out,'w',encoding='utf-8') as f:
    f.write(x)
print("written")
# sanity: ensure no 89.6 / -0.4 / Match remain
for s in ['89.6','-0.4','Match','97.4','+7.4']:
    print(s, x.count(s))
