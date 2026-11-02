# Explicit permutations of (Z/4Z)^m with uniformly bounded differential uniformity

Paper and supplementary material (version 1.0.0) of H. Fukui, *Explicit permutations of (Z/4Z)^m with uniformly
bounded differential uniformity*.

This version is archived at Zenodo, DOI [10.5281/zenodo.23875216](https://doi.org/10.5281/zenodo.23875216)
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
| `paper/main_theory_v7.tex`, `paper/main_theory_v7.pdf` | the paper (8 pages) |
| `REPRODUCE.md` | how to rerun every check |
| `magma/`, `logs/` | Magma scripts listed in Appendix A of the paper and their outputs |
| `runner/` | C program for Table 1 (digit formulas), its fail-closed runner, validator and negative controls |
| `studio_runs/runs/` | the 11 recorded runs used for Table 1 (m = 1..10) |
| `make_manifest.py`, `expected_*.tsv` | fail-closed aggregator and what it must find |
| `TABLE_PROVENANCE.tsv`, `parameters.json` | provenance of each entry of Table 1 |
| `SHA256SUMS` | SHA-256 of every other file |
| `CITATION.cff`, `LICENSE` | citation metadata; licences |

## Rebuilding the PDF
```
cd paper && pdflatex main_theory_v7.tex && pdflatex main_theory_v7.tex
```

## Licences
Text (paper, README.md, REPRODUCE.md, CITATION.cff): CC BY 4.0. Scripts, programs and recorded outputs: MIT.
See `LICENSE`.
