# -*- coding: utf-8 -*-
"""Execute PRESPEC_horizon_matched_normal_period_v1.json exactly as written; plus bottleneck split by window."""
import sys, json, numpy as np, pandas as pd
sys.stdout.reconfigure(encoding='utf-8')
REP = r'G:\我的云端硬盘\艺术计算研究｜Cities+SEPS SSCI投稿｜2026-10\05_阶段审计与城市匹配\34_SEPS_manuscript_prototype_and_internal_desk_reject_v1\replication_package_v0.1'
OUT = r'D:\seps_fig_work\horizon'
p = pd.read_csv(REP + r'\data\UK_DCMS_15_museums_FY2008_2024_annual_GIA_visits_and_outputs_official_ODS_join_v1.csv')
COL = {'total_visits': 'visitors_total_actual', 'under16': 'under16_visits', 'formal_education': 'formal_education_under18_visits',
       'onsite_U18': 'organized_on_site_under18_participations'}
M = list(COL)
V = {m: p.pivot(index='museum_group', columns='year_start', values=c).apply(pd.to_numeric, errors='coerce') for m, c in COL.items()}
FLAG12 = {'Horniman Museum', 'National Portrait Gallery', "Sir John Soane's Museum"}; FLAG13 = {'Horniman Museum', 'National Portrait Gallery'}
def window(g, base, outs):
    rows = []
    for y in outs:
        a = []
        for m in M:
            b, v = V[m].loc[g, base], V[m].loc[g, y]
            if not (pd.notna(b) and b > 0 and pd.notna(v)): return None
            a.append(min(v / b, 1.0))
        a = np.array(a); E = a.mean()
        st = 'GREEN' if a.min() >= 0.9 else ('RED' if a.max() < 0.9 else 'AMBER')
        rows.append({'museum_group': g, 'baseline': base, 'outcome': y, 'horizon': y - base, 'attainment_pipe': '|'.join(f'{x:.6f}' for x in a),
                     'equalweight': E, 'weakest': a.min(), 'masking': E - a.min(), 'state90': st,
                     'bottleneck': M[int(a.argmin())]})
    return rows
def run(name, nb, nouts, lb, louts, exclude):
    groups = [g for g in V['total_visits'].index if g != 'Museum of the Home' and g not in exclude]
    R = []
    for g in groups:
        n, l = window(g, nb, nouts), window(g, lb, louts)
        if n is None or l is None: continue
        for r in n: r['period'] = 'normal'
        for r in l: r['period'] = 'late'
        R += n + l
    df = pd.DataFrame(R); df['spec'] = name
    s = df.groupby('period').agg(museum_years=('masking', 'size'), museums=('museum_group', 'nunique'), mean_M=('masking', 'mean'),
                                 median_M=('masking', 'median'), mean_E=('equalweight', 'mean'), mean_min=('weakest', 'mean'))
    st = df.groupby(['period', 'state90']).size().unstack(fill_value=0)
    pm = df.groupby(['museum_group', 'period']).masking.mean().unstack()
    out = {'spec': name, 'museums': sorted(df.museum_group.unique()),
           'normal': {**{k: (round(float(v), 4) if isinstance(v, float) else int(v)) for k, v in s.loc['normal'].items()}, 'states90': st.loc['normal'].to_dict()},
           'late': {**{k: (round(float(v), 4) if isinstance(v, float) else int(v)) for k, v in s.loc['late'].items()}, 'states90': st.loc['late'].to_dict()},
           'R_mean_late_over_normal': round(float(s.loc['late', 'mean_M'] / s.loc['normal', 'mean_M']), 3),
           'museums_late_higher': int((pm.late > pm.normal).sum()), 'museums_total': int(len(pm)),
           'bottleneck_counts': {per: df[df.period == per].bottleneck.value_counts().to_dict() for per in ['normal', 'late']}}
    return df, out
res, frames = {}, []
for name, nb, nouts, lb, louts, exc in [
        ('PRIMARY_4to6y', 2012, [2016, 2017, 2018], 2018, [2022, 2023, 2024], FLAG12),
        ('S1_4to5y_base2013', 2013, [2017, 2018], 2018, [2022, 2023], FLAG13),
        ('S2_primary_incl_flagged', 2012, [2016, 2017, 2018], 2018, [2022, 2023, 2024], set()),
        ('S3_short_1to2y_reference', 2016, [2017, 2018], 2018, [2022, 2023, 2024], FLAG12)]:
    df, o = run(name, nb, nouts, lb, louts, exc); res[name] = o; frames.append(df)
    print(json.dumps(o, indent=1, ensure_ascii=False))
pd.concat(frames).to_csv(OUT + r'\horizon_matched_museum_year_detail_v1.csv', index=False)
R = res['PRIMARY_4to6y']['R_mean_late_over_normal']
verdict = ('R>=1.5: retain claim with horizon-matched figures' if R >= 1.5 else
           ('1.0<R<1.5: soften claim; part of original contrast reflects horizon' if R > 1.0 else 'R<=1.0: drop doubling claim'))
res['PRESPEC_decision'] = {'R_primary': R, 'verdict': verdict}
# bottleneck split in frozen 50 museum-years (five missions)
b = pd.read_csv(REP + r'\data\UK_DCMS_museum_year_robust_warning_vs_equalweight_VISITOR_benchmark_v1.csv')
b = b[b.dimension_set == 'core5'].copy(); b['bn'] = b.bottleneck_missions_pipe.str.split('|').str[0]
b['window'] = np.where(b.FY_start <= 2021, 'shutdown_FY2020_21_to_2021_22', 'later_FY2022_23_to_2024_25')
split = b.groupby('window').bn.value_counts().unstack(fill_value=0)
res['bottleneck_split_core5'] = {w: split.loc[w].to_dict() for w in split.index}
res['bottleneck_split_core5_by_year'] = b.groupby('FY_start').bn.value_counts().unstack(fill_value=0).to_dict(orient='index')
print(split.to_string()); print(res['PRESPEC_decision'])
json.dump(res, open(OUT + r'\horizon_matched_RESULTS_v1.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False, default=int)
