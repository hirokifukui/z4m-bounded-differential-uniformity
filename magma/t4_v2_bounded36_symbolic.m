// r04 t4_v2: symbolic check of Theorem 1.1 directly from the unreduced difference equations (low: L'+L=s;
// high, squared: (D(L')(a+u)+L+D(L)a+t)^2 + L'L = 0, equivalent by injectivity of Frobenius).
// Case A (u notin {0,1}): b is determined by the low equation (coefficient kappa=u^2+u); the high equation becomes a polynomial
//   in A of degree 36 with leading coefficient U^8/kappa^4.  Also checks N = kappa*L has degree 9, leading coefficient U.
// Case B (u=1): low equation free of b, degree 5 in A, monic; high equation (given L'=L+s) monic of degree 4 in L.
// Case C (u=0): low equation = v D(a) + s; high equation (given L'=L+s) of degree 1 in L with coefficient s.
K<U,v,s,t,c> := FunctionField(GF(2),5);
R<A,b> := PolynomialRing(K,2);
D := func<x | x^2+x+c>;
a := A^2; u := U^2; kap := u^2+u;
L := D(a)*b; Lp := D(a+u)*(b+v+A*U);
E1 := Lp+L+s;
assert Degree(E1,b) eq 1 and Coefficient(E1,b,1) eq kap;
bsol := -(Coefficient(E1,b,0))/kap;
S<AA> := PolynomialRing(K);
bsolA := Evaluate(bsol,[AA,0]);
LA := Evaluate(D(a),[AA,0])*bsolA; LpA := LA + s;
NA := kap*LA; assert Degree(NA) eq 9 and LeadingCoefficient(NA) eq U;
Y1 := D(LpA)*(AA^2+u); Z1 := D(LA)*AA^2;
E2A := (Y1+LA+Z1+t)^2 + LpA*LA;
assert Evaluate(Lp,[AA,bsolA]) eq LpA;
assert Degree(E2A) eq 36 and LeadingCoefficient(E2A)*kap^4 eq U^8;
print "Case A: low determines b; deg N = 9, lc U; high deg_A 36, lc*kappa^4 = U^8  OK";
// Case B
LB := D(a)*b; LpB := D(a+1)*(b+v+A);
E1B := LpB+LB+s; assert Degree(E1B,b) le 0 and Degree(E1B,A) eq 5 and LeadingCoefficient(E1B) eq 1;
K2<v2,s2,t2,c2,A2> := FunctionField(GF(2),5); T2<LL> := PolynomialRing(K2);
D2 := func<x | x^2+x+c2>; a2 := A2^2;
LpL := LL + s2;
E2B := (D2(LpL)*(a2+1) + LL + D2(LL)*a2 + t2)^2 + LpL*LL;
assert Degree(E2B) eq 4 and LeadingCoefficient(E2B) eq 1;
print "Case B: low deg_A 5 monic, b-free; high monic deg_L 4  OK";
// Case C
LC := D(a)*b; LpC := D(a)*(b+v); assert LpC+LC+s eq v*D(a)+s;
E2C := (D2(LpL)*a2 + LL + D2(LL)*a2 + t2)^2 + LpL*LL;
assert Degree(E2C) eq 1 and Coefficient(E2C,1) eq s2;
print "Case C: low = v D(a) + s; high deg_L 1 with coefficient s  OK";
print "T4 PASS";
quit;
