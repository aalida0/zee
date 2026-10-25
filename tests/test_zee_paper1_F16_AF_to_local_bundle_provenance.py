#!/usr/bin/env python3
"""F16 separate provenance/security regression for AF->local scalar/Y/f inputs."""
from __future__ import annotations
import json,tempfile,unittest
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from zee_paper1_F16_verify_AF_to_local_bundle import (
    verify,sha,STATUS,FILES)
class TestTransfer(unittest.TestCase):
    def test_source_closure_and_tamper_rejection(self):
        with tempfile.TemporaryDirectory() as home:
            d=Path(home);model=d/"ZeeTypeII.m"
            model.write_text("(* synthetic SOURCE FOR HASH CLOSURE TEST ONLY *)\n")
            (d/FILES[0]).write_text("zeeF16Cases = {CASE1,CASE2,CASE3};\n")
            p={"full_model_madwidth_physical_totals":None,
               "complete_UFO_and_Ward_amplitudes_validated":False,
               "complex_Y_and_f_reconstructed_from_exact_F13":True}
            payload={key:dict(p) for key in ("A","B","C")}
            (d/FILES[1]).write_text(json.dumps(payload))
            report={
               "status":STATUS,
               "exact_F13_candidates":["A","B","C"],
               "all_three_local_SARAH_numeric_vertex_checks_passed":False,
               "actual_generated_complex_Zee_UFO_exists":False,
               "SARAH_ZeeTypeII_source_SHA256":sha(model),
               "numeric_fixture_SHA256":sha(d/FILES[0]),
               "source_reconstruction_SHA256":sha(d/FILES[1])}
            (d/"summary.json").write_text(json.dumps(report))
            manifest={
               "status":STATUS,
               "summary_SHA256":sha(d/"summary.json"),
               "fixture_SHA256":sha(d/FILES[0]),
               "all_three_local_SARAH_numeric_vertex_checks_passed":False}
            (d/"manifest.json").write_text(json.dumps(manifest))
            verify(d,model)
            (d/FILES[0]).write_text("MALICIOUS_OR_STALE_FIXTURE")
            with self.assertRaisesRegex(ValueError,"fixture"):
                verify(d,model)
            (d/FILES[0]).write_text("zeeF16Cases = {CASE1,CASE2,CASE3};\n")
            model.write_text("CHANGED_SOURCE")
            with self.assertRaisesRegex(ValueError,"SARAH"):
                verify(d,model)
if __name__=="__main__":unittest.main()
