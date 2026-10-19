"""One F2 full-cohort structure test; physics engines mocked, NOT calibrated.

Tests 27 genuine-shaped E4A source records, 18 pinned Type-II control
definitions extended to dense ~32 mass grid, 54 Zee LO/NLO rows and
EOS vs flavio NP-delta comparison + deliberate F1 mismatch and
unexpected source C1. Actual engine acceptance requires AF test below.
"""
import json
import math
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import zee_gateF2_eos_flavio_nlo_27_validation as f

class ToyEnginesNotPhysics:
    alpha160=0.108
    as4pi=alpha160/(4*math.pi)
    flavio_version="TOY"
    wilson_version="TOY"
    eos_version="TOY"
    flavio_sm=3.36e-4
    eos_sm=3.2e-4
    def prepare(self):
        return {"TOY":True}
    def evaluate(self,high):
        # EOS response is deliberately not equivalent to flavio rate
        # but its DeltaBR is similar enough for a diagnostic test.
        c7=high.get(7,0.)
        c8=high.get(8,0.)
        c4=high.get(4,0.)
        d=-8.2e-4*c7-2.0e-4*c8-0.5e-4*c4+0.65e-4*c7*c7
        de=0.93*d
        return {"flavio_BR":self.flavio_sm+d,
                "eos_NLO_BR":self.eos_sm+de,
                "flavio_delta_BR":d,
                "eos_NLO_delta_BR":de,
                "EOS_low_scale_delta_C7":c7,
                "EOS_low_scale_delta_C8":c8,
                "EOS_low_scale_delta_C4":c4}

def fixture():
    models=[]; rows={}; existing=[]
    rate=ToyEnginesNotPhysics()
    for i in range(27):
        name=f"B4_{318+i:07d}"
        g=0.91+i*.01
        m1=260.+i*4.;m2=680.+i*10.;t=5.6+.01*i
        models.append(dict(candidate_id=name,gamma=g,mH1_GeV=m1,
                           mH2_GeV=m2,tanbeta=t))
        block={}
        for order in range(3):
            for op in range(1,9):
                if op==7:a,b=(-0.055/(1+m1/600.),-0.055/(1+m2/600.))
                elif op==8:a,b=(-0.025/(1+m1/600.),-0.025/(1+m2/600.))
                elif op==4:a,b=(-0.008/(1+m1/600.),-0.008/(1+m2/600.))
                else:a=b=0.
                if order==0 and op==4:a=b=0.
                if order==2:a=b=0.
                block[order,f"C{op}"]=[0.,a/(order+1),b/(order+1),
                                      math.cos(g)**2*a/(order+1)+
                                      math.sin(g)**2*b/(order+1)]
        rows[name]=block
        mat=f.model_coeffs(rows,name)
        br=rate.evaluate(f.from_e4a_source(
            mat,math.cos(g)**2,"LO",rate.as4pi))["flavio_BR"]
        existing.append({"candidate_id":name,"flavio_hybrid_BR":br})
    typeii={}
    for t in f.TANBETA_VALUES:
        for m in f.DENSE_MASS:
            typeii[m,t]={(order,n):(
                (-.055/(1+m/600.) if n==7 else
                 -.025/(1+m/600.) if n==8 else
                 -.008/(1+m/600.) if n==4 and order==1 else 0.)/(order+1),
                (-.055/(1+m/600.) if n==7 else
                 -.025/(1+m/600.) if n==8 else
                 -.008/(1+m/600.) if n==4 and order==1 else 0.)/(order+1))
                for order in range(3) for n in range(1,9)}
    return ({"status":"source_proxy"},models,rows),typeii,existing

class TestF2OneLargeRealWorkflowContract(unittest.TestCase):
    @patch("builtins.print")  # Never display synthetic F2_ZEE as real AF physics
    def test_27_zee_dense_typeii_and_fail_closed_injections(self, _unused_print):
        e4a,typeii,rows=fixture()
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"f1.json"
            def make_f1(zee):
                path.write_text(json.dumps({
                    "source_e4a_summary_sha256":"fixture sha",
                    "summary":{"Zee_models":27,"TypeII_controls":18},
                    "Zee_allowed_or_excluded":None,
                    "Zee_27_results":zee,
                }))
            make_f1(rows)
            with patch.object(f,"read_source_e4a",return_value=e4a),patch.object(
                f,"sha",return_value="fixture sha"),patch.object(
                f,"typeii_controls",return_value=typeii):
                report=f.run(ToyEnginesNotPhysics(),Path(d)/"e4a.json",
                             path,Path(d)/"probe")
                self.assertEqual(report["status"],f.SUCCESS)
                self.assertEqual(len(report["Zee_27_by_matching_order"]),54)
                self.assertEqual(len(report["TypeII_dense_by_matching_order"]),
                                 4*len(f.DENSE_MASS))
                self.assertTrue(report["summary"][
                    "F1_27_real_flavio_predictions_reproduced"])
                self.assertIsNone(report["Zee_physical_allowed_or_excluded"])
                self.assertFalse(report["summary"]["publishable_Zee_95CL_exclusions"])
                # Optional original E1 legacy SuperIso comparison must
                # carry the independently source-locked E4A ancestry.
                legacy_path=Path(d)/"e1.json"
                e4a[0]["fingerprints_sha256"]={"E1":"fixture sha"}
                legacy_path.write_text(json.dumps({
                    "tested":27,"rows":[{
                        "candidate_id":r["candidate_id"],
                        "B_to_Xs_gamma_legacy_Zee_BR":4.0e-4}
                        for r in rows]}))
                with_legacy=f.run(ToyEnginesNotPhysics(),
                                  Path(d)/"e4a.json",path,Path(d)/"probe",
                                  legacy_path)
                self.assertTrue(with_legacy["summary"][
                    "separate_legacy_E1_27_comparison_included"])
                self.assertTrue(all(x[
                    "legacy_SuperIso_BR_separate_scheme"]==4.0e-4
                    for x in with_legacy["Zee_27_by_matching_order"]))
                corrupted=list(rows)
                corrupted[0]=dict(corrupted[0])
                corrupted[0]["flavio_hybrid_BR"]+=2e-5
                make_f1(corrupted)
                with self.assertRaisesRegex(ValueError,"nonreproduction"):
                    f.run(ToyEnginesNotPhysics(),Path(d)/"e4a.json",
                          path,Path(d)/"probe")
                a=f.model_coeffs(e4a[2],e4a[1][0]["candidate_id"])
                a[1,1]=(-2.,0.)
                with self.assertRaisesRegex(ValueError,"unexpected NLO C1"):
                    f.from_e4a_source(a,.2,"NLO_matching",.009)

if __name__=="__main__":
    unittest.main()
