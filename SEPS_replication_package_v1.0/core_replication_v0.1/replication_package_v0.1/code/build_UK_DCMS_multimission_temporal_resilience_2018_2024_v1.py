#!/usr/bin/env python3
"""Temporal mission resilience from official pre-pandemic FY2018/19 baseline through FY2020/21–FY2024/25.
Descriptive public-service recovery, not causal funding productivity.
"""
from pathlib import Path
import csv,json,math,statistics
import numpy as np
from scipy.optimize import linprog
root=next(q for p in Path('G:/').iterdir() if p.is_dir() for q in p.iterdir() if q.is_dir() and 'Cities+SEPS' in q.name)
stage=next(root.glob('05_*'));src=stage/'31_UK_DCMS_museum_site_finance_visits_same_institution_open_2024_25_screen_v1';out=stage/'32_UK_DCMS_definition_breaks_multioutput_novelty_model_screen_v1'
with (src/'UK_DCMS_15_museums_FY2008_2024_annual_GIA_visits_and_outputs_official_ODS_join_v1.csv').open(encoding='utf-8-sig') as f:panel=list(csv.DictReader(f))
loanqa=json.loads((out/'UK_DCMS_Table9_loanvenue_2023_25_header_source_discrepancy_QA_v1.json').read_text(encoding='utf-8'))
def canon(x):
 import re
 x=re.sub(r'\s*\[Note[^]]*\]','',x).strip()
 return {'Imperial War Museums':'Imperial War Museum','Tate Gallery Group':'Tate Gallery'}.get(x,x)
loan24={canon(x['source_name']):x['numeric'] for x in loanqa['institution_rows'] if x['numeric'] is not None}
idx={(r['museum_group'],int(r['year_start'])):r for r in panel}
missions=[('visitors_total_actual','total_visits'),('under16_visits','under16'),('formal_education_under18_visits','formal_education'),('organized_on_site_under18_participations','onsite_U18'),('UK_loan_venues','UK_loan_venues')]
years=[2020,2021,2022,2023,2024]
names=sorted({r['museum_group'] for r in panel if r['museum_group']!='Museum of the Home'})
def get(name,y,key):
 if key=='UK_loan_venues' and y==2024:return loan24.get(name)
 x=idx[(name,y)].get(key,'')
 try:return float(x)
 except:return None
records=[]
for name in names:
 row={'museum_group':name,'baseline_FY':'2018/19','postshock_years':'2020/21|2021/22|2022/23|2023/24|2024/25',
  'Museum_of_Home_excluded_per_DCMS_comparator':'YES'}
 for key,label in missions:
  base=get(name,2018,key)
  vals=[get(name,y,key) for y in years]
  ratio=[v/base if v is not None and base is not None and base>0 else None for v in vals]
  cap=[min(r,1.0) if r is not None and r>=0 else None for r in ratio]
  row[label+'_baseline_2018']=base if base is not None else ''
  row[label+'_postshock_raw_values_pipe']='|'.join('' if v is None else str(v) for v in vals)
  row[label+'_postshock_recovery_ratio_pipe']='|'.join('' if v is None else f'{v:.6f}' for v in ratio)
  row[label+'_shock_retention_2020_21']=round(ratio[0],6) if ratio[0] is not None else ''
  row[label+'_endpoint_recovery_2024_25']=round(ratio[-1],6) if ratio[-1] is not None else ''
  row[label+'_temporal_resilience_AUC_mean_capped']=round(sum(cap)/len(cap),6) if all(v is not None for v in cap) else ''
  eligible=[years[i] for i,r in enumerate(ratio) if r is not None and years[i]>=2021 and r>=0.9]
  row[label+'_first_FYstart_reach_90pct_baseline']=min(eligible) if eligible else ''
  row[label+'_postshock_years_below_90pct']=sum(r is not None and r<0.9 for r in ratio)
  row[label+'_trajectory_complete_5years']=int(all(v is not None for v in ratio))
 records.append(row)
# weight-free robust temporal resilience over AUC mission dimensions
def robust(dimlabels):
 eligible=[r for r in records if all(isinstance(r.get(x+'_temporal_resilience_AUC_mean_capped'),float) for x in dimlabels)]
 A=np.array([[r[x+'_temporal_resilience_AUC_mean_capped'] for x in dimlabels] for r in eligible],float)
 n,k=A.shape;outrows=[]
 dom=np.zeros((n,n),bool)
 for i in range(n):
  for j in range(n):
   if i!=j:dom[i,j]=np.all(A[i]>=A[j]-1e-12) and np.any(A[i]>A[j]+1e-12)
 for i,r in enumerate(eligible):
  # possible top and maximum strict margin across all policy weights
  Aub=[];b=[]
  for j in range(n):
   if i==j:continue
   Aub.append(np.r_[-(A[i]-A[j]),1]);b.append(0.)
  rr=linprog(np.r_[np.zeros(k),-1],A_ub=np.array(Aub),b_ub=np.array(b),A_eq=np.array([np.r_[np.ones(k),0]]),b_eq=[1],
    bounds=[(0,1)]*k+[(-2,2)],method='highs')
  rr0=linprog(np.zeros(k),A_ub=np.array([-(A[i]-A[j]) for j in range(n) if i!=j]),b_ub=np.zeros(n-1),A_eq=np.ones((1,k)),b_eq=[1],bounds=[(0,1)]*k,method='highs')
  outrows.append({'museum_group':r['museum_group'],'n_missions':k,'mission_AUC_pipe':'|'.join(f'{x:.6f}' for x in A[i]),
    'weakest_mission_temporal_resilience':round(float(A[i].min()),6),
    'mean_mission_temporal_resilience_DIAGNOSTIC':round(float(A[i].mean()),6),
    'Pareto_nondominated':int(dom[:,i].sum()==0),'Pareto_dominates_n':int(dom[i].sum()),'Pareto_dominated_by_n':int(dom[:,i].sum()),
    'possible_top_some_weights':int(rr0.success),'strict_top_possible':int(rr.x[-1]>1e-8),'max_strict_margin':round(float(rr.x[-1]),8),
    'witness_weights_pipe':'|'.join(f'{x:.6f}' for x in rr.x[:k])})
 return eligible,outrows
summary={}
for label,dims in [('core4',['total_visits','under16','formal_education','onsite_U18']),('core5',['total_visits','under16','formal_education','onsite_U18','UK_loan_venues'])]:
 eligible,r=robust(dims)
 with (out/f'UK_DCMS_temporal_resilience_weight_free_{label}_v1.csv').open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(r[0]));w.writeheader();w.writerows(r)
 summary[label]={'missions':dims,'complete_museums':len(r),'names':[x['museum_group'] for x in r],
  'Pareto_nondominated':sum(x['Pareto_nondominated'] for x in r),'possible_top':sum(x['possible_top_some_weights'] for x in r),
  'strict_top_possible':sum(x['strict_top_possible'] for x in r),
  'median_weakest_mission_temporal_resilience':round(statistics.median(x['weakest_mission_temporal_resilience'] for x in r),4)}
 print('TEMPORAL_ROBUST',label,json.dumps(summary[label],ensure_ascii=False),flush=True)
fields=list(dict.fromkeys(k for r in records for k in r))
with (out/'UK_DCMS_14group_mission_temporal_resilience_trajectories_FY2020_2024_v1.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(records)
qa={'definition':'For each mission, baseline=FY2018/19. Post-shock window is FY2020/21 through FY2024/25. Annual attainment=min(output_t/baseline,1). Temporal resilience AUC is arithmetic mean of the 5 annual attainments; each financial year equally weighted in time, while mission priorities remain unspecified.',
 'source_comparability':'Museum of the Home excluded following DCMS official pre-pandemic comparison note. National Portrait Gallery source x creates incomplete core trajectories and is excluded only from complete-case robust temporal MCDA. Loan FY2024/25 restored from audited Table9 last-column source discrepancy.',
 'summary':summary,
 'limits':['AUC is a monitoring descriptor, not welfare, technical efficiency, or causal effect.','Zero values reported in original source are preserved as real zero where numeric; x/w remain missing.','Recovery to baseline is capped at one to prevent overshoot in one year/mission compensating service shortfall when measuring restoration.','Equal time-year weights are a transparent resilience convention and must be sensitivity-tested if used in a paper.']}
(out/'UK_DCMS_temporal_multimission_resilience_definition_AND_QA_v1.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8')
