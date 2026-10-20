"""N2 true gauge and charged-pair bosonic source calculations."""
import math,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import zee_priority1_neutral_bosonic_two_body as N
from gate6_benchmark import benchmark
from gate6_width_inventory import (
 trilinears,vector_width,scalar_width,SW2,ALPHA_INV,MW,MZ)

def point(**kwargs):
 x={"id":"B4_N2_TEST","mH1":208.77,"mH2":681.85,
    "mh2":597.72,"ma":635.23,"beta":math.atan(5.647),
    "alpha":math.atan(5.647)+.003,"gamma":1.1201,
    "m12sq":57700.,"lc":4.473,"k1":1.082,
    "k2":.00398,"k12":-.001266}
 return {**x,**kwargs}

class N2RealPhysics(unittest.TestCase):
 def test_all_fourteen_bosonic_channels_nonnegative_source(self):
  z=N.calculate(point())
  self.assertEqual(z["status"],N.STATUS)
  self.assertEqual(set(z["additional_gauge_and_charged_pair_LO_GeV"]),{"h","H","A"})
  self.assertEqual(len(z["additional_gauge_and_charged_pair_LO_GeV"]["h"]),6)
  self.assertEqual(len(z["additional_gauge_and_charged_pair_LO_GeV"]["H"]),6)
  self.assertEqual(len(z["additional_gauge_and_charged_pair_LO_GeV"]["A"]),4)
  for key,rows in z["additional_gauge_and_charged_pair_LO_GeV"].items():
   self.assertTrue(all(v>=0 and math.isfinite(v) for v in rows.values()))
   self.assertAlmostEqual(sum(rows.values()),z[
     "additional_included_subtotals_NOT_physical_totals_GeV"][key])
  self.assertTrue(z["old_Gate6_H2_H1_h_H_trilinear_source_closed"])
  self.assertIsNone(z["neutral_physical_total_widths"])
  self.assertIsNone(z["full_model_allowed_or_excluded"])

 def test_original_Gate6_offdiag_cubic_h_and_H_pure_source_closure(self):
  p=point()
  scalar=benchmark(beta=p["beta"],mH1=p["mH1"],mH2=p["mH2"],
      mh2=p["mh2"],ma=p["ma"],alpha=p["alpha"],
      gamma=p["gamma"],m12sq=p["m12sq"],lc=p["lc"],
      k1=p["k1"],k2=p["k2"],k12=p["k12"])
  z=N.charged_hessian_cubic_matrices(scalar)
  old=trilinears(scalar)
  self.assertAlmostEqual(z["h"][0,1],old["h125"],places=11)
  self.assertAlmostEqual(z["H"][0,1],old["hheavy"],places=11)
  self.assertAlmostEqual(z["h"][1,0],z["h"][0,1],places=11)
  self.assertAlmostEqual(z["H"][1,0],z["H"][0,1],places=11)

 def test_charged_identical_vs_mixed_pair_count_and_threshold(self):
  p=point(mh2=640.,mH1=210.,mH2=690.)
  r,mats,_=N.charged_pair_subset(p)
  self.assertEqual(r["h"]["H1plus_H1minus"],0.)
  self.assertEqual(r["H"]["H1plus_H2minus_and_conjugate"],0.)
  self.assertEqual(r["H"]["H2plus_H2minus"],0.)
  self.assertAlmostEqual(
   r["H"]["H1plus_H1minus"],
   scalar_width(p["mh2"],p["mH1"],p["mH1"],float(mats["H"][0,0])))
  # An artificial heavy neutral test makes mixed charged pairs open.
  p2=point(mh2=1300.,mH1=250.,mH2=700.,ma=1320.)
  z,g,_=N.charged_pair_subset(p2)
  self.assertAlmostEqual(z["H"]["H1plus_H2minus_and_conjugate"],
     2*scalar_width(1300.,250.,700.,float(g["H"][0,1])),places=10)

 def test_W_charge_pair_factor_2_matches_gate6_current(self):
  p=point(mh2=645.,ma=695.,mH1=200.,mH2=800.)
  z=N.gauge_subset(p)
  gw=math.sqrt(4*math.pi/(ALPHA_INV*SW2))
  self.assertAlmostEqual(z["A"]["H1_W_both_charge_modes"],
    2*vector_width(p["ma"],p["mH1"],MW,gw/2*math.cos(p["gamma"])),places=9)
  self.assertEqual(z["A"]["H2_W_both_charge_modes"],0.)
  d=p["beta"]-p["alpha"]
  self.assertAlmostEqual(z["H"]["H1_W_both_charge_modes"],
    2*vector_width(p["mh2"],p["mH1"],MW,
        gw/2*math.cos(p["gamma"])*math.cos(d)),places=9)

 def test_neutral_ZA_Zh_aligned_and_complementarity(self):
  p=point(mh2=600.,ma=850.,alpha=math.atan(5.647),
          beta=math.atan(5.647))
  z=N.gauge_subset(p)
  self.assertAlmostEqual(z["A"]["h_Z"],0.,places=12)
  self.assertGreater(z["A"]["H_Z"],0.)
  self.assertEqual(z["H"]["A_Z"],0.)
  self.assertEqual(z["h"]["A_Z"],0.)
  p2=point(mh2=850.,ma=600.,alpha=math.atan(5.647),
           beta=math.atan(5.647))
  z2=N.gauge_subset(p2)
  self.assertGreater(z2["H"]["A_Z"],0.)
  self.assertEqual(z2["A"]["H_Z"],0.)

 def test_gauge_weight_as_gamma_goes_to_doublet_or_singlet(self):
  p=point(mh2=700.,ma=730.,mH1=230.,mH2=300.,gamma=.00001)
  first=N.gauge_subset(p)
  p["gamma"]=math.pi/2-.00001
  second=N.gauge_subset(p)
  self.assertAlmostEqual(first["A"]["H1_W_both_charge_modes"],
                         second["A"]["H2_W_both_charge_modes"],
                         places=8)
  self.assertAlmostEqual(first["A"]["H2_W_both_charge_modes"],
                         second["A"]["H1_W_both_charge_modes"],
                         places=8) if p["mH1"]==p["mH2"] else None

 def test_invalid_masses_and_mixing_refused(self):
  with self.assertRaisesRegex(ValueError,"charged mixing"):
   N.gauge_subset(point(gamma=0.))
  with self.assertRaisesRegex(ValueError,"physical masses"):
   N.gauge_subset(point(ma=-100.))
  with self.assertRaisesRegex(ValueError,"source missing"):
   N.calculate({k:v for k,v in point().items() if k!="id"})

if __name__=="__main__":unittest.main()
