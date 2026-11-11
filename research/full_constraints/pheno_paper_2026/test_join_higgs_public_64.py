"""Tamper guards for 64-card real source-scoped Higgs constraint join."""
import json
import math
import tempfile
import unittest
from pathlib import Path
from research.full_constraints.pheno_paper_2026.join_higgs_public_64 import (
    load,keyed,finite,selected_max
)
class HiggstoolsJoinedGateTests(unittest.TestCase):
    def test_finite_and_selected_max_requires_complete_source(self):
        self.assertAlmostEqual(selected_max({"H":{"observed_ratio":.02},
                                              "A":{"observed_ratio":.2}},"observed_ratio"),.2)
        for bad in ({},{"H":{"observed_ratio":float("nan")}},
                    {"H":{"observed_ratio":None}}):
            with self.assertRaises((ValueError,TypeError)):
                selected_max(bad,"observed_ratio")
        for bad in (float("nan"),float("inf"),None,"0.3"):
            with self.assertRaises(ValueError):
                finite(bad,"test")
    def test_exact_card_identity_and_overlap_rejection(self):
        rows=[{"scalar_id":i,"ordering":j,"seed":k}
              for i in range(16) for j in ("NO","IO") for k in (20261111,20261112)]
        self.assertEqual(len(keyed(rows,"synthetic")),64)
        rows[-1]=dict(rows[0])
        with self.assertRaises(ValueError):keyed(rows,"tampered")
    def test_incomplete_or_accepted_input_fails(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/"x.json"
            payload={"n_h125_cases":64,"global_acceptance":None,"cases":[{}]*64}
            f.write_text(json.dumps(payload))
            x,sha=load(f,64,"n_h125_cases")
            self.assertEqual(len(x["cases"]),64)
            self.assertEqual(len(sha),64)
            payload["global_acceptance"]=True;f.write_text(json.dumps(payload))
            with self.assertRaises(ValueError):load(f,64,"n_h125_cases")
            payload["global_acceptance"]=None;payload["cases"].pop();f.write_text(json.dumps(payload))
            with self.assertRaises(ValueError):load(f,64,"n_h125_cases")
if __name__=="__main__": unittest.main()
