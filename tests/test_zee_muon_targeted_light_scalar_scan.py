"""Paper 2 lighter-mass targeted scalar/EWPO pilot regression tests.

No experimental-allowed claim. Test proposal integrity and that
unmodified GateB4 sufficient scalar and correlated STU gates are used.
"""
from __future__ import annotations
import math
import unittest
from pathlib import Path
import sys
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from gateB4_adaptive_zee_scalar_scan import (
    encode,decode,scalar_screen,ewpo_screen,make_record
)
from zee_muon_targeted_light_scalar_scan import (
    STATUS,parse_targets,deform,choose_sources,objective,sample
)


def source():
    return {
        "seed_id":"B4_seed_0",
        "mH1":300.,"mH2":700.,"mh2":580.7,"ma":633.7,
        "alpha":1.398,"beta":1.394,"gamma":1.089,"m12sq":57700.,
        "lc":4.473,"k1":1.082,"k2":.00398,"k12":-.001266,
    }


class TestLightScalarTargetedScan(unittest.TestCase):
    def test_status_remains_screened_not_global_allowed(self):
        self.assertIn("NOT_ALLOWED",STATUS)
        self.assertIn("SCALAR_EWPO",STATUS)

    def test_target_mass_parser(self):
        self.assertEqual(parse_targets("250:500,300:550"),
                         [(250.,500.),(300.,550.)])
        with self.assertRaisesRegex(ValueError,"Repeated"):
            parse_targets("250:500,250:500")
        with self.assertRaisesRegex(ValueError,"domain"):
            parse_targets("400:450")
        with self.assertRaisesRegex(ValueError,"Use"):
            parse_targets("250,500")

    def test_random_targets_correlate_neutral_and_soft(self):
        rng=np.random.default_rng(120)
        q=deform(source(),(250.,500.),rng,mass_sigma=0.)
        self.assertEqual(q["mH1"],250.)
        self.assertEqual(q["mH2"],500.)
        self.assertGreater(q["mh2"],200.)
        self.assertGreater(q["ma"],200.)
        self.assertTrue(all(k in q for k in (
            "alpha","beta","gamma","m12sq","k1","k2","k12","lc")))
        self.assertGreater(q["m12sq"],0.)
        self.assertLess(abs(q["k12"]),min(q["k1"],q["k2"]))
        self.assertNotAlmostEqual(q["m12sq"],source()["m12sq"],delta=1.)
        self.assertIsNotNone(decode(encode(q)))

    def test_reuse_existing_B4_scalar_and_EWPO_pass(self):
        p=decode(encode(source()))
        theory=scalar_screen(p)
        self.assertIsNotNone(theory)
        self.assertTrue(theory["sufficient_global_quartic_BFB"])
        self.assertTrue(theory["tree_unitarity_pass"])
        stu=ewpo_screen(p,48)
        self.assertIsNotNone(stu)
        rec=make_record(p,theory,stu,0,"test",source()["seed_id"])
        y=objective(p,rec)
        self.assertTrue(y["sigma_Z_both_charges_1500GeV_fb"]>0.)
        self.assertTrue(y["n_Z_ll_tb_tb_conditional_ceiling_0p5ab"]>=0.)
        self.assertEqual(rec["candidate_status"],
                         "SCALAR_EWPO_SCREEN_ONLY_NOT_ALLOWED")

    def test_zero_proposals_not_universal_no_go(self):
        rows,summary=sample([source()],[(250.,500.)],0,
                            np.random.default_rng(1),
                            quadrature=48,source_count=1,report_every=0)
        self.assertEqual(rows,[])
        self.assertEqual(summary["n_attempts"],0)
        self.assertEqual(summary["n_scalar_STU_passes"],0)

    def test_choose_sources_deduplicates_cells(self):
        duplicate={**source(),"seed_id":"B4_seed_clone"}
        self.assertEqual(len(choose_sources([source(),duplicate],32)),1)


if __name__=="__main__":
    unittest.main()
