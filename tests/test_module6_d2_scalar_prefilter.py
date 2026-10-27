"""Structural D2 tests; actual scalar-screen physics must be run by Codex."""
import copy
import json
import math
from pathlib import Path
import unittest

from module2.interface import scalar_input,canonical_hash
from module6.d2_scalar_prefilter import neighborhood,candidate,prefilter,STATUS

ROOT=Path(__file__).resolve().parents[1]

def seed():
    return json.loads((ROOT/"module3/example.json").read_text())

class D2PrefilterTests(unittest.TestCase):
    def test_deterministic_finite_bounded_development_support(self):
        specs=neighborhood()
        self.assertGreater(len(specs),25)
        self.assertLessEqual(len(specs),64)
        self.assertEqual(specs[0],("source",{}))
        self.assertEqual(len({name for name,_ in specs}),len(specs))
        self.assertTrue(all(set(d)<=set(("mH1","mH2","mh2","ma","gamma"))
                            for _,d in specs))

    def test_sha_bound_scalar_coherence_and_nonmutation(self):
        src=seed();old=copy.deepcopy(src)
        point,p=candidate(src,"test_H1_plus10",{"mH1":10.0})
        self.assertEqual(src,old)
        self.assertEqual(point["benchmark_id"],point["module2_input"]["benchmark_id"])
        self.assertEqual(point["benchmark_id"],point["module2_input"]["scalar"]["record"]["benchmark_id"])
        self.assertEqual(point["module2_input"]["scalar"]["sha256"],
                         canonical_hash(point["module2_input"]["scalar"]["record"]))
        self.assertEqual(p["mH1"],310.)
        self.assertEqual(p["mH2"],700.)
        self.assertEqual(p["gamma"],1.089)
        scalar_input(point["module2_input"]["scalar"])

    def test_unchanged_inputs_rejected_if_tampered(self):
        data=seed()
        data["module2_input"]["scalar"]["record"]["physical"]["mH1"]=450.
        with self.assertRaises(ValueError):candidate(data,"bad",{})
        for bad in ({"mH1":float("nan")},{"mH1":True},{"unrecognized":15}):
            with self.assertRaises(ValueError):candidate(seed(),"bad",bad)

    def test_real_source_neighborhood_still_unknown_vacuum(self):
        report=prefilter(seed())
        self.assertEqual(report["status"],STATUS)
        self.assertFalse(report["constraints_complete"])
        self.assertIsNone(report["global_zee_acceptance"])
        self.assertEqual(report["point_count"],len(neighborhood()))
        self.assertEqual(report["points"][0]["status"],"PASSES_SCOPED_TREE_AND_EWPO")
        self.assertGreaterEqual(report["scoped_pass_count"],1)
        for row in report["points"]:
            self.assertEqual(row["vacuum"],"NOT_EVALUATED")
            self.assertEqual(row["neutrino"],"NOT_EVALUATED")
            self.assertEqual(row["B_to_Xs_gamma"],"NOT_EVALUATED")
            self.assertIsNone(row["global_zee_acceptance"])

if __name__=="__main__":unittest.main()
