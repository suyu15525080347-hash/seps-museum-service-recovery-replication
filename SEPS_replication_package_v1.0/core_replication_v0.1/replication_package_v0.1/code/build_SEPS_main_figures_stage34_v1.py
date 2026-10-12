#!/usr/bin/env python3
from pathlib import Path
import csv,json,shutil,math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=next(q for p in Path('G:/').iterdir() if p.is_dir() for q in p.iterdir() if q.is_dir() and 'Cities+SEPS' in q.name)
stage=next(root.glob('05_*'));s32=stage/'32_UK_DCMS_definition_breaks_multioutput_novelty_model_screen_v1';s33=stage/'33_UK_DCMS_robust_early_warning_benchmark_vs_equal_weight_v1';out=stage/'34_SEPS_manuscript_prototype_and_internal_desk_reject_v1'
# Fig1 source-comparable recovery vs latest real GIA
q=json.loads((s32/'UK_DCMS_14group_source_comparable_mission_recovery_QA_v2.json').read_text(encoding='utf-8'))
h=json.loads((out/'HMT_September2026_deflator_update_and_DCMS_realGIA_revision_QA_v1.json').read_text(encoding='utf-8'))
S=q['summary'];keys=['visitors_total_actual','under16_visits','formal_education_under18_visits','organized_on_site_under18_participations','UK_loan_venues'];labels=['Total visits','Under-16 visits','Formal education','On-site U18 activities','UK loan venues']
vals=[S[k]['weighted_or_sum_ratio'] for k in keys]+[h['source_comparable_14museum_real_GIA_2024_25_vs_2018_19_ratio_latest']]
labels+=['Real Grant-in-Aid']
fig,ax=plt.subplots(figsize=(9.7,5.4));bars=ax.bar(range(len(vals)),vals);ax.axhline(1,linewidth=1.3)
ax.set_xticks(range(len(labels)),labels,rotation=22,ha='right');ax.set_ylabel('FY2024/25 ÷ FY2018/19 ratio')
ax.set_title('Museum service recovery differs from real Grant-in-Aid context\nSource-comparable cohort; descriptive, not a funding effect')
for b,v in zip(bars,vals):ax.text(b.get_x()+b.get_width()/2,v+.015,f'{v:.2f}',ha='center',fontsize=9)
ax.set_ylim(0,1.28);ax.grid(axis='y',alpha=.2);fig.tight_layout()
f1=out/'Figure1_source_comparable_mission_recovery_vs_realGIA_v1.png';fig.savefig(f1,dpi=220,bbox_inches='tight');plt.close(fig)
# Figures 2-3 copy audited stage33
shutil.copy2(s33/'UK_DCMS_core5_equalweight_vs_weakestmission_warning_benchmark_v1.png',out/'Figure2_equalweight_vs_weakestmission_warning_benchmark_v1.png')
shutil.copy2(s33/'UK_DCMS_core5_robust_warning_state_counts_threshold_sensitivity_v1.png',out/'Figure3_robust_warning_state_threshold_sensitivity_v1.png')
# Figure4 temporal AUC heatmap
with (s32/'UK_DCMS_temporal_resilience_weight_free_core5_v1.csv').open(encoding='utf-8-sig') as fh:rows=list(csv.DictReader(fh))
dims=['Total visits','Under-16','Formal education','On-site U18','UK loan venues'];names=[r['museum_group'] for r in rows]
arr=np.array([[float(x) for x in r['mission_AUC_pipe'].split('|')] for r in rows])
fig,ax=plt.subplots(figsize=(9.4,6.4));im=ax.imshow(arr,aspect='auto',vmin=0,vmax=1)
ax.set_xticks(range(5),dims,rotation=20,ha='right');ax.set_yticks(range(len(names)),names)
ax.set_title('Five-year public-service recovery by mission\nMean capped attainment, FY2020/21–FY2024/25 relative to FY2018/19')
for i in range(arr.shape[0]):
 for j in range(arr.shape[1]):ax.text(j,i,f'{arr[i,j]:.2f}',ha='center',va='center',fontsize=8)
fig.colorbar(im,ax=ax,label='Five-year mission recovery AUC');fig.tight_layout()
f4=out/'Figure4_five_year_mission_temporal_resilience_AUC_v1.png';fig.savefig(f4,dpi=220,bbox_inches='tight');plt.close(fig)
files=[out/'Figure0_methods_schematic_UK_DCMS_robust_service_recovery_v1.png',f1,out/'Figure2_equalweight_vs_weakestmission_warning_benchmark_v1.png',out/'Figure3_robust_warning_state_threshold_sensitivity_v1.png',f4]
print('MAIN_FIGURES',[(x.name,x.stat().st_size) for x in files],flush=True)
