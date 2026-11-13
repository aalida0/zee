import json
import math
import tempfile
from pathlib import Path
import unittest
from .materiality import *

class TestMateriality(unittest.TestCase):
    def test_64_safe_headroom_but_no_proven_bound(self):
        r=screen_64()
        self.assertEqual(len(r),3)
        self.assertAlmostEqual(r['mu_to_e_gamma']['observed_rate_safety_ratio'],1.5e-13/1.6273e-15)
        self.assertAlmostEqual(r['mu_to_e_gamma']['sufficient_uniform_omitted_amplitude_bound_over_1loop'],
                               math.sqrt(1.5e-13/1.6273e-15)-1)
        self.assertLess(r['mu_to_e_gamma']['sufficient_uniform_omitted_amplitude_bound_over_1loop'],9)
        self.assertFalse(r['mu_to_e_gamma']['bound_is_proven'])
        self.assertIsNone(r['mu_to_e_gamma']['full_physical_comparison'])

    def test_source_coherence_and_untrusted_source_rejection(self):
        r={'source':{'gitlab_thdm_py_sha256':PAPER_SOURCE_SHA256},
           'comparison_scope':'four pure 2HDM points','data':[],
           'exact_direct_em_zero_test':[]}
        def grp(cL,cR):
            return {'cL':list(cL),'cR':list(cR),
                    'c_norm':math.hypot(abs(complex(*cL)),abs(complex(*cR)))}
        for i in range(4):
            groups={name:grp((1e-18,2e-18),(3e-18,4e-18)) for name in GROUPS}
            groups['one_loop']=grp((1e-8,0),(2e-8,0))
            total=complex(1e-8,0)+4*complex(1e-18,2e-18)
            totalR=complex(2e-8,0)+4*complex(3e-18,4e-18)
            ratio=math.hypot(abs(4*complex(1e-18,2e-18)),abs(4*complex(3e-18,4e-18)))/math.sqrt(5e-16)
            row={'benchmark_id':f'card_{i}', 'm_doublet_bare':500.,
                'official_Wilson_source_groups':groups,
                'official_coherent_Wilson':{'cL':[total.real,total.imag],
                                            'cR':[totalR.real,totalR.imag]},
                'official_two_loop_to_one_loop_norm_ratio':ratio}
            r['data'].append(row)
            r['exact_direct_em_zero_test'].append({'id':f'card_{i}','norm':0})
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'verified.json'
            p.write_text(json.dumps(r))
            out=analyze_official_proxy(p)
            self.assertEqual(len(out['four_card_corrected_2HDM_source']),4)
            self.assertIsNone(out['physical_LFV'])
            r['source']['gitlab_thdm_py_sha256']='unknown'
            p.write_text(json.dumps(r))
            with self.assertRaisesRegex(ValueError,'Unrecognized'):
                analyze_official_proxy(p)

if __name__=='__main__':unittest.main()
