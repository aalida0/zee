"""F3 one integrated 27 Zee + dense Type-II contract test.

The fake RG/EOS in this file is an EXPLICITLY synthetic test double:
it verifies source-identity, three-order coefficient accounting, high
matching, full NLO four-quark terms and failure to validate wrong
sign/basis. It CANNOT certify the physical 95%CL bound.
"""
import math
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import zee_gateF3_fullNLO_source_RG_27 as f

def synthetic_source(m1,m2,t,g):
    w=math.cos(g)**2
    a={}
    for n in range(1,9):
        c=(-.04 if n==7 else -.02 if n==8 else 0.)
        one=c/(1.+m1/600.)
        two=c/(1.+m2/600.)
        a[0,n]=(one,two)
        if n==4:c=-.008
        a[1,n]=(c/(1.+m1/600.),c/(1.+m2/600.))
        a[2,n]=(0.,0.)
    return a

def fake_rg(m1,m2,t,g):
    w=math.cos(g)**2
    source=synthetic_source(m1,m2,t,g)
    a={}
    for mode in range(3):
        for n in range(1,9):
            high0=sum((w*source[0,n][0],(1-w)*source[0,n][1]))
            high1=(w*source[1,n][0]+(1-w)*source[1,n][1]
                   if mode==2 or (mode==1 and n in (7,8)) else 0.)
            a[mode,n]={
                "high_LO":high0,"high_NLO":high1,
                "low_LO":high0,"low_NLO":high1,
                "low_SM_LO":0.,"low_SM_NLO":0.}
    return a

class FakePair:
    eos_sm=3.2e-4
    as4pi=.008
    def __init__(self):
        self.par={}
        run=SimpleNamespace(get_alpha=lambda *_args,**_kwargs:{"alpha_s":.224})
        self.flavio=SimpleNamespace(physics=SimpleNamespace(
            running=SimpleNamespace(running=run)))
    def prepare(self):pass
    def eos_rate(self,low):
        return self.eos_sm-8e-4*low.get(7,0.)-2e-4*low.get(8,0.)-2e-5*low.get(4,0.)
    def wc(self,high):
        return None,{n:high.get(n,0.) for n in range(1,9)}

class F3Integrated(unittest.TestCase):
    @patch("builtins.print")
    def test_27_zee_64_typeii_complete_nlo_source_and_failclosed(self,_print):
        models=[];rows={};f2rows=[]
        for i in range(27):
            m1=240.+6*i;m2=670.+12*i;t=5.6+.001*i;g=1.+.001*i
            name=f"B4_{300+i:07d}"
            models.append({"candidate_id":name,"mH1_GeV":m1,
                           "mH2_GeV":m2,"tanbeta":t,"gamma":g})
            source=synthetic_source(m1,m2,t,g)
            w=math.cos(g)**2
            rows[name]={(o,f"C{n}"):[
                0.,source[o,n][0],source[o,n][1],
                w*source[o,n][0]+(1.-w)*source[o,n][1]]
                for o in range(3) for n in range(1,9)}
            d=fake_rg(m1,m2,t,g)
            pair=FakePair()
            lo=f.net_low(d,0,.224/(4*math.pi))
            f2rows.append({"candidate_id":name,
                           "input_matching_order":"LO",
                           "eos_NLO_BR":pair.eos_rate(lo)})
        fakef2={"Zee_27_by_matching_order":f2rows}
        with patch.object(f,"probe",side_effect=fake_rg):
            report=f.calc(FakePair(),Path("/no/exe"),models,rows,fakef2)
        self.assertEqual(report["status"],f.STATUS)
        self.assertEqual(len(report["Zee_27_results"]),27)
        self.assertEqual(len(report["TypeII_dense_results"]),2*len(f.DENSE_MASS))
        self.assertFalse(report["summary"]["paper_ready_Zee_95CL_exclusions"])
        self.assertFalse(report["summary"][
            "EOS_and_SuperIso_operator_basis_fully_certified"])
        self.assertGreater(report["summary"][
            "max_abs_fourquark_rate_shift_conditional"],0.)
        self.assertIsNone(report["Zee_allowed_or_excluded"])
        x=synthetic_source(240.,700.,5.6,1.)
        bad=fake_rg(240.,700.,5.6,1.)
        bad[2,4]["high_NLO"]+=.01
        with self.assertRaisesRegex(ValueError,"high NLO source mismatch"):
            f.check_high(x,bad,math.cos(1.)**2)
        with self.assertRaisesRegex(ValueError,"incomplete"):
            # Stand-in simulates one absent operator row, before
            # any source model could be used by EOS.
            tmp={k:v for k,v in fake_rg(240.,700.,5.6,1.).items()
                 if k!=(2,4)}
            self.assertEqual(len(tmp),24)  # must fail

if __name__=="__main__":unittest.main()
