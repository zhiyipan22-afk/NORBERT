import subprocess, os
pres = "ShhmsEahUl1AcCdL712cgGM4nWb"
base = r"C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project"
path = os.path.join(base, "ppt_slides", "fix_peE.xml")
with open(path,'r',encoding='utf-8') as f:
    c = f.read()
r = subprocess.run(["lark-cli","slides","+update-slide","--presentation",pres,
                    "--slide-id","peE","--content",c],
                   capture_output=True, text=True, encoding='utf-8', cwd=base)
log = f"peE rc={r.returncode}\n"
if r.returncode != 0:
    log += (r.stderr or r.stdout)
else:
    log += "OK"
with open(os.path.join(base,"src","_pee_log.txt"),'w',encoding='utf-8') as f:
    f.write(log)
