#!/usr/bin/env python3
"""Fast regression tests for real Paper-1 feasibility scan and honest boundaries."""
from __future__ import annotations
import argparse
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import zee_paper1_florentino_feasibility_scan as scan

class TestPaper1IntegratedFeasibility(unittest.TestCase):
    def test_output_truth_contract(self):
        self.assertIn("NOT_ALLOWED",scan.STATUS)
        self.assertGreaterEqual(len(scan.MISSING),8)
        self.assertTrue(any("B->Xs" in x for x in scan.MISSING))
        self.assertTrue(any("production" in x for x in scan.MISSING))
        self.assertTrue(any("LFV" in x for x in scan.MISSING))
        self.assertTrue(any("NuFIT" in x or "oscillation" in x
                            for x in scan.MISSING))

    def test_finite_values_and_scalar_validation(self):
        p={k:1. for k in scan.SPECTRUM_FIELDS}
        p.update(id="X",mH1=300.,mH2=700.,gamma=1.089,beta=1.394)
        got=scan.scalar_row(p)
        self.assertEqual(got["id"],"X")
        self.assertEqual(got["mH2"],700.)
        with self.assertRaises(ValueError):
            scan.scalar_row({**p,"mH2":300.})
        with self.assertRaises(ValueError):
            scan.scalar_row({**p,"gamma":0.})
        with self.assertRaises(ValueError):
            scan.scalar_row({**p,"mH1":float("nan")})
        with self.assertRaises(ValueError):
            scan.finite(True,"x")

    def test_florentino_p2_fallback_provenance_not_exact_published(self):
        p=scan.p2_seed()
        self.assertEqual(p["seed_id"],"P2_INSPIRED_BETA1394_K120")
        self.assertAlmostEqual(p["beta"],1.394)
        self.assertAlmostEqual(p["k12"],0.)
        self.assertAlmostEqual(p["mH1"],300.)
        self.assertAlmostEqual(p["mH2"],700.)
        self.assertAlmostEqual(p["gamma"],1.089)
        self.assertIn("P2_INSPIRED",p["id"])

    def test_cannot_silently_choose_conflicting_e2_archives(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory)
            self.assertEqual(
                scan.locate_seed_csv(folder),
                (None,"NEW_P2_TABLE2_INSPIRED_SCALAR_START_NOT_PUBLISHED_SINGLE_POINT"))
            supplied=folder/"mine.csv"
            supplied.write_text("id\nX\n")
            self.assertEqual(scan.locate_seed_csv(folder,supplied)[0],supplied)
            with self.assertRaises(FileNotFoundError):
                scan.locate_seed_csv(folder,folder/"missing.csv")

    def test_matrix_encoding_does_not_drop_complex_phases(self):
        z=np.array([[0,1j,2-3j],[.0005,0,-1j],
                    [4+1j,.1,0]],complex)
        out=scan.complex_payload(z)
        self.assertEqual(out["imag"][0][2],-3.)
        self.assertEqual(out["real"][2][0],4.)
        with self.assertRaises(ValueError):
            scan.complex_payload(np.ones((2,2)))

    def test_no_neutrino_solution_is_not_an_exclusion(self):
        with patch.object(scan,"antisymmetric_f_with_null_condition",
                          return_value=(np.zeros((3,3),complex),None)):
            with patch.object(scan,"build_trial",return_value=None):
                result=scan.optimize_point({},np.zeros((3,3),complex),
                  np.random.default_rng(1),trials=3,local_seeds=1,
                  max_evals=0)
        self.assertEqual(result["status"],
                         "NO_NEUTRINO_CLOSED_TRIALS_FOUND_NOT_EXCLUSION")
        self.assertIsNone(result["model_allowed_or_excluded"])

    def test_no_overwrite_before_scan(self):
        with tempfile.TemporaryDirectory() as directory:
            args=argparse.Namespace(output=directory,max_spectra=1,
                 scalar_steps=0,trials=1,optimize_seeds=1,
                 optimize_evals=0,quadrature_nodes=40,
                 chains=1,seed_csv=None,seed_count=1,seed=1)
            with self.assertRaises(FileExistsError):
                scan.execute(args)

if __name__=="__main__":
    unittest.main()
