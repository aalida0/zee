"""Minimal dependency-free Priority1 backend and actual HiggsTools API contracts."""
import contextlib,csv,io,json,math,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import zee_priority1_contracts as c
import zee_priority1_higgstools as h
import zee_priority1_cli as cli

def model():
    return {"candidate_id":"B4_0004143","h":125.,"H":590.,
            "A":630.,"H1":210.,"H2":680.,"gamma":1.12,"tanbeta":5.6}
def decays(*,complete=True):
    x={"all_physical_decay_channels_enumerated":complete,
       "off_shell_and_QCD_treatment_validated":True,
       "independent_width_validation_reference":"TEST ONLY: synthetic",
       "higgstools_decay_mode_mapping_validated":True,
       "particles":{
         s:{"mass_GeV":model()[s],"total_width_GeV":3.,
            "partial_widths_GeV":{"bb":2.,"tautau":1.}}
         for s in c.IDS}}
    return x
def production(*,complete=True):
    return {
     "all_relevant_hadronic_channels_enumerated":complete,
     "interference_K_factors_PDF_uncertainties_validated":True,
     "generator_tune_and_validation_reference":"TEST ONLY: synthetic",
     "higgstools_production_mode_mapping_validated":True,
     "particles":{s:{"ggH":{
           "sigma_pb":.1,"uncertainty_pb":.01,"collider":"LHC13"}}
           for s in c.IDS}}
def bsgamma():
    return {
     "scheme_matched_two_charged_inclusive_rate":True,
     "operator_basis_and_matrix_element_closure":True,
     "SM_and_TypeII_670_independent_controls_pass":True,
     "calibrated_BSM_uncertainty_likelihood":True,
     "branching_ratio":3.5e-4,"theory_sigma":1.e-5,
     "Egamma_cut_GeV":1.6,
     "perturbative_order":"NNLO",
     "validation_document":"TEST ONLY"}
def neutrino():
    return {"full_two_ordering_oscillation_likelihood_computed":True,
     "mass_matrix_closure_eV":1e-12,
     "oscillation_fit":{"ordering":"NO","chi2":1.,"dataset":"TEST",
                        "source_version":"TEST"}}
def lfv():
    return {"all_one_and_two_loop_amplitudes_interfered":True,
     "conversion_nuclear_overlap_and_capture_included":True,
     "source_validation_reference":"TEST",
     "rates_and_limits":{k:{"prediction":1e-20,"experimental_90CL_limit":1e-10}
       for k in ("mu_to_e_gamma","tau_to_e_gamma","tau_to_mu_gamma",
                 "mu_to_3e","mu_e_conversion")}}
def csvpoints(path):
    with Path(path).open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=[
          "id","mH1","mH2","mh2","ma","gamma","tanbeta","candidate_status"])
        w.writeheader()
        w.writerow({"id":"B4_0004143","mH1":210,"mH2":680,
         "mh2":590,"ma":630,"gamma":1.12,"tanbeta":5.6,
         "candidate_status":"SCALAR_EWPO_SCREEN_ONLY_NOT_ALLOWED"})

class TestPriorityOne(unittest.TestCase):
    def test_empty_backends_never_allow(self):
        x=c.evaluate({model()["candidate_id"]:model()}, {})
        self.assertFalse(x[0]["all_priority1_backend_inputs_complete"])
        self.assertTrue(all(s=="BLOCKED_NO_BACKEND_INPUT"
                            for s in x[0]["stages"].values()))
        self.assertIsNone(x[0]["experimental_Zee_allowed_or_excluded"])

    def test_neutrino_exact_closure_and_ordering(self):
        r=neutrino()
        self.assertEqual(c.validate_neutrino(r),"EVALUATED_FULL_OSCILLATION_INPUT")
        r["full_two_ordering_oscillation_likelihood_computed"]=False
        self.assertIn("BLOCKED",c.validate_neutrino(r))
        r["full_two_ordering_oscillation_likelihood_computed"]=True
        r["mass_matrix_closure_eV"]=1e-5
        self.assertIn("FAIL_",c.validate_neutrino(r))

    def test_lfv_no_missing_Barr_Zee_or_conversion(self):
        r=lfv()
        self.assertEqual(c.validate_lfv(r),"EVALUATED_COMPLETE_LFV_INPUT")
        r["all_one_and_two_loop_amplitudes_interfered"]=False
        self.assertIn("BLOCKED",c.validate_lfv(r))
        r["all_one_and_two_loop_amplitudes_interfered"]=True
        del r["rates_and_limits"]["mu_e_conversion"]
        self.assertIn("BLOCKED",c.validate_lfv(r))

    def test_no_legacy_superiso_as_modern_precision_rate(self):
        r=bsgamma()
        self.assertEqual(c.validate_bsgamma(r),"EVALUATED_MODERN_INCLUSIVE_RATE_INPUT")
        r["scheme_matched_two_charged_inclusive_rate"]=False
        self.assertIn("BLOCKED",c.validate_bsgamma(r))
        r["scheme_matched_two_charged_inclusive_rate"]=True
        r["Egamma_cut_GeV"]=1.9
        self.assertIn("BLOCKED",c.validate_bsgamma(r))

    def test_five_state_width_sums_and_missing_H_are_blocked(self):
        r=decays()
        self.assertEqual(c.validate_decays(r,model()),"EVALUATED_FIVE_STATE_DECAY_INPUT")
        r["particles"]["H"]["partial_widths_GeV"]["bb"]=1.
        self.assertIn("BLOCKED",c.validate_decays(r,model()))
        r=decays()
        del r["particles"]["A"]
        self.assertIn("BLOCKED",c.validate_decays(r,model()))

    def test_production_has_pb_and_five_states(self):
        self.assertEqual(c.validate_production(production(),model()),
                         "EVALUATED_FIVE_STATE_PRODUCTION_INPUT")
        r=production()
        r["particles"]["H1"]["ggH"]["sigma_pb"]=-1.
        with self.assertRaisesRegex(ValueError,"negative"):
            c.validate_production(r,model())
        r=production()
        r["particles"]["H"]["ggH"]["collider"]="FCCee240"
        self.assertIn("BLOCKED",c.validate_production(r,model()))

    def test_real_higgstools_prediction_dictionary_no_implicit_width(self):
        data=h.predictions_dict(model(),decays(),production())
        self.assertEqual(data["m_H1"],210.)
        self.assertEqual(data["w_H"],3.)
        self.assertAlmostEqual(data["br_A_bb"],2/3)
        self.assertAlmostEqual(data["cxn_H1_ggH_LHC13"],.1)
        self.assertEqual(data["CP_A"],"odd")
        x=decays();x["all_physical_decay_channels_enumerated"]=False
        with self.assertRaisesRegex(ValueError,"Incomplete"):
            h.predictions_dict(model(),x,production())

    def test_higgstools_adapter_calls_five_particle_API(self):
        called={}
        def convert(data,**kwargs):
            called.update(kwargs)
            return {"data":data}
        ret=h.run(model(),decays(),production(),lambda obj:"HB TEST",
                  lambda obj:155.,conversion=convert,
                  bounds_constructor=lambda _:None,signals_constructor=lambda _:None)
        self.assertEqual(called["neutralIds"],["h","H","A"])
        self.assertEqual(called["singleChargedIds"],["H1","H2"])
        self.assertEqual(called["doubleChargedIds"],[])
        self.assertFalse(ret["all_physical_model_constraints_tested"])
        self.assertIsNone(ret["full_Zee_allowed_or_excluded"])
        self.assertEqual(ret["HiggsSignals_chi2"],155.)

    def test_invalid_b4_duplicate_and_false_allowed_input(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"x.csv";csvpoints(p)
            self.assertEqual(len(c.read_points(p)),1)
            data=p.read_text();p.write_text(data+data.splitlines()[1]+"\n")
            with self.assertRaisesRegex(ValueError,"duplicate"):
                c.read_points(p)
            p.write_text(data.replace("SCALAR_EWPO_SCREEN_ONLY_NOT_ALLOWED",
                                      "EXPERIMENTALLY_ALLOWED"))
            with self.assertRaisesRegex(ValueError,"cannot be called allowed"):
                c.read_points(p)

    def test_export_wrong_stage_provenance_and_unknown_id_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"b.json"
            body={"schema_version":1,"stage":"neutrino",
             "provenance":{"source":"synthetic test"},
             "records":[{"candidate_id":"B4_0004143"}]}
            p.write_text(json.dumps(body))
            rows,ref=c.load_export(p,"neutrino",{"B4_0004143":model()})
            self.assertIn("B4_0004143",rows)
            body["stage"]="lfv";p.write_text(json.dumps(body))
            with self.assertRaisesRegex(ValueError,"wrong stage"):
                c.load_export(p,"neutrino",{"B4_0004143":model()})
            body["stage"]="neutrino"
            body["records"][0]["candidate_id"]="other"
            p.write_text(json.dumps(body))
            with self.assertRaisesRegex(ValueError,"unknown/duplicate"):
                c.load_export(p,"neutrino",{"B4_0004143":model()})

    def test_single_entry_CLI_reports_all_missing_and_shas(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d);csvpoints(path/"points.csv")
            out=path/"output"
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(cli.main([
                    "--points",str(path/"points.csv"),
                    "--out",str(out)]),0)
            report=json.loads((out/"summary.json").read_text())
            self.assertEqual(report["points"],1)
            self.assertIsNone(report["full_Zee_model_allowed_or_excluded"])
            self.assertTrue(all(
              "BLOCKED_NO_BACKEND_INPUT" in report[
                "per_component_status_counts"][s]
              for s in c.REQUIRED))
            self.assertEqual(len((out/"per_candidate.jsonl").read_text().splitlines()),1)
            with self.assertRaises(SystemExit):
                cli.main(["--points",str(path/"points.csv"),
                          "--out",str(out)])
            with self.assertRaises(SystemExit):
                cli.main(["--points",str(path/"points.csv"),
                          "--out",str(path/"new"),"--require-all-inputs"])

    def test_externally_claimed_completed_numerical_sources_still_no_exclusion(self):
        d={k:{model()["candidate_id"]:v} for k,v in
           (("neutrino",neutrino()),("lfv",lfv()),
            ("bsgamma",bsgamma()),("decays",decays()),
            ("production",production()))}
        row=c.evaluate({model()["candidate_id"]:model()},d)[0]
        self.assertTrue(row["all_priority1_backend_inputs_complete"])
        self.assertIsNone(row["experimental_Zee_allowed_or_excluded"])
        self.assertFalse(row["complete_global_likelihood_implemented"])

if __name__=="__main__":
    unittest.main()
