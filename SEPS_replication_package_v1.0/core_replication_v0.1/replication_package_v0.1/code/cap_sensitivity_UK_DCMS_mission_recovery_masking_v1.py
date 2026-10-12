#!/usr/bin/env python3
"""Pre-specified cap sensitivity: 1.00 primary vs 1.25 vs uncapped recovery ratios."""
from pathlib import Path
import csv,json,statistics,collections
import numpy as np
root=next(q for p in Path('G:/').iterdir() if p.is_dir() for q in p.iterdir() if q.is_dir() and 'Cities+SEPS' in q.name)
stage=next(root.glob('05_*'));s33=stage/'33_UK_DCMS_robust_early_warning_benchmark_vs_equal_weight_v1';out=stage/'34_SEPS_manuscript_prototype_and_internal_desk_reject_v1'
with (s33/'UK_DCMS_museum_year_robust_warning_vs_equalweight_VISITOR_benchmark_v1.csv').open(encoding='utf-8-sig') as f:rows=[r for r in csv.DictReader(f) if r['dimension_set']=='core5']
variants=[('cap_1.00',1.0),('cap_1.25',1.25),('uncapped',None)]
detail=[];summary=[]
for label,cap in variants:
 spans=[];vm=[];mask90=mask80=0;eq90=all90=0
 bott=collections.Counter()
 for r in rows:
  raw=np.array([float(x) for x in r['raw_recovery_pipe'].split('|')])
  a=raw.copy() if cap is None else np.minimum(raw,cap)
  eq=float(a.mean());mn=float(a.min());vis=float(a[0])
  spans.append(eq-mn);vm.append(max(0,vis-mn))
  mask90+=int(eq>=.9 and mn<.9);mask80+=int(eq>=.8 and mn<.8);eq90+=int(eq>=.9);all90+=int(mn>=.9)
  for i,v in enumerate(a):
   if abs(v-mn)<=1e-12:bott[i]+=1
  detail.append({'variant':label,'museum_group':r['museum_group'],'FY_start':r['FY_start'],
   'equalweight':round(eq,8),'weakest':round(mn,8),'masking_span':round(eq-mn,8),
   'visitor_masking':round(max(0,vis-mn),8),'equal_pass90_not_all':int(eq>=.9 and mn<.9)})
 summary.append({'variant':label,'cap':cap if cap is not None else 'none','museum_years':len(rows),
   'mean_equalweight_masking_span':round(statistics.mean(spans),4),
   'median_equalweight_masking_span':round(statistics.median(spans),4),
   'mean_visitor_masking_span':round(statistics.mean(vm),4),
   'masking_cases_t090':mask90,'masking_cases_t080':mask80,
   'equalweight_pass_t090':eq90,'allmissions_pass_t090':all90,
   'bottleneck_index_counts':dict(bott)})
with (out/'UK_DCMS_recovery_cap_sensitivity_summary_v1.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
with (out/'UK_DCMS_recovery_cap_sensitivity_detail_v1.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(detail[0]));w.writeheader();w.writerows(detail)
qa={'variants':summary,
 'decision_rule':'Core masking result passes robustness if mean masking remains positive/material and tau=.90 pass-but-not-all cases do not disappear under cap1.25 and uncapped specifications.',
 'primary_cap_rationale':'cap1.00 encodes restoration-to-baseline; surplus in one mission cannot compensate another mission shortfall.',
 'uncapped_warning':'Uncapped equal weighting allows large over-recovery in one dimension to offset another shortfall and is therefore not preferred for a restoration objective.'}
(out/'UK_DCMS_recovery_cap_sensitivity_QA_v1.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8')
print('CAP_SENSITIVITY',json.dumps(summary,ensure_ascii=False),flush=True)
