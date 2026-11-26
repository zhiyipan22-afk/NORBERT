import subprocess, os
pres = "ShhmsEahUl1AcCdL712cgGM4nWb"
base = r"C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project"
with open(os.path.join(base,"ppt_slides","fix_peX.xml"),'r',encoding='utf-8') as f:
    c = f.read()
r = subprocess.run(["lark-cli","slides","+update-slide","--presentation",pres,
                    "--slide-id","peX","--content",c],
                   capture_output=True, text=True, encoding='utf-8', cwd=base)
log = f"rc={r.returncode}\n{r.stdout}\n{r.stderr}"
with open(os.path.join(base,"src","_pex_log.txt"),'w',encoding='utf-8') as f:
    f.write(log)
print("rc", r.returncode)
