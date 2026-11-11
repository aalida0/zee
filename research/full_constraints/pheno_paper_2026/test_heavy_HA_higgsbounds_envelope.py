"""Fail-closed source H/A LO-maximal-rate HiggsBounds input tests."""
import copy
import unittest
from research.full_constraints.pheno_paper_2026.heavy_HA_higgsbounds_envelope import prepare_source

def setup():
    widths={"state":"H","mass_GeV":950.,"mixed_order_known_channel_sum_GeV":15.,
            "channel_widths_GeV":{"t tbar":10.,"b bbar":1.,"tau tau":.2,"gg":.1,
                                   "H1 W both charges":3.7},
            "full_physical_total_width_GeV":None,"full_Higgs":"UNKNOWN"}
    rate={"state":"H","mass_GeV":950.,"rates":{"ggF":{"sigma_pb":0.01},
                                                  "bbH":{"sigma_pb":0.005}}}
    return widths,rate

class HeavyHABoundsEnvelopeTest(unittest.TestCase):
    def test_missing_exotic_partial_stays_in_denominator(self):
        w,r=setup()
        q=prepare_source(w,r,"H")
        self.assertAlmostEqual(q["source_partial_BR_upper_components"]["tt"],10/15)
        self.assertAlmostEqual(q["fraction_omitted_to_HP_input"],3.7/15)
        self.assertTrue(q["uncomputed_real_total_width"])

    def test_invalid_or_missing_rate_widths_fail_instead_of_zero(self):
        for mode in ("state","mass","total","negative","physical","no_tautau","rate"):
            w,r=copy.deepcopy(setup())
            if mode=="state":w["state"]="A"
            if mode=="mass":r["mass_GeV"]+=1
            if mode=="total":w["mixed_order_known_channel_sum_GeV"]+=1
            if mode=="negative":w["channel_widths_GeV"]["t tbar"]=-5
            if mode=="physical":w["full_physical_total_width_GeV"]=15
            if mode=="no_tautau":del w["channel_widths_GeV"]["tau tau"]
            if mode=="rate":r["rates"]["ggF"]["sigma_pb"]=-.1
            with self.assertRaises((ValueError,ArithmeticError),msg=mode):
                prepare_source(w,r,"H")

if __name__=="__main__":unittest.main()
