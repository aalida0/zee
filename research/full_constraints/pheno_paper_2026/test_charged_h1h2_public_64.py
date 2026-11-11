"""Source-specific Zee H1/H2 doublet-factor and complete D4 decay tests."""
import copy
import math
import unittest
from research.full_constraints.scan_pilot_2026.historical_certified_texture import source_points
from research.full_constraints.pheno_paper_2026.charged_h1h2_public_64 import (
    normalized_tb_couplings,physical_two_body,
)
from research.full_constraints.pheno_paper_2026.H2_charged_higgsbounds_probe import TOOL_DECAYS

class ChargedSourceMatchedCouplings(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p={row["id"]:row["input_card"]["physical"] for row in source_points()}

    def test_typeII_doublet_projection_for_all_original_16(self):
        self.assertEqual(len(self.p),16)
        for p in self.p.values():
            k1=normalized_tb_couplings(p,1)
            k2=normalized_tb_couplings(p,2)
            beta=p["beta"];g=p["gamma"]
            self.assertAlmostEqual(k1["kappa_t"],math.cos(g)/math.tan(beta))
            self.assertAlmostEqual(k1["kappa_b"],math.cos(g)*math.tan(beta))
            self.assertAlmostEqual(k2["kappa_t"],-math.sin(g)/math.tan(beta))
            self.assertAlmostEqual(k2["kappa_b"],-math.sin(g)*math.tan(beta))
            self.assertAlmostEqual(k1["doublet_amplitude"]**2+k2["doublet_amplitude"]**2,1.)
            self.assertAlmostEqual(k1["kappa_b"]/k1["kappa_t"],math.tan(beta)**2)

    def test_invalid_which_charge_rejected(self):
        with self.assertRaises(ValueError):
            normalized_tb_couplings(self.p[15673],3)

    def test_physical_two_body_uses_full_including_exotic_denominator(self):
        channels=[{"channel":c,"width_GeV":i/200.} for i,(_,c) in enumerate(TOOL_DECAYS,1)]
        channels+=[{"channel":"H1 Z","width_GeV":3.1},
                   {"channel":"H1 h","width_GeV":1.2}]
        s=math.fsum(x["width_GeV"] for x in channels)
        d={"total":{"status":"D4_COMPLETE_TWO_BODY_BR_PASS","total_width_GeV":s},
           "channels":channels}
        a=physical_two_body(d,require_h2=True)
        self.assertAlmostEqual(a["BR_H1Z"],3.1/s)
        self.assertLess(sum(a["SM_final_state_BRs"].values()),1)
        tamper=copy.deepcopy(d);tamper["total"]["total_width_GeV"]=s-.5
        with self.assertRaises(ValueError):physical_two_body(tamper,require_h2=True)

    def test_native_missing_required_channels_are_never_zero_filled(self):
        d={"total":{"status":"D4_COMPLETE_TWO_BODY_BR_PASS","total_width_GeV":1.0},
           "channels":[{"channel":"t anti-b","width_GeV":1.0}]}
        with self.assertRaises(KeyError):physical_two_body(d)

if __name__=="__main__":unittest.main()
