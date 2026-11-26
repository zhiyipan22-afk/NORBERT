import zipfile, re
p = r'C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project\NoRBERT_Presentation.pptx'
z = zipfile.ZipFile(p)
slides = sorted([n for n in z.namelist() if re.match(r'ppt/slides/slide\d+\.xml', n)],
                key=lambda x: int(re.search(r'(\d+)', x).group(1)))
print("slide count:", len(slides))
for i, n in enumerate(slides):
    x = z.read(n).decode('utf-8', errors='ignore')
    # strip tags, keep text
    txt = re.sub(r'<[^>]+>', '', x)
    if '97.4' in txt or '89.6' in txt or 'Reproduction' in txt:
        print(f"slide {i+1}: 97.4={'97.4' in txt} 89.6={'89.6' in txt} Reproduction={'Reproduction' in txt}")
