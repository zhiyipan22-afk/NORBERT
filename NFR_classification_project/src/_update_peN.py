"""
Update peN slide with verbose error output
"""
import subprocess
import os

pres = "ShhmsEahUl1AcCdL712cgGM4nWb"
base_dir = r"C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project"

xml_path = os.path.join(base_dir, "ppt_slides/peN_new.xml")
with open(xml_path, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"XML length: {len(content)}")
print(f"First 200 chars: {content[:200]}")
print()

print("Updating peN...")
result = subprocess.run(
    ["lark-cli", "slides", "+update-slide",
     "--presentation", pres,
     "--slide-id", "peN",
     "--content", content],
    capture_output=True, text=True, encoding='utf-8',
    cwd=base_dir
)
print(f"Return code: {result.returncode}")
if result.returncode != 0:
    print(f"Error: {result.stderr}")
else:
    print("Success!")
