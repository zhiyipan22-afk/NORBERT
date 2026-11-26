import subprocess, os
pres = "ShhmsEahUl1AcCdL712cgGM4nWb"
base = r"C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project"
r = subprocess.run(["lark-cli","slides","+add-slide","--presentation",pres,
                    "--slide","@./ppt_slides/add_task45.xml",
                    "--before-slide-id","peH"],
                   capture_output=True, text=True, encoding='utf-8', cwd=base)
log = f"rc={r.returncode}\n"
log += (r.stdout or "") + "\n" + (r.stderr or "")
with open(os.path.join(base,"src","_add45_log.txt"),'w',encoding='utf-8') as f:
    f.write(log)
