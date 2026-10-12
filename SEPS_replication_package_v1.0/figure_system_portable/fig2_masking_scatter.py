"""Figure 2 - Equal-weight score vs weakest-mission attainment, 50 museum-years (unified-style re-render)."""
import os
import sys, numpy as np, pandas as pd, matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
from matplotlib.lines import Line2D
sys.stdout.reconfigure(encoding='utf-8')
from seps_style import *
setup()
d = pd.read_csv(os.path.join(WORK, 'fig_core5_tidy.csv'))
end = d[d.FY_start == 2024].set_index('museum_group')
order = end.worst_mission_score.sort_values().index.tolist(); NUM = {g: i + 1 for i, g in enumerate(order)}
d['bn'] = d.bottleneck_missions_pipe.str.split('|').str[0]
TAU = 0.90
eqp = (d.equal_weight_score >= TAU); allp = (d.worst_mission_score >= TAU)
assert eqp.sum() == 6 and allp.sum() == 2 and (eqp & ~allp).sum() == 4

FW, FH = 190, 118
fig = plt.figure(figsize=(FW * MM, FH * MM))
ax = fig.add_axes([13 / FW, 11 / FH, 104 / FW, 92 / FH])
ax.set_xlim(0, 1.02); ax.set_ylim(0, 1.02); ax.set_aspect('equal')
# masked zone: equal-weight passes, weakest mission below tau
ax.add_patch(Rectangle((TAU, 0), 1.02 - TAU, TAU, facecolor=STATE_LIGHT['AMBER'], edgecolor='none', zorder=0))
ax.add_patch(Rectangle((TAU, TAU), 1.02 - TAU, 1.02 - TAU, facecolor=STATE_LIGHT['GREEN'], edgecolor='none', zorder=0))
ax.plot([0, 1.02], [0, 1.02], color=INK2, lw=0.6, zorder=1)
ax.text(0.47, 0.505, 'equal weight = weakest mission (no masking)', rotation=45, fontsize=7, color=INK2, ha='center', va='bottom')
ax.axvline(TAU, color=INK, lw=0.55, ls=(0, (2.2, 1.4)), zorder=1); ax.axhline(TAU, color=INK, lw=0.55, ls=(0, (2.2, 1.4)), zorder=1)
# museum trajectories
for g, sub in d.sort_values('FY_start').groupby('museum_group'):   # faint group paths (context only)
    ax.plot(sub.equal_weight_score, sub.worst_mission_score, color='#D9D3C8', lw=0.4, zorder=2)
for m in MISSIONS:
    s = d[d.bn == m]
    ax.scatter(s.equal_weight_score, s.worst_mission_score, s=20, color=MCOL[m], edgecolor='white', lw=0.5, zorder=4)
e24 = d[d.FY_start == 2024]
ax.scatter(e24.equal_weight_score, e24.worst_mission_score, s=46, facecolor='none', edgecolor=INK, lw=0.6, zorder=5)
LBL = {'Horniman Museum': (-0.012, -0.035), 'Tate Gallery': (0.0, -0.036), 'National Museums Liverpool': (-0.034, 0.0),
       'Victoria and Albert Museum': (-0.034, 0.012), 'Royal Museums Greenwich': (-0.034, -0.01), 'Science Museum Group': (0.012, -0.03),
       'Natural History Museum': (-0.03, 0.022), 'Imperial War Museum': (-0.036, 0.0), "Sir John Soane's Museum": (0.0, 0.033),
       'British Museum': (-0.034, 0.012)}
for _, r in e24.iterrows():
    dx, dy = LBL[r.museum_group]
    ax.text(r.equal_weight_score + dx, r.worst_mission_score + dy, str(NUM[r.museum_group]), fontsize=7, fontweight='bold',
            ha='center', va='center', zorder=6, path_effects=halo(1.5))
# worked example of masking span (Horniman FY2024/25)
h = e24.set_index('museum_group').loc['Horniman Museum']
ax.annotate('', xy=(h.equal_weight_score, h.equal_weight_score), xytext=(h.equal_weight_score, h.worst_mission_score),
            arrowprops=dict(arrowstyle='<->', color=STATE['RED'], lw=0.7, shrinkA=2.5, shrinkB=0), zorder=3)
ax.text(h.equal_weight_score - 0.014, (h.equal_weight_score + h.worst_mission_score) / 2 + 0.02,
        f'masking span\n$M_{{it}}$ = {h.equal_weight_score - h.worst_mission_score:.2f}\n(group 1, FY2024/25)', fontsize=7,
        color=STATE['RED'], va='center', ha='right', linespacing=1.05, path_effects=halo(1.5))
ax.set_xlabel('Equal-weight attainment score, $E_{it}$', fontsize=9); ax.set_ylabel('Weakest-mission attainment, $\\min_k\\,a_{ikt}$', fontsize=9)
ax.set_xticks(np.arange(0, 1.01, 0.2)); ax.set_yticks(np.arange(0, 1.01, 0.2))
ax.text(TAU - 0.008, 1.0, 'τ = 0.90', fontsize=7, ha='right', va='top', style='italic')
ax.text(0.962, 0.40, f'Equal-weight\npass, mission\nshortfall\n(n = {(eqp & ~allp).sum()})', fontsize=7, ha='center',
        va='center', color='#8A5A10', fontweight='bold', linespacing=1.05)
ax.text(0.906, 0.906, f'all five ≥ τ\n(n = {allp.sum()})', fontsize=7, ha='left', va='bottom', color='#1F5C55',
        fontweight='bold', linespacing=1.0)

# ---------------- right column: legend + masking distribution (equal-weight vs visitor-only)
RX = 128.0
fig.text(RX / FW, 110.5 / FH, 'Point colour:\nweakest mission', fontsize=7, fontweight='bold', va='top', linespacing=1.0)
cnt = d.bn.value_counts()
for i, m in enumerate(sorted(MISSIONS, key=lambda m: -cnt.get(m, 0))):
    y = 102.5 - i * 3.6
    fig.patches.append(plt.Circle(((RX + 1.4) / FW, y / FH), 0.0075, transform=fig.transFigure, color=MCOL[m]))
    fig.text((RX + 3.4) / FW, y / FH, MLABEL[m], fontsize=7, va='center')
    fig.text((RX + 48.0) / FW, y / FH, str(cnt.get(m, 0)), fontsize=7, va='center', ha='right', fontweight='bold')
fig.text((RX + 48.0) / FW, 106.0 / FH, 'n', fontsize=7, va='center', ha='right', color=INK2, style='italic')
y0 = 82.0
fig.lines.append(Line2D([(RX + 0.2) / FW, (RX + 2.8) / FW], [y0 / FH] * 2, transform=fig.transFigure, color='#D9D3C8', lw=0.8))
fig.text((RX + 3.4) / FW, y0 / FH, 'path of one group,\nFY2020/21 → 2024/25', fontsize=7, va='center', linespacing=1.0)
fig.patches.append(plt.Circle(((RX + 1.4) / FW, (y0 - 6.2) / FH), 0.011, transform=fig.transFigure, facecolor='none', edgecolor=INK, lw=0.6))
fig.text((RX + 3.4) / FW, (y0 - 6.2) / FH, 'FY2024/25; number =\ngroup in Fig. 1', fontsize=7, va='center', linespacing=1.0)
# panel B: masking-span distributions
axB = fig.add_axes([(RX + 3.0) / FW, 13 / FH, 47 / FW, 46 / FH])
rng = np.random.default_rng(7)
for j, (col, lab, c) in enumerate([('threshold_free_equalweight_masking_span', 'Equal\nweight', '#3D4651'),
                                   ('threshold_free_visitor_masking_span', 'Visitor\nonly', '#4E8FC4')]):
    v = d[col].values
    xj = j + rng.uniform(-0.17, 0.17, len(v))
    axB.scatter(xj, v, s=5, color=c, alpha=0.55, lw=0, zorder=2)
    q1, med, q3 = np.percentile(v, [25, 50, 75])
    axB.plot([j - 0.28, j + 0.28], [med, med], color=INK, lw=1.0, zorder=3)
    axB.plot([j, j], [q1, q3], color=INK, lw=0.5, zorder=3)
    axB.scatter([j + 0.36], [v.mean()], marker='<', s=14, color=STATE['RED'], zorder=4, lw=0)
    axB.text(j, -0.075, lab, ha='center', va='top', fontsize=7, linespacing=0.95)
    axB.text(j + 0.47, v.mean(), f'{v.mean():.4f}', fontsize=7, va='center', color=STATE['RED'])
ymax = max(d.threshold_free_equalweight_masking_span.max(), d.threshold_free_visitor_masking_span.max())
print('max spans', d.threshold_free_equalweight_masking_span.max(), d.threshold_free_visitor_masking_span.max())
axB.set_xlim(-0.5, 1.75); axB.set_ylim(0, max(0.62, ymax * 1.04)); axB.set_xticks([])
axB.set_yticks(np.arange(0, ymax + 0.2, 0.2)); axB.spines['bottom'].set_visible(False)
axB.set_ylabel('Masking span vs weakest mission', fontsize=7, labelpad=1.5)
axB.text(0.0, 1.035, 'red marker = mean; bar = median;\nvertical line = interquartile range', transform=axB.transAxes,
         fontsize=7, color=INK2, va='bottom', linespacing=1.0)
assert round(d.threshold_free_equalweight_masking_span.mean(), 4) == 0.2299
panel_label(fig, 2.5 / FW, (FH - 1.0) / FH, 'A')
panel_title(fig, 8.0 / FW, (FH - 1.7) / FH, 'Equal weighting averages away the weakest mission (50 museum-years)')
panel_label(fig, (RX - 2.0) / FW, 70.0 / FH, 'B')
fig.text((RX + 3.6) / FW, 69.3 / FH, 'Masking span', fontsize=7, fontweight='bold', va='top')
save(fig, 'Figure2_equalweight_vs_weakest_mission_v2')
