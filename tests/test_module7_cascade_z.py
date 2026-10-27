"""Source-locked tree partial width tests, not collider cross-section or BR tests."""
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from module7.cascade_z import cascade_width,STATUS

ROOT=Path(__file__).resolve().parents[1]
BASE={"mH1_GeV":300.,"mH2_GeV":700.,"mZ_GeV":91.1876,
      "mW_GeV":80.379,"v_GeV":246.21965,"gamma_rad":1.089}

def independent_paper_eq72(x):
    M,m,mz,mw,v,gamma=(x[k] for k in
        ("mH2_GeV","mH1_GeV","mZ_GeV","mW_GeV","v_GeV","gamma_rad"))
    if M<=m+mz:return 0.
    g=2*mw/v
    d = (M*M-(m+mz)**2)*(M*M-(m-mz)**2)
    return (g*g/(64*math.pi*M**3*mw*mw)*
            ((-0.5*math.sin(2*gamma))**2)*d**1.5)

class CascadeTests(unittest.TestCase):
    def test_paper_eq72_for_d2_three_spectra(self):
        for m in (250.,300.,350.):
            row={**BASE,"mH1_GeV":m}
            r=cascade_width(row)
            self.assertEqual(r["status"],STATUS)
            self.assertTrue(r["is_kinematically_open"])
            self.assertAlmostEqual(r["partial_width_GeV"],independent_paper_eq72(row),delta=1e-12)
            self.assertIsNone(r["branching_fraction"])
            self.assertIsNone(r["total_width_GeV"])
            self.assertIsNone(r["global_zee_acceptance"])

    def test_normalization_and_independent_projector(self):
        r=cascade_width(BASE)
        w,z=BASE["mW_GeV"],BASE["mZ_GeV"]
        g=2*w/BASE["v_GeV"]
        coeff=-math.sin(BASE["gamma_rad"])*math.cos(BASE["gamma_rad"])
        self.assertAlmostEqual(r["normalized_offdiagonal_Z_coupling"],coeff,places=15)
        self.assertAlmostEqual(r["absolute_gauge_vertex_coefficient"],
                               abs(g/(2*(w/z))*coeff),places=15)
        # In rest frame, |M|^2 summed over on-shell Z polarisations =
        # |g_Z|^2 * lambda(M^2,m^2,mZ^2) / mZ^2.
        M=BASE["mH2_GeV"]
        p3=r["kallen_sqrt_GeV2"]/(2*M)
        m2=r["absolute_gauge_vertex_coefficient"]**2*(
             r["kallen_sqrt_GeV2"]**2/z**2)
        width=p3/(8*math.pi*M*M)*m2
        self.assertAlmostEqual(width,r["partial_width_GeV"],places=12)

    def test_zero_mixing_and_sign_invariance(self):
        for gamma in (0.,math.pi/2,-math.pi/2):
            self.assertEqual(cascade_width({**BASE,"gamma_rad":gamma})["partial_width_GeV"],0.)
        reference=cascade_width(BASE)["partial_width_GeV"]
        self.assertAlmostEqual(reference,
              cascade_width({**BASE,"gamma_rad":-BASE["gamma_rad"]})["partial_width_GeV"],
              places=13)
        self.assertAlmostEqual(reference,
              cascade_width({**BASE,"gamma_rad":math.pi/2-BASE["gamma_rad"]})["partial_width_GeV"],
              places=13)

    def test_threshold_and_near_threshold(self):
        z=BASE["mZ_GeV"];m=BASE["mH1_GeV"]
        for M in (m+z-1.,m+z):
            row=cascade_width({**BASE,"mH2_GeV":M})
            self.assertFalse(row["is_kinematically_open"])
            self.assertEqual(row["partial_width_GeV"],0.)
        widths=[cascade_width({**BASE,"mH2_GeV":m+z+d})["partial_width_GeV"] 
                for d in (1e-4,1e-3,1e-2)]
        self.assertTrue(widths[0]<widths[1]<widths[2])

    def test_fail_closed_bad_input(self):
        samples=(
            {**BASE,"mH1_GeV":800.},
            {**BASE,"mW_GeV":100.},
            {**BASE,"gamma_rad":2.},
            {**BASE,"v_GeV":float("nan")},
            {**BASE,"mH2_GeV":True},
            {**BASE,"unverified_Br":0.5},
        )
        for row in samples:
            with self.subTest(row=row),self.assertRaises(ValueError):
                cascade_width(row)

    def test_cli_idempotence_and_invalid_duplicate(self):
        with tempfile.TemporaryDirectory() as folder:
            inp=Path(folder)/"in.json";out=Path(folder)/"out.json"
            inp.write_text(json.dumps(BASE))
            args=[sys.executable,"-m","module7.cascade_z","--input",str(inp),
                  "--output",str(out)]
            proc=subprocess.run(args,cwd=ROOT,capture_output=True,text=True)
            self.assertEqual(proc.returncode,0,proc.stderr)
            output=json.loads(out.read_text())
            self.assertEqual(output["status"],STATUS)
            old=out.read_bytes()
            inp.write_text('{"mH1_GeV":300,"mH1_GeV":400}')
            bad=subprocess.run(args,cwd=ROOT,capture_output=True,text=True)
            self.assertNotEqual(bad.returncode,0)
            self.assertEqual(out.read_bytes(),old)

if __name__=="__main__":
    unittest.main()
