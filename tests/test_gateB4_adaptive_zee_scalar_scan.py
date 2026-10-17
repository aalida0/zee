"""B4 tests: physical seed, adaptive explorer, diversity and B3 handoff."""
from __future__ import annotations
import csv
import math
from pathlib import Path
import sys
import tempfile
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from gate6_benchmark import benchmark
from gate6_width_inventory import inventory
from gateB3_general_zee_charged_lepton_widths import read_b1
from gateB4_adaptive_zee_scalar_scan import (
    STATUS,SINGLET_DEFAULTS,COORDS,read_seed_csv,
    encode,decode,propose,scalar_screen,ewpo_screen,
    nonleptonic_proxy,coarse_bin,shortlist,scan,write_csv
)

def seed():
    return {
        "seed_id":"0","mH1":300.,"mH2":700.,"mh2":580.7,"ma":633.7,
        "alpha":1.398,"beta":1.394,"gamma":1.089,"m12sq":57700.,
        **SINGLET_DEFAULTS,
    }

class TestGateB4(unittest.TestCase):
    def test_encode_decode_preserves_scalar_potential_inputs(self):
        p=seed()
        x=encode(p)
        self.assertEqual(x.shape,(len(COORDS),))
        q=decode(x)
        self.assertIsNotNone(q)
        for k in q:
            self.assertAlmostEqual(p[k],q[k],delta=max(1e-9,abs(p[k])*1e-12))

    def test_reference_scalar_and_oblique_pass(self):
        p=decode(encode(seed()))
        th=scalar_screen(p)
        self.assertIsNotNone(th)
        self.assertTrue(th["sufficient_global_quartic_BFB"])
        self.assertTrue(th["tree_unitarity_pass"])
        ew=ewpo_screen(p,48)
        self.assertIsNotNone(ew)
        self.assertTrue(all(
            v["inside_95percent_3D_gaussian_ellipsoid"]
            for v in ew["correlated_fit_screens"].values()))

    def test_nonleptonic_upper_proxy_does_not_double_count_typeii(self):
        p=decode(encode(seed()))
        b2,b1,proxy=nonleptonic_proxy(p)
        old=inventory(beta=p["beta"],mH1=p["mH1"],mH2=p["mH2"],
                      alpha=p["alpha"],gamma=p["gamma"],
                      m12sq=p["m12sq"],mh2=p["mh2"],ma=p["ma"],
                      lc=p["lc"],k1=p["k1"],k2=p["k2"],
                      k12=p["k12"])
        oldf=old["conditional_fractions_included_channels_only"]
        self.assertGreaterEqual(b2,oldf["H2"]["H1_Z"])
        self.assertGreaterEqual(b1,oldf["H1"]["tb"])
        self.assertTrue(0<=proxy<=1)

    def test_seed_schema_and_b3_scanned_quartics_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"input.csv"
            rows=[{
                "id":"B4_000001","mH1":300.,"mH2":700.,
                "mh2":580.7,"ma":633.7,"alpha":1.398,"beta":1.394,
                "gamma":1.089,"m12sq":57700.,"lc":4.60,
                "k1":1.13,"k2":0.0060,"k12":-0.0017,
            }]
            cols=list(rows[0])
            with path.open("w",newline="") as fh:
                w=csv.DictWriter(fh,fieldnames=cols)
                w.writeheader();w.writerows(rows)
            seeds=read_seed_csv(path)
            self.assertEqual(seeds[0]["seed_id"],"B4_000001")
            self.assertAlmostEqual(seeds[0]["k2"],.006)
            b3=read_b1(path)
            self.assertAlmostEqual(b3["B4_000001"]["k2"],.006)
            self.assertAlmostEqual(b3["B4_000001"]["k12"],-.0017)
            self.assertAlmostEqual(b3["B4_000001"]["lc"],4.6)

    def test_sampler_is_reproducible_and_fail_closed(self):
        seeds=[seed()]
        kw={"steps":20,"chains":2,"quad":48,"adaptive_block":20,
            "report_every":0}
        a,ma=scan(seeds,rng=np.random.default_rng(77),**kw)
        b,mb=scan(seeds,rng=np.random.default_rng(77),**kw)
        self.assertEqual(ma,mb)
        self.assertEqual(a,b)
        self.assertGreaterEqual(len(a),1)
        self.assertIsNone(ma["n_physically_allowed_points"])
        self.assertEqual(
            sum(ma["stage_rejection_counts"].values())
            +ma["EWPO_screen_pass_proposals"],
            kw["steps"])
        self.assertTrue(all("NOT_ALLOWED" in p["candidate_status"] for p in a))

    def test_large_disallowed_moves_and_coarse_diversity(self):
        p=seed()
        x=encode(p)
        q=x.copy();q[0]=50.
        self.assertIsNone(decode(q))
        random=np.random.default_rng(2026)
        self.assertEqual(propose(x,random,1.).shape,x.shape)
        a=decode(x)
        self.assertIsNotNone(a)
        self.assertEqual(coarse_bin(a),coarse_bin(a))
        rec={
            **a,"production_weighted_nonleptonic_cascade_upper_proxy":.7}
        chosen=shortlist([rec,dict(rec)],10)
        self.assertEqual(len(chosen),1)

    def test_status_distinguishes_screen_from_allowed(self):
        self.assertIn("NOT_ALLOWED",STATUS)
        self.assertIn("SCREEN_ONLY",STATUS)

if __name__=="__main__":
    unittest.main()
