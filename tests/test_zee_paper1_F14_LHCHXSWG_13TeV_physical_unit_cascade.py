#!/usr/bin/env python3
"""F14 official-file format tests: synthetic grid except real published anchor."""
from __future__ import annotations
import math,tempfile,unittest,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"scripts"))
import zee_paper1_F14_LHCHXSWG_13TeV_physical_unit_cascade as f

HEADER="""#Contacts: Martin Flechl, Steve Sekula, Maria Ubiali, Marco Zaro
#Date: 2016/2/5
#Santander-matched cross sections for gg->tH+ + X in tan beta (0.1-60) and mH+ (200-2000 GeV), sqrt(s)=13 TeV.
#mhp tb xsec unc- unc+
"""
MASS=(200,600,1200,2000)
TANB=(.1,5.,60.)

def grid_txt():
    rows=[]
    for m in MASS:
        for t in TANB:
            if m==200 and t==.1:
                xs,down,up=336.33,42.293,41.074
            else:
                xs=336.33*(200/m)**3*(.1/t)**.35
                down,up=.14*xs,.12*xs
            rows.append(f"{m} {t} {xs:.15g} {down:.15g} {up:.15g}")
    return HEADER+"\n".join(rows)+"\n"

def ranked():
    return [{
      "candidate_id":f"F13_heavy_{i:07d}",
      "mH1":"552.6","mH2":str(830+20*i),"tanbeta":"5.341",
      "gamma":"1.098","lepton_included_cascade_proxy_NOT_pb":".37078",
      "scalar_nonleptonic_included_cascade_proxy_NOT_pb":".37572",
      "z_UNCALIBRATED_NOT_CL":"1.9489",
      "z_below_1p96_diagnostic_ONLY":"True",
      "neutrino_closed_fixed_old_NO":"True",
      "partial_LFV_score_NOT_full_CL":"0.0000226",
    } for i in range(8)]

class TestF14(unittest.TestCase):
    def load(self,text=None):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"official.txt"
            path.write_text(grid_txt() if text is None else text)
            return f.read_grid(path)
    def test_published_anchor_and_grid(self):
        g=self.load()
        self.assertEqual(g["points"],12)
        p=f.interpolate(g,200,.1)
        self.assertAlmostEqual(p["TypeII_Santander_NLO13TeV_sigma_pb"],336.33)
        self.assertAlmostEqual(p["TypeII_total_uncminus_pb"],42.293)
        self.assertAlmostEqual(p["TypeII_total_uncplus_pb"],41.074)
        self.assertEqual(f.interpolate(g,2000,60)[
            "mass_grid_nodes_GeV"],[2000,2000])
    def test_log_interpolation_and_relative_uncertainties(self):
        g=self.load()
        p=f.interpolate(g,900,5)
        self.assertAlmostEqual(
           p["TypeII_Santander_NLO13TeV_sigma_pb"],
           math.sqrt(g["data"][(600,5.)][0]*g["data"][(1200,5.)][0]))
        self.assertAlmostEqual(p["TypeII_total_uncminus_fraction"],.14)
        self.assertAlmostEqual(p["TypeII_total_uncplus_fraction"],.12)
        q=f.interpolate(g,600,math.sqrt(5*60))
        self.assertAlmostEqual(q["ln_tanbeta_linear_fraction"],.5)
        self.assertAlmostEqual(q["TypeII_Santander_NLO13TeV_sigma_pb"],
             math.sqrt(g["data"][(600,5.)][0]*g["data"][(600,60.)][0]))
    def test_wrong_domain_holes_duplicate_and_wrong_version(self):
        g=self.load()
        for m,t in ((199,5),(2001,5),(800,.09),(800,61)):
            with self.assertRaises(ValueError):f.interpolate(g,m,t)
        lines=grid_txt().splitlines()
        row=next(x for x in lines if x.startswith("600 5.0 "))
        with self.assertRaises(ValueError):
            self.load("\n".join(x for x in lines if x!=row)+"\n")
        with self.assertRaises(ValueError):self.load(grid_txt()+row+"\n")
        with self.assertRaises(ValueError):
            self.load(grid_txt().replace("336.33 42.293 41.074","335 42.293 41.074"))
        with self.assertRaises(ValueError):
            self.load(grid_txt().replace("sqrt(s)=13 TeV","sqrt(s)=14 TeV"))
    def test_eight_no_double_counting_mixing_and_uncertainties(self):
        g=self.load()
        out=f.selected_records(g,ranked())
        self.assertEqual(len(out),8)
        for r in out:
            xs=r["TypeII_Santander_NLO13TeV_sigma_pb"]
            mix=r["mixing_sin2_gamma_doublet_production_weight"]
            proxy=r["general_Zee_included_channel_cascade_proxy_NOT_pb"]
            self.assertAlmostEqual(r[
                "13TeV_TypeII_sigma_times_included_cascade_proxy_pb"],xs*proxy)
            self.assertAlmostEqual(r[
                "Zee_assuming_TypeII_aligned_quarks_sigma_H2_pb"],xs*mix)
            self.assertAlmostEqual(r[
                "general_Zee_conditional_included_BR_H2_H1Z_times_BR_H1_tb"],
                proxy/mix)
            self.assertAlmostEqual(r[
                "13TeV_cascade_estimate_prod_uncplus_ONLY_pb"],
                r["TypeII_total_uncplus_pb"]*proxy)
            self.assertIsNone(r["fully_Zee_allowed_or_excluded"])
            self.assertIsNone(r["physical_complete_13TeV_R_tbZ_pb"])
            self.assertFalse(r["LHCHXSWG_13TeV_charge_convention_checked"])
    def test_reject_bad_source_proxy(self):
        g=self.load();rows=ranked()
        rows[0]["lepton_included_cascade_proxy_NOT_pb"]=".40"
        with self.assertRaises(ValueError):f.selected_records(g,rows)
    def test_minimum_flavor_no_lepton_solution(self):
        g=self.load()
        c=f.minimum_flavor_control(g,[dict(
            id="lowest-z",mH1="715.46",mH2="1123.64",tanbeta="5.37",
            gamma=".6114",abs_z_illustrative_NOT_CL="1.8815",
            production_weighted_nonleptonic_cascade_upper_proxy=".06788")])
        self.assertEqual(c["candidate_id"],"lowest-z")
        self.assertFalse(c["complex_neutrino_Yukawa_optimized"])
        self.assertIsNone(c["full_Zee_allowed_or_excluded"])

if __name__=="__main__":unittest.main()
