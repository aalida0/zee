#!/usr/bin/env python3
"""Read only the locally saved four-card native build validation; execute nothing."""
from pathlib import Path
import json, re, sys
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from module14.scan import file_sha,encode
from module7.cascade_z import cascade_width
from module2.core import forward,matrix

def slha(path):
    blocks={};decays={}; current=None; d=None
    for line in path.read_text().splitlines():
        text=line.split('#')[0].split()
        if not text:continue
        if text[0].upper()=='BLOCK':current=blocks.setdefault(text[1].upper(),{});d=None;continue
        if text[0].upper() in ('DECAY','DECAY1L'):
            d=decays.setdefault(text[0].upper(),{}).setdefault(int(text[1]),{'total':float(text[2]),'br':{}});current=None;continue
        try:
            if current is not None:current[tuple(map(int,text[:-1]))]=float(text[-1].replace('D','E'))
            elif d is not None:d['br'][tuple(map(int,text[2:]))]=float(text[0])
        except ValueError:pass
    return blocks,decays
import argparse
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--local',required=True)
parser.add_argument('--original-spheno-archive',required=True)
parser.add_argument('--output',required=True)
args=parser.parse_args()
if file_sha(args.original_spheno_archive) != '3f84a6c3e47f40e0dd1bcccb88eb08a1d0a65aa3d8e42504befdfc3d47ec9529':
    raise ValueError('Pinned pristine SPheno archive mismatch')
original_cards = {0: {'full.in': '3766b799d689467cf733e92c5a803ed6ad66ea0479bbf7ccf5f8c603fa896576', 'original.in': '9f482fff50757228a2919ea1565f48d034349cb34efb99746bc9dce2dd6499c5', 'tree.in': '1f011ef238ac255eb1a8ae9c42e608ce26eb3dd2a186e539bbf53ff826f2ad41'}, 1: {'full.in': '436d89d29f68e9c7b1a26b58227b1a6e92fb407f16cce598c17ffd3cb9da8bad', 'original.in': '4242010cfcc484152b4a26174cdb9751f3dc0adadaa8f0df4f9cd3130fc35d49', 'tree.in': '24b0bac78af2c8f35ea1a76039515166152fad4ae198fa8d74018973063dd335'}, 2: {'full.in': 'aaa21d601c1c58f54060a764e018e7de80270480358f768be406fc1ccb1de002', 'original.in': 'bac3c31269e85de2b3d29683c70c826361de655cfe178d3e299e80a8a4fb1eda', 'tree.in': '4a735620b95f4a403e0d0b3113020f933b12b3173403b2581fc6ba44452fcda4'}, 3: {'full.in': 'd5efc93f376a2221b106066a68e5c5f74c86d3dfcb736035c6031cc48fc3ee3e', 'original.in': 'b6682f2d790ea945daa89383ad57347e9f8884bf7e34f2f483391c750b578ba6', 'tree.in': '788ae8cb1bc1c00d15f550808975af007d6b248e5f9c966574dbc9834360c3ab'}}
root=Path(args.local);groups=json.load(open('validation/module12/d12_benchmarks.json'))['groups']; comparisons=[]
for i,g in enumerate(groups):
    w=g['witnesses']['central'];p=w['module2_input']['scalar']['record']['physical'];runtime=root/'runtime'/f'group{i}'
    for mode in ('tree','full'):
        if 'Finished!' not in (runtime/(mode+'.log')).read_text():
            raise ValueError('Incomplete native runtime')
        if re.search(r'(?i)\b(nan|infinity)\b',(runtime/(mode+'.spc')).read_text()):
            raise ValueError('Nonfinite native spectrum')
    if any(file_sha(runtime/name) != sha for name, sha in original_cards[i].items()):
        raise ValueError('Only original saved D12 cards and recorded evaluation flags are accepted')
    tree,dt=slha(runtime/'tree.spc');loop,dl=slha(runtime/'full.spc')
    def mx(b,name):return np.array([[b[name][(i,j)]+1j*b.get('IM'+name,{}).get((i,j),0) for j in range(1,4)] for i in range(1,4)])
    uv=mx(loop,'UVMIX');zp=mx(tree,'CHARGEMIX')
    expected_zp=np.array([[np.cos(p['beta']),np.sin(p['beta']),0],[-np.sin(p['beta'])*np.cos(p['gamma']),np.cos(p['beta'])*np.cos(p['gamma']),np.sin(p['gamma'])],[np.sin(p['beta'])*np.sin(p['gamma']),-np.cos(p['beta'])*np.sin(p['gamma']),np.cos(p['gamma'])]])
    # Independent D4 tree H2->H1 Z depends on scalar card and frozen EW.
    card={'mH1_GeV':p['mH1'],'mH2_GeV':p['mH2'],'gamma_rad':p['gamma'],'v_GeV':p['v'],'mW_GeV':80.379,'mZ_GeV':91.1876}
    ref=cascade_width(card)['partial_width_GeV']
    gz=(tree['GAUGE'][(1,)]**2+tree['GAUGE'][(2,)]**2)**.5
    matched_ref=ref*(gz/(2*card['mZ_GeV']/p['v']))**2
    measured=dt['DECAY'][9000037]['total']*dt['DECAY'][9000037]['br'].get((37,23),0.)
    # Compare a complete scalar one-loop subset only; native includes gauge.
    lfv={}
    for k,ch in [(701,'mu_to_e_gamma'),(702,'tau_to_e_gamma'),(703,'tau_to_mu_gamma')]:
        reference=w['signed_radiative'][ch]['grouped_BR']['scalar_one_loop']
        lfv[ch]={'tree_scheme_native_BR':tree['FLAVORKITLFV'][(k,)],'module4_scalar_reference_BR':reference,
                 'relative_rate_difference':abs(tree['FLAVORKITLFV'][(k,)]/reference-1),'full_scheme_native_BR':loop['FLAVORKITLFV'][(k,)]}
    y=w['yukawas'];ml=w['module2_input']['lepton_masses_GeV']
    arr=lambda z:np.array(z['real'])+1j*np.array(z['imag'])
    mnu=forward(arr(y['F']),arr(y['D']),m1=p['mH1'],m2=p['mH2'],gamma=p['gamma'],ml=ml)
    target=np.linalg.svd(mnu,compute_uv=False)[::-1]
    comparisons.append({'group':i,'id':w['id'],'tree_scalar_mass_max_relative_difference':max(abs(tree['MASS'][(k,)]/p[n]-1) for k,n in [(25,'mh1'),(35,'mh2'),(36,'ma'),(37,'mH1'),(9000037,'mH2')]),
        'charged_mixing_absolute_magnitude_max_difference':float(np.max(abs(abs(zp)-abs(expected_zp)))),
        'neutrino_UV_unitarity_max_residual':float(np.max(abs(uv@uv.conjugate().T-np.eye(3)))),
        'full_scheme_neutrino_masses_eV':[loop['MASS'][(k,)]*1e9 for k in (12,14,16)],'module2_neutrino_singular_values_eV':target.tolist(),
        'h_light_full_mass_GeV':loop['MASS'][(25,)],'h_light_full_DECAY1L_total_GeV':dl['DECAY1L'][25]['total'],
        'h125_tree_scheme_gamma_gamma_width_GeV':dt['DECAY'][25]['total']*dt['DECAY'][25]['br'].get((22,22),0),
        'D4_H2_H1Z_width_GeV':ref,'native_tree_H2_H1Z_width_GeV':measured,'D4_cascade_relative_difference':abs(measured/ref-1),'matched_native_gauge_D4_relative_difference':abs(measured/matched_ref-1),'native_gZ':gz,
        'LFV':lfv,'additional_LFV':'UNVALIDATED; nonzero values are not interference/coverage checks',
        'files_sha256':{f.name:file_sha(f) for f in runtime.iterdir() if f.name in ('original.in','full.in','tree.in','full.log','tree.log','full.spc','tree.spc')}})
report={'build_status':'SPHENO_FULL_BUILD_VALIDATED','physics_adapter_status':'UNVALIDATED','operative_observables':[],
        'sarah':'4.15.4','spheno':'4.0.5','compiler':'GNU Fortran 11.4.0; pristine SPheno archive, no precision patches',
        'original_minimal_compile_command':'gfortran -c -g -ffree-line-length-none -J. -I ORIGINAL_SPHENO/include Wrapper_LoopDecay_Fe_ZeeTypeII.f90',
        'original_error':'Function zrunomatrix / zrunomatrixc has no IMPLICIT type',
        'original_minimal_log_sha256':file_sha(root/'original-minimal-compile.log'),
        'original_wrapper_sha256':file_sha(root/'original-repro/Wrapper_LoopDecay_Fe_ZeeTypeII.f90'),
        'cause':'Majorana Fv has no MatterSector rotation; getMixingMatrix[Fv]={NoMatrix,NoMatrix} differs from loop-decay guard {NoMatrix}; generated external rotations reference nonexistent ZRU symbols',
        'fix':'Add {{vL},{VL,UV}}, UV metadata and Fv->{VL,conj[VL]}; regenerate all interfaces/couplings/masses/decays with unchanged Lagrangian. No identity assignment or removed physical modes.',
        'original_query_log_sha256':file_sha(root/'original-query.log'),'mathematica_version':'15.0.1 Linux x86 64-bit, July 2 2026',
        'generation_log_sha256':file_sha(root/'generation.log'),'full_build_log_sha256':file_sha(root/'full-build.log'),
        'executable_sha256':file_sha(root/'SPheno-4.0.5/bin/SPhenoZeeTypeII'),
        'spheno_archive_sha256':file_sha(args.original_spheno_archive),
        'input_reference_sha256':file_sha('validation/module12/d12_benchmarks.json'),
        'corrected_model_sha256':{p.name:file_sha(p) for p in (root/'models/ZeeTypeII').iterdir()},
        'original_model_sha256':{p.name:file_sha(p) for p in Path('models/SARAH/ZeeTypeII').glob('*.m')},
        'generated_source_sha256':{str(p.relative_to(root/'output')):file_sha(p) for p in sorted((root/'output').rglob('*')) if p.is_file() and p.suffix in ('.f90','.F90','.vin','.xml')},
        'runtime_summary':json.load(open(root/'runtime/summary.json')),'tree_runtime_summary':json.load(open(root/'runtime/tree-summary.json')),'comparisons':comparisons,
        'limitations':['Tree-scheme radiative rates not fully matched complex dipoles; stock kernels not precision-patched','Full loop spectrum and neutrino masses not scheme-matched to D12; light scalar no longer h125','Nonperturbative-size one-loop widths reject HiggsTools replacement','No validated nonzero scalar/box/penguin interference reference for three-body or conversion','No new operative flavor/vacuum/Higgs constraint']}
with open(args.output,'x') as f:f.write(encode(report)+'\n')
