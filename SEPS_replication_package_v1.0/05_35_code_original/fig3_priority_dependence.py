"""Figure 3 - Priority dependence: set-valued scores, scalar verdict -> set-valued state flows, threshold x weight-floor matrix."""
import sys, numpy as np, pandas as pd, matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, PathPatch, Circle
from matplotlib.path import Path
from matplotlib.lines import Line2D
sys.stdout.reconfigure(encoding='utf-8')
from seps_style import *
setup()
d = pd.read_csv(os.path.join(WORK, 'fig_core5_tidy.csv'))
end = d[d.FY_start == 2024].set_index('museum_group')
order = end.worst_mission_score.sort_values().index.tolist(); NUM = {g: i + 1 for i, g in enumerate(order)}
d['rank'] = d.museum_group.map(NUM); d = d.sort_values(['rank', 'FY_start']).reset_index(drop=True)
st = lambda c: d[c].str.split('_').str[0]
d['S90'] = st('robust_state_t0.90_wfloor0.00')
assert d.S90.value_counts().to_dict() == {'AMBER': 25, 'RED': 23, 'GREEN': 2}
assert np.allclose(d['robust_lower_wfloor_0.00'], d.worst_mission_score) and np.allclose(d['robust_upper_wfloor_0.00'], d.best_mission_score)
GAP = 1.6
d['xp'] = (d['rank'] - 1) * (5 + GAP) + (d.FY_start - 2020)
XMAX = d.xp.max() + 0.8
FW, FH = 190, 128
fig = plt.figure(figsize=(FW * MM, FH * MM))
def ax_mm(x, y, w, h, **kw): return fig.add_axes([x / FW, y / FH, w / FW, h / FH], **kw)
LX, LW = 16.0, 116.0
# ---------------- A: admissible score intervals
axA = ax_mm(LX, 64, LW, 48)
for _, r in d.iterrows():
    c = STATE[r.S90]
    axA.plot([r.xp, r.xp], [r['robust_lower_wfloor_0.10'], r['robust_upper_wfloor_0.10']], color=c, lw=3.4, alpha=0.30,
             solid_capstyle='butt', zorder=2)
    axA.plot([r.xp, r.xp], [r['robust_lower_wfloor_0.00'], r['robust_upper_wfloor_0.00']], color=c, lw=0.9, zorder=3)
    for yv in (r['robust_lower_wfloor_0.00'], r['robust_upper_wfloor_0.00']):
        axA.plot([r.xp - 0.22, r.xp + 0.22], [yv, yv], color=c, lw=0.9, zorder=3)
axA.scatter(d.xp, d.visitor_only_score, marker='D', s=6, color='#4E8FC4', edgecolor='white', lw=0.3, zorder=5)
axA.scatter(d.xp, d.equal_weight_score, s=8, color='white', edgecolor=INK, lw=0.6, zorder=6)
axA.axhline(0.9, color=INK, lw=0.55, ls=(0, (2.2, 1.4)), zorder=1)
axA.text(XMAX + 0.3, 0.9, 'τ = 0.90', fontsize=7, style='italic', va='center', ha='left')
for k in range(1, 10):
    axA.axvline(k * (5 + GAP) - GAP / 2 - 0.5, color=RULE, lw=0.4, zorder=0)
axA.set_xlim(-0.8, XMAX); axA.set_ylim(-0.02, 1.04); axA.set_xticks([])
axA.set_yticks([0, 0.25, 0.5, 0.75, 1]); axA.set_ylabel('Admissible composite score $S_{it}(w)$', fontsize=9)
axA.spines['bottom'].set_visible(False)
# group labels between A and C
for g, k in NUM.items():
    xc = (k - 1) * (5 + GAP) + 2
    axA.text(xc, -0.07, f'{k}', fontsize=7, fontweight='bold', ha='center', va='top', transform=axA.transData, clip_on=False)
    axA.text(xc, -0.145, ABBR[g], fontsize=7, ha='center', va='top', color=INK2, transform=axA.transData, clip_on=False)

# ---------------- C: state matrix, threshold x weight floor
TAUS = ['0.75', '0.80', '0.90', '1.00']; EPS = ['0.00', '0.05', '0.10']
rows = [(t, e) for t in TAUS for e in EPS]
axC = ax_mm(LX, 8, LW, 40)
summ = []
for i, (t, e) in enumerate(rows):
    s = st(f'robust_state_t{t}_wfloor{e}')
    y = len(rows) - 1 - i
    for x, v in zip(d.xp, s):
        axC.add_patch(Rectangle((x - 0.45, y - 0.42), 0.9, 0.84, facecolor=STATE[v], edgecolor='none', lw=0))
    vc = s.value_counts(); summ.append((t, e, vc.get('RED', 0), vc.get('AMBER', 0), vc.get('GREEN', 0)))
    axC.text(XMAX + 1.6, y, f'{vc.get("RED", 0)}', fontsize=7, ha='right', va='center', color=STATE['RED'], fontweight='bold')
    axC.text(XMAX + 3.9, y, f'{vc.get("AMBER", 0)}', fontsize=7, ha='right', va='center', color='#A86F14', fontweight='bold')
    axC.text(XMAX + 6.0, y, f'{vc.get("GREEN", 0)}', fontsize=7, ha='right', va='center', color=STATE['GREEN'], fontweight='bold')
for i, (t, e) in enumerate(rows):
    y = len(rows) - 1 - i
    axC.text(-0.9, y, f'ε={float(e):.2f}', fontsize=7, ha='right', va='center', color=INK2, clip_on=False)
for j, t in enumerate(TAUS):
    yc = len(rows) - 1 - (3 * j + 1)
    axC.text(-6.6, yc, f'τ = {t}', fontsize=7, ha='center', va='center', clip_on=False, fontweight='bold', rotation=90)
    if j: axC.axhline(len(rows) - 3 * j - 0.5, color='white', lw=1.6)
# highlight primary specification row
yp = len(rows) - 1 - rows.index(('0.90', '0.00'))
axC.add_patch(Rectangle((-0.75, yp - 0.55), XMAX + 0.1, 1.1, facecolor='none', edgecolor=INK, lw=0.8, zorder=5))
for lab, xo in [('R', 1.6), ('A', 3.9), ('G', 6.0)]:
    axC.text(XMAX + xo, len(rows) - 0.3, lab, fontsize=7, ha='right', va='bottom', color=INK2)
axC.set_xlim(-0.8, XMAX); axC.set_ylim(-0.6, len(rows) - 0.4); axC.axis('off')
s90 = [x for x in summ if x[0] == '0.90' and x[1] == '0.00'][0]
assert s90[2:] == (23, 25, 2), s90
print(pd.DataFrame(summ, columns=['tau', 'eps', 'RED', 'AMBER', 'GREEN']).to_string())

# ---------------- B: scalar verdict -> set-valued state (alluvial, tau = 0.90, eps = 0)
vis = np.where(d['visitor_pass_0.90'] == 1, 'pass', 'fail'); eqv = np.where(d['equalweight_pass_0.90'] == 1, 'pass', 'fail')
ct_v = pd.crosstab(vis, d.S90); ct_e = pd.crosstab(d.S90, eqv)
print(ct_v); print(ct_e)
axB = ax_mm(146, 12.5, 43.5, 103.5); axB.set_xlim(-0.36, 1.36); axB.axis('off')
GAPN = 2.6; W = 0.085
def stack(names, counts):
    pos, y = {}, 0.0
    for n in names:
        c = counts.get(n, 0); pos[n] = [y, y + c]; y += c + GAPN
    return pos
mid_order = ['GREEN', 'AMBER', 'RED']; side_order = ['pass', 'fail']
cm = d.S90.value_counts().to_dict(); cv = pd.Series(vis).value_counts().to_dict(); ce = pd.Series(eqv).value_counts().to_dict()
H = 50 + 2 * GAPN
def flip(p): return {k: [H - v[1], H - v[0]] for k, v in p.items()}
PM, PV, PE = flip(stack(mid_order, cm)), flip(stack(side_order, cv)), flip(stack(side_order, ce))
axB.set_ylim(-1, H + 9)
def band(x0, a0, b0, x1, a1, b1, color):
    xm = (x0 + x1) / 2
    verts = [(x0, b0), (xm, b0), (xm, b1), (x1, b1), (x1, a1), (xm, a1), (xm, a0), (x0, a0), (x0, b0)]
    codes = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4, Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4, Path.CLOSEPOLY]
    axB.add_patch(PathPatch(Path(verts, codes), facecolor=color, edgecolor='none', alpha=0.5, zorder=1))
XL, XM, XR = 0.0, 0.5, 1.0
# left -> middle (stack inside nodes top-down in partner order)
offL = {k: PV[k][1] for k in PV}; offM_in = {k: PM[k][1] for k in PM}
for sv in side_order:
    for sm in mid_order:
        n = ct_v.loc[sv, sm] if (sv in ct_v.index and sm in ct_v.columns) else 0
        if n == 0: continue
        band(XL + W / 2, offL[sv], offL[sv] - n, XM - W / 2, offM_in[sm], offM_in[sm] - n, STATE[sm])
        offL[sv] -= n; offM_in[sm] -= n
offM_out = {k: PM[k][1] for k in PM}; offR = {k: PE[k][1] for k in PE}
for sm in mid_order:
    for se in side_order:
        n = ct_e.loc[sm, se] if (sm in ct_e.index and se in ct_e.columns) else 0
        if n == 0: continue
        band(XM + W / 2, offM_out[sm], offM_out[sm] - n, XR - W / 2, offR[se], offR[se] - n, STATE[sm])
        offM_out[sm] -= n; offR[se] -= n
SIDEC = {'pass': '#3D4651', 'fail': '#B9B2A6'}
for x, P, cmap_, cnts in [(XL, PV, SIDEC, cv), (XR, PE, SIDEC, ce), (XM, PM, STATE, cm)]:
    for k, (y0, y1) in P.items():
        axB.add_patch(Rectangle((x - W / 2, y0), W, y1 - y0, facecolor=cmap_[k], edgecolor='white', lw=0.5, zorder=3))
        lab = {'pass': 'pass', 'fail': 'fail', 'GREEN': 'GREEN', 'AMBER': 'AMBER', 'RED': 'RED'}[k]
        if x == XM:
            axB.text(x, (y0 + y1) / 2, f'{lab}\n{cnts[k]}', fontsize=7, ha='center', va='center', color='white',
                     fontweight='bold', zorder=4, linespacing=0.95) if (y1 - y0) > 5 else \
                axB.text(x + W / 2 + 0.03, (y0 + y1) / 2, f'{lab} {cnts[k]}', fontsize=7, ha='left', va='center',
                         color=STATE[k], fontweight='bold', zorder=4)
        else:
            ha = 'right' if x == XL else 'left'; xo = -W / 2 - 0.03 if x == XL else W / 2 + 0.03
            axB.text(x + xo, (y0 + y1) / 2, f'{lab}\n{cnts[k]}', fontsize=7, ha=ha, va='center', linespacing=0.95,
                     fontweight='bold', color=INK)
for x, t in [(XL, 'Visitor\nonly'), (XM, 'Set-valued\nstate'), (XR, 'Equal\nweight')]:
    axB.text(x, H + 2.0, t, fontsize=7, ha='center', va='bottom', fontweight='bold', linespacing=1.0)

# ---------------- titles, legends
panel_label(fig, 2.5 / FW, (FH - 1.0) / FH, 'A')
panel_title(fig, 8.0 / FW, (FH - 1.7) / FH, 'Admissible score intervals across 50 museum-years')
# three-row, two-column legend at final-size 7 pt; preserves 7 pt text without crowding
legend_rows = [
    (FH - 7.4, [
        ('line', STATE['RED'], 'RED: all weights < τ', 8.0),
        ('line', '#C98A22', 'AMBER: priority-dependent', 68.0),
    ]),
    (FH - 10.8, [
        ('line', STATE['GREEN'], 'GREEN: all weights ≥ τ', 8.0),
        ('band', '#9AA1A9', '10% minimum mission-weight range', 68.0),
    ]),
    (FH - 14.2, [
        ('eq', INK, 'equal weight', 8.0),
        ('vis', '#4E8FC4', 'visitor only', 68.0),
    ]),
]
for ly, items in legend_rows:
    for kind, c, txt, xx in items:
        yy = ly / FH
        if kind == 'line':
            fig.lines.append(Line2D([xx / FW] * 2, [(ly - 1.2) / FH, (ly + 1.2) / FH], transform=fig.transFigure, color=c, lw=1.0))
        elif kind == 'band':
            fig.lines.append(Line2D([xx / FW] * 2, [(ly - 1.2) / FH, (ly + 1.2) / FH], transform=fig.transFigure, color=c, lw=3.4, alpha=0.35, solid_capstyle='butt'))
        elif kind == 'eq':
            fig.lines.append(Line2D([xx / FW], [yy], transform=fig.transFigure, marker='o', ms=2.8, mfc='white', mec=INK, mew=0.6, ls='none'))
        else:
            fig.lines.append(Line2D([xx / FW], [yy], transform=fig.transFigure, marker='D', ms=2.2, mfc=c, mec='white', mew=0.3, ls='none'))
        fig.text((xx + 1.7) / FW, yy, txt, fontsize=7, va='center', color=INK2)
panel_label(fig, 143.0 / FW, (FH - 1.0) / FH, 'B')
panel_title(fig, 148.0 / FW, (FH - 1.7) / FH, 'Three verdicts\n(same 50 cases)')
fig.text(148.0 / FW, (FH - 9.0) / FH, 'τ = 0.90; colour = state', fontsize=7, color=INK2, va='top')
panel_label(fig, 2.5 / FW, 53.0 / FH, 'C')
panel_title(fig, 8.0 / FW, 52.3 / FH, 'Set-valued state across thresholds τ and minimum mission weights ε (same column order as A)')
nv = ct_v.loc['pass', 'AMBER']; ne = ct_e.loc['AMBER', 'pass']; nf = ct_e.loc['AMBER', 'fail']
save(fig, 'Figure3_priority_dependence_states_v2')
