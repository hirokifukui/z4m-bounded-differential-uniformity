#!/usr/bin/env python3
"""r05: fail-closed validator for one run directory of gc_ddt_v2 (used by run_gc_v2.sh and make_manifest.py).

usage: validate_run.py <run_dir> <m> <cidx> <K> [--write-summary]
Exit 0 and print "MAX ..." only if ALL of the following hold; otherwise print "FAIL ..." and exit 1.
  * exit_codes.txt exists, has exactly K lines "k rc", worker ids are exactly {0..K-1} each once, every rc == 0;
  * shard_k.out exists for each k in 0..K-1 and no other shard_*.out exists; each holds exactly one "SHARD" line;
  * every shard line has m, cidx, K, k equal to the expected values (k = its file index) and perm=1;
  * c and poly are identical across shards;
  * per shard: ndirs and alphasum equal the values of the deterministic loop
        alpha in {k, k+K, k+2K, ...} intersect [1, N-1];
  * per nonempty shard: 1 <= best <= N, 1 <= alpha < N, 0 <= beta < N, alpha % K == k;
    per empty shard (ndirs == 0 by the loop): exactly the documented sentinel best=0 alpha=-1 beta=-1;
  * totals: ndirs = N-1, alphasum = N(N-1)/2 (implied by the per-shard checks, checked again).
With --write-summary the summary.json is (re)written; without it an existing summary.json must agree with the
recomputed values (status PASS, m, cidx, c, poly, K, N, ndirs, Delta, alpha, beta, shards).
This checks that the recorded outputs are well formed and mutually consistent with the deterministic partition;
it is not a proof that an arbitrary program executed each direction.
"""
import sys, os, re, json, glob

SENTINEL = dict(best=0, alpha=-1, beta=-1)
KEYS = ["m", "poly", "cidx", "c", "K", "k", "ndirs", "alphasum", "best", "alpha", "beta", "perm"]


class Fail(Exception):
    pass


def expected_shard(N, K, k):
    al = list(range(k, N, K))
    al = [a for a in al if a != 0]
    return len(al), sum(al)


def parse_shard(path):
    try:
        lines = [l for l in open(path).read().splitlines() if l.strip()]
    except OSError as e:
        raise Fail(f"cannot read {path}: {e}")
    if len(lines) != 1 or not lines[0].startswith("SHARD "):
        raise Fail(f"malformed or empty shard output: {path}")
    toks = lines[0].split()[1:]
    kv = {}
    for t in toks:
        if "=" not in t:
            raise Fail(f"bad token {t!r} in {path}")
        a, b = t.split("=", 1)
        if a in kv:
            raise Fail(f"duplicate key {a} in {path}")
        kv[a] = b
    if sorted(kv) != sorted(KEYS):
        raise Fail(f"unexpected key set {sorted(kv)} in {path}")
    out = {}
    for key in KEYS:
        if key == "poly":
            if not re.fullmatch(r"0x[0-9A-F]+", kv[key]):
                raise Fail(f"bad poly {kv[key]!r} in {path}")
            out[key] = kv[key]
        else:
            if not re.fullmatch(r"-?[0-9]+", kv[key]):
                raise Fail(f"non-integer {key}={kv[key]!r} in {path}")
            out[key] = int(kv[key])
    return out


def validate(d, m, cidx, K, write_summary=False):
    if not (1 <= m <= 10) or K < 1 or cidx < 0:
        raise Fail(f"bad parameters m={m} cidx={cidx} K={K}")
    if not os.path.isdir(d):
        raise Fail(f"run directory missing: {d}")
    N = 4 ** m
    # exit codes
    ecf = os.path.join(d, "exit_codes.txt")
    if not os.path.isfile(ecf):
        raise Fail("exit_codes.txt missing")
    ec_lines = [l for l in open(ecf).read().splitlines() if l.strip()]
    if len(ec_lines) != K:
        raise Fail(f"exit_codes.txt has {len(ec_lines)} records, expected K={K}")
    ids, codes = [], []
    for l in ec_lines:
        p = l.split()
        if len(p) != 2 or not all(re.fullmatch(r"[0-9]+", x) for x in p):
            raise Fail(f"malformed exit-code record {l!r}")
        ids.append(int(p[0])); codes.append(int(p[1]))
    if sorted(ids) != list(range(K)):
        raise Fail(f"worker ids {sorted(ids)} != 0..{K-1} (missing/duplicate)")
    bad = [(i, c) for i, c in zip(ids, codes) if c != 0]
    if bad:
        raise Fail(f"nonzero exit status for workers {bad}")
    # shard files
    files = sorted(glob.glob(os.path.join(d, "shard_*.out")))
    want = {os.path.join(d, f"shard_{k}.out") for k in range(K)}
    if set(files) != want:
        raise Fail(f"shard file set mismatch: extra={sorted(set(files)-want)} missing={sorted(want-set(files))}")
    rows = []
    for k in range(K):
        r = parse_shard(os.path.join(d, f"shard_{k}.out"))
        if (r["m"], r["cidx"], r["K"], r["k"], r["perm"]) != (m, cidx, K, k, 1):
            raise Fail(f"shard {k}: parameters mismatch {r}")
        en, es = expected_shard(N, K, k)
        if r["ndirs"] != en or r["alphasum"] != es:
            raise Fail(f"shard {k}: ndirs/alphasum = {r['ndirs']}/{r['alphasum']}, deterministic loop gives {en}/{es}")
        if en == 0:
            if {x: r[x] for x in SENTINEL} != SENTINEL:
                raise Fail(f"shard {k}: empty shard must carry sentinel best=0 alpha=-1 beta=-1, got {r}")
        else:
            if not (1 <= r["best"] <= N and 1 <= r["alpha"] < N and 0 <= r["beta"] < N and r["alpha"] % K == k):
                raise Fail(f"shard {k}: invalid best/alpha/beta {r['best']}/{r['alpha']}/{r['beta']}")
        rows.append(r)
    if len({r["c"] for r in rows}) != 1 or len({r["poly"] for r in rows}) != 1:
        raise Fail("inconsistent c/poly across shards")
    nd = sum(r["ndirs"] for r in rows); asum = sum(r["alphasum"] for r in rows)
    if nd != N - 1 or asum != N * (N - 1) // 2:
        raise Fail(f"coverage: ndirs={nd} (want {N-1}), alphasum={asum} (want {N*(N-1)//2})")
    nonempty = [r for r in rows if r["ndirs"] > 0]
    b = max(nonempty, key=lambda r: (r["best"], -r["k"]))
    summ = dict(m=m, cidx=cidx, c=rows[0]["c"], poly=rows[0]["poly"], K=K, N=N, ndirs=nd,
                Delta=b["best"], alpha=b["alpha"], beta=b["beta"], shards=K, status="PASS")
    sj = os.path.join(d, "summary.json")
    if write_summary:
        json.dump(summ, open(sj, "w"), indent=1)
    else:
        if not os.path.isfile(sj):
            raise Fail("summary.json missing")
        try:
            old = json.load(open(sj))
        except Exception as e:
            raise Fail(f"summary.json malformed: {e}")
        for key in ["status", "m", "cidx", "c", "poly", "K", "N", "ndirs", "Delta", "shards"]:
            if old.get(key) != summ[key]:
                raise Fail(f"summary.json {key}={old.get(key)!r} disagrees with recomputed {summ[key]!r}")
        # argmax: any recorded (alpha,beta) must be the one of a shard attaining Delta
        if (old.get("alpha"), old.get("beta")) not in {(r["alpha"], r["beta"]) for r in nonempty if r["best"] == summ["Delta"]}:
            raise Fail("summary.json argmax is not attained by any shard")
        summ["alpha"], summ["beta"] = old["alpha"], old["beta"]
    return summ, rows


def main():
    a = sys.argv[1:]
    ws = "--write-summary" in a
    a = [x for x in a if x != "--write-summary"]
    if len(a) != 4:
        print("FAIL usage: validate_run.py <run_dir> <m> <cidx> <K> [--write-summary]"); sys.exit(1)
    try:
        d = a[0]; m, c, K = (int(x) for x in a[1:])
        s, _ = validate(d, m, c, K, ws)
    except (Fail, ValueError) as e:
        print(f"FAIL {e}"); sys.exit(1)
    print("MAX m=%d cidx=%d c=%d poly=%s Delta=%d alpha=%d beta=%d dirs=%d/%d shards=%d dir=%s" %
          (s["m"], s["cidx"], s["c"], s["poly"], s["Delta"], s["alpha"], s["beta"], s["ndirs"], s["N"] - 1, s["K"], d))


if __name__ == "__main__":
    main()
