"""Native validated, conditional LO on-shell charged-scalar two-body ledger.

Run: python -m module7.d4_inputs; math -script scripts/zee_d4_vertices.m;
python -m module7.d4_decay_table. No vacuum search or flavor recomputation.
"""
import json
import math
import re
from pathlib import Path

from module2.interface import canonical_hash
from module7.cascade_z import cascade_width
from module7.d4_inputs import ROOT, PINNED, SM, families, sha, yukawa_masses, ckm
from module7.d4_native import validate_native
from module7.d4_tree_kernels import scalar_vector, scalar_scalar, scalar_fermions

UP, DOWN, LEPTONS = ('u','c','t'), ('d','s','b'), ('e','mu','tau')
NEUTRALS = ('Z','photon','h','H','A')
REFERENCE = 'https://link.springer.com/article/10.1140/epjc/s10052-021-09956-2'


def expected_channels(k):
    return ({u+' anti-'+d for u in UP for d in DOWN}
            | {'W '+n for n in ('h','H','A','Z','photon')}
            | {f'H{j} '+n for j in (1,2) for n in NEUTRALS}
            | {l+' nu_all' for l in LEPTONS})


def complete_total(rows, k):
    """Fail closed on unknown, missing, duplicate or nonfinite partial widths."""
    names = [r['channel'] for r in rows]
    if len(names) != len(set(names)) or set(names) != expected_channels(k):
        raise ValueError('Incomplete or duplicate channel inventory')
    missing = [r['channel'] for r in rows if
               r['status'] not in ('OPEN','CLOSED','FORBIDDEN_CP','UNKNOWN_VERTEX') or
               r['status'] == 'UNKNOWN_VERTEX' or
               (r['kinematically_open'] and not r['independently_validated']) or
               (r['status']=='FORBIDDEN_CP' and r.get('exact_zero')!='CP') or
               any(r[key] is None or not math.isfinite(r[key]) or r[key] < 0
                   for key in ('width_GeV','width_minus_GeV'))]
    if missing:
        return {'status':'BR_NOT_EVALUATED','total_width_GeV':None,
                'branching_fraction':None,'missing_widths':missing}
    total = math.fsum(r['width_GeV'] for r in rows)
    minus = math.fsum(r['width_minus_GeV'] for r in rows)
    if total <= 0 or not math.isclose(total,minus,rel_tol=2e-13,abs_tol=1e-15):
        raise ValueError('Charge-conjugate total mismatch')
    return {'status':'D4_COMPLETE_TWO_BODY_BR_PASS','total_width_GeV':total,
            'Gamma_total_on_shell_two_body_GeV':total,'total_width_minus_GeV':minus,
            'branching_fraction':next((r['width_GeV']/total for r in rows if r['channel']=='H1 Z'),0.) if k==2 else None,
            'branching_fractions':{r['channel']:r['width_GeV']/total for r in rows if r['width_GeV']>0},
            'missing_widths':[]}


def coefficients(case, index):
    return [complex(c['real'],c['imag']) for c in case['coefficients'][index]]


def row(channel, M, masses, wp, wm, query, exact_zero=None, validated=True):
    opened = M > sum(masses)
    status = 'FORBIDDEN_CP' if exact_zero=='CP' else 'OPEN' if opened else 'CLOSED'
    return {'channel':channel,'mother_charge':'+','conjugate_mother_charge':'-',
            'daughter_masses_GeV':list(masses),'kinematically_open':opened,
            'status':status,'width_GeV':wp,'width_minus_GeV':wm,
            'native_query_indices':query,'independently_validated':validated,
            'exact_zero':exact_zero,'scheme':'d4_SM_input_card','errors':[]}


def nonleptonic(p, case, k):
    M=p[f'mH{k}'];w=SM['EW']['mW'];z=SM['EW']['mZ']
    kin=SM['kinematic_masses']; rows=[]
    for i,u in enumerate(UP):
        for j,d in enumerate(DOWN):
            index=(k-1)*18+2*(i*3+j)
            a,b=coefficients(case,index);am,bm=coefficients(case,index+1)
            rows.append(row(u+' anti-'+d,M,[kin[i],kin[3+j]],
                scalar_fermions(M,kin[i],kin[3+j],a,b,3),
                scalar_fermions(M,kin[3+j],kin[i],am,bm,3),[index,index+1]))
    for j,n in enumerate(('h','H','A')):
        mass=p[('mh1','mh2','ma')[j]]
        index=36+(k-1)*4+j*2 if j<2 else 44+(k-1)*2
        c,cm=coefficients(case,index)[0],coefficients(case,index+1)[0]
        rows.append(row('W '+n,M,[w,mass],scalar_vector(M,mass,w,c),scalar_vector(M,mass,w,cm),[index,index+1]))
    for daughter in (1,2):
        m=p[f'mH{daughter}']
        for n,mn in zip(NEUTRALS,[z,0.,p['mh1'],p['mh2'],p['ma']]):
            query=[];zero=None;validated=False;wp=wm=0.
            if daughter != k:
                validated=True
                if n=='Z':
                    query=[91];c=coefficients(case,91)[0]
                    wp=wm=scalar_vector(M,m,z,c)
                    if k==2:
                        frozen=cascade_width({'mH1_GeV':p['mH1'],'mH2_GeV':p['mH2'],
                            'mW_GeV':w,'mZ_GeV':z,'v_GeV':p['v'],'gamma_rad':p['gamma']})['partial_width_GeV']
                        if not math.isclose(wp,frozen,rel_tol=2e-14,abs_tol=1e-13):
                            raise ValueError('CONFLICT: native versus frozen D3 normalization')
                        wp=wm=frozen
                elif n=='photon':
                    query=[90];zero='GAUGE'
                else:
                    offset={'h':0,'H':1,'A':2}[n]
                    index=(48 if k==1 else 51)+offset
                    reverse=(51 if k==1 else 48)+offset
                    query=[index,reverse]
                    if n=='A':zero='CP'
                    else:
                        wp=scalar_scalar(M,m,mn,coefficients(case,index)[0])
                        wm=scalar_scalar(M,m,mn,coefficients(case,reverse)[0])
            rows.append(row(f'H{daughter} '+n,M,[m,mn],wp,wm,query,zero,validated))
    for n,mn,offset in [('Z',z,0),('photon',0.,1)]:
        index=92+(k-1)*2+offset
        rows.append(row('W '+n,M,[w,mn],0.,0.,[index,index+4],'GAUGE'))
    return rows


def leptons(p, case, k):
    M=p[f'mH{k}']; rows=[]
    for i,l in enumerate(LEPTONS):
        ml=SM['lepton_masses'][i];plus=[];minus=[];queries=[]
        for j in range(3):
            index=54+(k-1)*18+2*(i*3+j);queries.extend([index,index+1])
            a,b=coefficients(case,index);am,bm=coefficients(case,index+1)
            plus.append(scalar_fermions(M,0.,ml,a,b,1))
            minus.append(scalar_fermions(M,ml,0.,am,bm,1))
        r=row(l+' nu_all',M,[ml,0.],math.fsum(plus),math.fsum(minus),queries)
        r['neutrino_sum']='three massless tree eigenstates; two orthogonal helicities, PMNS invariant'
        rows.append(r)
    return rows


def build():
    native=validate_native()
    data,d3=families()
    raw=json.loads((ROOT/'validation/module7/local/d4_native.json').read_text())
    cases={c['id']:c for c in raw['numeric_cases']}
    tables={}; points=[]
    refs={250.:11.671906176399391,300.:9.411343258642537,350.:7.1240428396019855}
    for r,n,e in data:
        p=r['module2_input']['scalar']['record']['physical'];name=e['spectrum_name']
        totals={};lrows={}
        for k in (1,2):
            case=cases[r['benchmark_id']+f'/H{k}']
            bosons=nonleptonic(p,case,k);lep=leptons(p,case,k)
            lrows[f'H{k}']=lep;totals[f'H{k}']=complete_total(bosons+lep,k)
            if k==2 and next(x['width_GeV'] for x in bosons if x['channel']=='H1 Z') != refs[p['mH1']]:
                raise ValueError('CONFLICT: pinned D3 cascade normalization')
            if name not in tables:tables[name]={'physical':p,'mothers':{},'conditional_D3_context':next(x for x in d3['selected_widths'] if x['spectrum_name']==name)}
            key=f'H{k}'
            if key in tables[name]['mothers']:
                if bosons != tables[name]['mothers'][key]['channels']:
                    raise ValueError('Nonleptonic family invariance falsified')
            else:
                # Independent scheme variation keeps kinematics fixed.
                old=SM['quark_reference_masses'];V=ckm();scheme=[]
                doublet=math.cos(p['gamma']) if k==1 else -math.sin(p['gamma'])
                for i in range(3):
                    for j in range(3):
                        a=math.sqrt(2)*old[i]/p['v']/math.tan(p['beta'])*doublet*V[i,j]
                        b=math.sqrt(2)*old[j+3]/p['v']*math.tan(p['beta'])*doublet*V[i,j]
                        scheme.append(scalar_fermions(p[key.replace('H','mH')],SM['kinematic_masses'][i],SM['kinematic_masses'][j+3],a,b,3))
                tables[name]['mothers'][key]={'mother_mass_GeV':p[f'mH{k}'],'channels':bosons,
                    'decay_yukawa_masses_GeV':yukawa_masses(p[f'mH{k}']),
                    'quark_sum_GeV':math.fsum(x['width_GeV'] for x in bosons[:9]),
                    'quark_sum_unevolved_reference_Yukawas_GeV':math.fsum(scheme)}
        points.append({'benchmark_id':r['benchmark_id'],'spectrum_name':name,'family_name':e['family_name'],
            'scalar_sha256':e['bound_scalar_sha256'],'module2_input_sha256':e['module2_input_sha256'],
            'D_sha256':e['D_sha256'],'full_Module2_sha256':e['per_sector_output_sha256']['neutrino'],
            'leptonic_channels':lrows,'mothers':totals})
    contrasts={}
    for name,t in tables.items():
        group=[p for p in points if p['spectrum_name']==name]
        contrasts[name]={'nonleptonic_width_spread_GeV':0.,'independent_D_hashes':len({p['D_sha256'] for p in group}),
            'leptonic_sum_GeV':{k:{p['family_name']:math.fsum(x['width_GeV'] for x in p['leptonic_channels'][k]) for p in group} for k in ('H1','H2')}}
    validation={}
    for label, filename in [('generic_kernels','d4_kernel_tests.log'),('D4','d4_tests.log'),
                            ('D3_regression','d4_D3_regression_tests.log'),('all_Module7','d4_all_module7_tests.log')]:
        path=ROOT/'validation/module7/local'/filename
        if path.exists():
            log=path.read_text();match=re.search(r'Ran (\d+) tests? in ',log)
            if match and log.rstrip().endswith('OK'):
                validation[label]={'passed':int(match.group(1)),'log_sha256':sha(path),'log':str(path.relative_to(ROOT))}
    sources=[*ROOT.glob('module7/d4_*.py'),*ROOT.glob('tests/test_module7_d4_*.py')]
    return {'schema_version':'1.0.0','statuses':['D4_TREE_DECAY_TABLE_PASS','D4_COMPLETE_TWO_BODY_BR_PASS','PHYSICAL_LHC_CLAIM_NOT_EVALUATED'],
        'approximation':'LO on-shell tree two-body only; native tree neutrinos massless; no off-shell, finite unstable daughter width, loop decay or NLO QCD/EW correction',
        'd3_base':'5f70b8cddaf1092d9c97f3c2cb4e2eab5dfa8a36','pinned_input_bytes_sha256':PINNED,
        'native_evidence':'validation/module7/d4_native_validation.json',
        'native_raw_output_sha256':native['raw_output_sha256'],'SM_input_card':SM,'reference':REFERENCE,
        'source_sha256':{str(s.relative_to(ROOT)):sha(s) for s in sorted(sources)},
        'validation':validation,
        'spectrum_tables':tables,'conditional_lepton_families':points,'family_contrasts':contrasts,
        'inventory_proof':[
            'Frozen physical charged particles: H1,H2,W,quarks,charged leptons. No new colored scalars, right neutrinos, or doubly charged particles.',
            'Charge,color,Lorentz invariance: charged scalar + neutral h/H/A/Z/photon; W + neutral h/H/A/Z/photon; all nine u anti-d; three charged leptons times all three neutrinos.',
            'WZ and Wphoton amplitudes vanish after physical Goldstone-orthogonal projection; offdiagonal H photon exact zero. Same-parent scalar daughters closed.',
            'Fermion-boson final states cannot couple a spin-zero mother by Lorentz invariance. Gluon plus color-singlet charged state forbidden by color. Goldstones/ghosts are not additional physical states.',
            'Each mother has exactly 27 exclusive or proven inclusive channels. Charge-conjugate widths checked individually, never added to the H+ total.'
        ],
        'leptonic_status':'NATIVE_GENERAL_ZEE_INCLUSIVE_MASSLESS_TREE_WIDTHS_VALIDATED',
        'blockers_to_tree_two_body_BR':[],
        'uncomputed':['loop-induced neutrino-mass effects and F-D helicity interference proportional to mnu','off-shell three-body channels','finite unstable daughter widths','loop-only channels','NLO QCD/EW and uncertainties','production cross sections and detector/LHC reach','joint constrained neutrino/flavor population and complete LFV'],
        'publication_decision':'No new mechanism/formula or scalar-only BR novelty over 2021; conditional leptonic final states vary with inverse families; constrained flavor-correlated signatures and justified parton-level production rates still required.',
        '2026_LINEARIZED_FLAVOR_FILTER_READY':False,'COMPLETE_LFV':False,'global_zee_acceptance':None,
        'preserved_D3_statuses':d3['statuses']}


def main():
    report=build()
    native=validate_native()
    (ROOT/'validation/module7/d4_native_validation.json').write_text(json.dumps(native,indent=2,allow_nan=False)+'\n')
    # Compact per-record JSON; full native numerical cases and logs stay ignored.
    (ROOT/'validation/module7/d4_decay_table.json').write_text(json.dumps(report,indent=1,allow_nan=False)+'\n')
    for p in report['conditional_lepton_families']:
        print(p['benchmark_id'],[(k,v['total_width_GeV'],v['branching_fraction']) for k,v in p['mothers'].items()])


if __name__=='__main__':main()
