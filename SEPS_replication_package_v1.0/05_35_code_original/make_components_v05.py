# -*- coding: utf-8 -*-
import sys, docx, re
sys.stdout.reconfigure(encoding='utf-8')
S34 = r'G:\我的云端硬盘\艺术计算研究｜Cities+SEPS SSCI投稿｜2026-10\05_阶段审计与城市匹配\34_SEPS_manuscript_prototype_and_internal_desk_reject_v1'
OUT = r'D:\seps_fig_work\ms'
HL = ['Official DCMS data show uneven recovery across five museum service missions.',
      'Total visits are rarely the weakest mission; youth learning and loans lag.',
      'Equal weighting hides weakest-mission gaps even in pre-pandemic years.',
      'Set-valued monitoring separates robust from priority-dependent conclusions.',
      'Late recovery is marked by deeper shortfalls, not only wider mission gaps.']
for h in HL: assert len(h) <= 85, (len(h), h)
D = docx.Document(); D.add_paragraph().add_run('Highlights').bold = True
for h in HL: D.add_paragraph(h, style='List Bullet')
D.save(OUT + r'\SEPS_highlights_v0.5.docx')
md = open(S34 + r'\SEPS_submission_components_v0.3.md', encoding='utf-8').read()
md = md.replace('# SEPS submission components v0.3', '# SEPS submission components v0.5').replace(
    'Status: submission-preparation draft; author declarations still require confirmation.',
    'Status: submission-preparation draft aligned with manuscript v0.5; author declarations still require confirmation.')
old_hl = md.split('## Highlights')[1].split('## Keywords')[0]
md = md.replace(old_hl, '\n' + '\n'.join('- ' + h for h in HL) + '\n\n')
old_ai = md.split('## Generative AI and AI-assisted technologies disclosure')[1].split('## CRediT')[0]
new_ai = (' — factual draft for author confirmation\nDuring the preparation of this work, the author(s) used OpenAI ChatGPT and Anthropic Claude to assist with '
          'manuscript drafting and language editing, literature organisation, the generation and debugging of reproducible analysis and '
          'figure scripts, and the drafting of figure captions. All source selection, variable definitions, analytical decisions (including the '
          'pre-specified horizon-matched check), code execution, numerical verification, interpretation and final manuscript content were reviewed '
          'by the author(s), who take full responsibility for the work. No generative image tool was used: all figures are drawn by code from the '
          'cited data.\n[AUTHOR MUST CONFIRM this wording against the final submitted workflow and the Elsevier policy shown in the live submission system.]\n\n')
md = md.replace(old_ai, new_ai)
md = md.replace('Reproducible analysis code, derived tables and source-audit metadata are maintained in the project archive.',
                'Reproducible analysis code, derived tables, source-audit metadata and figure-geography provenance (GLA, ONS, OpenStreetMap, Wikidata) are maintained in the project archive.')
open(OUT + r'\SEPS_submission_components_v0.5.md', 'w', encoding='utf-8').write(md)
print('ok', [len(h) for h in HL])
