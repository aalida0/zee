#!/usr/bin/env python3
"""F15 physics validation; real heavy Zee scalar/Yukawa B3 width handoff.

Three F13 source point files are PRIVATE on AF; these tests reconstruct
an actual heavy Zee scalar and exact neutrino/partial LFV solution
without pretending mock parameter files equal original F13 solutions.
"""
import math,unittest,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import zee_paper1_F15_charged_width_CKM_mass_scheme_audit as x
from zee_paper1_F13_heavy_P1_seeds import validated_p1_seeds
from zee_paper1_florentino_feasibility_scan import optimize_point
from gateA1b_hierarchical_no_seed import target_neutrino_matrix
from gateB3_general_zee_charged_lepton_widths import (
   evaluate as evaluate_b3,complex_matrix)
from gate6_width_inventory import tb_width

class TestF15(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sources,stats=validated_p1_seeds(160,40,20261021,max_seeds=2)
        if not sources:raise AssertionError("No real heavy P1 scalar/EWPO seed")
        cls.scalar=sources[0][0].copy()
        cls.scalar["id"]="F15_REAL_HEAVY_SCALAR_TEST"
        target,_=target_neutrino_matrix()
        candidate=optimize_point(
            cls.scalar,target,np.random.default_rng(1910),
            trials=35,local_seeds=2,max_evals=70)
        if "best" not in candidate:
            raise AssertionError("No real neutrino-closed complex F13 seed")
        best=candidate["best"]
        cls.b3=evaluate_b3(cls.scalar,
            complex_matrix(best["optimized_f"],"f"),
            complex_matrix(best["optimized_Y"],"Y"),target)
    def test_all_nine_modes_and_tb_source_normalization(self):
        p=self.scalar;tan=math.tan(p["beta"]);gamma=p["gamma"]
        ck=x.validate_ckm()
        self.assertEqual(len(ck["row_sum_squares"]),3)
        for state,mass,dfrac in (("H1",p["mH1"],math.cos(gamma)**2),
                                 ("H2",p["mH2"],math.sin(gamma)**2)):
            inventory=x.quark_inventory(mass,tan,dfrac,4.7)
            self.assertEqual(set(inventory),{
                "ud","us","ub","cd","cs","cb","td","ts","tb"})
            self.assertGreater(inventory["tb"],0)
            self.assertGreater(inventory["cs"],0)
            self.assertAlmostEqual(
                 inventory["tb"],
                 tb_width(mass,tan,dfrac)*x.VABS[2,2]**2,delta=1e-9)
            self.assertGreater(sum(inventory.values()),inventory["tb"])
    def test_source_complex_zee_B3_widths_and_scheme_variations(self):
        p=self.scalar
        self.assertLess(self.b3["neutrino_matrix_closure_eV"],1e-9)
        self.assertGreater(self.b3["BR_H2_H1Z_included_general_Zee"],0)
        self.assertGreater(self.b3["BR_H1_tb_included_general_Zee"],0)
        sig=.0016
        a=x.scenario(self.b3,p,sig,4.7)
        b=x.scenario(self.b3,p,sig,3.0)
        c=x.scenario(self.b3,p,sig,2.5)
        self.assertGreater(a["H1"]["CKM_other_8_quark_modes_GeV"],0)
        self.assertGreater(a["H2"]["CKM_other_8_quark_modes_GeV"],0)
        self.assertLess(a["relative_new_over_original_B3_proxy"],1.0001)
        self.assertGreater(a["relative_new_over_original_B3_proxy"],0)
        self.assertGreater(b["approximate_sigma13_product_pb"],0)
        self.assertGreater(c["approximate_sigma13_product_pb"],0)
        for z in (a,b,c):
            self.assertIsNone(z["actual_physical_signal_rate_pb"])
            self.assertIsNone(z["physical_total_charged_widths_GeV"])
        # Explicitly avoid treating 4.7,3.0,2.5 as a statistical uncertainty.
        self.assertNotEqual(a["relative_new_over_original_B3_proxy"],
                            b["relative_new_over_original_B3_proxy"])
    def test_no_nonphysical_inputs_or_hadron_rate_claim(self):
        p=self.scalar;tan=math.tan(p["beta"])
        for mb in (-1,0,float("nan")):
            with self.assertRaises(ValueError):
                x.charged_quark_width(850,"t","b",tan,.5,mb)
        for name in ("top","x",None):
            with self.assertRaises(ValueError):
                x.charged_quark_width(850,name,"b",tan,.5,4.7)
        self.assertIn("NOT_FULL_WIDTH",x.STATUS)
        self.assertTrue(any("FCC-hh" in s for s in x.MISSING))
        self.assertTrue(any("NNLO" in s for s in x.MISSING))
    def test_FCC_hh_requirements_are_not_cross_section_predictions(self):
        p=self.scalar
        payload={"candidate_id":"HEAVY_REAL_INPUT",
                 "spectrum":{"gamma":p["gamma"]},
                 "mb_input_stress_scenarios_NOT_an_NLO_uncertainty":{
                  "fixed_b4p7":x.scenario(self.b3,p,.0016,4.7)}}
        tab=x.fcc_production_thresholds([payload])
        self.assertEqual(len(tab),18)
        q=next(v for v in tab if v["proton_proton_sqrt_s_GeV"]==85000
               and v["event_count_target_NOT_significance"]==25
               and v["selection_efficiency_ASSUMED_NOT_simulated"]==.05)
        n=q["required_TypeII_like_baseline_sigma_at_this_energy_fb"]
        proxy=q["CKM_LO_included_channel_cascade_proxy_NOT_full_BR"]
        self.assertAlmostEqual(n*20000*.0673*.05*proxy,25.)
        self.assertIsNone(q["FCC_85_or_100TeV_actual_production_sigma_fb"])
        self.assertFalse(q["complete_Zee_widths_and_observability_certified"])
        at100=next(v for v in tab if v["proton_proton_sqrt_s_GeV"]==100000
               and v["event_count_target_NOT_significance"]==25
               and v["selection_efficiency_ASSUMED_NOT_simulated"]==.05)
        self.assertAlmostEqual(at100[
            "required_TypeII_like_baseline_sigma_at_this_energy_fb"]/n,
            2/3)
    def test_source_LFV_complex_phase_not_deleted(self):
        # B3 helper itself validates antisymmetry and exact matrix closure.
        self.assertGreater(self.b3["totals_included_GeV"]["H1"],0)
        self.assertGreater(self.b3["totals_included_GeV"]["H2"],0)
        self.assertGreater(self.b3["production_weighted_partial_cascade_proxy"],0)
if __name__=="__main__":unittest.main()
