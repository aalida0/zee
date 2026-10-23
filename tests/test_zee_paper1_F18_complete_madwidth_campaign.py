#!/usr/bin/env python3
"""Single F18 campaign-level integration regression using synthetic MadWidth
tables. It tests parsing, 2-body resonance bootstrap, 2+3-body branching
fractions and real-F17f amplitude-closure logic. It does NOT execute MG5;
the user's actual SARAH UFO is only exercised by F18 local one-shot.
"""
from pathlib import Path
import math,sys,tempfile,unittest,json,io,contextlib
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from zee_paper1_F18_complete_madwidth_campaign import (
    SCALARS,read_slha,validate_case_outcomes,validate_table,command_deck,
    ensure_consistent_2body_stage,check_MadWidth_input_preserved,
    do_madwidth,diagnose_existing_campaign,madwidth_log_diagnostic)


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
    lines=["BLOCK MASS"," 25 125"," 35 725"," 36 450"," 37 570",
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

    def test_actual_bug_mg5_returns_zero_but_writes_no_card(self):
        # MG5 command-file mode may return exit code 0 despite a command
        # failure visible in the log. This exact regression must never
        # pass as a physics card.
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            mg5=root/"dummy_mg5"
            mg5.write_text("#!/bin/sh\\necho 'ERROR: invalid compute_widths in test'\\nexit 0\\n")
            mg5.chmod(0o755)
            card=root/"source.slha"
            card.write_text("BLOCK MASS\\n 37 500\\n")
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
            self.assertEqual(card.read_text(),"BLOCK MASS\\n 37 500\\n")

    def test_original_failed_F18_archived_diagnosis_without_rerun(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/"F18_existing"
            job=root/"F13_heavy_0001330"/"stage_2body"
            job.mkdir(parents=True)
            (job/"madwidth.log").write_text(
                "import model original\\nTraceback (most recent call last):\\n"
                "ERROR: original interface model has bad parameter\\n")
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
    @staticmethod
    def _corrupt_card(directory,text):
        path=directory/"bad.slha";path.write_text(text);return path

if __name__=="__main__":unittest.main()
