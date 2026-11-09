"""Independent loop-kernel limiting and four-card neutral tau transfer controls."""
import copy
import math
import unittest

from research.full_constraints.lfv_2hdm_photon_2026.neutral_tau_Gc_source_limit import (
    SOURCE, common_asymptotic_identity, gc_kernel, gc_asymptotic,
    herrero_gamma_kernel_prefactor, recalculate_card, evaluate
)


class TestNeutralTau2015_2017SourceMatch(unittest.TestCase):
    def test_algebraic_2017_prefactor_for_multiple_scalar_masses(self):
        for m in (125., 300., 500., 1000., 2000.):
            lhs, rhs = common_asymptotic_identity(1.77686, m)
            self.assertAlmostEqual(lhs/rhs, 1, places=14)
            self.assertGreater(gc_kernel((1.77686/m)**2)/gc_asymptotic((1.77686/m)**2),1)

    def test_2015_kernel_asymptotic_ratio(self):
        shifts=[]
        for r in (.0002, .00002, .000002, .0000002):
            shifts.append(abs(gc_kernel(r)/gc_asymptotic(r)-1))
        self.assertEqual(sorted(shifts,reverse=True),shifts)
        self.assertLess(shifts[-1], 6e-7)

    def test_original_four_cards_source_guard_and_correction(self):
        output=evaluate()
        self.assertEqual(len(output["cards"]),4)
        for row in output["cards"]:
            self.assertIsNone(row["full_common_K1"])
            self.assertEqual(row["physical_lfv"], "UNKNOWN")
            for s in row["scalars"].values():
                self.assertLess(s["prefactor_asymptotic_source_residual"],2e-14)
                self.assertLess(abs(s["per_scalar_relative_correction"]),.001)
            self.assertLess(row["relative_tau_L_kernel_shift"],.00006)
            self.assertLess(row["relative_tau_R_kernel_shift"],.00006)

    def test_complex_linearity_and_external_phases(self):
        from research.full_constraints.lfv_2hdm_photon_2026.neutral_tau_Gc_source_limit import z
        import json
        card=json.loads(SOURCE.read_text())["cards"][0]
        a=recalculate_card(card)
        b=copy.deepcopy(card)
        phi=complex(math.cos(.31),math.sin(.31))
        for scalar in b["by_scalar"].values():
            for key in ("gLV_GeV_minus2","gRV_GeV_minus2"):
                q=z(scalar[key])*phi
                scalar[key]=[q.real,q.imag]
        for key in ("gLV_source_tau_neutral_GeV_minus2","gRV_source_tau_neutral_GeV_minus2"):
            q=z(b[key])*phi
            b[key]=[q.real,q.imag]
        ret=recalculate_card(b)
        for old,new in (
            (a["gLV_tau_only_finite_x_kernel_candidate"],ret["gLV_tau_only_finite_x_kernel_candidate"]),
            (a["gRV_tau_only_finite_x_kernel_candidate"],ret["gRV_tau_only_finite_x_kernel_candidate"])
        ):
            self.assertAlmostEqual(abs(z(new)/(z(old)*phi)-1),0,places=12)

    def test_forbidden_mass_domain_rejected(self):
        for x in (0, -1, .1, float("nan"),1.):
            with self.assertRaises(ValueError):
                gc_kernel(x)


if __name__=="__main__":
    unittest.main()
