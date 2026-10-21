#!/usr/bin/env python3
"""F16: independent real heavy Zee scalar + optimized complex f/Y fixture tests.

These tests do not substitute for actual Mathematica SARAH or MadWidth.
"""
import math,sys,tempfile,json
from pathlib import Path
from unittest import TestCase,main,mock
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import zee_paper1_F16_exact_F13_SARAH_vertex_fixtures as f
from zee_paper1_F13_heavy_P1_seeds import validated_p1_seeds
from zee_paper1_florentino_feasibility_scan import optimize_point,complex_payload
from gateA1b_hierarchical_no_seed import target_neutrino_matrix,ME,MMU,MTAU
from gateB3_general_zee_charged_lepton_widths import evaluate as b3_eval
from zee_paper1_F15_charged_width_CKM_mass_scheme_audit import close

class TestF16(TestCase):
    @classmethod
    def setUpClass(cls):
        points,_=validated_p1_seeds(160,40,20261021,max_seeds=2)
        if not points:raise AssertionError("No actual scalar/EWPO passing heavy points")
        cls.p=dict(points[0][0],id="F16_REAL_HEAVY_SCALAR_TEST")
        target,_=target_neutrino_matrix()
        result=optimize_point(cls.p,target,np.random.default_rng(905),
                  trials=35,local_seeds=2,max_evals=70)
        if "best" not in result:
            raise AssertionError("No actual reconstructed complex neutrino source")
        cls.best=result["best"]
        cls.b3=b3_eval(cls.p,
            np.asarray(cls.best["optimized_f"]["real"])+
              1j*np.asarray(cls.best["optimized_f"]["imag"]),
            np.asarray(cls.best["optimized_Y"]["real"])+
              1j*np.asarray(cls.best["optimized_Y"]["imag"]),target)

    def test_real_P1_heavy_scalar_SU2_and_charged_trilinears(self):
        phys,rules,expected,su2=f.expected_sarah(self.p,self.b3)
        self.assertEqual(len(rules),16)
        self.assertLess(su2["quartic_max_relative_residual"],4e-11)
        self.assertEqual(expected["charged_Goldstone_H1_H2_rotation"].shape,(3,3))
        self.assertTrue(np.allclose(
            expected["charged_Goldstone_H1_H2_rotation"] @
            expected["charged_Goldstone_H1_H2_rotation"].T,
            np.eye(3),atol=1e-12))
        self.assertAlmostEqual(
            expected["gZ_H1H2_derivative_abs"],
            91.1876/phys["inputs"]["v"]*math.sin(self.p["gamma"])*
            math.cos(self.p["gamma"]))
        self.assertEqual(len(expected["masses_GeV"]),5)

    def test_f16_exact_complex_phases_and_neutrino_case_roundtrip(self):
        np.testing.assert_allclose(
            np.asarray(self.best["optimized_Y"]["real"])+
            1j*np.asarray(self.best["optimized_Y"]["imag"]),
            np.asarray(self.best["optimized_Y"]["real"])+
            1j*np.asarray(self.best["optimized_Y"]["imag"]))
        self.assertLess(self.b3["neutrino_matrix_closure_eV"],1e-9)
        self.assertTrue(np.any(np.abs(
            self.best["optimized_Y"]["imag"])>0))
        with tempfile.TemporaryDirectory() as temp:
            dir=Path(temp)
            p=dir/"F13_priority_01_NOT_ALLOWED.json"
            data={"scalar":self.p,"neutrino_and_partial_lfv":{
                "best":self.best}}
            p.write_text(json.dumps(data))
            ranked={k:self.p[k] for k in ("mH1","mH2","beta","gamma")}
            production={"TypeII_Santander_NLO13TeV_sigma_pb":".0016",
               "13TeV_TypeII_sigma_times_included_cascade_proxy_pb":
                 str(.0016*self.b3["production_weighted_partial_cascade_proxy"])}
            with mock.patch.object(f,"source_b3",return_value=(
               self.b3,self.p,{"priority_record_SHA256":"fixture"})):
                case,wl=f.build_case(self.p["id"],ranked,{self.p["id"]:production},{
                    "f13dir":dir})
            self.assertTrue(case["SARAH_E3_FSARAH_eq_2_fChEN"])
            self.assertTrue(case["SARAH_weak_vev_basis_Y_mass_rotated"])
            self.assertTrue(case[
                "source_SU2_higgs_basis_rotation_relative_error"]<4e-11)
            self.assertIsNone(case["full_model_madwidth_physical_totals"])
            self.assertIn('"FSARAH" -> ',wl)
            self.assertIn('"LeptonicWidths" -> ',wl)
            self.assertIn('"ScalarRules" -> ',wl)
            self.assertIn('"ExpectedHm" -> ',wl)
            self.assertTrue(wl.startswith("<|") and wl.endswith("|>"))

    def test_bad_scalar_does_not_pass_as_sarah_model(self):
        p=dict(self.p,mH1=-1)
        with self.assertRaises(ValueError):
            f.expected_sarah(p,self.b3)

    def test_sarah_wolfram_fixture_float_complex_encoder(self):
        self.assertEqual(f.wlreal(1e-6),"9.99999999999999955*^-07")
        self.assertIn("I*(",f.wlcomplex(1+2j))
        with self.assertRaises(ValueError):f.wlreal(float("nan"))
        with self.assertRaises(ValueError):f.wlmatrix([1,2,3])
        self.assertTrue(any("UFO" in s for s in f.MISSING))

if __name__=="__main__":
    main()
