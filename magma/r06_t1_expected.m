// r06 T1: expected parameter set for the T5 ring-model logs, enumerated exactly as t5_ringmodel_v2.m does.
// Run on A9 (run_magma, detach=False). Output -> logs/magma_r06_t1_expected.log; source of expected_magma_ring.tsv.
for m in [1..6] do
  f2 := IrreduciblePolynomial(GF(2), m);
  F<w> := ext<GF(2) | f2>;
  Els := [F!Eltseq(e) : e in VectorSpace(GF(2),m)];
  cs := [c : c in Els | Trace(c) eq 1];
  assert #cs eq 2^(m-1);
  assert IsIrreducible(f2);
  printf "m=%o f2=%o ntrace1=%o\n", m, f2, #cs;
  for c in cs do printf "EXP m=%o c=%o\n", m, Eltseq(c); end for;
end for;
print "R06 T1 EXPECTED ALL PASS";
quit;
