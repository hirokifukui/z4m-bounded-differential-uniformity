#!/usr/bin/env python3
"""r05/r06 negative controls for make_manifest.py (aggregation stage).

usage: python3 test_manifest.py <round dir>
Copies the round's make_manifest.py, runner/, logs/, expected_runs.tsv and studio_runs/runs into a temporary
directory, runs one positive control and a set of injected faults on the copies only, and checks that every fault
is rejected (nonzero exit, line starting with FAIL, TABLE_PROVENANCE.tsv not written). The originals are untouched.
"""
import sys, os, shutil, subprocess, tempfile, json, glob, re

RD = os.path.abspath(sys.argv[1])


def fresh():
    t = tempfile.mkdtemp(prefix="mf_")
    for x in ["make_manifest.py", "expected_runs.tsv", "expected_magma_ring.tsv"]:
        shutil.copy(os.path.join(RD, x), t)
    for x in ["runner", "logs"]:
        shutil.copytree(os.path.join(RD, x), os.path.join(t, x))
    shutil.copytree(os.path.join(RD, "studio_runs", "runs"), os.path.join(t, "runs"))
    return t


def run(t):
    p = subprocess.run([sys.executable, os.path.join(t, "make_manifest.py"), t, os.path.join(t, "runs")],
                       capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr).strip()


def rd(t, pat):
    r = sorted(glob.glob(os.path.join(t, "runs", pat)))
    assert r, pat
    return r[0]


def edit(path, fn):
    s = open(path).read(); open(path, "w").write(fn(s))


def shard_edit(t, pat, k, fn):
    edit(os.path.join(rd(t, pat), f"shard_{k}.out"), fn)


def kv_add(line, key, d):
    return re.sub(rf"\b{key}=(-?\d+)", lambda mo: f"{key}={int(mo.group(1))+d}", line)


faults = {
    "empty_exit_codes": lambda t: open(os.path.join(rd(t, "run_m3_c0_*"), "exit_codes.txt"), "w").close(),
    "missing_summary": lambda t: os.remove(os.path.join(rd(t, "run_m3_c0_*"), "summary.json")),
    "malformed_summary": lambda t: open(os.path.join(rd(t, "run_m3_c0_*"), "summary.json"), "w").write("{not json"),
    "summary_status_not_pass": lambda t: edit(os.path.join(rd(t, "run_m3_c0_*"), "summary.json"), lambda s: s.replace('"PASS"', '"FAIL"')),
    "summary_delta_disagrees": lambda t: edit(os.path.join(rd(t, "run_m5_c0_*"), "summary.json"),
                                              lambda s: json.dumps(dict(json.loads(s), Delta=8))),
    "summary_ndirs_wrong": lambda t: edit(os.path.join(rd(t, "run_m2_c0_*"), "summary.json"),
                                          lambda s: json.dumps(dict(json.loads(s), ndirs=14))),
    "duplicate_worker_id": lambda t: edit(os.path.join(rd(t, "run_m3_c0_*"), "exit_codes.txt"), lambda s: s.replace("\n1 0\n", "\n0 0\n", 1)),
    "missing_worker_record": lambda t: edit(os.path.join(rd(t, "run_m3_c0_*"), "exit_codes.txt"), lambda s: "\n".join(s.splitlines()[:-1]) + "\n"),
    "nonzero_status": lambda t: edit(os.path.join(rd(t, "run_m4_c0_*"), "exit_codes.txt"), lambda s: s.replace("\n5 0\n", "\n5 3\n", 1)),
    "balanced_shard_counts": lambda t: (shard_edit(t, "run_m3_c0_*", 1, lambda s: kv_add(kv_add(s, "ndirs", 1), "alphasum", 1)),
                                        shard_edit(t, "run_m3_c0_*", 2, lambda s: kv_add(kv_add(s, "ndirs", -1), "alphasum", -1))),
    "invalid_best_nonempty": lambda t: shard_edit(t, "run_m3_c0_*", 1, lambda s: re.sub(r"best=\d+ alpha=\d+ beta=\d+", "best=0 alpha=-1 beta=-1", s)),
    "sentinel_tampered": lambda t: shard_edit(t, "run_m1_c0_*", 0, lambda s: s.replace("best=0 alpha=-1 beta=-1", "best=5 alpha=-1 beta=-1")),
    "missing_shard_file": lambda t: os.remove(os.path.join(rd(t, "run_m3_c0_*"), "shard_7.out")),
    "extra_shard_file": lambda t: shutil.copy(os.path.join(rd(t, "run_m3_c0_*"), "shard_7.out"), os.path.join(rd(t, "run_m3_c0_*"), "shard_20.out")),
    "expected_run_missing": lambda t: shutil.rmtree(rd(t, "run_m6_c0_*")),
    "stray_unexpected_run": lambda t: shutil.copytree(rd(t, "run_m3_c0_*"), os.path.join(t, "runs", "run_m3_c5_K20_X")),
    "second_candidate_same_key": lambda t: shutil.copytree(rd(t, "run_m3_c0_*"), rd(t, "run_m3_c0_*") + "_dup"),
    "meta_src_hash_mismatch": lambda t: edit(os.path.join(rd(t, "run_m7_c0_*"), "meta.txt"), lambda s: re.sub(r"src_sha256=\w+", "src_sha256=" + "0" * 64, s)),
    "magma_pass_marker_removed": lambda t: edit(os.path.join(t, "logs", "magma_r04_t5_m6.log"),
                                                lambda s: "\n".join(l for l in s.splitlines() if "PASS" not in l) + "\n"),
    "exclusion_without_reason": lambda t: open(os.path.join(t, "excluded_runs.tsv"), "w").write(os.path.basename(rd(t, "run_m3_c0_*")) + "\t \n"),
}

L5, L6 = "magma_r04_t5_m1to5.log", "magma_r04_t5_m6.log"


def lg_edit(t, lg, fn):
    edit(os.path.join(t, "logs", lg), fn)


def drop_first(pat):
    def f(s):
        out, done = [], False
        for l in s.splitlines():
            if not done and re.match(pat, l):
                done = True; continue
            out.append(l)
        return "\n".join(out) + "\n"
    return f


def dup_first(pat):
    def f(s):
        out, done = [], False
        for l in s.splitlines():
            out.append(l)
            if not done and re.match(pat, l):
                out.append(l); done = True
        return "\n".join(out) + "\n"
    return f


# r06 T1: Magma ring-model log faults (GPT R05 review M1 cases first, then further cases)
faults.update({
    "magma_m5_header_and_rows_removed": lambda t: lg_edit(t, L5, lambda s: "\n".join(l for l in s.splitlines() if not l.startswith("m=5")) + "\n"),
    "magma_m5_one_row_removed": lambda t: lg_edit(t, L5, drop_first(r"m=5 c=")),
    "magma_not_pass_marker": lambda t: lg_edit(t, L5, lambda s: s.replace("T5 ALL PASS", "T5 NOT PASS")),
    "magma_m6_row_duplicated": lambda t: lg_edit(t, L6, dup_first(r"m=6 c=")),
    "magma_delta_9999": lambda t: lg_edit(t, L6, lambda s: s.replace("Delta=9 ", "Delta=9999 ", 1)),
    "magma_delta_37": lambda t: lg_edit(t, L5, lambda s: s.replace("Delta=10 ", "Delta=37 ", 1)),
    "magma_wrong_field_poly": lambda t: lg_edit(t, L5, lambda s: s.replace("m=4 f2=$.1^4 + $.1 + 1", "m=4 f2=$.1^4 + $.1^3 + 1", 1)),
    "magma_extra_trace_one_row": lambda t: lg_edit(t, L6, lambda s: s.replace("maps=2 MAX=9", "m=6 c=[ 0, 1, 0, 1, 0, 0 ] Delta=9 dirs=4095 OK\nmaps=3 MAX=9")),
    "magma_row_c_not_trace_one": lambda t: lg_edit(t, L6, lambda s: s.replace("c=[ 1, 0, 0, 1, 0, 0 ]", "c=[ 1, 0, 0, 0, 0, 0 ]")),
    "magma_dirs_wrong": lambda t: lg_edit(t, L5, lambda s: s.replace("dirs=1023 OK", "dirs=1022 OK", 1)),
    "magma_row_flag_fail": lambda t: lg_edit(t, L5, lambda s: s.replace("dirs=63 OK", "dirs=63 FAIL", 1)),
    "magma_summary_mismatch": lambda t: lg_edit(t, L5, lambda s: s.replace("maps=31 MAX=10", "maps=30 MAX=10")),
    "magma_unrecognized_line": lambda t: lg_edit(t, L6, lambda s: s.replace("maps=2", "warning: something\nmaps=2")),
    "expected_table_truncated": lambda t: edit(os.path.join(t, "expected_magma_ring.tsv"), drop_first(r"c\tmagma_r04_t5_m1to5.log\t5\t")),
})

results = []
t = fresh(); rc, out = run(t)
ok = rc == 0 and out.splitlines()[-1].startswith("OK")
results.append(("positive_baseline", "ok", rc, out.splitlines()[-1], ok))
shutil.rmtree(t)
for name, f in faults.items():
    t = fresh(); f(t)
    rc, out = run(t)
    last = out.splitlines()[-1] if out else ""
    ok = rc != 0 and last.startswith("FAIL") and not os.path.exists(os.path.join(t, "TABLE_PROVENANCE.tsv"))
    results.append((name, "fail", rc, last, ok))
    shutil.rmtree(t)
bad = 0
for name, want, rc, last, ok in results:
    print(f"{'OK ' if ok else 'BAD'}  {name} want={want} rc={rc} :: {last}")
    bad += not ok
print(f"SUMMARY pass={len(results)-bad} bad={bad}")
sys.exit(1 if bad else 0)
