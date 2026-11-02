// r04 t6 (replaces r02 s5): coordinate (sigma) digits with basis e_0 = 1 (Magma's GF(2^m) Eltseq basis, first vector 1),
// carry = coordinatewise AND; form1 p=x^3, d=x^4+x^2+1, h=0; G = F o J o F; row alpha=(1,0).
// Asserts: the basis has e_0 = 1; row max = 6, 22, 74 for m = 3, 5, 7, and each is >= q/2 (Proposition 6.1).
d := func<x | x^4+x^2+1>;
expv := AssociativeArray(); expv[3] := 6; expv[5] := 22; expv[7] := 74;
for m in [3,5,7] do
  F := GF(2^m); q := #F;
  assert Eltseq(F!1) eq [1] cat [0 : i in [2..m]];
  andF := func<x,y | F!([ e[i]*f[i] : i in [1..m]]) where e is Eltseq(x) where f is Eltseq(y)>;
  addS := func<x,y | <x[1]+y[1], x[2]+y[2]+andF(x[1],y[1])>>;
  subS := func<x,y | <x[1]+y[1], x[2]+y[1]+y[2]+andF(x[1],y[1])>>;
  Fm := func<x | <x[1]^3, d(x[1])*x[2]>>;
  Gm := func<x | Fm(<Fm(x)[2], Fm(x)[1]>)>;
  al := <F!1, F!0>;
  cnt := AssociativeArray();
  for a in F do for b in F do
    x := <a,b>; df := subS(Gm(addS(x,al)), Gm(x));
    if IsDefined(cnt, df) then cnt[df] +:= 1; else cnt[df] := 1; end if;
  end for; end for;
  mx := Max([cnt[k] : k in Keys(cnt)]);
  printf "sigma m=%o q/2=%o row alpha=(1,0): max=%o\n", m, q div 2, mx;
  assert mx eq expv[m] and mx ge q div 2;
end for;
print "T6 SIGMA PASS";
quit;
