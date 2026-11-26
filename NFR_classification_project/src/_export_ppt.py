import subprocess, os
pres = "ShhmsEahUl1AcCdL712cgGM4nWb"
base = r"C:\Users\pzy\Documents\Master-ddl\metrix\group_work\NFR_classification_project"
r = subprocess.run(["lark-cli","drive","+export",
                    "--token",pres,"--doc-type","slides",
                    "--file-extension","pptx",
                    "--output-dir",base,
                    "--file-name","NoRBERT_Presentation",
                    "--overwrite","--json"],
                   capture_output=True, text=True, encoding='utf-8', cwd=base)
log = f"rc={r.returncode}\n{r.stdout}\n{r.stderr}"
with open(os.path.join(base,"src","_export_log.txt"),'w',encoding='utf-8') as f:
    f.write(log)
print("done")
