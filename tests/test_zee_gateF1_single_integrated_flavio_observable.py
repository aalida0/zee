"""One large F1 integration regression: synthetic observable interface ONLY.

Tests source-derived 27 mixed-spectrum paths, 18 single-Type-II mass/tanbeta
controls, all 24 E4A operator/order identities per spectrum, the published
2015 C7/C8 response derivative, SM normalization, charged endpoints,
quadratic-interference consistency, current experiment diagnostic labels and
rejection of deliberately corrupted normalization or Wilson signs.

The actual F1 command executes REAL flavio/wilson and E4A AF output.
Passing a simulated test does NOT validate a physical branching ratio.
"""
import math
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import zee_gateF1_peerreviewed_flavio_27_observable as f

class FakeFlavioEngine:
    flavio_version="fixture_only_not_external_flavio"
    wilson_version="fixture_only_not_external_wilson"
    def __init__(self):
        self.calls=0
    def prediction(self,c7,c8):
        self.calls+=1
        return f.SM_2015 -8.22e-4*c7 -1.99e-4*c8 + (
             1.2e-4*c7*c7+0.8e-4*c8*c8+0.15e-4*c7*c8)

def synthetic_source():
    models=[];by={}
    for i in range(27):
        label=f"B4_{i:07d}"
        m1=240.+7*i;m2=680.+11*i;tan=5.6+0.01*i
        g=1.05+0.008*i
        models.append({"candidate_id":label,"mH1_GeV":m1,
                       "mH2_GeV":m2,"tanbeta":tan,"gamma":g})
        by[label]={}
        c=math.cos(g)**2;s=math.sin(g)**2
        for order in range(3):
            for n in range(1,9):
                sm=(-.205 if n==7 else -.103)
                a=(-.05 if n==7 else -.022 if n==8 else .0005)/(
                    1+m1/600.)/(order+1)
                b=(-.05 if n==7 else -.022 if n==8 else .0005)/(
                    1+m2/600.)/(order+1)
                by[label][order,f"C{n}"]=[sm,a,b,sm+c*a+s*b]
    typeii=[]
    for tan in (5.6,50.):
        for mass in (300.,450.,550.,600.,650.,670.,700.,800.,1000.):
            typeii.append({
                "mH_GeV":mass,"tanbeta":tan,
                "LO_C7":-.050/(1+mass/600.),
                "LO_C8":-.022/(1+mass/600.),
                "three_gamma_endpoints_checked":True})
    return {"pure_TypeII_18_results":typeii},models,by

class TestF1SingleIntegratedPeerReviewedObservable(unittest.TestCase):
    def test_one_27_zee_18_typeII_end_to_end_and_corruption_rejection(self):
        source=synthetic_source()
        engine=FakeFlavioEngine()
        with patch.object(f,"read_source_e4a",return_value=source),patch.object(
            f,"sha",return_value="synthetic_source_not_physics"):
            report=f.real_run(engine,Path("/fixture/e4a.json"))
        self.assertEqual(report["status"],f.STATUS)
        self.assertEqual(len(report["Zee_27_results"]),27)
        self.assertEqual(len(report["TypeII_18_results"]),18)
        self.assertEqual(report["summary"]["TypeII_controls"],18)
        self.assertEqual(report["summary"]["Zee_models"],27)
        self.assertEqual(engine.calls,5+18+4*27)
        self.assertTrue(report["C7_C8_2015_derivative_validation"][
            "both_operator_derivative_sign_and_scale_consistent"])
        self.assertFalse(report["summary"][
            "published_2017_580GeV_TypeII_95CL_reproduced"])
        self.assertIsNone(report["Zee_allowed_or_excluded"])
        self.assertTrue(all(z["Zee_physically_allowed"] is None
                            for z in report["Zee_27_results"]))
        self.assertTrue(all(z["flavio_hybrid_BR"]>f.SM_2015
                            for z in report["Zee_27_results"]))
        # This is NOT the 2017 NNLO curve reproduction: only the
        # source-pinned LO matching and same historical observable are tested.
        self.assertEqual(report["accuracy"],f.NO_FULL_NNLO)
        # Reject mismatched E4A pure-reference collection.
        bad=dict(source[0]);bad["pure_TypeII_18_results"]=source[0][
            "pure_TypeII_18_results"][:-1]
        with self.assertRaisesRegex(ValueError,"TypeII"):
            f.validate_e4a_typeii(bad)

        # Flip the effective-basis response sign on purpose.
        class WrongWilsonConvention(FakeFlavioEngine):
            def prediction(self,c7,c8):
                self.calls+=1
                return f.SM_2015+8.22e-4*c7-1.99e-4*c8
        badengine=WrongWilsonConvention()
        sm=f.no_np_test(badengine)["flavio_SM"]
        self.assertFalse(f.basis_derivative_test(badengine,sm)[
            "both_operator_derivative_sign_and_scale_consistent"])
        # Reject source coefficients corrupted AFTER source-provenance checks.
        corrupt={name:dict(vals) for name,vals in source[2].items()}
        entry=dict(corrupt["B4_0000000"])
        val=list(entry[0,"C7"]);val[3]+=0.0004
        entry[0,"C7"]=val
        corrupt["B4_0000000"]=entry
        with self.assertRaisesRegex(ValueError,"vector mismatch"):
            f.evaluate_zee(FakeFlavioEngine(),source[1],corrupt)

if __name__=="__main__":
    unittest.main()
