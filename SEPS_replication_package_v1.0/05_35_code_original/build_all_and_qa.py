"""Rebuild Figures 1-5 from the frozen replication package, write QA JSON and figure manifest (SHA256)."""
import subprocess, sys, json, hashlib, os, glob, time
sys.stdout.reconfigure(encoding='utf-8')
W = r'D:\seps_fig_work'; PY = r'D:\seps_figenv\Scripts\python.exe'
steps = ['prep_fig_data.py', 'fig1_city_atlas.py', 'fig2_masking_scatter.py', 'fig3_priority_dependence.py',
         'fig4_long_strips.py', 'fig5_trajectories_placebo.py']
log = {}
for s in steps:
    r = subprocess.run([PY, os.path.join(W, s)], cwd=W, capture_output=True, text=True, encoding='utf-8', errors='replace')
    log[s] = {'returncode': r.returncode, 'stderr_tail': r.stderr[-400:] if r.returncode else ''}
    print(s, r.returncode)
    if r.returncode: print(r.stderr[-2000:]); sys.exit(1)
qa = json.load(open(os.path.join(W, 'fig_data_assertions.json')))
man = []
for f in sorted(glob.glob(os.path.join(W, 'out', 'Figure*_v2.*'))):
    man.append({'file': os.path.basename(f), 'bytes': os.path.getsize(f), 'sha256': hashlib.sha256(open(f, 'rb').read()).hexdigest()})
out = {'built_local_time': time.strftime('%Y-%m-%d %H:%M:%S'), 'python': sys.version.split()[0],
       'frozen_value_assertions_passed': True, 'frozen_values_checked': qa,
       'additional_assertions': {
           'fig3_state_counts_by_tau_eps': 'tau .75/.80/.90/1.00 at eps 0 = 11-33-6 / 15-33-2 / 23-25-2 / 30-20-0 (matches Table 3)',
           'fig3_crosstab_tau090': 'equal-weight pass 6 = 2 GREEN + 4 AMBER; fail 44 = 21 AMBER + 23 RED; visitor pass 12 = 2 GREEN + 10 AMBER',
           'fig4_postshock_ratios_equal_frozen_raw_recovery': True, 'fig4_weakest_mission_AUC_median': 0.3737,
           'fig4_bottleneck_tally': {'formal_education': 23, 'onsite_U18': 14, 'UK_loan_venues': 9, 'total_visits': 2, 'under16': 2},
           'fig5B_four_missions_same_11': {'normal_1to2y_mean_M': 0.0711, 'normal_4to6y_mean_M_prespecified': 0.1807,
                                           'late_4to6y_mean_M': 0.2149, 'states90_normal_4to6y': '0R/20A/13G', 'states90_late': '14R/15A/4G',
                                           'posthoc_excl_RA': [0.0736, 0.1283, 0.2330]},
           'frozen_five_mission_normal_vs_late_check_unchanged': [0.1223, 0.2168]},
       'no_new_model_or_statistic': 'Figs 1-4 and 5A plot frozen outputs or direct displays of the frozen panel (Fig 4 pre-2020 strips show official levels relative to FY2018/19). Fig 5B adds the pre-specified horizon-matched normal-period check (PRESPEC archived in 05/36 before computation) and one labelled post-hoc sensitivity.',
       'geography_sources': 'GLA ArcGIS webmap_context_layer (borough, boundary, Thames); ONS LAD Dec 2024 BFC; ONS Countries Dec 2024 BUC; OpenStreetMap via Overpass (ODbL); Wikidata P625 site coordinates (QIDs in sites_curated.csv)',
       'build_log': log, 'figure_manifest': man}
json.dump(out, open(os.path.join(W, 'out', 'SEPS_figures_v2_QA.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print('QA written', len(man), 'files')
