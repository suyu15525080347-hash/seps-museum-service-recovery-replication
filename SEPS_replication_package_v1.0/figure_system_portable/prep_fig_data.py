"""Build tidy figure data from the frozen replication package and assert frozen headline values."""
import os
import pandas as pd, numpy as np, json, sys
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8')
from seps_style import REP, WORK, MISSIONS
b = pd.read_csv(os.path.join(REP, 'data', 'UK_DCMS_museum_year_robust_warning_vs_equalweight_VISITOR_benchmark_v1.csv'))
c5 = b[b.dimension_set == 'core5'].copy()
att = c5.capped_attainment_pipe.str.split('|', expand=True).astype(float); att.columns = MISSIONS
raw = c5.raw_recovery_pipe.str.split('|', expand=True).astype(float); raw.columns = ['raw_' + m for m in MISSIONS]
c5 = pd.concat([c5.reset_index(drop=True), att.reset_index(drop=True), raw.reset_index(drop=True)], axis=1)
# --- assertions against frozen values (handoff section 3)
chk = {}
chk['n_museum_years'] = len(c5); assert len(c5) == 50 and c5.museum_group.nunique() == 10
chk['mask_eq_mean'] = round(c5.threshold_free_equalweight_masking_span.mean(), 4); assert chk['mask_eq_mean'] == 0.2299
chk['mask_eq_median'] = round(c5.threshold_free_equalweight_masking_span.median(), 4); assert chk['mask_eq_median'] == 0.2200
chk['mask_vis_mean'] = round(c5.threshold_free_visitor_masking_span.mean(), 4); assert chk['mask_vis_mean'] == 0.2407
chk['mask_vis_median'] = round(c5.threshold_free_visitor_masking_span.median(), 4); assert chk['mask_vis_median'] == 0.2447
cnt = Counter(); [cnt.update(s.split('|')) for s in c5.bottleneck_missions_pipe]
chk['bottleneck_counts'] = dict(cnt)
assert cnt == Counter({'formal_education': 23, 'onsite_U18': 14, 'UK_loan_venues': 9, 'total_visits': 2, 'under16': 2})
st = c5['robust_state_t0.90_wfloor0.00'].str.split('_').str[0].value_counts().to_dict(); chk['states_t090'] = st
assert st == {'AMBER': 25, 'RED': 23, 'GREEN': 2}
chk['eq_pass_090'] = int(c5['equalweight_pass_0.90'].sum()); chk['all_pass_090'] = int(c5['all_missions_pass_0.90'].sum())
assert (chk['eq_pass_090'], chk['all_pass_090']) == (6, 2)
# recompute equal weight / worst from attainment
assert np.allclose(c5[MISSIONS].mean(axis=1), c5.equal_weight_score, atol=2e-6)
assert np.allclose(c5[MISSIONS].min(axis=1), c5.worst_mission_score, atol=2e-6)
# --- real GIA ratio recomputed from official ODS join + HMT September 2026 deflators
p = pd.read_csv(os.path.join(REP, 'data', 'UK_DCMS_15_museums_FY2008_2024_annual_GIA_visits_and_outputs_official_ODS_join_v1.csv'))
D18, D24 = 76.2884, 96.7570
g = p[p.financial_year.isin(['2018/19', '2024/25'])].pivot(index='museum_group', columns='financial_year', values='Grant_in_Aid_GBP')
g['real_GIA_ratio'] = (g['2024/25'] / D24) / (g['2018/19'] / D18)
t2 = pd.read_csv(os.path.join(REP, 'outputs', 'Table2_museum_endpoint_multimission_recovery_v1.csv')).set_index('museum_group')
cmp = g.join(t2[['real_GIA_ratio']], rsuffix='_table2', how='inner')
assert np.allclose(cmp.real_GIA_ratio, cmp.real_GIA_ratio_table2, atol=5e-6), cmp
g14 = g.loc[t2.index]
chk['realGIA_aggregate_14'] = round((g14['2024/25'].sum() / D24) / (g14['2018/19'].sum() / D18), 6)
chk['realGIA_median_14'] = round(g14.real_GIA_ratio.median(), 6)
assert chk['realGIA_aggregate_14'] == 1.150174 and chk['realGIA_median_14'] == 1.060463, chk
c5 = c5.merge(g[['real_GIA_ratio']], left_on='museum_group', right_index=True, how='left')
c5.to_csv(os.path.join(WORK, 'fig_core5_tidy.csv'), index=False)
t2.join(g[['2018/19', '2024/25']]).to_csv(os.path.join(WORK, 'fig_table2_plus_gia.csv'))
json.dump(chk, open(os.path.join(WORK, 'fig_data_assertions.json'), 'w'), indent=1)
print(json.dumps(chk, indent=1))
print(c5[c5.FY_start == 2024][['museum_group', 'worst_mission_score', 'equal_weight_score', 'bottleneck_missions_pipe', 'real_GIA_ratio']].sort_values('worst_mission_score').to_string())
