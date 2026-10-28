"""D7 dry-run, genuine one-point worker, and aggregate fail-closed tests.

Tests do not certify a CERN batch execution or a physically viable point.
"""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import os
import subprocess
import tarfile
from unittest import mock
from module2.interface import canonical_hash
from module9.d7_prepare import prepare,design,make_point,TOTAL,SHARDS
from module9.d7_worker import run
from module9.d7_collect import collect, verify_staged_artifacts

ROOT=Path(__file__).resolve().parents[1]
SEED=ROOT/"module3/example.json"

def source():
    return json.loads(SEED.read_text())

class D7PilotTests(unittest.TestCase):
    def test_heavy_mass_broad_design_deterministic(self):
        a=design();b=design()
        self.assertEqual(a,b)
        self.assertEqual(len(a),32)
        self.assertEqual(len(set(x[0] for x in a)),32)
        self.assertEqual(len([x for x in a if x[1]=="broad"]),16)
        self.assertTrue(all(v["mH2"]>v["mH1"]+91.1876 for _,_,v in a))
        self.assertGreater(max(v["mH1"] for _,_,v in a),900.)
        self.assertGreater(max(v["mH2"] for _,_,v in a),1400.)

    def test_sha_bound_generated_input_is_immutable_source(self):
        seed=source();before=copy.deepcopy(seed)
        identity,arm,param=design()[0]
        p=make_point(seed,identity,param)
        self.assertEqual(seed,before)
        self.assertEqual(p["benchmark_id"],p["module2_input"]["scalar"]["record"]["benchmark_id"])
        self.assertEqual(p["module2_input"]["scalar"]["sha256"],
                         canonical_hash(p["module2_input"]["scalar"]["record"]))
        self.assertEqual(p["module2_input"]["ordering"],"NO")
        self.assertEqual(p["module2_input"]["target_eV"],seed["module2_input"]["target_eV"])

    def test_real_pilot_preparation_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as f:
            folder=Path(f)/"run"
            m=prepare(SEED.read_bytes(),folder)
            self.assertEqual(m["total_points"],TOTAL)
            self.assertEqual(m["shard_count"],SHARDS)
            self.assertEqual([x["name"] for x in m["shards"]],
                             ["part_000.jsonl","part_001.jsonl","part_002.jsonl","part_003.jsonl"])
            for entry in m["shards"]:
                raw=(folder/"shards"/entry["name"]).read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(),entry["sha256"])
                self.assertEqual(len(raw.decode().splitlines()),8)
            with self.assertRaises(ValueError):prepare(SEED.read_bytes(),folder)

    def test_real_worker_on_source_NO_one_point(self):
        inp=source()
        row={"point_id":inp["benchmark_id"],"arm":"source_integration_oracle",
             "input_sha256":canonical_hash(inp),"input":inp}
        raw=(json.dumps(row,allow_nan=False)+"\n").encode()
        output,receipt=run(raw)
        self.assertEqual(receipt["input_count"],1)
        self.assertEqual(receipt["evaluation_error"],0)
        self.assertEqual(output[0]["execution_status"],"EVALUATED_SCOPED")
        self.assertEqual(output[0]["scalar_status"],"SCOPED_PASS")
        self.assertEqual(output[0]["neutrino_status"],"INVERSE_TARGET_CLOSURE_PASS")
        self.assertLess(output[0]["neutrino_inverse_relative_residual"],2e-9)
        self.assertIsNone(output[0]["global_zee_acceptance"])

    def test_stale_hash_and_id_fail_closed(self):
        inp=source()
        row={"point_id":inp["benchmark_id"],"arm":"source",
             "input_sha256":canonical_hash(inp),"input":inp}
        row["input"]["module2_input"]["scalar"]["record"]["physical"]["mH1"]=450.
        result,rec=run((json.dumps(row)+"\n").encode())
        self.assertEqual(rec["evaluation_error"],1)
        self.assertEqual(result[0]["execution_status"],"EVALUATION_ERROR")
        self.assertIsNone(result[0]["global_zee_acceptance"])

    def test_reject_rehashed_incompatible_inputs(self):
        for mutation in ("ordering", "dataset", "target", "family", "id2", "id1", "mass_order", "closed_cascade", "scalar_hash", "output", "nonfinite"):
            with self.subTest(mutation=mutation):
                inp=source(); mod=inp["module2_input"]; wrapper=mod["scalar"]
                if mutation == "ordering": mod["ordering"]="IO"
                if mutation == "dataset": mod["dataset"]={"ordering":"IO"}
                if mutation == "target": mod["target_eV"]["real"][0][0] += .1
                if mutation == "family": mod["homogeneous_coefficients"]["real"][0] += .1
                if mutation == "id2": mod["benchmark_id"]="other"
                if mutation == "id1": wrapper["record"]["benchmark_id"]="other"
                if mutation == "mass_order": wrapper["record"]["physical"]["mH1"]=800.
                if mutation == "closed_cascade": wrapper["record"]["physical"]["mH2"]=310.
                if mutation == "nonfinite": wrapper["record"]["physical"]["mH2"]=float("inf")
                if mutation == "output": inp["module2_output"]={}
                if mutation not in ("scalar_hash", "nonfinite"):
                    wrapper["sha256"]=canonical_hash(wrapper["record"])
                if mutation == "scalar_hash": wrapper["sha256"]="0"*64
                if mutation == "nonfinite":
                    with self.assertRaises(ValueError): run((json.dumps(inp)+"\n").encode())
                    continue
                row={"point_id":inp["benchmark_id"], "arm":"source", "input_sha256":canonical_hash(inp), "input":inp}
                rows, rec=run((json.dumps(row)+"\n").encode())
                self.assertEqual(rows[0]["execution_status"], "EVALUATION_ERROR")
                self.assertEqual(rec["worker_exit_code"], 2)

    def test_strict_json_and_duplicate_points(self):
        for raw in (b'{"point_id":"x","point_id":"y"}', b'{"x":NaN}', b'{"x":1e999}', b'', b'null'):
            with self.subTest(raw=raw), self.assertRaises(ValueError): run(raw)
        inp=source(); row={"point_id":inp["benchmark_id"],"arm":"source", "input_sha256":canonical_hash(inp),"input":inp}
        raw=(json.dumps(row)+"\n").encode()
        with self.assertRaises(ValueError): run(raw+raw)

    def test_nonfinite_computation_is_evaluation_error(self):
        inp=source(); row={"point_id":inp["benchmark_id"],"arm":"source", "input_sha256":canonical_hash(inp),"input":inp}
        with mock.patch("module9.d7_worker.evaluate_one", return_value={"bad":float("nan")}):
            rows, rec=run((json.dumps(row)+"\n").encode())
        self.assertEqual(rows[0]["execution_status"], "EVALUATION_ERROR")
        self.assertEqual(rec["evaluation_error"], 1)

    def test_prepare_rejects_changed_source(self):
        with tempfile.TemporaryDirectory() as f:
            for mutation in (lambda p:p["module2_input"].update(ordering="IO"),
                             lambda p:p["module2_input"].update(benchmark_id="wrong")):
                inp=source(); mutation(inp)
                with self.assertRaises(ValueError): prepare(json.dumps(inp).encode(), Path(f)/"bad")

    def test_worker_cli_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as f:
            p=Path(f); (p/"out").write_text("keep")
            proc=subprocess.run([os.sys.executable,"-m","module9.d7_worker", "--shard",str(SEED),
                                 "--output",str(p/"out"),"--receipt",str(p/"rec")],cwd=ROOT,capture_output=True)
            self.assertNotEqual(proc.returncode,0)
            self.assertEqual((p/"out").read_text(),"keep")


class D7CollectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory()
        cls.root=Path(cls.tmp.name)
        cls.manifest=prepare(SEED.read_bytes(), cls.root/"input")
        cls.fixture=[]
        for shard in cls.manifest["shards"]:
            raw=(cls.root/"input/shards"/shard["name"]).read_bytes()
            rows,receipt=run(raw)
            cls.fixture.append((rows,receipt))

    @classmethod
    def tearDownClass(cls): cls.tmp.cleanup()

    def setUp(self):
        self.case=tempfile.TemporaryDirectory(); self.p=Path(self.case.name)
        self.results=self.p/"results"; self.receipts=self.p/"status"
        self.results.mkdir(); self.receipts.mkdir()
        self.m=copy.deepcopy(self.manifest)
        for i,(rows,receipt) in enumerate(self.fixture): self.write(i,copy.deepcopy(rows),copy.deepcopy(receipt))

    def tearDown(self): self.case.cleanup()

    def write(self, i, rows, rec):
        raw="".join(json.dumps(row, allow_nan=False,sort_keys=True)+"\n" for row in rows).encode()
        rec["result_bytes_sha256"]=hashlib.sha256(raw).hexdigest()
        (self.results/f"result_{i}.jsonl").write_bytes(raw)
        (self.receipts/f"receipt_{i}.json").write_text(json.dumps(rec))

    def collect(self, history=None):
        return collect(self.m,self.root/"input/shards",self.results,self.receipts,history)

    def batch_fixture(self):
        self.m.update(execution_source_commit="a"*40,source_bundle_sha256="b"*64)
        ads=[]
        for i,(rows,rec) in enumerate(self.fixture):
            rec=copy.deepcopy(rec)
            rec.update(source_commit="a"*40,source_bundle_sha256="b"*64,
                       execution_mode="HTCONDOR",condor_cluster_id="123",condor_proc_id=str(i))
            self.write(i, rows,rec)
            ads.append(dict(ClusterId=123,ProcId=i,Owner="test_fixture_only",RemoteHost="slot1@test",
                            RemoteWallClockTime=1.,JobStatus=4,ExitCode=0,ExitBySignal=False))
        return ads

    def test_real_all_shards_explicit_local(self):
        x=self.collect()
        self.assertEqual(x["point_count_collected"],32)
        self.assertEqual(x["pilot_completion_status"],"COMPLETE_SCOPED")
        self.assertEqual(x["execution_mode"],"LOCAL_SIMULATION")
        self.assertFalse(x["D7_BATCH_PILOT_COMPLETE"])
        self.assertEqual(x["evaluation_errors"],[])
        self.assertEqual(x["scoped_scalar_pass"]+x["scoped_scalar_fail_or_unknown"],32)

    def test_missing_job_is_incomplete(self):
        (self.receipts/"receipt_3.json").unlink()
        x=self.collect()
        self.assertEqual(x["point_count_collected"],24)
        self.assertEqual(x["missing_shards"],["part_003.jsonl"])
        self.assertFalse(x["D7_BATCH_PILOT_COMPLETE"])
        self.assertEqual(x["pilot_completion_status"],"INCOMPLETE_OR_BLOCKED")

    def test_tamper_result_bytes(self):
        p=self.results/"result_0.jsonl";p.write_bytes(p.read_bytes()+b"\n")
        with self.assertRaises(ValueError):self.collect()

    def test_tamper_manifest(self):
        for key,value in (("shards",self.m["shards"][:3]),("points",self.m["points"][:31]),
                          ("shard_count",True),("source_bytes_sha256","0"*64)):
            with self.subTest(key=key):
                self.m=copy.deepcopy(self.manifest);self.m[key]=value
                with self.assertRaises(ValueError):self.collect()

    def test_rehashed_semantic_tamper(self):
        for mutation in ("unknown_status","false_pass","global","constraints","wrong_point","wrong_input","negative_runtime","neutrino","gate","physical","receipt_count","receipt_exit","receipt_library"):
            with self.subTest(mutation=mutation):
                rows,rec=copy.deepcopy(self.fixture[0]);r=rows[0]
                if mutation == "unknown_status":r["scalar_status"]="UNKNOWN"
                if mutation == "false_pass":r["scalar_status"]="SCOPED_PASS"
                if mutation == "global":r["global_zee_acceptance"]=True
                if mutation == "constraints":r["constraints_complete"]=True
                if mutation == "wrong_point":r["point_id"]="other"
                if mutation == "wrong_input":r["input_sha256"]="0"*64
                if mutation == "negative_runtime":r["elapsed_seconds"]=-1
                if mutation == "neutrino":r["neutrino_status"]="INVERSE_TARGET_CLOSURE_PASS"
                if mutation == "gate":r["gates"]["ewpo"]["status"]="invented"
                if mutation == "physical":r["physical"]["mH2"]+=1
                if mutation == "receipt_count":rec["scoped_pass"]+=1
                if mutation == "receipt_exit":rec["worker_exit_code"]=1
                if mutation == "receipt_library":del rec["library_versions"]["scipy"]
                self.write(0,rows,rec)
                with self.assertRaises(ValueError):self.collect()

    def test_evaluation_error_is_incomplete_not_exclusion(self):
        rows,rec=copy.deepcopy(self.fixture[0]);old=rows[0]
        rows[0]={k:old[k] for k in ("point_id","input_sha256","elapsed_seconds","constraints_complete","global_zee_acceptance")}
        rows[0].update(execution_status="EVALUATION_ERROR",scalar_status="UNKNOWN",error_type="ValueError",error="fixture")
        rec["scoped_fail_or_unknown"]-=1;rec["evaluation_error"]+=1;rec["worker_exit_code"]=2
        self.write(0,rows,rec)
        x=self.collect()
        self.assertEqual(x["pilot_completion_status"],"INCOMPLETE_OR_BLOCKED")
        self.assertEqual(len(x["evaluation_errors"]),1)
        self.assertEqual(x["scoped_scalar_fail_or_unknown"],
                         sum(rec["scoped_fail_or_unknown"] for _,rec in self.fixture)-1)

    def test_condor_history_contract_fixture_only(self):
        ads=self.batch_fixture();x=self.collect(ads)
        self.assertTrue(x["D7_BATCH_PILOT_COMPLETE"])
        ads[0]["ExitCode"]=2;x=self.collect(ads)
        self.assertFalse(x["D7_BATCH_PILOT_COMPLETE"])
        self.assertEqual(x["condor_job_errors"],["123.0"])

    def test_condor_history_missing_or_mismatched(self):
        ads=self.batch_fixture()
        for bad in (ads[:3],ads+[ads[0]], [{**a,"ClusterId":999} for a in ads],
                    [{**a,"ProcId":0} for a in ads], [{k:v for k,v in a.items() if k!="RemoteHost"} for a in ads]):
            with self.subTest(bad=bad), self.assertRaises(ValueError):self.collect(bad)

    def test_staged_origin_mismatch(self):
        ads=self.batch_fixture();self.m["execution_source_commit"]="c"*40
        with self.assertRaises(ValueError):self.collect(ads)
        self.m["execution_source_commit"]="a"*40;self.m["source_bundle_sha256"]="d"*64
        with self.assertRaises(ValueError):self.collect(ads)

    def test_duplicate_and_extra_results(self):
        rows,rec=copy.deepcopy(self.fixture[0]);rows[1]=copy.deepcopy(rows[0])
        self.write(0,rows,rec)
        with self.assertRaises(ValueError):self.collect()
        self.write(0,*copy.deepcopy(self.fixture[0]))
        (self.results/"result_4.jsonl").write_text("extra")
        with self.assertRaises(ValueError):self.collect()

    def test_modified_shard_and_cross_shard_duplicate(self):
        with tempfile.TemporaryDirectory() as f:
            p=Path(f);m=prepare(SEED.read_bytes(),p/"input")
            path=p/"input/shards/part_000.jsonl";raw=path.read_bytes()
            path.write_bytes(raw+b"\n")
            with self.assertRaises(ValueError):collect(m,p/"input/shards",self.results,self.receipts)
            path.write_bytes(raw)
            m["shards"][1]["name"]="part_000.jsonl"
            with self.assertRaises(ValueError):collect(m,p/"input/shards",self.results,self.receipts)

    def test_staged_artifact_tamper(self):
        with tempfile.TemporaryDirectory() as f:
            p=Path(f);files=("worker.sh","d7_pilot.sub","source_commit.txt","bundle.sha256","shards.txt")
            for name in files: (p/name).write_text("a"*40 if name=="source_commit.txt" else "fixture")
            (p/"scan_bundle.tar.gz").write_bytes(b"archive fixture")
            m={"execution_source_commit":"a"*40,"source_bundle_sha256":hashlib.sha256(b"archive fixture").hexdigest(),
               "staged_artifact_sha256":{name:hashlib.sha256((p/name).read_bytes()).hexdigest() for name in files}}
            verify_staged_artifacts(m,p)
            (p/"worker.sh").write_text("changed")
            with self.assertRaises(ValueError):verify_staged_artifacts(m,p)


class D7WrapperTests(unittest.TestCase):
    def test_wrapper_rejects_bad_bundle_before_source_execution(self):
        with tempfile.TemporaryDirectory() as f:
            p=Path(f);(p/"part_000.jsonl").write_text("fixture")
            (p/"scan_bundle.tar.gz").write_bytes(b"not archive")
            (p/"bundle.sha256").write_text("0"*64+"  scan_bundle.tar.gz\n")
            (p/"source_commit.txt").write_text("a"*40+"\n")
            proc=subprocess.run(["bash",str(ROOT/"module9/condor/worker.sh"),"part_000.jsonl"],cwd=p,capture_output=True)
            self.assertNotEqual(proc.returncode,0)
            self.assertFalse((p/"source").exists())

    def test_wrapper_rejects_commit_mismatch_before_extraction(self):
        with tempfile.TemporaryDirectory() as f:
            p=Path(f);(p/"part_000.jsonl").write_text("fixture")
            with tarfile.open(p/"scan_bundle.tar.gz","w:gz",pax_headers={"comment":"b"*40}) as tf:
                info=tarfile.TarInfo("marker");info.size=0;tf.addfile(info)
            digest=hashlib.sha256((p/"scan_bundle.tar.gz").read_bytes()).hexdigest()
            (p/"bundle.sha256").write_text(digest+"  scan_bundle.tar.gz\n")
            (p/"source_commit.txt").write_text("a"*40+"\n")
            proc=subprocess.run(["bash",str(ROOT/"module9/condor/worker.sh"),"part_000.jsonl"],cwd=p,capture_output=True)
            self.assertNotEqual(proc.returncode,0)
            self.assertIn(b"D7_ARCHIVE_COMMIT_MISMATCH",proc.stderr)
            self.assertFalse((p/"source").exists())

    def test_wrapper_rejects_invalid_args(self):
        for args in ([],["../part_000.jsonl"],["part_000.jsonl","123"],["part_004.jsonl"], ["part_000.jsonl","123","4"]):
            proc=subprocess.run(["bash",str(ROOT/"module9/condor/worker.sh"),*args],cwd=ROOT,capture_output=True)
            self.assertEqual(proc.returncode,64)


if __name__=="__main__":unittest.main()
