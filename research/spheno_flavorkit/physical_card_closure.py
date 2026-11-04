"""Two new full Zee spectrum cards and controlled pole-input replacements.

No new neutrino fit or vacuum certificate is asserted. Uses frozen scalar
reconstruction and the unchanged generated Lagrangian/executable.
"""
from pathlib import Path
import copy
import json
import math
import sys
import subprocess
import hashlib
import numpy as np
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parents[1]))
from module1.scalar_constraints import reconstruct,unitarity,ewpo
from module1.bfb import check_bfb
from module3.core import dipole_ledger
OUT=ROOT/'local/crossing_physical_cards'


def matrix(x):return np.array(x['real'])+1j*np.array(x['imag'])
def encoded(x):return {'real':np.real(x).tolist(),'imag':np.imag(x).tolist()}
def packed(x):return {'real':float(x.real),'imag':float(x.imag)}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    OUT.mkdir(exist_ok=True)
    original=json.loads((ROOT.parents[1]/'validation/module12/d12_benchmarks.json').read_text())
    dataset={'SM_decay_card':original['SM_decay_card'],'groups':[]}
    gate_evidence=[]
    for n in range(2):
        base=original['groups'][2*n]['witnesses']['central']
        record=copy.deepcopy(base['module2_input']['scalar']['record']);p=record['physical']
        record['benchmark_id']=f'D15_new_physical_card_{n}'
        for name,factor in [('mH1',1.013),('mH2',1.009),('mh2',1.006),('ma',1.006)]:p[name]*=factor
        p['gamma']+=.014 if n==0 else -.017;p['alpha']+=.003
        params,inherit,reconstruction=reconstruct(p)
        gates={'reconstruction':reconstruction,'bfb':check_bfb(params),'unitarity':unitarity(params,inherit),'ewpo':ewpo(p,record['electroweak'],record['ew_fit'])}
        # Positive reconstructed masses/finite parameters define the physical
        # spectrum card. Record all additional gates, without claiming global
        # scalar acceptance or spending time on numerical vacuum searches.
        assert all(math.isfinite(v) for v in params.values())
        f=matrix(base['yukawas']['F']).copy();y2=matrix(base['yukawas']['Ye2']).copy()
        for i in range(3):
            for j in range(i+1,3):
                f[i,j]*=(.84+.04*i)*np.exp(1j*(.23+.11*j+.07*n));f[j,i]=-f[i,j]
        y2*= (.87+.04*n)*np.exp(1j*(.29-.12*n))
        ml=np.array(base['module2_input']['lepton_masses_GeV'])
        ye=(np.diag(np.sqrt(2)*ml/p['v'])-math.sin(p['beta'])*y2)/math.cos(p['beta'])
        d=-math.sin(p['beta'])*ye+math.cos(p['beta'])*y2
        assert np.max(abs(f+f.T))<1e-20
        assert max(np.max(abs(m)) for m in [f,y2,ye,d])<math.sqrt(4*math.pi)
        ledger=dipole_ledger(f,d,p,ml,1,0)
        total=sum((np.array([v['C_L'],v['C_R']]) for v in ledger.values()),np.zeros(2,complex))
        oldrad=base['signed_radiative']['mu_to_e_gamma']
        oldcs=oldrad['grouped_amplitudes']['scalar_one_loop']
        oldnorm=sum(abs(complex(z['real'],z['imag']))**2 for z in oldcs)
        br=oldrad['grouped_BR']['scalar_one_loop']*sum(abs(total)**2)/oldnorm
        w={'id':record['benchmark_id'],'module2_input':{'scalar':{'record':record},'lepton_masses_GeV':ml.tolist()},
           'yukawas':{name:encoded(v) for name,v in [('F',f),('D',d),('Ye',ye),('Ye2',y2)]},
           'signed_radiative':{'mu_to_e_gamma':{'signed_amplitudes':{'module3_'+key:{'C_L':packed(value['C_L']),'C_R':packed(value['C_R'])} for key,value in ledger.items()},'grouped_amplitudes':{'scalar_one_loop':[packed(z) for z in total]},'grouped_BR':{'scalar_one_loop':br}}}}
        dataset['groups'].append({'ordering':'NOT_A_NEW_NEUTRINO_FIT','witnesses':{'central':w}})
        gate_evidence.append({'id':w['id'],'gates':gates,'physical':p,'frozen_source':'Module1 reconstruction; no vacuum search'})
    data=OUT/'new-inputs.json';data.write_text(json.dumps(dataset,indent=2)+'\n')
    (OUT/'scalar-gates.json').write_text(json.dumps(gate_evidence,indent=2)+'\n')
    for scheme in ['default','matched_leptons']:
        work=OUT/scheme;work.mkdir(exist_ok=True)
        commands=[
          ['compare_dipoles.py','--dataset',str(data),'--workdir',str(work),'--output',str(work/'comparison.json')]+(['--match-leptons'] if scheme=='matched_leptons' else []),
          ['check_components.py','--dataset',str(data),'--logs',str(work),'--output',str(work/'components.json')],
          ['check_rate.py','--comparison',str(work/'comparison.json'),'--logs',str(work)]]
        for args in commands:
            with (work/(args[0]+'.log')).open('w') as log:
                subprocess.run([sys.executable,str(ROOT/args[0]),*args[1:]],stdout=log,stderr=log,check=True)
    records=[]
    for scheme in ['default','matched_leptons']:
        work=OUT/scheme
        comp=json.loads((work/'components.json').read_text())['records']
        for rec in comp:
            for name,c in rec['components'].items():
                errs=c['same_input_candidate_relative_residual']
                assert all(e is not None and e<1e-10 for e in errs),(scheme,rec['group'],name,errs)
            records.append({'scheme':scheme,'group':rec['group'],'components':{name:c['same_input_candidate_relative_residual'] for name,c in rec['components'].items()},'scheme_decomposition':rec['scheme_decomposition'],'readback_masses':rec['masses_readback'],'readback_SM':rec['sm_readback']})
    shifts=[]
    for n in range(2):
        def coeff(s):
            row=json.loads((OUT/s/'comparison.json').read_text())['records'][n]
            return np.array([complex(*row['coefficients_GeV_minus2'][c]['K2']) for c in 'LR'])
        before,after=coeff('default'),coeff('matched_leptons')
        shifts.append({'card':n,'pole_input_only_relative_shift':(abs(after-before)/abs(before)).tolist()})
    evidence={'status':'PASS matched scalar-one-loop amplitudes; no global Zee acceptance','new_cards':2,'full_executions':4,'records':records,'controlled_scheme_shifts':shifts,'scalar_gates':gate_evidence,'dataset_sha256':sha(data),'cards':{str(p.relative_to(OUT)):sha(p) for p in OUT.glob('*/*.in')},'executable_sha256':sha(ROOT/'local/SPheno-4.0.5/bin/SPhenoZeeTypeII')}
    (OUT/'evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
    print(json.dumps({'new_cards':2,'full_executions':4,'pole_input_shifts':shifts,'maximum_matched_residual':max(e for r in records for es in r['components'].values() for e in es)},indent=2))

if __name__=='__main__':main()
