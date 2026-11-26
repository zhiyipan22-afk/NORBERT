import subprocess, os, re
import xml.dom.minidom as M

pres = "ShhmsEahUl1AcCdL712cgGM4nWb"
base = r"C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project"
logs = []

# --- validate pew XML ---
for sid in ['pew', 'peE']:
    path = os.path.join(base, "ppt_slides", f"fix_{sid}.xml")
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()
    try:
        M.parseString(c)
        logs.append(f"{sid}: local XML well-formed")
    except Exception as e:
        logs.append(f"{sid}: local XML ERROR {e}")

# --- update pew ---
path = os.path.join(base, "ppt_slides", "fix_pew.xml")
with open(path, 'r', encoding='utf-8') as f:
    pew = f.read()
r = subprocess.run(["lark-cli","slides","+update-slide","--presentation",pres,
                    "--slide-id","pew","--content",pew],
                   capture_output=True, text=True, encoding='utf-8', cwd=base)
logs.append(f"pew update rc={r.returncode}")
if r.returncode != 0:
    logs.append("pew stderr: " + (r.stderr or r.stdout)[:600])

# --- diagnose peE: dry-run full error ---
path = os.path.join(base, "ppt_slides", "fix_peE.xml")
with open(path, 'r', encoding='utf-8') as f:
    pee = f.read()
r2 = subprocess.run(["lark-cli","slides","+update-slide","--presentation",pres,
                    "--slide-id","peE","--content",pee],
                   capture_output=True, text=True, encoding='utf-8', cwd=base)
logs.append(f"peE update rc={r2.returncode}")
if r2.returncode != 0:
    logs.append("peE stderr: " + (r2.stderr or r2.stdout)[:1200])

with open(os.path.join(base,"src","_diag_log.txt"),'w',encoding='utf-8') as f:
    f.write("\n\n".join(logs))
