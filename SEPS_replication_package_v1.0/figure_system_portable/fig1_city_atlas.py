"""Figure 1 - City-scale geography of multi-mission museum recovery (London + Liverpool).
All values from the frozen replication package; geography from GLA, ONS, OSM, Wikidata (see provenance)."""
import os
import sys, numpy as np, pandas as pd, geopandas as gpd, matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, FancyBboxPatch
from matplotlib.lines import Line2D
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
sys.stdout.reconfigure(encoding='utf-8')
from seps_style import *
from basemap_lib import draw_city, to27700, load, clip
from shapely.geometry import box
setup()

# ---------------- data
d = pd.read_csv(os.path.join(WORK, 'fig_core5_tidy.csv'))
end = d[d.FY_start == 2024].set_index('museum_group')
order = end.worst_mission_score.sort_values().index.tolist()          # rank 1 = most constrained
NUM = {g: i + 1 for i, g in enumerate(order)}
norm = Normalize(0, 1)
def ncol(v): return REC_CMAP(norm(v))
sites = to27700(pd.read_csv(os.path.join(WORK, 'sites_curated.csv')))

# ---------------- canvas (mm layout)
FW, FH = 190, 225
fig = plt.figure(figsize=(FW * MM, FH * MM))
def ax_mm(x, y, w, h, **kw): return fig.add_axes([x / FW, y / FH, w / FW, h / FH], **kw)

L = to27700(pd.DataFrame({'lon': [-0.214, 0.026], 'lat': [51.4345, 51.5435]}))
(LX0, LY0), (LX1, LY1) = L[['x', 'y']].values
MAPW = 124.0; MAPH = MAPW * (LY1 - LY0) / (LX1 - LX0)
MAP_Y = FH - 9 - MAPH
axA = ax_mm(5, MAP_Y, MAPW, MAPH)
boro = draw_city(axA, 'london', LX0, LY0, LX1, LY1)
M_PER_MM_A = (LX1 - LX0) / MAPW
print('map A height mm', round(MAPH, 1), 'm/mm', round(M_PER_MM_A, 1))

R_UNIT_MM = 2.55   # node radius in mm for real-GIA ratio = 1.0 (radius proportional to ratio)
def node(ax, x, y, g, mpm, z=20, label=True):
    r = R_UNIT_MM * end.loc[g, 'real_GIA_ratio'] * mpm
    ax.add_patch(Circle((x, y), r, facecolor=ncol(end.loc[g, 'worst_mission_score']), edgecolor='white', lw=0.9, zorder=z))
    ax.add_patch(Circle((x, y), r, facecolor='none', edgecolor=INK, lw=0.45, zorder=z + 0.1))
    ax.add_patch(Circle((x, y), R_UNIT_MM * mpm, facecolor='none', edgecolor=INK, lw=0.45, ls=(0, (1.6, 1.1)), zorder=z + 0.2))
    tc = 'white' if end.loc[g, 'worst_mission_score'] < 0.42 or end.loc[g, 'worst_mission_score'] > 0.97 else INK
    if label:
        ax.text(x, y, str(NUM[g]), ha='center', va='center', fontsize=7, fontweight='bold', color=tc, zorder=z + 0.3)
    return r

# ---------------- Panel A content
SAT_C = '#59636E'
OFF = {'Natural History Museum': (-650, -1150), 'Science Museum Group': (-1250, 480), 'Victoria and Albert Museum': (720, -1080),
       'British Museum': (-260, 260), "Sir John Soane's Museum": (330, -170), 'Royal Museums Greenwich': (-950, -760)}
LAB = {  # (dx_mm, dy_mm, ha) label position relative to node centre, in mm
    'Natural History Museum': (0, -6.0, 'center'), 'Science Museum Group': (0, 4.4, 'center'),
    'Victoria and Albert Museum': (4.2, -1.2, 'left'), 'British Museum': (-4.1, 0.6, 'right'),
    "Sir John Soane's Museum": (3.8, 0.9, 'left'), 'Tate Gallery': (-4.2, -0.6, 'right'),
    'Imperial War Museum': (3.7, -1.5, 'left'), 'Royal Museums Greenwich': (-4.6, -1.2, 'right'),
    'Horniman Museum': (-4.9, 0.0, 'right')}
LNAME = {'Natural History Museum': 'Natural History\nMuseum', 'Science Museum Group': 'Science Museum\nGroup',
         'Victoria and Albert Museum': 'V&A', 'British Museum': 'British\nMuseum', "Sir John Soane's Museum": "Sir John\nSoane's",
         'Tate Gallery': 'Tate', 'Imperial War Museum': 'Imperial War\nMuseums', 'Royal Museums Greenwich': 'Royal Museums\nGreenwich',
         'Horniman Museum': 'Horniman\nMuseum'}
lon_s = sites[sites.city_frame == 'London']
for g, sub in lon_s[lon_s.role.isin(['anchor', 'other_site'])].groupby('museum_group'):
    a = sub[sub.role == 'anchor'].iloc[0]
    nx, ny = a.x + OFF.get(g, (0, 0))[0], a.y + OFF.get(g, (0, 0))[1]
    for _, s in sub[sub.role == 'other_site'].iterrows():
        axA.plot([nx, s.x], [ny, s.y], color=SAT_C, lw=0.45, alpha=0.65, zorder=12, solid_capstyle='round')
        axA.scatter(s.x, s.y, s=7, color='white', edgecolor=SAT_C, lw=0.6, zorder=13)
    if g in OFF:
        axA.plot([nx, a.x], [ny, a.y], color=INK, lw=0.45, zorder=14)
        axA.scatter(a.x, a.y, s=4, color=INK, zorder=15, lw=0)
    r = node(axA, nx, ny, g, M_PER_MM_A)
    dx, dy, ha = LAB[g]
    axA.text(nx + dx * M_PER_MM_A, ny + dy * M_PER_MM_A, LNAME[g], ha=ha, va='center', fontsize=7, fontweight='bold',
             color=INK, linespacing=0.95, zorder=30, path_effects=halo(1.8))
SATLAB = {}  # site-label text omitted at final-size 7 pt; site geometry remains
ctx = lon_s[lon_s.role == 'context_not_in_core5']
axA.scatter(ctx.x, ctx.y, s=13, marker='D', facecolor='white', edgecolor='#7D8590', lw=0.7, zorder=16)
CTXLAB = {}  # contextual-site text omitted at final-size 7 pt; diamonds remain
# borough boundary geometry retained; borough-name text omitted for legibility
tp = to27700(pd.DataFrame({'lon': [-0.0560], 'lat': [51.5063]})).iloc[0]
axA.text(tp.x, tp.y, 'River Thames', fontsize=7, color='#6F93A3', style='italic', rotation=0, ha='center',
         va='center', zorder=7)
# scale bar + north arrow
sx, sy = LX1 - 5 * M_PER_MM_A - 2000, LY0 + 4 * M_PER_MM_A
axA.add_patch(Rectangle((sx, sy), 1000, 0.6 * M_PER_MM_A, color=INK, zorder=40, lw=0))
axA.add_patch(Rectangle((sx + 1000, sy), 1000, 0.6 * M_PER_MM_A, facecolor='white', edgecolor=INK, lw=0.4, zorder=40))
for k, t in [(0, '0'), (1000, '1'), (2000, '2 km')]:
    axA.text(sx + k, sy + 1.6 * M_PER_MM_A, t, fontsize=7, ha='center', va='bottom', zorder=40, path_effects=halo(1.2))
nx_, ny_ = LX1 - 5 * M_PER_MM_A, LY1 - 9 * M_PER_MM_A
axA.annotate('', xy=(nx_, ny_ + 5 * M_PER_MM_A), xytext=(nx_, ny_), zorder=40,
             arrowprops=dict(arrowstyle='-|>,head_width=0.18,head_length=0.35', color=INK, lw=0.6))
axA.text(nx_, ny_ + 6.2 * M_PER_MM_A, 'N', fontsize=7, ha='center', va='bottom', fontweight='bold', zorder=40)

# ---------------- Panel B: Liverpool inset
V = to27700(pd.DataFrame({'lon': [-3.040, -2.908], 'lat': [53.349, 53.431]}))
(VX0, VY0), (VX1, VY1) = V[['x', 'y']].values
BW = 54.0; BH = BW * (VY1 - VY0) / (VX1 - VX0)
axB = ax_mm(134, FH - 9 - BH, BW, BH)
lad = draw_city(axB, 'liverpool', VX0, VY0, VX1, VY1)
M_PER_MM_B = (VX1 - VX0) / BW
liv = sites[sites.city_frame == 'Liverpool']
g = 'National Museums Liverpool'
a = liv[liv.role == 'anchor'].iloc[0]
nx, ny = a.x + 1500, a.y - 650
for _, s in liv[liv.role == 'other_site'].iterrows():
    axB.plot([nx, s.x], [ny, s.y], color=SAT_C, lw=0.5, alpha=0.85, zorder=12)
    axB.scatter(s.x, s.y, s=7, color='white', edgecolor=SAT_C, lw=0.6, zorder=13)
axB.plot([nx, a.x], [ny, a.y], color=INK, lw=0.45, zorder=14); axB.scatter(a.x, a.y, s=4, color=INK, zorder=15, lw=0)
node(axB, nx, ny, g, M_PER_MM_B)
axB.text(nx + 4.0 * M_PER_MM_B, ny - 0.2 * M_PER_MM_B, 'NML', fontsize=7, fontweight='bold',
         ha='left', va='center', linespacing=0.95, zorder=30, path_effects=halo(1.8))
LIVLAB = {}  # minor Liverpool site-label text omitted at 7 pt
tl = sites[sites.site == 'Tate Liverpool'].iloc[0]
axB.scatter(tl.x, tl.y, s=7, color='white', edgecolor=SAT_C, lw=0.6, zorder=13)
axB.text(tl.x - 1.5 * M_PER_MM_B, tl.y - 3.1 * M_PER_MM_B, f"Tate Liverpool [{NUM['Tate Gallery']}]", fontsize=7,
         color=SAT_C, style='italic', ha='right', va='center', zorder=29, path_effects=halo(1.4))
axB.text(VX0 + 0.66 * (VX1 - VX0), VY0 + 0.20 * (VY1 - VY0), 'River Mersey', fontsize=7, color='#6F93A3', style='italic',
         rotation=-40, ha='center', va='center', zorder=7)
sx, sy = VX1 - 4 * M_PER_MM_B - 2000, VY0 + 3 * M_PER_MM_B
axB.add_patch(Rectangle((sx, sy), 1000, 0.6 * M_PER_MM_B, color=INK, zorder=40, lw=0))
axB.add_patch(Rectangle((sx + 1000, sy), 1000, 0.6 * M_PER_MM_B, facecolor='white', edgecolor=INK, lw=0.4, zorder=40))
for k, t in [(0, '0'), (1000, '1'), (2000, '2 km')]:
    axB.text(sx + k, sy + 1.6 * M_PER_MM_B, t, fontsize=7, ha='center', va='bottom', zorder=40, path_effects=halo(1.2))

# ---------------- UK locator (inside right column)
LOC_Y = MAP_Y + 0.5
LOC_H = (FH - 9 - BH) - 5 - LOC_Y
axU = ax_mm(133, LOC_Y, LOC_H * 0.6, LOC_H)
ctry = load('ons_countries24_buc')
ctry.plot(ax=axU, color='#ECE9E3', edgecolor='#B5AC9C', lw=0.3)
axU.set_xlim(20000, 660000); axU.set_ylim(0, 1000000)
axU.set_aspect('equal', adjustable='datalim'); axU.axis('off')
uk = sites[sites.city_frame == 'UK']
axU.scatter(uk.x, uk.y, s=3.5, color='white', edgecolor=SAT_C, lw=0.5, zorder=5)
for (x0, y0, x1, y1), lab in [((LX0, LY0, LX1, LY1), 'A'), ((VX0, VY0, VX1, VY1), 'B')]:
    axU.add_patch(Rectangle((x0 - 9000, y0 - 9000), x1 - x0 + 18000, y1 - y0 + 18000, facecolor='none', edgecolor=INK, lw=0.7, zorder=6))
    axU.text(x0 - 22000, (y0 + y1) / 2, lab, fontsize=7, fontweight='bold', ha='right', va='center', zorder=7)
axU.text(0.0, 1.0, 'UK', transform=axU.transAxes, fontsize=7, color=INK2, va='top')

# ---------------- colour bar (right column, beside locator)
CBY = LOC_Y + LOC_H - 11.5
axC = ax_mm(156.5, CBY, 30.5, 2.0)
cb = plt.colorbar(ScalarMappable(norm=norm, cmap=REC_CMAP), cax=axC, orientation='horizontal')
cb.outline.set_linewidth(0.4); cb.set_ticks([0, 0.25, 0.5, 0.75, 1]); cb.ax.set_xticklabels(['0', '.25', '.50', '.75', '1'])
cb.ax.tick_params(labelsize=7, length=1.5, width=0.4, pad=1)
axC.plot([0.9, 0.9], [0, 1], color=INK, lw=0.6, transform=axC.transAxes)
axC.text(0.9, 1.3, 'τ = 0.90', transform=axC.transAxes, fontsize=7, ha='center', va='bottom', style='italic')
fig.text(156.5 / FW, (CBY + 11.0) / FH, 'Node colour:\nweakest mission\nFY2024/25', fontsize=7, va='top', ha='left',
         linespacing=1.0, fontweight='bold')
fig.text(156.5 / FW, (CBY - 5.0) / FH, 'Mission output ÷\nFY2018/19, capped at 1;\ncolour = minimum of\nfive missions.',
         fontsize=7, va='top', ha='left', color=INK2, linespacing=1.05)

# ---------------- size + symbol legend box inside map A (bottom-right)
lx0, ly0 = LX0 + 1.5 * M_PER_MM_A, LY0 + 1.5 * M_PER_MM_A
axA.add_patch(FancyBboxPatch((lx0, ly0), 49.0 * M_PER_MM_A, 29.5 * M_PER_MM_A, boxstyle='round,pad=0,rounding_size=60',
                             facecolor='white', edgecolor='#C9CED4', lw=0.4, alpha=0.93, zorder=45))
def mmA(dx, dy): return lx0 + dx * M_PER_MM_A, ly0 + dy * M_PER_MM_A
axA.text(*mmA(1.8, 27.4), 'Node size: real Grant-in-Aid,\nFY2024/25 ÷ FY2018/19', fontsize=7, fontweight='bold', va='top', zorder=46, linespacing=1.0)
for i, v in enumerate([1.0, 1.25, 1.5]):
    cx, cy = mmA(6 + i * 12.0, 15.3)
    axA.add_patch(Circle((cx, cy), R_UNIT_MM * v * M_PER_MM_A, facecolor='#E9E6E0', edgecolor=INK, lw=0.4, zorder=46))
    axA.add_patch(Circle((cx, cy), R_UNIT_MM * M_PER_MM_A, facecolor='none', edgecolor=INK, lw=0.4, ls=(0, (1.6, 1.1)), zorder=46))
    axA.text(cx, cy - (R_UNIT_MM * v + 1.4) * M_PER_MM_A, f'×{v:.2f}', fontsize=7, ha='center', va='top', zorder=46)
axA.text(*mmA(1.8, 6.0), 'dashed ring = FY2018/19 level (×1.00)', fontsize=7, color=INK2, va='center', zorder=46)
sym_y = 2.6
axA.scatter(*mmA(2.6, sym_y), s=7, color='white', edgecolor=SAT_C, lw=0.6, zorder=46)
axA.text(*mmA(4.0, sym_y), 'other site of group', fontsize=7, color=INK2, va='center', zorder=46)
axA.scatter(*mmA(26.0, sym_y), s=10, marker='D', facecolor='white', edgecolor='#7D8590', lw=0.6, zorder=46)
axA.text(*mmA(27.5, sym_y), 'not in 5-mission panel', fontsize=7, color=INK2, va='center', zorder=46)

# ---------------- Panel C: mission cards (rank order = map numbers)
BN = {'total_visits': 'Visits', 'under16': 'U16', 'formal_education': 'Formal ed.',
      'onsite_U18': 'On-site U18', 'UK_loan_venues': 'Loans'}
FULLN = {'British Museum': 'British Museum', 'Horniman Museum': 'Horniman Museum', 'Imperial War Museum': 'Imperial War Museums',
         'National Museums Liverpool': 'National Museums Liverpool', 'Natural History Museum': 'Natural History Museum',
         'Royal Museums Greenwich': 'Royal Museums Greenwich', 'Science Museum Group': 'Science Museum Group',
         "Sir John Soane's Museum": "Sir John Soane's Museum", 'Tate Gallery': 'Tate', 'Victoria and Albert Museum': 'Victoria and Albert Museum'}
CW, CX0, CY0 = 36.0, 5.0, 3.0
CH = (MAP_Y - 9.5 - CY0) / 2
ang = np.pi / 2 - np.arange(5) * 2 * np.pi / 5
WORST_C = '#B83A3A'; EQ_C = '#3D4651'
for i, g in enumerate(order):
    row, colm = divmod(i, 5)
    cx = CX0 + colm * CW; cy = CY0 + (1 - row) * CH
    fig.patches.append(FancyBboxPatch((cx / FW + 0.8 / FW, cy / FH + 0.6 / FH), (CW - 1.6) / FW, (CH - 1.2) / FH,
                       boxstyle='round,pad=0,rounding_size=0.006', transform=fig.transFigure, facecolor='#FAF9F6',
                       edgecolor='#DEDAD2', lw=0.45, zorder=-10))
    e = end.loc[g]; wv = e.worst_mission_score
    # badge + header
    axb = ax_mm(cx + 1.9, cy + CH - 6.4, 4.2, 4.2); axb.set_xlim(-1, 1); axb.set_ylim(-1, 1); axb.axis('off')
    axb.add_patch(Circle((0, 0), 0.98, facecolor=ncol(wv), edgecolor=INK, lw=0.45))
    axb.text(0, -0.03, str(NUM[g]), ha='center', va='center', fontsize=7, fontweight='bold',
             color='white' if (wv < 0.42 or wv > 0.97) else INK)
    fig.text((cx + 7.0) / FW, (cy + CH - 2.6) / FH, SHORTNAME[g], fontsize=7, fontweight='bold', va='top', ha='left')
    fig.text((cx + 7.0) / FW, (cy + CH - 5.6) / FH, f"GIA ×{e.real_GIA_ratio:.2f}  ·  EW {e.equal_weight_score:.2f}",
             fontsize=7, va='top', ha='left', color=INK2)
    # radar
    axr = ax_mm(cx + 3.6, cy + 8.0, 15.6, 15.6, projection='polar')
    vals = e[MISSIONS].values.astype(float)
    th = np.r_[ang, ang[0]]; vv = np.r_[vals, vals[0]]
    for rr, ls, lw_, c_ in [(0.5, '-', 0.3, '#D5D0C7'), (0.9, (0, (1.6, 1.1)), 0.45, INK2), (1.0, '-', 0.45, '#B9B2A6')]:
        axr.plot(np.linspace(0, 2 * np.pi, 121), np.full(121, rr), color=c_, lw=lw_, ls=ls, zorder=1)
    for a_ in ang: axr.plot([a_, a_], [0, 1], color='#D5D0C7', lw=0.3, zorder=1)
    axr.fill(th, vv, color=ncol(wv), alpha=0.75, zorder=2, lw=0)
    axr.plot(th, vv, color=INK, lw=0.55, zorder=3)
    k = int(np.argmin(vals))
    axr.scatter([ang[k]], [vals[k]], s=9, color=WORST_C, edgecolor='white', lw=0.5, zorder=4)
    axr.set_ylim(0, 1.0); axr.set_xticks([]); axr.set_yticks([]); axr.spines['polar'].set_visible(False)
    axr.set_facecolor('none')
    fig.text((cx + 2.4) / FW, (cy + 3.0) / FH, f"{BN[e.bottleneck_missions_pipe.split('|')[0]]} {wv:.2f}",
             fontsize=7, ha='left', va='center', color=WORST_C, fontweight='bold')
    # sparkline (five-year)
    axs = ax_mm(cx + 23.4, cy + 8.0, 11.0, 15.6)
    sub = d[d.museum_group == g].sort_values('FY_start')
    xx = np.arange(5)
    axs.fill_between(xx, sub.worst_mission_score, sub.equal_weight_score, color='#E7E1D6', lw=0, zorder=1)
    axs.axhline(0.9, color=INK2, lw=0.45, ls=(0, (1.6, 1.1)), zorder=1)
    axs.plot(xx, sub.equal_weight_score, color=EQ_C, lw=0.85, zorder=3)
    axs.plot(xx, sub.worst_mission_score, color=WORST_C, lw=0.85, zorder=3)
    axs.scatter([4], [sub.worst_mission_score.iloc[-1]], s=6, color=WORST_C, zorder=4, lw=0)
    axs.scatter([4], [sub.equal_weight_score.iloc[-1]], s=6, color=EQ_C, zorder=4, lw=0)
    axs.set_xlim(-0.25, 4.25); axs.set_ylim(0, 1.04)
    axs.set_xticks([0, 4]); axs.set_xticklabels([])
    axs.set_yticks([0, 0.5, 1]); axs.set_yticklabels([], fontsize=7)
    axs.tick_params(length=1.4, pad=0.8, width=0.4)
    axs.set_facecolor('none')
    for sp in ['left', 'bottom']: axs.spines[sp].set_linewidth(0.4)
    span_end = sub.equal_weight_score.iloc[-1] - sub.worst_mission_score.iloc[-1]
    fig.text((cx + CW - 1.8) / FW, (cy + 6.0) / FH, f"gap {span_end:.2f}", fontsize=7, ha='right', va='center', color=INK2)

# ---------------- panel letters, titles, key line
panel_label(fig, 4.0 / FW, (FH - 1.2) / FH, 'A')
panel_title(fig, 9.0 / FW, (FH - 1.9) / FH, 'London: nine study groups at their anchor sites')
panel_label(fig, 132.5 / FW, (FH - 1.2) / FH, 'B')
panel_title(fig, 137.5 / FW, (FH - 1.9) / FH, 'Liverpool inset')
yC = CY0 + 2 * CH + 2.0
panel_label(fig, 4.0 / FW, (yC + 4.6) / FH, 'C')
panel_title(fig, 9.0 / FW, (yC + 3.9) / FH, 'Group mission profiles, ordered by weakest-mission recovery (numbers match A and B)')
kx = 9.0
fig.text(kx / FW, (yC + 0.7) / FH,
         'Radar: FY2024/25 mission attainment (Visits · U16 · Edu · U18 · Loans); dashed ring = τ .90; red = weakest.',
         fontsize=7, color=INK2, va='center')
fig.text(kx / FW, (yC - 2.2) / FH,
         'Sparkline: FY20/21–24/25; equal-weight vs weakest mission; shading = masking gap.',
         fontsize=7, color=INK2, va='center')
save(fig, 'Figure1_city_atlas_multimission_recovery_v2')
