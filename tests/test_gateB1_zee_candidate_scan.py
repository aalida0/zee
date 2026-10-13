"""Gate B1: no fake model approval from a partial physics screen."""
from __future__ import annotations

from pathlib import Path
import math
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from gate6_benchmark import benchmark
from gate6_width_inventory import inventory, MZ, G12
from gateA1b_hierarchical_no_seed import scalar_kappa, target_neutrino_matrix
from gateB1_zee_candidate_scan import (
    SEED,STATUS,physical_point_spectrum,neutrino_at_point,
    make_point,flatten,
)

class TestGateB1(unittest.TestCase):
    def test_generalized_scalar_defaults_preserve_prior_seed(self):
        a=benchmark()
        b=physical_point_spectrum(SEED)
        self.assertAlmostEqual(a["mu4_GeV"],b["mu4_GeV"],places=9)
        self.assertTrue(a["sufficient_global_quartic_BFB"])
        self.assertTrue(a["tree_unitarity_pass"])
        self.assertEqual(a["status"],"TREE_SCALAR_SECTOR_SCREEN_NOT_FULL_ZEE_BENCHMARK")

    def test_mixing_angle_changes_cascade_coupling(self):
        w=inventory(**{
            "beta":SEED["beta"],"mH1":SEED["mH1"],
            "mH2":SEED["mH2"],"gamma":SEED["gamma"]
        })
        self.assertAlmostEqual(w["g12_used"],G12,delta=2e-9)
        small=inventory(beta=SEED["beta"],mH1=SEED["mH1"],
                        mH2=SEED["mH2"],gamma=.12)
        self.assertLess(small["g12_used"],w["g12_used"])
        self.assertLess(
            small["partial_widths_GeV"]["H2"]["H1_Z"],
            w["partial_widths_GeV"]["H2"]["H1_Z"])
        self.assertTrue(small["missing"])

    def test_neutrino_loop_prefactor_tracks_spectrum(self):
        p=dict(SEED)
        k=scalar_kappa(p["mH1"],p["mH2"],p["gamma"])
        self.assertAlmostEqual(k,scalar_kappa(),places=14)
        q=dict(p);q["gamma"]=0.
        self.assertAlmostEqual(scalar_kappa(q["mH1"],q["mH2"],0.),0.)
        with self.assertRaisesRegex(ValueError,"Vanishing"):
            neutrino_at_point(q)

    def test_complex_neutrino_matrix_closes_for_altered_point(self):
        p=dict(SEED)
        p["gamma"]=0.6
        p["mH2"]=850.
        Y,info=neutrino_at_point(p)
        self.assertEqual(Y.shape,(3,3))
        self.assertEqual(info["rank"],5)
        self.assertLess(info["neutrino_closure_eV"],1e-9)
        self.assertGreater(info["max_abs_Y"],0)
        self.assertTrue(info["neutrino_solution_not_global_fit"])

    def test_deterministic_scan_seed(self):
        import numpy as np
        a=np.random.default_rng(101)
        b=np.random.default_rng(101)
        self.assertEqual(make_point(a,0),SEED)
        self.assertEqual(make_point(a,1),make_point(b,1))

    def test_outputs_never_claim_physical_acceptance(self):
        src=Path(__file__).resolve().parents[1]/"scripts"
        code=(src/"gateB1_zee_candidate_scan.py").read_text()
        self.assertIn("NOT_GLOBAL_ALLOWED",STATUS)
        self.assertIn("n_physically_allowed_points",code)
        self.assertIn("None",code)
        self.assertIn("higgstools_applied\":False",code)
        self.assertIn("MISSING_FLAVOUR_AND_NEUTRINO_LIKELIHOOD",code)

if __name__=="__main__":
    unittest.main()
