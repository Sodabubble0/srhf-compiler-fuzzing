# SRHF Compiler Fuzzing: Aggregated Results and Analysis Artifacts

Paper: **Survey of Supervised and Reinforced Hybrid Fine-tuning and
Fuzz-Oriented Empirical Study**

Authors: Qinghao Zhang, Dehong Gao, Lingyue Huang, Qichao Zhang,
Libin Yang, Xiaoyan Cai.

Repository: https://github.com/Sodabubble0/srhf-compiler-fuzzing

This repository is the **results and analysis package** accompanying the
final manuscript. It contains the aggregate data needed to recompute Table 2,
rebuild both panels of Figure 2, inspect the experimental configuration, and
reproduce the reported compiler internal compiler error (ICE).

The plotting scripts generate all figures on demand from the CSV files.

## 1. Scope

### Package contents

| Category | Contents |
|---|---|
| Table 2 results | Published metrics and the underlying extracted/compiled counts for all 15 configurations |
| Figure 2(a) | Compile-yield vs. final-coverage data for the 15 configurations |
| Figure 2(b) | Structural feature percentages and exact counts for the ten coordination configurations plus an aggregate Dataset row |
| Experimental configuration | Training and evaluation settings, reward definitions, software and compiler environment |
| Analysis scripts | Metric recomputation, Table 2 rendering, Figure 2 plotting, and the structural-feature analyzer |
| Compiler failure | Original and reduced TRAPO test case, reproduction script, diagnostics, and run logs |

Mapping to the manuscript:

| Manuscript item | Location in this repository |
|---|---|
| Table 2 aggregate results and raw counts | `data/table2_results.csv`, `data/evaluation_counts.csv` |
| Figure 2(a) scatter data | `data/table2_results.csv` |
| Figure 2(b) structural heatmap data | `data/figure2_structural_features.csv` |
| Experimental configuration | `configs/` |
| Metric, plotting, and structural-analysis scripts | `scripts/` |
| TRAPO ICE reproduction case | `ice/` |

### Scope boundaries

This package covers the aggregate results, analysis scripts, experimental
configuration, and compiler-failure materials. The curated training set,
model checkpoints, generated corpus, and full training logs remain part of
the authors' experimental environment. The package supports reproduction of
the **reported aggregate analyses** and the **compiler failure case**; full
model retraining uses the training set and checkpoints.

## 2. Quick start

The analysis scripts run on Python 3.9+ with NumPy and Matplotlib, using the
CSV files in this package.

```bash
python -m pip install -r scripts/requirements.txt

python scripts/compute_metrics.py          # recompute the three rates and check Table 2
python scripts/summarize_table2.py         # render Table 2, including Avg. rows
python scripts/plot_figure2.py --no-show   # rebuild Figure 2(a) and 2(b)
python scripts/analyze_structures.py ice/original.cpp
```

The plotting script writes its output to `figures/`, which it creates on
demand.

## 3. Data files

### `data/table2_results.csv`

Machine-readable version of Table 2 in the final manuscript.

| Column | Meaning |
|---|---|
| `category` | Base, SFT, RFT, Sequential SFT–RFT, Joint optimization, Adaptive routing, or Policy shaping |
| `approach` | Configuration name as used in the paper |
| `extraction_rate_pct` | `N_extracted / N_calls`, in percent |
| `conditional_compile_rate_pct` | `N_compiled / N_extracted`, in percent |
| `end_to_end_yield_pct` | `N_compiled / N_calls`, in percent |
| `final_line_coverage` | maximum cumulative GCC source lines covered in the run |
| `verified_ice_count` | manually verified and reproduced compiler ICEs |

Percentages are stored with two decimals, matching the manuscript. The CSV
contains the **15 individual configurations**; the manuscript's category
`Avg.` rows are recomputed by `scripts/summarize_table2.py` from these
records. The conventional SFT baseline is stored under the canonical name
`SFT`; the manuscript table labels it `SFT (LoRA)`.

### `data/evaluation_counts.csv`

The raw aggregate counts behind the three generation-usability metrics.

| Column | Meaning |
|---|---|
| `approach` | Configuration name |
| `total_calls` | LLM calls in the evaluation (10,000 for every configuration) |
| `extracted_count` | outputs from which a non-empty `<code>...</code>` block was extracted |
| `compiled_count` | extracted programs that compiled successfully |
| `final_line_coverage` | final cumulative GCC line coverage |
| `verified_ice_count` | verified compiler ICEs |
| `prompt_protocol` | `legacy` (raw prompt string) or `chat` (chat template + system prompt) |
| `coverage_sampling` | `batch_20` (20 equal batches) or `hourly` (legacy reference runs) |

The counts are source records from the runs. For the ten coordination
configurations and the base model, counts were read from each run's metrics
report. For the four reference runs (SFT, GRPO, GSPO, SFT→GSPO), counts were
read from reference-run reclassification records that preserve the original
compilation totals and pass counts. `python scripts/compute_metrics.py`
recomputes all three rates and verifies them against `table2_results.csv`; the
maximum difference is 0.0046 percentage points (two-decimal rounding).

### `data/figure2_structural_features.csv`

Structural feature percentages and counts used by Figure 2(b).

| Column | Meaning |
|---|---|
| `approach` | Dataset or configuration name |
| `category` | Dataset or coordination category |
| `template_pct` | percentage of analyzed programs containing a template construct |
| `lambda_pct` | percentage containing a lambda expression |
| `constexpr_pct` | percentage containing `constexpr`, `consteval`, or `constinit` |
| `explicit_cast_pct` | percentage containing a C++-style or C-style explicit cast |
| `exception_pct` | percentage containing `try`, `catch`, `throw`, or `noexcept` |
| `inline_assembly_pct` | percentage containing inline assembly |
| `programs_analyzed` | denominator (extracted programs, or 3,980 training examples for the Dataset row) |
| `template_count`, `lambda_count`, ... | exact number of analyzed programs containing each feature |

The `*_pct` columns reproduce the values printed in Figure 2(b): one decimal
for method rows and two decimals for the Dataset row. The `*_count` columns and
`programs_analyzed` are the exact file-level counts; the heatmap colors are
computed from these exact ratios, so the CSV can be used to recompute both the
displayed values and the color scale.

The ten method rows come from the per-run structural reports of the evaluated
configurations. The `Dataset` row is an **aggregate** computed with exactly
the same lexical analyzer over the `<code>` blocks of all 3,980 training
examples. It reports aggregate counts and percentages over the training set.

Feature detection uses deterministic lexical patterns (see
`scripts/analyze_structures.py`). A program may match several feature
categories; a ratio is the number of programs with at least one match divided
by the number of programs analyzed. For method rows the denominator is the
number of extracted programs; for the Dataset row it is 3,980 training
examples.

## 4. Figure 2 in the final manuscript

The final manuscript has one two-panel figure:

- **Figure 2(a)** — end-to-end compile yield vs. final compiler line coverage;
- **Figure 2(b)** — structural feature frequencies for the Dataset and the
  ten coordination configurations.

`scripts/plot_figure2.py` rebuilds both panels as a single figure by default:

```bash
python scripts/plot_figure2.py --no-show
# writes figures/figure2_compile_yield_and_structure.{png,pdf,svg}
```

To generate one panel only:

```bash
python scripts/plot_figure2.py --no-show --panel a
# writes figures/figure2a_compile_yield_vs_coverage.{png,pdf,svg}

python scripts/plot_figure2.py --no-show --panel b
# writes figures/figure2b_structural_features.{png,pdf,svg}
```

### Heatmap color scale

The final manuscript caption uses **within-feature robust z-scores**, so the
script defaults to a median/MAD normalization:

```text
z = (x - median) / (1.4826 * median_absolute_deviation)
```

The center and scale are computed over the ten coordination configurations;
the aggregate Dataset row uses the same center and scale. Colors are clipped
to `[-2, +2]` and are computed from the exact `*_count` / `programs_analyzed`
ratios. Cell labels use the one-/two-decimal values printed in Figure 2(b).
Use `--zscore-over all` to include the Dataset row in the normalization.

For comparison with the earlier preprint, which used mean/SD normalization,
the script also provides:

```bash
python scripts/plot_figure2.py --no-show --zscore std
# writes figures/figure2b_structural_features_std.{png,pdf,svg}
```

Panel (a) uses filled markers for the three coordination categories and
hollow diamonds for the five reference configurations, following the final
manuscript figure.

## 5. Experimental setup

| Item | Value |
|---|---|
| Base model | Qwen2.5-Coder-7B-Instruct |
| Training data | 3,980 instruction-response examples |
| Target compiler | self-built GCC 13.1.0 with coverage instrumentation, commit `cc035c5d` |
| Language standard | C++23 |
| Evaluation budget | 10,000 calls per configuration |
| Prompt | fixed fuzzing instruction requesting `<think>...</think><code>...</code>` |
| Sampling | temperature 1.0, top-p 0.8 |
| Maximum new tokens | 1,024 per output |
| Compilation timeout | 10 s |
| Address-space limit | 8 GiB |
| Coverage | GCC source lines executed while compiling the generated programs, summarized with lcov 1.16 |

Full training configurations, evaluation settings, and software versions are
in [`configs/training_configs.yaml`](configs/training_configs.yaml),
[`configs/evaluation_config.yaml`](configs/evaluation_config.yaml), and
[`configs/environment.md`](configs/environment.md).

## 6. Reproducing the reported analyses

### Table 2

```bash
python scripts/compute_metrics.py
python scripts/summarize_table2.py --output table2_summary.md
```

`compute_metrics.py` exits with status 1 if any recomputed rate differs from
the published Table 2 value by more than 0.011 percentage points.
`summarize_table2.py` renders the 15 configurations, the four manuscript
`Avg.` rows (RFT, Joint optimization, Adaptive routing, and Policy shaping),
the relative final-coverage changes with respect to the base model, and the
best and second-best individual approaches per metric. Category averages use
unweighted means and half-up rounding to match the manuscript.

### Figure 2

```bash
python scripts/plot_figure2.py --no-show
```

The default output is the combined two-panel figure. See Section 4 for the
single-panel and z-score options. The script reads the public CSVs in
`data/`.

### Structural analyzer

```bash
python scripts/analyze_structures.py path/to/codes/ --pattern "case_*.cpp"
python scripts/analyze_structures.py path/to/codes/ --all --json report.json
```

This is the analyzer used for Figure 2(b). It applies deterministic lexical
patterns; a program may match several feature categories, and ratios are
file-level. The script runs on any directory of C++ files.

## 7. Compiler failure case

The TRAPO configuration produced the manually verified ICE in the evaluation.
The reduced two-line test case is the exact original source.

```bash
cd ice
chmod +x reproduce.sh
./reproduce.sh --runs 5

# Cross-version check:
CXX=/usr/bin/g++ ./reproduce.sh --runs 3

# Negative control:
CXX=clang++ STD=c++2b ./reproduce.sh
```

Verified results: instrumented GCC 13.1.0 reproduces the ICE 5/5; stock Ubuntu
GCC 11.4.0 reproduces it 3/3; clang 13.0.1 produces a regular diagnostic with
no ICE. See [`ice/README.md`](ice/README.md) for the full evidence table,
diagnostics, and upstream status.

## 8. Interpretation notes

1. **Verified ICEs.** The evaluation pipeline also records an automated
   `CRASH_ICE` label. The `verified_ice_count` column counts failures that
   were manually inspected and reproduced; the manual inspection separates
   genuine compiler failures from ordinary compilation errors.
2. **Reference coverage sampling.** SFT, GRPO, GSPO, and SFT→GSPO were produced
   by an earlier pipeline that sampled coverage hourly. Table 2 uses their
   final coverage values; the 20-batch runs provide the coverage trajectories.
3. **Prompt protocol.** DFT→GSPO uses the Qwen chat template and a dedicated
   system prompt; the other fourteen configurations use the raw prompt string.
4. **Single runs.** Each configuration was evaluated once; the reported
   differences are descriptive.
5. **Compiler-side coverage.** "Final line coverage" counts the GCC source
   lines executed while compiling the generated programs.
6. **Call-level budget.** The 10,000-call budget counts calls; repeated
   programs contribute to the accumulated coverage process.
7. **Category averages.** `Avg.` rows are descriptive unweighted means over the
   approaches in each category. ICE counts are reported per approach; the
   `Avg.` ICE cell is `—`.

## 9. Data availability

This package provides the aggregated experimental results underlying Table 2
and Figure 2, the analysis scripts, the experimental configuration, and the
compiler failure reproduction materials at
https://github.com/Sodabubble0/srhf-compiler-fuzzing.

The curated dataset of 3,980 supervised fine-tuning examples, trained model
checkpoints, and the complete generated test corpus are maintained separately.
The package supports reproduction of the reported aggregate analyses and the
compiler failure case; full model retraining uses the training set and
checkpoints.

A standalone version of this statement, suitable for the submission system,
is in [`DATA_AVAILABILITY.md`](DATA_AVAILABILITY.md).

## 10. Repository layout

```text
srhf-compiler-fuzzing-results/
├── README.md
├── DATA_AVAILABILITY.md
├── data/
│   ├── table2_results.csv
│   ├── evaluation_counts.csv
│   └── figure2_structural_features.csv
├── configs/
│   ├── training_configs.yaml
│   ├── evaluation_config.yaml
│   └── environment.md
├── scripts/
│   ├── compute_metrics.py
│   ├── summarize_table2.py
│   ├── plot_figure2.py
│   ├── analyze_structures.py
│   └── requirements.txt
└── ice/
    ├── original.cpp
    ├── minimized.cpp
    ├── reproduce.sh
    ├── gcc_output.txt
    ├── README.md
    └── logs/
```

`figures/` is created by `plot_figure2.py` at runtime.

## 11. Contact

Corresponding author: Libin Yang — `libiny@nwpu.edu.cn`

Other authors: Qinghao Zhang (`qinghaozhang@mail.nwpu.edu.cn`), Dehong Gao,
Lingyue Huang, Qichao Zhang, Xiaoyan Cai.
