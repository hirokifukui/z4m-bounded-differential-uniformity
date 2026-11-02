// r04 T6: G_c = F_c o J o F_c in the actual ring GR(4,m) = Z4[X]/(f), full DDT, ring addition only.
// Parameters (Magma command line, strings):  mlo, mhi, cmax  (cmax = 0 means all c with Tr(c)=1).
//   magma mlo:=1 mhi:=5 cmax:=0 t5_ringmodel_v2.m      // r03 run 1
//   magma mlo:=6 mhi:=6 cmax:=2 t5_ringmodel_v2.m      // r03 run 2
// Field: F = GF(2)[x]/(f2), f2 = IrreduciblePolynomial(GF(2),m) (printed). c is indexed by the order of
// VectorSpace(GF(2),m) enumeration (printed as Eltseq). Teichmuller digits x = T(a)+2T(b), T(a) = lift(a)^q mod f.
// No Teichmuller addition formula is used: digits are recovered from ring elements by table lookup.
// Exits with a runtime error (no "ALL PASS") if G_c is not a permutation or Delta > 36.
if not assigned mlo then mlo := "1"; end if;
if not assigned mhi then mhi := "5"; end if;
if not assigned cmax then cmax := "0"; end if;
mlo := StringToInteger(mlo); mhi := StringToInteger(mhi); cmax := StringToInteger(cmax);
assert 1 le mlo and mlo le mhi and cmax ge 0;
Z4 := Integers(4); P<X> := PolynomialRing(Z4);
maxall := 0; nmaps := 0;
for m in [mlo..mhi] do
  f2 := IrreduciblePolynomial(GF(2), m);
  F<w> := ext<GF(2) | f2>; q := 2^m;
  f := P![Integers()!c : c in Eltseq(f2)];
  Els := [F!Eltseq(e) : e in VectorSpace(GF(2),m)];
  ixF := AssociativeArray(F); for i in [1..q] do ixF[Els[i]] := i; end for;
  liftp := func<a | P![Integers()!z : z in Eltseq(a)]>;
  T := [ (liftp(a)^q) mod f : a in Els ];
  vec := func<g | [Integers()!Coefficient(g,i) : i in [0..m-1]]>;
  key := func<v | &+[ (v[i] mod 4) * 4^(i-1) : i in [1..m]]>;
  N := 4^m; digA := [0 : i in [1..N]]; digB := [0 : i in [1..N]]; elv := [[0 : j in [1..m]] : i in [1..N]];
  for ia in [1..q] do for ib in [1..q] do
    v := vec((T[ia] + 2*T[ib]) mod f); k := key(v)+1;
    digA[k] := ia; digB[k] := ib; elv[k] := v;
  end for; end for;
  assert &and[digA[k] ne 0 : k in [1..N]];
  cs := [c : c in Els | Trace(c) eq 1];
  if cmax gt 0 and cmax lt #cs then cs := cs[1..cmax]; end if;
  printf "m=%o f2=%o #c=%o\n", m, f2, #cs;
  for c in cs do
    D := func<x | x^2+x+c>;
    Gk := [0 : i in [1..N]];
    for k in [1..N] do
      a := Els[digA[k]]; b := Els[digB[k]];
      L := D(a)*b; a2 := L; b2 := D(L)*a;
      Gk[k] := key(vec((T[ixF[a2]] + 2*T[ixF[b2]]) mod f)) + 1;
    end for;
    assert #Set(Gk) eq N;
    Dl := 0; ndir := 0;
    for ka in [2..N] do
      av := elv[ka]; cnt := [0 : i in [1..N]];
      for k in [1..N] do
        xa := key([elv[k][i] + av[i] : i in [1..m]]) + 1;
        dv := [elv[Gk[xa]][i] - elv[Gk[k]][i] : i in [1..m]];
        j := key(dv) + 1; cnt[j] +:= 1;
      end for;
      Dl := Max(Dl, Max(cnt)); ndir +:= 1;
    end for;
    assert ndir eq N-1;
    maxall := Max(maxall, Dl); nmaps +:= 1;
    printf "m=%o c=%o Delta=%o dirs=%o %o\n", m, Eltseq(c), Dl, ndir, Dl le 36 select "OK" else "FAIL";
  end for;
end for;
printf "maps=%o MAX=%o\n", nmaps, maxall;
assert maxall le 36;
print "T5 ALL PASS";
quit;
