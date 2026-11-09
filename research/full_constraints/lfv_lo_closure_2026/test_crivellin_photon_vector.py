"""Focused validation of Crivellin singlet-photon semi-leptonic source limit."""
import copy
import math
import unittest

from research.full_constraints.lfv_lo_closure_2026.crivellin_photon_vector import (
    ALPHA, AL_CAPTURE_GEV, AL_OVERLAPS, MUON_GEV, evaluate, evaluate_card, z
)


def toy():
    # One pure charged singlet H2, lambda=(1+2i)e-5, source A1 and A2.
    lam = complex(1e-5, 2e-5)
    m = 700.0
    weight = 1 / m**2
    a1 = -lam * weight / (288 * math.pi**2)
    a2 = (3 / 2) * a1
    return dict(
        id="synthetic_unmixed_F_limit",
        lam_FdagF=[lam.real, lam.imag],
        A1L_F=[a1.real, a1.imag],
        A2R_F=[a2.real, a2.imag],
        by_state={
            "H1": dict(mass_GeV=300.0, singlet_fraction=0.0),
            "H2": dict(mass_GeV=m, singlet_fraction=1.0),
        },
    )


class TestCrivellinFPhotonVector(unittest.TestCase):
    def test_pure_singlet_source_eqA2(self):
        c = toy()
        r = evaluate_card(c)
        lam = z(c["lam_FdagF"])
        expected = 4 * math.pi * ALPHA * (2 / 3) * lam / (
            288 * math.pi**2 * 700.0**2
        )
        self.assertAlmostEqual(abs(z(r["Cu_LL"])/expected-1), 0, places=12)
        self.assertEqual(r["Cu_LL"], r["Cu_LR"])
        self.assertEqual(r["Cd_LL"], r["Cd_LR"])
        self.assertAlmostEqual(abs(z(r["Cd_LL"])/z(r["Cu_LL"])+0.5), 0, places=12)
        self.assertAlmostEqual(abs(z(r["gn_F_photon_source"])), 0, places=26)
        self.assertAlmostEqual(
            abs(z(r["gp_F_photon_source"]) /
                (2 * z(r["Cu_LL"]) + z(r["Cd_LL"])) - 2), 0, places=12
        )

    def test_crivellin_vs_native_dipole_relative_sign_is_explicit(self):
        r = evaluate_card(toy())
        self.assertAlmostEqual(
            abs(z(r["source_Eq9_dipole_cR"]) +
                z(r["native_e_mmu_over_2_A2R_F"])), 0, places=26
        )
        self.assertIn("OPPOSITE", r["source_dipole_sign_versus_native"])

    def test_mixing_exchange_and_common_phase(self):
        x = toy()
        m1, m2 = 350., 850.
        gamma = 0.9
        x["by_state"] = dict(
            H1=dict(mass_GeV=m1, singlet_fraction=math.sin(gamma)),
            H2=dict(mass_GeV=m2, singlet_fraction=math.cos(gamma)),
        )
        lam = z(x["lam_FdagF"])
        w = math.sin(gamma)**2/m1**2 + math.cos(gamma)**2/m2**2
        a1 = -lam*w/(288*math.pi**2)
        x["A1L_F"] = [a1.real, a1.imag]
        x["A2R_F"] = [1.5*a1.real, 1.5*a1.imag]
        base = evaluate_card(x)
        swapped = copy.deepcopy(x)
        swapped["by_state"]["H1"], swapped["by_state"]["H2"] = (
            swapped["by_state"]["H2"], swapped["by_state"]["H1"]
        )
        again = evaluate_card(swapped)
        self.assertAlmostEqual(
            abs(z(base["gp_F_photon_source"])-z(again["gp_F_photon_source"])),
            0, places=25
        )
        self.assertAlmostEqual(
            base["Al27_F_photon_vector_ONLY_diagnostic"] /
            again["Al27_F_photon_vector_ONLY_diagnostic"], 1, places=12
        )
        phi = complex(math.cos(.73),math.sin(.73))
        rot = copy.deepcopy(x)
        for key in ("lam_FdagF", "A1L_F", "A2R_F"):
            zrot = z(rot[key])*phi
            rot[key] = [zrot.real,zrot.imag]
        rerot = evaluate_card(rot)
        self.assertAlmostEqual(
            rerot["Al27_F_photon_vector_ONLY_diagnostic"]/
            base["Al27_F_photon_vector_ONLY_diagnostic"], 1, places=12
        )

    def test_Al_vector_only_rate_matches_source_A3(self):
        x = toy()
        r = evaluate_card(x)
        gp = z(r["gp_F_photon_source"])
        gn = z(r["gn_F_photon_source"])
        vp, vn = AL_OVERLAPS
        direct = 4 * MUON_GEV**5 * abs(gp*vp + gn*vn)**2 / AL_CAPTURE_GEV
        self.assertAlmostEqual(
            direct/r["Al27_F_photon_vector_ONLY_diagnostic"], 1, places=13
        )
        self.assertIsNone(r["physical_Al27_conversion_rate"])

    def test_frozen_four_card_source(self):
        output = evaluate()
        expected = (3.4600839022156295e-25, 1.0448148665660996e-24,
                    2.1621817758143e-22, 6.528973653333932e-22)
        for row, ref in zip(output["cards"], expected):
            self.assertAlmostEqual(
                row["Al27_F_photon_vector_ONLY_diagnostic"]/ref, 1, places=12
            )
        self.assertIsNone(output["physical_Al27_conversion_rate"])
        self.assertEqual(output["physical_lfv"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
