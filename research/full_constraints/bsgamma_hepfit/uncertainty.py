"""Finite fixed-card propagation. No physical likelihood or total theory sigma."""
import json, os, subprocess
from pathlib import Path
import numpy as np
from execute import ordinary, parse, sha, verify_source, IDS
HERE=Path(__file__).resolve().parent
SRC=Path('/tmp/zee-hepfit/HEPfit-322bd73a2dadd94ce94a6d71cb79d616e569120a')
BIN=Path('/tmp/zee-hepfit/driver')

def main():
    verify_source(SRC)
    prior=json.loads((HERE/'execution/HEPFIT_EXECUTION.json').read_text())
    assert sha(BIN)==prior['binary_sha256']
    out=HERE/'uncertainty_receipts'; out.mkdir(exist_ok=False)
    config=SRC/'Configurations/Temporary/Bsgamma/Bsgamma_input.conf'
    lines=config.read_text().splitlines(); start=next(i for i,l in enumerate(lines) if l.startswith('CorrelatedGaussianParameters'))
    fields=[l.split() for l in lines[start+1:start+8]]
    names=[f[1].removeprefix('Gambino_') for f in fields]
    sig=np.array([float(f[3]) for f in fields])
    corr=np.array([list(map(float,l.split())) for l in lines[start+8:start+15]])
    cov=corr*np.outer(sig,sig); chol=np.linalg.cholesky(cov)
    # Predeclared one-at-a-time published scale endpoints; columns of the
    # Cholesky factor are joint correlated input displacements, not new spectra.
    specs={'central':{}}
    for key,ends in [('mu0',(80.,320.)),('mu_b_bsgamma',(1.25,5.)),('mu_c_bsgamma',(1.25,5.))]:
        for v in ends: specs[f'{key}_{v:g}']={'mut':v,'muw':v} if key=='mu0' else {key:v}
    for j in range(7):
        for sign in (-1,1): specs[f'fit_{j}_{sign:+d}']=dict(zip(names,sign*chol[:,j]))
    for sign in (-1,1): specs[f'BLNP_{sign:+d}']={'BLNPcorr':sign*.05}
    cards=json.loads((HERE.parents[2]/'module1/d10_benchmarks.json').read_text())['records']
    cards={r['input']['benchmark_id']:r['input']['physical'] for r in cards if r['input']['benchmark_id'] in IDS}
    env=dict(os.environ,HEPFITTABS=str(SRC),LD_LIBRARY_PATH='/tmp/zee-hepfit/compat/usr/lib/x86_64-linux-gnu:/home/amine/root/lib')
    runs={}
    def run(label,mode,p):
        inp=out/(label+'.txt'); log=out/(label+'.log')
        inp.write_text(''.join(f'{k} {v:.17g}\n' for k,v in sorted(p.items())))
        cmd=[str(BIN),mode,str(inp)]
        proc=subprocess.run(cmd,env=env,capture_output=True,text=True,timeout=90)
        log.write_text(proc.stdout+proc.stderr)
        assert proc.returncode==0 and 'UNKNOWN_INPUT' not in proc.stdout,label
        val=parse(proc.stdout)
        runs[label]={'input':p,'values':val,'argv':cmd,'returncode':proc.returncode,'input_sha256':sha(inp),'stdout_sha256':sha(log)}
        return val
    responses={}
    for label,change in specs.items():
        p=prior['runs']['SM_reference']['input'].copy()
        if label.startswith('fit_'):
            for k,v in change.items(): p[k]+=v
        else: p.update(change)
        sm=run(label+'_SM','sm',p)
        responses[label]={'SM':sm['BR_NLO']}
        for bid,s in cards.items():
            arr,_=ordinary(s['mH1'],s['mH2'],s['gamma'],np.tan(s['beta']),sm['mt_MSbar_mut'],p['muw'])
            q=prior['runs'][bid+'_central']['input'].copy(); q.update(p)
            for o in range(2):
                for i in range(8): q[f'NP{o}_{i+1}']=arr[o][i]
            v=run(label+'_'+bid,'bridge',q)
            responses[label][bid]=v['BR_NLO']; responses[label][bid+'_delta']=v['BR_NLO']-sm['BR_NLO']
        print(label,flush=True)
    central=responses['central']
    shifts={k:{n:v-central[n] for n,v in r.items()} for k,r in responses.items()}
    # Linearized covariance of (SM, D7, F13, delta_D7, delta_F13) from
    # the documented seven Gaussian inputs ONLY.
    order=list(central)
    jac=np.array([[(responses[f'fit_{j}_+1'][n]-responses[f'fit_{j}_-1'][n])/2 for j in range(7)] for n in order])
    result={'status':'B_FULL_RATE_BLOCKED','physical_bsgamma':'UNKNOWN','theory_sigma':None,'exclusion':None,
        'binary_sha256':sha(BIN),'runner_sha256':sha(Path(__file__)),'config_sha256':sha(config),
        'names':names,'input_sigma':sig.tolist(),'correlation':corr.tolist(),'covariance':cov.tolist(),'cholesky':chol.tolist(),
        'predeclared_variations':specs,'runs':runs,'responses':responses,'signed_shifts':shifts,
        'output_order':order,'fit_direction_sensitivity':jac.tolist(),'partial_fit_output_covariance':(jac@jac.T).tolist(),
        'partial_fit_sigma':dict(zip(order,np.sqrt(np.diag(jac@jac.T)).tolist()))}
    (HERE/'UNCERTAINTY_RUNS.json').write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__': main()
