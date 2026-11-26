"""
Re-update peO slide
"""
import subprocess
import os

pres = "ShhmsEahUl1AcCdL712cgGM4nWb"
base_dir = r"C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project"

# Read peO new XML
with open(os.path.join(base_dir, "ppt_slides/peO_new.xml"), 'r', encoding='utf-8') as f:
    content = f.read()

print(f"XML length: {len(content)}")
print(f"Contains '10-fold': {'10-fold' in content}")
print(f"Contains '63.1%': {'63.1%' in content}")

# Update
print("\nUpdating peO...")
result = subprocess.run(
    ["lark-cli", "slides", "+update-slide",
     "--presentation", pres,
     "--slide-id", "peO",
     "--content", content],
    capture_output=True, text=True, encoding='utf-8',
    cwd=base_dir
)
print(f"Return code: {result.returncode}")
if result.returncode == 0:
    print("Success!")
else:
    print(f"Error: {result.stderr[:500]}")
