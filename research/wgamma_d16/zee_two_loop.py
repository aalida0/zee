"""Isolated radiative-dipole CLI: available classes, guarded unavailable total.

python -m research.wgamma_d16.zee_two_loop --witness NO --output PATH
python -m research.wgamma_d16.zee_two_loop --input module4/example.json --output PATH
--require-completion exits 2 AFTER writing evidence when a class is missing.
"""
import argparse
import json
from pathlib import Path
import platform
import subprocess
import time

import numpy as np
import scipy
from module2.interface import canonical_hash
from module3.core import dipole_ledger, radiative_width, OPERATOR, BASIS
from module4.interface import unpack
from module4.amplitudes import ledger as photon_ledger, CHANNELS
from module4.charged_scalar import ledger as scalar_photon_ledger
from .external_2hdm import pack, sha
from .zee_mixed_hz import mixed_hz
from .neutral_fermion_z import ledger as neutral_z_ledger
from .f_current_probe import probe

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

MISSING={
    'kinetic_W_Goldstone_ghost_pinch_LSZ':
        'full Zee physical-charged/W-G/BRST/LSZ sum; the new regulated xi=1 WWW outer topology is not a complete gauge class',
    'potential_charged_W':
        'unequal charged masses, physical W derivative currents, Goldstone mass-difference partners and matched full-set subtraction; diagonal f11 reuse not established',
    'charged_fermion_W':
        'general charged mixing and native complex currents in complete charged-current aggregate; no whole-group rescaling established',
    'F_dagger_F_two_loop':
        'surviving gauge-dressed charged-scalar/neutrino graphs, external emission, counterterms and LSZ; regulated W-neutrino subloop has a nonzero UV pole',
    'neutral_mixing_reducible_sector':
        'assignment/cancellation of A-Z/G0 and A-G+-H+- source terms with external photon emission and renormalized two-point insertions',
}


def witness(ordering='NO',spectrum=0):
    """Actual frozen inverse, with explicit illustrative quark mass dataset."""
    from module3.witnesses import example
    from module2.interface import evaluate as neutrino
    original=json.loads((ROOT/'module4/example.json').read_text())
    inp=example(ordering,spectrum)
    return dict(schema_version='1.0.0',kind='module3_matching_input_v1',
                module3_input=inp,module2_output=neutrino(inp['module2_input']),
                two_loop_inputs=original['two_loop_inputs'])


def add(rows,key,coefficient,error,order,group,source):
    if key in rows:
        raise ValueError('Duplicate coherent contribution: '+key)
    c=np.asarray(coefficient,complex);err=np.broadcast_to(np.asarray(error,float),(2,))
    if c.shape!=(2,) or not np.isfinite(c).all() or not np.isfinite(err).all() or min(err)<0:
        raise ValueError('Finite complex coefficient pair and nonnegative numerical errors required')
    rows[key]=dict(C_LR=c,K2_LR=-c.conjugate(),quadrature_error=err,loop_order=order,
                   gauge_invariant_class=group,source=source,
                   operator=OPERATOR,basis=BASIS)


def evaluate(data):
    start=time.perf_counter()
    inp,nout,p,ml,F,D=unpack(data)
    scalar=inp['module2_input']['scalar']['record']
    scalar=scalar.get('input',scalar)
    mw,mz=scalar['electroweak']['mW'],scalar['electroweak']['mZ']
    alpha=(2*mw/p['v'])**2*(1-(mw/mz)**2)/(4*np.pi)
    fm=data['two_loop_inputs']['fermion_masses_GeV']
    channels={}
    for name,(i,j) in CHANNELS.items():
        rows={}
        for key,row in dipole_ledger(F,D,p,ml,i,j).items():
            add(rows,'one_loop_'+key,[row['C_L'],row['C_R']],0.,1,'frozen_one_loop','Module3/D15')
        for key,row in photon_ledger(D,p,ml,alpha,fm,mw,i,j).items():
            if row['coherent_inclusion']:
                add(rows,'photon_'+key,[row['C_L'],row['C_R']],row['numerical_error'],2,
                    'fermion_photon','Module4 MATCHING_AUDIT')
        for key,row in scalar_photon_ledger(D,p,ml,alpha,i,j).items():
            add(rows,'photon_'+key,[row['C_L'],row['C_R']],row['numerical_error'],2,
                'physical_scalar_photon','Module4 CHARGED_SCALAR_AUDIT')
        for key,row in neutral_z_ledger(D,p,ml,mw,mz,fm,i,j).items():
            add(rows,'neutral_'+key,row['C_LR'],row['quadrature_error'],2,
                'neutral_fermion_Z_photon','neutral_fermion_z.py; common native neutral currents')
        hz=mixed_hz(D,p,ml,mw,mz,i,j)
        for key,row in hz['rows'].items():
            add(rows,'physical_scalar_Z_'+key,row['C_LR'],row['error'],2,
                'physical_scalar_Z_photon_current','zee_mixed_hz.py; real-photon current subset only')
        totals={group:sum((r['C_LR'] for r in rows.values() if r['gauge_invariant_class']==group),
                          np.zeros(2,complex)) for group in sorted({r['gauge_invariant_class'] for r in rows.values()})}
        total=sum(totals.values(),np.zeros(2,complex))
        one=totals['frozen_one_loop'];two=total-one
        err=sum((r['quadrature_error'] for r in rows.values()),np.zeros(2))
        gamma_total=inp['constants']['total_lepton_widths_GeV'][0 if i==1 else 1]
        width=radiative_width(total,ml[i],ml[j],inp['constants']['alpha_em'])
        # This is a partial, coherently interfering rate. Full total stays null.
        channels[name]=dict(ledger=rows,class_totals=totals,
            included_only_C_LR=total,included_only_two_loop_C_LR=two,
            included_only_quadrature_error=err,included_only_BR=width/gamma_total,
            one_two_loop_interference_norm2=float(2*np.vdot(one,two).real),
            incoherent_one_plus_two_norm2=float(np.vdot(one,one).real+np.vdot(two,two).real),
            mixed_hz_current=hz,full_two_loop_C_LR=None,full_C_LR=None,full_BR=None,
            unavailable_classes={k:dict(status='NOT_CALCULATED',C_LR=None,reason=v) for k,v in MISSING.items()})
    return dict(status='BLOCKED_ZEE_TWO_LOOP_COMPLETION',
        acceptance_target='ZEE_TWO_LOOP_RADIATIVE_LFV_PASS',acceptance=False,
        scope='INCLUDED_CLASSES_ONLY; no full radiative LFV prediction or exclusion',
        channels=channels,F_current_probe=probe(F),
        gates=dict(input_neutrino_forward=nout['gates']['forward'],
            physical_scalar_Z_radiative_current='SCOPED_PASS',
            neutral_fermion_Z_photon='COMMON_CLASS_SCOPED_PASS',
            full_mixed_potential_Z_sector='UNKNOWN_REDUCIBLE_ASSIGNMENT',
            Zee_W_gauge_UV_ST='NOT_CALCULATED',F_quadratic_gauge_sum='NOT_CALCULATED'),
        input_sha256=canonical_hash(data),
        neutrino_input_sha256=nout['provenance']['input_sha256'],
        ordering=inp['module2_input']['ordering'],physical=p,
        inputs=dict(D=D,F=F,lepton_masses_GeV=ml,fermion_masses_GeV=fm),
        scheme=dict(virtual_gauge_couplings='tree_on_shell_MW_MZ_v',alpha_loop=alpha,
                    alpha_real_photon_rate=inp['constants']['alpha_em'],
                    quark_mass_dataset=data['two_loop_inputs'],
                    approximation='mnu=0; leading external invariants in two-loop denominators; quadratic Yukawa scope; no QED running',
                    truncation_error='NOT_QUANTIFIED; quadrature errors exclude truncation, matching and input errors'),
        provenance=dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            code_sha256={str(f.relative_to(ROOT)):sha(f) for directory in
                (HERE,ROOT/'module3',ROOT/'module4') for f in sorted(directory.glob('*.py'))},
            frozen_model_sha256=sha(ROOT/'models/SARAH/ZeeTypeII/ZeeTypeII.m'),
            D15_bridge_evidence_sha256=sha(ROOT/'research/spheno_flavorkit/crossing_bridge_evidence.json'),
            environment=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__)),
        elapsed_seconds=time.perf_counter()-start)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    source=ap.add_mutually_exclusive_group(required=True)
    source.add_argument('--input',type=Path)
    source.add_argument('--witness',choices=('NO','IO'))
    ap.add_argument('--spectrum',type=int,choices=(0,1,2),default=0)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--require-completion',action='store_true')
    args=ap.parse_args()
    data=json.loads(args.input.read_text()) if args.input else witness(args.witness,args.spectrum)
    result=evaluate(data)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(pack(result),indent=2,sort_keys=True,allow_nan=False)+'\n')
    print(result['status'],len(result['channels']),'channels;',
          len(next(iter(result['channels'].values()))['ledger']),'included rows/channel')
    if args.require_completion and not result['acceptance']:
        raise SystemExit(2)


if __name__=='__main__':
    main()
