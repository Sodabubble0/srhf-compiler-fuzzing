# Experimental environment

This document records the environment used for the experiments in the paper.
It supports interpretation and, where possible, reproduction of the evaluation
protocol and the compiler-failure case. GCC sources, compiler binaries, CUDA
packages, container images, model weights, and the training set remain in the
authors' experimental environment.

## 1. Hardware and operating system

| Item | Value |
|---|---|
| GPU | 5 × NVIDIA A800-SXM4-80GB (one GPU per training or evaluation run) |
| CPU | 112 cores |
| Memory | 251 GB (shared machine; fuzz subprocesses were memory-capped) |
| OS | Ubuntu 22.04, Linux kernel 6.8.0 |

## 2. Python environment used for the paper

| Item | Value |
|---|---|
| Environment | conda environment `FuzzLLMs-Zero-zqh` |
| Python | 3.10.18 |
| PyTorch | 2.10.0+cu128 |
| Transformers | 5.3.0 |
| TRL | 0.29.0 (`GRPOTrainer`; the reinforcement-based configurations extend it) |
| PEFT | 0.18.1 |
| Datasets | 4.7.0 |
| Accelerate | 1.6.0 |
| LLaMA-Factory | 0.9.4.dev0 (used for the conventional SFT baseline) |
| CUDA | 12.8 |

The versions above cover the packages that matter for interpreting the
training and evaluation behavior.

## 3. Compiler target

| Item | Value |
|---|---|
| Compiler | GCC 13.1.0, self-built coverage-instrumented build named `GCC-13-COVERAGE` |
| Source | `releases/gcc-13.1.0` tag |
| Commit | `cc035c5d8672f87dc8c2756d9f8367903aa72d93` (2023-04-26) |
| Configure flags | `--enable-languages=c,c++ --enable-coverage --disable-multilib` |
| Build | Boostrapped with `./contrib/download_prerequisites`, `make -j$(nproc)`, `make install` |
| Language standard for fuzz cases | C++23 (`-std=c++23`) |
| Compile command | `timeout 10s g++ -x c++ -std=c++23 <case>.cpp -o <work_dir>/coverage/<case>` |
| Memory cap | `RLIMIT_AS = 8 GiB` in the evaluation pipeline |

The `--enable-coverage` build instruments the compiler itself. The generated
test programs use the standard compile command; the measurement target is the
set of GCC source lines executed while compiling them.

### Cross-check compilers used for the ICE case

| Compiler | Version | Role |
|---|---|---|
| Instrumented GCC | 13.1.0, commit `cc035c5d` | evaluated build; ICE reproduced 5/5 |
| Stock Ubuntu g++ | 11.4.0-1ubuntu1~22.04.2 | cross-version check; ICE reproduced 3/3 |
| Clang | Ubuntu clang 13.0.1-2ubuntu2.2 | negative control; clean diagnostic, no ICE |

The clang 13 control used `-std=c++2b`.

## 4. Coverage and fuzzing tools

| Tool | Version / role |
|---|---|
| gcov | shipped with the instrumented GCC 13.1.0 build |
| lcov | 1.16 (`--capture`, `--gcov-tool`, `--ignore-errors source,graph`) |
| AFL++ `afl-showmap` | used during training-time reward computation; the final 10,000-call measurement uses the compiler's gcov instrumentation |
| Coverage redirect | `GCOV_PREFIX=<work_dir>/gcda_feed`, `GCOV_PREFIX_STRIP=0` |
| Coverage merge | `.gcda` tree copied into `gcc-coverage-build/gcc`, then summarized with lcov |

The persisted environment record covers the Python and compiler stack. During
training, fuzz subprocesses were run with `afl-showmap -m 4096` and a
`prlimit` watchdog, because the machine is shared.

## 5. Training data

| Item | Value |
|---|---|
| Dataset size | 3,980 instruction-response examples |
| Construction | Compiled primarily from historical GCC Bugzilla reports and attached C++ test cases, followed by extraction, cleaning, deduplication, and structured organization |
| Fields | `instruction`, `input`, `output` |
| Prompt-length filter | at most 512 tokens (all 3,980 examples passed) |
| Public release | Aggregate counts and percentages are included in this package; the 3,980 examples and their contents remain in the authors' experimental environment. |

The aggregate structural frequencies of the dataset that appear as the
`Dataset` row of `data/figure2_structural_features.csv` were computed with the
same lexical analyzer that is published in `scripts/analyze_structures.py`.
This package reports aggregate counts and percentages over the 3,980
examples.

## 6. Minimal environment for this repository

The public analysis scripts run with:

- Python 3.9 or newer
- `numpy`
- `matplotlib`

Install with:

```bash
python -m pip install -r scripts/requirements.txt
```

The ICE reproduction additionally requires a C++ compiler. It was verified
with the instrumented GCC 13.1.0 build and with stock Ubuntu g++ 11.4.0.

## 7. Recording notes

- The GCC source commit was identified from the build tree and the
  `releases/gcc-13.1.0` tag.
- AFL++ usage is recorded in Section 4.
- The four reference runs (SFT, GRPO, GSPO, SFT→GSPO) were produced by an
  earlier pipeline that sampled coverage hourly. Table 2 uses their final
  coverage values.
- All reported configurations are single runs and are reported descriptively.
