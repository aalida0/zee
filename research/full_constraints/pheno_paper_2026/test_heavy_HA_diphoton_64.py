"""Source-control validation of original D7/F13 Zee heavy H/A photon amplitudes."""
import math,unittest
from module2.interface import decode
from research.full_constraints.higgs.sushi_bridge import benchmark
from research.full_constraints.higgs.neutral_widths import photons
from research.full_constraints.pheno_paper_2026.heavy_HA_diphoton_64 import heavy_photons

class NativeHeavyPhotonSourceTests(unittest.TestCase):
    def test_reproduce_original_D7_F13_exact_one_loop_H_A(self):
        for name in ("D7","F13"):
            r,w=benchmark(name)
            p=r["input"]["physical"];D=decode(w["yukawas"]["D"])
            for state in ("H","A"):
                ref=photons(name,state)
                actual=heavy_photons(p,D,state)
                self.assertTrue(math.isclose(ref["amplitude"]["width_GeV"],actual["width_gamma_gamma_GeV"],
                                             rel_tol=2e-12,abs_tol=1e-20),
                                f"{name} {state}: original heavy Gamma gamma mismatch")
                self.assertTrue(math.isclose(ref["amplitude"]["norm"],
                    (actual["even_amplitude"]["real"]**2+actual["even_amplitude"]["imag"]**2+
                     actual["odd_amplitude"]["real"]**2+actual["odd_amplitude"]["imag"]**2),
                    rel_tol=2e-12,abs_tol=1e-16))
                self.assertTrue(actual["general_complex_lepton_Yukawa_included"])
                self.assertTrue(actual["Zgamma_model_specific_incomplete"])

    def test_invalid_CP_resonance_rejected(self):
        r,w=benchmark("F13")
        with self.assertRaises(ValueError):
            heavy_photons(r["input"]["physical"],decode(w["yukawas"]["D"]),"h")

if __name__=="__main__":unittest.main()
