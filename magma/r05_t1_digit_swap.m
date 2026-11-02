// r05 T1: exact Delta of literal digit swap J(a,b)=(b,a) under Teichmuller and coordinate digit laws, m=1..5
// Teichmuller: (a,b)+(u,v)=(a+u, b+v+sqrt(a u)); coordinate: (a,b)+(u,v)=(a xor u, b xor v xor (a and u)).
// DDT entry count #{x : J(x+alpha) = J(x)+beta}; beta recovered by solving z+beta=y.
polys := [ [1,1], [1,1,1], [1,1,0,1], [1,1,0,0,1], [1,0,1,0,0,1] ];
P<t> := PolynomialRing(GF(2));
for m in [1..5] do
  q := 2^m; N := q*q;
  f := P!polys[m]; assert IsIrreducible(f);
  F<w> := ext<GF(2) | f>;
  E := [ F!Intseq(i,2,m) : i in [0..q-1] ];   // index i <-> element with bit j = coeff of w^j
  idx := AssociativeArray(); for i in [0..q-1] do idx[E[i+1]] := i; end for;
  sq := func< z | z^(2^(m-1)) >;
  // precompute tables on indices
  MUL := [ [ idx[E[i+1]*E[j+1]] : j in [0..q-1] ] : i in [0..q-1] ];
  SQ := [ idx[sq(E[i+1])] : i in [0..q-1] ];
  bestT := 0; argT := [];
  bestC := 0; argC := [];
  for al in [1..N-1] do
    u := al div q; v := al mod q;
    cntT := AssociativeArray(); cntC := AssociativeArray();
    for a in [0..q-1] do
      carryT := SQ[MUL[a+1][u+1]+1];
      carryC := BitwiseAnd(a,u);
      for b in [0..q-1] do
        // Teichmuller: x=(a,b), x+alpha=(a xor u, b xor v xor carryT); J swaps
        y0 := BitwiseXor(BitwiseXor(b,v),carryT); y1 := BitwiseXor(a,u);
        z0 := b; z1 := a;
        be0 := BitwiseXor(y0,z0); be1 := BitwiseXor(BitwiseXor(y1,z1), SQ[MUL[z0+1][be0+1]+1]);
        key := be0*q+be1; cntT[key] := IsDefined(cntT,key) select cntT[key]+1 else 1;
        // coordinate
        y0 := BitwiseXor(BitwiseXor(b,v),carryC); y1 := BitwiseXor(a,u);
        be0 := BitwiseXor(y0,z0); be1 := BitwiseXor(BitwiseXor(y1,z1), BitwiseAnd(z0,be0));
        key := be0*q+be1; cntC[key] := IsDefined(cntC,key) select cntC[key]+1 else 1;
      end for;
    end for;
    mt := Max([cntT[k] : k in Keys(cntT)]); mc := Max([cntC[k] : k in Keys(cntC)]);
    if mt gt bestT then bestT := mt; argT := [al]; end if;
    if mc gt bestC then bestC := mc; argC := [al]; end if;
  end for;
  // witness for coordinate: alpha=(0,e0) i.e. u=0,v=1 ; beta=(e0,0) i.e. index 1*q+0
  wit := #[ 1 : a in [0..q-1], b in [0..q-1] | BitwiseXor(BitwiseXor(b,1),0) eq BitwiseXor(b,1) and
            (BitwiseXor(b,1) eq BitwiseXor(b,1)) and
            (BitwiseXor(BitwiseXor(b,1),b) eq 1) and (BitwiseXor(BitwiseXor(a,a), BitwiseAnd(b,1)) eq 0) ];
  printf "m=%o q=%o DeltaT=%o (expect q=%o) DeltaC=%o (expect q^2/2=%o) witness_count=%o\n", m, q, bestT, q, bestC, N div 2, wit;
  assert bestT eq q; assert bestC eq N div 2; assert wit eq N div 2;
end for;
print "PASS r05_t1_digit_swap";
