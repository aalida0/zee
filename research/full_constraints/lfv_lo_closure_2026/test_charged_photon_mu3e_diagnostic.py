"""Tests for the strictly partial charged-photon mu -> 3e diagnostic."""
import cmath
import json
import math
import tempfile
import unittest
from pathlib import Path

from research.full_constraints.lfv_lo_closure_2026.charged_photon_mu3e_diagnostic import (
    SOURCE, calculate, photon_only_rate,
)


class TestChargedPhotonMu3e(unittest.TestCase):
    def test_zero_and_common_phase_invariance(self):
        self.assertEqual(photon_only_rate(0j, 0j), 0)
        a_nd = 1e-17 * (1 + 2j)
        a_d = 1.5 * a_nd
        initial = photon_only_rate(a_nd, a_d)
        for phi in (0.17, 0.97, -1.3):
            got = photon_only_rate(a_nd * cmath.exp(1j * phi),
                                   a_d * cmath.exp(1j * phi))
            self.assertAlmostEqual(got / initial, 1, 13)

    def test_interference_retained(self):
        a_nd = 1.0e-16 * (1 + .7j)
        a_d = 1.5 * a_nd
        c = 16 / 3 * math.log(0.1056583755 / 0.00051099895) - 22 / 3
        without = abs(a_nd)**2 + c * abs(a_d)**2
        with_interference = without - 4 * (a_nd * a_d.conjugate()).real
        self.assertLess(with_interference, without)
        self.assertGreater(photon_only_rate(a_nd, a_d), 0)

    def test_four_cards_and_incompleteness_guard(self):
        vals = [
            ("d7_NO_neutral_near_heavy_07/NO/texture_0.0001",
             (1.1465682405575036e-17, 1.4666883990653168e-17),
             (1.0259016229383885e-18, 1.313276548302263e-18), 3.43991360e-25),
            ("d7_NO_neutral_near_heavy_07/IO/texture_0.0001",
             (1.456835092172181e-17, 2.8884288609241766e-17),
             (1.4988590682362801e-18, 2.9765306295109564e-18), 1.04140273e-24),
            ("F13_heavy_0001330/NO/texture_0.001",
             (2.8661749375722796e-16, 3.666406744865868e-16),
             (2.8454651365448357e-21, 3.642534370707241e-21), 2.13248968e-22),
            ("F13_heavy_0001330/IO/texture_0.001",
             (3.6417755888035106e-16, 7.220453277264942e-16),
             (4.1572705139914815e-21, 8.255771361307945e-21), 6.43931473e-22),
        ]
        cards = []
        for card_id, f, d, _ in vals:
            fd, dd = 1.5 * complex(*f), 1.5 * complex(*d)
            cards.append(dict(id=card_id, A1L_F=list(f),
                              A2R_F=[fd.real, fd.imag],
                              A1R_D=list(d), A2L_D=[dd.real, dd.imag]))
        source = dict(status="CHARGED_MASSLESS_NEUTRINO_PHOTON_SOURCE_TRANSFER",
                      physical_lfv="UNKNOWN", full_common_K1=None, cards=cards)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "CHARGED_RESULT.json"
            path.write_text(json.dumps(source))
            out = calculate(path)
            for row, (_, _, _, expected) in zip(out["cards"], vals):
                self.assertAlmostEqual(row["charged_total_photon_only_BR"] / expected, 1, 7)
                self.assertIsNone(row["physical_mu3e_BR"])
            self.assertIsNone(out["physical_mu3e_BR"])
            self.assertEqual(out["physical_lfv"], "UNKNOWN")
            source["full_common_K1"] = [1, 2]
            path.write_text(json.dumps(source))
            with self.assertRaises(ValueError):
                calculate(path)

    def test_actual_frozen_source_if_present(self):
        if not SOURCE.is_file():
            self.skipTest("frozen source not available in isolated test")
        out = calculate(SOURCE)
        expected = [3.43991360e-25, 1.04140273e-24, 2.13248968e-22, 6.43931473e-22]
        for card, value in zip(out["cards"], expected):
            self.assertAlmostEqual(card["charged_total_photon_only_BR"] / value, 1, 7)
        self.assertIsNone(out["physical_mu3e_BR"])


if __name__ == "__main__":
    unittest.main()
