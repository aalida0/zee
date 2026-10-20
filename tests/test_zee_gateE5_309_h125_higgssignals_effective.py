"""Synthetic end-to-end E5 309 HiggsSignals effective-input regressions.

These validate model-input normalization, exact E4H tree-width closure,
HiggsTools interaction and 309-point accounting. Actual HiggsSignals
datasets and C++ bindings are tested separately in the AF user run.
"""
from __future__ import annotations
import json,math,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import zee_gateE5_309_h125_higgssignals_effective as m
from zee_gateD5_h125_direct_LFV_27 import h125_widths
from gateA1b_hierarchical_no_seed import ML


class FakeHiggsParticle:
 def __init__(self):
  self.width=0.
  self.decay={}
  self.mass=None
 def setMass(self,mass):self.mass=mass
 def totalWidth(self):return self.width
 def setDecayWidth(self,channel,partial):
  old=self.decay.get(channel,0.)
  self.decay[channel]=partial
  self.width+=partial-old
 def br(self,channel):return self.decay.get(channel,0.)/self.width

class FakePredictions:
 def __init__(self):self.h=None
 def addParticle(self,part):
  self.h=FakeHiggsParticle()
  return self.h

class FakeEff:
 pass

class FakeHP:
 Predictions=FakePredictions
 NeutralEffectiveCouplings=FakeEff
 smLikeEffCouplings=object()
 @staticmethod
 def BsmParticle(*args,**kwargs):return object()
 @staticmethod
 def effectiveCouplingInput(h,eff):
  h.width=0.004
  h.decay={"bb":0.002,"WW":0.0008,"ZZ":0.0004,
           "tautau":0.0002,"mumu":.00001,"gg":0.0002,
           "gamgam":.00001,"cc":.0001,"Zgam":.00001}

class FakeSignals:
 def __init__(self,datapath):self.path=datapath
 def observableCount(self):return 17
 def __call__(self,pred):
  h=pred.h
  return 70. + 100*abs(h.br("bb")-.5)

class FakeHS:
 Signals=FakeSignals


class E5Contracts(unittest.TestCase):
 def base(self,delta=0.,Y=None):
  if Y is None:Y=np.zeros((3,3),dtype=complex)
  beta=1.3
  p={"id":"B4_TEST","alpha":beta-delta,"beta":beta,
     "mh2":580.,"ma":635.,"mH1":300.,"mH2":700.,"gamma":1.11,
     "production_weighted_nonleptonic_cascade_upper_proxy":.55}
  payload={"real":Y.real.tolist(),"imag":Y.imag.tolist()}
  source={"candidate_id":"B4_TEST",
          "D2":{"chosen_optimized_source":{"solution":{
            "candidate_id":"B4_TEST","Y":payload}}},
          "selected_D4_extended_partial_LFV_score_NOT_EXCLUSION":.003}
  h=h125_widths(p,Y)
  reference={"candidate_id":"B4_TEST",
             "h125_tree_LFV_partial_widths_GeV":
                h["h125_LFV_partial_widths_GeV"],
             "worst_h125_direct_reference_ratio":.0002}
  return p,source,reference

 def test_exact_alignment_yukawa_ratios_are_sm_including_mu_tau(self):
  p,src,ref=self.base()
  x=m.model_couplings(p,src,ref)
  c=x["effective_couplings"]
  for key in ("WW","ZZ","tt","bb","ee","mumu","tautau"):
   self.assertAlmostEqual(c[key].real,1.,places=11)
  for k in ("ee","mumu","tautau"):
   self.assertAlmostEqual(c[k].imag,0.,places=13)
  self.assertEqual(x["alignment_delta_beta_minus_alpha"],0.)

 def test_nonzero_lepton_flavor_and_complex_diagonal_enter_eff_input(self):
  y=np.zeros((3,3),dtype=complex)
  y[0,1]=.01+.02j
  y[1,0]=.02-.01j
  y[2,2]=.003j
  p,src,ref=self.base(delta=.05,Y=y)
  result=m.model_couplings(p,src,ref)
  self.assertAlmostEqual(result["effective_couplings"]["WW"],math.cos(.05))
  self.assertNotAlmostEqual(result["effective_couplings"]["tautau"].imag,0.)
  self.assertGreater(result["h125_exact_LFV_GeV"]["h_to_e_mu"],0.)
  old=ref["h125_tree_LFV_partial_widths_GeV"]["h_to_e_mu"]
  new=result["h125_exact_LFV_GeV"]["h_to_e_mu"]
  self.assertAlmostEqual(old/new,1.)
  ref["h125_tree_LFV_partial_widths_GeV"]["h_to_e_mu"]*=2
  with self.assertRaisesRegex(ValueError,"recalculation mismatch"):
   m.model_couplings(p,src,ref)

 def test_HiggsTools_total_width_exactly_recomputed_with_offdiagonal_modes(self):
  p,src,ref=self.base(delta=.05,
        Y=np.array([[0,.01,0],[.01,0,0],[0,0,0]],complex))
  package=m.model_couplings(p,src,ref)
  pred,h,initial,total=m.build_predictions(FakeHP,package)
  self.assertAlmostEqual(initial,.004)
  self.assertAlmostEqual(total,initial+sum(package[
      "h125_exact_LFV_GeV"].values()))
  self.assertLessEqual(h.br("bb"),.5)
  row=m.analyze_one(FakeSignals("dummy"),FakeHP,package,70.)
  self.assertTrue(math.isfinite(row["h125_effective_HiggsSignals_chi2"]))
  self.assertIsNone(row["full_Zee_physical_allowed_or_excluded"])

 def test_sm_HiggsSignals_reference_same_dataset_and_mass(self):
  signals,chi,nobs=m.sm_baseline(FakeHP,FakeHS,Path("dummy"))
  self.assertEqual(nobs,17)
  self.assertAlmostEqual(chi,70.)

 def test_empty_HS_dataset_refused_without_fabricating_chi2(self):
  with tempfile.TemporaryDirectory() as td:
   with self.assertRaisesRegex(ValueError,"No HiggsSignals"):
    m.dataset_provenance(td)
   (Path(td)/"one.json").write_text('{"some":"measurement"}')
   proof=m.dataset_provenance(td)
   self.assertEqual(proof["file_count"],1)
   self.assertEqual(len(proof["dataset_sha256_manifest"]),64)

 def test_309_partial_chi2_not_arbitrary_experimental_exclusion(self):
  p,src,ref=self.base()
  pkg=m.model_couplings(p,src,ref)
  signals=FakeSignals("dummy")
  template=m.analyze_one(signals,FakeHP,pkg,70.)
  with tempfile.TemporaryDirectory() as td:
   packs,rows={},{}
   for idx in range(309):
    key=f"B4_{idx:05d}"
    packs[key]={**pkg,"candidate_id":key}
    rows[key]={**template,"candidate_id":key}
   report=m.finish(Path(td),packs,rows,{"TEST_ONLY":True},70.,17)
   self.assertEqual(report["HiggsSignals_chi2_evaluated_in_effective_coupling_approx"],309)
   self.assertIsNone(report["full_model_allowed_points"])
   self.assertTrue(report["charged_Zee_scalar_loop_amplitudes_missing"])
   self.assertTrue((Path(td)/
       "E5_309_ranked_conditional_h125_HiggsSignals_NOT_ALLOWED.csv").exists())
   with self.assertRaisesRegex(ValueError,"incomplete"):
    m.finish(Path(td),packs,{k:v for k,v in rows.items()
                               if k!="B4_00000"},{"TEST":True},70.,17)

 def test_fails_closed_on_duplicate_checkpoint_or_physical_label(self):
  with tempfile.TemporaryDirectory() as td:
   path=Path(td)/"ck.jsonl"
   row={"candidate_id":"B4_TEST","h125_effective_HiggsSignals_chi2":3.,
        "full_Zee_physical_allowed_or_excluded":None}
   path.write_text(json.dumps(row)+"\n")
   self.assertEqual(len(m.checkpoint(path,{"B4_TEST"})),1)
   path.write_text(json.dumps(row)+"\n"+json.dumps(row)+"\n")
   with self.assertRaisesRegex(ValueError,"Corrupted"):
    m.checkpoint(path,{"B4_TEST"})
   path.write_text(json.dumps({**row,"full_Zee_physical_allowed_or_excluded":True})+"\n")
   with self.assertRaisesRegex(ValueError,"Corrupted"):
    m.checkpoint(path,{"B4_TEST"})

if __name__=="__main__":unittest.main()
