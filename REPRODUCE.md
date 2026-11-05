# Reproducing the computations (main_theory_v10)

The proofs in the paper do not depend on these computations. They check the stated identities and degrees and
recompute Table 1.

## Contents
- `paper/main_theory_v10.tex`, `paper/main_theory_v10.pdf` — the manuscript.
- `magma/` — Magma scripts listed in Appendix A, plus `r06_t1_expected.m` (expected parameter list of the ring-model logs).
- `logs/` — Magma output (A9). Completion of a Magma run is judged by its final assertion/PASS line; the operating-system
  exit status was not recorded.
- `runner/` — C program `gc_ddt_v2.c` for Table 1 (digit formulas), its fail-closed runner `run_gc_v2.sh`, the shared
  validator `validate_run.py`, and negative controls (`negative_tests.sh`, `test_manifest.py`).
- `studio_runs/runs/` — the 11 recorded runs used for Table 1 (m = 1..10; two values of c for m = 8).
- `expected_runs.tsv`, `expected_magma_ring.tsv` — what the manifest must find; `make_manifest.py` — fail-closed
  aggregator writing `TABLE_PROVENANCE.tsv`, `parameters.json`, `SHA256SUMS`.

## 1. Byte-for-byte check of the published manifest (first, on an untouched unpacked copy)
```sh
python3 -B make_manifest.py . studio_runs/runs   # rewrites TABLE_PROVENANCE.tsv, parameters.json, SHA256SUMS
git diff --stat                                   # (in a git checkout) or compare with the files of the archive: no change
python3 -B runner/test_manifest.py .              # 35 aggregator controls
```
`-B` keeps Python from writing `__pycache__`; the aggregator also sets this itself and never hashes `__pycache__`.

## 2. Rerunning the computations (on a separate copy)
Compiling the runner and new runs add files, so the SHA256SUMS of that copy will differ from the published one; the
recorded runs in `studio_runs/runs/` and the logs in `logs/` are the ones the paper uses. Magma writes to standard
output; the comments `# -> ../logs/...` name the published log of each run, and a new output can be saved with
`> new.log`.
```sh
# Magma (any recent version), run from the magma/ directory of the package
cd magma
magma t4_v2_bounded36_symbolic.m
magma mlo:=1 mhi:=5 cmax:=0 t5_ringmodel_v2.m      # -> ../logs/magma_r04_t5_m1to5.log
magma mlo:=6 mhi:=6 cmax:=2 t5_ringmodel_v2.m      # -> ../logs/magma_r04_t5_m6.log
magma c1_form1_assert.m; magma t3_u0_form1_v2.m; magma t1_J_counterexample.m
magma r05_t1_digit_swap.m; magma t6_sigma_row.m; magma r06_t1_expected.m
cd ..

# C (digit formulas), from the runner/ directory
cd runner
clang -O3 -o gc_ddt_v2 gc_ddt_v2.c        # or cc -O3
./run_gc_v2.sh 7 0 20 runs                # m cidx K [outroot]; prints MAX ... only if every check passes
bash negative_tests.sh                    # 17 runner controls
cd ..

```

## Scope of the checks
The manifest checks that the recorded outputs are complete, well formed and consistent with the deterministic partition
of directions (C) and with the expected parameter list (Magma); it is not a proof that a program executed. For m = 6 the
ring model covers two values of c (the first two in Magma's enumeration), not all 32.
