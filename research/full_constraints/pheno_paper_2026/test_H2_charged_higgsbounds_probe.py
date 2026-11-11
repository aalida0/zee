"""Unit and falsification controls for source Zee H2 HiggsBounds bridge."""
import copy
import unittest
from research.full_constraints.pheno_paper_2026.H2_charged_higgsbounds_probe import inspect_decay_contract, TOOL_DECAYS

class ZeeH2ChargedWidthsTests(unittest.TestCase):
    def fixture(self):
        channels=[{"channel":source,"width_GeV":0.01*(i+1)} for i,(_,source) in enumerate(TOOL_DECAYS)]
        channels.append({"channel":"H1 Z","width_GeV":4.0})
        channels.append({"channel":"H1 h","width_GeV":2.0})
        total=sum(x["width_GeV"] for x in channels)
        d={"total":{"status":"D4_COMPLETE_TWO_BODY_BR_PASS","total_width_GeV":total},
           "channels":channels}
        return d,{"D4_BR_H2_H1Z":4/total}

    def test_h2_exotic_cascade_is_in_total_denominator_not_lost(self):
        d,f=self.fixture()
        actual=inspect_decay_contract(d,f)
        self.assertEqual(set(actual["input_BRs"]),{x for x,_ in TOOL_DECAYS})
        self.assertAlmostEqual(actual["BR_H2_to_H1_Z"],f["D4_BR_H2_H1Z"])
        self.assertAlmostEqual(actual["all_two_body_BRs_sum"],1.0)
        self.assertLess(sum(actual["input_BRs"].values()),1.0)

    def test_reference_bad_duplicate_negative_or_unmatched_exotic_fails(self):
        d,f=self.fixture()
        for alter in ("total","duplicate","negative","missing","wrong_cascade"):
            t=copy.deepcopy(d);q=copy.deepcopy(f)
            if alter=="total":t["total"]["total_width_GeV"]+=1
            if alter=="duplicate":t["channels"].append(copy.deepcopy(t["channels"][0]))
            if alter=="negative":t["channels"][0]["width_GeV"]=-1
            if alter=="missing":t["channels"]=[z for z in t["channels"] if z["channel"]!="H1 Z"]
            if alter=="wrong_cascade":q["D4_BR_H2_H1Z"]*=.5
            with self.assertRaises((ValueError,KeyError),msg=alter):
                inspect_decay_contract(t,q)

    def test_invalid_d4_gate_fails_closed(self):
        d,f=self.fixture()
        d["total"]["status"]="NOT_EVALUATED"
        with self.assertRaises(ValueError):inspect_decay_contract(d,f)

if __name__=="__main__":
    unittest.main()
