import subprocess, os, re

pres = "ShhmsEahUl1AcCdL712cgGM4nWb"
base = r"C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project"
logs = []

pages = ['peV', 'pei', 'peH', 'pew', 'peE']
for sid in pages:
    path = os.path.join(base, "ppt_slides", f"fix_{sid}.xml")
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    r = subprocess.run(
        ["lark-cli", "slides", "+update-slide",
         "--presentation", pres, "--slide-id", sid, "--content", content],
        capture_output=True, text=True, encoding='utf-8', cwd=base)
    if r.returncode == 0:
        logs.append(f"{sid}: OK")
    else:
        msg = r.stderr or r.stdout
        mm = re.search(r'"message":\s*"([^"]{0,500})', msg)
        logs.append(f"{sid}: FAIL - {mm.group(1) if mm else msg[:400]}")

with open(os.path.join(base, "src", "_update5_log.txt"), 'w', encoding='utf-8') as f:
    f.write("\n".join(logs))
