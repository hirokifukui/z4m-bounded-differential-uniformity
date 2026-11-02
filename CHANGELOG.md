# Changelog

## 1.0.2 (2026-11-02)
No change to any theorem, proof, table value, recorded computation or script.
- Paper (`paper/main_theory_v9`): the affiliation and e-mail are also given on the first page (footnote), as the IACR
  ePrint rules ask; PDF title and author metadata.

## 1.0.1 (2026-11-02)
No change to any theorem, proof, table value or recorded computation.
- Paper (`paper/main_theory_v8`): the abstract states separately that every permutation has Δ ≥ 2 (Proposition 3.2), the
  lower end of 2 ≤ D_m ≤ 36; the Appendix names where the supplementary material is archived (Zenodo concept DOI and
  GitHub); arXiv and DOI links for [2] and [7]; an internal TeX comment removed.
- `REPRODUCE.md`: the byte-for-byte check of the manifest comes first, on an untouched copy, with `python3 -B`;
  recomputations go on a separate copy; how to save new Magma output.
- `make_manifest.py`: does not write bytecode and never hashes `__pycache__` or hidden directories such as `.git` (in
  1.0.0, a plain `python3` run could add `runner/__pycache__` to SHA256SUMS, and a run inside a git checkout could add `.git`).
- Comments in `runner/negative_tests.sh` and `runner/test_manifest.py` describe the controls by what they test.
- `CITATION.cff`: no top-level licence list (the licences differ by file; see LICENSE); the paper is CC BY 4.0.
- README: the 11 runs include two values of c for m = 8; meaning of `host=` in the run records.

## 1.0.0 (2026-11-02)
First release (DOI 10.5281/zenodo.23875216).
