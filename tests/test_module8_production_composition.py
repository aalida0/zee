"""Only test conditional rate arithmetic. No event generation or physical xsec."""
import copy
import json
import unittest
from pathlib import Path

from module8.production_composition import compose,STATUS,PROCESSES

ROOT=Path(__file__).resolve().parents[1]

def ledger():
    return json.loads((ROOT/"validation/module7/d4_decay_table.json").read_text())

def synthetic_card():
    names=("mH1_m50p0","source","mH1_p50p0")
    return {"schema_version":"1.0.0","sqrt_s_TeV":13.6,
      "generator_validation":"UNVERIFIED",
      "rate_cards":[{"spectrum":name,"process":p,
                    "sigma_LO_pb":0.01,"integration_error_pb":0.0001,
                    "charge_scope":"H2plus_and_H2minus_inclusive",
                    "pdf_label":"SYNTHETIC_UNIT_TEST_NOT_PDF",
                    "scale_label":"SYNTHETIC_UNIT_TEST",
                    "source_run_id":"SYNTHETIC_DO_NOT_PUBLISH"}
            for name in names for p in sorted(PROCESSES)]}

class RateCompositionTests(unittest.TestCase):
    def test_independent_D4_baseline_products(self):
        d4=ledger()
        output=compose(d4,synthetic_card())
        self.assertEqual(output["status"],STATUS)
        self.assertFalse(output["physical_rate_validation"])
        self.assertIsNone(output["experimental_exclusion"])
        self.assertIsNone(output["global_zee_acceptance"])
        self.assertEqual(len(output["entries"]),12)
        actual=next(r for r in output["entries"] if r["spectrum"]=="source" and r["family"]=="baseline")
        b2=.8087627985129457
        b1=.9964794284816165
        self.assertAlmostEqual(actual["single_H1_chain_product"],b2*b1,places=14)
        self.assertAlmostEqual(actual["mixed_pair_two_H1_chain_product"],b2*b1*b1,places=14)
        self.assertAlmostEqual(actual["rates"]["tbH2_5FS"]["conditional_sigma_times_tree_BR_pb"],
                               .01*b2*b1,places=14)
        self.assertAlmostEqual(actual["rates"]["H1H2_mixed_DY"]["conditional_sigma_times_tree_BR_pb"],
                               .01*b2*b1*b1,places=14)

    def test_no_four_five_flavor_summing(self):
        result=compose(ledger(),synthetic_card())
        self.assertEqual(result["processes_not_to_sum"],["tbH2_4FS","tbH2_5FS"])
        for entry in result["entries"]:
            self.assertEqual(set(entry["rates"]),set(PROCESSES))
            self.assertTrue(all(not r["accepted_LHC_prediction"] for r in entry["rates"].values()))

    def test_all_three_spectra_and_four_families(self):
        rows=compose(ledger(),synthetic_card())["entries"]
        self.assertEqual(len(set((x["spectrum"],x["family"]) for x in rows)),12)
        for name in ("mH1_m50p0","source","mH1_p50p0"):
            vals=[x["single_H1_chain_product"] for x in rows if x["spectrum"]==name]
            self.assertEqual(len(vals),4)
            self.assertTrue(all(0.<v<1. for v in vals))

    def test_fail_closed_missing_or_invented_cross_section(self):
        mutations=(
            lambda c:c["rate_cards"].pop(),
            lambda c:c["rate_cards"].append(copy.deepcopy(c["rate_cards"][0])),
            lambda c:c["rate_cards"][0].__setitem__("sigma_LO_pb",-1.),
            lambda c:c["rate_cards"][0].__setitem__("sigma_LO_pb",float("nan")),
            lambda c:c["rate_cards"][0].__setitem__("charge_scope","H2plus_only"),
            lambda c:c["rate_cards"][0].__setitem__("pdf_label",""),
            lambda c:c["rate_cards"][0].__setitem__("accepted",True),
            lambda c:c.__setitem__("generator_validation","PHYSICS_VERIFIED"),
            lambda c:c.__setitem__("sqrt_s_TeV",13.),
        )
        for mut in mutations:
            card=synthetic_card();mut(card)
            with self.subTest(mut=str(mut)),self.assertRaises((ValueError,TypeError)):
                compose(ledger(),card)

    def test_d4_physics_not_silently_approvable(self):
        d4=ledger()
        d4["global_zee_acceptance"]=True
        with self.assertRaises(ValueError):compose(d4,synthetic_card())
        d4=ledger();d4["statuses"]=[]
        with self.assertRaises(ValueError):compose(d4,synthetic_card())

if __name__=="__main__":
    unittest.main()
