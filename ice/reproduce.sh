#!/usr/bin/env bash
# Reproduce the TRAPO compiler ICE (GCC PR c++/124397 family).
#
# Usage:
#   ./reproduce.sh                         # compile minimized.cpp once
#   ./reproduce.sh --runs 5                # five runs
#   ./reproduce.sh --original              # compile the 16-line original case
#   CXX=/usr/bin/g++ ./reproduce.sh        # choose a compiler
#   CXX=clang++ STD=c++2b ./reproduce.sh   # negative control (clang 13)
#   ./reproduce.sh --out my_output.txt     # save the first run's diagnostics
#
# The script uses a temporary directory for binaries. Memory is capped at
# 8 GiB and each run times out after 60 s.

set -u

CXX="${CXX:-g++}"
STD="${STD:-c++23}"
RUNS=1
SRC="minimized.cpp"
OUT=""

while [ "$#" -gt 0 ]; do
    case "$1" in
        --original)
            SRC="original.cpp"
            shift
            ;;
        --runs)
            RUNS="$2"
            shift 2
            ;;
        --out)
            OUT="$2"
            shift 2
            ;;
        -h|--help)
            sed -n '2,20p' "$0"
            exit 0
            ;;
        *)
            echo "Unknown argument: $1" >&2
            exit 2
            ;;
    esac
done

cd "$(dirname "$0")" || exit 1

if [ ! -f "$SRC" ]; then
    echo "Source file not found: $SRC" >&2
    exit 1
fi

TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT

echo "Compiler : $($CXX --version 2>/dev/null | head -n 1)"
echo "Standard : -std=$STD"
echo "Source   : $SRC"
echo "Runs     : $RUNS"
echo

ICE_RUNS=0
for i in $(seq 1 "$RUNS"); do
    (
        ulimit -v 8388608 2>/dev/null || true
        # Keep instrumented-build .gcda files out of the source tree.
        export GCOV_PREFIX="$TMPDIR/gcda_$i"
        export GCOV_PREFIX_STRIP=0
        timeout -k 5 60 "$CXX" -x c++ -std="$STD" "$SRC" -o "$TMPDIR/out$i"
    ) 2> "$TMPDIR/run$i.err"
    rc=$?

    if grep -qiE 'internal compiler error' "$TMPDIR/run$i.err"; then
        ice=1
        ICE_RUNS=$((ICE_RUNS + 1))
    else
        ice=0
    fi

    printf 'run%d: exit=%d ICE=%d\n' "$i" "$rc" "$ice"
done

echo
echo "ICE observed in $ICE_RUNS/$RUNS run(s)."

if [ -n "$OUT" ]; then
    cp "$TMPDIR/run1.err" "$OUT"
    echo "First run's diagnostics saved to: $OUT"
else
    echo
    echo "First run's diagnostics (first 25 lines):"
    sed -n '1,25p' "$TMPDIR/run1.err"
fi
