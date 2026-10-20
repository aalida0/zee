"""E6 charged scalar gauge/Higgs cubic and two-eigenstate diphoton tests.

Numerical source checks run WITHOUT HiggsTools. An installed HiggsTools
E6/SM-reference closure is checked by the runner against real saved E5 rows.
"""
from __future__ import annotations
import json,math,sys,tempfile,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import zee_gateE6_309_charged_gamma_higgssignals as x
import zee_gateE6_zgamma_mixed_PV as zpv


class FakeH:
 def __init__(self):
  self.mass=0.
  self.width=0.
  self.w={}
 def setMass(self,m):self.mass=m
 def totalWidth(self):return self.width
 def setDecayWidth(self,k,val):
  self.width+=val-self.w.get(k,0.)
  self.w[k]=val
 def br(self,k):return self.w.get(k,0.)/self.width

class FakeP:
 def addParticle(self,*args,**kwargs):
  self.h=FakeH()
  return self.h

class FakeEff:pass
class FakeHP:
 Predictions=FakeP
 NeutralEffectiveCouplings=FakeEff
 @staticmethod
 def BsmParticle(*args,**kwargs):return object()
 @staticmethod
 def effectiveCouplingInput(h,ec):
  h.width=.004
  h.w={"gamgam":.00001,"bb":.002,"WW":.0007,
       "ZZ":.0003,"gg":.0002,"tautau":.0002,
       "mumu":.00001,"cc":.0001,"Zgam":.00001}

class FakeSignals:
 def __call__(self,pred):
  return 153. + 8e4*(pred.h.br("gamgam")-.0025)**2


class E6Unit(unittest.TestCase):
 def scalar(self):
  return {
   "alpha":1.398,"beta":1.394,"gamma":1.089,"m12sq":57700.,
   "mH1":300.,"mH2":700.,"mh2":580.7,"ma":633.7,
   "lc":4.473,"k1":1.082,"k2":.00398,"k12":-.001266}
 def pak(self):
  s=self.scalar()
  c={"uu":1+0j,"dd":1+0j,"cc":1+0j,"ss":1+0j,
     "tt":1+0j,"bb":1+0j,"ee":1+0j,"mumu":1+0j,
     "tautau":1+0j,"WW":1.,"ZZ":1.,
     "gg":1.,"gamgam":1.,"Zgam":1.,"lam":1.}
  return {"candidate_id":"B4_TEST","effective_couplings":c,
          "scalar":s,"cascade_proxy_not_xsec":.65,
          "h125_exact_LFV_GeV":{
           "h_to_e_mu":0.,"h_to_e_tau":0.,"h_to_mu_tau":0.}}

 def test_independent_3x3_gauge_vs_higgs_basis_H1_H2_cubics(self):
  G=x.hcharged_trilinears(self.scalar())
  self.assertLess(G["hessian_Higgs_basis_max_abs_residual_GeV"],1e-4)
  self.assertLess(G["mass_eigensystem_max_abs_residual_GeV2"],1e-6)
  self.assertTrue(G["offdiagonal_Z_H1_H2_nonzero"])
  self.assertNotAlmostEqual(G["g_h_H1plus_H2minus_GeV"],0.)
  self.assertAlmostEqual(G["g_h_H1plus_H1minus_GeV"],-397.48554434,places=5)
  self.assertAlmostEqual(G["g_h_H2plus_H2minus_GeV"],1073.50939332,places=5)
  self.assertAlmostEqual(G["g_h_H1plus_H2minus_GeV"],110.51063744,places=5)

 def test_independent_near_alignment_mu_and_charged_singlet_rotation(self):
  for offset in (0.,.002,-.075,.13):
   for gamma in (.11,.6,1.22):
    p={**self.scalar(),
       "alpha":self.scalar()["beta"]+offset,
       "gamma":gamma}
    # Arbitrary scalar input can fail scalar BFB; trilinear algebraic
    # closure is still exact before applying physical theory constraints.
    G=x.hcharged_trilinears(p)
    self.assertLess(G["hessian_Higgs_basis_max_abs_residual_GeV"],1e-4)
    self.assertLess(G["mass_eigensystem_max_abs_residual_GeV2"],1e-6)

 def test_scalar_loop_heavy_mass_decoupling_and_sign(self):
  self.assertAlmostEqual(x.a_scalar(.00001).real,1./3.,places=5)
  self.assertAlmostEqual(x.a_scalar(.02).imag,0.,places=13)
  self.assertGreater(x.a_scalar(.02).real,1./3.)
  self.assertAlmostEqual(x.a_fermion(.0001).real,4./3.,places=4)
  self.assertAlmostEqual(x.a_vector(.0001).real,-7.,places=3)
  pack=self.pak()
  G=x.hcharged_trilinears(self.scalar())
  r=x.gamma_ratio(pack,G)
  self.assertGreater(r[
   "new_over_old_h_gamma_gamma_partial_width_LO_amplitude_ratio"],0.)
  for k in ("H1_charged_scalar_LO_amplitude",
            "H2_charged_scalar_LO_amplitude"):
   self.assertAlmostEqual(r[k][1],0.,places=13)
  both=x.gamma_ratio(pack,{
    **G,"g_h_H1plus_H1minus_GeV":0.,"g_h_H2plus_H2minus_GeV":0.})
  self.assertAlmostEqual(
    both["new_over_old_h_gamma_gamma_partial_width_LO_amplitude_ratio"],1.)

 def test_scalar_gamma_offdiagonal_zero_with_photon_current(self):
  pack=self.pak()
  G=x.hcharged_trilinears(pack["scalar"])
  # h12 cannot close a loop with 2 diagonal photon vertices.
  orig=x.gamma_ratio(pack,G)
  changed=x.gamma_ratio(pack,{
    **G,"g_h_H1plus_H2minus_GeV":G["g_h_H1plus_H2minus_GeV"]+9999.})
  self.assertEqual(orig,changed)
  # But the offdiagonal Z current is present: Zgamma cannot be
  # computed by adding only equal-mass scalar loop functions.
  self.assertGreater(abs(G["Z_generator_T3_minus_sW2_mass_basis"][0][1]),0.)
   self.assertAlmostEqual(
       G["Z_generator_T3_minus_sW2_mass_basis"][0][1],
       -.25*math.sin(2*pack["scalar"]["gamma"]),places=12)

 def test_actual_sm_particle_CPodd_yukawa_adds_in_quadrature(self):
  pak=self.pak()
  G=x.hcharged_trilinears(pak["scalar"])
  nom=x.gamma_ratio(pak,G)
  pak["effective_couplings"]["tautau"]=1.+3.j
  withodd=x.gamma_ratio(pak,G)
  self.assertGreater(withodd["new_over_old_h_gamma_gamma_partial_width_LO_amplitude_ratio"],0.)
  self.assertNotEqual(nom["SM_particle_odd_LO_amplitude"],
                      withodd["SM_particle_odd_LO_amplitude"])

 def test_HiggsTools_gamma_override_changes_total_width_and_chisq(self):
  pack=self.pak()
  pred,h,old,total=x.e5.build_predictions(FakeHP,pack)
  oldref={
    "h125_effective_HiggsSignals_chi2":FakeSignals()(pred),
    "h125_total_width_with_h_LFV_GeV":total,
    "delta_chi2_vs_SM_same_dataset_NOT_calibrated_CL":
      FakeSignals()(pred)-153.,
  }
  record=x.evaluate(FakeSignals(),FakeHP,pack,oldref,{"smchi":153.})
  self.assertAlmostEqual(
    record["h125_corrected_total_width_GeV"],
    total-record["gamma_gamma_original_partial_GeV"]+
           record["gamma_gamma_corrected_partial_GeV"]-
           record["Zgamma_original_partial_GeV"]+
           record["Zgamma_corrected_partial_GeV"])
  self.assertTrue(record["h_Zgamma_full_one_loop_charged_scalar_mixed_mass_completed"])
  self.assertTrue(record["Zgamma_full_mixed_mass_PV_amplitudes"][
      "full_offdiagonal_ZH1H2_included"])
  self.assertIsNone(record["full_Zee_allowed_or_excluded"])
  bad={**oldref,"h125_effective_HiggsSignals_chi2":oldref[
        "h125_effective_HiggsSignals_chi2"]+1.}
  with self.assertRaisesRegex(ValueError,"not reproducible"):
   x.evaluate(FakeSignals(),FakeHP,pack,bad,{"smchi":153.})

 def test_full_309_not_allowed_results_csv(self):
  pak=self.pak()
  pred,h,old,width=x.e5.build_predictions(FakeHP,pak)
  reference={
    "h125_effective_HiggsSignals_chi2":FakeSignals()(pred),
    "h125_total_width_with_h_LFV_GeV":width,
    "delta_chi2_vs_SM_same_dataset_NOT_calibrated_CL":0.,
  }
  template=x.evaluate(FakeSignals(),FakeHP,pak,reference,{"smchi":153.})
  rows={};cohort={}
  for idx in range(309):
   tag=f"B4_{idx:07d}"
   rows[tag]={**template,"candidate_id":tag}
   cohort[tag]={**pak,"candidate_id":tag}
  # finish requires original priority IDs: construct a real-size synthetic
  # cohort with 5 anchors and 304 synthetic IDs.
  for key in x.TARGETS:
   last=next(iter(rows))
   rows[key]=rows.pop(last) | {"candidate_id":key}
   cohort[key]=cohort.pop(last) | {"candidate_id":key}
  with tempfile.TemporaryDirectory() as folder:
   out=Path(folder)
   summ=x.finish(out,rows,cohort,{"synthetic":True},153.,159)
   self.assertEqual(summ["updated_HiggsSignals_hgamma_gamma_models"],309)
   self.assertIsNone(summ["full_Zee_allowed_or_excluded"])
   self.assertTrue(summ[
       "full_h_to_Zgamma_one_loop_scalar_subset_with_mixed_mass_completed"])
   self.assertTrue(summ[
       "full_h_to_Zgamma_higher_order_model_prediction_NOT_completed"])
   self.assertTrue((out/"E6_309_gamma_Zgamma_loop_HS_ranked_NOT_ALLOWED.csv").exists())
   with self.assertRaisesRegex(ValueError,"partial cohort"):
    x.finish(out,dict(list(rows.items())[:-1]),cohort,{},153.,159)

 def test_Zgamma_mixed_PV_matches_analytic_I1_and_symmetric_B0_C0(self):
  for mass in (80.379,200.,300.,700.,1200.):
   self.assertTrue(zpv.crosscheck_equal_mass(mass))
  for mi,mj in ((250.,700.),(200.,1000.),(625.,260.)):
   self.assertAlmostEqual(zpv.mixed_mass_F(mi,mj),
                          zpv.mixed_mass_F(mj,mi),places=10)
  t=self.pak()
  G=x.hcharged_trilinears(t["scalar"])
  z=zpv.zgam_ratio(t,G)
  self.assertTrue(z["full_offdiagonal_ZH1H2_included"])
  self.assertTrue(z["PV_48_64_quadrature_and_equal_mass_I1_checked"])
  self.assertAlmostEqual(
      z["ordered_mixed_H1H2_and_H2H1_amplitudes"][0],
      z["ordered_mixed_H1H2_and_H2H1_amplitudes"][1],places=10)
  self.assertGreater(z[
      "full_charged_scalar_plus_modified_SM_LO_hZgamma_over_SM_LO_width"],0.)
  self.assertGreater(abs(z[
      "ordered_mixed_H1H2_and_H2H1_amplitudes"][0]),0.)

 def test_Zgamma_no_couplings_recovers_SM_reference_exactly(self):
  pack=self.pak()
  G=x.hcharged_trilinears(pack["scalar"])
  n={**G,"g_h_H1plus_H1minus_GeV":0.,
     "g_h_H2plus_H2minus_GeV":0.,
     "g_h_H1plus_H2minus_GeV":0.}
  q=zpv.zgam_ratio(pack,n)
  self.assertAlmostEqual(
      q["full_charged_scalar_plus_modified_SM_LO_hZgamma_over_SM_LO_width"],
      1.,places=12)

 def test_fail_closed_on_bad_higgs_potential_and_loop_mass(self):
  with self.assertRaises(ValueError):x.hcharged_trilinears(
      {**self.scalar(),"gamma":float("nan")})
  with self.assertRaises(ValueError):x.a_scalar(-.1)
  with self.assertRaises(ValueError):x.gamma_ratio(
      {**self.pak(),"scalar":{**self.scalar(),"mH1":40.}},
      {"g_h_H1plus_H1minus_GeV":20.,
       "g_h_H2plus_H2minus_GeV":30.})

if __name__=="__main__":
 unittest.main()
