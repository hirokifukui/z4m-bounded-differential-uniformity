#!/usr/bin/env python3
"""r05/r06: build TABLE_PROVENANCE.tsv, parameters.json and SHA256SUMS -- fail closed.

usage: python3 make_manifest.py <round dir> <studio runs dir>

Inputs read from <round dir>:
  expected_runs.tsv      lines "m cidx K" (the digit-formula runs the table relies on); '#' starts a comment
  excluded_runs.tsv      optional; lines "<run dir basename><TAB><reason>" for run dirs deliberately not used
  runner/validate_run.py the same validator used by run_gc_v2.sh
  runner/gc_ddt_v2.c     source whose SHA-256 must equal src_sha256 in every used run's meta.txt
  logs/magma_r04_t5_m1to5.log, logs/magma_r04_t5_m6.log   Magma ring-model logs (A9)
  expected_magma_ring.tsv  (r06) expected (log, m, f2, c) set of those logs; source logs/magma_r06_t1_expected.log

Fails (exit 1, writes nothing) if: an expected run has no run directory, or more than one not excluded;
a run directory is neither expected nor excluded; any expected run fails validate_run.validate (empty or short
exit_codes.txt, missing/duplicate worker ids, nonzero status, missing/malformed/disagreeing summary.json,
per-shard count/sum off the deterministic loop, invalid best/alpha/beta, missing shard); meta.txt lacks the
source hash or it differs; a Magma ring-model log deviates from expected_magma_ring.tsv (r06: last line
exactly 'T5 ALL PASS'; header field polynomial and #c; the (m, c) set with no missing, duplicate or extra
row; each c trace-one; 1 <= Delta <= 36; dirs = 4^m - 1; OK flag; maps/MAX summary recomputed; no
unrecognized line). All checks finish before any file is written.
Magma completion is judged by the assertion/PASS marker only: run_magma (detach) does not record the OS exit status.
SHA256SUMS never lists itself.
"""
import sys, os, re, json, glob, hashlib

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(here, "runner"))
import validate_run as V  # noqa: E402


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def die(msg):
    print(f"FAIL {msg}")
    sys.exit(1)


# ---- r06 T1: strict validation of the Magma ring-model logs -------------------------------------------
# Every non-empty line must be a header, a result row, the single summary line, or the exact final marker
# "T5 ALL PASS" (last line). The (m, f2, c) set must equal expected_magma_ring.tsv: no missing, duplicate or
# extra rows. Independently of that table, each c is re-checked to be trace-one in GF(2)[x]/(f2), each f2 to be
# irreducible of degree m, and for scope=complete the table itself must list every trace-one c.
MAGMA_HDR = re.compile(r"m=(\d+) f2=(.+) #c=(\d+)")
MAGMA_ROW = re.compile(r"m=(\d+) c=\[\s*([01](?:\s*,\s*[01])*)\s*\] Delta=(\d+) dirs=(\d+) (OK|FAIL)")
MAGMA_SUM = re.compile(r"maps=(\d+) MAX=(\d+)")
MAGMA_FINAL = "T5 ALL PASS"
DELTA_BOUND = 36  # the bound asserted by t5_ringmodel_v2.m


def f2_bits(text):
    bits = 0
    for t in text.replace(" ", "").split("+"):
        if t == "1":
            e = 0
        elif t == "$.1":
            e = 1
        elif re.fullmatch(r"\$\.1\^\d+", t):
            e = int(t[4:])
        else:
            die(f"unparsable field polynomial {text!r}")
        if bits >> e & 1:
            die(f"repeated term in field polynomial {text!r}")
        bits |= 1 << e
    return bits


def gf2_mulmod(x, y, poly, m):
    r = 0
    while y:
        if y & 1:
            r ^= x
        y >>= 1
        x <<= 1
        if x >> m & 1:
            x ^= poly
    return r


def gf2_irreducible(poly, m):
    # no factor of degree 1..m//2 (trial division over GF(2)[x])
    def pmod(a, b):
        db = b.bit_length() - 1
        while a and a.bit_length() - 1 >= db:
            a ^= b << (a.bit_length() - 1 - db)
        return a
    for d in range(1, m // 2 + 1):
        for g in range(1 << d, 1 << (d + 1)):
            if pmod(poly, g) == 0:
                return False
    return True


def gf2_trace(c, poly, m):
    t, x = 0, c
    for _ in range(m):
        t ^= x
        x = gf2_mulmod(x, x, poly, m)
    if t not in (0, 1):
        die("trace computation left the prime field")
    return t


def eltseq_int(s):
    v = [int(z) for z in s.replace(" ", "").split(",")]
    return v, sum(b << i for i, b in enumerate(v))


def load_expected_magma(rd):
    p = os.path.join(rd, "expected_magma_ring.tsv")
    if not os.path.isfile(p):
        die("expected_magma_ring.tsv missing")
    dims, cs = {}, {}
    for l in open(p):
        l = l.split("#", 1)[0].rstrip("\n")
        if not l.strip():
            continue
        f = l.split("\t")
        if f[0] == "dim" and len(f) == 5:
            lg, m, poly, scope = f[1], int(f[2]), f[3], f[4]
            if (lg, m) in dims or scope not in ("complete", "fixed"):
                die(f"expected_magma_ring.tsv: bad/duplicate dim line {l!r}")
            bits = f2_bits(poly)
            if bits.bit_length() - 1 != m or not gf2_irreducible(bits, m):
                die(f"expected_magma_ring.tsv: m={m} f2={poly} is not irreducible of degree m")
            dims[(lg, m)] = (poly, bits, scope)
        elif f[0] == "c" and len(f) == 4:
            key = (f[1], int(f[2]))
            v, ci = eltseq_int(f[3])
            if len(v) != key[1]:
                die(f"expected_magma_ring.tsv: wrong length {l!r}")
            if ci in cs.setdefault(key, set()):
                die(f"expected_magma_ring.tsv: duplicate c {l!r}")
            cs[key].add(ci)
        else:
            die(f"expected_magma_ring.tsv: malformed line {l!r}")
    if set(cs) != set(dims) or not dims:
        die("expected_magma_ring.tsv: dim and c entries disagree")
    for (lg, m), (poly, bits, scope) in dims.items():
        tr1 = {c for c in range(2 ** m) if gf2_trace(c, bits, m) == 1}
        if len(tr1) != 2 ** (m - 1):
            die(f"expected_magma_ring.tsv: trace self-check failed at m={m}")
        if not cs[(lg, m)] <= tr1:
            die(f"expected_magma_ring.tsv: m={m} lists a c that is not trace-one")
        if scope == "complete" and cs[(lg, m)] != tr1:
            die(f"expected_magma_ring.tsv: m={m} scope=complete but the trace-one set is not fully listed")
    return dims, cs


def validate_magma_log(rd, lg, dims, cs):
    p = os.path.join(rd, "logs", lg)
    if not os.path.isfile(p):
        die(f"{lg} missing")
    exp_m = sorted(m for (l, m) in dims if l == lg)
    if not exp_m:
        die(f"{lg}: no expectation in expected_magma_ring.tsv")
    lines = [l.strip() for l in open(p) if l.strip()]
    if not lines or lines[-1] != MAGMA_FINAL:
        die(f"{lg}: last line is not exactly {MAGMA_FINAL!r}")
    if sum(1 for l in lines if l == MAGMA_FINAL) != 1:
        die(f"{lg}: final marker repeated")
    headers, cur, summary, out = [], None, None, []
    seen = set()
    for i, l in enumerate(lines[:-1]):
        h, r, s = MAGMA_HDR.fullmatch(l), MAGMA_ROW.fullmatch(l), MAGMA_SUM.fullmatch(l)
        if summary is not None:
            die(f"{lg}: line after the maps/MAX summary: {l!r}")
        if h:
            m = int(h.group(1))
            if m in headers:
                die(f"{lg}: duplicate header m={m}")
            if headers and m <= headers[-1]:
                die(f"{lg}: headers out of order at m={m}")
            if (lg, m) not in dims:
                die(f"{lg}: unexpected dimension m={m}")
            if h.group(2) != dims[(lg, m)][0]:
                die(f"{lg}: m={m} field polynomial {h.group(2)!r} != expected {dims[(lg, m)][0]!r}")
            if int(h.group(3)) != len(cs[(lg, m)]):
                die(f"{lg}: m={m} header #c={h.group(3)} != expected {len(cs[(lg, m)])}")
            if cur is not None and len([x for x in out if x[0] == cur]) != len(cs[(lg, cur)]):
                die(f"{lg}: m={cur} has {len([x for x in out if x[0] == cur])} rows, expected {len(cs[(lg, cur)])}")
            headers.append(m); cur = m
        elif r:
            m = int(r.group(1))
            if cur is None or m != cur:
                die(f"{lg}: row m={m} under header m={cur}")
            v, ci = eltseq_int(r.group(2))
            if len(v) != m:
                die(f"{lg}: m={m} c has length {len(v)}")
            if (m, ci) in seen:
                die(f"{lg}: duplicate row m={m} c={v}")
            if ci not in cs[(lg, m)]:
                die(f"{lg}: unexpected row m={m} c={v}")
            if gf2_trace(ci, dims[(lg, m)][1], m) != 1:
                die(f"{lg}: m={m} c={v} is not trace-one")
            D, dirs = int(r.group(3)), int(r.group(4))
            if not (1 <= D <= min(DELTA_BOUND, 4 ** m)):
                die(f"{lg}: m={m} c={v} Delta={D} out of range [1, {min(DELTA_BOUND, 4 ** m)}]")
            if dirs != 4 ** m - 1:
                die(f"{lg}: m={m} dirs={dirs} != {4 ** m - 1}")
            if r.group(5) != "OK":
                die(f"{lg}: m={m} c={v} flagged {r.group(5)}")
            seen.add((m, ci)); out.append((m, r.group(2).replace(" ", ""), D, dirs))
        elif s:
            summary = (int(s.group(1)), int(s.group(2)))
        else:
            die(f"{lg}: unrecognized line {i + 1}: {l!r}")
    if headers != exp_m:
        die(f"{lg}: headers {headers} != expected dimensions {exp_m}")
    for m in exp_m:
        got = {ci for (mm, ci) in seen if mm == m}
        if got != cs[(lg, m)]:
            die(f"{lg}: m={m} rows {len(got)} != expected {len(cs[(lg, m)])} (missing {len(cs[(lg, m)] - got)})")
    if summary is None:
        die(f"{lg}: maps/MAX summary missing")
    if summary != (len(out), max(x[2] for x in out)):
        die(f"{lg}: summary maps={summary[0]} MAX={summary[1]} != recomputed {len(out)}, {max(x[2] for x in out)}")
    return out
# ---------------------------------------------------------------------------------------------------------


def read_table(p, ncols, required):
    if not os.path.isfile(p):
        if required:
            die(f"{p} missing")
        return []
    out = []
    for l in open(p):
        l = l.split("#", 1)[0].rstrip("\n")
        if not l.strip():
            continue
        parts = l.split("\t") if ncols == 2 else l.split()
        if len(parts) != ncols:
            die(f"malformed line in {p}: {l!r}")
        out.append(parts)
    return out


def main():
    if len(sys.argv) != 3:
        die("usage: make_manifest.py <round dir> <studio runs dir>")
    rd, runs = sys.argv[1], sys.argv[2]
    expected = []
    for p in read_table(os.path.join(rd, "expected_runs.tsv"), 3, True):
        try:
            expected.append(tuple(int(x) for x in p))
        except ValueError:
            die(f"non-integer expected run {p}")
    if not expected or len(set(expected)) != len(expected):
        die("expected_runs.tsv empty or has duplicates")
    excluded = {b: r for b, r in read_table(os.path.join(rd, "excluded_runs.tsv"), 2, False)}
    for b, r in excluded.items():
        if not r.strip():
            die(f"exclusion of {b} has no reason")
    src = os.path.join(rd, "runner", "gc_ddt_v2.c")
    if not os.path.isfile(src):
        die("runner/gc_ddt_v2.c missing")
    src_hash = sha(src)

    alldirs = sorted(os.path.basename(d) for d in glob.glob(os.path.join(runs, "run_m*")) if os.path.isdir(d))
    used, rows = {}, []
    params = {"digit_formula_runs": [], "ring_model_runs": [], "excluded_runs": excluded,
              "notes": {"digit_runs": "C exit statuses recorded per worker in exit_codes.txt; validated by runner/validate_run.py",
                        "magma": "completion judged by final assertion/PASS marker; OS exit status not recorded by run_magma(detach)",
                        "scope": "consistency of well-formed recorded outputs with the deterministic partition; not a proof of program execution"}}
    for (m, ci, K) in expected:
        pref = f"run_m{m}_c{ci}_K{K}_"
        cands = [b for b in alldirs if b.startswith(pref) and b not in excluded]
        if len(cands) != 1:
            die(f"expected run m={m} cidx={ci} K={K}: {len(cands)} non-excluded run directories {cands}")
        b = cands[0]; used[b] = (m, ci, K); d = os.path.join(runs, b)
        try:
            s, shard_rows = V.validate(d, m, ci, K, write_summary=False)
        except V.Fail as e:
            die(f"{b}: {e}")
        mf = os.path.join(d, "meta.txt")
        if not os.path.isfile(mf):
            die(f"{b}: meta.txt missing")
        meta = open(mf).read().strip().splitlines()
        mh = [l.split("=", 1)[1] for l in meta if l.startswith("src_sha256=")]
        if mh != [src_hash]:
            die(f"{b}: meta src_sha256 {mh} != runner/gc_ddt_v2.c {src_hash}")
        shard_hash = hashlib.sha256(b"".join(open(os.path.join(d, f"shard_{k}.out"), "rb").read() for k in range(K))).hexdigest()
        rows.append([str(m), str(4 ** m), "digit formulas (gc_ddt_v2.c, run_gc_v2.sh)", "studio", s["poly"],
                     f"cidx={ci} c={s['c']} (integer bit vector, bit i = coeff of x^i)",
                     f"{s['ndirs']}/{s['N']-1} directions, {K} shards, all {K} worker exit statuses 0, per-shard count/sum checked",
                     str(s["Delta"]), f"alpha={s['alpha']} beta={s['beta']} (index a*q+b)", b, shard_hash[:16]])
        params["digit_formula_runs"].append(dict(m=m, cidx=ci, c=s["c"], poly=s["poly"], N=s["N"], directions=s["ndirs"],
                                                 shards=K, Delta=s["Delta"], alpha=s["alpha"], beta=s["beta"], run_dir=b,
                                                 meta=meta, shard_outputs_sha256=shard_hash))
    stray = [b for b in alldirs if b not in used and b not in excluded]
    if stray:
        die(f"run directories neither expected nor excluded: {stray}")
    missing_excl = [b for b in excluded if b not in alldirs]
    if missing_excl:
        die(f"excluded run directories not present: {missing_excl}")

    dims, cs = load_expected_magma(rd)
    for lg in sorted({l for (l, _) in dims}):
        p = os.path.join(rd, "logs", lg)
        for (m, cstr, D, dirs) in validate_magma_log(rd, lg, dims, cs):
            poly = dims[(lg, m)][0]
            c = "[ " + ", ".join(cstr.split(",")) + " ]"
            rows.append([str(m), str(4 ** m), "ring model Z4[X]/(f), ring addition only (t5_ringmodel_v2.m, Magma)", "A9",
                         poly.replace("$.1", "x"), f"c={c} (Eltseq in Magma's basis of GF(2)[x]/(f2))",
                         f"{dirs}/{4**m-1} directions; exact final marker 'T5 ALL PASS' (OS exit status not recorded); "
                         f"(m,c) set checked against expected_magma_ring.tsv", str(D), "-", lg, sha(p)[:16]])
            params["ring_model_runs"].append(dict(m=m, c_eltseq=c, field_poly=poly.replace("$.1", "x"), Delta=D,
                                                  directions=dirs, log=lg, completion="exact final marker; expected set matched"))
    params["notes"]["magma_expected"] = ("m<=5: every trace-one c (complete); m=6: the two c fixed by cmax=2 "
                                         "(the first two of Magma's enumeration), not all 32")

    hdr = ["m", "N", "method", "node", "field_poly", "c", "coverage", "Delta", "argmax", "source", "sha256_16"]
    with open(os.path.join(rd, "TABLE_PROVENANCE.tsv"), "w") as f:
        f.write("\t".join(hdr) + "\n")
        for r in rows:
            f.write("\t".join(r) + "\n")
    json.dump(params, open(os.path.join(rd, "parameters.json"), "w"), indent=1)
    out = []
    for root, _, files in os.walk(rd):
        for fn in sorted(files):
            p = os.path.join(root, fn); rel = os.path.relpath(p, rd)
            if rel == "SHA256SUMS" or fn.startswith("."):
                continue
            out.append((rel, sha(p)))
    with open(os.path.join(rd, "SHA256SUMS"), "w") as f:
        for rel, h in sorted(out):
            f.write(f"{h}  {rel}\n")
    print("OK rows", len(rows), "digit_runs", len(used), "excluded", len(excluded), "files", len(out))


if __name__ == "__main__":
    main()
