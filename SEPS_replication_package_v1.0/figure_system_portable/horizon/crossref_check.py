import requests, json, sys
sys.stdout.reconfigure(encoding='utf-8')
H = {'User-Agent': 'SEPS-reference-check/0.1 (mailto:none@example.org)'}
dois = ['10.1111/j.1467-9299.2006.00600.x', '10.1016/S0377-2217(97)00163-X', '10.1016/j.ejor.2005.12.041',
        '10.1287/opre.33.1.38', '10.1080/01900699508525011', '10.1111/j.1540-6210.2006.00612.x']
out = []
for d in dois:
    r = requests.get('https://api.crossref.org/works/' + d, headers=H, timeout=60)
    if r.status_code != 200: print(d, 'HTTP', r.status_code); out.append({'doi': d, 'status': r.status_code}); continue
    m = r.json()['message']
    rec = {'doi': d, 'title': m.get('title', [''])[0], 'journal': (m.get('container-title') or [''])[0],
           'year': (m.get('published-print') or m.get('published-online') or m.get('issued'))['date-parts'][0][0],
           'volume': m.get('volume'), 'issue': m.get('issue'), 'page': m.get('page'),
           'authors': [f"{a.get('family')}, {a.get('given')}" for a in m.get('author', [])]}
    out.append(rec); print(json.dumps(rec, ensure_ascii=False))
json.dump(out, open(r'D:\seps_fig_work\horizon\crossref_new_refs_v1.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
