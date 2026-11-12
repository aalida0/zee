"""Adversarial source-identity, partial-vs-physical acceptance and width gates."""
import copy,unittest
from research.full_constraints.pheno_paper_2026.join_Higgs_B_width_64 import join_case

class ScopedZeeGates(unittest.TestCase):
    def fixture(self):
        family={"id":15673,"ordering":"NO","seed":1,"scalar_sha256":"source"}
        h={"scalar_id":15673,"ordering":"NO","seed":1,
           "all_evaluated_direct_search_subsets_below_selected_limits":True,
           "h125_HiggsSignals_delta_chi2_vs_same_dataset_SM":.12,
           "full_HiggsBounds_observed_exclusion":None,
           "physical_HiggsSignals_95CL":None,"global_acceptance":None}
        t={"scalar_id":15673,"ordering":"NO","seed":1,"global_acceptance":None,
           "actual_resonance_shape_validation":None,
           "metrics":{"all_open_H1W_and_H2H1Z_far_five_widths":True,
              "source_width_floor_over_mass":{"H1":.003,"H2":.04,"H":.055,"A":.06},
              "inferred_narrow_width_allowed":None}}
        scalar={"scalar_sha256":"source","published_Eq4_nominal_gaussian_inside":True,
                "published_2026_Eq4_B_pull":1.2}
        return family,h,t,scalar

    def test_conservative_source_prioritization_no_global_pass(self):
        a=join_case(*self.fixture())
        self.assertTrue(a["source_B_direct_threshold_and_h125_small_penalty_for_followup"])
        self.assertIsNone(a["global_acceptance"])
        self.assertIsNone(a["full_LFV"])
        self.assertIsNone(a["physical_Higgs"])

    def test_threshold_gap_and_relative_h125_penalty_change_followup_only(self):
        a,b,c,d=self.fixture()
        c["metrics"]["all_open_H1W_and_H2H1Z_far_five_widths"]=False
        out=join_case(a,b,c,d)
        self.assertTrue(out["source_B_plus_named_direct_scoped_screen"])
        self.assertFalse(out["source_B_plus_direct_and_threshold_well_separated"])
        self.assertFalse(out["source_B_direct_threshold_and_h125_small_penalty_for_followup"])
        c["metrics"]["all_open_H1W_and_H2H1Z_far_five_widths"]=True
        b["h125_HiggsSignals_delta_chi2_vs_same_dataset_SM"]=10
        out=join_case(a,b,c,d)
        self.assertTrue(out["source_B_plus_direct_and_threshold_well_separated"])
        self.assertFalse(out["source_B_direct_threshold_and_h125_small_penalty_for_followup"])

    def test_two_sided_B_interior_does_not_imply_one_sided_upper_95(self):
        a,b,c,d=self.fixture()
        d["published_2026_Eq4_B_pull"]=1.82
        d["published_Eq4_nominal_gaussian_inside"]=True
        scoped=join_case(a,b,c,d)
        self.assertTrue(scoped["source_B_published_2026_LO_NP_two_sided_Gaussian"])
        self.assertFalse(scoped["source_B_published_2026_LO_NP_one_sided_Gaussian"])
        self.assertFalse(scoped["source_B_direct_threshold_and_h125_small_penalty_for_followup"])

    def test_source_errors_and_fictitious_pass_rejected(self):
        for fault in ("mismatch","scalar","global","higgs_pass","width_pass"):
            inputs=list(copy.deepcopy(self.fixture()))
            if fault=="mismatch":inputs[1]["seed"]=2
            if fault=="scalar":inputs[3]["scalar_sha256"]="changed"
            if fault=="global":inputs[1]["global_acceptance"]=True
            if fault=="higgs_pass":inputs[1]["full_HiggsBounds_observed_exclusion"]=False
            if fault=="width_pass":inputs[2]["metrics"]["inferred_narrow_width_allowed"]=True
            with self.assertRaises(ValueError,msg=fault):join_case(*inputs)

if __name__=="__main__":unittest.main()
