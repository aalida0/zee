#!/usr/bin/env python3
"""Four frozen texture cards: source-checked subsets only, never a full LFV prediction."""
import csv, hashlib, json, math, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; sys.path.insert(0,str(ROOT))
import numpy as np
from module2.interface import decode, canonical_hash
from module3.core import vertices
from module3 import tree
from research.full_constraints.lfv.source_to_code import box_kernel
O=Path(__file__).resolve().parent
CARD=ROOT/'validation/module12/d12_benchmarks.json'
EXPECTED='f31ef3ccb64c3e4ff53131d35d52c21536b951a01e2c3924af766b7b2adf1cd8'

def current(z,n,gp,gn):
    """Correct FlavorKit equal-density isoscalar/isovector contraction; complex allowed."""
    g0=(gp+gn)/2; g1=(gp-gn)/2
    return (z+n)*g0+(z-n)*g1

def pair(z): return [float(complex(z).real),float(complex(z).imag)]

def run():
    assert hashlib.sha256(CARD.read_bytes()).hexdigest()==EXPECTED
    groups=json.loads(CARD.read_text())['groups']; assert len(groups)==4
    integrated=json.loads((ROOT/'research/full_constraints/lfv_integrated_2026/DIPOLE_TERMS.json').read_text())
    byid={x['id']:x for x in integrated['cards']}
    rows=[]; cards=[]
    limits={'mu_to_e_gamma':1.5e-13,'tau_to_e_gamma':5.6e-8,'tau_to_mu_gamma':4.2e-8,'mu3e':1e-12,'muAl_conversion':None}
    for group in groups:
        w=group['witnesses']['low_joint']; p=w['module2_input']['scalar']['record']['physical']; y=w['yukawas']
        assert {k:canonical_hash(v) for k,v in y.items()}==w['yukawa_sha256']
        assert canonical_hash(w['module2_input']['scalar']['record'])==w['scalar_sha256']
        neutral=vertices(decode(y['D']),p,w['module2_input']['lepton_masses_GeV'])
        scalars=tree.wilsons(neutral,1,0,0)
        sc={'S'+k:pair(sum(row['direct'][k] for row in scalars.values())) for k in ('LL','RR','LR','RL')}
        f=decode(y['F']); kernel=box_kernel(p['mH1'],p['mH2'],p['gamma'])
        box=f[1,2]*f[0,2].conjugate()*np.sum(abs(f[0])**2)*kernel/(64*math.pi**2)
        dip=byid[w['id']]; radiative={}
        for ch in ['mu_to_e_gamma','tau_to_e_gamma','tau_to_mu_gamma']:
            old=w['signed_radiative'][ch]
            radiative[ch]={'C_L':old['C_L'],'C_R':old['C_R'],'BR_subset':old['BR_implemented'],'status':'CONDITIONAL_SUBSET','limit_90CL':limits[ch]}
        radiative['mu_to_e_gamma']['neutral_Zgamma_C_LR']=dip['zgamma_C']
        radiative['mu_to_e_gamma']['baseline_plus_Zgamma_BR_subset']=dip['baseline_plus_zgamma_partial_BR']
        cards.append({'id':w['id'],'scalar_sha256':w['scalar_sha256'],'yukawa_sha256':w['yukawa_sha256'],
                      'radiative':radiative,'tree_scalar_contact_GeV_minus2':sc,'mu3e_tree_only_BR_saved':w['mu_to_3e_tree'],
                      'F_only_box_raw_VLL_GeV_minus2':pair(box),'F_only_box_paper_L_PLPL_GeV_minus2':pair(-box),
                      'box_warning':'full ordered-action bridge to photon and Z amplitudes unvalidated',
                      'mu3e_complete_wilson':None,'conversion_complete_wilson':None,'physical_lfv':'UNKNOWN','global_acceptance':None})
        for ch in limits:
            subset=radiative[ch]['BR_subset'] if ch in radiative else None
            rows.append({'card':w['id'],'observable':ch,'subset_rate':subset,'limit_90CL':limits[ch],
                         'subset_below_limit':(subset<limits[ch]) if subset is not None else None,
                         'physical_rate':None,'classification':'UNKNOWN'})
    result={'verdict':'LFV_LEADING_SCOPE_INCOMPLETE','card_file_sha256':EXPECTED,'cards':cards,
            'uncertainty':'Unquantified missing amplitudes, nuclear matching and input schemes; no numerical theory bound assigned.',
            'physical_lfv':'UNKNOWN','global_acceptance':None}
    (O/'NUMERICAL.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    with (O/'CONSTRAINT_MATRIX.csv').open('w',newline='') as out:
        writer=csv.DictWriter(out,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    print('PASS: four frozen cards; scoped tree contacts, F-only boxes and stored radiative coefficients')
if __name__=='__main__': run()
