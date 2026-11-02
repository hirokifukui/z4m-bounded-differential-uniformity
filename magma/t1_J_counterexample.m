// r04 T1: negative control for the over-general claim. p=x, d=1, h=0 gives F=id, so F o J o F = J,
// J(a,b)=(b,a) in Teichmuller digits of GR(4,m)=Z4[X]/(f). Full DDT in the ring model (ring addition only).
// Asserts Delta(J) = q for m=1..5, and that the single row alpha = T(1) (digits (1,0)) already has an
// output value hit q times (on the inputs with a=0).
Z4 := Integers(4); P<X> := PolynomialRing(Z4);
for m in [1..5] do
  f2 := IrreduciblePolynomial(GF(2), m); F := ext<GF(2) | f2>; q := 2^m;
  f := P![Integers()!c : c in Eltseq(f2)];
  Els := [F!Eltseq(e) : e in VectorSpace(GF(2),m)];
  ixF := AssociativeArray(F); for i in [1..q] do ixF[Els[i]] := i; end for;
  liftp := func<a | P![Integers()!z : z in Eltseq(a)]>;
  T := [ (liftp(a)^q) mod f : a in Els ];
  vec := func<g | [Integers()!Coefficient(g,i) : i in [0..m-1]]>;
  key := func<v | &+[ (v[i] mod 4) * 4^(i-1) : i in [1..m]]>;
  N := 4^m; digA := [0:i in [1..N]]; digB := [0:i in [1..N]]; elv := [[0:j in [1..m]]:i in [1..N]];
  for ia in [1..q] do for ib in [1..q] do
    v := vec((T[ia]+2*T[ib]) mod f); k := key(v)+1; digA[k] := ia; digB[k] := ib; elv[k] := v;
  end for; end for;
  Jk := [ key(vec((T[digB[k]] + 2*T[digA[k]]) mod f)) + 1 : k in [1..N] ];
  assert #Set(Jk) eq N;
  Dl := 0; rowone := 0;
  kone := key(vec(T[ixF[F!1]] mod f)) + 1;     // alpha = T(1), digits (1,0)
  for ka in [2..N] do
    av := elv[ka]; cnt := [0:i in [1..N]];
    for k in [1..N] do
      xa := key([elv[k][i]+av[i] : i in [1..m]]) + 1;
      j := key([elv[Jk[xa]][i]-elv[Jk[k]][i] : i in [1..m]]) + 1; cnt[j] +:= 1;
    end for;
    Dl := Max(Dl, Max(cnt)); if ka eq kone then rowone := Max(cnt); end if;
  end for;
  printf "m=%o q=%o Delta(J)=%o row(alpha=T(1)) max=%o\n", m, q, Dl, rowone;
  assert Dl eq q and rowone ge q;
end for;
print "T1 J PASS";
quit;
