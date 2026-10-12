"""Figure 5 - (A) mean five-mission recovery trajectories FY2020/21-2024/25 (10 groups);
(B) same 11 museums, four missions: short-horizon normal, horizon-matched normal (pre-specified check) and late recovery."""
import os
import sys, json, numpy as np, pandas as pd, matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
sys.stdout.reconfigure(encoding='utf-8')
from seps_style import *
setup()
d = pd.read_csv(os.path.join(WORK, 'fig_core5_tidy.csv'))
hz = pd.read_csv(os.path.join(WORK, 'horizon', 'horizon_matched_museum_year_detail_v1.csv'))
FW, FH = 190, 102
fig = plt.figure(figsize=(FW * MM, FH * MM))
def ax_mm(x, y, w, h, **kw): return fig.add_axes([x / FW, y / FH, w / FW, h / FH], **kw)
# ---------------- A
axA = ax_mm(14, 18, 84, 68)
x = np.arange(5)
mean = d.groupby('FY_start')[MISSIONS].mean()
for m in MISSIONS:
    axA.plot(x, mean[m], color=MCOL[m], lw=1.5, marker='o', ms=3.2, mec='white', mew=0.5, zorder=3)
ends = mean.loc[2024].sort_values(); ylab = {}; last = -1
for m, v in ends.items():
    yv = max(v, last + 0.045); ylab[m] = yv; last = yv
for m in MISSIONS:
    axA.plot([4.06, 4.22], [mean.loc[2024, m], ylab[m]], color=MCOL[m], lw=0.5)
    axA.text(4.26, ylab[m], f'{MLABEL[m]}  {mean.loc[2024, m]:.2f}', color=MCOL[m], fontsize=7, va='center', fontweight='bold')
axA.axhline(0.9, color=INK, lw=0.55, ls=(0, (2.2, 1.4)))
axA.text(0.0, 0.88, 'τ = 0.90', fontsize=7, style='italic', va='top', ha='left')
axA.set_xlim(-0.2, 5.6); axA.set_ylim(0, 1.0); axA.set_xticks(x); axA.set_xticklabels([f'FY{f}' for f in FY])
axA.spines['bottom'].set_bounds(0, 4); axA.set_ylabel('Mean capped attainment (10 groups)')
axA.text(0.02, 0.97, 'Mean capped attainment across the 10 complete five-mission groups.',
         transform=axA.transAxes, fontsize=7, color=INK2, va='top')
# ---------------- B
P = [('S3_short_1to2y_reference', 'normal', 'Normal\n1–2 y'), ('PRIMARY_4to6y', 'normal', 'Normal\n4–6 y'), ('PRIMARY_4to6y', 'late', 'Late\nrecovery\n4–6 y')]
cols = [hz[(hz.spec == s) & (hz.period == per)] for s, per, _ in P]
pm = pd.concat([c.groupby('museum_group').masking.mean().rename(i) for i, c in enumerate(cols)], axis=1)
end = d[d.FY_start == 2024].set_index('museum_group')
order = end.worst_mission_score.sort_values().index.tolist(); NUM = {g: i + 1 for i, g in enumerate(order)}
axB = ax_mm(121, 18, 42, 68)
pm = pm.sort_values(2); last = -1
for gname, r in pm.iterrows():
    axB.plot([0, 1, 2], r.values, color='#B9B2A6', lw=0.6, zorder=2)
    axB.scatter([0, 1, 2], r.values, s=8, color=['#9DB4C4', '#6F8FA3', STATE['RED']], edgecolor='white', lw=0.3, zorder=3)
    lab = str(NUM[gname]) if gname in NUM else {'National Gallery': 'NG', 'Royal Armouries': 'RA', 'Wallace Collection': 'WC'}.get(gname, '?')
    yl = max(r[2], last + 0.0125); last = yl
    axB.text(2.08, yl, lab, fontsize=7, va='center', color=INK if gname in NUM else INK3, fontweight='bold')
means = [c.masking.mean() for c in cols]
assert [round(v, 4) for v in means] == [0.0711, 0.1807, 0.2149], means
axB.plot([0, 1, 2], means, color=INK, lw=1.8, zorder=4); axB.scatter([0, 1, 2], means, s=30, color=INK, marker='D', zorder=5)
for i, v in enumerate(means):
    axB.text(i - 0.12, v - (0.03 if i == 2 else 0), f'{v:.3f}', fontsize=7, ha='right', va='center', fontweight='bold',
             path_effects=halo(1.8), zorder=6)
mx = [c[c.museum_group != 'Royal Armouries'].masking.mean() for c in cols]     # post-hoc sensitivity (see text)
axB.plot([0, 1, 2], mx, color=INK, lw=0.8, ls=(0, (2, 1.2)), zorder=4)
axB.scatter([0, 1, 2], mx, s=26, facecolor='white', edgecolor=INK, lw=0.8, marker='D', zorder=5)
axB.text(1.0 + 0.12, mx[1], f'{mx[1]:.3f}', fontsize=7, ha='left', va='top', color=INK2, path_effects=halo(1.5), zorder=6)
axB.text(2.0 - 0.1, mx[2] + 0.03, f'{mx[2]:.3f}', fontsize=7, ha='right', va='bottom', color=INK2, path_effects=halo(1.5), zorder=6)
ra = pm.loc['Royal Armouries', 1]
axB.annotate('RA: on-site U18 falls 96% in one\nyear (FY15/16→16/17), apparent\nreporting break', xy=(1, ra), xytext=(1.12, ra - 0.02),
             fontsize=7, color=INK2, va='top', ha='left', arrowprops=dict(arrowstyle='-', color=INK3, lw=0.4), linespacing=1.0)
ymax = max(pm.max().max() * 1.12, 0.5)
for i, c in enumerate(cols):
    axB.text(i, ymax * 0.99, f'weakest\nmean {c.weakest.mean():.2f}', fontsize=7, ha='center', va='top', color=INK2, linespacing=1.0)
axB.set_xlim(-0.55, 2.4); axB.set_ylim(0, ymax); axB.set_xticks([0, 1, 2]); axB.set_xticklabels([p[2] for p in P], fontsize=7)
axB.set_ylabel('Mean equal-weight masking span (four missions)')
axS = ax_mm(166, 18, 23, 68); axS.set_xlim(0, 10); axS.set_ylim(0, 40); axS.axis('off')
for ci, c in enumerate(cols):
    s = c.state90.value_counts()
    seq = ['GREEN'] * s.get('GREEN', 0) + ['AMBER'] * s.get('AMBER', 0) + ['RED'] * s.get('RED', 0)
    x0 = 0.15 + ci * 3.35
    for k, st_ in enumerate(seq):
        rr, cc = divmod(k, 3)
        axS.add_patch(Rectangle((x0 + cc * 0.98, 1.0 + rr * 0.98 * 1.62), 0.84, 0.84 * 1.62, facecolor=STATE[st_], edgecolor='none'))
    top = 1.0 + int(np.ceil(len(seq) / 3)) * 0.98 * 1.62
    axS.text(x0 + 1.4, top + 0.5, f"{s.get('RED', 0)} R\n{s.get('AMBER', 0)} A\n{s.get('GREEN', 0)} G", fontsize=7,
             ha='center', va='bottom', linespacing=1.0)
    axS.text(x0 + 1.4, 0.3, ['1–2 y', '4–6 y', 'late'][ci], fontsize=7, ha='center', va='top')
assert dict(cols[1].state90.value_counts()) == {'AMBER': 20, 'GREEN': 13}
assert dict(cols[2].state90.value_counts()) == {'AMBER': 15, 'RED': 14, 'GREEN': 4}
fig.text(121.0 / FW, 5.0 / FH,
         '◆ all 11, pre-specified     ◇ excluding RA, post hoc',
         fontsize=7, color=INK2, va='center')
panel_label(fig, 2.5 / FW, (FH - 1.0) / FH, 'A')
panel_title(fig, 8.0 / FW, (FH - 1.7) / FH, 'Five-year paths: attendance leads; youth learning and loans lag')
panel_label(fig, 113.0 / FW, (FH - 1.0) / FH, 'B')
panel_title(fig, 118.0 / FW, (FH - 1.7) / FH, 'Matched normal years vs late recovery')
fig.text(118.0 / FW, (FH - 5.6) / FH,
         'Masking rises with horizon even in normal years.\n'
         'Recovery mainly deepens shortfall (RED).\n'
         'Four missions; τ = 0.90 states at right.',
         fontsize=7, color=INK2, va='top', linespacing=1.05)
save(fig, 'Figure5_mission_trajectories_and_normal_period_contrast_v2')
print(pm.round(3).to_string())
