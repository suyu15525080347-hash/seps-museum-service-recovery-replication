"""Shared visual system for SEPS Figures 1-5 (one paper, one look)."""
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, to_rgb
import os

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(BASE, '..'))
REP = os.path.join(ROOT, 'core_replication_v0.1', 'replication_package_v0.1')
WORK = BASE
OUTDIR = os.path.join(WORK, 'out'); os.makedirs(OUTDIR, exist_ok=True)

MM = 1 / 25.4
FULL_W = 190 * MM   # Elsevier double-column
INK = '#1F2328'; INK2 = '#57606A'; INK3 = '#8C959F'; RULE = '#D0D7DE'

MISSIONS = ['total_visits', 'under16', 'formal_education', 'onsite_U18', 'UK_loan_venues']
MLABEL = {'total_visits': 'Total visits', 'under16': 'Under-16 visits', 'formal_education': 'Formal education',
          'onsite_U18': 'On-site U18 learning', 'UK_loan_venues': 'UK loan venues'}
MSHORT = {'total_visits': 'Visits', 'under16': 'U16', 'formal_education': 'Edu', 'onsite_U18': 'U18',
          'UK_loan_venues': 'Loans'}
MCOL = {'total_visits': '#2B3A55', 'under16': '#4E8FC4', 'formal_education': '#8A4F9E',
        'onsite_U18': '#D07A2D', 'UK_loan_venues': '#5E8C3E'}

# recovery attainment 0..1 : crimson -> terracotta -> amber -> sand -> sage -> teal
REC_CMAP = LinearSegmentedColormap.from_list('recovery', [
    (0.00, '#7A1F2B'), (0.30, '#C2463A'), (0.55, '#E39A3B'), (0.75, '#EED9A0'),
    (0.90, '#A9CDB9'), (1.00, '#2E7D74')])
STATE = {'RED': '#B83A3A', 'AMBER': '#E3A23B', 'GREEN': '#2E7D74'}
STATE_LIGHT = {'RED': '#F2D4D2', 'AMBER': '#F8E6C4', 'GREEN': '#CFE5E1'}

SHORTNAME = {'British Museum': 'British Museum', 'Horniman Museum': 'Horniman', 'Imperial War Museum': 'IWM',
             'National Museums Liverpool': 'NML', 'Natural History Museum': 'NHM',
             'Royal Museums Greenwich': 'RMG', 'Science Museum Group': 'Science Museum Gp',
             "Sir John Soane's Museum": "Soane's", 'Tate Gallery': 'Tate', 'Victoria and Albert Museum': 'V&A'}
ABBR = {'British Museum': 'BM', 'Horniman Museum': 'HOR', 'Imperial War Museum': 'IWM',
        'National Museums Liverpool': 'NML', 'Natural History Museum': 'NHM', 'Royal Museums Greenwich': 'RMG',
        'Science Museum Group': 'SMG', "Sir John Soane's Museum": 'SJS', 'Tate Gallery': 'TATE',
        'Victoria and Albert Museum': 'V&A'}
FY = ['2020/21', '2021/22', '2022/23', '2023/24', '2024/25']
FYS = ["20/21", "21/22", "22/23", "23/24", "24/25"]


def setup():
    mpl.rcParams.update({
        'font.family': 'Arial', 'font.size': 7.2, 'axes.titlesize': 8.0, 'axes.labelsize': 7.2,
        'xtick.labelsize': 7.0, 'ytick.labelsize': 7.0, 'legend.fontsize': 7.0,
        'axes.edgecolor': INK2, 'axes.linewidth': 0.5, 'xtick.color': INK2, 'ytick.color': INK2,
        'xtick.major.width': 0.5, 'ytick.major.width': 0.5, 'xtick.major.size': 2, 'ytick.major.size': 2,
        'axes.labelcolor': INK, 'text.color': INK, 'axes.spines.top': False, 'axes.spines.right': False,
        'svg.fonttype': 'none', 'pdf.fonttype': 42, 'savefig.dpi': 600, 'figure.dpi': 150,
        'lines.solid_capstyle': 'round'})


def panel_label(fig_or_ax, x, y, s, transform=None, **kw):
    t = transform if transform is not None else fig_or_ax.transFigure
    fig_or_ax.text(x, y, s, transform=t, fontsize=9.5, fontweight='bold', va='top', ha='left', color=INK, **kw)


def panel_title(fig, x, y, s, **kw):
    fig.text(x, y, s, fontsize=7, fontweight='bold', va='top', ha='left', color=INK, **kw)


def save(fig, stem):
    for ext in ('png', 'svg', 'pdf'):
        fig.savefig(os.path.join(OUTDIR, f'{stem}.{ext}'), dpi=600 if ext == 'png' else None,
                    facecolor='white')
    print('saved', stem)


def halo(lw=2.2, color='white'):
    import matplotlib.patheffects as pe
    return [pe.withStroke(linewidth=lw, foreground=color)]
