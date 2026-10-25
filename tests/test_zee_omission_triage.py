"""Standalone dependency-free mathematical tests; independent of Module4 kernels."""
import copy
import hashlib
import json
import math
from pathlib import Path
import sys
import subprocess
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from zee_omission_triage import analyze, sharp_envelope, vector_norm, OPERATOR, BASIS

SCRIPT = Path(__file__).resolve().parents[1]/'scripts'/'zee_omission_triage.py'


def z(x): return {'real':float(complex(x).real),'imag':float(complex(x).imag)}


def record(c1=(2+3j, 4-1j), c2=(-1+2j, 1+1j)):
    summed=(c1[0]+c2[0],c1[1]+c2[1])
    ch={'ledger':{'a':{'C_L':z(c1[0]),'C_R':z(c1[1]),'validation_status':'VALIDATION_PASS'},
                  'b':{'C_L':z(c2[0]),'C_R':z(c2[1]),'validation_status':'VALIDATION_PASS'}},
        'C_L':z(summed[0]),'C_R':z(summed[1]),'partial_BR':1e-11,
        'rate_scope':'INCLUDED_TOPOLOGIES_ONLY','physical_status':'PREDICTION_INCOMPLETE',
        'experimental_comparison':'NOT_EVALUATED',
        'two_loop_candidates':{name:{'coherent_inclusion':False, 'status':'UNKNOWN',
            'validation_status':'GAUGE_MATCHING_UNRESOLVED', 'loop_species':'W+Goldstone+ghost',
            'operator_convention':OPERATOR, 'basis':BASIS}
            for name in ('h_W_gamma','H_W_gamma')},
        'omitted_topologies':{'W_gamma':{'status':'UNKNOWN'}}}
    for row in ch['ledger'].values():
        row.update(operator_convention=OPERATOR,basis=BASIS)
    return {'schema_version':'1.0.0','benchmark_id':'synthetic_not_physical','status':'PARTIAL',
            'COMPLETE_LFV':False,'global_zee_acceptance':None,
            'provenance':{'operator_convention':OPERATOR, 'basis':BASIS,
                          'source':'synthetic mathematical fixture, not physics validation'},
            'channels':{k:copy.deepcopy(ch) for k in ('mu_to_e_gamma','tau_to_mu_gamma','tau_to_e_gamma')}}


class Tests(unittest.TestCase):
    def test_envelope_is_sharp_at_aligned_and_antialigned_boundaries(self):
        c=(2+3j,4-1j); n=math.sqrt(30)
        for fraction in (0,0.01,0.2,0.9,1,2):
            b=n*fraction
            env=sharp_envelope(c,b,3e-12)
            for sign,edge in ((1,'norm_max'),(-1,'norm_min')):
                delta=tuple(-x if sign<0 and b>n else sign*b*x/n for x in c)
                new=vector_norm(tuple(c[i]+delta[i] for i in range(2)))
                self.assertAlmostEqual(new,env[edge],delta=1e-13*max(1,n+b))
            self.assertTrue(math.isclose(env['partial_BR_min'],3e-12*(max(0,n-b)/n)**2,rel_tol=1e-13))
            self.assertTrue(math.isclose(env['partial_BR_max'],3e-12*((n+b)/n)**2,rel_tol=1e-13))

    def test_envelope_bounds_independent_phases_and_chiralities(self):
        c=(2+3j, 4-1j)
        for b in (0.1,2.,10.):
            e=sharp_envelope(c,b,1e-10)
            for k in range(257):
                theta=2*math.pi*k/257
                for w in (0.0,0.25,0.5,0.9,1.0):
                    d=(b*math.sqrt(w)*complex(math.cos(theta),math.sin(theta)),
                       b*math.sqrt(1-w)*complex(math.cos(2*theta),math.sin(2*theta)))
                    n=vector_norm((c[0]+d[0],c[1]+d[1]))
                    self.assertGreaterEqual(n+1e-12,e['norm_min'])
                    self.assertLessEqual(n,e['norm_max']+1e-12)

    def test_cancellation_can_magnify_small_assumed_omission(self):
        r=record(c1=(1+1j, 2+0j),c2=(-1.000001-1j,-2+0j))
        a=analyze(r,(0.01,))
        t=a['channels']['mu_to_e_gamma']
        self.assertGreater(t['cancellation_index_sum_over_result'],1e6)
        self.assertGreater(t['conditional_scenarios'][0]['partial_BR_max']/t['included_partial_BR'],1e6)
        self.assertEqual(t['physical_conclusion'],'UNDETERMINED_MISSING_AMPLITUDES_NOT_BOUNDED')

    def test_common_rephasing_invariant(self):
        r=record(); q=copy.deepcopy(r)
        phase=complex(math.cos(0.7),math.sin(0.7))
        for ch in q['channels'].values():
            for row in list(ch['ledger'].values())+[ch]:
                for key in ('C_L','C_R'):
                    row[key]=z(complex(**row[key])*phase)
        a=analyze(r,(0.1,0.5));b=analyze(q,(0.1,0.5))
        for chan in a['channels']:
            for k in ('included_norm_GeV_minus2','largest_included_component_norm_GeV_minus2','cancellation_index_sum_over_result'):
                self.assertAlmostEqual(a['channels'][chan][k],b['channels'][chan][k],places=9)

    def test_signed_complex_sum_and_independent_cancellation_index(self):
        for ch in analyze(record())['channels'].values():
            self.assertEqual(ch['included_C_L'],z(1+5j))
            self.assertEqual(ch['included_C_R'],z(5))
            self.assertEqual(ch['ledger_sum_C_L'],z(1+5j))
            self.assertEqual(ch['ledger_sum_C_R'],z(5))
            self.assertAlmostEqual(ch['included_norm_GeV_minus2'],math.sqrt(51))
            self.assertAlmostEqual(ch['largest_included_component_norm_GeV_minus2'],math.sqrt(30))
            self.assertAlmostEqual(ch['cancellation_index_sum_over_result'],
                                   (math.sqrt(30)+math.sqrt(7))/math.sqrt(51))

    def test_no_physical_classification_and_w_never_included(self):
        r=record(); a=analyze(r)
        self.assertEqual(a['status'],'DIAGNOSTIC_ONLY_NOT_LFV_CONSTRAINT')
        self.assertNotIn('allowed',str(a).lower())
        bad=copy.deepcopy(r);bad['channels']['mu_to_e_gamma']['two_loop_candidates']['h_W_gamma']['coherent_inclusion']=True
        with self.assertRaises(ValueError):analyze(bad)
        bad=copy.deepcopy(r);bad['channels']['mu_to_e_gamma']['omitted_topologies']['W_gamma']['status']='PASS'
        with self.assertRaises(ValueError):analyze(bad)

    def test_reject_tampering_and_unvalidated_ledger(self):
        r=record()
        for mutation in (
            lambda d: d['channels']['mu_to_e_gamma']['C_L'].__setitem__('real',999),
            lambda d: d['channels']['mu_to_e_gamma']['ledger']['a'].__setitem__('validation_status','UNKNOWN'),
            lambda d: d['channels']['mu_to_e_gamma'].__setitem__('rate_scope','FULL_LFV'),
            lambda d: d.__setitem__('COMPLETE_LFV', True),
            lambda d: d['channels']['tau_to_e_gamma'].__setitem__('partial_BR',float('nan')),
        ):
            bad=copy.deepcopy(r);mutation(bad)
            with self.assertRaises(ValueError):analyze(bad)

    def test_zero_amplitude_no_fake_br_calibration(self):
        env=sharp_envelope((0j,0j),0.1,0.0)
        self.assertIsNone(env['partial_BR_max'])
        self.assertEqual(env['norm_max'],0.1)
        with self.assertRaises(ValueError):sharp_envelope((1+0j,0j),-0.1,1e-9)
        with self.assertRaises(ValueError):sharp_envelope((0j,0j),0.1,1e-9)
        r=record((1+2j,3-4j),(-1-2j,-3+4j))
        for ch in r['channels'].values():ch['partial_BR']=0
        for ch in analyze(r)['channels'].values():
            self.assertIsNone(ch['cancellation_index_sum_over_result'])
            self.assertIsNone(ch['conditional_scenarios'][0]['partial_BR_max'])
            self.assertEqual(ch['conditional_scenarios'][0]['norm_min'],0)

    def test_excluded_w_and_provenance_fail_closed(self):
        mutations=(
            lambda c:c.__setitem__('two_loop_candidates',{}),
            lambda c:c['two_loop_candidates'].pop('H_W_gamma'),
            lambda c:c['two_loop_candidates']['h_W_gamma'].__setitem__('status','PASS'),
            lambda c:c['two_loop_candidates']['h_W_gamma'].__setitem__('validation_status','VALIDATION_PASS'),
            lambda c:c['ledger'].__setitem__('h_W_gamma',copy.deepcopy(c['ledger']['a'])),
            lambda c:c['ledger']['a'].__setitem__('loop_species','W+Goldstone+ghost'),
            lambda c:c['ledger']['a'].__setitem__('coherent_inclusion',0),
            lambda c:c['ledger']['a'].__setitem__('operator_convention','wrong'),
            lambda c:c['ledger']['a'].__setitem__('basis','wrong'),
            lambda c:c['omitted_topologies'].__setitem__('W_gamma',None),
            lambda c:c['omitted_topologies']['W_gamma'].__setitem__('C_L',z(1)),
        )
        for mutation in mutations:
            bad=record();mutation(bad['channels']['mu_to_e_gamma'])
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):analyze(bad)
        for prov in (None,{},dict(operator_convention='wrong',basis=BASIS)):
            bad=record();bad['provenance']=prov
            with self.assertRaises(ValueError):analyze(bad)

    def test_cli_hash_preservation_and_invalid_json(self):
        r=record();original=copy.deepcopy(r)
        result=analyze(r)
        self.assertEqual(r,original)
        result['channels']['mu_to_e_gamma']['excluded_two_loop_candidates']['h_W_gamma']['status']='changed'
        self.assertEqual(r,original)
        with tempfile.TemporaryDirectory() as directory:
            inp=Path(directory)/'input.json';out=Path(directory)/'output.json'
            raw=(json.dumps(r,indent=1)+'\n').encode();inp.write_bytes(raw)
            def run():
                return subprocess.run([sys.executable,str(SCRIPT),'--input',str(inp),'--output',str(out)],
                                      capture_output=True,text=True)
            good=run();self.assertEqual(good.returncode,0,good.stderr)
            result=json.loads(out.read_text())
            self.assertEqual(result['input_sha256'],hashlib.sha256(raw).hexdigest())
            self.assertEqual(result['source_provenance'],r['provenance'])
            for key,ch in r['channels'].items():
                self.assertEqual(result['channels'][key]['excluded_two_loop_candidates'],ch['two_loop_candidates'])
                self.assertEqual(result['channels'][key]['omitted_topologies'],ch['omitted_topologies'])
            sentinel=out.read_bytes()
            for raw in ('{','[]','{"x":1,"x":2}','{"x":NaN}','{"x":Infinity}',
                        json.dumps(r).replace('1e-11','1e999')):
                inp.write_text(raw)
                bad=run();self.assertNotEqual(bad.returncode,0)
                self.assertEqual(out.read_bytes(),sentinel)

    def test_invalid_budget_fractions(self):
        for fractions in ((),(-1,),(0.1,0.1),(float('nan'),),(True,)):
            with self.assertRaises(ValueError):analyze(record(),fractions)


if __name__ == '__main__':unittest.main()
