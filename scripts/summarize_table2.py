#!/usr/bin/env python3
"""Render Table 2 of the final manuscript from the public CSV.

Input : data/table2_results.csv
Output: a Markdown table on stdout (and optionally a file)

What is computed
----------------
1. The 15 individual configurations in manuscript order.
2. Unweighted category averages ("Avg." rows) for RFT, Joint optimization,
   Adaptive routing, and Policy shaping. Categories with a single approach
   (Base, SFT, Sequential SFT-RFT) appear as individual rows, matching the
   manuscript.
3. Relative final-coverage changes with respect to the base model, shown in
   parentheses in the coverage column.
4. Best and second-best individual approaches per metric.

Rounding follows the manuscript: two decimals for percentages, one decimal
for relative changes, and half-up rounding for the category averages.

Usage:
    python scripts/summarize_table2.py
    python scripts/summarize_table2.py --output table2_summary.md
"""

import argparse
import csv
import sys
from collections import OrderedDict
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = BASE_DIR / "data" / "table2_results.csv"

# The CSV uses the canonical approach name; the manuscript table adds the
# implementation detail for the conventional SFT baseline.
DISPLAY_NAME = {"SFT": "SFT (LoRA)"}

METRIC_COLUMNS = [
    ("extraction_rate_pct", "Extraction (%)"),
    ("conditional_compile_rate_pct", "Conditional compile (%)"),
    ("end_to_end_yield_pct", "End-to-end yield (%)"),
    ("final_line_coverage", "Final line coverage"),
]

D2 = Decimal("0.01")
D1 = Decimal("0.1")


def read_rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def group_by_category(rows):
    groups = OrderedDict()
    for row in rows:
        groups.setdefault(row["category"], []).append(row)
    return groups


def dec_mean(strings):
    values = [Decimal(s) for s in strings]
    return sum(values) / Decimal(len(values))


def fmt2(value):
    return format(value.quantize(D2, rounding=ROUND_HALF_UP), "f")


def fmt_signed_1(value):
    q = value.quantize(D1, rounding=ROUND_HALF_UP)
    if q == 0:
        return "0.0%"
    sign = "+" if q > 0 else ""
    return f"{sign}{format(q, 'f')}%"


def coverage_cell(coverage, base_coverage):
    relative = (Decimal(coverage) - base_coverage) / base_coverage * Decimal(100)
    return f"{int(coverage):,d} ({fmt_signed_1(relative)})"


def markdown_table(rows, groups, base_coverage):
    lines = []
    lines.append("| Category | Approach | Extraction (%) | Conditional compile (%) | "
                 "End-to-end yield (%) | Final line coverage | Verified ICEs |")
    lines.append("|---|---|---:|---:|---:|---:|---:|")
    for category, members in groups.items():
        for row in members:
            coverage = int(row["final_line_coverage"])
            lines.append(
                f"| {category} | {DISPLAY_NAME.get(row['approach'], row['approach'])} | "
                f"{row['extraction_rate_pct']} | "
                f"{row['conditional_compile_rate_pct']} | "
                f"{row['end_to_end_yield_pct']} | "
                f"{coverage_cell(coverage, base_coverage)} | "
                f"{row['verified_ice_count']} |")
        if len(members) < 2:
            continue
        avg_er = dec_mean([r["extraction_rate_pct"] for r in members])
        avg_ccr = dec_mean([r["conditional_compile_rate_pct"] for r in members])
        avg_e2e = dec_mean([r["end_to_end_yield_pct"] for r in members])
        avg_cov = dec_mean([r["final_line_coverage"] for r in members])
        avg_cov_int = int(avg_cov.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
        lines.append(
            f"| {category} | *Avg.* | "
            f"{fmt2(avg_er)} | {fmt2(avg_ccr)} | {fmt2(avg_e2e)} | "
            f"{coverage_cell(avg_cov_int, base_coverage)} | — |")
    return "\n".join(lines)


def best_and_second(rows, column):
    values = sorted({Decimal(r[column]) for r in rows}, reverse=True)
    result = []
    for rank, value in enumerate(values[:2], start=1):
        winners = [DISPLAY_NAME.get(r["approach"], r["approach"])
                   for r in rows if Decimal(r[column]) == value]
        result.append((rank, value, winners))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT,
                        help="Table 2 CSV (default: data/table2_results.csv)")
    parser.add_argument("--output", type=Path, default=None,
                        help="optional Markdown output file")
    args = parser.parse_args()

    rows = read_rows(args.input)
    groups = group_by_category(rows)
    base = next(r for r in rows if r["approach"] == "Base model")
    base_coverage = Decimal(base["final_line_coverage"])

    parts = []
    parts.append("# Table 2 summary\n")
    parts.append("Recomputed from `data/table2_results.csv`. Percentages use "
                 "two decimals and relative coverage changes use one decimal, "
                 "matching the final manuscript. Category averages are "
                 "unweighted means and are not independent experimental "
                 "records.\n")
    parts.append(markdown_table(rows, groups, base_coverage))
    parts.append("")
    parts.append("Notes: `SFT` in the CSV is labelled `SFT (LoRA)` in the "
                 "manuscript table. Average rows cover categories with at "
                 "least two approaches; the final column is `—` because ICE "
                 "counts are reported per approach. Half-up rounding is used "
                 "for the category averages.")
    parts.append("")

    parts.append("## Best and second-best individual approaches\n")
    for column, label in METRIC_COLUMNS:
        best = best_and_second(rows, column)
        chunks = []
        for rank, value, winners in best:
            if column == "final_line_coverage":
                value_text = f"{int(value):,d}"
            else:
                value_text = fmt2(value)
            chunks.append(f"{'best' if rank == 1 else 'second'} {value_text}: "
                          + ", ".join(winners))
        parts.append(f"- **{label}** — " + "; ".join(chunks))
    parts.append("")

    output = "\n".join(parts)
    if args.output:
        args.output.write_text(output + "\n", encoding="utf-8")
        print(f"Wrote {args.output}")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
