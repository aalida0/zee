"""Synthetic Gate A1M regression tests. No vendor physics certified."""
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/"scripts"))
from gateA1m_prepare_isolated_superiso import (
    create_isolated, patch_wilson, digest
)
from gateA1m_compare_matching import compare
from gateA1l_check_matching_pilot import parse

def vendor_source():
    lines=["void CW_calculator(void){",
           "for(ie=1;ie<=10;ie++) C0w[ie]=C1w[ie]=C2w[ie]=0.;"]
    for i in (7,8,9,10):
        h=f"C{i}H_1"
        lines.append(f"if(cabs({h})*alphas_mu/4./pi>cabs(C0w[{i}])) "
                     f"{h}*=cabs(C0w[{i}])/cabs({h})*4.*pi/alphas_mu;")
    for i in (7,8,9,10):
        lines.append(f"C0w[{i}]=42;")
    lines.append("}")
    return "\n".join(lines)+"\n"

def make_output(path,patched):
    lines=[
        "STATUS MATCHING_WILSON_PILOT_NO_PHYSICAL_BR_VENDOR_NLO_C7_C8_AUDIT_REQUIRED",
        "INPUT muW=160.7384 w1=0.21471339018904734 w2=0.7852866098109527"
    ]
    w1=.21471339018904734
    w2=1-w1
    for o in (0,1,2):
        for i in range(1,11):
            sm=float(i+o)/50.
            l=-.012*i/(o+1)
            h=-.004*i/(o+1)
            if o==1 and i in (7,8,9,10) and not patched:
                l=h=0.
            zee=sm+w1*l+w2*h
            lines.append(f"COEFF order={o} i={i} sm={sm:.17g} "
                         f"delta1={l:.17g} delta2={h:.17g} zee={zee:.17g}")
    path.write_text("\n".join(lines)+"\n")

class TestIsolatedPatch(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=pathlib.Path(self.tmp.name)
        self.vendor=self.root/"vendor"
        (self.vendor/"src").mkdir(parents=True)
        (self.vendor/"Makefile").write_text("all:\n\t@echo ok\n")
        (self.vendor/"src"/"wilson.c").write_text(vendor_source())
        self.copy=self.root/"isolated"

    def test_exact_four_lines_changed_no_other_statements(self):
        src=vendor_source()
        patched,rows=patch_wilson(src)
        self.assertEqual(set(rows),{"C7H_1","C8H_1","C9H_1","C10H_1"})
        self.assertEqual(len(patched.splitlines()),len(src.splitlines()))
        for name in rows:
            self.assertIn(f"remove premature zeroing of {name}",patched)
        self.assertEqual(patched.count("DIAGNOSTIC ONLY"),4)

    def test_vendor_copy_is_untouched_and_pinned(self):
        before=(self.vendor/"src/wilson.c").read_bytes()
        r=create_isolated(self.vendor,self.copy,expected_sha=digest(before))
        self.assertEqual(before,(self.vendor/"src/wilson.c").read_bytes())
        self.assertNotEqual(before,(self.copy/"src/wilson.c").read_bytes())
        self.assertEqual(r["changed_statement_count"],4)
        self.assertFalse(r["vendor_source_modified"])
        self.assertFalse(r["physical_Zee_BR_calculated"])

    def test_wrong_source_hash_rejected_before_copy(self):
        with self.assertRaises(ValueError):
            create_isolated(self.vendor,self.copy)
        self.assertFalse(self.copy.exists())

    def test_reject_patch_inside_vendor(self):
        with self.assertRaises(ValueError):
            create_isolated(self.vendor,self.vendor/"build",
                            expected_sha=digest(vendor_source().encode()))

    def test_refuses_overwriting_existing_copy(self):
        self.copy.mkdir()
        with self.assertRaises(FileExistsError):
            create_isolated(self.vendor,self.copy,
                            expected_sha=digest(vendor_source().encode()))

    def test_any_missing_matching_statement_rejected(self):
        content=vendor_source().replace(
            "if(cabs(C8H_1)*alphas_mu/4./pi>cabs(C0w[8]))","if(0)")
        with self.assertRaises(ValueError):
            patch_wilson(content)

    def test_compare_requires_nlo_repaired_only(self):
        native=self.root/"native.txt"
        patched=self.root/"patched.txt"
        make_output(native,False)
        make_output(patched,True)
        r=compare(native,patched,{
            "changed_statement_count":4,
            "changed_symbols":{"C7H_1":1,"C8H_1":2,"C9H_1":3,"C10H_1":4}
        })
        self.assertIn("DIAGNOSTIC",r["status"])
        self.assertEqual(r["max_unchanged_entry_abs_difference"],0.)
        self.assertFalse(r["Zee_benchmark_accepted_or_excluded"])
        self.assertTrue(r["nlo_charged_coefficient_changes"]["C7"]["patched_single_light"] != 0)

    def test_compare_rejects_lo_change(self):
        native=self.root/"native.txt"
        patched=self.root/"patched.txt"
        make_output(native,False)
        make_output(patched,True)
        txt=patched.read_text()
        patched.write_text(txt.replace("order=0 i=7 sm=0.14000000000000001",
                                      "order=0 i=7 sm=0.24000000000000001"))
        # If Python string formatting differs, perturb first order=0 i=7 explicitly.
        if patched.read_text()==txt:
            lines=txt.splitlines()
            ix=next(i for i,v in enumerate(lines) if v.startswith("COEFF order=0 i=7 "))
            lines[ix]=lines[ix].replace("delta1=","sm=9.1 delta1=",1)
            patched.write_text("\n".join(lines)+"\n")
        with self.assertRaises((ValueError,TypeError)):
            compare(native,patched,{
                "changed_statement_count":4,
                "changed_symbols":{"C7H_1":1,"C8H_1":2,"C9H_1":3,"C10H_1":4}
            })

if __name__=="__main__":
    unittest.main()
