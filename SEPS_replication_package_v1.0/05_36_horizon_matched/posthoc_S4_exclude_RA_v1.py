# -*- coding: utf-8 -*-
"""POST-HOC sensitivity (not in pre-specification): exclude Royal Armouries, whose organised on-site U18 series falls
from 244,665 (FY2015/16) to 10,364 (FY2016/17), a 96% one-year drop while total visits fall 4%; this is consistent with an
undocumented reporting change. Reported alongside, never instead of, the pre-specified primary result."""
import json, sys, pandas as pd
sys.stdout.reconfigure(encoding='utf-8')
W = r'D:\seps_fig_work\horizon'
h = pd.read_csv(W + r'\horizon_matched_museum_year_detail_v1.csv')
res = json.load(open(W + r'\horizon_matched_RESULTS_v1.json', encoding='utf-8'))
out = {'label': 'S4_POSTHOC_exclude_Royal_Armouries', 'status': 'post hoc; not pre-specified',
       'reason': 'Royal Armouries organised on-site U18: 244,665 (FY2015/16) -> 10,364 (FY2016/17), -95.8% in one year; total visits 1,944,414 -> 1,870,534 (-3.8%).'}
for spec in ['PRIMARY_4to6y', 'S3_short_1to2y_reference']:
    x = h[(h.spec == spec) & (h.museum_group != 'Royal Armouries')]
    g = x.groupby('period')
    o = {per: {'museum_years': int(len(v)), 'mean_M': round(v.masking.mean(), 4), 'median_M': round(v.masking.median(), 4),
               'mean_weakest': round(v.weakest.mean(), 4), 'states90': v.state90.value_counts().to_dict()} for per, v in g}
    o['R_mean'] = round(o['late']['mean_M'] / o['normal']['mean_M'], 3); o['R_median'] = round(o['late']['median_M'] / o['normal']['median_M'], 3)
    pm = x.groupby(['museum_group', 'period']).masking.mean().unstack()
    o['museums_late_higher'] = f"{int((pm.late > pm.normal).sum())}/{len(pm)}"
    out[spec] = o
p = h[h.spec == 'PRIMARY_4to6y']
out['PRIMARY_median_R_all_11'] = round(p[p.period == 'late'].masking.median() / p[p.period == 'normal'].masking.median(), 3)
res['S4_POSTHOC_exclude_RA'] = out
json.dump(res, open(W + r'\horizon_matched_RESULTS_v1.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False, default=int)
print(json.dumps(out, indent=1, ensure_ascii=False))
