"""Site coordinates from Wikidata (P625) by exact English label; output auditable CSV with QIDs."""
import requests, sys, csv, time
sys.stdout.reconfigure(encoding='utf-8')
H = {'User-Agent': 'SEPS-figure-research/0.1 (academic figure provenance)', 'Accept': 'application/sparql-results+json'}
labels = ['British Museum', 'Natural History Museum', 'Victoria and Albert Museum', 'Young V&A', 'Science Museum',
          'Tate Modern', 'Tate Britain', 'Imperial War Museum London', 'Churchill War Rooms', 'HMS Belfast',
          'National Maritime Museum', 'Royal Observatory, Greenwich', "Queen's House", 'Cutty Sark', 'Horniman Museum',
          "Sir John Soane's Museum", 'National Gallery', 'National Portrait Gallery', 'Wallace Collection',
          'Museum of the Home', 'World Museum', 'Walker Art Gallery', 'Merseyside Maritime Museum',
          'International Slavery Museum', 'Museum of Liverpool', 'Sudley House', 'Lady Lever Art Gallery',
          'Tate Liverpool', 'RIBA North', 'National Railway Museum', 'Science and Industry Museum',
          'National Science and Media Museum', 'Locomotion', 'IWM North', 'IWM Duxford', 'Imperial War Museum Duxford',
          'Tate St Ives', 'Natural History Museum at Tring', 'Royal Armouries Museum', 'Fort Nelson',
          'Royal Observatory Greenwich', 'Royal Observatory', 'Horniman Museum and Gardens', 'Horniman Museum & Gardens',
          'Imperial War Museum North', 'Royal Armouries', 'RIBA North, National Architecture Centre', 'Mann Island Buildings',
          'Royal Armouries Museum, Leeds']
vals = ' '.join('"%s"@en' % l.replace('"', '\\"') for l in labels)
q = '''SELECT ?name ?item ?desc ?coord WHERE { VALUES ?name { %s }
 ?item rdfs:label ?name ; wdt:P625 ?coord .
 OPTIONAL { ?item schema:description ?desc FILTER(lang(?desc)="en") }
 ?item wdt:P17 wd:Q145 . }''' % vals
for k in range(5):
    r = requests.get('https://query.wikidata.org/sparql', params={'query': q, 'format': 'json'}, headers=H, timeout=120)
    if r.status_code == 200: break
    print('retry', r.status_code); time.sleep(10)
rows = []
for b in r.json()['results']['bindings']:
    c = b['coord']['value'].replace('Point(', '').replace(')', '').split()
    rows.append([b['name']['value'], b['item']['value'].split('/')[-1], b.get('desc', {}).get('value', ''), float(c[1]), float(c[0])])
rows.sort()
with open(r'D:\seps_fig_work\gis\wikidata_site_candidates.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['label', 'qid', 'description', 'lat', 'lon']); w.writerows(rows)
for x in rows: print(x)
found = {x[0] for x in rows}
print('MISSING:', [l for l in labels if l not in found])
