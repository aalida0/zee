"""Execute only the two original D12 cards and their algebraic controls.

No likelihood, exclusion, parameter generation, or scan interface is provided.
"""
import argparse
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from zee_module5_bmu_nlo import matching
from provenance import verify_source

PIN = '322bd73a2dadd94ce94a6d71cb79d616e569120a'
IDS = ('d7_NO_neutral_near_heavy_07', 'F13_heavy_0001330')
KEYS = ('C7_LO', 'C8_LO', 'C4_NLO_raw', 'C7_NLO_raw', 'C8_NLO_raw')


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def ordinary(m1, m2, gamma, tanb, mt, mu):
    weights = (math.cos(gamma)**2, math.sin(gamma)**2)
    parts = [matching(m, tanb, mt, mu=mu) for m in (m1, m2)]
    c = {k: sum(w * part[k] for w, part in zip(weights, parts)) for k in KEYS}
    arrays = [[0.] * 8 for _ in range(2)]
    arrays[0][6:8] = c['C7_LO'], c['C8_LO']
    arrays[1][3] = c['C4_NLO_raw']
    arrays[1][6:8] = c['C7_NLO_raw'], c['C8_NLO_raw']
    return arrays, c


def parse(text):
    values = {}
    for line in text.splitlines():
        if line.startswith('VALUE '):
            _, k, v = line.split()
            if k in values or not math.isfinite(float(v)):
                raise ValueError('Invalid output ' + k)
            values[k] = float(v)
    if not {'BR_NLO', 'BR_stock_NNLO', 'overall', 'C_sem'} <= values.keys():
        raise ValueError('Missing executed observable')
    return values


def table_reference(path, logtb, logmass):
    """Independent bilinear interpolation of the pinned published NNLO table."""
    rows = [list(map(float, line.split())) for line in path.read_text().splitlines()
            if line.strip() and not line.lstrip().startswith('#')]
    grid = {(x, y): z for x, y, z in rows}
    xs = sorted({x for x, _, _ in rows}); ys = sorted({y for _, y, _ in rows})
    def bounds(a, x):
        if not a[0] <= x <= a[-1]:
            raise ValueError('Outside published table')
        lo = max(v for v in a[:-1] if v <= x)
        return lo, a[a.index(lo)+1]
    x0, x1 = bounds(xs, logtb); y0, y1 = bounds(ys, logmass)
    t=(logtb-x0)/(x1-x0); u=(logmass-y0)/(y1-y0)
    return sum(w * grid[x, y] for x, y, w in
               [(x0,y0,(1-t)*(1-u)), (x1,y0,t*(1-u)), (x0,y1,(1-t)*u), (x1,y1,t*u)])


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source', type=Path, required=True)
    ap.add_argument('--binary', type=Path, required=True)
    ap.add_argument('--superiso', type=Path, required=True)
    ap.add_argument('--superiso-inputs', type=Path, required=True)
    ap.add_argument('--compat-lib-dir', type=Path, required=True)
    ap.add_argument('--root-lib-dir', type=Path, required=True)
    ap.add_argument('--output-dir', type=Path, required=True)
    args = ap.parse_args()
    verify_source(args.source)
    out = args.output_dir.resolve(); out.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((ROOT/'research/full_constraints/SOURCE_MANIFEST.json').read_text())
    for p in ['module1/d10_benchmarks.json', 'validation/module12/d12_benchmarks.json',
              'scripts/zee_module5_bmu_nlo.py', 'module5/patches/d9b_superiso_v5.0.patch']:
        if sha(ROOT/p) != manifest['repository_inputs'][p]:
            raise ValueError('Frozen source mismatch: '+p)
    env = dict(os.environ, HEPFITTABS=str(args.source.resolve()),
               LD_LIBRARY_PATH=f'{args.compat_lib_dir.resolve()}:{args.root_lib_dir.resolve()}')
    raw_si=subprocess.check_output([str(args.superiso_inputs.resolve())],text=True)
    (out/'SuperIso_inputs.log').write_text(raw_si)
    si_input=dict((k,float(v)) for k,v in (line.split() for line in raw_si.splitlines()))
    base = {}
    config = args.source/'Configurations/Temporary/Bsgamma'
    for f in ['StandardModel_THDM_Misiak.conf', 'Flavour_Misiak.conf', 'THDM.conf', 'Bsgamma_input.conf']:
        for line in (config/f).read_text().splitlines():
            t = line.split()
            if t and t[0] == 'ModelParameter':
                base[t[1].removeprefix('Gambino_')] = float(t[2])
    # Current SM mandatory EW remainder parameters, zero as in upstream SM cards.
    for k in ['delSin2th_q','delSin2th_b','delsigma0H','delR0l','delR0c','delGammaWlv','delGammaWqq']:
        base[k] = 0.
    # Drop obsolete, unused kaon/D-mixing parameters from the historical card.
    for k in ['DeltaMK','Dmk','EpsK','KbarEpsK','SM_M12D','phiEpsK']:
        base.pop(k, None)
    base['mut'] = base['muw'] = 160.
    thdm_keys = set('logtb bma mHh2 mA2 mHp2 m12_2 Rpeps NLOuniscale BDtaunu_SM BDtaunu_A BDtaunu_B BDstartaunu_SM BDstartaunu_A BDstartaunu_B bsgamma_theoryerror Q_THDM'.split())
    runs = {}; commands=[]

    def run(label, mode, params, np=None):
        p = dict(params)
        if mode == 'sm': p = {k:v for k,v in p.items() if k not in thdm_keys}
        if np is not None:
            for o in range(2):
                for i in range(8): p[f'NP{o}_{i+1}'] = np[o][i]
        inp=out/(label+'.txt'); log=out/(label+'.log')
        inp.write_text(''.join(f'{k} {v:.17g}\n' for k,v in sorted(p.items())))
        cmd=[str(args.binary.resolve()),mode,str(inp)]
        proc=subprocess.run(cmd,env=env,capture_output=True,text=True,timeout=90)
        log.write_text(proc.stdout+proc.stderr)
        if proc.returncode: raise RuntimeError(f'{label} failed: {log}')
        if 'UNKNOWN_INPUT' in proc.stdout: raise ValueError('Unused input in '+label)
        values=parse(proc.stdout)
        runs[label]={'values':values,'input':p,'mode':mode,'stdout_sha256':sha(log),
                     'input_sha256':sha(inp),'stdout':str(log.relative_to(out))}
        commands.append({'label':label,'argv':cmd,'returncode':proc.returncode})
        print(label,values['BR_NLO'],flush=True)
        return values

    sm=run('SM_reference','sm',base)
    cards = {r['input']['benchmark_id']:r['input'] for r in
             json.loads((ROOT/'module1/d10_benchmarks.json').read_text())['records']
             if r['input']['benchmark_id'] in IDS}
    checks={}; comparisons={}
    for bid in IDS:
        s=cards[bid]['physical']; p=base.copy()
        p.update(mHh2=s['mh2']**2,mA2=s['ma']**2,mHp2=s['mH1']**2,
                 bma=s['beta']-s['alpha'],logtb=math.log10(math.tan(s['beta'])),m12_2=s['m12sq'])
        tb=math.tan(s['beta']); m1=s['mH1']; m2=s['mH2']; g=s['gamma']
        one=run(bid+'_native_m1','thdm',p)
        independent_table=table_reference(args.source/'THDM/tabs/bsgammatable.dat',math.log10(tb),math.log10(m1))
        checks[bid+'_table_interpolation_residual']=one['BR_TypeII_table']-independent_table
        mt=one['mt_MSbar_mut']
        # Only order-separated NP coefficients enter the bridge.
        specs={'central':(m1,m2,g),'gamma_zero':(m1,m2,0.),
               'gamma_half_pi':(m1,m2,math.pi/2),'exchange':(m2,m1,g+math.pi/2),
               'equal':(m1,m1,g)}
        vals={}; arrays={}
        for label,(a,b,c) in specs.items():
            arr,_=ordinary(a,b,c,tb,mt,160.); arrays[label]=arr
            vals[label]=run(bid+'_'+label,'bridge',p,arr)
        p2=p.copy();p2['mHp2']=m2*m2
        two=run(bid+'_native_m2','thdm',p2)
        zero=run(bid+'_zero_NP','bridge',p,[[0.]*8 for _ in range(2)])
        checks[bid+'_zero_SM']=zero['BR_NLO']-sm['BR_NLO']
        checks[bid+'_gamma_zero']=vals['gamma_zero']['BR_NLO']-one['BR_NLO']
        checks[bid+'_gamma_half_pi']=vals['gamma_half_pi']['BR_NLO']-two['BR_NLO']
        checks[bid+'_equal']=vals['equal']['BR_NLO']-one['BR_NLO']
        checks[bid+'_exchange']=vals['exchange']['BR_NLO']-vals['central']['BR_NLO']
        for o in range(2):
            a=one['a_s_muw'] if o else 1.
            c=arrays['gamma_zero'][o].copy()
            c[6]-=4*c[3]/9.; c[7]-=c[3]/6.
            for i in range(8):
                checks[f'{bid}_matching_{o}_{i+1}']=a*c[i]-one[f'high_1_{o}_{i+1}']
        # Fixed-card matching-scale controls, not a theory error envelope.
        for mu in (120.,200.):
            pm=p.copy();pm['muw']=pm['mut']=mu
            ref=run(bid+f'_scale_{mu:g}_SM','sm',pm)
            arr,_=ordinary(m1,m2,g,tb,ref['mt_MSbar_mut'],mu)
            run(bid+f'_scale_{mu:g}','bridge',pm,arr)
        comparisons[bid]={'published_NNLO_table':independent_table,
            'HEPfit_NLO_BR':vals['central']['BR_NLO'],
            'coherent_minus_incoherent':vals['central']['BR_NLO']-(math.cos(g)**2*one['BR_NLO']+math.sin(g)**2*two['BR_NLO'])}
    # Independent signed operator and held-out cross-term probes, on D7 only.
    bid=IDS[0]; p=runs[bid+'_central']['input'].copy()
    p={k:v for k,v in p.items() if not k.startswith('NP')}
    zero=[[0.]*8 for _ in range(2)]
    probe_indices={'C4_NLO':(1,3,.1),'C7_LO':(0,6,.02),'C8_LO':(0,7,.02)}
    for name,(o,i,size) in probe_indices.items():
        for sign in (-1,1):
            c=copy.deepcopy(zero);c[o][i]=sign*size
            run('probe_'+name+('_plus' if sign>0 else '_minus'),'bridge',p,c)
    for name,vector in [('joint',(.02,.02)),('heldout',(-.017,.023))]:
        c=copy.deepcopy(zero);c[0][6:8]=vector
        run('probe_'+name,'bridge',p,c)
    for bid in IDS:
        p=runs[bid+'_central']['input']; s=cards[bid]['physical']
        # Existing D9B client, same saved scalar card; its native input scheme retained.
        base_cmd=[str(args.superiso.resolve()),'160']
        proc=subprocess.run(base_cmd,capture_output=True,text=True,check=True)
        d=dict((k,float(v)) for k,v in (line.split() for line in proc.stdout.splitlines()))
        arr,c=ordinary(s['mH1'],s['mH2'],s['gamma'],math.tan(s['beta']),d['mt_match'],160.)
        cmd=[str(args.superiso.resolve()),str(s['mH1']),str(math.tan(s['beta'])),'0',*[str(c[k]) for k in KEYS],'160']
        proc=subprocess.run(cmd,capture_output=True,text=True,check=True)
        (out/(bid+'_SuperIso.log')).write_text(proc.stdout+proc.stderr)
        data=dict((k,float(v)) for k,v in (line.split() for line in proc.stdout.splitlines()))
        comparisons[bid]['SuperIso']=data
        comparisons[bid]['BR_difference']=runs[bid+'_central']['values']['BR_NLO']-data['injected_BR']
        commands.append({'label':bid+'_SuperIso','argv':cmd,'returncode':proc.returncode})
        # Align public physical inputs, NOT the backend central values. The
        # two semileptonic formulae, QCD running and HQE/EM prescriptions remain.
        shared={k:v for k,v in p.items() if not k.startswith('NP')}
        shared.update(mtop=172.57,AlsMz=.118,Mz=91.188,mbottom=4.183,
            mcharm=1.273,mstrange=.0935,ale=1/137.036,BRsem=10.65,
            Mbkin=si_input['Mbkin'],Mcatmuc=si_input['mc_at_2'],
            mu_b_bsgamma=si_input['mu_b'],mu_c_bsgamma=2.,
            muG2=si_input['muG2'],rhoD3=si_input['rhoD3'],rhoLS3=si_input['rhoLS3'],
            **{'lambda':.22501,'A':.826,'rhob':.1591,'etab':.3523})
        # Identical ordinary NP high-scale C4/C7/C8 to the fresh D9B execution.
        sh=run(bid+'_shared_inputs_shared_NP','bridge',shared,arr)
        shsm=run(bid+'_shared_inputs_SM','sm',shared)
        def decomposition(h, ss, prefix):
            ps=ss[prefix+'_P0']+ss[prefix+'_P1']+ss[prefix+'_P_em']
            ns=ss[prefix+'_N_E0']; nh=h['N']; ph=h['P_NLO']
            return {'normalization':(h['overall']-si_input['overall'])*(ph+nh),
                    'perturbative_including_EM':si_input['overall']*(ph-ps),
                    'power':si_input['overall']*(nh-ns),
                    'direct_difference':h['BR_NLO']-ss[prefix+'_BR']}
        comparisons[bid]['default_decomposition']=decomposition(runs[bid+'_central']['values'],data,'injected')
        comparisons[bid]['shared_decomposition']=decomposition(sh,data,'injected')
        comparisons[bid]['shared_SM_decomposition']=decomposition(shsm,data,'SM')
    result={'HEPfit_commit':PIN,'runtime_status':'HEPFIT_RUNTIME_PASS',
       'executable_status':'INDEPENDENT_RATE_EXECUTABLE',
       'accuracy':'Real top-only NP matching through NLO QCD, NLO evolution and P numerator; native HEPfit partial EW and HQE normalization retained. Not uniformly truncated full Zee.',
       'cut_GeV':1.6,'Top_input_scheme':'POLE via explicit FlagMtPole=true; running top printed per run',
       'primed_prescription':'Native Bsgamma C7p = evolved primed + (ms/mb)*C7; general primed matching NOT validated',
       'stock_NNLO_warning':'BR_stock_NNLO on bridge runs omits NNLO NP matching and is diagnostic only; not an accepted NNLO prediction.',
       'independent_rate_status':('INDEPENDENT_RATE_MATCHED' if all(abs(v['BR_difference'])<2e-13 for v in comparisons.values()) else 'INDEPENDENT_RATE_MISMATCH'),
       'published_table_status':'INTERPOLATION_REPRODUCED; INDEPENDENT_RATE_MATCHING_NOT_ESTABLISHED',
       'full_rate_status':'B_FULL_RATE_BLOCKED','uncertainty_status':'UNCERTAINTY_CALIBRATION_BLOCKED',
       'physical_bsgamma':'UNKNOWN','theory_sigma':None,'exclusion':None,
       'runs':runs,'implementation_residuals':checks,'comparisons':comparisons,
       'commands':commands,'binary_sha256':sha(args.binary),'superiso_binary_sha256':sha(args.superiso),
       'SuperIso_inputs':si_input,
       'driver_sha256':sha(HERE/'driver.cpp'),'runner_sha256':sha(Path(__file__))}
    (out/'HEPFIT_EXECUTION.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')


if __name__=='__main__': main()
