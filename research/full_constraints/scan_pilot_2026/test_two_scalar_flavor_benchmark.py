import math
import unittest
from module14.scan import digest, neutrino_input
from research.full_constraints.scan_pilot_2026.historical_certified_texture import source_points
from research.full_constraints.scan_pilot_2026 import fresh_8d_lfv_pilot as opt
from research.full_constraints.scan_pilot_2026 import two_scalar_flavor_benchmark as s


class TwoScalarZeeSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cards={p["id"]:p for p in source_points()}

    def test_only_original_two_spectra_with_frozen_vacuum(self):
        self.assertEqual(s.IDS,(15591,15673))
        self.assertEqual(s.SEEDS,(20261111,20261112))
        for ident in s.IDS:
            row=self.cards[ident]
            self.assertEqual(row["gates"]["vacuum"]["assessment"],"PASS")
            self.assertEqual(row["bsg_nominal_classification"],"APPROX_COMPATIBLE")
            self.assertIsNone(row["global_acceptance"])
            self.assertEqual(len(row["families"]),4)
            self.assertEqual(row["families"][0]["production"]["energy_TeV"],13)

    def test_fresh_neutrino_target_independently_source_generated(self):
        for ident in s.IDS:
            row=self.cards[ident]
            raw={"id":ident,"scalar":row["input_card"],"scalar_sha256":row["scalar_sha256"]}
            for ordering in s.ORDERINGS:
                seed, spec, inp=neutrino_input(raw,s.SEEDS[0],ordering,1)
                self.assertEqual(seed,digest(["d14-neutrino-v1",s.SEEDS[0],ident,ordering,1]))
                self.assertEqual(inp["scalar"]["sha256"],row["scalar_sha256"])
                result=opt.evaluate(inp,opt.starting_vector(inp,0))
                self.assertLess(result["neutrino_relative_closure"],2e-9)
                self.assertIsNone(result["global_acceptance"])
                self.assertEqual(result["physical_LFV"],"UNKNOWN")

    def test_no_automatic_13TeV_or_14TeV_acceptance(self):
        self.assertEqual(s.LIMIT,1.5e-13)
        for ident in s.IDS:
            sigma=self.cards[ident]["families"][0]["production"]["sigma_pb"]
            self.assertGreater(sigma,0)
            self.assertIsNone(self.cards[ident]["global_acceptance"])


if __name__=="__main__":
    unittest.main()
