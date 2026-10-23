#!/usr/bin/env python3
"""F17f strict CKM reconstruction, quark rotations and W/Hqq numerical gates.

Unit tests are synthetic; only local original-SARAH-UFO execution is
considered a physics amplitude validation.
"""
from pathlib import Path
import math,sys,unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from zee_paper1_F17f_unitary_CKM_UFO_quark_gate import (
    unitary_ckm_from_f15,make_quark_basis,compare_W_to_ckm,
    spin_half_quark_width,vertex_group,expected_lepton_widths)
from zee_paper1_F15_charged_width_CKM_mass_scheme_audit import VABS,charged_quark_width
from test_zee_paper1_F17d_source_matched_prevalidation_cards import synthetic_case


class TestF17f(unittest.TestCase):
    def test_f15_complex_unitary_completion(self):
        mat,meta=unitary_ckm_from_f15()
        self.assertLess(meta["unitarity_max_abs"],1e-13)
        self.assertLess(meta["F15_input_magnitude_max_abs_delta"],3e-5)
        self.assertGreater(meta["delta_rad"],0)
        self.assertTrue(any(abs(z.imag)>1e-6 for z in mat.flatten()))
        np.testing.assert_allclose(mat@mat.conj().T,np.eye(3),atol=1e-13)
        self.assertLess(np.max(abs(abs(mat)-VABS)),3e-5)
        self.assertAlmostEqual(float(abs(mat[2,0])),.00854,places=8)

    def test_source_down_mass_basis_complex_provenance(self):
        row,_=synthetic_case()
        v,details=unitary_ckm_from_f15()
        values,meta=make_quark_basis({},row,v)
        self.assertLess(meta["down_mass_basis_residual"],1e-12)
        zdl=np.array([[complex(values[("UDLMIX",(i,j))],
                                  values[("IMUDLMIX",(i,j))])
                       for j in range(1,4)] for i in range(1,4)])
        yd=np.array([[complex(values[("YD",(i,j))],values[("IMYD",(i,j))])
                       for j in range(1,4)] for i in range(1,4)])
        expected=yd@zdl.conj().T
        self.assertLess(float(np.max(abs(expected-np.diag(np.diag(expected))))),1e-12)
        self.assertTrue(np.any(abs(np.imag(zdl))>1e-6))
        self.assertTrue(np.any(abs(np.imag(yd))>1e-8))

    def test_real_W_vertex_magnitude_gate(self):
        v,_=unitary_ckm_from_f15()
        fake=[]
        for i,u in enumerate((2,4,6)):
            for j,d in enumerate((1,3,5)):
                g=.65/math.sqrt(2)*abs(v[i,j])
                fake.append({"vertex":f"W{i}{j}","pdgs":[-u,d,24],
                             "couplings":[{"colour":0,
                                  "structure":"Gamma(3,2,1)*ProjM(2,1)",
                                  "absolute":g}]})
        picked=vertex_group(fake,{tuple(sorted((24,u,d)))
                                   for u in (2,4,6) for d in (1,3,5)})
        self.assertEqual(len(picked),9)
        rows,err=compare_W_to_ckm(picked,v,.65)
        self.assertEqual(len(rows),9)
        self.assertLess(err,1e-13)
        fake[0]["couplings"][0]["absolute"] *= 1.1
        _,err=compare_W_to_ckm(fake,v,.65)
        self.assertGreater(err,.09)

    def test_quark_width_interference_and_CKM(self):
        row,_=synthetic_case()
        ckm,_=unitary_ckm_from_f15()
        gamma=row["gamma_rad"];tanb=math.tan(row["beta_rad"]);v=row["vev_GeV"]
        M=row["mH1_GeV"];mt=172.;mb=4.7
        vt=ckm[2,2]
        # Common relative phase must not affect the spin trace.
        l=math.sqrt(2)*mt/(v*tanb)*math.cos(gamma)*vt
        r=math.sqrt(2)*mb*tanb/v*math.cos(gamma)*vt
        values={("MASS",(37,)):M,("MASS",(6,)):mt,("MASS",(5,)):mb}
        vertex={"pdgs":[-6,5,37],"couplings":[
            {"structure":"ProjM(2,1)","colour":0,"value_re":l.real,"value_im":l.imag},
            {"structure":"ProjP(2,1)","colour":0,"value_re":r.real,"value_im":r.imag}]}
        measured=spin_half_quark_width(vertex,values,6,5,37)
        expected=charged_quark_width(M,"t","b",tanb,math.cos(gamma)**2,
                  mb=mb)*(abs(vt)/VABS[2,2])**2
        self.assertAlmostEqual(measured/expected,1.,delta=2e-5)
        vertex["couplings"][1]["value_re"]*=-1
        vertex["couplings"][1]["value_im"]*=-1
        broken=spin_half_quark_width(vertex,values,6,5,37)
        self.assertGreater(abs(broken-measured),1e-5)

    def test_b3_complex_width_target_source(self):
        row,_=synthetic_case()
        # The generic F17d regression fixture omits YChen; reconstruct its
        # exact Higgs-basis matrix from Ye and Ye2 before computing widths.
        modified=dict(row)
        modified["matrices_re_im"]=dict(row["matrices_re_im"])
        mat=[[list(x) for x in line] for line in row["matrices_re_im"]["YChen"]] if "YChen" in row["matrices_re_im"] else None
        # F17d test fixture only contains Ye/Ye2. Build the YChen matrix
        # consistently from the weak source using the Higgs basis rotation.
        beta=row["beta_rad"]
        mat=[[[(-math.sin(beta)*complex(*row["matrices_re_im"]["YeSARAH"][i][j])
                +math.cos(beta)*complex(*row["matrices_re_im"]["Ye2SARAH"][i][j])).real/math.sqrt(2),
                (-math.sin(beta)*complex(*row["matrices_re_im"]["YeSARAH"][i][j])
                +math.cos(beta)*complex(*row["matrices_re_im"]["Ye2SARAH"][i][j])).imag/math.sqrt(2)]
                for j in range(3)] for i in range(3)]
        modified["matrices_re_im"]["YChen"]=mat
        result=expected_lepton_widths(modified)
        self.assertGreater(result["H1"]["e"],0.)
        copied=[[[x[0],x[1]] for x in line] for line in mat]
        copied[0][0][1]+=0.2
        modified["matrices_re_im"]["YChen"]=copied
        changed=expected_lepton_widths(modified)
        self.assertGreater(changed["H1"]["e"],result["H1"]["e"])


if __name__=="__main__": unittest.main()
