"""D7 dry-run, genuine one-point worker, and aggregate fail-closed tests.

Tests do not certify a CERN batch execution or a physically viable point.
"""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from module2.interface import canonical_hash
from module9.d7_prepare import prepare,design,make_point,TOTAL,SHARDS
from module9.d7_worker import run
from module9.d7_collect import collect

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

    def test_collector_completeness_and_tamper(self):
        with tempfile.TemporaryDirectory() as f:
            p=Path(f);m=prepare(SEED.read_bytes(),p/"input")
            results=p/"results";receipts=p/"status"
            results.mkdir();receipts.mkdir()
            first=m["shards"][0]
            rows=[json.loads(line) for line in (p/"input"/"shards"/first["name"]).read_text().splitlines()]
            processed=[{"point_id":x["point_id"],"input_sha256":x["input_sha256"],
                        "execution_status":"EVALUATED_SCOPED","scalar_status":"SCOPED_FAIL_OR_UNKNOWN",
                        "global_zee_acceptance":None} for x in rows]
            raw="".join(json.dumps(x)+"\n" for x in processed).encode()
            (results/"result_0.jsonl").write_bytes(raw)
            (receipts/"receipt_0.json").write_text(json.dumps({
                "source_shard_sha256":first["sha256"],"result_bytes_sha256":hashlib.sha256(raw).hexdigest(),
                "input_count":8,"output_count":8
            }))
            x=collect(m,p/"input"/"shards",results,receipts)
            self.assertEqual(x["point_count_collected"],8)
            self.assertEqual(len(x["missing_shards"]),3)
            self.assertEqual(x["pilot_completion_status"],"INCOMPLETE_OR_BLOCKED")
            (results/"result_0.jsonl").write_bytes(raw+b"\n")
            with self.assertRaises(ValueError):collect(m,p/"input"/"shards",results,receipts)

if __name__=="__main__":unittest.main()
