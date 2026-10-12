"""Portable rebuild of final Figure 1-5 from packaged data.
No analysis choices are changed; embedded assertions stop on frozen-value mismatch.
"""
import subprocess, sys, os, json, hashlib, glob
HERE=os.path.dirname(os.path.abspath(__file__))
steps=["prep_fig_data.py","fig1_city_atlas.py","fig2_masking_scatter.py","fig3_priority_dependence.py","fig4_long_strips.py","fig5_trajectories_placebo.py"]
for s in steps:
    print("RUN",s)
    subprocess.run([sys.executable,os.path.join(HERE,s)],cwd=HERE,check=True)
out=os.path.join(HERE,"out")
man=[]
for f in sorted(glob.glob(os.path.join(out,"Figure*_v2.*"))):
    man.append({"file":os.path.basename(f),"bytes":os.path.getsize(f),"sha256":hashlib.sha256(open(f,"rb").read()).hexdigest()})
json.dump({"rebuild_passed":True,"manifest":man},open(os.path.join(out,"portable_rebuild_QA.json"),"w",encoding="utf-8"),indent=2)
print("PASS",len(man),"figure files")
