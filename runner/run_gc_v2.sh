#!/bin/bash
# r05 fail-closed runner for gc_ddt_v2 (r04 runner with the acceptance test moved to validate_run.py).
# usage: run_gc_v2.sh m cidx K [outroot]
#   Uses $GC_BIN (default ./gc_ddt_v2) and $GC_VAL (default validate_run.py next to this script). Creates a fresh
#   run directory, launches K shards, waits on every PID individually, records "k rc" for each, and accepts the run
#   only if validate_run.py accepts it: all K workers exit 0 with ids 0..K-1 once each; every shard's ndirs and
#   alphasum equal the deterministic loop alpha = k (mod K); nonempty shards have 1<=best<=N, 1<=alpha<N,
#   0<=beta<N, alpha%K=k; empty shards carry exactly the sentinel best=0 alpha=-1 beta=-1.
#   On success prints "MAX ..." and exits 0; otherwise prints "FAIL ..." and exits 1. Never prints MAX on failure.
set -u
if [ $# -lt 3 ] || [ $# -gt 4 ]; then echo "FAIL usage: run_gc_v2.sh m cidx K [outroot]" >&2; exit 1; fi
m=$1; c=$2; K=$3; root=${4:-runs}
for v in "$m" "$c" "$K"; do case "$v" in ''|*[!0-9]*) echo "FAIL non-integer argument: $v" >&2; exit 1;; esac; done
if [ "$K" -lt 1 ]; then echo "FAIL K must be >= 1" >&2; exit 1; fi
BIN=${GC_BIN:-./gc_ddt_v2}; SRC=${GC_SRC:-gc_ddt_v2.c}
VAL=${GC_VAL:-$(cd "$(dirname "$0")" && pwd)/validate_run.py}
[ -x "$BIN" ] || { echo "FAIL binary not found: $BIN" >&2; exit 1; }
[ -f "$VAL" ] || { echo "FAIL validator not found: $VAL" >&2; exit 1; }
mkdir -p "$root" || exit 1
dir=$(mktemp -d "$root/run_m${m}_c${c}_K${K}_$(date +%Y%m%dT%H%M%S)_XXXX") || { echo "FAIL mktemp" >&2; exit 1; }
{
  echo "date=$(date -u +%Y-%m-%dT%H:%M:%SZ)"; echo "host=$(hostname)"; echo "args=m=$m cidx=$c K=$K"
  echo "bin=$BIN"; echo "bin_sha256=$(shasum -a 256 "$BIN" | cut -d' ' -f1)"
  [ -f "$SRC" ] && echo "src_sha256=$(shasum -a 256 "$SRC" | cut -d' ' -f1)"
  echo "val_sha256=$(shasum -a 256 "$VAL" | cut -d' ' -f1)"
  echo "compiler=$(cc --version 2>/dev/null | head -1)"
} > "$dir/meta.txt"
pids=()
for k in $(seq 0 $((K-1))); do
  "$BIN" "$m" "$c" "$K" "$k" > "$dir/shard_$k.out" 2> "$dir/shard_$k.err" &
  pids+=($!)
done
fail=0
for k in $(seq 0 $((K-1))); do
  wait "${pids[$k]}"; rc=$?
  echo "$k $rc" >> "$dir/exit_codes.txt"
  [ "$rc" -ne 0 ] && fail=1
done
if [ "$fail" -ne 0 ]; then echo "FAIL nonzero exit in shard(s); see $dir/exit_codes.txt"; exit 1; fi
python3 "$VAL" "$dir" "$m" "$c" "$K" --write-summary
rc=$?
[ $rc -ne 0 ] && exit 1
exit 0
