// r04 T6: u=0 direction of the form1 family (p=x^3, d=x^4+x^2+1, h in {0,x^3,x^2,x^5}).
// Asserts: removed d-factor exponent 2 (h=0,x^3,x^2) / 4 (h=x^5); deg g = 88 / 96; lc g = v^21 / v^28;
// g has only even exponents in a; over K(a), E2 mod E1 is linear in L with coefficient s^2/w.
K<v,s,t> := FunctionField(GF(2),3);
R<a> := PolynomialRing(K); S<L> := PolynomialRing(R);
d := func<x | x^4+x^2+1>;
hs := [* func<x | 0*x>, func<x | x^3>, func<x | x^2>, func<x | x^5> *];
expE := [2,2,2,4]; expDeg := [88,88,88,96]; expLc := [v^21, v^21, v^21, v^28];
for k in [1..4] do
  h := hs[k]; w := v*d(a); Lp := L + w;
  E1 := Lp^3 + L^3 + s;
  E2 := (h(Lp)+d(Lp)*a^3 + L^3 + h(L)+d(L)*a^3 + t)^2 + Lp^3*L^3;
  g := Resultant(E1, E2); e := 0; while g mod d(a) eq 0 do g := g div d(a); e +:= 1; end while;
  assert e eq expE[k]; assert Degree(g) eq expDeg[k]; assert LeadingCoefficient(g) eq expLc[k];
  assert #[i : i in [0..Degree(g)] | IsOdd(i) and Coefficient(g,i) ne 0] eq 0;
  printf "hk%o: removed d^%o, deg %o, lc %o  OK\n", k-1, e, Degree(g), LeadingCoefficient(g);
end for;
K2<v,s,t,a> := FunctionField(GF(2),4); S2<L> := PolynomialRing(K2);
d2 := func<x | x^4+x^2+1>;
hs2 := [* func<x | 0*x>, func<x | x^3>, func<x | x^2>, func<x | x^5> *];
for k in [1..4] do
  h := hs2[k]; w := v*d2(a); Lp := L + w;
  E1 := Lp^3 + L^3 + s; E2 := (h(Lp)+d2(Lp)*a^3 + L^3 + h(L)+d2(L)*a^3 + t)^2 + Lp^3*L^3;
  r := E2 mod E1; assert Degree(r) eq 1 and Coefficient(r,1) eq s^2/w;
end for;
print "T3 PASS";
quit;
