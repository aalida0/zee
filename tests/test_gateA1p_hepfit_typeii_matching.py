"""Gate A1P tests: independent reference integrity, parser and mismatches.

Synthetic matching examples do not certify HEPfit/SuperIso agreement.
"""
import hashlib
import json
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/"scripts"))

from gateA1p_prepare_hepfit_matching import extract,git_blob_sha,generate
from gateA1p_audit_running_top import audit as audit_mt_source
from gateA1p_compare_hepfit_matching import (
    read_hepfit,compare_mass,report,TOLERANCES
)

def example_hepfit_source():
    return (
        "/* Copyright (C) HEPfit Collaboration; GPL upstream test fixture */\n"
        "#include \"THDMMatching.h\"\n"
        "double THDMMatching::setWCbsg(int i,double tan,double mt,"
        "double mhp,double mu,orders order) {\n"
        " double Li2=gsl_sf_dilog(1.-1./x);\n"
        " CWbsgArrayNNLO[6]=0.; CWbsgArrayNNLO[7]=0.;\n"
        " CWbsgArrayNLO[6]=0.; CWbsgArrayNLO[7]=0.;\n"
        " CWbsgArrayLO[6]=0.; CWbsgArrayLO[7]=0.;\n"
        " return 0.;\n"
        "}\n"
    )

def matching_value(order,op,mass):
    # Distinct synthetic values with exact referential closure.
    if order==0 and op in (7,8): return -.12*(300./mass)*(9.-op)
    if order==1 and op in (4,7,8): return .07*op*(300./mass)
    if order==2 and op in (3,4,5,6,7,8): return -.15*op*(300./mass)
    return 0.

def write_pair(root,mass,beta=1.394,modified=None):
    import math
    hf=root/f"hepfit_{mass}.txt"
    si=root/f"superiso_{mass}.txt"
    linesh=["HEPFIT_SOURCE_ONLY_NOT_PHYSICAL_BR",
            f"INPUT mass={mass} tanbeta={math.tan(beta):.17g} "
            f"mt_muW=163.10709645657502 muW=160.7384"]
    liness=[
        "STATUS MATCHING_WILSON_PILOT_NO_PHYSICAL_BR_VENDOR_NLO_C7_C8_AUDIT_REQUIRED",
        "INPUT mH1=%g mH2=%g beta=1.394 gamma=0 "
        "tanbeta=%.17g muW=160.7384 w1=1 w2=0"
        % (mass,mass+1,math.tan(beta))
    ]
    for order in range(3):
        for op in range(1,11):
            value=matching_value(order,op,mass)
            if op<=8:
                linesh.append(
                    f"HEPFIT order={order} op={op} "
                    f"delta={value:.17g} mass={mass}")
            obs=value
            if modified == (order,op):
                obs+=0.4
            liness.append(f"COEFF order={order} i={op} sm=0 "
                          f"delta1={obs:.17g} delta2={obs:.17g} "
                          f"zee={obs:.17g}")
    hf.write_text("\n".join(linesh)+"\n")
    si.write_text("\n".join(liness)+"\n")
    return si,hf

class TestGateA1P(unittest.TestCase):
    def setUp(self):
        d=tempfile.TemporaryDirectory()
        self.addCleanup(d.cleanup)
        self.root=pathlib.Path(d.name)
        self.manifest=self.root/"manifest.json"
        self.manifest.write_text(json.dumps({
            "upstream_git_blob":"8029be52c3e2f83490dfe3199f80e5db484dd23b"
        }))

    def test_git_blob_sha_standard(self):
        self.assertEqual(git_blob_sha(b"hello world\n"),
                         "3b18e512dba79e4c8300dd08aeb37f8e728b8dad")

    def test_extract_unmodified_formula_only(self):
        source=example_hepfit_source()
        content=extract(source)
        self.assertIn("gsl_sf_dilog",content)
        self.assertIn("CWbsgArrayNNLO[6]",content)
        self.assertFalse("class THDMMatching" in content)

    def test_duplicate_function_is_rejected(self):
        with self.assertRaises(ValueError):
            extract(example_hepfit_source()*2)

    def test_audit_top_mass_source_accepts_pinned_A1M_contents(self):
        path=self.root/"wilson.c"
        content="double mass_top_muW = running_mass(param->mass_top_pole, muW);\n"
        path.write_text(content)
        digest=hashlib.sha256(content.encode()).hexdigest()
        item=audit_mt_source(path,expected_sha=digest)
        self.assertIn("SOURCE_AUDIT",item["status"])
        self.assertFalse(item["mt_muW_source_value_directly_evaluated"])

    def test_audit_top_mass_source_rejects_wrong_hash(self):
        path=self.root/"wilson.c"
        path.write_text("double mass_top_muW = 163.0;\n")
        with self.assertRaises(ValueError):
            audit_mt_source(path,expected_sha="x"*64)

    def test_unknown_source_revision_rejected(self):
        source=self.root/"source.cpp"
        source.write_text(example_hepfit_source())
        with self.assertRaisesRegex(ValueError,"Unrecognized independent"):
            generate(source,self.root/"generated.cpp",
                     self.root/"manifest_a.json")
        self.assertFalse((self.root/"generated.cpp").exists())

    def test_pinned_synthetic_source_can_generate(self):
        source=self.root/"source.cpp"
        raw=example_hepfit_source().encode()
        source.write_bytes(raw)
        manifest=self.root/"generated_manifest.json"
        cpp=self.root/"shim.cpp"
        r=generate(source,cpp,manifest,expected_blob=git_blob_sha(raw))
        self.assertEqual(r["upstream_git_blob"],git_blob_sha(raw))
        self.assertIn("HEPFIT_SOURCE_ONLY_NOT_PHYSICAL_BR",cpp.read_text())
        self.assertFalse(r["physical_BtoXs_gamma_validated"])

    def test_reference_row_integrity(self):
        _,hf=write_pair(self.root,300)
        inp,values=read_hepfit(hf)
        self.assertEqual(len(values),24)
        self.assertEqual(inp["mass"],300)
        self.assertEqual(values[0,7],matching_value(0,7,300))

    def test_pilot_matching_four_masses_pass(self):
        pairs=[(m,*write_pair(self.root,m)) for m in (300,700,1000,2000)]
        result=report(pairs,1.394,self.manifest)
        self.assertEqual(result["failed_count"],0)
        self.assertEqual(result["compared_count"],4*(2+3+6))
        self.assertFalse(result["full_bsgamma_independently_validated"])
        self.assertIsNone(result["Zee_benchmark_excluded"])

    def test_nlo_mismatch_detected(self):
        si,hf=write_pair(self.root,700,modified=(1,7))
        rows,inp=compare_mass(si,hf,700,1.394)
        self.assertFalse(next(x for x in rows
            if x["order"]==1 and x["operator"]=="C7")["numerically_consistent"])

    def test_nnlo_mismatch_detected(self):
        si,hf=write_pair(self.root,300,modified=(2,8))
        rows,inp=compare_mass(si,hf,300,1.394)
        self.assertFalse(next(x for x in rows
            if x["order"]==2 and x["operator"]=="C8")["numerically_consistent"])

    def test_matching_scale_difference_rejected(self):
        si,hf=write_pair(self.root,300)
        hf.write_text(hf.read_text().replace("muW=160.7384","muW=165.0"))
        with self.assertRaisesRegex(ValueError,"muW mismatch"):
            compare_mass(si,hf,300,1.394)

    def test_unpinned_reference_rejected(self):
        si,hf=write_pair(self.root,300)
        self.manifest.write_text('{"upstream_git_blob": "wrong"}')
        with self.assertRaisesRegex(ValueError,"unknown HEPfit"):
            report([(300,si,hf)],1.394,self.manifest)

if __name__=="__main__":
    unittest.main()
