"""
Update PPT slides using lark-cli via Python subprocess
"""
import subprocess
import os

pres = "ShhmsEahUl1AcCdL712cgGM4nWb"
base_dir = r"C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project"

slides_to_update = [
    ("peE", "ppt_slides/peE_new.xml"),
    ("peO", "ppt_slides/peO_new.xml"),
    ("peQ", "ppt_slides/peQ_new.xml"),
]

for slide_id, xml_path in slides_to_update:
    full_path = os.path.join(base_dir, xml_path)
    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"Updating slide {slide_id}...")
    result = subprocess.run(
        ["lark-cli", "slides", "+update-slide",
         "--presentation", pres,
         "--slide-id", slide_id,
         "--content", content],
        capture_output=True, text=True, encoding='utf-8',
        cwd=base_dir
    )
    if result.returncode == 0:
        print(f"  Success!")
    else:
        print(f"  Error: {result.stderr[:200]}")

print("\nDone!")
