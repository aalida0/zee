"""One source-backed E4A 216-evaluation integrated regression."""
import math
import unittest
from pathlib import Path
from unittest.mock import patch
from gateA1s_run_modern_2026_screen import linearized_2026
from zee_gateE4a_integrated_precision_matching_calibration import (
    run_cohort,typeII_controls,OBSERVABLE_STATUS,
    eq4_closure,gamma_trajectory_checks
)

def synthetic(m1,m2,t,g):
    a=math.cos(g)**2
    b=math.sin(g)**2
    rows={}
    for order in range(3):
        for op in range(1,9):
            sm=-.21 if op==7 else -.11
            d1=(-.06 if op in (7,8) else .002)/(1+m1/600)/(order+1)
            d2=(-.06 if op in (7,8) else .002)/(1+m2/600)/(order+1)
            rows[order,op]=[sm,d1,d2,sm+a*d1+b*d2]
    return {'input':{'mH1':m1,'mH2':m2,'tanbeta':t,'gamma':g,
                     'mu0':160.,'w1':a,'w2':b},
            'coefficient_rows':rows,'max_coherent_Wilson_residual':0.}

class TestE4A(unittest.TestCase):
    def test_integrated_27_zee_18_typeII_216_sources(self):
        e1={}; e3={}; calls=[]
        for i in range(27):
            key=f'B4_{i:07d}'
            m1,m2,t,g=250.+i*8,685.+i*12,5.6+i*.01,1.05+i*.005
            z=synthetic(m1,m2,t,g)['coefficient_rows']
            a=math.cos(g)**2;b=1-a
            d7=a*z[0,7][1]+b*z[0,7][2]
            d8=a*z[0,8][1]+b*z[0,8][2]
            e1[key]={'candidate_id':key,'mH1':m1,'mH2':m2,
                     'tanbeta':t,'gamma':g}
            e3[key]={'LO_delta_C7_Zee_mu0_160':d7,
                     'LO_delta_C8_Zee_mu0_160':d8,
                     '2026_Eq4_original_LO_linearized_BR_times_1e4':
                         linearized_2026(d7,d8)['linearized_predicted_central_times_1e4']}
        def evaluate(binary,m1,m2,t,g):
            calls.append((m1,m2,t,g))
            return synthetic(m1,m2,t,g)
        with patch('zee_gateE4a_integrated_precision_matching_calibration.run_matching',
                   side_effect=evaluate):
            models,coeff=run_cohort(Path('/not_executed'),e1,e3)
            pure=typeII_controls(Path('/not_executed'))
        self.assertEqual((len(models),len(coeff),len(pure),len(calls)),
                         (27,648,18,216))
        self.assertEqual(len(calls)*24,5184)
        self.assertEqual(sum(x['mH_GeV']==670 for x in pure),2)
        self.assertTrue(all(x['max_degenerate_residual']<1e-12 for x in pure))
        self.assertTrue(all(x['modern_2026_95CL_exclusion']=='NOT_IMPLEMENTED'
                            for x in models))
        self.assertIn('BLOCKED',OBSERVABLE_STATUS)
