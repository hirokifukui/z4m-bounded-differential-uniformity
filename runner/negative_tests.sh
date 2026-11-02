#!/bin/bash
# Negative controls for run_gc_v2.sh: 13 fault cases, 2 checks on shard summaries, and legitimate empty shards.
# Each fail case must end with exit 1 and no "MAX" line; ok cases must exit 0 with a MAX line.
set -u
R=./run_gc_v2.sh; T=$(mktemp -d negtest_XXXX); pass=0; failn=0
mkfake(){ printf '#!/bin/bash\n%s\n' "$2" > "$T/$1"; chmod +x "$T/$1"; }
mkfake all_fail 'exit 7'
mkfake one_fail '[ "$4" = 1 ] && exit 7; exec ./gc_ddt_v2 "$@"'
mkfake empty 'exit 0'
mkfake one_empty '[ "$4" = 0 ] && exit 0; exec ./gc_ddt_v2 "$@"'
mkfake missing '[ "$4" = 1 ] && { ./gc_ddt_v2 "$1" "$2" "$3" 0; exit $?; }; exec ./gc_ddt_v2 "$@"'
mkfake dup_line './gc_ddt_v2 "$@"; ./gc_ddt_v2 "$@"'
mkfake short_cov 'out=$(./gc_ddt_v2 "$@") || exit $?; echo "$out" | sed -E "s/ndirs=([0-9]+)/ndirs=0/"'
mkfake wrong_c 'out=$(./gc_ddt_v2 "$@") || exit $?; [ "$4" = 1 ] && out=$(echo "$out" | sed -E "s/ c=([0-9]+)/ c=999/"); echo "$out"'
# Shard summaries: invalid best on a nonempty shard; balanced +1/-1 change of ndirs/alphasum on two shards
mkfake invalid_best 'out=$(./gc_ddt_v2 "$@") || exit $?; echo "$out" | sed -E "s/best=[0-9]+ alpha=[0-9]+ beta=[0-9]+/best=0 alpha=-1 beta=-1/"'
mkfake balanced_cov 'out=$(./gc_ddt_v2 "$@") || exit $?; case "$4" in 1) d=1;; 2) d=-1;; *) d=0;; esac; echo "$out" | awk -v d=$d '"'"'{for(i=1;i<=NF;i++){split($i,a,"=");if(a[1]=="ndirs"||a[1]=="alphasum")$i=a[1]"="(a[2]+d)};print}'"'"''
mkfake alpha_wrong_class 'out=$(./gc_ddt_v2 "$@") || exit $?; [ "$4" = 1 ] && out=$(echo "$out" | sed -E "s/ alpha=([0-9]+) / alpha=2 /"); echo "$out"'
check(){ name=$1; want=$2; shift 2; out=$("$@" 2>&1); rc=$?
  hasmax=0; echo "$out" | grep -q '^MAX' && hasmax=1
  if { [ "$want" = fail ] && [ $rc -ne 0 ] && [ $hasmax -eq 0 ]; } || { [ "$want" = ok ] && [ $rc -eq 0 ] && [ $hasmax -eq 1 ]; }; then
    echo "OK   $name rc=$rc :: $(echo "$out" | tail -1)"; pass=$((pass+1))
  else echo "BAD  $name rc=$rc :: $(echo "$out" | tail -1)"; failn=$((failn+1)); fi; }
check positive_m3_K4      ok   $R 3 0 4 "$T/runs"
check positive_m1_K20_empty_shards ok $R 1 0 20 "$T/runs"
check all_shards_fail     fail env GC_BIN=$T/all_fail  $R 3 0 4 "$T/runs"
check one_shard_fail      fail env GC_BIN=$T/one_fail  $R 3 0 4 "$T/runs"
check K_zero              fail $R 3 0 0 "$T/runs"
check all_empty           fail env GC_BIN=$T/empty     $R 3 0 4 "$T/runs"
check one_empty           fail env GC_BIN=$T/one_empty $R 3 0 4 "$T/runs"
check missing_shard       fail env GC_BIN=$T/missing   $R 3 0 4 "$T/runs"
check duplicate_line      fail env GC_BIN=$T/dup_line  $R 3 0 4 "$T/runs"
check short_coverage      fail env GC_BIN=$T/short_cov $R 3 0 4 "$T/runs"
check inconsistent_c      fail env GC_BIN=$T/wrong_c   $R 3 0 4 "$T/runs"
check bad_cidx            fail $R 3 99 4 "$T/runs"
check bad_m               fail $R 11 0 4 "$T/runs"
check nonint_arg          fail $R 3 x 4 "$T/runs"
check invalid_best        fail env GC_BIN=$T/invalid_best $R 3 0 4 "$T/runs"
check balanced_wrong_coverage fail env GC_BIN=$T/balanced_cov $R 3 0 4 "$T/runs"
check alpha_wrong_residue fail env GC_BIN=$T/alpha_wrong_class $R 3 0 4 "$T/runs"
echo "SUMMARY pass=$pass bad=$failn"
[ $failn -eq 0 ]
