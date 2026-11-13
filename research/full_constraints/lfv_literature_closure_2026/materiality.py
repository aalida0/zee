"""Source-locked two-loop 2HDM proxy and original 64 Zee one-loop safety margins.

Uses the *already executed* pinned corrected upstream general-2HDM 2025/26
complex cL/cR groups. It DOES NOT map the one-state charged bosonic loop to
the physical two-mixed-charged-state Zee model; its pure-2HDM 2-loop ratios
are not full Zee amplitudes. 64 summary extrema are from the existing
12-Nov source-derived scan, not per-card data and not a new calculation.
All unresolved physical LFV statuses are kept null.
"""
import argparse
import json
import math
from pathlib import Path

PAPER_SOURCE_SHA256 = '9b4af7aa4bf7bf533a7b82c8c2603d118346424e3b7b5f9f06ab8cb41bc4e193'
RADIATIVE_BOUND = 1.5e-13
ONE_LOOP_64_MAXIMA = {
    'mu_to_e_gamma': {'rate':1.6273e-15, 'observed_bound':1.5e-13,
                      'source':'ACTUAL_64_SOURCE_ONE_LOOP_MU3E_CONVERSION_2026-11-12.md'},
    'mu_to_3e': {'rate':1.0729e-17, 'observed_bound':1.e-12,
                'source':'ACTUAL_64_SOURCE_ONE_LOOP_MU3E_CONVERSION_2026-11-12.md'},
    'mu_Au_to_e_Au': {'rate':2.7637e-17, 'observed_bound':7.e-13,
                     'source':'ACTUAL_64_SOURCE_ONE_LOOP_MU3E_CONVERSION_2026-11-12.md'},
}
GROUPS = ('neutral_fermion','neutral_bosonic','charged_fermion','charged_bosonic')


def pair(z):
    if not isinstance(z,(tuple,list)) or len(z)!=2:
        raise ValueError('Complex coefficient requires real,imag tuple')
    v=complex(float(z[0]),float(z[1]))
    if not (math.isfinite(v.real) and math.isfinite(v.imag)):
        raise ValueError('Nonfinite complex Wilson')
    return v


def _norm(cL,cR):
    return math.hypot(abs(cL),abs(cR))


def screen_64():
    out = {}
    for key, record in ONE_LOOP_64_MAXIMA.items():
        rate=record['rate']
        bound=record['observed_bound']
        if not (0<rate<bound):
            raise ValueError('Recorded 64-point bound or rate invalid')
        margin=bound/rate
        # For a bound on the omitted FULL process-amplitude norm, the
        # triangle inequality guarantees no exclusion if kappa < this.
        # No calculation actually establishes any kappa here.
        max_kappa=math.sqrt(margin)-1
        out[key] = dict(record,
            observed_rate_safety_ratio=margin,
            sufficient_uniform_omitted_amplitude_bound_over_1loop=max_kappa,
            bound_is_proven=False,
            full_physical_comparison=None)
    return out


def analyze_official_proxy(path):
    p=Path(path)
    report=json.loads(p.read_text())
    source=report['source']
    if source['gitlab_thdm_py_sha256']!=PAPER_SOURCE_SHA256:
        raise ValueError('Unrecognized corrected two-loop source')
    if report['comparison_scope'].find('pure 2HDM')<0:
        raise ValueError('Wrong source/physical-model declaration')
    if len(report['data'])!=4:
        raise ValueError('Expected exactly four old D7/F13 source cards')
    checked=[]
    for row in report['data']:
        groups=row['official_Wilson_source_groups']
        if set(groups)!=set(GROUPS)|{'one_loop'}:
            raise ValueError('Source decomposition incomplete')
        vals={name:(pair(x['cL']),pair(x['cR'])) for name,x in groups.items()}
        for name,x in groups.items():
            n=_norm(*vals[name])
            if not math.isclose(n,x['c_norm'],rel_tol=1e-10,abs_tol=1e-40):
                raise ValueError('Source component norm mismatch: '+name)
        one=vals['one_loop']
        loop=(sum(vals[name][0] for name in GROUPS),
              sum(vals[name][1] for name in GROUPS))
        combined=(one[0]+loop[0],one[1]+loop[1])
        observed=(pair(row['official_coherent_Wilson']['cL']),
                  pair(row['official_coherent_Wilson']['cR']))
        if _norm(combined[0]-observed[0],combined[1]-observed[1])>1e-12*_norm(*one):
            raise ValueError('Corrected original source coherent sum disagrees')
        ratio=_norm(*loop)/_norm(*one)
        if not math.isclose(ratio,row['official_two_loop_to_one_loop_norm_ratio'],rel_tol=1e-9):
            raise ValueError('Corrected two-loop ratio mismatch')
        triangle=sum(_norm(*vals[name]) for name in GROUPS)/_norm(*one)
        checked.append({'witness_id':row['benchmark_id'],
            'pure_2HDM_single_mass_proxy_GeV':row['m_doublet_bare'],
            'relative_norm_2loop_over_1loop':ratio,
            'triangle_bound_sum_individual_2loop_norms_over_1loop':triangle,
            'individual_group_norms':{name:_norm(*vals[name]) for name in GROUPS},
            'zero_direct_em_is_exact_source_selection_rule':True,
            'Zee_two_loop_Wilson':None,'Zee_physical_LFV_pass':None})
    zeros=report['exact_direct_em_zero_test']
    if len(zeros)!=4 or any(x['norm']!=0 for x in zeros) or {x['id'] for x in zeros}!={x['witness_id'] for x in checked}:
        raise ValueError('Lost direct-em exact zero source test')
    return {'status':'VALIDATED_PURE_2HDM_PROXY_MATERIALITY_ONLY',
        'source':source,'comparison_scope':report['comparison_scope'],
        'four_card_corrected_2HDM_source':checked,
        'new_64_Zee_one_loop_maxima':screen_64(),
        'uncomputed_Zee_mixed_F_W_Goldstone_2loop':None,
        'physical_LFV':None,'global_zee_acceptance':None,
        'unqualified_transfer_forbidden':'Do not apply 2HDM proxy correction to Zee two-state masses as if it were full Zee.'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--official-proxy-json',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    out=analyze_official_proxy(a.official_proxy_json)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    if a.output.exists():
        raise FileExistsError('Never overwrite prior source receipts')
    a.output.write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
    print('PASS',out['status'],'FOUR OLD SOURCE CARDS',len(out['four_card_corrected_2HDM_source']))
    print('FULL ZEE LFV UNKNOWN')

if __name__=='__main__':main()
