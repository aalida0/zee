#!/usr/bin/env python3
"""F11 independent computational checks: operator superposition and truth labels.

These interface tests are NOT replacements for independent 2026 NNLO physics.
"""
from __future__ import annotations
import math
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import zee_paper1_F11_six_real_flavio_LO_NP_rate as q

def good_source(probe,m1,m2,t,g):
    c=math.cos(g)**2;s=math.sin(g)**2
    rows={}
    for order in range(3):
        for op in range(1,9):
            light=-(.15 if op==7 else .065 if op==8 else .001)/(m1/300)**2
            heavy=-(.15 if op==7 else .065 if op==8 else .001)/(m2/300)**2
            sm=-.18 if op==7 else -.07 if op==8 else 0.3
            rows[order,op]=[sm,light,heavy,sm+c*light+s*heavy]
    return {"input":{"mH1":m1,"mH2":m2,"tanbeta":t,"gamma":g,
                     "mu0":160.,"w1":c,"w2":s},
            "coefficient_rows":rows,
            "max_coherent_Wilson_residual":0.}

class TestF11(unittest.TestCase):
    def test_status_not_full_nnlo(self):
        self.assertIn("NOT_MODERN_NNLO_EXCLUSION",q.STATUS)
        self.assertGreaterEqual(len(q.MISSING),4)
        self.assertTrue(any("2026" in s for s in q.MISSING))
        self.assertTrue(any("LFV" in s for s in q.MISSING))
    def test_matching_gamma_closure(self):
        src=q.matching(None,300.,700.,5.6,1.1,runner=good_source)
        a,b,c=q.coeff(src,7)
        self.assertAlmostEqual(c,math.cos(1.1)**2*a+math.sin(1.1)**2*b)
        e=q.matching(None,500.,500.,5.6,1.1,runner=good_source)
        l,h,m=q.coeff(e,7)
        self.assertAlmostEqual(l,h)
        self.assertAlmostEqual(l,m)
    def test_source_permutation_rejected(self):
        def modified(*args):
            obj=good_source(*args)
            obj["coefficient_rows"][0,7][3]+=.3
            return obj
        with self.assertRaises(ValueError):
            q.matching(None,300,700,5.6,.7,runner=modified)
    def test_mass_and_higgs_weights_rejected(self):
        def modified(*args):
            obj=good_source(*args)
            obj["input"]["mH2"]+=2
            return obj
        with self.assertRaises(ValueError):
            q.matching(None,300,700,5.6,.7,runner=modified)
    def test_published_2026_Eq4_linearized_not_full_NNLO(self):
        r=q.linearized_2026(-.04,-.02)
        self.assertAlmostEqual(r["linearized_predicted_central_times_1e4"],
                               3.54+8.51*.04+2.16*.02)
        self.assertIs(r["quadratic_NP_terms_omitted"],True)
        self.assertIs(r["NLO_NNLO_NP_matching_omitted"],True)
        self.assertAlmostEqual(q.MODERN_SM["central_times_1e4"],3.54)
        self.assertAlmostEqual(q.PDG_EXP["central_times_1e4"],3.49)
    def test_independent_A1S_vs_E4A_gate_catches_mismatch(self):
        with patch.object(q,"independent_a1s_coefficients",
                          return_value=(-.020,-.010)):
            self.assertTrue(q.cross_check_a1s_vs_e4a(
                Path("/tmp/nonexistent_fake_source"),670.,5.6,-.02,-.01))
            with self.assertRaises(ValueError):
                q.cross_check_a1s_vs_e4a(
                    Path("/tmp/nonexistent_fake_source"),670.,5.6,-.03,-.01)
    def test_six_physical_rates_use_coherent_amplitude_not_average(self):
        class Engine:
            _sm=3.36e-4
            def prediction(self,a,b):
                return self._sm - 8.22e-4*a - 1.99e-4*b + 1.0e-3*a*a
        six=[]
        f10={}
        for i in range(6):
            key=f"B4_{i}"
            six.append({"id":key,"mH1":300.+i*10,
                        "mH2":700.+i*11,"gamma":1.089,"tanbeta":5.6})
            f10[key]={"legacy_SuperIso_full_Zee_BR_Egamma1p6_NOT_2026":.000391,
                      "Zee_to_TypeII670_legacy_NP_shift_ratio_NOT_CL":1.5,
                      "P1_general_lepton_included_cascade_proxy_NOT_pb":.56,
                      "partial_LFV_max_ratio_NOT_PHYSICAL_CL":1e-4}
        out=q.six_rates(Engine(),None,six,f10,runner=good_source)
        self.assertEqual(len(out),6)
        for z in out:
            self.assertGreater(z["BR_flavio_TypeII670_same_tanbeta_hybrid"],
                               3.36e-4)
            self.assertGreater(z["Zee_to_TypeII670_same_flavio_NP_rate_shift_NOT_CL"],0.)
            self.assertAlmostEqual(
                z["Zee_to_TypeII670_same_flavio_NP_rate_shift_NOT_CL"],
                (z["BR_flavio_LO_NP_hybrid"]-3.36e-4)/
                (z["BR_flavio_TypeII670_same_tanbeta_hybrid"]-3.36e-4))
            self.assertGreater(z["BR_2026_published_Eq4_LINEARIZED"],
                               q.MODERN_SM["central_times_1e4"]*1e-4)
            self.assertIsNotNone(z[
                "Zee_to_TypeII670_2026_Eq4_LINEAR_NP_SHIFT_NOT_CL"])
            self.assertIsNone(z[
                "flavio_quadratic_fraction_from_2015_response_DIAGNOSTIC"])
            self.assertFalse(z[
                "2026_160GeV_source_crosschecked_A1S_vs_E4A"])
            self.assertIsNone(z["modern_NNLO_Zee_2026_95CL"])
            self.assertIsNone(z["fully_Zee_allowed_or_excluded"])
            self.assertIsNone(z["physical_Zee_hadronic_R_tbZ_pb"])
            weighted=math.cos(z["gamma"])**2*z[
                "BR_flavio_LO_NP_pure_light"]+math.sin(z["gamma"])**2*z[
                "BR_flavio_LO_NP_pure_heavy"]
            self.assertGreater(abs(weighted-z["BR_flavio_LO_NP_hybrid"]),1e-9)

if __name__=="__main__":
    unittest.main()
