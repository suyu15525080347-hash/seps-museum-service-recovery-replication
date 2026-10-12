#!/usr/bin/env python3
"""Threshold-free and threshold-grid benchmark for multi-mission recovery warnings under unknown policy weights.
Compares robust score envelopes with equal-weight and visitor-only summaries. No causal claims, no learned weights.
"""
from pathlib import Path
import csv,json,math,statistics,collections
import numpy as np
from scipy.optimize import linprog
root=next(q for p in Path('G:/').iterdir() if p.is_dir() for q in p.iterdir() if q.is_dir() and 'Cities+SEPS' in q.name)
stage=next(root.glob('05_*'))
srcdir=stage/'32_UK_DCMS_definition_breaks_multioutput_novelty_model_screen_v1'
out=stage/'33_UK_DCMS_robust_early_warning_benchmark_vs_equal_weight_v1'
out.mkdir(exist_ok=True)
with (srcdir/'UK_DCMS_14group_mission_temporal_resilience_trajectories_FY2020_2024_v1.csv').open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
dims4=['total_visits','under16','formal_education','onsite_U18']
dims5=dims4+['UK_loan_venues']
years=[2020,2021,2022,2023,2024]
thresholds=[0.75,0.80,0.90,1.00]
weight_floors=[0.00,0.05,0.10]
def parsepipe(x):
 out=[]
 for z in str(x).split('|'):
  try:out.append(float(z))
  except:out.append(None)
 return out
def robust_interval(a,eps):
 k=len(a)
 if eps*k>1+1e-12:return None
 # LP to preserve exact method for later extensibility
 bounds=[(eps,1)]*k
 Aeq=np.ones((1,k));beq=[1]
 lo=linprog(np.asarray(a),A_eq=Aeq,b_eq=beq,bounds=bounds,method='highs')
 hi=linprog(-np.asarray(a),A_eq=Aeq,b_eq=beq,bounds=bounds,method='highs')
 if not lo.success or not hi.success:raise RuntimeError('weight envelope LP failed')
 return float(lo.fun),float(-hi.fun)
long=[];museum_complete={}
for r in rows:
 name=r['museum_group']
 for label,dims in [('core4',dims4),('core5',dims5)]:
  series={}
  ok=True
  for d in dims:
   arr=parsepipe(r[d+'_postshock_recovery_ratio_pipe'])
   if len(arr)!=5:raise RuntimeError('bad path '+name+d)
   if any(v is None or v<0 for v in arr):ok=False
   series[d]=arr
  if not ok:continue
  museum_complete[(name,label)]=True
  for yi,y in enumerate(years):
   raw=np.array([series[d][yi] for d in dims],float)
   a=np.minimum(raw,1.0)
   eq=float(a.mean());visitor=float(a[0]);mn=float(a.min());mx=float(a.max())
   bottlenecks=[dims[i] for i,v in enumerate(a) if abs(v-mn)<=1e-12]
   rec={'museum_group':name,'dimension_set':label,'FY_start':y,'financial_year':f'{y}/{str(y+1)[-2:]}',
    'n_missions':len(dims),'raw_recovery_pipe':'|'.join(f'{x:.6f}' for x in raw),
    'capped_attainment_pipe':'|'.join(f'{x:.6f}' for x in a),
    'equal_weight_score':round(eq,8),'visitor_only_score':round(visitor,8),
    'worst_mission_score':round(mn,8),'best_mission_score':round(mx,8),
    'bottleneck_missions_pipe':'|'.join(bottlenecks),
    'threshold_free_equalweight_masking_span':round(max(0,eq-mn),8),
    'threshold_free_visitor_masking_span':round(max(0,visitor-mn),8)}
   for eps in weight_floors:
    lo,hi=robust_interval(a,eps)
    rec[f'robust_lower_wfloor_{eps:.2f}']=round(lo,8)
    rec[f'robust_upper_wfloor_{eps:.2f}']=round(hi,8)
    rec[f'uncertainty_width_wfloor_{eps:.2f}']=round(hi-lo,8)
    rec[f'equalweight_minus_lower_wfloor_{eps:.2f}']=round(eq-lo,8)
   for t in thresholds:
    rec[f'equalweight_pass_{t:.2f}']=int(eq>=t-1e-12)
    rec[f'visitor_pass_{t:.2f}']=int(visitor>=t-1e-12)
    rec[f'all_missions_pass_{t:.2f}']=int(mn>=t-1e-12)
    rec[f'any_mission_pass_{t:.2f}']=int(mx>=t-1e-12)
    rec[f'equalweight_pass_but_not_allmissions_{t:.2f}']=int(eq>=t-1e-12 and mn<t-1e-12)
    rec[f'visitor_pass_but_not_allmissions_{t:.2f}']=int(visitor>=t-1e-12 and mn<t-1e-12)
    for eps in weight_floors:
     lo=rec[f'robust_lower_wfloor_{eps:.2f}'];hi=rec[f'robust_upper_wfloor_{eps:.2f}']
     state='GREEN_ALL_ADMISSIBLE_WEIGHTS' if lo>=t-1e-12 else ('RED_ALL_ADMISSIBLE_WEIGHTS' if hi<t-1e-12 else 'AMBER_WEIGHT_DEPENDENT')
     rec[f'robust_state_t{t:.2f}_wfloor{eps:.2f}']=state
   long.append(rec)
# save long
fields=list(dict.fromkeys(k for r in long for k in r))
with (out/'UK_DCMS_museum_year_robust_warning_vs_equalweight_VISITOR_benchmark_v1.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(long)
# summarize per dimension set
summary={}
for label in ('core4','core5'):
 rr=[r for r in long if r['dimension_set']==label]
 info={'museum_years':len(rr),'museums':len({r['museum_group'] for r in rr}),
  'mean_equalweight_masking_span':round(statistics.mean(r['threshold_free_equalweight_masking_span'] for r in rr),4),
  'median_equalweight_masking_span':round(statistics.median(r['threshold_free_equalweight_masking_span'] for r in rr),4),
  'mean_visitor_masking_span':round(statistics.mean(r['threshold_free_visitor_masking_span'] for r in rr),4),
  'median_visitor_masking_span':round(statistics.median(r['threshold_free_visitor_masking_span'] for r in rr),4),
  'bottleneck_counts':dict(collections.Counter(x for r in rr for x in r['bottleneck_missions_pipe'].split('|') if x))}
 for eps in weight_floors:
  info[f'mean_uncertainty_width_wfloor_{eps:.2f}']=round(statistics.mean(r[f'uncertainty_width_wfloor_{eps:.2f}'] for r in rr),4)
  info[f'median_equalweight_minus_lower_wfloor_{eps:.2f}']=round(statistics.median(r[f'equalweight_minus_lower_wfloor_{eps:.2f}'] for r in rr),4)
 for t in thresholds:
  info[f't{t:.2f}_equalweight_pass_count']=sum(r[f'equalweight_pass_{t:.2f}'] for r in rr)
  info[f't{t:.2f}_allmissions_pass_count']=sum(r[f'all_missions_pass_{t:.2f}'] for r in rr)
  info[f't{t:.2f}_equalweight_masking_count']=sum(r[f'equalweight_pass_but_not_allmissions_{t:.2f}'] for r in rr)
  info[f't{t:.2f}_visitor_masking_count']=sum(r[f'visitor_pass_but_not_allmissions_{t:.2f}'] for r in rr)
  for eps in weight_floors:
   states=collections.Counter(r[f'robust_state_t{t:.2f}_wfloor{eps:.2f}'] for r in rr)
   info[f't{t:.2f}_wfloor{eps:.2f}_states']=dict(states)
 summary[label]=info
 print('BENCHMARK_SUMMARY',label,json.dumps(info,ensure_ascii=False),flush=True)
# recovery declaration timing by museum, threshold
timing=[]
for label in ('core4','core5'):
 for name in sorted({r['museum_group'] for r in long if r['dimension_set']==label}):
  rr=sorted([r for r in long if r['dimension_set']==label and r['museum_group']==name],key=lambda x:x['FY_start'])
  for t in (0.80,0.90,1.00):
   def first(field):
    ys=[r['FY_start'] for r in rr if r[field]==1]
    return min(ys) if ys else ''
   row={'dimension_set':label,'museum_group':name,'threshold':t,
    'first_FYstart_equalweight_pass':first(f'equalweight_pass_{t:.2f}'),
    'first_FYstart_visitor_pass':first(f'visitor_pass_{t:.2f}'),
    'first_FYstart_allmissions_pass':first(f'all_missions_pass_{t:.2f}')}
   a=row['first_FYstart_equalweight_pass'];b=row['first_FYstart_allmissions_pass']
   row['equalweight_lead_years_vs_allmissions']='' if a=='' or b=='' else b-a
   row['equalweight_ever_pass_but_allmissions_never_pass']=int(a!='' and b=='')
   timing.append(row)
with (out/'UK_DCMS_recovery_declaration_timing_equalweight_vs_allmissions_v1.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(timing[0]));w.writeheader();w.writerows(timing)
qa={'model':'Exact admissible-weight score envelope for capped mission recovery attainments. W_epsilon={w_k>=epsilon, sum w=1}. Equal-weight and visitor-only are benchmark summaries, not ground truth.',
 'weight_floors':weight_floors,'thresholds':thresholds,
 'threshold_free_key':'For any pass threshold tau between worst_mission and equal_weight score, equal-weight declares pass while at least one mission does not. Span=equal_weight-min mission exactly measures this masking threshold interval without selecting tau.',
 'threshold_grid_key':'0.75/0.80/0.90/1.00 are transparent sensitivity thresholds, not empirically optimized cutoffs. Primary claim should use threshold-free spans and complete mission vectors.',
 'state_def':'GREEN iff every admissible weighted score >= threshold; RED iff every admissible weighted score < threshold; AMBER otherwise. Under epsilon=0, lower=min mission and upper=max mission.',
 'no_accuracy_claim':'There is no externally adjudicated true early-warning label in the DCMS source. Therefore results measure aggregation information loss/stability, NOT predictive accuracy, false-negative rate, sensitivity or specificity.',
 'summary':summary}
(out/'UK_DCMS_robust_warning_vs_equalweight_benchmark_QA_v1.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8')
print('ALL_MUSEUM_YEAR_CASES',len(long),'TIMING_ROWS',len(timing),flush=True)
