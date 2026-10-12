"""Basemap drawing helpers (EPSG:27700) for London and Liverpool frames."""
import os, geopandas as gpd, pandas as pd
from shapely.geometry import box
G = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gis')
WATER = '#D3E2E9'; LAND_OUT = '#EFEDE8'; LAND_IN = '#FBFAF7'; BORO = '#C9C3B8'; PARK = '#E1EAD6'
ROAD_MAJ = '#E0DBD2'; ROAD_MIN = '#ECE8E2'; RAIL = '#D6D1C9'; BORO = '#B5AC9C'

_cache = {}
def load(name):
    if name not in _cache:
        _cache[name] = gpd.read_file(os.path.join(G, name + '.gpkg'))
    return _cache[name]

def clip(g, frame):
    return g[g.intersects(frame)].clip(frame)

def draw_city(ax, city, xmin, ymin, xmax, ymax, roads_min_class='tertiary'):
    frame = box(xmin, ymin, xmax, ymax)
    ax.set_facecolor(WATER if city == 'liverpool' else LAND_OUT)
    if city == 'london':
        b = clip(load('gla_london_borough'), frame)
        b.plot(ax=ax, color=LAND_IN, edgecolor='none', zorder=1)
    else:
        b = clip(load('ons_lad24_bfc_merseyside'), frame)
        b.plot(ax=ax, color=LAND_IN, edgecolor='none', zorder=1)
    pk = load(f'osm_{city}_parks')
    pk = pk[(pk.get('leisure').isin(['park', 'common'])) | (pk.get('landuse').isin(['recreation_ground', 'cemetery']))]
    pk = pk[pk.area > 30000]
    clip(pk, frame).plot(ax=ax, color=PARK, edgecolor='none', zorder=2)
    w = load(f'osm_{city}_water'); w = w[w.area > 4000]
    clip(w, frame).plot(ax=ax, color=WATER, edgecolor='none', zorder=3)
    if city == 'london':
        clip(load('gla_river_thames'), frame).plot(ax=ax, color=WATER, edgecolor='#B9CED8', linewidth=0.35, zorder=3)
    r = load(f'osm_{city}_roads')
    cls_minor = ['tertiary', 'secondary'] if roads_min_class == 'tertiary' else ['secondary']
    clip(r[r.highway.isin(cls_minor)], frame).plot(ax=ax, color=ROAD_MIN, linewidth=0.28, zorder=4)
    clip(r[r.highway.isin(['primary', 'trunk', 'motorway'])], frame).plot(ax=ax, color=ROAD_MAJ, linewidth=0.55, zorder=4)
    rl = load(f'osm_{city}_rail')
    clip(rl, frame).plot(ax=ax, color=RAIL, linewidth=0.3, linestyle=(0, (2, 1.2)), zorder=4)
    bl = b.boundary
    if city == 'london':
        th = load('gla_river_thames').geometry.union_all().buffer(15)
        bl = bl.difference(th)
    gpd.GeoSeries(bl, crs=b.crs).plot(ax=ax, color=BORO, linewidth=0.5, linestyle=(0, (4, 1.6)), zorder=5)
    ax.set_xlim(xmin, xmax); ax.set_ylim(ymin, ymax); ax.set_aspect('equal')
    ax.set_xticks([]); ax.set_yticks([]); ax.set_xlabel(''); ax.set_ylabel('')
    for s in ax.spines.values(): s.set_visible(True); s.set_color('#9AA1A9'); s.set_linewidth(0.5)
    return b

def to27700(df, lon='lon', lat='lat'):
    g = gpd.GeoDataFrame(df.copy(), geometry=gpd.points_from_xy(df[lon], df[lat]), crs=4326).to_crs(27700)
    g['x'] = g.geometry.x; g['y'] = g.geometry.y
    return g
