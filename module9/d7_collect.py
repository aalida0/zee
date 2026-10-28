"""Fail-closed D7 aggregation; CERN completion requires actual Condor history.

Without --condor-history every aggregate is explicitly LOCAL_SIMULATION.
Hashes establish consistency, not independent authentication of execution.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re

from module2.interface import canonical_hash, strict_loads, finite_json
from module9.d7_inputs import SEED_SHA256, seed_input, validate_point, VARIED
from module9.d7_prepare import design, make_point, ANCESTOR, SEED, STATUS as PREPARE_STATUS
from module9.d7_worker import STATUS as WORKER_STATUS, SCALAR_GATES

STATUS = "D7_BATCH_PILOT_AGGREGATE_ONLY"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def number(value):
    return type(value) in (int, float) and math.isfinite(value) and value >= 0


def validate_manifest(manifest):
    finite_json(manifest)
    require(isinstance(manifest, dict), "Unknown D7 manifest")
    for key, value in {"schema_version":"d7-pilot-1.0.0", "total_points":32,
                       "shard_count":4, "point_count_per_shard":8,
                       "source_ordering":"NO", "ancestor_commit":ANCESTOR,
                       "status":PREPARE_STATUS, "nufit_likelihood":"NOT_EVALUATED",
                       "deterministic_seed":SEED, "source_bytes_sha256":SEED_SHA256,
                       "constraints_complete":False, "global_zee_acceptance":None}.items():
        require(key in manifest and type(manifest[key]) is type(value) and manifest[key] == value,
                "Invalid manifest " + key)
    require(len(manifest["points"]) == 32 and len(manifest["shards"]) == 4,
            "Wrong manifest cardinality")
    expected = {}
    for spec, entry in zip(design(), manifest["points"]):
        identity, arm, physical = spec
        inp = make_point(seed_input(), identity, physical)
        require(entry == {"point_id":identity, "arm":arm, "input_sha256":canonical_hash(inp),
                          "scalar_sha256":inp["module2_input"]["scalar"]["sha256"],
                          "physical":inp["module2_input"]["scalar"]["record"]["physical"],
                          "ordering":"NO", "global_zee_acceptance":None},
                "Manifest differs from deterministic pinned NO design")
        expected[identity] = entry
    for key, pattern in (("execution_source_commit", r"[0-9a-f]{40}"),
                         ("source_bundle_sha256", r"[0-9a-f]{64}")):
        if key in manifest:
            require(isinstance(manifest[key], str) and re.fullmatch(pattern, manifest[key]),
                    "Invalid staged provenance " + key)
    require(("execution_source_commit" in manifest) == ("source_bundle_sha256" in manifest),
            "Partial staged provenance")
    return expected


def verify_staged_artifacts(manifest, folder):
    """Bind the retained submit-side scripts and source archive to the manifest."""
    if "execution_source_commit" not in manifest:
        return
    files = {"worker.sh", "d7_pilot.sub", "source_commit.txt", "bundle.sha256", "shards.txt"}
    require(set(manifest.get("staged_artifact_sha256", {})) == files, "Missing staged artifact inventory")
    for name, digest in manifest["staged_artifact_sha256"].items():
        require(hashlib.sha256((folder/name).read_bytes()).hexdigest() == digest,
                "Changed staged artifact " + name)
    require(hashlib.sha256((folder/"scan_bundle.tar.gz").read_bytes()).hexdigest() == manifest["source_bundle_sha256"],
            "Changed staged source archive")
    require((folder/"source_commit.txt").read_text().strip() == manifest["execution_source_commit"],
            "Changed staged commit")


def validate_row(row, original, expected):
    finite_json(row)
    require(isinstance(row, dict), "Malformed result row")
    require(row.get("point_id") == original["point_id"] and
            row.get("input_sha256") == original["input_sha256"], "Input/output point mismatch")
    require("global_zee_acceptance" in row and row["global_zee_acceptance"] is None and
            row.get("constraints_complete") is False, "Illegal viability/completeness claim")
    require(number(row.get("elapsed_seconds")), "Invalid point runtime")
    if row.get("execution_status") == "EVALUATION_ERROR":
        require(row.get("scalar_status") == "UNKNOWN" and isinstance(row.get("error"), str)
                and isinstance(row.get("error_type"), str), "Malformed evaluation error")
        return
    require(row.get("execution_status") == "EVALUATED_SCOPED", "Unknown execution status")
    require(row.get("arm") == expected["arm"] and row.get("scalar_sha256") == expected["scalar_sha256"],
            "Scalar/arm provenance mismatch")
    require(row.get("physical") == {k: expected["physical"][k] for k in VARIED}, "Result scalar inputs changed")
    gates = row.get("gates", {})
    require(set(gates) == set(SCALAR_GATES), "Missing scalar gates")
    allowed = {
        "reconstruction":{"PASS":"RECONSTRUCTION_VALIDATED"},
        "bfb":{"PASS":"BFB_CERTIFIED_SUFFICIENT", "FAIL":"BFB_NEGATIVE_WITNESS", "UNKNOWN":"BFB_UNKNOWN"},
        "unitarity":{"PASS":"TREE_UNITARITY_PASS", "FAIL":"TREE_UNITARITY_FAIL"},
        "ewpo":{"PASS":"SCALAR_OBLIQUE_INSIDE_95", "FAIL":"SCALAR_OBLIQUE_OUTSIDE_95"}}
    for name, gate in gates.items():
        require(gate.get("assessment") in ("PASS","FAIL","UNKNOWN") and
                allowed[name].get(gate["assessment"]) == gate.get("status"), "Invalid gate result")
    passed = all(g["assessment"] == "PASS" for g in gates.values())
    require(row.get("scalar_status") == ("SCOPED_PASS" if passed else "SCOPED_FAIL_OR_UNKNOWN"),
            "Scalar gate/status mismatch")
    if passed:
        require(row.get("neutrino_status") == "INVERSE_TARGET_CLOSURE_PASS" and
                number(row.get("neutrino_inverse_relative_residual")) and
                row["neutrino_inverse_relative_residual"] <= 2e-9, "Missing/invalid NO closure")
    else:
        require(row.get("neutrino_status") == "NOT_EVALUATED" and
                row.get("neutrino_inverse_relative_residual") is None, "Unexpected neutrino claim")
    require(set(row.get("selected_STU", {})) == {"S","T","U"}, "Missing STU diagnostics")
    require(all(type(v) in (int, float) and math.isfinite(v) for v in row["selected_STU"].values()),
            "Invalid STU numbers")
    require(set(row.get("reconstruction_residuals", {})) == {
        "tadpole_max_over_v3","spectrum_max_relative_residual","mixing_max_residual_GeV2"},
        "Missing reconstruction diagnostics")
    require(all(number(v) for v in row["reconstruction_residuals"].values()) and
            number(row.get("ewpo_chi2")) and number(row.get("unitarity_max_abs_eigenvalue")),
            "Invalid scalar diagnostics")
    require(row.get("COMPLETE_LFV") is False and all(row.get(k) == "NOT_EVALUATED" for k in
            ("vacuum","physical_bsgamma","collider_rate")), "Illegal external constraint claim")


def collect(manifest, shards_folder, results_folder, receipts_folder, condor_history=None):
    expected = validate_manifest(manifest)
    shards_folder, results_folder, receipts_folder = map(Path, (shards_folder, results_folder, receipts_folder))
    batch = condor_history is not None
    history = {}
    if batch:
        require("execution_source_commit" in manifest, "CERN collection requires staged provenance")
        require(isinstance(condor_history, list) and len(condor_history) == 4, "Require four Condor history ads")
        for ad in condor_history:
            require(type(ad.get("ClusterId")) is int and type(ad.get("ProcId")) is int,
                    "Missing Condor job IDs")
            key = (str(ad["ClusterId"]), str(ad["ProcId"]))
            require(key not in history, "Duplicate Condor history job")
            history[key] = ad
        require(len({k[0] for k in history}) == 1 and {k[1] for k in history} == {"0","1","2","3"},
                "History must describe one four-job cluster")
    require({p.name for p in shards_folder.glob("*.jsonl")} == {f"part_{i:03d}.jsonl" for i in range(4)},
            "Unexpected shard files")
    require({p.name for p in results_folder.glob("*.jsonl")} <= {f"result_{i}.jsonl" for i in range(4)},
            "Unexpected result files")
    require({p.name for p in receipts_folder.glob("*.json")} <= {f"receipt_{i}.json" for i in range(4)},
            "Unexpected receipt files")
    output, missing, infra, job_errors, jobs = [], [], [], [], []
    seen_inputs = set()
    for idx, item in enumerate(manifest["shards"]):
        name = f"part_{idx:03d}.jsonl"
        require(item.get("name") == name and type(item.get("points")) is int and item["points"] == 8,
                "Invalid shard inventory")
        shard = shards_folder / name
        raw_input = shard.read_bytes()
        require(hashlib.sha256(raw_input).hexdigest() == item["sha256"], "Changed original shard " + name)
        shard_in = [strict_loads(line) for line in raw_input.decode().splitlines()]
        require(len(shard_in) == 8, "Unexpected shard cardinality")
        require(raw_input == "".join(json.dumps(row, sort_keys=True, allow_nan=False)+"\n" for row in shard_in).encode(),
                "Shard differs from canonical generated bytes")
        for offset, original in enumerate(shard_in):
            require(set(original) == {"point_id","arm","input_sha256","input"}, "Malformed input row")
            pid = original["point_id"]
            require(pid in expected and pid not in seen_inputs, "Duplicate/unknown input")
            require(pid == manifest["points"][idx*8+offset]["point_id"], "Wrong shard membership/order")
            seen_inputs.add(pid)
            validate_point(original["input"])
            require(original["arm"] == expected[pid]["arm"] and
                    canonical_hash(original["input"]) == original["input_sha256"] == expected[pid]["input_sha256"],
                    "Stale input or manifest SHA")
        out_path = results_folder / f"result_{idx}.jsonl"
        rec_path = receipts_folder / f"receipt_{idx}.json"
        if not out_path.is_file() or not rec_path.is_file():
            missing.append(name)
            continue
        receipt = strict_loads(rec_path.read_text())
        raw = out_path.read_bytes()
        require(receipt.get("schema_version") == "d7-worker-1.0.0" and receipt.get("status") == WORKER_STATUS,
                "Unknown worker receipt")
        for dest, src in (("source_commit", "execution_source_commit"), ("source_bundle_sha256", "source_bundle_sha256")):
            if src in manifest:
                require(receipt.get(dest) == manifest[src], "Executing source differs from staged manifest")
        require(receipt.get("source_shard_sha256") == item["sha256"] and
                receipt.get("result_bytes_sha256") == hashlib.sha256(raw).hexdigest(), "Result/receipt hash mismatch")
        rows = [strict_loads(line) for line in raw.decode().splitlines()]
        require(len(rows) == 8, "Unexpected returned cardinality")
        for original, row in zip(shard_in, rows):
            validate_row(row, original, expected[original["point_id"]])
            if row["execution_status"] == "EVALUATION_ERROR":
                infra.append(row["point_id"])
        counts = {"input_count":8, "output_count":8,
                  "scoped_pass":sum(r["scalar_status"] == "SCOPED_PASS" for r in rows),
                  "scoped_fail_or_unknown":sum(r["scalar_status"] == "SCOPED_FAIL_OR_UNKNOWN" for r in rows),
                  "evaluation_error":sum(r["execution_status"] == "EVALUATION_ERROR" for r in rows)}
        counts["worker_exit_code"] = 2 if counts["evaluation_error"] else 0
        require(all(type(receipt.get(k)) is int and receipt[k] == v for k, v in counts.items()),
                "Worker receipt counters/exit status disagree with results")
        require(receipt.get("constraints_complete") is False and "global_zee_acceptance" in receipt
                and receipt["global_zee_acceptance"] is None, "Invalid receipt scope")
        for key in ("python_version","python_executable","execution_host","platform","machine",
                    "environment_cvmfs_selected","completed_utc"):
            require(isinstance(receipt.get(key), str) and receipt[key].strip(), "Missing runtime provenance " + key)
        require(number(receipt.get("elapsed_seconds")) and number(receipt.get("peak_rss_KiB")), "Missing runtime/resource usage")
        versions = receipt.get("library_versions", {})
        require(all(isinstance(versions.get(k), str) and versions[k] for k in ("numpy","scipy","jsonschema","mpmath")),
                "Missing library provenance")
        for key in ("python_executable_sha256", "environment_setup_sha256", "installed_distribution_inventory_sha256"):
            require(isinstance(receipt.get(key), str) and re.fullmatch(r"[0-9a-f]{64}", receipt[key]),
                    "Missing runtime hash " + key)
        if "environment_setup_sha256" in manifest:
            require(receipt["environment_setup_sha256"] == manifest["environment_setup_sha256"],
                    "Worker environment setup differs from staged source")
        require(receipt.get("execution_mode") in ("LOCAL_SIMULATION","HTCONDOR"), "Unknown execution origin")
        if batch:
            key = (receipt.get("condor_cluster_id"), receipt.get("condor_proc_id"))
            require(receipt["execution_mode"] == "HTCONDOR" and key in history and key[1] == str(idx),
                    "Receipt/Condor history job identity mismatch")
            ad = history[key]
            require(isinstance(ad.get("Owner"), str) and ad["Owner"], "Missing billed Condor owner")
            require(isinstance(ad.get("RemoteHost"), str) and ad["RemoteHost"], "Missing Condor execution host")
            require(number(ad.get("RemoteWallClockTime")), "Missing Condor runtime")
            if (ad.get("JobStatus") != 4 or ad.get("ExitCode") != 0 or ad.get("ExitBySignal") is not False):
                job_errors.append(".".join(key))
            jobs.append({"receipt":receipt, "condor_history":ad})
        else:
            jobs.append({"receipt":receipt})
        output.extend(rows)
    require(len(seen_inputs) == 32 and len({r["point_id"] for r in output}) == len(output), "Incomplete/duplicate input inventory")
    if batch:
        require(len({a["Owner"] for a in history.values()}) == 1, "Mixed Condor owners")
    complete = not missing and not infra and not job_errors and len(output) == 32
    return {"schema_version":"d7-summary-1.0.0", "status":STATUS,
            "execution_mode":"HTCONDOR_WITH_HISTORY" if batch else "LOCAL_SIMULATION",
            "pilot_completion_status":"COMPLETE_SCOPED" if complete else "INCOMPLETE_OR_BLOCKED",
            "D7_BATCH_PILOT_COMPLETE":bool(batch and complete),
            "constraints_complete":False, "global_zee_acceptance":None,
            "execution_source_commit":manifest.get("execution_source_commit"),
            "source_bundle_sha256":manifest.get("source_bundle_sha256"),
            "point_count_expected":32, "point_count_collected":len(output),
            "missing_shards":missing, "evaluation_errors":infra, "condor_job_errors":job_errors,
            "scoped_scalar_pass":sum(r["scalar_status"] == "SCOPED_PASS" for r in output),
            "scoped_scalar_fail_or_unknown":sum(r["scalar_status"] == "SCOPED_FAIL_OR_UNKNOWN" for r in output),
            "inverse_neutrino_closure_pass":sum(r.get("neutrino_status") == "INVERSE_TARGET_CLOSURE_PASS" for r in output),
            "mass_minmax_GeV":{k:[min(p["physical"][k] for p in manifest["points"]), max(p["physical"][k] for p in manifest["points"])] for k in ("mH1","mH2")},
            "jobs":jobs, "scoped_rows":output,
            "cutflow_representativeness":"DEVELOPMENT_SUPPORT_ONLY_NO_GLOBAL_EFFICIENCY_INFERENCE",
            **{k:"NOT_EVALUATED" for k in ("full_LFV","nuFIT_joint_likelihood","global_vacuum","physical_bsgamma","collider_rates","rg_closure")}}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    for name in ("manifest","shards","results","receipts","output"):
        ap.add_argument("--" + name, type=Path, required=True)
    ap.add_argument("--condor-history", type=Path, help="JSON from condor_history CLUSTER -json; required to certify CERN completion")
    args = ap.parse_args()
    require(not args.output.exists(), "Refuse existing aggregate output")
    manifest = strict_loads(args.manifest.read_text())
    validate_manifest(manifest)
    verify_staged_artifacts(manifest, args.manifest.parent)
    report = collect(manifest, args.shards, args.results, args.receipts,
                     strict_loads(args.condor_history.read_text()) if args.condor_history else None)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as dst:
        dst.write(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(STATUS, report["execution_mode"], report["pilot_completion_status"], report["point_count_collected"])
    return 0 if report["pilot_completion_status"] == "COMPLETE_SCOPED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
