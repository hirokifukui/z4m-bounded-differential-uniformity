// r03 T9 / c1: assert version of r02 s1 + s6 + s9 (form1 family, Teichmuller digits).
// OUTPUT (A9, 2026-10-30): hk0-2 Jacobian OK MV 440; hk3 Jacobian OK MV 510; random (p,d,h) 6/6 OK; C1 ALL PASS.
P<U,v,s,t,A,b> := PolynomialRing(GF(2),6);
d := func<x | x^4+x^2+1>;
hs := [* func<x | 0*x>, func<x | x^3>, func<x | x^2>, func<x | x^5> *];
a := A^2; u := U^2;
sup := func<f | {[e[5], e[6]] : e in [Exponents(m) : m in Monomials(f)]} join {[0,0]}>;
expMV := [440,440,440,510];
for k in [1..4] do
  h := hs[k];
  L  := h(a) + d(a)*b; Lp := h(a+u) + d(a+u)*(b+v+A*U);
  Z0 := L^3; Z1 := h(L) + d(L)*a^3; Y0 := Lp^3; Y1 := h(Lp) + d(Lp)*(a+u)^3;
  Sq := (Y1+Z0+Z1+t)^2; Psi := Y0+Z0; Pr := Y0*Z0;
  assert Derivative(Sq,A) eq 0 and Derivative(Sq,b) eq 0;
  Jac := Derivative(Psi,A)*Derivative(Pr,b) + Derivative(Psi,b)*Derivative(Pr,A);
  assert Jac eq Psi*L^2*Lp^2*d(a)*d(a+u)*U;
  E1 := Psi + s; E2 := Sq + Pr;
  P1 := Polytope([x : x in sup(E1)]); P2 := Polytope([x : x in sup(E2)]);
  mv := (Volume(P1+P2) - Volume(P1) - Volume(P2))/2;
  assert mv eq expMV[k];
  printf "hk%o: Jacobian identity OK, MV = %o OK\n", k-1, mv;
end for;
Q<x> := PolynomialRing(GF(2)); ev := func<f, y | Evaluate(f, y)>; SetSeed(7);
for rep in [1..6] do
  p := Q![Random(GF(2)) : i in [0..Random(2,5)]] + x; dd := Q![Random(GF(2)) : i in [0..Random(2,4)]] + 1;
  hh := Q![Random(GF(2)) : i in [0..Random(1,4)]];
  L := ev(hh,a)+ev(dd,a)*b; Lp := ev(hh,a+u)+ev(dd,a+u)*(b+v+A*U);
  Z0 := ev(p,L); Y0 := ev(p,Lp);
  jac := Derivative(Y0+Z0,A)*Derivative(Y0*Z0,b)+Derivative(Y0+Z0,b)*Derivative(Y0*Z0,A);
  assert jac eq (Y0+Z0)*ev(Derivative(p),L)*ev(Derivative(p),Lp)*ev(dd,a)*ev(dd,a+u)*U;
end for;
print "random (p,d,h) Jacobian identity: 6/6 OK";
print "C1 ALL PASS";
