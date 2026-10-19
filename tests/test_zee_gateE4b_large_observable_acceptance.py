"""ONE large end-to-end E4B OBSERVABLE protocol acceptance test.

This test's invented toy NNLO responses check only the *interface* and
fail-closed logic, NOT the publication's NNLO calculation or 670-GeV
physics result. No mock response counts as an author numerical source.

In one test: 27 real-format Zee x24 coefficients, genuine SM control,
>=6 independently specified fixture Type-II numerical anchors,
15 mass-limit decisions, 27 x 2 pure two-state checks, 27 genuine
two-state coherent NP^2 toy terms. Inject wrong SM/holdout/95CL/basis
responses to verify fail-closed. The unavailable real external
source still blocks the physical pipeline.
"""
from pathlib import Path
import sys
import math
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))

from zee_gateE4b_2026_observable_validation import (
    BACKEND_PROTOCOL,BLOCKED,ECUT,MU0,SM_REF,SM_SIGMA,
    typeii_calibration,zee_predictions,load_manifest,
    read_source_e4a,prediction
)

def coef(m):
    return -.085/(1+m/600.)
def math_br(delta):
    return SM_REF-3.5e-4*delta+5.e-5*delta*delta

def standalone(m):
    return math_br(coef(m))

def record(action, **kw):
    return {"action":action,"protocol":BACKEND_PROTOCOL,
            "scientific_precision_level":"FULL_2026_NNLO",**kw}

def pred(action,br):
    return record(action,BR=br,sigma_theory=SM_SIGMA,
                  fully_correlated_with_SM_nuisances=True)

class TestE4BOneLargeObservableProtocol(unittest.TestCase):
    def test_full_27_x_24_matching_typeII_curve_limit_and_fail_closed(self):
        model=[]
        arrays={}
        for n in range(27):
            key=f"B4_{n:07d}"
            m1,m2=200.+10*n,700.+8*n
            gamma=1.10+.002*n
            model.append({"candidate_id":key,"mH1_GeV":m1,
                          "mH2_GeV":m2,"gamma":gamma,"tanbeta":5.6})
            rows={}
            w1,w2=math.cos(gamma)**2,math.sin(gamma)**2
            for order in range(3):
                for op in range(1,9):
                    sm=-.2 if op==7 else -.11
                    a=coef(m1) if op==7 and order==0 else 0.
                    b=coef(m2) if op==7 and order==0 else 0.
                    rows[order,f"C{op}"]=[sm,a,b,sm+w1*a+w2*b]
            arrays[key]=rows
        mass_inputs=(550.,650.,670.,700.,800.,1000.)
        # Fixture only; these are NOT source-published 2026 authors' rates.
        reference={
            "independent_from_tested_backend":True,
            "source_reference":"arxiv:2608.29863",
            "confidence_procedure":"TEST_ONLY_95CL",
            "pure_typeII_numerical_reference":[
                {"mass_GeV":m,"tanbeta":50.,"BR":standalone(m)}
                for m in mass_inputs]}
        calls=[]
        def backend(action,payload):
            calls.append(action)
            if action=="describe":
                return record(action,validated_capabilities=[
                    "SM_2026_NNLO","TypeII_2026_NNLO",
                    "Zee_two_mixed_charged_from_raw_3order",
                    "source_approved_A1M_basis_map","correlated_95CL"])
            if action=="predict_sm":
                return pred(action,SM_REF)
            if action=="predict_typeii":
                return pred(action,standalone(payload["mass_GeV"]))
            if action=="typeii_excluded_95":
                return record(action,excluded_95=payload["mass_GeV"]<=670.,
                              confidence_procedure="TEST_ONLY_95CL")
            if action=="predict_twocharged_from_raw_superiso":
                gamma=payload["gamma"]
                w1,w2=math.cos(gamma)**2,math.sin(gamma)**2
                d={z["operator"]:z for z in payload["coefficient_rows"]
                   if z["order"]==0}
                delta=w1*d["C7"]["NP_light"]+w2*d["C7"]["NP_heavy"]
                return pred(action,math_br(delta))
            raise ValueError("Unexpected action")
        calibration=typeii_calibration(backend,reference)
        self.assertTrue(calibration[
            "TypeII_published_670_limit_independently_reproduced"])
        self.assertEqual(len(calibration["independent_author_holdouts"]),6)
        self.assertEqual(calibration["last_excluded_mass_GeV"],670.)
        points=zee_predictions(backend,model,arrays)
        self.assertEqual(len(points),27)
        self.assertTrue(all(z["source_pure_state_consistency_checked"]
                            for z in points))
        self.assertTrue(all(z["Zee_full_global_model_allowed"]=="UNKNOWN"
                            for z in points))
        self.assertEqual(len([c for c in calls if c=="predict_twocharged_from_raw_superiso"]),81)

        # All three independent blockers tested against the full cohort.
        def wrong_SM(action,payload):
            z=backend(action,payload)
            if action=="predict_sm":
                z=dict(z,BR=z["BR"]+1.e-5)
            return z
        with self.assertRaisesRegex(ValueError,"SM reference"):
            typeii_calibration(wrong_SM,reference)

        wrong_author=dict(reference)
        wrong_author["pure_typeII_numerical_reference"]=[
            dict(z) for z in reference["pure_typeII_numerical_reference"]]
        wrong_author["pure_typeII_numerical_reference"][0]["BR"]+=2.e-5
        with self.assertRaisesRegex(ValueError,"Type-II BR curve mismatch"):
            typeii_calibration(backend,wrong_author)

        def wrong_limit(action,payload):
            z=backend(action,payload)
            if action=="typeii_excluded_95":
                z=dict(z,excluded_95=payload["mass_GeV"]<=550.)
            return z
        with self.assertRaisesRegex(ValueError,"670 GeV Type-II"):
            typeii_calibration(wrong_limit,reference)

        def wrong_basis(action,payload):
            z=backend(action,payload)
            if (action=="predict_twocharged_from_raw_superiso"
                    and payload["gamma"]==0.):
                z=dict(z,BR=z["BR"]+2.e-5)
            return z
        with self.assertRaisesRegex(ValueError,"pure Type-II observable nonclosure"):
            zee_predictions(wrong_basis,model,arrays)

        with self.assertRaisesRegex(ValueError,"correlated"):
            prediction(pred("predict_sm",3.54e-4) |
                       {"fully_correlated_with_SM_nuisances":False})
        self.assertIn("BLOCKED",BLOCKED)

if __name__=="__main__":
    unittest.main()
