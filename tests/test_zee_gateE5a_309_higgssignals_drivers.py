"""E5A synthetic regression: 309 E5 HiggsSignals re-evaluation and drivers.

No fixture is a physical Zee exclusion or experimentally certified HS fit.
"""
from __future__ import annotations
import json,math,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import zee_gateE5a_309_higgssignals_drivers as a


class Fakes:
    class Pred:
        def __init__(self):self.name=None
        def addParticle(self,p):
            self.h=Fakes.Particle()
            return self.h
    class Particle:
        def __init__(self):
            self.eff={}
            self.width=.004
            self.d={}
        def setMass(self,x):self.mass=x
        def setDecayWidth(self,ch,x):
            original=self.d.get(ch,0.)
            self.width+=x-original
            self.d[ch]=x
        def totalWidth(self):return self.width
        def br(self,ch):return self.d.get(ch,0.)/self.width
    class Ec:pass
    class HP:
        Predictions=None
        NeutralEffectiveCouplings=None
        smLikeEffCouplings=None
        @staticmethod
        def BsmParticle(*args,**kwargs):return object()
        @staticmethod
        def effectiveCouplingInput(h,c):
            h.eff={k:getattr(c,k,1.) for k in (
               "bb","tt","tautau","WW","ZZ")}
            h.width=.004
            h.d={"bb":0.001,"WW":0.0008,"ZZ":0.0004,
                 "tautau":0.0002,"mumu":0.00001,"gg":0.0003,
                 "gamgam":.0001}
    class Signals:
        def __call__(self,p):
            c=p.h.eff
            return (100+20*(complex(c["bb"]).real-1)**2+
                   3*(complex(c["tautau"]).real-1)**2+
                   (float(c["WW"])-1)**2)
    class Measurement:
        def __init__(self,i):self.i=i
        def __call__(self,p):return 10+(self.i+1)*(p.h.eff["bb"].real-1)**2
        def id(self):return self.i
        def reference(self):return "TEST REF"
        def loadedFrom(self):return "synthetic.json"


Fakes.HP.Predictions=Fakes.Pred
Fakes.HP.NeutralEffectiveCouplings=Fakes.Ec
Fakes.HP.smLikeEffCouplings=Fakes.Ec()


class TestE5A(unittest.TestCase):
    def package(self):
        c={
           "uu":1+0j,"dd":.6+0j,"cc":1+0j,"ss":.6+0j,
           "tt":1+0j,"bb":.6+0j,
           "ee":1+0j,"mumu":1+0j,"tautau":.7+0j,
           "WW":.99,"ZZ":.99,"gg":1.,"gamgam":1.,"Zgam":1.,"lam":1.}
        return {"candidate_id":"B4_TEST","effective_couplings":c,
                "h125_exact_LFV_GeV":{
                   "h_to_e_mu":0.,"h_to_e_tau":0.,"h_to_mu_tau":0.},
                "alignment_delta_beta_minus_alpha":.14,
                "cascade_proxy_not_xsec":.7}

    def test_sector_restoration_retains_other_couplings_and_input(self):
        old=self.package()
        bottom=a.do_sector(old,a.SECTORS["bottom_down_strange_to_SM"])
        self.assertEqual(bottom["effective_couplings"]["bb"],1+0j)
        self.assertEqual(bottom["effective_couplings"]["tautau"],.7+0j)
        self.assertEqual(old["effective_couplings"]["bb"],.6+0j)
        self.assertEqual(a.do_sector(old,a.SECTORS["VV_to_SM"])["effective_couplings"]["WW"],1.)

    def test_actual_original_chisq_must_reproduce_before_ablation(self):
        model=self.package()
        s=Fakes.Signals()
        old=s(a.e5.build_predictions(Fakes.HP,model)[0])
        ref={
            "h125_effective_HiggsSignals_chi2":old,
            "delta_chi2_vs_SM_same_dataset_NOT_calibrated_CL":old-100.,
            "h125_total_width_with_h_LFV_GeV":.004}
        row=a.compute(s,Fakes.HP,model,ref,100.)
        self.assertAlmostEqual(row["chi2_exactly_reproduced"],old)
        self.assertEqual(set(row["counterfactuals_NOT_physical_Zee_models"]),set(a.SECTORS))
        self.assertLess(row["counterfactuals_NOT_physical_Zee_models"][
          "bottom_down_strange_to_SM"]["chisq_shift_relative_to_original"],0)
        self.assertIsNone(row["fully_allowed_or_excluded_Zee"])
        with self.assertRaisesRegex(ValueError,"Original E5"):
            a.compute(s,Fakes.HP,model,{**ref,"h125_effective_HiggsSignals_chi2":old+1},100.)

    def test_full_309_ledger_summary_never_assigns_physical_CL(self):
        model=self.package()
        s=Fakes.Signals()
        old=s(a.e5.build_predictions(Fakes.HP,model)[0])
        ref={"h125_effective_HiggsSignals_chi2":old,
             "delta_chi2_vs_SM_same_dataset_NOT_calibrated_CL":old-100.,
             "h125_total_width_with_h_LFV_GeV":.004}
        base=a.compute(s,Fakes.HP,model,ref,100.)
        cohort={f"B4_{i:07d}":{**base,"candidate_id":f"B4_{i:07d}"}
                for i in range(309)}
        with tempfile.TemporaryDirectory() as tmp:
            manifest={"source_cohort_ids":sorted(cohort),
                      "source_E5_provenance":{"synthetic":True}}
            summary=a.finalize(Path(tmp),cohort,{},manifest,100.,159)
            self.assertIsNone(
                summary["pearson_approx_chisq_vs_abs_bottom_deviation"])
            self.assertFalse(
                summary["pearson_approx_chisq_vs_abs_bottom_deviation_defined"])
            self.assertIsNone(
                json.loads((Path(tmp)/"summary.json").read_text())[
                    "pearson_approx_chisq_vs_abs_bottom_deviation"])
            self.assertEqual(summary["models"],309)
            self.assertIsNone(summary["full_Zee_allowed_or_excluded"])
            self.assertTrue((Path(tmp)/"E5A_309_ranked_drivers_NOT_ALLOWED.csv").exists())
            with self.assertRaisesRegex(ValueError,"incomplete"):
                a.finalize(Path(tmp),dict(list(cohort.items())[:-1]),{},manifest,100.,159)

    def test_nonconstant_309_cohort_gives_finite_pearson(self):
        model=self.package()
        s=Fakes.Signals()
        old=s(a.e5.build_predictions(Fakes.HP,model)[0])
        ref={"h125_effective_HiggsSignals_chi2":old,
             "delta_chi2_vs_SM_same_dataset_NOT_calibrated_CL":old-100.,
             "h125_total_width_with_h_LFV_GeV":.004}
        base=a.compute(s,Fakes.HP,model,ref,100.)
        rows={}
        for i in range(309):
            tag=f"B4_{i:07d}"
            # Synthetic nondegenerate collection, strictly a summary test.
            rows[tag]={**base, "candidate_id":tag,
                       "delta_chi2_vs_fixed_SM":i*.25,
                       "kappaBottom":0.5 + i/1000.}
        with tempfile.TemporaryDirectory() as tmp:
            manifest={"source_cohort_ids":sorted(rows)}
            summary=a.finalize(Path(tmp),rows,{},manifest,100.,159)
            self.assertTrue(summary[
                "pearson_approx_chisq_vs_abs_bottom_deviation_defined"])
            self.assertTrue(math.isfinite(summary[
                "pearson_approx_chisq_vs_abs_bottom_deviation"]))
            self.assertIsNone(summary["full_Zee_allowed_or_excluded"])

    def test_checkpoint_rejects_duplicate_and_exclusion(self):
        actual=Fakes.Signals()(a.e5.build_predictions(Fakes.HP,self.package())[0])
        row=a.compute(Fakes.Signals(),Fakes.HP,self.package(),{
              "h125_effective_HiggsSignals_chi2":actual,
              "delta_chi2_vs_SM_same_dataset_NOT_calibrated_CL":actual-100.,
              "h125_total_width_with_h_LFV_GeV":.004},100.)
        with tempfile.TemporaryDirectory() as tmp:
            ck=Path(tmp)/"cp.jsonl"
            ck.write_text(json.dumps(row)+"\n")
            self.assertEqual(len(a.checkpoint_read(ck,{"B4_TEST"})),1)
            ck.write_text(json.dumps(row)+"\n"+json.dumps(row)+"\n")
            with self.assertRaisesRegex(ValueError,"duplicate"):
                a.checkpoint_read(ck,{"B4_TEST"})
            ck.write_text(json.dumps({**row,"fully_allowed_or_excluded_Zee":True})+"\n")
            with self.assertRaisesRegex(ValueError,"corruption"):
                a.checkpoint_read(ck,{"B4_TEST"})

    def test_per_measurement_internal_correlation_calls_are_not_summed_as_global(self):
        model=self.package()
        class Signals:
            def measurements(self):
                return [Fakes.Measurement(101),Fakes.Measurement(202)]
        fakepack={"B4_TEST":model}
        result={"B4_TEST":{"delta_chi2_vs_fixed_SM":3.47}}
        result,nb=a.measurements_summary(
            Signals(),Fakes.HP,fakepack,result,max_each=1)
        self.assertEqual(nb,2)
        self.assertEqual(len(result["B4_TEST"]["leading_12_measurements_by_absolute_delta"]),2)


if __name__=="__main__":
    unittest.main()
