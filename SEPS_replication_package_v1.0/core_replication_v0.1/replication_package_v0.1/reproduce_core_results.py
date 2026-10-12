#!/usr/bin/env python3
from pathlib import Path
import csv, statistics, collections, json

ROOT=Path(__file__).resolve().parent
src=ROOT/"data"/"UK_DCMS_14group_mission_temporal_resilience_trajectories_FY2020_2024_v1.csv"
dims=["total_visits","under16","formal_education","onsite_U18","UK_loan_venues"]
years=["2020/21","2021/22","2022/23","2023/24","2024/25"]

def pipe(s):
    out=[]
    for z in str(s).split("|"):
        try: out.append(float(z))
        except: out.append(None)
    return out

rows=list(csv.DictReader(src.open(encoding="utf-8-sig")))
cases=[]
for r in rows:
    paths={d:pipe(r[d+"_postshock_recovery_ratio_pipe"]) for d in dims}
    if any(len(v)!=5 or any(x is None or x < 0 for x in v) for v in paths.values()):
        continue
    for j,fy in enumerate(years):
        raw=[paths[d][j] for d in dims]
        a=[min(x,1.0) for x in raw]
        eq=sum(a)/5; mn=min(a); mx=max(a); vis=a[0]
        bott=[dims[k] for k,v in enumerate(a) if abs(v-mn)<=1e-12]
        cases.append({"museum_group":r["museum_group"],"financial_year":fy,"raw":raw,"a":a,
                      "eq":eq,"mn":mn,"mx":mx,"vis":vis,"bottleneck":bott})

spans=[c["eq"]-c["mn"] for c in cases]
vspans=[max(0,c["vis"]-c["mn"]) for c in cases]
bott=collections.Counter(x for c in cases for x in c["bottleneck"])

def states(t):
    red=sum(c["mx"] < t-1e-12 for c in cases)
    green=sum(c["mn"] >= t-1e-12 for c in cases)
    return {"RED":red,"AMBER":len(cases)-red-green,"GREEN":green}

summary={
    "museum_years":len(cases),
    "museums":len({c["museum_group"] for c in cases}),
    "mean_equalweight_masking_span":round(statistics.mean(spans),4),
    "median_equalweight_masking_span":round(statistics.median(spans),4),
    "mean_visitor_masking_span":round(statistics.mean(vspans),4),
    "median_visitor_masking_span":round(statistics.median(vspans),4),
    "bottleneck_counts":dict(bott),
    "t090_equalweight_pass":sum(c["eq"]>=.9-1e-12 for c in cases),
    "t090_allmissions_pass":sum(c["mn"]>=.9-1e-12 for c in cases),
    "t090_equalweight_masking":sum(c["eq"]>=.9-1e-12 and c["mn"]<.9-1e-12 for c in cases),
    "t090_visitor_masking":sum(c["vis"]>=.9-1e-12 and c["mn"]<.9-1e-12 for c in cases),
    "t090_states":states(.9)
}

loo={}
for drop in [None]+list(range(5)):
    label="all5" if drop is None else "drop_"+dims[drop]
    vals=[]
    mask90=0
    for c in cases:
        a=[v for i,v in enumerate(c["a"]) if i!=drop] if drop is not None else c["a"]
        eq=sum(a)/len(a); mn=min(a)
        vals.append(eq-mn)
        mask90 += int(eq>=.9-1e-12 and mn<.9-1e-12)
    loo[label]={"mean_masking_span":round(statistics.mean(vals),4),"masking_cases_t090":mask90}
summary["leave_one_out"]=loo

caps={}
for label,cap in [("cap_1.00",1.0),("cap_1.25",1.25),("uncapped",None)]:
    vals=[];mask90=0
    for c in cases:
        a=c["raw"][:] if cap is None else [min(v,cap) for v in c["raw"]]
        eq=sum(a)/5;mn=min(a)
        vals.append(eq-mn);mask90+=int(eq>=.9 and mn<.9)
    caps[label]={"mean_masking_span":round(statistics.mean(vals),4),"masking_cases_t090":mask90}
summary["cap_sensitivity"]=caps

expected={
"museum_years":50,"museums":10,"mean_equalweight_masking_span":0.2299,
"median_equalweight_masking_span":0.22,"mean_visitor_masking_span":0.2407,
"median_visitor_masking_span":0.2447,"t090_equalweight_pass":6,
"t090_allmissions_pass":2,"t090_equalweight_masking":4,"t090_visitor_masking":10,
"t090_states":{"RED":23,"AMBER":25,"GREEN":2}}
for k,v in expected.items():
    if summary[k] != v:
        raise AssertionError(f"{k}: got {summary[k]!r}, expected {v!r}")

out=ROOT/"outputs"/"reproduced_core_results_v0.1.json"
out.write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding="utf-8")
print(json.dumps(summary,indent=2,ensure_ascii=False))
print("PASS: core manuscript benchmark reproduced exactly.")
