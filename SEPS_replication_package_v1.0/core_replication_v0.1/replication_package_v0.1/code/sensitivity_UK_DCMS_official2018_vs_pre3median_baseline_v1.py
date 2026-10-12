#!/usr/bin/env python3
"""Sensitivity of mission-resilience warning to official FY2018/19 baseline vs median FY2016/17-2018/19.
No significance selection; same source-comparable museum cohort and mission definitions.
"""
from pathlib import Path
import csv,json,math,statistics,collections,re
import numpy as np
root=next(q for p in Path('G:/').iterdir() if p.is_dir() for q in p.iterdir() if q.is_dir() and 'Cities+SEPS' in q.name)
stage=next(root.glob('05_*'))
src=stage/'31_UK_DCMS_museum_site_finance_visits_same_institution_open_2024_25_screen_v1'
s32=stage/'32_UK_DCMS_definition_breaks_multioutput_novelty_model_screen_v1'
out=stage/'33_UK_DCMS_robust_early_warning_benchmark_vs_equal_weight_v1'
with (src/'UK_DCMS_15_museums_FY2008_2024_annual_GIA_visits_and_outputs_official_ODS_join_v1.csv').open(encoding='utf-8-sig') as f:panel=list(csv.DictReader(f))
loanqa=json.loads((s32/'UK_DCMS_Table9_loanvenue_2023_25_header_source_discrepancy_QA_v1.json').read_text(encoding='utf-8'))
def canon(x):
 x=re.sub(r'\s*\[Note[^]]*\]','',x).strip()
 return {'Imperial War Museums':'Imperial War Museum','Tate Gallery Group':'Tate Gallery'}.get(x,x)
loan24={canon(x['source_name']):x['numeric'] for x in loanqa['institution_rows'] if x['numeric'] is not None}
idx={(r['museum_group'],int(r['year_start'])):r for r in panel}
missions=['visitors_total_actual','under16_visits','formal_education_under18_visits','organized_on_site_under18_participations','UK_loan_venues']
years=[2020,2021,2022,2023,2024]
names=sorted({r['museum_group'] for r in panel if r['museum_group']!='Museum of the Home'})
def get(name,y,key):
 if key=='UK_loan_venues' and y==2024:return loan24.get(name)
 try:return float(idx[(name,y)].get(key,''))
 except:return None
def baseval(name,key,kind):
 if kind=='official2018':return get(name,2018,key)
 vals=[get(name,y,key) for y in (2016,2017,2018)]
 if any(v is None for v in vals):return None
 return statistics.median(vals)
records=[]
for name in names:
 for bkind in ('official2018','pre3median_2016_2018'):
  bas=[baseval(name,k,bkind) for k in missions]
  paths=[[get(name,y,k) for y in years] for k in missions]
  if any(x is None or x<=0 for x in bas) or any(v is None for p in paths for v in p):continue
  endpoint=np.array([min(paths[j][-1]/bas[j],1.0) for j in range(5)],float)
  auc=np.array([statistics.mean(min(v/bas[j],1.0) for v in paths[j]) for j in range(5)],float)
  records.append({'museum_group':name,'baseline_kind':bkind,
   'endpoint_attainment_pipe':'|'.join(f'{x:.6f}' for x in endpoint),
   'temporal_AUC_pipe':'|'.join(f'{x:.6f}' for x in auc),
   'endpoint_equalweight':round(float(endpoint.mean()),8),'endpoint_min':round(float(endpoint.min()),8),
   'endpoint_masking_span':round(float(endpoint.mean()-endpoint.min()),8),
   'temporal_equalweight':round(float(auc.mean()),8),'temporal_min':round(float(auc.min()),8),
   'temporal_masking_span':round(float(auc.mean()-auc.min()),8),
   'endpoint_allmissions_ge_090':int(endpoint.min()>=0.9-1e-12),
   'temporal_allmissions_AUC_ge_075':int(auc.min()>=0.75-1e-12)})
# paired museums common both baseline defs
with (out/'UK_DCMS_core5_baseline_sensitivity_official2018_vs_pre3median_v1.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
pairs=collections.defaultdict(dict)
for r in records:pairs[r['museum_group']][r['baseline_kind']]=r
pairs={k:v for k,v in pairs.items() if len(v)==2}
def vec(r,field):return np.array([float(x) for x in r[field].split('|')])
endpoint_corr=[];auc_corr=[];status_changes=[]
for name,p in pairs.items():
 a=p['official2018'];b=p['pre3median_2016_2018']
 endpoint_corr.extend(zip(vec(a,'endpoint_attainment_pipe'),vec(b,'endpoint_attainment_pipe')))
 auc_corr.extend(zip(vec(a,'temporal_AUC_pipe'),vec(b,'temporal_AUC_pipe')))
 if a['endpoint_allmissions_ge_090']!=b['endpoint_allmissions_ge_090'] or a['temporal_allmissions_AUC_ge_075']!=b['temporal_allmissions_AUC_ge_075']:
  status_changes.append({'museum_group':name,'official_endpoint_green90':a['endpoint_allmissions_ge_090'],
   'pre3_endpoint_green90':b['endpoint_allmissions_ge_090'],'official_temporal_green75':a['temporal_allmissions_AUC_ge_075'],
   'pre3_temporal_green75':b['temporal_allmissions_AUC_ge_075']})
x=np.array([a for a,b in endpoint_corr]);y=np.array([b for a,b in endpoint_corr])
xa=np.array([a for a,b in auc_corr]);ya=np.array([b for a,b in auc_corr])
qa={'paired_complete_museums':len(pairs),'museum_names':sorted(pairs),
 'baseline_A':'Official DCMS headline comparator FY2018/19.',
 'baseline_B':'Sensitivity only: per-museum per-mission median of FY2016/17,FY2017/18,FY2018/19; chosen before looking at outcomes to reduce single-year baseline noise and remain after UK-loan comparability break.',
 'endpoint_attainment_cell_Pearson':round(float(np.corrcoef(x,y)[0,1]),4),
 'temporal_AUC_cell_Pearson':round(float(np.corrcoef(xa,ya)[0,1]),4),
 'endpoint_mean_absolute_difference':round(float(np.mean(np.abs(x-y))),4),
 'temporal_AUC_mean_absolute_difference':round(float(np.mean(np.abs(xa-ya))),4),
 'status_change_cases':status_changes,
 'mean_endpoint_masking_official2018':round(statistics.mean(v['official2018']['endpoint_masking_span'] for v in pairs.values()),4),
 'mean_endpoint_masking_pre3median':round(statistics.mean(v['pre3median_2016_2018']['endpoint_masking_span'] for v in pairs.values()),4),
 'mean_temporal_masking_official2018':round(statistics.mean(v['official2018']['temporal_masking_span'] for v in pairs.values()),4),
 'mean_temporal_masking_pre3median':round(statistics.mean(v['pre3median_2016_2018']['temporal_masking_span'] for v in pairs.values()),4),
 'guardrail':'No baseline selected by fit or p-value. Official FY2018/19 remains primary; pre-3-year median is robustness only. Correlations describe source sensitivity, not predictive validation.'}
(out/'UK_DCMS_baseline_choice_sensitivity_QA_v1.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8')
print('BASELINE_SENSITIVITY',json.dumps(qa,ensure_ascii=False),flush=True)
