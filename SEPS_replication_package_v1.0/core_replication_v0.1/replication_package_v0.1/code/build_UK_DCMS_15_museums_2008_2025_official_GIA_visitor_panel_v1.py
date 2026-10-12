#!/usr/bin/env python3
"""15 current national-museum groups by 17 financial years: primary official UK 2026 ODS visits+GIA+other outcomes. No regression."""
import zipfile,xml.etree.ElementTree as ET,csv,json,re,collections,math
from pathlib import Path
root=next(q for p in Path('G:/').iterdir() if p.is_dir() if p.is_dir() for q in p.iterdir() if q.is_dir() and 'Cities+SEPS' in q.name)
out=next(root.glob('05_*'))/'31_UK_DCMS_museum_site_finance_visits_same_institution_open_2024_25_screen_v1'
ns={'table':'urn:oasis:names:tc:opendocument:xmlns:table:1.0','text':'urn:oasis:names:tc:opendocument:xmlns:text:1.0','office':'urn:oasis:names:tc:opendocument:xmlns:office:1.0'}
def rawtable(kind,tabname):
 with zipfile.ZipFile(out/f'UK_DCMS_2024_25_{kind}_OFFICIAL.ods') as z:d=ET.fromstring(z.read('content.xml'))
 tabs=[x for x in d.findall('.//table:table',ns) if x.get('{'+ns['table']+'}name')==tabname]
 if len(tabs)!=1:raise RuntimeError('Tab missing '+kind+tabname)
 arr=[]
 for row in tabs[0].findall('table:table-row',ns):
  vals=[]
  for cell in row:
   if not cell.tag.endswith('table-cell') or cell.tag.endswith('covered-table-cell'):continue
   ps=cell.findall('text:p',ns)
   v=' '.join(''.join(p.itertext()) for p in ps).strip()
   if not v:v=cell.get('{'+ns['office']+'}value','')
   n=min(55,int(cell.get('{'+ns['table']+'}number-columns-repeated','1')))
   vals.extend([v]*n)
  arr.append(vals)
 return arr
museum_names=['British Museum','Museum of the Home','Horniman Museum','Imperial War Museum','National Gallery',
'National Museums Liverpool','National Portrait Gallery','Natural History Museum','Royal Armouries',
'Royal Museums Greenwich','Science Museum Group',"Sir John Soane's Museum",'Tate Gallery',
'Victoria and Albert Museum','Wallace Collection']
def canonical(text):
 t=re.sub(r'\s*\[Note[^]]*\]','',text).strip()
 t={'Imperial War Museums':'Imperial War Museum','Tate Gallery Group':'Tate Gallery'}.get(t,t)
 return t
metrics=[('performance','1','visitors_total_actual'),('performance','3','under16_visits'),
('performance','4','overseas_visits'),('performance','7','formal_education_under18_visits'),
('performance','8','organized_on_site_under18_participations'),('performance','9','UK_loan_venues'),
('income','3','Grant_in_Aid_GBP'),('income','1','fundraising_including_objects_GBP'),('income','5','total_reported_income_GBP')]
data={};summary={}
for kind,sheet,field in metrics:
 arr=rawtable(kind,sheet)
 headers=[i for i,row in enumerate(arr) if row and row[0].strip() in ('Name of museum or gallery','Name of organisation','Museum or Gallery','Name of Museum/Gallery')]
 if not headers:
  headers=[i for i,row in enumerate(arr) if row and ('Name of museum' in row[0] or 'Name of organisation' in row[0])]
 if len(headers)!=1:
  print('BAD_HEADER',field,[(i,row[:4]) for i,row in enumerate(arr[:9])],flush=True)
  raise RuntimeError(f'header unresolved {field}')
 headeridx=headers[0];head=arr[headeridx]
 yearcols={}
 for j,h in enumerate(head):
  mm=re.match(r'^(20\d\d)\s*/\s*(?:20)?(\d{2}|\d{4})',h.strip())
  if mm:
   yy=int(mm.group(1))
   if 2008<=yy<=2024:yearcols[j]=yy
 if not yearcols:raise RuntimeError('No years '+field)
 raw_missing=collections.Counter();observed=0;seen=set();unknown=[]
 for row in arr[headeridx+1:]:
  if not row:continue
  name=canonical(row[0])
  if name not in museum_names:
   if name and name not in ('Total','Grand Total'):unknown.append(name)
   continue
  if name in seen:raise RuntimeError('duplicate museum in source table '+field+name)
  seen.add(name)
  for col,year in yearcols.items():
   raw=row[col].strip() if col<len(row) else ''
   key=(name,year)
   value=None
   if raw.lower() in ('x','b','n/a','na','',':','..'):raw_missing[raw or '<blank>']+=1
   else:
    try:
     x=float(raw.replace(',','').replace('£','').replace('%','').strip())
     if x<0:raise ValueError('negative sentinel')
     value=x;observed+=1
    except ValueError:
     raw_missing[raw]+=1
   data.setdefault(key,{})[field]=value
   data[key][field+'_raw_source_cell']=raw
  # Note that missing museum row entirely is distinct from x-coded entries
 summary[field]={'source_ods':kind,'source_sheet':sheet,'yearcols':yearcols,'unique_current_museums_found':len(seen),
  'missing_museum_names':sorted(set(museum_names)-seen),'numeric_museum_year_cells':observed,'missing_codes':dict(raw_missing),
  'extraneous_historical_or_other_institution_rows':sorted(set(unknown))[:30]}
 print('OFFICIAL_ODS_METRIC',field,'institutions',len(seen),'numeric_values',observed,'missing',dict(raw_missing),'noted_other_rows',len(unknown),flush=True)
outrows=[]
for museum in museum_names:
 for year in range(2008,2025):
  orig=data.get((museum,year),{})
  row={'museum_group':museum,'year_start':year,'financial_year':f'{year}/{str(year+1)[-2:]}'}
  row.update(orig)
  row['GIA_and_annual_visits_both_valid']=int(row.get('visitors_total_actual') is not None and row.get('Grant_in_Aid_GBP') is not None)
  row['formally_excluded_causal_treatment']='DONT_INFER_GIA_EFFECT_FROM_PANEL'
  outrows.append(row)
fields=list(dict.fromkeys(k for row in outrows for k in row))
dest=out/'UK_DCMS_15_museums_FY2008_2024_annual_GIA_visits_and_outputs_official_ODS_join_v1.csv'
with dest.open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(outrows)
paired=[r for r in outrows if r['GIA_and_annual_visits_both_valid']]
byyr=collections.Counter(int(r['year_start']) for r in paired)
diagnostics={
 'institution_groups_declared_2024_25':len(museum_names),'years_fy2008_2024':17,
 'fixed_museum_year_grid':len(outrows),'valid_GIA_visits_pairs':len(paired),
 'paired_by_financial_start_year':dict(sorted(byyr.items())),
 'source_sheet_metric_QA':summary,
 'extreme_donation_warning':'Museum self-generated fundraising and total income can be dominated by donated artifacts valued non-cash; particularly British Museum 2024/25. Do NOT assume these are recurrent cash operating receipts.',
 'causal_limitation':'Grants allocated to museum groups are not exogenous, museums operate multiple premises, and visits reflect pandemic restrictions, special exhibitions, heritage tourism, closures and renovations. This is not a causal panel.',
 'comparability_warning':'Original source ODS contains group mergers (historical Museum of Science and Industry, National Museum of Science and Industry) and special museums no longer in current 15. Canonical science GROUP source 2008-10 Grant-in-Aid marked x; not backfilled from predecessor institutions. b break-in-series markers in header documented but not modeled. Closed years marked x remain missing.',
 'publication_gate':'G1 national museums real 2008/09-2024/25 institution×FY grants and visits PASS; G2 city planning/arts neighborhood geolocation absent, G3 public policy causal treatment not identified, G4 novelty/literature not audited. May fit alternative SEPS original performance/comparability methodology, but prior SEPS 2023 arts efficiency paper is direct competitor.'
}
(out/'UK_DCMS_15_museums_FY2008_2024_official_GIA_and_visits_reconciliation_QA_v1.json').write_text(json.dumps(diagnostics,ensure_ascii=False,indent=2),encoding='utf-8')
print('UK_DCMS_MUSEUM_GIA_VISITOR_PANEL_PASS',json.dumps({'groups':len(museum_names),'year_grid':len(outrows),'valid_pairs':len(paired),'by_fiscal_year':dict(byyr)},ensure_ascii=False),flush=True)
