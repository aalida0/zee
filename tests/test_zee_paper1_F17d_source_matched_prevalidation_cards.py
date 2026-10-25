#!/usr/bin/env python3
"""F17d synthetic interface and complex SLHA regressions, NOT physics validation."""
import json,math,sys,tempfile,csv,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from zee_paper1_F17d_source_matched_prevalidation_cards import (
    slots_from_real_ufo,verify_csv,values_for_source,check_slots,
    lepton_mass_error,render,actual_ufo_gauge)

def fake_ufo_parameters():
    params={}
    def add(block,code):
        name="EXTERNAL"+str(len(params))
        params[name]=dict(name=name,nature="external",type="real",value=0.,
                          lhablock=block,lhacode=list(code))
    for k in (1,2,3,4,5,6,11,13,15,23,25,35,36,37,9000037):
        add("MASS",(k,))
    for k in (6,23,24,25,35,36,37,9000037):
        add("DECAY",(k,))
    for block in ("YU","YD","YE","YEE2","FZEE",
                  "UDLMIX","UDRMIX","UULMIX","UURMIX","UELMIX","UERMIX"):
        for i in range(1,4):
            for j in range(1,4):
                add(block,(i,j));add("IM"+block,(i,j))
    for i in range(1,10):add("ZEEQUARTIC",(i,))
    add("ZEEPOT",(5,))
    for block,n in (("CHARGEMIX",3),("SCALARMIX",2),("PSEUDOSCALARMIX",2)):
        for i in range(1,n+1):
            for j in range(1,n+1):add(block,(i,j))
    for i in (1,2,3):add("SMINPUTS",(i,))
    add("HMIX",(10,))
    for i in (25,35,36):
        for j in (21,22):add("EFFHIGGSCOUPLINGS",(i,j,j))
    assert len(params)==258
    return params

def synthetic_case():
    beta,gamma,alpha,v=1.394,1.089,.2,246.22
    sb,cb=math.sin(beta),math.cos(beta)
    sg,cg=math.sin(gamma),math.cos(gamma)
    masses=(.000511,.10566,1.77686)
    y=[[complex(0.004*(i-j),0.003*(i+j+1)) for j in range(3)]
       for i in range(3)]
    dm=lambda i,j:math.sqrt(2)*masses[i]/v if i==j else 0.
    ye=[[cb*dm(i,j)-sb*y[i][j] for j in range(3)] for i in range(3)]
    ye2=[[sb*dm(i,j)+cb*y[i][j] for j in range(3)] for i in range(3)]
    f=[[complex(.001*(i-j),.002*(i+j+1)) if i<j
        else (-complex(.001*(j-i),.002*(i+j+1)) if i>j else 0j)
        for j in range(3)] for i in range(3)]
    zp=[[cb,sb,0],[-sb*cg,cb*cg,sg],[sb*sg,-cb*sg,cg]]
    zh=[[math.cos(alpha),math.sin(alpha)],[-math.sin(alpha),math.cos(alpha)]]
    za=[[cb,sb],[-sb,cb]]
    encode=lambda matrix:[[[complex(z).real,complex(z).imag] for z in line]
                          for line in matrix]
    row=dict(candidate_id="F13_heavy_0001330",beta_rad=beta,gamma_rad=gamma,
             vev_GeV=v,lepton_masses_GeV=masses,
             mH1_GeV=572.2,mH2_GeV=873.2,mHeavyNeutral_GeV=700.,
             mA_GeV=460.,
             matrices_re_im=dict(FSARAH=encode(f),YeSARAH=encode(ye),
                Ye2SARAH=encode(ye2),MixCharged=encode(zp),
                MixCPeven=encode(zh),MixCPodd=encode(za)))
    rules={k:float(i+1) for i,k in enumerate(
          ["Mu4","Lambda1","Lambda2","Lambda3","Lambda4","Lambda5",
           "LambdaC","K1","K2","K12"])}
    return row,{"sarah_2VEV_lagrangian_rules":rules}

class TestF17d(unittest.TestCase):
    def test_258_slots_and_complex_phases(self):
        slots=slots_from_real_ufo(fake_ufo_parameters())
        row,case=synthetic_case()
        values=values_for_source(row,case)
        check_slots(slots,values)
        self.assertLess(lepton_mass_error(row,values),1e-10)
        self.assertNotEqual(values[("IMYE",(1,2))],0.)
        self.assertNotEqual(values[("IMYEE2",(2,1))],0.)
        self.assertNotEqual(values[("IMFZEE",(1,2))],0.)
        self.assertEqual(values[("MASS",(9000037,))],873.2)
        self.assertEqual(values[("ZEEQUARTIC",(6,))],7.)
        output=render(slots,values,row["candidate_id"])
        for text in ("BLOCK CHARGEMIX","BLOCK IMYE","BLOCK IMFZEE",
                     "BLOCK IMYEE2","DECAY 9000037",
                     "NOT MADWIDTH READY","CKM=IDENTITY"):
            self.assertIn(text,output)
        self.assertNotIn("BLOCK DECAY",output)
    def test_incomplete_or_corrupt_fails(self):
        slots=slots_from_real_ufo(fake_ufo_parameters())
        row,case=synthetic_case()
        values=values_for_source(row,case)
        del values[("IMYEE2",(2,3))]
        with self.assertRaises(ValueError):check_slots(slots,values)
        values=values_for_source(row,case)
        values[("IMYE",(1,2))] *= -1
        with self.assertRaises(ValueError):lepton_mass_error(row,values)
        pars=fake_ufo_parameters()
        del pars[next(iter(pars))]
        with self.assertRaises(ValueError):slots_from_real_ufo(pars)
    def test_source_CSV_exact_match(self):
        slots=slots_from_real_ufo(fake_ufo_parameters())
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/"external.csv"
            with p.open("w",newline="") as f:
                w=csv.DictWriter(f,["name","nature","type","lhablock","lhacode"])
                w.writeheader()
                for (block,code),name in slots.items():
                    w.writerow(dict(name=name,nature="external",type="real",
                                    lhablock=block,lhacode=json.dumps(list(code))))
            self.assertTrue(verify_csv(p,slots))
            p.write_text(p.read_text().replace("CHARGEMIX","WRONGMIX"))
            with self.assertRaises(ValueError):verify_csv(p,slots)
if __name__=="__main__":unittest.main()
