#!/usr/bin/env python3
"""Download latest 1 Oct 2026 official HMT GDP-deflator XLSX, parse FY indices, compare June vintage and recompute DCMS real-GIA endpoint context."""
from pathlib import Path
import urllib.request,re,zipfile,xml.etree.ElementTree as ET,json,hashlib,csv,statistics
root=next(q for p in Path('G:/').iterdir() if p.is_dir() for q in p.iterdir() if q.is_dir() and 'Cities+SEPS' in q.name)
stage=next(root.glob('05_*'));s31=stage/'31_UK_DCMS_museum_site_finance_visits_same_institution_open_2024_25_screen_v1';s32=stage/'32_UK_DCMS_definition_breaks_multioutput_novelty_model_screen_v1';out=stage/'34_SEPS_manuscript_prototype_and_internal_desk_reject_v1'
page='https://www.gov.uk/government/statistics/gdp-deflators-at-market-prices-and-money-gdp-september-2026-quarterly-national-accounts'
req=urllib.request.Request(page,headers={'User-Agent':'Mozilla/5.0 academic source verification'})
with urllib.request.urlopen(req,timeout=60) as f:html=f.read(1000000).decode('utf-8','replace')
links=re.findall(r'href="([^"]+\.xlsx[^"]*)"',html,re.I)
links=[x.replace('&amp;','&') for x in links]
if not links:raise RuntimeError('No official xlsx href found')
url=links[0] if links[0].startswith('http') else 'https://www.gov.uk'+links[0]
print('LATEST_HMT_XLSX_URL',url,flush=True)
req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 academic source verification'})
with urllib.request.urlopen(req,timeout=80) as f:raw=f.read(2000000)
dest=out/'HMT_GDP_Deflators_QNA_September2026_OFFICIAL.xlsx';dest.write_bytes(raw)
if not zipfile.is_zipfile(dest):raise RuntimeError('Downloaded HMT file not XLSX')
ns='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
with zipfile.ZipFile(dest) as z:
 shared=[]
 if 'xl/sharedStrings.xml' in z.namelist():
  rr=ET.fromstring(z.read('xl/sharedStrings.xml'))
  for si in rr.findall('{%s}si'%ns):shared.append(''.join(t.text or '' for t in si.iter() if t.tag.endswith('}t')))
 sh=ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
 def cv(c):
  v=c.find('{%s}v'%ns)
  if v is None:return ''
  x=v.text or ''
  return shared[int(x)] if c.get('t')=='s' else x
 defl={}
 for row in sh.findall('.//{%s}sheetData/{%s}row'%(ns,ns)):
  d={c.get('r')[0]:cv(c) for c in row.findall('{%s}c'%ns)}
  fy=d.get('B','')
  if re.match(r'^20\d\d-\d\d$',fy):
   try:defl[fy]=float(d.get('C',''))
   except:pass
for k in ('2018-19','2024-25','2025-26'):
 print('LATEST_DEFLATOR',k,defl.get(k),flush=True)
# old June values from recorded source
old={'2018-19':76.1639,'2024-25':96.6694,'2025-26':100.0}
# GIA current 14 comparable excluding Museum of Home
with (s31/'UK_DCMS_15_museums_FY2008_2024_annual_GIA_visits_and_outputs_official_ODS_join_v1.csv').open(encoding='utf-8-sig') as f:rows=list(csv.DictReader(f))
names=sorted({r['museum_group'] for r in rows if r['museum_group']!='Museum of the Home'})
idx={(r['museum_group'],int(r['year_start'])):r for r in rows}
ratios=[]
sum18=sum24=0
for n in names:
 g18=float(idx[(n,2018)]['Grant_in_Aid_GBP']);g24=float(idx[(n,2024)]['Grant_in_Aid_GBP'])
 real18=g18*defl['2024-25']/defl['2018-19'];real24=g24
 ratios.append(real24/real18);sum18+=real18;sum24+=real24
newratio=sum24/sum18
oldratio=1.1493
qa={'page_url':page,'xlsx_url':url,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),
 'latest_deflators':{k:defl.get(k) for k in ('2018-19','2024-25','2025-26')},
 'old_June2026_deflators':old,
 'deflator_revision_pct':{k:round(100*(defl[k]/old[k]-1),6) for k in old},
 'source_comparable_14museum_real_GIA_2024_25_vs_2018_19_ratio_latest':round(newratio,6),
 'old_manuscript_ratio_from_June_vintage':oldratio,
 'ratio_revision':round(newratio-oldratio,6),
 'median_museum_real_GIA_ratio_latest':round(statistics.median(ratios),6),
 'decision':'All manuscript real-GIA values must use latest September 2026 HMT vintage as of current date. Service-output recovery metrics unaffected.'}
(out/'HMT_September2026_deflator_update_and_DCMS_realGIA_revision_QA_v1.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8')
print('LATEST_REAL_GIA_CONTEXT',json.dumps(qa,ensure_ascii=False),flush=True)
