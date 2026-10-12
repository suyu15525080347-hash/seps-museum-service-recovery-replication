"""Figure 4 - Long-run mission strips FY2012/13-FY2024/25 (relative to FY2018/19), five-year AUC matrix, bottleneck tally."""
import os
import sys, numpy as np, pandas as pd, matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.cm import ScalarMappable
sys.stdout.reconfigure(encoding='utf-8')
from seps_style import *
setup()
d = pd.read_csv(os.path.join(WORK, 'fig_core5_tidy.csv'))
end = d[d.FY_start == 2024].set_index('museum_group')
order = end.worst_mission_score.sort_values().index.tolist(); NUM = {g: i + 1 for i, g in enumerate(order)}
p = pd.read_csv(os.path.join(REP, 'data', 'UK_DCMS_15_museums_FY2008_2024_annual_GIA_visits_and_outputs_official_ODS_join_v1.csv'))
tr = pd.read_csv(os.path.join(REP, 'data', 'UK_DCMS_14group_mission_temporal_resilience_trajectories_FY2020_2024_v1.csv')).set_index('museum_group')
COL = {'total_visits': 'visitors_total_actual', 'under16': 'under16_visits', 'formal_education': 'formal_education_under18_visits',
       'onsite_U18': 'organized_on_site_under18_participations', 'UK_loan_venues': 'UK_loan_venues'}
YEARS = list(range(2012, 2025)); LOAN_FIRST = 2016   # DCMS notes: UK loan-venue series not comparable before FY2016/17
R = {}   # (group, mission, year) -> ratio to FY2018/19
for g in order:
    pg = p[p.museum_group == g].set_index('year_start')
    for m in MISSIONS:
        v = pd.to_numeric(pg[COL[m]], errors='coerce')
        if m == 'UK_loan_venues':   # FY2024/25 loan value from audited derived series (Table 9 header QA)
            v.loc[2024] = float(tr.loc[g, 'UK_loan_venues_postshock_raw_values_pipe'].split('|')[-1])
        base = v.loc[2018]
        for y in YEARS:
            ok = not (m == 'UK_loan_venues' and y < LOAN_FIRST)
            R[(g, m, y)] = (v.loc[y] / base) if (ok and pd.notna(v.loc[y]) and base > 0) else np.nan
# consistency check: post-shock ratios equal the frozen benchmark raw ratios
for _, r in d.iterrows():
    for m in MISSIONS:
        assert abs(R[(r.museum_group, m, r.FY_start)] - r['raw_' + m]) < 2e-5, (r.museum_group, m, r.FY_start)
auc = d.groupby('museum_group')[MISSIONS].mean()
wauc = auc.min(axis=1)
assert round(wauc.median(), 4) == 0.3737, wauc.median()
# extended colour scale: 0..1 = recovery cmap (as Figs 1-3); >1 = darker teal (above FY2018/19 level, display only)
EXT = LinearSegmentedColormap.from_list('ext', ['#2E7D74', '#123F3A'])
def ccol(r):
    if np.isnan(r): return None
    return REC_CMAP(min(r, 1.0)) if r <= 1 else EXT(min((r - 1) / 0.5, 1.0))
FW, FH = 190, 195
fig = plt.figure(figsize=(FW * MM, FH * MM))
def ax_mm(x, y, w, h, **kw): return fig.add_axes([x / FW, y / FH, w / FW, h / FH], **kw)
SH, BG = 2.60, 1.9      # strip height, block gap (mm)
TOP = FH - 16.0
XL0, CWm = 37.0, 7.15    # x of first year column, column width (mm)
axA = ax_mm(0, 0, FW, FH); axA.set_xlim(0, FW); axA.set_ylim(0, FH); axA.axis('off')
ROWY = {}
for gi, g in enumerate(order):
    y_blk = TOP - gi * (5 * SH + BG)
    ROWY[g] = y_blk
    for mi, m in enumerate(MISSIONS):
        yy = y_blk - (mi + 1) * SH
        for yi, y in enumerate(YEARS):
            x = XL0 + yi * CWm
            r = R[(g, m, y)]
            c = ccol(r)
            if c is None:
                axA.add_patch(Rectangle((x, yy), CWm - 0.25, SH - 0.22, facecolor='#F1EFEA', edgecolor='#D9D4CA', lw=0.25, hatch='//////'))
            else:
                axA.add_patch(Rectangle((x, yy), CWm - 0.25, SH - 0.22, facecolor=c, edgecolor='none'))
        axA.text(XL0 - 0.8, yy + SH / 2 - 0.1, MSHORT[m], fontsize=7, ha='right', va='center', color=INK2)
    # bottleneck markers (post-shock, weakest mission per year)
    for _, r in d[d.museum_group == g].iterrows():
        k = MISSIONS.index(r.bottleneck_missions_pipe.split('|')[0])
        x = XL0 + YEARS.index(int(r.FY_start)) * CWm + (CWm - 0.25) / 2
        axA.add_patch(Circle((x, y_blk - (k + 1) * SH + SH / 2 - 0.11), 0.42, facecolor='white', edgecolor=INK, lw=0.45, zorder=5))
    # group label
    wv = end.loc[g, 'worst_mission_score']
    axA.add_patch(Circle((4.6, y_blk - 2.5 * SH), 1.9, facecolor=REC_CMAP(wv), edgecolor=INK, lw=0.45))
    axA.text(4.6, y_blk - 2.5 * SH - 0.05, str(NUM[g]), fontsize=7, fontweight='bold', ha='center', va='center',
             color='white' if (wv < 0.42 or wv > 0.97) else INK)
    nm = {'Victoria and Albert Museum': 'V&A', 'Imperial War Museum': 'IWM', 'National Museums Liverpool': 'NML',
          "Sir John Soane's Museum": "Soane's", 'Royal Museums Greenwich': 'RMG', 'Science Museum Group': 'SMG',
          'Natural History Museum': 'NHM', 'Tate Gallery': 'Tate'}.get(g, g)
    axA.text(7.4, y_blk - 2.5 * SH, nm, fontsize=7, fontweight='bold', ha='left', va='center')
BOT = TOP - 10 * (5 * SH + BG) + BG

# year header + baseline/shock markers
for yi, y in enumerate(YEARS):
    x = XL0 + yi * CWm + (CWm - 0.25) / 2
    axA.text(x, TOP + 1.1, f'{str(y)[2:]}/{str(y + 1)[2:]}', fontsize=7, ha='left', va='bottom', rotation=55, rotation_mode='anchor',
             fontweight='bold' if y in (2018, 2020) else 'normal')
xb = XL0 + YEARS.index(2018) * CWm
axA.add_patch(Rectangle((xb - 0.25, BOT - 0.35), CWm + 0.25, TOP - BOT + 0.6, facecolor='none', edgecolor=INK, lw=0.7, zorder=6))
xs = XL0 + YEARS.index(2020) * CWm - 0.2
axA.plot([xs, xs], [BOT - 0.4, TOP + 0.3], color=INK, lw=0.6, ls=(0, (2, 1.2)), zorder=6)
def bracket(x0, x1, y, txt):
    axA.plot([x0, x0, x1, x1], [y - 0.6, y, y, y - 0.6], color=INK2, lw=0.45)
    axA.text((x0 + x1) / 2, y + 0.4, txt, fontsize=7, ha='center', va='bottom', color=INK2)
# bottleneck tally aligned with post-shock columns
TY = BOT - 4.0; US = 1.75
axA.text(XL0 + YEARS.index(2020) * CWm - 1.2, TY - 2.5 * US, 'weakest mission\n(10 museum-years/year)',
         fontsize=7, ha='right', va='center', color=INK2, linespacing=1.05)
tot = {}
for y in range(2020, 2025):
    bn = d[d.FY_start == y].bottleneck_missions_pipe.str.split('|').str[0]
    bn = sorted(bn, key=lambda m: MISSIONS.index(m))
    x0 = XL0 + YEARS.index(y) * CWm + (CWm - 0.25) / 2 - US
    for k, m in enumerate(bn):
        rr, cc = divmod(k, 2)
        axA.add_patch(Rectangle((x0 + cc * US, TY - (rr + 1) * US), US - 0.25, US - 0.25, facecolor=MCOL[m], edgecolor='none'))
        tot[m] = tot.get(m, 0) + 1
assert tot == {'formal_education': 23, 'onsite_U18': 14, 'UK_loan_venues': 9, 'total_visits': 2, 'under16': 2}
legend_items = [
    ('formal_education', 'Edu 23', 37.0),
    ('onsite_U18', 'U18 14', 56.0),
    ('UK_loan_venues', 'Loans 9', 75.0),
    ('total_visits', 'Visits 2', 96.0),
    ('under16', 'U16 2', 117.0),
]
for m, lab, lx in legend_items:
    axA.add_patch(Rectangle((lx, 13.2), US - 0.25, US - 0.25, facecolor=MCOL[m], edgecolor='none'))
    axA.text(lx + US + 0.4, 13.2 + (US - 0.25)/2, lab, fontsize=7, va='center')
# colour legend for strips
axL = ax_mm(XL0, 5.0, 46, 1.8)
cb = plt.colorbar(ScalarMappable(norm=Normalize(0, 1), cmap=REC_CMAP), cax=axL, orientation='horizontal')
cb.outline.set_linewidth(0.4); cb.set_ticks([0, 0.25, 0.5, 0.75, 1]); cb.ax.tick_params(labelsize=7, length=1.4, width=0.4, pad=1)
axL2 = ax_mm(XL0 + 47.5, 5.0, 12, 1.8)
cb2 = plt.colorbar(ScalarMappable(norm=Normalize(1, 1.5), cmap=EXT), cax=axL2, orientation='horizontal')
cb2.outline.set_linewidth(0.4); cb2.set_ticks([1.25, 1.5]); cb2.ax.set_xticklabels(['1.25', '≥1.5']); cb2.ax.tick_params(labelsize=7, length=1.4, width=0.4, pad=1)
fig.text(XL0 / FW, 8.6 / FH, 'Output ÷ FY2018/19; ≤1 uses recovery scale; >1 darker (display only)',
         fontsize=7, color=INK2, va='bottom')
axA.add_patch(Rectangle((102.0, 4.9), 3.2, 1.9, facecolor='#F1EFEA', edgecolor='#D9D4CA', lw=0.25, hatch='//////'))
axA.text(106.0, 5.85, 'not collected / not comparable', fontsize=7, va='center', color=INK2)
axA.add_patch(Circle((153.0, 5.85), 0.42, facecolor='white', edgecolor=INK, lw=0.45))
axA.text(155.0, 5.85, 'weakest', fontsize=7, va='center', color=INK2)

# ---------------- B: five-year AUC matrix + weakest-mission AUC dot plot
BX0, BCW = 137.0, 6.1
for mi, m in enumerate(MISSIONS):
    axA.text(BX0 + mi * BCW, TOP + 1.1, MSHORT[m], fontsize=7, ha='center', va='bottom', fontweight='bold')
DX0, DX1 = BX0 + 5 * BCW - 0.4, 187.0          # weakest-AUC axis
def dx(v): return DX0 + v * (DX1 - DX0)
for g in order:
    yc = ROWY[g] - 2.5 * SH
    for mi, m in enumerate(MISSIONS):
        v = auc.loc[g, m]
        axA.add_patch(Circle((BX0 + mi * BCW, yc), 2.55, facecolor=REC_CMAP(v), edgecolor='white', lw=0.5))
        axA.text(BX0 + mi * BCW, yc - 0.05, f'{v:.2f}'[1:] if v < 1 else '1.0', fontsize=7, ha='center', va='center',
                 color='white' if (v < 0.42 or v > 0.97) else INK)
        if m == auc.loc[g].idxmin():
            axA.add_patch(Circle((BX0 + mi * BCW, yc), 2.85, facecolor='none', edgecolor=INK, lw=0.6))
    axA.plot([DX0, DX1], [yc, yc], color=RULE, lw=0.4)
    axA.add_patch(Circle((dx(wauc.loc[g]), yc), 0.95, facecolor=REC_CMAP(wauc.loc[g]), edgecolor=INK, lw=0.45, zorder=5))
med = wauc.median()
axA.plot([dx(med)] * 2, [BOT - 0.4, TOP + 0.3], color=STATE['RED'], lw=0.6, ls=(0, (2, 1.2)))
axA.text(dx(med), BOT - 1.0, f'median\n{med:.4f}', fontsize=7, ha='center', va='top', color=STATE['RED'], linespacing=1.0)
for v in (0, 0.5, 1):
    axA.text(dx(v), TOP + 1.1, f'{v:g}', fontsize=7, ha='center', va='bottom', color=INK2)
    axA.plot([dx(v)] * 2, [TOP + 0.2, TOP + 0.8], color=INK2, lw=0.4)
axA.text((DX0 + DX1) / 2, TOP + 5.4, 'weakest\nmission AUC', fontsize=7, ha='center', va='bottom', fontweight='bold', linespacing=1.0)
axA.text(BX0 + 2 * BCW, TOP + 5.4, 'five-year mean attainment\n(AUC), FY20/21–24/25', fontsize=7, ha='center', va='bottom',
         fontweight='bold', linespacing=1.0)
# ---------------- titles
panel_label(fig, 2.5 / FW, (FH - 1.0) / FH, 'A')
panel_title(fig, 8.0 / FW, (FH - 1.7) / FH, 'Thirteen-year mission outputs: common shock, uneven recovery')
panel_label(fig, (BX0 - 4.5) / FW, (FH - 1.0) / FH, 'B')
fig.text((BX0 - 0.5) / FW, (FH - 1.7) / FH, 'Five-year cumulative recovery', fontsize=7, fontweight='bold', va='top')
save(fig, 'Figure4_long_run_mission_strips_v2')
print(auc.round(3).to_string()); print(wauc.round(4).to_string())
