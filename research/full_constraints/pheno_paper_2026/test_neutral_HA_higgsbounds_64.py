"""Heavy H/A source-matched public LO HiggsBounds envelope falsification tests."""
import copy,math,unittest
from research.full_constraints.pheno_paper_2026.neutral_HA_higgsbounds_64 import source_rates,HEAVY_DECAYS

class HeavySourceEnvelopeChecks(unittest.TestCase):
    def fixture(self, state="A"):
        prod={(42,state):{
          "scalar_id":42,"state":state,"original_scalar_sha256":"TEST_SHA",
          "mass_GeV":900.0,"QCD_order":"LO","energy_TeV":13,
          "PDF":"MMHT2014lo68cl",
          "rates":{"ggF":{"sigma_pb":0.04},"bbH":{"sigma_pb":0.003}}
        }}
        channels={"t tbar":20.0,"tau tau":0.1,"b bbar":0.2,
                  "cc source dummy":0.0}
        if state=="A":channels["H Z (HDECAY reference only)"]=0.003
        case={"scalar_id":42,"scalar_sha256":"TEST_SHA",
              "states":{state:{"mass_GeV":900.0,
               "mixed_order_known_channel_sum_GeV":sum(channels.values()),
               "channel_widths_GeV":channels,
               "full_physical_total_width_GeV":None,
               "normalized_physical_branching_fractions":None,
               "source_uncomputed_on_shell":[],
               "additional_missing_groups":["Zgamma loops"],
               "source_uncomputed_channel_groups":["EW QCD"]}}}
        return prod,case

    def test_basic_positive_widths_and_source_matches(self):
        p,c=self.fixture()
        out=source_rates(p,c,"A")
        self.assertGreater(out["known_Gamma_over_M"],0)
        self.assertAlmostEqual(out["sigma13_ggF_LO_pb"],0.04)
        self.assertTrue(out["missing"])

    def test_source_mass_and_width_inconsistency_rejected(self):
        for attr in ("hash","mass","partial","negative","order","physical_total"):
            p,c=self.fixture()
            if attr=="hash":p[(42,"A")]["original_scalar_sha256"]="OTHER"
            if attr=="mass":p[(42,"A")]["mass_GeV"]+=1
            if attr=="partial":c["states"]["A"]["mixed_order_known_channel_sum_GeV"]+=0.5
            if attr=="negative":c["states"]["A"]["channel_widths_GeV"]["t tbar"]=-1
            if attr=="order":p[(42,"A")]["QCD_order"]="NLO"
            if attr=="physical_total":c["states"]["A"]["full_physical_total_width_GeV"]=20.
            with self.assertRaises(ValueError,msg=attr):
                source_rates(p,c,"A")

    def test_missing_open_onshell_not_ignored_except_tiny_source_matched_threshold(self):
        p,c=self.fixture()
        c["states"]["A"]["source_uncomputed_on_shell"]=["A -> H Z on-shell, model-matched tree transition NOT included"]
        out=source_rates(p,c,"A")
        self.assertEqual(len(out["near_threshold_unvalidated"]),1)
        self.assertLess(out["near_threshold_unvalidated"][0]["HDECAY_fraction_of_known_sum"],.005)
        c["states"]["A"]["channel_widths_GeV"]["H Z (HDECAY reference only)"]=1.
        c["states"]["A"]["mixed_order_known_channel_sum_GeV"]=sum(c["states"]["A"]["channel_widths_GeV"].values())
        with self.assertRaises(ValueError):source_rates(p,c,"A")
        c["states"]["A"]["source_uncomputed_on_shell"]=["Some other open channel"]
        with self.assertRaises(ValueError):source_rates(p,c,"A")

if __name__=="__main__":unittest.main()
