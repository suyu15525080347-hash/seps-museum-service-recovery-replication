"""Convert raw Overpass JSON to projected GeoPackages (EPSG:27700); refetch any missing layer."""
import json, os, sys, time, hashlib, requests
import geopandas as gpd
from shapely.geometry import LineString, Polygon, MultiPolygon
from shapely.ops import polygonize, unary_union, linemerge
sys.stdout.reconfigure(encoding='utf-8')
G = r'D:\seps_fig_work\gis'
H = {'User-Agent': 'SEPS-figure-research/0.1 (academic figure provenance)'}
prov = json.load(open(os.path.join(G, 'basemap_provenance.json'), encoding='utf-8'))
if not os.path.exists(os.path.join(G, 'osm_liverpool_parks.json')):
    bb = '(53.340,-3.075,53.445,-2.905)'
    q = f'[out:json][timeout:120];way["leisure"="park"]{bb};out geom;'
    for ep in ['https://overpass-api.de/api/interpreter', 'https://overpass.kumi.systems/api/interpreter',
               'https://overpass.private.coffee/api/interpreter']:
        try:
            r = requests.post(ep, data={'data': q}, headers=H, timeout=250)
            if r.status_code == 200 and r.content[:1] == b'{':
                open(os.path.join(G, 'osm_liverpool_parks.json'), 'wb').write(r.content)
                prov['osm_liverpool_parks.json'] = {'url': ep + ' :: ' + q, 'bytes': len(r.content),
                    'sha256': hashlib.sha256(r.content).hexdigest(), 'retrieved_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
                print('fetched liverpool parks', ep, len(r.content)); break
            print('fail', ep, r.status_code)
        except Exception as e:
            print('err', ep, e)
    json.dump(prov, open(os.path.join(G, 'basemap_provenance.json'), 'w', encoding='utf-8'), indent=1)

def el_geoms(path, area=False):
    js = json.load(open(path, encoding='utf-8'))
    recs = []
    for el in js['elements']:
        tags = el.get('tags', {})
        if el['type'] == 'way' and 'geometry' in el:
            pts = [(p['lon'], p['lat']) for p in el['geometry']]
            if len(pts) < 2: continue
            if area and len(pts) >= 4 and pts[0] == pts[-1]:
                recs.append({'geometry': Polygon(pts), **{k: tags.get(k) for k in ('highway', 'leisure', 'landuse', 'natural', 'name', 'waterway')}})
            elif not area:
                recs.append({'geometry': LineString(pts), **{k: tags.get(k) for k in ('highway', 'railway', 'name', 'natural')}})
        elif el['type'] == 'relation' and area:
            outers = [LineString([(p['lon'], p['lat']) for p in m['geometry']]) for m in el.get('members', [])
                      if m.get('role') == 'outer' and 'geometry' in m and len(m['geometry']) > 1]
            if not outers: continue
            u = unary_union(outers)
            polys = list(polygonize(list(u.geoms) if hasattr(u, 'geoms') else [u]))
            if polys:
                recs.append({'geometry': unary_union(polys), **{k: tags.get(k) for k in ('leisure', 'landuse', 'natural', 'name', 'waterway')}})
    g = gpd.GeoDataFrame(recs, geometry='geometry', crs=4326)
    g = g[g.is_valid | g.buffer(0).is_valid]
    return g.to_crs(27700)

for city in ['london', 'liverpool']:
    for lay, area in [('roads', False), ('rail', False), ('parks', True), ('water', True)] + ([('coast', False)] if city == 'liverpool' else []):
        p = os.path.join(G, f'osm_{city}_{lay}.json')
        if not os.path.exists(p): print('MISSING', p); continue
        g = el_geoms(p, area)
        if area: g['geometry'] = g.buffer(0)
        g.to_file(os.path.join(G, f'osm_{city}_{lay}.gpkg'), driver='GPKG')
        print(city, lay, len(g))
for nm in ['gla_london_borough', 'gla_boundary', 'gla_river_thames', 'ons_lad24_bfc_merseyside', 'ons_countries24_buc']:
    g = gpd.read_file(os.path.join(G, nm + '.geojson'))
    print(nm, len(g), g.crs, list(g.columns)[:6], g.geom_type.unique())
    g.to_crs(27700).to_file(os.path.join(G, nm + '.gpkg'), driver='GPKG')
