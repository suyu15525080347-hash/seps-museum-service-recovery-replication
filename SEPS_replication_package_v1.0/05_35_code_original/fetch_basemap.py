"""Fetch auditable open basemap layers for SEPS Figure 1.
Sources (all open, no login):
  GLA ArcGIS context layers (London borough, GLA boundary, River Thames)
  ONS Open Geography Portal: LAD Dec 2024 BFC (Liverpool city region), Countries Dec 2024 BUC (UK locator)
  OpenStreetMap via Overpass API (major roads, parks, inland water, rail) -- (c) OSM contributors, ODbL
"""
import requests, json, sys, time, hashlib, os
sys.stdout.reconfigure(encoding='utf-8')
OUT = r'D:\seps_fig_work\gis'; os.makedirs(OUT, exist_ok=True)
H = {'User-Agent': 'SEPS-figure-research/0.1 (academic figure provenance)'}
log = {}
def save(name, content, url):
    p = os.path.join(OUT, name)
    open(p, 'wb').write(content)
    log[name] = {'url': url, 'bytes': len(content), 'sha256': hashlib.sha256(content).hexdigest(),
                 'retrieved_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
    print('saved', name, len(content))

GLA = 'https://gis.london.gov.uk/arcgis/rest/services/apps/webmap_context_layer/MapServer/{}/query'
for lid, nm in [(3, 'gla_london_borough'), (0, 'gla_boundary'), (1, 'gla_river_thames')]:
    params = {'where': '1=1', 'outFields': '*', 'returnGeometry': 'true', 'f': 'geojson', 'outSR': 4326}
    r = requests.get(GLA.format(lid), params=params, headers=H, timeout=120)
    save(nm + '.geojson', r.content, r.url)

ONS = 'https://services1.arcgis.com/ESMARspQHYMw9BZ9/arcgis/rest/services/{}/FeatureServer/0/query'
q = {'where': "LAD24NM IN ('Liverpool','Wirral','Sefton','Knowsley','St. Helens','Halton','Cheshire West and Chester')",
     'outFields': 'LAD24CD,LAD24NM', 'returnGeometry': 'true', 'f': 'geojson', 'outSR': 4326}
r = requests.get(ONS.format('Local_Authority_Districts_December_2024_Boundaries_UK_BFC'), params=q, headers=H, timeout=180)
save('ons_lad24_bfc_merseyside.geojson', r.content, r.url)
q = {'where': '1=1', 'outFields': 'CTRY24CD,CTRY24NM', 'returnGeometry': 'true', 'f': 'geojson', 'outSR': 4326}
r = requests.get(ONS.format('Countries_December_2024_Boundaries_UK_BUC'), params=q, headers=H, timeout=180)
save('ons_countries24_buc.geojson', r.content, r.url)

OVP = 'https://overpass-api.de/api/interpreter'
boxes = {'london': (51.418, -0.245, 51.552, 0.045), 'liverpool': (53.340, -3.075, 53.445, -2.905)}
for city, (s, w, n, e) in boxes.items():
    bb = f'({s},{w},{n},{e})'
    queries = {
        'roads': f'[out:json][timeout:240];(way["highway"~"^(motorway|trunk|primary|secondary|tertiary)$"]{bb};);out geom;',
        'parks': f'[out:json][timeout:240];(way["leisure"~"^(park|common|garden)$"]{bb};relation["leisure"~"^(park|common)$"]{bb};way["landuse"~"^(recreation_ground|cemetery|grass)$"]{bb};);out geom;',
        'water': f'[out:json][timeout:240];(way["natural"="water"]{bb};relation["natural"="water"]{bb};way["waterway"="dock"]{bb};);out geom;',
        'rail': f'[out:json][timeout:240];(way["railway"="rail"]["usage"="main"]{bb};);out geom;',
    }
    if city == 'liverpool':
        queries['coast'] = f'[out:json][timeout:240];(way["natural"="coastline"]{bb};);out geom;'
    for k, qq in queries.items():
        for att in range(4):
            try:
                r = requests.post(OVP, data={'data': qq}, headers=H, timeout=300)
                if r.status_code == 200 and r.content[:1] == b'{':
                    save(f'osm_{city}_{k}.json', r.content, OVP + ' :: ' + qq); break
                print('retry', city, k, r.status_code); time.sleep(20)
            except Exception as ex:
                print('err', city, k, ex); time.sleep(20)
        time.sleep(5)
json.dump(log, open(os.path.join(OUT, 'basemap_provenance.json'), 'w', encoding='utf-8'), indent=1)
print('DONE')
