#!/usr/bin/env python3
"""Authoritative structural audit of DCMS 2024/25 ODS notes, break markers, source missing codes and multi-output balanced panels."""
from pathlib import Path
import zipfile,xml.etree.ElementTree as ET,re,json,csv,collections,statistics,math
root=next(q for p in Path('G:/').iterdir() if p.is_dir() for q in p.iterdir() if q.is_dir() and 'Cities+SEPS' in q.name)
stage=next(root.glob('05_*'))
srcdir=stage/'31_UK_DCMS_museum_site_finance_visits_same_institution_open_2024_25_screen_v1'
out=stage/'32_UK_DCMS_definition_breaks_multioutput_novelty_model_screen_v1'
out.mkdir(exist_ok=True)
ns={'table':'urn:oasis:names:tc:opendocument:xmlns:table:1.0','text':'urn:oasis:names:tc:opendocument:xmlns:text:1.0','office':'urn:oasis:names:tc:opendocument:xmlns:office:1.0'}
def parse_ods(path):
 with zipfile.ZipFile(path) as z:xml=z.read('content.xml')
 rootxml=ET.fromstring(xml);tabs={}
 for sheet in rootxml.findall('.//table:table',ns):
  name=sheet.get('{'+ns['table']+'}name');rows=[]
  for row in sheet.findall('table:table-row',ns):
   vals=[]
   for c in row:
    if not c.tag.endswith('table-cell') or c.tag.endswith('covered-table-cell'):continue
    txt=' '.join(''.join(p.itertext()) for p in c.findall('text:p',ns)).strip()
    if not txt:txt=c.get('{'+ns['office']+'}value','')
    rep=min(120,int(c.get('{'+ns['table']+'}number-columns-repeated','1')))
    vals.extend([txt]*rep)
   rows.append(vals)
  tabs[name]=rows
 return tabs
perf=parse_ods(srcdir/'UK_DCMS_2024_25_performance_OFFICIAL.ods')
inc=parse_ods(srcdir/'UK_DCMS_2024_25_income_OFFICIAL.ods')
# Exact notes sheets
notes={}
for kind,tabs in [('performance',perf),('income',inc)]:
 rows=tabs.get('Notes',[])
 entries=[]
 for i,row in enumerate(rows):
  if not row:continue
  vals=[x.strip() for x in row if str(x).strip()]
  if vals:entries.append({'xml_row_index':i,'cells':vals[:12]})
 notes[kind]=entries
 print('NOTES_COUNT',kind,len(entries),flush=True)
 for e in entries[:45]:print('NOTE',kind,e['xml_row_index'],str(e['cells']).encode('ascii','backslashreplace').decode('ascii')[:1800],flush=True)
# Tables and their headers, detect explicit b break markers and notes
table_inventory=[]
for kind,tabs in [('performance',perf),('income',inc)]:
 for tname,rows in tabs.items():
  if not tname.isdigit():continue
  title=next((row[0] for row in rows if row and row[0].strip()),'')
  hdr=None
  for i,row in enumerate(rows):
   if row and (row[0].strip().lower().startswith('name of ') or row[0].strip().lower().startswith('museum or gallery')):
    hdr=(i,row);break
  if hdr is None:
   # some tables may have another first column header
   for i,row in enumerate(rows):
    if row and any(re.match(r'^20\d\d',str(x).strip()) for x in row[1:25]):
     hdr=(i,row);break
  yearheaders=[]
  if hdr:
   for j,h in enumerate(hdr[1]):
    if re.match(r'^20\d\d',str(h).strip()):
     yearheaders.append({'column':j,'header':h,'has_break_b':'[b]' in h.lower()})
  table_inventory.append({'source':kind,'sheet':tname,'title':title,'header_row':hdr[0] if hdr else None,
   'year_headers':yearheaders,'break_year_headers':[x['header'] for x in yearheaders if x['has_break_b']]})
# Load generated panel
with (srcdir/'UK_DCMS_15_museums_FY2008_2024_annual_GIA_visits_and_outputs_official_ODS_join_v1.csv').open(encoding='utf-8-sig',newline='') as f:panel=list(csv.DictReader(f))
metrics=['Grant_in_Aid_GBP','visitors_total_actual','under16_visits','overseas_visits','formal_education_under18_visits','organized_on_site_under18_participations','UK_loan_venues']
def valid(v):
 try:return float(v)>=0
 except:return False
coverage={}
for m in metrics:
 byyear={}
 bymuseum={}
 for y in range(2008,2025):
  rows=[r for r in panel if int(r['year_start'])==y]
  byyear[str(y)]=sum(valid(r.get(m,'')) for r in rows)
 for name in sorted({r['museum_group'] for r in panel}):
  rows=[r for r in panel if r['museum_group']==name]
  bymuseum[name]=sum(valid(r.get(m,'')) for r in rows)
 coverage[m]={'valid_cells':sum(valid(r.get(m,'')) for r in panel),'by_year':byyear,'by_museum':bymuseum}
# balanced windows for multi-output subsets
subsets={
 'core_GIA_visits':['Grant_in_Aid_GBP','visitors_total_actual'],
 'broad_audience_GIA_visits_under16_overseas':['Grant_in_Aid_GBP','visitors_total_actual','under16_visits','overseas_visits'],
 'education_GIA_visits_formal_under18':['Grant_in_Aid_GBP','visitors_total_actual','formal_education_under18_visits'],
 'service_dispersion_GIA_visits_loanvenues':['Grant_in_Aid_GBP','visitors_total_actual','UK_loan_venues'],
 'five_output':['Grant_in_Aid_GBP','visitors_total_actual','under16_visits','overseas_visits','formal_education_under18_visits','UK_loan_venues']
}
windows=[]
museums=sorted({r['museum_group'] for r in panel})
for label,cols in subsets.items():
 for start in range(2008,2025):
  for end in range(start,2025):
   yrs=list(range(start,end+1))
   complete=[]
   for name in museums:
    ok=True
    for y in yrs:
     r=next(x for x in panel if x['museum_group']==name and int(x['year_start'])==y)
     if not all(valid(r.get(c,'')) for c in cols):ok=False;break
    if ok:complete.append(name)
   if len(yrs)>=3 and len(complete)>=8:
    windows.append({'subset':label,'start_FY':start,'end_FY':end,'n_years':len(yrs),'complete_museums':len(complete),
     'balanced_obs':len(yrs)*len(complete),'museum_names':complete})
best={}
for label in subsets:
 w=[x for x in windows if x['subset']==label]
 # prioritize obs then years then institutions
 best[label]=sorted(w,key=lambda x:(x['balanced_obs'],x['n_years'],x['complete_museums']),reverse=True)[:12]
 print('BEST_BALANCED',label,json.dumps(best[label][:5],ensure_ascii=False),flush=True)
# raw missing codes from *_raw_source_cell
rawcodes=collections.Counter()
for r in panel:
 for k,v in r.items():
  if k.endswith('_raw_source_cell') and str(v).strip().lower() in ('x','w','b','-','na','n/a',':','..'):
   rawcodes[(k,str(v).strip())]+=1
qa={'authoritative_notes':notes,'table_inventory':table_inventory,'coverage':coverage,
 'balanced_candidate_windows':best,'raw_missing_code_counts':{f'{k[0]}::{k[1]}':v for k,v in rawcodes.items()},
 'interpretation_guardrails':[
  'A [b] in an official column header indicates a documented break in series; do not fit an unqualified continuous level/trend over that boundary without design adjustment.',
  'x/w/- are source codes, not numeric zeros. Their exact semantics must be taken from the source Notes before use.',
  'Museum group may cover multiple physical sites. Institution-year outputs are not neighborhood-level service coverage.',
  'A balanced-window choice based on missingness is a data-quality decision, not optimization for statistical significance.'
 ]}
(out/'UK_DCMS_ODS_notes_breaks_balanced_multioutput_AUDIT_v1.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8')
# compact window CSV
flat=[]
for label,rows in best.items():
 for rank,r in enumerate(rows,1):
  flat.append({**{k:v for k,v in r.items() if k!='museum_names'},'rank_within_subset':rank,'museum_names_pipe':'|'.join(r['museum_names'])})
with (out/'UK_DCMS_multioutput_balanced_window_candidates_v1.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(flat[0]));w.writeheader();w.writerows(flat)
print('AUDIT_DONE',len(table_inventory),'tables','raw_source_codes',dict(rawcodes),flush=True)
