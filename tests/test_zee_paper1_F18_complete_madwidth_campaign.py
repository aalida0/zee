#!/usr/bin/env python3
"""Single F18 campaign-level integration regression using synthetic MadWidth
tables. It tests parsing, 2-body resonance bootstrap, 2+3-body branching
fractions and real-F17f amplitude-closure logic. It does NOT execute MG5;
the user's actual SARAH UFO is only exercised by F18 local one-shot.
"""
from pathlib import Path
import math,sys,tempfile,unittest,json,io,contextlib,hashlib,tarfile,os
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from zee_paper1_F18_archive_local_success import pack as archive_local_success
from zee_paper1_F18_merge_condor_results import merge as merge_completed_cases
from zee_paper1_F18_complete_madwidth_campaign import (
    SCALARS,read_slha,validate_case_outcomes,validate_table,command_deck,
    ensure_consistent_2body_stage,check_MadWidth_input_preserved,
    do_madwidth,diagnose_existing_campaign,madwidth_log_diagnostic,
    derive_internal_W_mass,prepare_madwidth_W_mass_card)


def mk_fixture(extra=False,lepton_split=3):
    neutral={25:(.004,[(.004,[5,-5])]),35:(1.,[(1.,[5,-5])]),
             36:(1.,[(1.,[5,-5])])}
    data={**neutral}
    # Fake model where +37 is H1+, +9000037 H2+.
    h1=[(16.,[6,-5]),(3.4,[24,25])]
    h2=[(6.,[37,23]),(2.,[6,-5]),(1.9,[37,25])]
    for base,leptons in ((h1,(.1,.2,.3)),(h2,(.02,.03,.05))):
        for pdg,total in zip((11,13,15),leptons):
            for nu in (12,14,16):
                base.append((total/3,[-pdg,nu]))
    if extra:
        h1.append((.2,[24,5,-5]))
        h2.append((.5,[24,5,-5]))
    data[37]=(20.+(.2 if extra else 0.),h1)
    data[9000037]=(10.+(.5 if extra else 0.),h2)
    mw=91.1876*math.sqrt(1-0.23122)
    lines=["BLOCK MASS"," 24 "+format(mw,".17e")," 25 125"," 35 725"," 36 450"," 37 570",
           " 9000037 880","BLOCK SMINPUTS"," 1 127.95",
           "BLOCK CHARGEMIX"," 2 3 0.89"]
    for pid in SCALARS:
        width,channels=data[pid]
        lines.append("DECAY "+str(pid)+" "+format(width,".17e"))
        for partial,daughters in channels:
            lines.append("  "+format(partial/width,".17e")+
                         " "+str(len(daughters))+" "+" ".join(map(str,daughters)))
    return "\n".join(lines)+"\n"


def case_ref():
    f17f={"independent_F16_B3_complex_lepton_width_target_GeV":{
        "H1":{"e":.1,"mu":.2,"tau":.3},
        "H2":{"e":.02,"mu":.03,"tau":.05}},
        "actual_UFO_charged_H_quark_width_checks":[{
            "H":"H1","up":"t","down":"b",
            "source_F15_CKM_completed_width_GeV":16.}]}
    f17e={"actual_UFO_H2_H1Z_partial_width_GeV":6.}
    return f17f,f17e


class F18CampaignRegression(unittest.TestCase):
    def test_one_campaign_2body_then_2plus3_body_and_independent_tree_matches(self):
        vals={("MASS",(25,)):125.,("MASS",(35,)):725.,
              ("MASS",(36,)):450.,("MASS",(37,)):570.,
              ("MASS",(9000037,)):880.,("SMINPUTS",(1,)):127.95,
              ("CHARGEMIX",(2,3)):.89}
        c,e=case_ref()
        with tempfile.TemporaryDirectory() as d:
            first=Path(d)/"two_body.slha"
            last=Path(d)/"two_plus_three.slha"
            first.write_text(mk_fixture())
            last.write_text(mk_fixture(extra=True))
            for card in (first,last):
                _,tables,_=check_MadWidth_input_preserved(card,vals)
                for pid in SCALARS:
                    validate_table(tables,pid,three_body=card==last)
            result=validate_case_outcomes("F13_heavy_0001330",vals,first,last,c,e,1)
            self.assertAlmostEqual(result["BR_H2_H1_Z_model_LO_2plus3"],6/10.5)
            self.assertAlmostEqual(result["BR_H1_tb_model_LO_2plus3"],16/20.2)
            self.assertAlmostEqual(result["charged_H_decay_tables"]["9000037"]
                                   ["three_body_sum_GeV"],.5)
            self.assertEqual(result["max_2body_stability_relative"],0.)
            self.assertAlmostEqual(result["source_amplitude_validation_two_plus_three"]
                                   ["Z_and_tb"]["H1_tb"]["relative"],0.)
            self.assertGreater(result["cascade_BR_product_model_LO_2plus3"],0.)
            self.assertFalse(result["model_fully_allowed"])

    def test_internal_sarah_MWm_is_source_matched_and_copied_not_modified(self):
        # Real bug: 258 UFO external parameters exclude W MASS(24), but
        # MadWidth's LHE numeric mass parser demands an explicit PDG 24.
        # The remedy is a run-local copied card, not a model regeneration.
        mz=91.1876
        values={("MASS",(23,)):mz,("MASS",(37,)):570.}
        pars={
            "MZ":{"nature":"external","name":"MZ","type":"real",
                  "lhablock":"MASS","lhacode":[23],"value":91.1876},
            "MWm":{"nature":"internal","name":"MWm","type":"real",
                   "value":"MZ*cmath.sqrt(1-0.23122)"}
        }
        particles={"Wp":{"pdg_code":24,
                         "mass":{"python_expression":"Param.MWm"}}}
        def fake_parse(_root,basename,_kind):
            return pars if basename=="parameters.py" else particles
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            old=root/"F17f_unchanged.slha"
            fixed=root/"F18_temporary_with_MW.slha"
            old.write_text("BLOCK MASS\n 23 9.11876000000000000e+01\n"
                           " 37 5.70000000000000000e+02\n"
                           "DECAY 37 0.0\n")
            snapshot=old.read_bytes()
            with patch("zee_paper1_F18_complete_madwidth_campaign.parse_objects",
                       side_effect=fake_parse),patch(
                "zee_paper1_F18_complete_madwidth_campaign.slots_from_real_ufo",
                return_value={("MASS",(23,)):"MZ"}):
                mass=derive_internal_W_mass(root,values)
                self.assertAlmostEqual(mass,
                    mz*math.sqrt(1-0.23122),places=12)
                meta=prepare_madwidth_W_mass_card(old,fixed,root,values)
                self.assertEqual(meta["new_UFO_external_parameters"],0)
                self.assertAlmostEqual(meta["derived_internal_MWm_GeV"],mass)
            self.assertEqual(old.read_bytes(),snapshot)
            masses,_,_ = read_slha(fixed)
            self.assertIn(24,masses)
            self.assertAlmostEqual(masses[24],mass,places=12)
            self.assertEqual(fixed.read_text().count("  24 "),1)
            with self.assertRaises(FileExistsError):
                prepare_madwidth_W_mass_card(old,fixed,root,values)

    def test_W_mass_mismatch_with_source_is_rejected(self):
        vals={("MASS",(23,)):91.1876}
        pars={"MZ":{"nature":"external","name":"MZ","type":"real"},
              "MWm":{"nature":"internal","name":"MWm","type":"real",
                     "value":"MZ*0.80"}}
        particles={"W":{"pdg_code":24,
                        "mass":{"python_expression":"Param.MWm"}}}
        with patch("zee_paper1_F18_complete_madwidth_campaign.parse_objects",
                   side_effect=lambda _root,basename,_kind:
                   pars if basename=="parameters.py" else particles),patch(
                   "zee_paper1_F18_complete_madwidth_campaign.slots_from_real_ufo",
                   return_value={("MASS",(23,)):"MZ"}):
            with self.assertRaisesRegex(ValueError,
                                        "contradicts F16 electroweak"):
                derive_internal_W_mass(Path("."),vals)


    def test_condor_worker_does_not_precreate_f18_output(self):
        worker=(Path(__file__).resolve().parents[1]/"scripts"/
                "zee_paper1_F18_condor_worker.sh").read_text()
        self.assertNotIn("mkdir -p F18_job_output",worker)
        self.assertIn('if [[ -e F18_job_output ]]',worker)
        self.assertIn('--output "$scratch/F18_job_output"',worker)
        self.assertIn('F18_CONDOR_OUTPUT_ALREADY_EXISTS_REFUSE_OVERWRITE',worker)

    def test_reuse_completed_local_one_and_merge_two_condor_cases(self):
        # The real user stopped the monolithic F18 process in benchmark 2;
        # the all-three summary.json does NOT necessarily exist. Preserve
        # the already validated per-case 1330 without recomputing it.
        def digest(path):
            return hashlib.sha256(Path(path).read_bytes()).hexdigest()
        def addfile(tar,name,raw):
            entry=tarfile.TarInfo(name)
            entry.size=len(raw)
            tar.addfile(entry,io.BytesIO(raw))
        status="F18_REAL_SARAH_ZEE_MADWIDTH_2AND3_BODY_3_CASES_MODEL_LO_NOT_EXCLUSION"
        cases=("F13_heavy_0001330","F13_heavy_0000981","F13_heavy_0001003")
        with tempfile.TemporaryDirectory() as d:
            base=Path(d)
            f17f=base/"F17f_real_UFO_unitary_complex_CKM_mock"
            f17f.mkdir()
            card=f17f/"orig_1330.slha";card.write_text("BLOCK MASS\n 37 500\n")
            f17f_report=f17f/"report.json"
            f17f_report.write_text(json.dumps({
                "CKM_candidate_cards":[{"candidate_id":cases[0],
                                        "file":card.name,"sha256":digest(card)}]}))
            source={"status":status,"MG5_binary_SHA256":"a"*64,
                    "original_F17f_report_SHA256":digest(f17f_report),
                    "F14_original_13TeV_CSV_SHA256":None,
                    "source_independent_CKM_and_lepton_amplitudes_validated_before_run":True,
                    "errors":{}}
            def result(name):
                return {"candidate_id":name,
                        "BR_H2_H1_Z_model_LO_2plus3":.45,
                        "BR_H1_tb_model_LO_2plus3":.99,
                        "cascade_BR_product_model_LO_2plus3":.45*.99,
                        "charged_H_decay_tables":{
                            "37":{"total_GeV":.3,"three_body_fraction":.01},
                            "9000037":{"total_GeV":13.,"three_body_fraction":.12}},
                        "provenance":{}}
            local=base/"F18_MadWidth_exact_three_interrupted"
            root=local/cases[0]
            root.mkdir(parents=True)
            (local/"initial_manifest.json").write_text(json.dumps(source))
            good=result(cases[0])
            good["provenance"]["source_F17f_card_SHA256"]=digest(card)
            for step,filename in (("MadWidth_two_body","two_body.slha"),
                                  ("MadWidth_two_plus_three","two_plus_three_body.slha")):
                file=root/filename
                file.write_text("BLOCK MASS\n 37 500\nDECAY 37 0.3\n")
                good["provenance"][step]={"output_SHA256":digest(file)}
            (root/"validated_model_LO_widths.json").write_text(json.dumps(good))
            results_dir=base/"results";results_dir.mkdir()
            archive=results_dir/("F18_local_completed_"+cases[0]+".tar.gz")
            archive_local_success(local,cases[0],archive)
            self.assertTrue(archive.is_file())
            self.assertFalse((local/"summary.json").exists())
            for name in cases[1:]:
                row=result(name)
                row["provenance"]={
                    "MadWidth_two_body":{"output_SHA256":"b"*64},
                    "MadWidth_two_plus_three":{"output_SHA256":"c"*64}}
                job_summary={**source,"requested_cases":[name],
                             "requested_cases_passed":True,
                             "results":[row]}
                tarpath=results_dir/("F18_result_"+name+".tar.gz")
                with tarfile.open(tarpath,"w:gz") as fh:
                    addfile(fh,name+"/worker_exit_code.txt",b"0\n")
                    addfile(fh,name+"/summary.json",json.dumps(job_summary).encode())
                    addfile(fh,name+"/validated_model_LO_widths.json",
                            json.dumps(row).encode())
            final=base/"merged"
            report=merge_completed_cases(results_dir,final)
            self.assertEqual(len(report["benchmarks"]),3)
            self.assertEqual(set(x["candidate_id"] for x in report["benchmarks"]),
                             set(cases))
            self.assertEqual(report["per_benchmark_source_archives"][cases[0]]["origin"],
                             "previously_completed_LOCAL_F18_not_a_Condor_job")
            self.assertAlmostEqual(report["benchmarks"][0]["cascade_BR_product_model_LO_2plus3"],
                                   .45*.99)
            self.assertTrue((final/"F18_CONDOR_three_summary.csv").exists())

    def test_local_reuse_refuses_modified_source_slha(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/"F18_interrupted";(root/"F13_heavy_0001330").mkdir(parents=True)
            (root/"initial_manifest.json").write_text('{"status":"invalid"}')
            with self.assertRaises((ValueError,FileNotFoundError)):
                archive_local_success(root,"F13_heavy_0001330",
                    Path(d)/"will_not_be_created.tar.gz")

    def test_actual_bug_mg5_returns_zero_but_writes_no_card(self):
        # MG5 command-file mode may return exit code 0 despite a command
        # failure visible in the log. This exact regression must never
        # pass as a physics card.
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            mg5=root/"dummy_mg5"
            mg5.write_text("#!/bin/sh\necho 'ERROR: invalid compute_widths in test'\nexit 0\n")
            mg5.chmod(0o755)
            card=root/"source.slha"
            card.write_text("BLOCK MASS\n 37 500\n")
            job=root/"stage_2body"
            dest=root/"expected.slha"
            with self.assertRaisesRegex(RuntimeError,
                                       "returncode=0"):
                do_madwidth(mg5,root/"original_ufo",card,dest,job,2)
            diagnostic=json.loads((job/"mg5_diagnostic.json").read_text())
            self.assertEqual(diagnostic["returncode"],0)
            self.assertFalse(diagnostic["expected_output_exists"])
            self.assertTrue(diagnostic["log_error_contexts"])
            self.assertIn("invalid compute_widths",
                          diagnostic["log_error_contexts"][0]["context"])
            self.assertEqual(card.read_text(),"BLOCK MASS\n 37 500\n")

    def test_original_failed_F18_archived_diagnosis_without_rerun(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/"F18_existing"
            job=root/"F13_heavy_0001330"/"stage_2body"
            job.mkdir(parents=True)
            (job/"madwidth.log").write_text(
                "import model original\nTraceback (most recent call last):\n"
                "ERROR: original interface model has bad parameter\n")
            stream=io.StringIO()
            with contextlib.redirect_stdout(stream):
                diagnose_existing_campaign(root)
            self.assertIn("F18_DIAGNOSTIC_LOG_ERROR_LINE",stream.getvalue())
            self.assertIn("NO_MG5_EXECUTION",stream.getvalue())

    def test_missing_resonance_or_incomplete_model_is_blocker(self):
        vals={("MASS",(25,)):125.,("MASS",(35,)):725.,
              ("MASS",(36,)):450.,("MASS",(37,)):570.,
              ("MASS",(9000037,)):880.,("SMINPUTS",(1,)):127.95,
              ("CHARGEMIX",(2,3)):.89}
        c,e=case_ref()
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"2.slha";f=Path(d)/"3.slha"
            p.write_text(mk_fixture())
            broken=mk_fixture(extra=True).replace(" 37 23"," 35 23")
            f.write_text(broken)
            with self.assertRaises(ValueError):
                validate_case_outcomes("bad",vals,p,f,c,e,1)
            f.write_text(mk_fixture(extra=True).replace("DECAY 9000037","DECAY 999999"))
            _,tables,_=read_slha(f)
            with self.assertRaises(ValueError):
                validate_table(tables,9000037,three_body=True)

    def test_source_not_overwritten_and_finite_widths(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"test.slha"
            p.write_text(mk_fixture())
            raw=p.read_bytes()
            _,tables,_=read_slha(p)
            self.assertEqual(p.read_bytes(),raw)
            with self.assertRaises(ValueError):
                read_slha(self._corrupt_card(
                    Path(d),mk_fixture().replace("DECAY 37 2.","DECAY 37 -2.")))
            text=command_deck(Path(d)/"UFO",p,Path(d)/"result.slha",body_decay=3)
            self.assertIn("compute_widths 25 35 36 37 9000037",text)
            self.assertIn("--body_decay=3",text)
            self.assertIn("--min_br=0.0",text)
            self.assertIn("--precision_channel=0.01",text)
            c2=command_deck(Path(d)/"UFO",p,Path(d)/"result.slha",
                            body_decay=3,nb_core=2)
            self.assertIn("set run_mode 2",c2)
            self.assertIn("set nb_core 2",c2)
            self.assertIn("compute_widths 25 35 36 37 9000037",c2)
    @staticmethod
    def _corrupt_card(directory,text):
        path=directory/"bad.slha";path.write_text(text);return path

if __name__=="__main__":unittest.main()
