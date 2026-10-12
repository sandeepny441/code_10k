#!/usr/bin/env python3
"""Recreate the HMDA application charts with Matplotlib.

Run: python3 recreate_applications_charts.py --out-dir ./charts
Dependency: matplotlib. Data is embedded so the script is portable.
Source: now_folder/001_yearly_application_outcomes/yearly_application_outcomes.md
Exports separate 2016–2017 and 2016–2025 charts at 300 dpi, plus vector SVGs.
Loan-made and denial percentages are calculated from total applications and
displayed beside their respective counts. Counts are displayed in millions.
All text is black except loan-made percentages (green) and denial percentages (red).
"""

from pathlib import Path
import argparse
import os

os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).parent / ".mpl-cache"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.font_manager import FontProperties

# Year, all applications, loan made, approved not taken, denied, withdrawn, incomplete.
DATA = [
    (2007, 21391373, 10441545, 1945380, 5952530, 2331997, 719921),
    (2008, 14193941, 7177262, 1105492, 3944602, 1552895, 413690),
    (2009, 14989908, 8950936, 851769, 3012967, 1727739, 446497),
    (2010, 12954875, 7863337, 650594, 2556789, 1448330, 435825),
    (2011, 11742810, 7095262, 636467, 2354846, 1225751, 430484),
    (2012, 15310652, 9783966, 710706, 2761964, 1529647, 524369),
    (2013, 13987170, 8706657, 740856, 2649931, 1345371, 544355),
    (2014, 10062525, 6039826, 422283, 2068237, 1122719, 409460),
    (2015, 12094483, 7404258, 404755, 2274913, 1475218, 535339),
    (2016, 13925802, 8377907, 436074, 2683178, 1748355, 680288),
    (2017, 12056034, 7339057, 409797, 2009743, 1696289, 601148),
    (2018, 12939736, 7720995, 339311, 2554198, 1771668, 553564),
    (2019, 15129137, 9325241, 402486, 2538965, 2144364, 718081),
    (2020, 22666973, 14541302, 619497, 2863286, 3396753, 1246135),
    (2021, 23297562, 14997308, 634632, 2919007, 3299209, 1447406),
    (2022, 14322093, 8394278, 417134, 2499110, 2221256, 790315),
    (2023, 9987150, 5691726, 308837, 1994758, 1456029, 535800),
    (2024, 10754906, 6176052, 360560, 2099966, 1536699, 581629),
    (2025, 11766671, 6827891, 417961, 2115090, 1710723, 695006),
]

W = 18.5
MARGIN = 0.40
INK = "#111111"
MUTED = INK
RULE = "#DFE5E0"
ROW_BG = "#F6F8F6"
COLORS = ["#17563F", "#70BF95", "#8F343B", "#D96960", "#F1C4BE"]
LABELS = ["Loan made", "Approved, not taken", "Denied", "Withdrawn", "Incomplete"]
PLOT_LEFT, PLOT_RIGHT = 1.22, 7.62
TABLE_LEFT = 7.95
COL_WIDTHS = [1.00, 2.35, 1.65, 2.25, 1.47, 1.43]
ROW_STEP = 0.50
BAR_HEIGHT = 0.40
BODY_SIZE = 16.5
HEADER_SIZE = 14.0
PERCENT_COLORS = {1: "#157A3D", 3: "#B3262E"}
PANEL_TOP = 1.58
FIRST_ROW_OFFSET = 1.03

plt.rcParams.update({
    "font.family": "Arial",
    "font.size": BODY_SIZE,
    "text.color": INK,
    "figure.facecolor": "white",
    "savefig.facecolor": "white",
    "svg.fonttype": "none",
    "axes.unicode_minus": False,
})


def label(ax, x, y, value, size=13, color=INK, weight="normal", ha="left", **kwargs):
    return ax.text(x, y, value, fontsize=size, color=color, fontweight=weight,
                   ha=ha, va="center", linespacing=1.28, **kwargs)


def line(ax, x0, x1, y, color=RULE, width=0.7, zorder=0):
    ax.plot([x0, x1], [y, y], color=color, linewidth=width, zorder=zorder,
            solid_capstyle="butt")


def header(fig, ax, period):
    label(ax, MARGIN, 0.45, "Mortgage applications by year", size=28, weight="bold")
    x = MARGIN
    legend_texts = []
    for title, color in zip(LABELS, COLORS):
        ax.add_patch(Rectangle((x, .89), .20, .20, facecolor=color, linewidth=0))
        t = label(ax, x + .30, .99, title, size=14)
        fig.canvas.draw()
        width_inches = t.get_window_extent(fig.canvas.get_renderer()).width / fig.dpi
        legend_texts.append(t)
        x += .30 + width_inches + .44
    line(ax, MARGIN, W - MARGIN, 1.28)
    return legend_texts


def panel(fig, ax, rows, top):
    """All chart bars and table values use identical physical row centers."""
    period = f"{rows[0][0]}–{rows[-1][0]}"
    label(ax, MARGIN, top, period, size=20, weight="bold")
    label(ax, W - MARGIN, top, "Applications in millions", size=14,
          color=MUTED, ha="right")
    header_y = top + .48
    first_y = top + FIRST_ROW_OFFSET
    bottom_y = first_y + (len(rows) - 1) * ROW_STEP + ROW_STEP / 2
    band_top = first_y - ROW_STEP / 2
    label(ax, MARGIN, header_y, "Year", size=HEADER_SIZE, weight="bold")
    line(ax, MARGIN, W - MARGIN, band_top - .04, width=.9)

    # Alternating light bands continue across the plot and table.
    for i in range(len(rows)):
        if i % 2 == 0:
            ax.add_patch(Rectangle((MARGIN - .10, first_y + i * ROW_STEP - ROW_STEP / 2),
                                   W - 2 * MARGIN + .20, ROW_STEP,
                                   facecolor=ROW_BG, linewidth=0, zorder=-4))

    scale = (PLOT_RIGHT - PLOT_LEFT) / 25
    for tick in range(0, 26, 5):
        x = PLOT_LEFT + tick * scale
        ax.plot([x, x], [band_top, bottom_y], color=RULE, linewidth=.6, zorder=-2)
        label(ax, x, bottom_y + .23, str(tick), size=13, ha="center")
    line(ax, PLOT_LEFT, PLOT_RIGHT, bottom_y, width=.9)
    headers = ["Total", "Loan made", "Approved,\nnot taken", "Denied",
               "Withdrawn", "Incomplete"]
    rights, lefts, header_artists = [], [], []
    x = TABLE_LEFT
    for j, (heading, width) in enumerate(zip(headers, COL_WIDTHS)):
        lefts.append(x)
        rights.append(x + width - .10)
        t = label(ax, rights[-1], header_y, heading, size=HEADER_SIZE,
                  ha="right", weight="bold")
        header_artists.append((t, x, x + width))
        x += width

    cells = []
    for i, row in enumerate(rows):
        year, total, made, not_taken, denied, withdrawn, incomplete = row
        assert total == sum(row[2:]), f"Outcome counts do not sum to total in {year}"
        y = first_y + i * ROW_STEP
        label(ax, MARGIN, y, str(year), size=BODY_SIZE, weight="bold")
        x = PLOT_LEFT
        for value, color in zip(row[2:], COLORS):
            width = value / 1_000_000 * scale
            ax.add_patch(Rectangle((x, y - BAR_HEIGHT / 2), width, BAR_HEIGHT,
                                   facecolor=color, edgecolor="white", linewidth=.55, zorder=2))
            x += width
        expected_end = PLOT_LEFT + total / 1_000_000 * scale
        assert abs(x - expected_end) < 1e-9
        values = [f"{value / 1_000_000:.1f}" for value in row[1:]]
        for j, value in enumerate(values):
            count_right = rights[j]
            if j in PERCENT_COLORS:
                percentage = f"({100 * row[j + 1] / total:.1f}%)"
                percent_artist = label(ax, rights[j], y, percentage, size=BODY_SIZE,
                                       color=PERCENT_COLORS[j], weight="bold", ha="right")
                percent_artist.set_gid(f"percentage-{year}-{'made' if j == 1 else 'denied'}")
                width_pixels, _, _ = fig.canvas.get_renderer().get_text_width_height_descent(
                    percentage, FontProperties(family="Arial", size=BODY_SIZE, weight="bold"), False)
                count_right -= width_pixels / fig.dpi + .09
                cells.append((percent_artist, lefts[j], lefts[j] + COL_WIDTHS[j], y))
            t = label(ax, count_right, y, value, size=BODY_SIZE,
                      weight="bold" if j == 0 else "normal", ha="right")
            t.set_gid(f"count-{year}-{j}")
            cells.append((t, lefts[j], lefts[j] + COL_WIDTHS[j], y))
    line(ax, TABLE_LEFT, W - MARGIN, bottom_y, width=.9)
    return header_artists, cells


def verify_layout(fig, ax, header_artists, cells):
    """Check text widths and vertical fit against the actual renderer."""
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    inverse = ax.transData.inverted()
    for text, left, right in header_artists:
        bounds = text.get_window_extent(renderer).transformed(inverse)
        assert bounds.x0 >= left + .03, f"Header extends outside its column: {text.get_text()}"
        assert bounds.x1 <= right - .06
    for text, left, right, y in cells:
        bounds = text.get_window_extent(renderer).transformed(inverse)
        assert bounds.x0 >= left + .06, f"Value extends outside its column: {text.get_text()}"
        assert bounds.x1 <= right - .06
        assert abs(bounds.y1 - bounds.y0) < ROW_STEP * .75
    for text in ax.texts:
        bounds = text.get_window_extent(renderer)
        assert bounds.x0 >= 0 and bounds.x1 <= fig.bbox.width
        assert bounds.y0 >= 0 and bounds.y1 <= fig.bbox.height
    text_bounds = [(t, t.get_window_extent(renderer)) for t in ax.texts]
    for i, (first, first_bounds) in enumerate(text_bounds):
        for second, second_bounds in text_bounds[i + 1:]:
            assert not first_bounds.overlaps(second_bounds), (
                f"Overlapping text: {first.get_text()!r} and {second.get_text()!r}")


def render(out_dir, stem, start, end):
    rows = [r for r in DATA if start <= r[0] <= end]
    assert [r[0] for r in rows] == list(range(start, end + 1))
    top = PANEL_TOP
    bottom_y = top + FIRST_ROW_OFFSET + (len(rows) - 1) * ROW_STEP + ROW_STEP / 2
    height = bottom_y + .49
    fig = plt.figure(figsize=(W, height), dpi=300)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(height, 0)
    ax.set_axis_off()
    period_label = f"{start}–{end}"
    header(fig, ax, period_label)
    header_artists, cells = panel(fig, ax, rows, top=top)
    verify_layout(fig, ax, header_artists, cells)
    for extension in ("png", "svg"):
        path = out_dir / f"{stem}.{extension}"
        fig.savefig(path, dpi=300)
        print(path)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=Path(__file__).parent)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    assert [r[0] for r in DATA] == list(range(2007, 2026))
    render(args.out_dir, "applications_2016_2017", 2016, 2017)
    render(args.out_dir, "applications_2016_2025", 2016, 2025)
    print("Verified: exact totals, proportional bars, shared row alignment, and text bounds.")


if __name__ == "__main__":
    main()
