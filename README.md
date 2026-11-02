# Explicit permutations of (Z/4Z)^m with uniformly bounded differential uniformity

Paper and supplementary material (version 1.0.1) of H. Fukui, *Explicit permutations of (Z/4Z)^m with uniformly
bounded differential uniformity*.

This version is archived at Zenodo, DOI [10.5281/zenodo.23875707](https://doi.org/10.5281/zenodo.23875707)
(all versions: [10.5281/zenodo.23875215](https://doi.org/10.5281/zenodo.23875215)).

## The result
Let R = GR(4,m) and q = 2^m, so that the additive group (R,+) ≅ (Z/4Z)^m has order N = q^2. In Teichmüller digits
(a,b) ∈ F_q^2 and for c ∈ F_q of absolute trace 1, the map

    G_c(a,b) = (L, (L^2 + L + c) a),   L = (a^2 + a + c) b,

is a permutation of R with differential uniformity at most 36 for every m ≥ 1 (with respect to ring addition): every
differential with a nonzero input difference holds with probability at most 36/N. Every permutation polynomial of R has
a differential of probability at least 2/√N (Rønjom–Sandrib). The bound concerns the fixed permutation, not an
average over keys. The proof is elementary and does not depend on the computations below.

## Contents
| Path | What it is |
|---|---|
| `paper/main_theory_v8.tex`, `paper/main_theory_v8.pdf` | the paper (8 pages) |
| `REPRODUCE.md` | how to rerun every check (byte check of the manifest first, recomputation on a separate copy) |
| `magma/`, `logs/` | Magma scripts listed in Appendix A of the paper and their outputs |
| `runner/` | C program for Table 1 (digit formulas), its fail-closed runner, validator and negative controls |
| `studio_runs/runs/` | the 11 recorded runs used for Table 1 (m = 1..10; two values of c for m = 8); `host=` in `meta.txt` is the label of the machine that ran them |
| `make_manifest.py`, `expected_*.tsv` | fail-closed aggregator and what it must find |
| `TABLE_PROVENANCE.tsv`, `parameters.json` | provenance of each entry of Table 1 |
| `SHA256SUMS` | SHA-256 of every other file |
| `CITATION.cff`, `LICENSE`, `CHANGELOG.md` | citation metadata; licences; changes between versions |

## Rebuilding the PDF
```
cd paper && pdflatex main_theory_v8.tex && pdflatex main_theory_v8.tex
```

## Licences
Text (paper, README.md, REPRODUCE.md, CITATION.cff): CC BY 4.0. Scripts, programs and recorded outputs: MIT.
See `LICENSE`.
