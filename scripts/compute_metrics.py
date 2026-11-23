#!/usr/bin/env python3
"""Recompute the three generation-usability metrics from raw counts.

Definitions (paper Section 4.4, Equations 12-14):

    Extraction Rate           = N_extracted / N_calls
    Conditional Compile Rate  = N_compiled  / N_extracted
    End-to-End Compile Yield  = N_compiled  / N_calls

Input : data/evaluation_counts.csv
Check : data/table2_results.csv (published values)

The script uses only the Python standard library. It exits with status 1 if
any recomputed percentage differs from the published value by more than the
tolerance (default 0.011 percentage points, i.e. rounding at two decimals).

Usage:
    python scripts/compute_metrics.py
    python scripts/compute_metrics.py --tolerance 0.02
"""

import argparse
import csv
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_COUNTS = BASE_DIR / "data" / "evaluation_counts.csv"
DEFAULT_PUBLISHED = BASE_DIR / "data" / "table2_results.csv"


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--counts", type=Path, default=DEFAULT_COUNTS,
                        help="raw-count CSV (default: data/evaluation_counts.csv)")
    parser.add_argument("--published", type=Path, default=DEFAULT_PUBLISHED,
                        help="published Table 2 CSV (default: data/table2_results.csv)")
    parser.add_argument("--tolerance", type=float, default=0.011,
                        help="maximum allowed absolute difference in percentage points")
    args = parser.parse_args()

    counts = read_csv(args.counts)
    published = {row["approach"]: row for row in read_csv(args.published)}

    header = (f"{'approach':10s} {'extracted':>10s} {'compiled':>9s} "
              f"{'extract %':>10s} {'cond %':>8s} {'e2e %':>8s} "
              f"{'paper cond %':>13s} {'max diff pp':>11s}")
    print(header)
    print("-" * len(header))

    worst = 0.0
    failures = []
    for row in counts:
        approach = row["approach"]
        total = int(row["total_calls"])
        extracted = int(row["extracted_count"])
        compiled = int(row["compiled_count"])

        er = 100.0 * extracted / total
        ccr = 100.0 * compiled / extracted
        e2e = 100.0 * compiled / total

        pub = published.get(approach)
        if pub is None:
            failures.append(f"{approach}: missing from published Table 2 CSV")
            delta = float("nan")
        else:
            delta = abs(ccr - float(pub["conditional_compile_rate_pct"]))
            for name, value, key in (
                ("extraction", er, "extraction_rate_pct"),
                ("end-to-end", e2e, "end_to_end_yield_pct"),
            ):
                d = abs(value - float(pub[key]))
                if d > delta:
                    delta = d
            worst = max(worst, delta)
            if delta > args.tolerance:
                failures.append(
                    f"{approach}: recomputed rates differ from published values "
                    f"by {delta:.4f} pp")

        paper_ccr = f"{float(pub['conditional_compile_rate_pct']):.2f}" if pub else "n/a"
        print(f"{approach:10s} {extracted:10d} {compiled:9d} "
              f"{er:10.2f} {ccr:8.2f} {e2e:8.2f} {paper_ccr:>13s} {delta:9.4f}")

    print()
    print(f"Maximum absolute difference from published Table 2: {worst:.4f} pp")
    print(f"Tolerance: {args.tolerance:.4f} pp")

    if failures:
        print("\nFAILED:")
        for message in failures:
            print("  - " + message)
        return 1

    print("OK: all 15 configurations are consistent with the published table.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
