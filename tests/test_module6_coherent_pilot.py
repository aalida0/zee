"""Tests for coherent candidate provenance and non-exclusion semantics.

Mocks isolate orchestration; a **real** end-to-end run is required by AGENTS.
"""
import copy
import hashlib
import json
import math
import sys
from decimal import Decimal, localcontext
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from module6.coherent_pilot import pilot,STATUS,SOURCE_TOP_MS_160,LHA_SOURCE_SHA256
from module2.interface import canonical_hash, scalar_input, evaluate as real_neutrino
from module1.scalar_constraints import evaluate as real_scalar
from module3.interface import evaluate as real_lfv
from module5.hyperiso_patch_contract import make_contract
from module5.bsgamma_2026_linear_diagnostic import run_contract

def independent_hash(record):
    return hashlib.sha256(json.dumps(record,sort_keys=True,separators=(',', ':'),
                                     allow_nan=False).encode()).hexdigest()

def source():
    return json.loads((ROOT/"module3/example.json").read_text())

def fake_scalar(record):
    return {"benchmark_id":record["benchmark_id"],
            "input":record,"lagrangian":{},"provenance":{},
            "status":"SCALAR_PIPELINE_UNKNOWN",
            "global_zee_acceptance":None,
            "gates":{"bfb":{"assessment":"PASS","status":"PASS"},
                     "vacuum":{"assessment":"UNKNOWN","status":"UNKNOWN"}}}

def fake_lfv(record):
    channels=("mu_to_e_gamma","tau_to_e_gamma","tau_to_mu_gamma")
    m2=record["module2_input"]
    return {"benchmark_id":record["benchmark_id"],
            "provenance":{"input_sha256":canonical_hash(record),
                          "module2_input_sha256":canonical_hash(m2),
                          "module2_output_sha256":canonical_hash(real_neutrino(m2)),
                          "scalar":scalar_input(m2["scalar"])[1]},
            "universality":{},"missing_contributions":[],
            "status":"SCOPED_LFV_COMPUTED","global_zee_acceptance":None,
            "COMPLETE_LFV":False,
            "gates":{"full_lfv":"NOT_EVALUATED"},
            "observables":{k:{"partial_BR":1e-12,"physical_status":"SCALAR_ONE_LOOP_APPROXIMATION",
                              "experimental_comparison":"NOT_EVALUATED"} for k in channels}}

def execute(inp=None):
    with patch("module6.coherent_pilot.scalar_evaluate",side_effect=fake_scalar),patch(
         "module6.coherent_pilot.lfv_evaluate",side_effect=fake_lfv):
        return pilot(inp if inp is not None else source(),SOURCE_TOP_MS_160,LHA_SOURCE_SHA256)

class PilotTests(unittest.TestCase):
    def test_coherent_and_explicitly_incomplete(self):
        out=execute()
        self.assertEqual(out["status"],STATUS)
        self.assertEqual(out["ordering"],"NO")
        self.assertIsNone(out["global_zee_acceptance"])
        self.assertFalse(out["constraints_complete"])
        self.assertFalse(out["neutrino_lfv"]["COMPLETE_LFV"])
        self.assertEqual(out["bsgamma"]["flavor_classification"],"UNCLASSIFIED")
        self.assertEqual(out["bsgamma"]["nonlinear_reliability"],"UNKNOWN")
        self.assertEqual(out["neutrino_lfv"]["module4_Barr_Zee_and_W_completion"],"NOT_EVALUATED")
        self.assertEqual(out["scalar"]["global_vacuum_certification"],"NOT_ESTABLISHED")

    def test_derives_charge_masses_from_same_bound_scalar_record(self):
        inp=source()
        out=execute(inp)
        self.assertEqual(out["provenance"]["bound_scalar_sha256"],inp["module2_input"]["scalar"]["sha256"])
        self.assertEqual(out["benchmark_id"],inp["benchmark_id"])
        self.assertNotEqual(out["bsgamma"]["delta_C7"],0.)
        self.assertEqual(out["bsgamma"]["matching_input"]["mH1_GeV"],300.)
        self.assertEqual(out["bsgamma"]["matching_input"]["mH2_GeV"],700.)
        self.assertEqual(out["bsgamma"]["matching_input"]["beta_rad"],1.394)
        self.assertEqual(out["bsgamma"]["matching_input"]["gamma_rad"],1.089)

    def test_tampered_scalar_sha_rejected(self):
        inp=source()
        inp["module2_input"]["scalar"]["record"]["physical"]["mH1"]=600.
        with self.assertRaises(ValueError): execute(inp)

    def test_reject_bad_top_mass_or_lha(self):
        with patch("module6.coherent_pilot.scalar_evaluate",side_effect=fake_scalar), patch(
            "module6.coherent_pilot.lfv_evaluate",side_effect=fake_lfv):
            for mass, sha in ((163.,LHA_SOURCE_SHA256),
                              (SOURCE_TOP_MS_160,"0"*64),
                              (True,LHA_SOURCE_SHA256),
                              ("163.96892236746697",LHA_SOURCE_SHA256),
                              (float("nan"),LHA_SOURCE_SHA256),
                              (float("inf"),LHA_SOURCE_SHA256),
                              (10**400,LHA_SOURCE_SHA256)):
                with self.assertRaises(ValueError):pilot(source(),mass,sha)

    def test_reject_unexpected_full_lfv_claim(self):
        bad=fake_lfv(source());bad["COMPLETE_LFV"]=True
        with patch("module6.coherent_pilot.scalar_evaluate",side_effect=fake_scalar), patch(
            "module6.coherent_pilot.lfv_evaluate",return_value=bad):
            with self.assertRaises(ValueError):pilot(source(),SOURCE_TOP_MS_160,LHA_SOURCE_SHA256)

    def test_rebound_scalar_changes_derived_flavor_only_after_rehash(self):
        baseline=execute()
        for key,value,flavor_key in (("mH1",340.,"mH1_GeV"),("mH2",730.,"mH2_GeV"),
                                     ("beta",1.3,"beta_rad"),("gamma",.9,"gamma_rad")):
            with self.subTest(key=key):
                inp=source(); wrapper=inp["module2_input"]["scalar"]
                wrapper["record"]["physical"][key]=value
                with self.assertRaisesRegex(ValueError,"SHA256 mismatch"):execute(inp)
                wrapper["sha256"]=independent_hash(wrapper["record"])
                out=execute(inp)
                self.assertEqual(out["bsgamma"]["matching_input"][flavor_key],value)
                self.assertEqual(out["bsgamma"]["bound_scalar_sha256"],wrapper["sha256"])
                self.assertNotEqual(out["bsgamma"]["delta_C7"],baseline["bsgamma"]["delta_C7"])

    def test_reject_ids_nested_types_and_unknown_scale_before_evaluation(self):
        bad=[]
        inp=source();inp["module2_input"]["benchmark_id"]="different";bad.append(inp)
        inp=source();w=inp["module2_input"]["scalar"]
        w["record"]["benchmark_id"]="different";w["sha256"]=independent_hash(w["record"]);bad.append(inp)
        inp=source();inp["module2_input"]["matching_scale_GeV"]=170.;bad.append(inp)
        inp=source();inp["matching_scale_GeV"]=170.;bad.append(inp)
        inp=source();inp["module2_input"]["lepton_masses_GeV"][0]=True;bad.append(inp)
        inp=source();inp["module2_input"]["scalar"]["kind"]="module1_output";bad.append(inp)
        for value in (True,"300",[300]):
            inp=source();w=inp["module2_input"]["scalar"]
            w["record"]["physical"]["mH1"]=value;w["sha256"]=independent_hash(w["record"]);bad.append(inp)
        with patch("module6.coherent_pilot.scalar_evaluate") as scalar:
            for inp in bad:
                with self.subTest(inp=inp),self.assertRaises(ValueError):
                    pilot(inp,SOURCE_TOP_MS_160,LHA_SOURCE_SHA256)
            scalar.assert_not_called()

    def test_flavor_scale_mismatch_rejected_by_frozen_contract(self):
        fc={"mH1_GeV":300.,"mH2_GeV":700.,"beta_rad":1.394,"gamma_rad":1.089,
            "mt_MSbar_GeV":SOURCE_TOP_MS_160,"matching_scale_GeV":170.}
        with self.assertRaisesRegex(ValueError,"160 GeV"):run_contract(make_contract(fc))

    def test_fail_and_unknown_are_preserved_without_global_decision(self):
        scalar=fake_scalar(source()["module2_input"]["scalar"]["record"])
        scalar["status"]="SCALAR_PIPELINE_FAIL"
        scalar["gates"]["bfb"]={"assessment":"FAIL","status":"NEGATIVE_WITNESS"}
        with patch("module6.coherent_pilot.scalar_evaluate",return_value=scalar),patch(
                "module6.coherent_pilot.lfv_evaluate",side_effect=fake_lfv):
            out=pilot(source(),SOURCE_TOP_MS_160,LHA_SOURCE_SHA256)
        self.assertEqual(out["scalar"]["gates"]["bfb"]["assessment"],"FAIL")
        self.assertEqual(out["scalar"]["gates"]["vacuum"]["assessment"],"UNKNOWN")
        self.assertIsNone(out["global_zee_acceptance"])
        self.assertEqual(out["bsgamma"]["experiment_comparison"],"NOT_EVALUATED")

    def test_sector_hash_mismatch_rejected(self):
        bad=fake_lfv(source());bad["provenance"]["scalar"]["sha256"]="0"*64
        with patch("module6.coherent_pilot.scalar_evaluate",side_effect=fake_scalar),patch(
                "module6.coherent_pilot.lfv_evaluate",return_value=bad):
            with self.assertRaisesRegex(ValueError,"provenance mismatch"):
                pilot(source(),SOURCE_TOP_MS_160,LHA_SOURCE_SHA256)


class RealIntegrationTests(unittest.TestCase):
    def test_real_witness_and_independent_flavor_oracle(self):
        # Transparent capture calls REAL frozen code, including all vacuum starts.
        captured={}
        def capture(name,fn):
            def call(data):
                result=fn(data);captured[name]=copy.deepcopy(result);return result
            return call
        inp=source()
        with patch("module6.coherent_pilot.scalar_evaluate",side_effect=capture("scalar",real_scalar)),patch(
                "module6.coherent_pilot.neutrino_evaluate",side_effect=capture("neutrino",real_neutrino)),patch(
                "module6.coherent_pilot.lfv_evaluate",side_effect=capture("neutrino_lfv",real_lfv)):
            out=pilot(inp,SOURCE_TOP_MS_160,LHA_SOURCE_SHA256)
        bound=independent_hash(inp["module2_input"]["scalar"]["record"])
        self.assertEqual(bound,inp["module2_input"]["scalar"]["sha256"])
        self.assertEqual(out["scalar"]["input_sha256"],bound)
        for sector in captured:
            self.assertEqual(out[sector]["output_sha256"],independent_hash(captured[sector]))
        for sector in ("neutrino","neutrino_lfv"):
            self.assertEqual(out[sector]["provenance"]["scalar"]["sha256"],bound)
        self.assertEqual(out["neutrino_lfv"]["provenance"]["module2_output_sha256"],
                         out["neutrino"]["output_sha256"])
        self.assertEqual(out["neutrino_lfv"]["provenance"]["input_sha256"],independent_hash(inp))
        self.assertEqual(out["neutrino"]["provenance"]["input_sha256"],independent_hash(inp["module2_input"]))
        self.assertEqual(set(out["scalar"]["gates"]),{"reconstruction","bfb","unitarity","vacuum","ewpo"})
        self.assertEqual([r["attempts"] for r in out["scalar"]["gates"]["vacuum"]["runs"]],
                         [66,66,18,66,66,18])
        self.assertLess(out["neutrino"]["inverse_family_relative_residual"],2e-9)
        # Separate Decimal rational/log calculation; no production loop function.
        fc=out["bsgamma"]["matching_input"]
        self.assertEqual([fc[k] for k in ("mH1_GeV","mH2_GeV","beta_rad","gamma_rad")],
                         [300.,700.,1.394,1.089])
        flavor_input={k:v for k,v in fc.items() if k!="top_mass_input_definition"}
        self.assertEqual(out["bsgamma"]["source_input_sha256"],independent_hash(flavor_input))
        flavor_bytes=json.dumps(flavor_input,sort_keys=True,separators=(',', ':')).encode()
        contract=make_contract(flavor_input)
        contract["input_sha256"]=hashlib.sha256(flavor_bytes).hexdigest()
        self.assertEqual(out["bsgamma"]["output_sha256"],
                         independent_hash(run_contract(contract,source_input_bytes=flavor_bytes)))
        self.assertEqual(out["bsgamma"]["bound_scalar_sha256"],bound)
        with localcontext() as ctx:
            ctx.prec=60
            d7=[];d8=[]
            for mass,weight in ((300,math.cos(1.089)**2),(700,math.sin(1.089)**2)):
                x=(Decimal("163.96892236746697")/Decimal(mass))**2
                a=x-1;ln=x.ln();w=Decimal(str(weight));tb=Decimal(str(math.tan(1.394)))
                f71=x*(7-5*x-8*x*x)/(24*a**3)+x*x*(3*x-2)*ln/(4*a**4)
                f81=x*(2+5*x-x*x)/(8*a**3)-3*x*x*ln/(4*a**4)
                f72=x*(3-5*x)/(12*a*a)+x*(3*x-2)*ln/(6*a**3)
                f82=x*(3-x)/(4*a*a)-x*ln/(2*a**3)
                d7.append(w*(f71/(3*tb*tb)+f72));d8.append(w*(f81/(3*tb*tb)+f82))
            for key,values in (("C7",d7),("C8",d8)):
                self.assertAlmostEqual(out["bsgamma"]["delta_"+key],float(sum(values)),delta=2e-15)
                for actual,expected in zip(out["bsgamma"]["coefficients"][key]["per_state_real"],values):
                    self.assertAlmostEqual(actual,float(expected),delta=2e-15)
            rate=Decimal("3.54")-Decimal("8.51")*sum(d7)-Decimal("2.16")*sum(d8)
            self.assertAlmostEqual(out["bsgamma"]["linearized_value_in_1e_minus4"],float(rate),delta=2e-14)
        self.assertIsNone(out["global_zee_acceptance"])
        self.assertFalse(out["constraints_complete"])
        for row in out["neutrino_lfv"]["observables"].values():
            self.assertEqual(row["experimental_comparison"],"NOT_EVALUATED")

if __name__=="__main__":unittest.main()
