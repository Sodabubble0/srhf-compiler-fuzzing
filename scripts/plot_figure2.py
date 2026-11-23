#!/usr/bin/env python3
"""Rebuild Figure 2 of the final manuscript.

The final Figure 2 has two panels:

    (a) compile yield vs. final compiler line coverage for the 15 configurations;
    (b) structural feature frequencies for the Dataset and the ten coordination
        configurations, colored by within-feature z-scores.

Inputs
------
    data/table2_results.csv
    data/figure2_structural_features.csv

Outputs (created on demand)
---------------------------
    figures/figure2_compile_yield_and_structure.{png,pdf,svg}   # default
    figures/figure2a_compile_yield_vs_coverage.{png,pdf,svg}    # --panel a
    figures/figure2b_structural_features.{png,pdf,svg}          # --panel b

The structural CSV stores both the one-/two-decimal percentages printed in the
manuscript and the exact file counts behind them. Heatmap colors are computed
from the exact counts; cell labels reproduce the printed values.

The final manuscript caption uses within-feature robust z-scores, so the
heatmap defaults to median/MAD normalization. `--zscore std` is available for
comparison with the earlier preprint, which used mean/SD normalization.

Usage:
    python scripts/plot_figure2.py --no-show
    python scripts/plot_figure2.py --no-show --panel b
    python scripts/plot_figure2.py --no-show --zscore std
"""

import argparse
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_TABLE2 = BASE_DIR / "data" / "table2_results.csv"
DEFAULT_STRUCT = BASE_DIR / "data" / "figure2_structural_features.csv"
DEFAULT_OUTDIR = BASE_DIR / "figures"

REFERENCE_CATEGORIES = {"Base", "SFT", "RFT", "Sequential SFT–RFT"}
CATEGORY_STYLE = {
    "Joint optimization": dict(marker="o", color="#2a6fdb"),
    "Adaptive routing": dict(marker="s", color="#e06a2b"),
    "Policy shaping": dict(marker="^", color="#1f9e77"),
}
REFERENCE_STYLE = dict(marker="D", facecolor="none", edgecolor="#777777")

LABEL_OFFSETS = {
    "Base model": (-8, -9),
    "SFT": (7, 6),
    "GRPO": (7, 6),
    "GSPO": (7, 7),
    "SFT→GSPO": (7, -9),
    "CHORD": (-8, -9),
    "SRFT": (7, 6),
    "UFT": (7, 8),
    "TRAPO": (-9, 8),
    "LUFFY": (7, 7),
    "DYPO": (-8, 7),
    "SASR": (-8, 7),
    "SuperRL": (7, -9),
    "MIFO": (7, 6),
    "DFT→GSPO": (7, -9),
}

FEATURES = [
    ("template_pct", "Template"),
    ("lambda_pct", "Lambda"),
    ("constexpr_pct", "Constexpr"),
    ("explicit_cast_pct", "Explicit cast"),
    ("exception_pct", "Exception"),
    ("inline_assembly_pct", "Inline assembly"),
]
COUNT_KEYS = [
    "template_count", "lambda_count", "constexpr_count",
    "explicit_cast_count", "exception_count", "inline_assembly_count",
]

SURFACE = "#ffffff"
INK = "#111111"
INK_2 = "#555555"
GRID = "#dddddd"
AXIS = "#999999"
SEPARATOR = "#52514e"
CELL_EDGE = "#ffffff"
Z_CLIP = 2.0

DIVERGING = LinearSegmentedColormap.from_list(
    "rdbu",
    ["#2166ac", "#67a9cf", "#d1e5f0", "#f7f7f7",
     "#fddbc7", "#ef8a62", "#b2182b"])


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def style_axes(ax):
    ax.grid(True, color=GRID, linewidth=0.6, zorder=0)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_color(AXIS)
        spine.set_linewidth(0.8)


def plot_panel_a(ax, rows):
    for row in rows:
        x = float(row["end_to_end_yield_pct"])
        y = int(row["final_line_coverage"])
        category = row["category"]

        if category in REFERENCE_CATEGORIES:
            ax.scatter(x, y, s=62, linewidths=1.1, zorder=3,
                       marker=REFERENCE_STYLE["marker"],
                       facecolor=REFERENCE_STYLE["facecolor"],
                       edgecolor=REFERENCE_STYLE["edgecolor"])
        else:
            style = CATEGORY_STYLE[category]
            ax.scatter(x, y, s=78, zorder=4, marker=style["marker"],
                       color=style["color"], edgecolor="white", linewidth=0.8)

        dx, dy = LABEL_OFFSETS.get(row["approach"], (8, 8))
        ax.annotate(row["approach"], xy=(x, y), xytext=(dx, dy),
                    textcoords="offset points", fontsize=9,
                    ha="left" if dx >= 0 else "right",
                    va="bottom" if dy >= 0 else "top",
                    color=INK)

    ax.set_xlabel("End-to-end compile yield (%)", fontsize=10.5)
    ax.set_ylabel("Final covered lines", fontsize=10.5)
    ax.set_xlim(25, 75)
    ax.set_ylim(150_000, 238_000)
    ax.set_xticks([30, 40, 50, 60, 70])
    ax.set_yticks(range(150_000, 230_001, 20_000))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{int(v / 1000)}k"))
    style_axes(ax)

    handles = [
        Line2D([], [], linestyle="", marker=CATEGORY_STYLE[c]["marker"],
               color=CATEGORY_STYLE[c]["color"], markersize=7, label=c)
        for c in ("Joint optimization", "Adaptive routing", "Policy shaping")
    ]
    handles.append(Line2D([], [], linestyle="", marker="D", markersize=7,
                          markerfacecolor="none", markeredgecolor="#777777",
                          label="Baselines"))
    ax.legend(handles=handles, loc="upper left", frameon=False, fontsize=9,
              handletextpad=0.5, borderaxespad=0.8)


def zscore(matrix, reference_rows, method):
    ref = matrix[reference_rows]
    if method == "robust":
        center = np.median(ref, axis=0)
        mad = np.median(np.abs(ref - center), axis=0)
        scale = 1.4826 * mad
        zero = scale < 1e-12
        if zero.any():
            scale = scale.copy()
            scale[zero] = ref[:, zero].std(axis=0)
            scale[scale < 1e-12] = 1.0
    else:
        center = ref.mean(axis=0)
        scale = ref.std(axis=0)
        scale[scale < 1e-12] = 1.0
    return (matrix - center) / scale


def plot_panel_b(fig, ax, rows, zscore_method, zscore_over):
    labels = [r["approach"] for r in rows]
    categories = [r["category"] for r in rows]
    display = [[r[key] for key, _ in FEATURES] for r in rows]
    # Colors are computed from the exact file counts; cell labels reproduce the
    # one-/two-decimal values printed in the final manuscript figure.
    matrix = np.array([
        [100.0 * float(r[count]) / int(r["programs_analyzed"])
         for count in COUNT_KEYS]
        for r in rows
    ], dtype=float)

    if zscore_over == "methods":
        reference_rows = [i for i, r in enumerate(rows)
                          if r["approach"] != "Dataset"]
    else:
        reference_rows = list(range(len(rows)))

    Z = np.clip(zscore(matrix, reference_rows, zscore_method), -Z_CLIP, Z_CLIP)
    nrow, ncol = matrix.shape

    im = ax.imshow(Z, cmap=DIVERGING, vmin=-Z_CLIP, vmax=Z_CLIP, aspect="auto")

    for i in range(nrow):
        for j in range(ncol):
            text_color = "white" if abs(Z[i, j]) >= 1.3 else INK
            ax.text(j, i, display[i][j], ha="center",
                    va="center", fontsize=8.4, color=text_color)

    for j in range(1, ncol):
        ax.axvline(j - 0.5, color=CELL_EDGE, linewidth=0.7)
    for i in range(1, nrow):
        ax.axhline(i - 0.5, color=CELL_EDGE, linewidth=0.7)

    dataset_rows = [i for i, c in enumerate(categories) if c == "Dataset"]
    if dataset_rows:
        ax.axhline(dataset_rows[-1] + 0.5, color=SEPARATOR, linewidth=1.5)
    for i in range(1, nrow):
        if categories[i] != categories[i - 1] and categories[i] != "Dataset":
            ax.axhline(i - 0.5, color=SEPARATOR, linewidth=1.0)

    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_color(AXIS)
        spine.set_linewidth(0.8)
    ax.tick_params(which="both", length=0)

    ax.set_xticks(range(ncol))
    ax.set_xticklabels([label for _, label in FEATURES], fontsize=8.8,
                       rotation=32, ha="left", rotation_mode="anchor")
    ax.xaxis.set_ticks_position("top")
    ax.xaxis.set_label_position("top")
    ax.tick_params(axis="x", pad=4)

    ax.set_yticks(range(nrow))
    ax.set_yticklabels(labels, fontsize=9)
    for tick, label in zip(ax.get_yticklabels(), labels):
        if label == "Dataset":
            tick.set_fontstyle("italic")
    ax.tick_params(axis="y", pad=6)

    ax.set_xlim(-0.5, ncol - 0.5)
    ax.set_ylim(nrow - 0.5, -0.5)

    cbar = fig.colorbar(im, ax=ax, fraction=0.033, pad=0.03,
                        ticks=[-Z_CLIP, 0, Z_CLIP])
    cbar.ax.set_yticklabels(["−2", "0", "+2"], fontsize=8.3)
    cbar.outline.set_edgecolor(AXIS)
    cbar.outline.set_linewidth(0.8)
    cbar.set_label(
        "Within-feature robust z-score" if zscore_method == "robust"
        else "Within-feature z-score",
        fontsize=8.3, labelpad=7)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--table2", type=Path, default=DEFAULT_TABLE2)
    parser.add_argument("--structure", type=Path, default=DEFAULT_STRUCT)
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUTDIR)
    parser.add_argument("--panel", choices=("both", "a", "b"), default="both")
    parser.add_argument("--zscore", choices=("robust", "std"), default="robust",
                        help="robust (default; final manuscript) or std "
                             "(earlier preprint)")
    parser.add_argument("--zscore-over", choices=("methods", "all"),
                        default="methods",
                        help="rows used to compute the heatmap color scale")
    parser.add_argument("--no-dataset", action="store_true",
                        help="omit the Dataset row from the heatmap")
    parser.add_argument("--no-show", action="store_true")
    args = parser.parse_args()

    table2 = read_csv(args.table2)
    structure = read_csv(args.structure)
    if args.no_dataset:
        structure = [r for r in structure if r["approach"] != "Dataset"]

    args.outdir.mkdir(parents=True, exist_ok=True)

    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Times New Roman", "Liberation Serif", "Nimbus Roman",
                       "DejaVu Serif"],
        "font.size": 10,
        "axes.edgecolor": AXIS,
        "axes.linewidth": 0.8,
        "text.color": INK,
        "axes.labelcolor": INK,
        "xtick.color": INK_2,
        "ytick.color": INK_2,
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
    })

    if args.panel == "both":
        fig, (ax_a, ax_b) = plt.subplots(
            1, 2, figsize=(13.0, 4.9),
            gridspec_kw={"width_ratios": [1.0, 1.05]})
        plot_panel_a(ax_a, table2)
        plot_panel_b(fig, ax_b, structure, args.zscore, args.zscore_over)
        fig.subplots_adjust(left=0.055, right=0.985, top=0.86, bottom=0.20,
                            wspace=0.34)
        fig.canvas.draw()
        pos_a = ax_a.get_position()
        pos_b = ax_b.get_position()
        fig.text(pos_a.x0 + pos_a.width / 2, 0.035,
                 "(a) Compile yield and compiler coverage",
                 ha="center", va="bottom", fontsize=10)
        fig.text(pos_b.x0 + pos_b.width / 2, 0.035,
                 "(b) Program structure frequencies (%)",
                 ha="center", va="bottom", fontsize=10)
        stem = args.outdir / "figure2_compile_yield_and_structure"
        for ext in ("png", "pdf", "svg"):
            fig.savefig(f"{stem}.{ext}", dpi=300, bbox_inches="tight",
                        facecolor=SURFACE)
        print(f"Saved {stem}.png / .pdf / .svg")

    elif args.panel == "a":
        fig, ax = plt.subplots(figsize=(7.2, 5.0))
        plot_panel_a(ax, table2)
        fig.tight_layout()
        fig.text(0.5, 0.015, "(a) Compile yield and compiler coverage",
                 ha="center", va="bottom", fontsize=10)
        stem = args.outdir / "figure2a_compile_yield_vs_coverage"
        for ext in ("png", "pdf", "svg"):
            fig.savefig(f"{stem}.{ext}", dpi=300, bbox_inches="tight",
                        facecolor=SURFACE)
        print(f"Saved {stem}.png / .pdf / .svg")

    else:
        fig, ax = plt.subplots(figsize=(8.4, 5.3))
        plot_panel_b(fig, ax, structure, args.zscore, args.zscore_over)
        fig.tight_layout()
        fig.text(0.5, 0.015, "(b) Program structure frequencies (%)",
                 ha="center", va="bottom", fontsize=10)
        suffix = "" if not args.no_dataset else "_no_dataset"
        suffix += "" if args.zscore == "robust" else "_std"
        stem = args.outdir / f"figure2b_structural_features{suffix}"
        for ext in ("png", "pdf", "svg"):
            fig.savefig(f"{stem}.{ext}", dpi=300, bbox_inches="tight",
                        facecolor=SURFACE)
        print(f"Saved {stem}.png / .pdf / .svg")

    print(f"z-score: {args.zscore}; scale computed over: {args.zscore_over}")

    if not args.no_show:
        plt.show()


if __name__ == "__main__":
    main()
