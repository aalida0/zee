"""Independent algebra and fail-closed tests of the 2026 Eq.(4) diagnostic.

The independent BMU source substitution tests support the documented LO
operator bridge. No test establishes a full Zee constraint.
"""
import copy
import json
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
import hashlib
import mpmath as mp

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from module5.hyperiso_patch_contract import make_contract
from module5.bsgamma_2026_linear_diagnostic import (
    eq4_conditional, run_contract, STATUS, SOURCE, MATCHING_GEV,
    COEF_C7, COEF_C8, CONVENTION_STATUS
)

BASE={"mH1_GeV":550.,"mH2_GeV":900.,
      "beta_rad":math.atan(5.3),"gamma_rad":1.09,
      "mt_MSbar_GeV":163.96892236746697,"matching_scale_GeV":160.}

def bmu_scalar_lo(mass, tanb, mt=BASE["mt_MSbar_GeV"]):
    """9904413v1 Sec.2 / App.B, not the production four-kernel formula.

    phi=H-, psi=t: Qpsi=2/3, Qphi=-1, kappapsi=4/3, kappaphi=0,
    xi=1; N R1=x/(2 tanb^2), N R2=x/2. P7/P8 are Eq.(10).
    """
    with mp.workdps(70):
        x=(mp.mpf(mt)/mass)**2
        def g1(z):
            if z==1:return -mp.mpf(1)/24
            return -z*mp.log(z)/(2*(1-z)**4)+(z*z-5*z-2)/(12*(1-z)**3)
        def g2(z):
            if z==1:return -mp.mpf(1)/3
            return mp.log(z)/(1-z)**3+(3-z)/(2*(1-z)**2)
        c7=x/2*((mp.mpf(2)/3*g1(x)+g1(1/x)/x)/mp.mpf(tanb)**2
                 +(mp.mpf(2)/3-x)*g2(x)-mp.mpf(1)/2)
        c8=x/2*(g1(x)/mp.mpf(tanb)**2+g2(x))
        return {"C7":float(c7),"C8":float(c8)}

def source_bridge_rows():
    rows=[]
    for mass in (163.96892236746697,300.,550.,900.,1000.,2000.,5000.,100000.):
        for tb in (0.5,2.,5.3,50.):
            source=bmu_scalar_lo(mass,tb)
            result=make_contract({**BASE,"mH1_GeV":mass,"gamma_rad":0.,
                                  "beta_rad":math.atan(tb)})
            actual={c:result["coefficients"][c]["real"] for c in ("C7","C8")}
            rows.append({"mass_GeV":mass,"tanbeta":tb,"source":source,
                         "frozen_LO":actual,
                         "absolute_residual":{c:abs(source[c]-actual[c]) for c in source}})
    return rows

class SourceLockedConditionalTest(unittest.TestCase):
    def test_exact_paper_coefficients_and_zero_np_baseline(self):
        self.assertEqual(SOURCE,"arXiv:2608.29863v1")
        self.assertEqual(MATCHING_GEV,160.)
        self.assertEqual((COEF_C7,COEF_C8),(-8.51,-2.16))
        self.assertEqual(eq4_conditional(0.,0.)["conditional_B_times_1e4"],3.54)

    def test_independent_arithmetic_and_linearity(self):
        for d7,d8 in ((0.001,0.),(0.,-0.002),(-0.01,-0.02),(0.03,0.005)):
            a=eq4_conditional(d7,d8)
            expected=3.54-8.51*d7-2.16*d8
            self.assertAlmostEqual(a["conditional_B_times_1e4"],expected,places=13)
            self.assertAlmostEqual(a["delta_B_times_1e4"],-8.51*d7-2.16*d8,places=13)
            self.assertEqual(a["C7_linear_term_times_1e4"],-8.51*d7)
            self.assertEqual(a["C8_linear_term_times_1e4"],-2.16*d8)
        d=eq4_conditional(-0.01,-0.02)
        self.assertGreater(d["conditional_B_times_1e4"],3.54)

    def test_two_charged_states_and_no_exclusion(self):
        result=run_contract(make_contract(BASE))
        self.assertEqual(result["status"],STATUS)
        self.assertEqual(result["external_convention_status"],CONVENTION_STATUS)
        self.assertEqual(CONVENTION_STATUS,"EXTERNAL_CONVENTION_PASS")
        self.assertEqual(result["matching_input"]["mt_MSbar_GeV"],BASE["mt_MSbar_GeV"])
        self.assertEqual(result["shift_input"]["DeltaC7"],make_contract(BASE)["coefficients"]["C7"]["real"])
        self.assertEqual(result["shift_input"]["DeltaC8"],make_contract(BASE)["coefficients"]["C8"]["real"])
        self.assertIsNone(result["zee_exclusion"])
        self.assertIsNone(result["zee_likelihood"])
        self.assertIsNone(result["global_zee_acceptance"])
        self.assertEqual(result["experiment_comparison"],"NOT_EVALUATED")
        self.assertEqual(result["hyperiso_injection"],"NOT_USED_SM_BSM_PATCH_DROPPED")

    def test_state_exchange(self):
        a=run_contract(make_contract(BASE))
        b=run_contract(make_contract({**BASE,"mH1_GeV":900.,"mH2_GeV":550.,
                                           "gamma_rad":math.pi/2-1.09}))
        self.assertAlmostEqual(a["linearized"]["conditional_B_times_1e4"],
                               b["linearized"]["conditional_B_times_1e4"],places=13)

    def test_source_contract_tamper_and_scale_fail(self):
        good=make_contract(BASE)
        mods=(
            lambda x:x["coefficients"]["C7"].__setitem__("real",0.),
            lambda x:x["input"].__setitem__("matching_scale_GeV",81.),
            lambda x:x.__setitem__("matching_scale_GeV",81.),
            lambda x:x["coefficients"]["C8"].__setitem__("imag",.1),
            lambda x:x.__setitem__("status","VALIDATED_ZEE_BR"),
            lambda x:x.__setitem__("extra",123),
            lambda x:x["coefficients"]["C7"].__setitem__("imag",False),
            lambda x:x["scalar_rows"][0].__setitem__("delta_C7",float("inf")),
            lambda x:x["input"].pop("mt_MSbar_GeV"),
            lambda x:x["input"].__setitem__("top_mass_input_definition","POLE"),
            lambda x:x.__setitem__("input_sha256","bad"),
        )
        for mutate in mods:
            x=copy.deepcopy(good)
            mutate(x)
            with self.assertRaises((ValueError,KeyError)):run_contract(x)
        with self.assertRaises(ValueError):
            run_contract(make_contract({**BASE,"matching_scale_GeV":81.}))

    def test_gamma_limits_and_two_state_source_substitution(self):
        for gamma in (0.,math.pi/2,BASE["gamma_rad"]):
            result=run_contract(make_contract({**BASE,"gamma_rad":gamma}))
            single=[bmu_scalar_lo(BASE[k],5.3) for k in ("mH1_GeV","mH2_GeV")]
            for c in ("C7","C8"):
                expected=math.cos(gamma)**2*single[0][c]+math.sin(gamma)**2*single[1][c]
                self.assertAlmostEqual(result["shift_input"]["Delta"+c],expected,delta=2e-15)

    def test_independent_bmu_normalized_scalar_source(self):
        for row in source_bridge_rows():
            for c in ("C7","C8"):
                with self.subTest(mass=row["mass_GeV"],tb=row["tanbeta"],c=c):
                    self.assertTrue(math.isclose(row["source"][c],row["frozen_LO"][c],
                                                 rel_tol=3e-13,abs_tol=2e-15))

    def test_2026_published_type_ii_sign_and_trend(self):
        # Sec.IV/Fig.3: positive enhancement, decoupling with mass,
        # decreasing enhancement with tanbeta. No fit to its NNLO curve.
        def shift(mass,tb):
            c=bmu_scalar_lo(mass,tb)
            self.assertLess(c["C7"],0.);self.assertLess(c["C8"],0.)
            return eq4_conditional(c["C7"],c["C8"])["delta_B_times_1e4"]
        masses=[shift(m,50.) for m in (550.,1000.,2000.,5000.)]
        betas=[shift(550.,tb) for tb in (0.5,2.,5.3,50.)]
        self.assertTrue(all(a>b>0 for a,b in zip(masses,masses[1:])))
        self.assertTrue(all(a>b>0 for a,b in zip(betas,betas[1:])))

    def test_nonfinite_values_rejected(self):
        for bad in (float("nan"),float("inf"),float("-inf"),True,10**400):
            with self.assertRaises(ValueError):eq4_conditional(bad,0.)
        for bad in (float("nan"),float("inf"),False):
            with self.assertRaises(ValueError):eq4_conditional(0.,bad)

    def test_original_input_hash_verified_only_with_original_bytes(self):
        raw=json.dumps(BASE).encode();c=make_contract(BASE)
        c["input_sha256"]=hashlib.sha256(raw).hexdigest()
        self.assertEqual(run_contract(c,raw)["source_input_hash_verification"],"VERIFIED")
        self.assertIn("NOT_VERIFIED",run_contract(c)["source_input_hash_verification"])
        for bad in (b'{}',raw+b' ',raw.replace(b'550.0',b'551.0')):
            with self.assertRaises(ValueError):run_contract(c,bad)
        c["input_sha256"]="0"*64
        with self.assertRaises(ValueError):run_contract(c,raw)

    def test_example_cli_and_duplicate_key_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);inp=root/"contract.json";out=root/"result.json"
            inp.write_text(json.dumps(make_contract(BASE)))
            cmd=[sys.executable,"-m","module5.bsgamma_2026_linear_diagnostic",
                 "--input",str(inp),"--output",str(out)]
            a=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True)
            self.assertEqual(a.returncode,0,a.stderr)
            obj=json.loads(out.read_text())
            self.assertEqual(obj["status"],STATUS)
            source=root/"source.json"
            source.write_text(json.dumps(BASE))
            contract=make_contract(BASE)
            contract["input_sha256"]=hashlib.sha256(source.read_bytes()).hexdigest()
            inp.write_text(json.dumps(contract))
            source_cmd=cmd+["--source-input",str(source)]
            a=subprocess.run(source_cmd,cwd=ROOT,text=True,capture_output=True)
            self.assertEqual(a.returncode,0,a.stderr)
            self.assertEqual(json.loads(out.read_text())["source_input_hash_verification"],"VERIFIED")
            old=out.read_bytes()
            source.write_text(source.read_text()+" ")
            a=subprocess.run(source_cmd,cwd=ROOT,text=True,capture_output=True)
            self.assertNotEqual(a.returncode,0)
            self.assertEqual(out.read_bytes(),old)
            for bad in ('{"input":{},"input":{}}',
                        inp.read_text().replace('"imag": 0.0','"imag": NaN',1),
                        inp.read_text().replace('"imag": 0.0','"imag": 1e999',1)):
                inp.write_text(bad)
                a=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True)
                self.assertNotEqual(a.returncode,0)
                self.assertEqual(out.read_bytes(),old)

if __name__=="__main__":
    unittest.main()
