# Data Availability Statement

Paper: **Survey of Supervised and Reinforced Hybrid Fine-tuning and
Fuzz-Oriented Empirical Study**

## Statement for the manuscript

> The aggregated experimental results underlying Table 2 and Figure 2,
> analysis scripts, experimental configurations, and compiler failure
> reproduction materials are available at
> **https://github.com/Sodabubble0/srhf-compiler-fuzzing**.
>
> The curated dataset of 3,980 supervised fine-tuning examples, trained model
> checkpoints, and the complete generated test corpus are maintained by the
> authors alongside the broader experimental environment. The public package
> supports reproduction of the reported aggregate analyses and the compiler
> failure case; full model retraining uses the curated training set and
> checkpoints.

The repository URL is
**https://github.com/Sodabubble0/srhf-compiler-fuzzing**. If a Zenodo DOI is
added later, update this statement and the submission-system link.

## Suggested submission-system fields

| Field | Suggested value |
|---|---|
| Do you want to share data? | Yes |
| Link to data repository | https://github.com/Sodabubble0/srhf-compiler-fuzzing |
| Repository name | GitHub or Zenodo (whichever hosts the repository) |
| Source of data | Original data |
| Title of the data set | SRHF Compiler Fuzzing: Aggregated Results and Analysis Artifacts |

## Scope

The repository contains:

- the published Table 2 metrics and the extracted/compiled counts behind them,
  including the category averages recomputed by the provided script;
- the compile-yield and final-coverage values used in Figure 2(a);
- the structural feature counts and percentages used in Figure 2(b),
  including an aggregate Dataset row computed over the 3,980 training
  examples;
- training and evaluation configuration files;
- analysis and plotting scripts;
- the original and reduced TRAPO test case, reproduction script, diagnostics,
  and archived run logs.

The training samples, expert responses, reasoning traces, model checkpoints,
generated test corpus, full training logs, compiler binaries, and figure files
are maintained in the authors' experimental environment. The aggregate Dataset
row reports counts and percentages over the 3,980 examples.

## Sharing scope

This statement reflects the current sharing scope. The 3,980-example training
set underlies the supervised and coordinated training results. The public
package documents the aggregate analyses and the compiler failure case; full
retraining uses the curated training set and checkpoints.
