#!/usr/bin/env python3
"""Deterministic lexical analysis of six C++ structural features.

This is the analyzer used to produce the structural feature profiles in
Figure 2(b). A feature is counted for a file when at least one of its regular
expressions matches; a file may belong to several feature categories. The
denominator of every ratio is the number of analyzed files.

Reported features
-----------------
    template, lambda, constexpr, explicit cast, exception, inline assembly

The analyzer applies lexical patterns to the extracted source code. It
characterizes the generated program distribution.

Usage:
    python scripts/analyze_structures.py path/to/codes/
    python scripts/analyze_structures.py path/to/case.cpp
    python scripts/analyze_structures.py path/to/codes/ --pattern "case_*.cpp"
    python scripts/analyze_structures.py path/to/codes/ --all --json out.json
"""

import argparse
import json
import re
import sys
from pathlib import Path

REPORTED_FEATURES = [
    "template",
    "lambda",
    "constexpr",
    "type_cast",
    "exception",
    "inline_asm",
]

FEATURE_PATTERNS = {
    "template": [
        r"\btemplate\s*<", r"\btypename\b",
    ],
    "lambda": [
        r"\blambda\b", r"\[[^\]]*\]\s*\(", r"\[\s*\]\s*\{",
        r"\[\s*=\s*\]", r"\[\s*&\s*\]",
    ],
    "constexpr": [
        r"\bconstexpr\b", r"\bconsteval\b", r"\bconstinit\b",
    ],
    "macro": [
        r"#define\s", r"#ifdef\s", r"#ifndef\s", r"#if\s", r"#endif",
        r"#elif\s", r"#undef\s", r"#pragma\s", r"#error\s", r"#include\s",
    ],
    "type_cast": [
        r"\bstatic_cast\s*<", r"\breinterpret_cast\s*<",
        r"\bconst_cast\s*<", r"\bdynamic_cast\s*<",
        r"\(\s*(?:int|long|short|char|float|double|unsigned|size_t"
        r"|void\s*\*|char\s*\*)\s*\)\s*\w",
    ],
    "exception": [
        r"\btry\s*\{", r"\bcatch\s*\(", r"\bthrow\b", r"\bnoexcept\b",
    ],
    "inline_asm": [
        r"\basm\b\s*[\({_]", r"__asm__?\s*[\({_]",
    ],
    "sizeof_alignof": [
        r"\bsizeof\s*[\(]", r"\balignof\s*[\(]", r"\bdecltype\s*[\(]",
    ],
    "concept_requires": [
        r"\bconcept\b", r"\brequires\b",
    ],
}


def analyze_text(text, features):
    counts = {}
    for feature in features:
        n = 0
        for pattern in FEATURE_PATTERNS[feature]:
            n += len(re.findall(pattern, text, re.IGNORECASE))
        counts[feature] = n
    return counts


def collect_files(inputs, pattern):
    files = []
    for item in inputs:
        path = Path(item)
        if path.is_dir():
            files.extend(sorted(path.glob(pattern)))
        elif path.is_file():
            files.append(path)
        else:
            raise SystemExit(f"Not a file or directory: {path}")
    return files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+",
                        help="one or more files or directories")
    parser.add_argument("--pattern", default="case_*.*",
                        help="glob used for directories (default: case_*.*)")
    parser.add_argument("--all", action="store_true",
                        help="also report macro, sizeof/alignof, and concept/requires")
    parser.add_argument("--json", type=Path, default=None,
                        help="optional JSON output path")
    args = parser.parse_args()

    features = list(REPORTED_FEATURES)
    if args.all:
        features = list(FEATURE_PATTERNS)

    files = collect_files(args.inputs, args.pattern)
    if not files:
        raise SystemExit("No files matched.")

    file_count = {feature: 0 for feature in features}
    total_occurrences = {feature: 0 for feature in features}

    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace")
        counts = analyze_text(text, features)
        for feature, n in counts.items():
            if n > 0:
                file_count[feature] += 1
            total_occurrences[feature] += n

    total_files = len(files)
    print(f"Analyzed {total_files} file(s)")
    header = f"{'feature':22s} {'files':>8s} {'ratio':>9s} {'occurrences':>13s}"
    print(header)
    print("-" * len(header))
    for feature in features:
        ratio = 100.0 * file_count[feature] / total_files
        print(f"{feature:22s} {file_count[feature]:8d} {ratio:8.2f}% "
              f"{total_occurrences[feature]:13d}")

    print("\nNote: a file may match multiple features; ratios are file-level "
          "and are not mutually exclusive.")

    if args.json:
        payload = {
            "total_files": total_files,
            "features": {
                feature: {
                    "file_count": file_count[feature],
                    "ratio": file_count[feature] / total_files,
                    "total_occurrences": total_occurrences[feature],
                }
                for feature in features
            },
        }
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(payload, indent=2) + "\n",
                             encoding="utf-8")
        print(f"Wrote {args.json}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
