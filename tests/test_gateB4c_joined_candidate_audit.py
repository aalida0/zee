"""B4C strict joined-audit regression: IDs, mismatches, rates and statuses."""
from __future__ import annotations
import math
import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from gateB4c_joined_candidate_audit import (
    STATUS,make_join,index_superiso,ensure_close
)

def mock_data():
    p=[]
    for ident,m1,m2,g in [("B4_A",205.,680.,1.18),
                          ("B4_B",308.,704.,1.09)]:
        s={
            "id":ident,"seed_id":"32" if ident=="B4_A" else "0",
            "mH1":str(m1),"mH2":str(m2),"mh2":"600.",
            "ma":"635.","gamma":str(g),"tanbeta":"5.6",
            "S":"0.01","T":"0.01","U":"0.001",
            "chi2_Gfitter":"0.2","chi2_PDG":"0.5",
            "max_unitarity":"15",
            "production_weighted_nonleptonic_cascade_upper_proxy":"0.7",
        }
        p.append(s)
    b2={}
    b3=[]
    a1v=[]
    for p0 in p:
        ident=p0["id"]
        b2[ident]=[]
        for j in range(2):
            score=1.e-7*(j+1)
            b2[ident].append({
                "candidate_id":ident,"mH1":float(p0["mH1"]),
                "mH2":float(p0["mH2"]),
                "gamma":float(p0["gamma"]),
                "max_abs_f":.0001,"max_abs_Y":.00001,
                "neutrino_matrix_closure_eV":1e-16,
                "partial_LFV_score_NOT_EXCLUSION":score,
                "partial_LFV_ratios_NOT_EXCLUSION":{
                    "mu_to_e_gamma":score,
                    "tau_to_mu_gamma":score*.02},
                "status":"NEUTRINO_CLOSED_PARTIAL_LFV_ONLY_NOT_ALLOWED",
            })
            b3.append({
                "candidate_id":ident,"b2_solution_rank":str(j+1),
                "mH1":p0["mH1"],"mH2":p0["mH2"],
                "gamma":p0["gamma"],
                "BR_H2_H1Z_included_general_Zee":.8,
                "BR_H1_tb_included_general_Zee":.95,
                "production_weighted_partial_cascade_proxy":.62-.01*j,
                "b2_partial_LFV_score_NOT_EXCLUSION":score,
                "neutrino_matrix_closure_eV":1e-16,
            })
        a1v.append({
            "mH1":p0["mH1"],"mH2":p0["mH2"],
            "gamma":p0["gamma"],"tanbeta":p0["tanbeta"],
            "SM_BR":.000338,"linear_delta_BR":.00005,
            "quadratic_delta_BR":.000002,"full_Zee_BR":.000390,
        })
    return p,b2,b3,a1v


class TestGateB4C(unittest.TestCase):
    def test_honest_audit_status(self):
        self.assertIn("NOT_ALLOWED",STATUS)
        self.assertIn("SCREEN_AUDIT_ONLY",STATUS)

    def test_out_of_order_legacy_csv_matched_by_parameters(self):
        p,b2,b3,a1v=mock_data()
        joined=make_join(p,b2,list(reversed(b3)),list(reversed(a1v)))
        self.assertEqual(len(joined),2)
        self.assertEqual([r["candidate_id"] for r in joined],["B4_A","B4_B"])
        self.assertEqual(joined[0]["n_B3_width_solutions"],2)
        self.assertAlmostEqual(joined[0]["B3_cascade_proxy_median"],.615)
        self.assertAlmostEqual(joined[0]["min_partial_LFV_score_NOT_EXCLUSION"],1e-7)
        self.assertEqual(joined[0]["leading_partial_LFV_channel"],"mu_to_e_gamma")
        self.assertTrue(all("NOT_ALLOWED" in r["status"] for r in joined))

    def test_A1V_must_be_one_to_one_and_matched(self):
        p,b2,b3,a1v=mock_data()
        a1v[0]["gamma"]="1.44"
        with self.assertRaisesRegex(ValueError,"SuperIso join"):
            make_join(p,b2,b3,a1v)

    def test_B3_wrong_candidate_spectrum_rejected(self):
        p,b2,b3,a1v=mock_data()
        b3[0]["mH2"]="800"
        with self.assertRaisesRegex(ValueError,"Mismatch mH2"):
            make_join(p,b2,b3,a1v)

    def test_B3_mismatched_lfv_score_rejected(self):
        p,b2,b3,a1v=mock_data()
        b3[1]["b2_partial_LFV_score_NOT_EXCLUSION"]=999.
        with self.assertRaisesRegex(ValueError,"Mismatch lfv"):
            make_join(p,b2,b3,a1v)

    def test_neutrino_closure_mismatch_rejected_at_ev_scale(self):
        p,b2,b3,a1v=mock_data()
        b3[0]["neutrino_matrix_closure_eV"]=3e-16
        with self.assertRaisesRegex(ValueError,"Mismatch closure"):
            make_join(p,b2,b3,a1v)

    def test_no_double_counted_ranks(self):
        p,b2,b3,a1v=mock_data()
        b3[1]["b2_solution_rank"]="1"
        with self.assertRaisesRegex(ValueError,"Missing/duplicate B3 rank"):
            make_join(p,b2,b3,a1v)

    def test_upper_proxy_consistency(self):
        p,b2,b3,a1v=mock_data()
        b3[0]["production_weighted_partial_cascade_proxy"]=.71
        with self.assertRaisesRegex(ValueError,"cannot.*increase"):
            make_join(p,b2,b3,a1v)

    def test_lfv_diagnostics_cannot_be_renamed_allowed(self):
        p,b2,b3,a1v=mock_data()
        b2["B4_A"][0]["status"]="ALLOWED"
        with self.assertRaisesRegex(ValueError,"unclassified"):
            make_join(p,b2,b3,a1v)

    def test_a1v_components_closure_required(self):
        p,b2,b3,a1v=mock_data()
        a1v[0]["full_Zee_BR"]=.0005
        with self.assertRaisesRegex(ValueError,"fails legacy"):
            make_join(p,b2,b3,a1v)

if __name__=="__main__":
    unittest.main()
