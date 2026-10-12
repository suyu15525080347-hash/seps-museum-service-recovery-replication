#!/usr/bin/env python3
"""Build manuscript-facing tables entirely from audited stage31-34 outputs."""
from pathlib import Path
import csv,json,collections
root=next(q for p in Path('G:/').iterdir() if p.is_dir() for q in p.iterdir() if q.is_dir() and 'Cities+SEPS' in q.name)
stage=next(root.glob('05_*'));s31=stage/'31_UK_DCMS_museum_site_finance_visits_same_institution_open_2024_25_screen_v1';s32=stage/'32_UK_DCMS_definition_breaks_multioutput_novelty_model_screen_v1';s33=stage/'33_UK_DCMS_robust_early_warning_benchmark_vs_equal_weight_v1';out=stage/'34_SEPS_manuscript_prototype_and_internal_desk_reject_v1'
def read(path):
 with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
# Table 1 manually source-backed
t1=[
{'source_or_indicator':'DCMS Museum Performance ODS','coverage':'FY2008/09–FY2024/25','main_fields':'total visits; under16; overseas; formal education; organized U18; UK loan venues','main_comparability_issue':'COVID cautions; closures; overseas method break; education notes; loan-venue break pre-2016/17'},
{'source_or_indicator':'DCMS Cultural Organisation Income ODS','coverage':'FY2008/09–FY2024/25','main_fields':'Grant-in-Aid; fundraising incl. donated objects; total income','main_comparability_issue':'GIA accounting differs from museum accounts; COVID emergency support; Horniman timing allocation; revised historical cells'},
{'source_or_indicator':'HM Treasury GDP deflator June 2026','coverage':'financial-year series','main_fields':'GDP deflator, 2025/26=100','main_comparability_issue':'economy-wide deflator, not museum-specific cost index'},
{'source_or_indicator':'NAO financial resilience report','coverage':'published Mar 2026','main_fields':'sector finance; visitor comparison; anonymized risk counts; early-warning recommendations','main_comparability_issue':'named visitor-recovery six available; financial-risk category membership anonymized'},
{'source_or_indicator':'PAC report','coverage':'published Jun 2026','main_fields':'KPI weaknesses; Strategic Indicator Tool; taxpayer value/oversight','main_comparability_issue':'policy context, not museum-level validation labels'}]
with (out/'Table1_sources_definitions_and_comparability_v1.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(t1[0]));w.writeheader();w.writerows(t1)
# Table2 source-comparable endpoint by museum
x=read(s32/'UK_DCMS_14_comparable_museums_FY2018_19_FY2024_25_mission_recovery_SOURCE_AUDITED_v2.csv')
t2=[]
for r in x:
 t2.append({'museum_group':r['museum_group'],
 'visits_ratio':r['visitors_total_actual_recovery_ratio'],'under16_ratio':r['under16_visits_recovery_ratio'],
 'formal_education_ratio':r['formal_education_under18_visits_recovery_ratio'],
 'onsite_U18_ratio':r['organized_on_site_under18_participations_recovery_ratio'],
 'UK_loan_venues_ratio':r['UK_loan_venues_recovery_ratio'],
 'real_GIA_ratio':r['Grant_in_Aid_2024_25_constant_GBP_recovery_ratio'],
 'nonfinancial_mission_geomean':r['nonfinancial_mission_geomean_ratio'],
 'n_nonfinancial_valid':r['n_nonfinancial_missions_valid']})
with (out/'Table2_museum_endpoint_multimission_recovery_v1.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(t2[0]));w.writeheader();w.writerows(t2)
# Table3 benchmark summary
q=json.loads((s33/'UK_DCMS_robust_warning_vs_equalweight_benchmark_QA_v1.json').read_text(encoding='utf-8'))
rows=[]
for label in ('core4','core5'):
 z=q['summary'][label]
 for t in (0.75,0.80,0.90,1.00):
  st=z[f't{t:.2f}_wfloor0.00_states']
  rows.append({'dimension_set':label,'threshold':t,'museum_years':z['museum_years'],
   'mean_equalweight_masking_span':z['mean_equalweight_masking_span'],
   'mean_visitor_masking_span':z['mean_visitor_masking_span'],
   'equalweight_pass':z[f't{t:.2f}_equalweight_pass_count'],
   'all_missions_pass':z[f't{t:.2f}_allmissions_pass_count'],
   'equalweight_pass_but_not_all':z[f't{t:.2f}_equalweight_masking_count'],
   'visitor_pass_but_not_all':z[f't{t:.2f}_visitor_masking_count'],
   'robust_RED':st.get('RED_ALL_ADMISSIBLE_WEIGHTS',0),'robust_AMBER':st.get('AMBER_WEIGHT_DEPENDENT',0),'robust_GREEN':st.get('GREEN_ALL_ADMISSIBLE_WEIGHTS',0)})
with (out/'Table3_equalweight_visitor_vs_robust_warning_benchmark_v1.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
# Table4 robustness panel
loo=read(s33/'UK_DCMS_leave_one_mission_out_warning_robustness_summary_v1.csv')
cap=read(out/'UK_DCMS_recovery_cap_sensitivity_summary_v1.csv')
base=json.loads((s33/'UK_DCMS_baseline_choice_sensitivity_QA_v1.json').read_text(encoding='utf-8'))
place=json.loads((out/'UK_DCMS_preCOVID_vs_late_recovery_placebo_QA_v1.json').read_text(encoding='utf-8'))
t4=[]
for r in loo:t4.append({'robustness_family':'leave-one-mission-out','variant':r['variant'],'key_result':'mean masking span','value':r['mean_masking_span'],'secondary':f"mask90={r['masking_cases_t090']}"})
for r in cap:t4.append({'robustness_family':'recovery cap','variant':r['variant'],'key_result':'mean masking span','value':r['mean_equalweight_masking_span'],'secondary':f"mask90={r['masking_cases_t090']}"})
t4 += [
{'robustness_family':'baseline','variant':'endpoint cell correspondence','key_result':'Pearson correlation','value':base['endpoint_attainment_cell_Pearson'],'secondary':f"MAE={base['endpoint_mean_absolute_difference']}"},
{'robustness_family':'baseline','variant':'temporal AUC correspondence','key_result':'Pearson correlation','value':base['temporal_AUC_cell_Pearson'],'secondary':f"MAE={base['temporal_AUC_mean_absolute_difference']}"},
{'robustness_family':'normal-period placebo','variant':'pre-COVID normal','key_result':'mean masking span','value':place['summary']['normal_preCOVID']['mean_equalweight_masking_span'],'secondary':'FY2017/18-2018/19'},
{'robustness_family':'normal-period placebo','variant':'late recovery','key_result':'mean masking span','value':place['summary']['late_recovery']['mean_equalweight_masking_span'],'secondary':'FY2022/23-2024/25'}]
with (out/'Table4_robustness_and_placebo_summary_v1.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(t4[0]));w.writeheader();w.writerows(t4)
# Table5 literature merge
museum=read(s32/'UK_DCMS_museum_performance_direct_competitor_G4_matrix_v1.csv')
general=read(s33/'UK_DCMS_general_robust_composite_indicator_method_competitors_v1.csv')
t5=[]
for r in museum:t5.append({'literature_stream':'museum performance','year':r['year'],'study':r['study'],'venue':r['venue'],'doi':r['doi'],'method':r['method'],'boundary_for_this_paper':r['direct_overlap']})
for r in general:t5.append({'literature_stream':'robust composite indicators','year':r['year'],'study':r['study'],'venue':r['venue'],'doi':r['doi'],'method':r['method'],'boundary_for_this_paper':r['implication']})
with (out/'Table5_closest_prior_literature_and_nonoverlap_v1.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(t5[0]));w.writeheader();w.writerows(t5)
print('MANUSCRIPT_TABLES_WRITTEN',{'T1':len(t1),'T2':len(t2),'T3':len(rows),'T4':len(t4),'T5':len(t5)},flush=True)
