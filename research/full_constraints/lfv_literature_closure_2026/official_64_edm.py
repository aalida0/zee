"""Source-locked corrected 2HDM electron EDM on 64 original Zee cards.

ONLY pure-2HDM control; missing two physical mixed Zee charged states and F.
Never label a result full Zee EDM, LFV pass, or complete model acceptance.
"""
import argparse, hashlib, importlib.util, inspect, json, math, sys, textwrap
from pathlib import Path
from zipfile import ZipFile
import numpy as np

from research.full_constraints.lfv_2hdm_gitlab_reuse_2026.official_gitlab_control import make_input

SRC_SHA='9b4af7aa4bf7bf533a7b82c8c2603d118346424e3b7b5f9f06ab8cb41bc4e193'
DATASET_SHA='2d97c2a58cb65f5ec7244282a04c5e19a0cae0897b8a0581b76503180acd4be9'
CM_PER_GEV=1.973269804e-14
BOUND_90CL=4.1e-30
V=246.21965
ML=np.array([0.00051099895,0.1056583755,1.77686])

def slha_blocks(raw):
    result, active={},None
    for line in raw.decode('utf-8').splitlines():
        cols=line.partition('#')[0].split()
        if not cols:continue
        if len(cols)==2 and cols[0].upper()=='BLOCK':
            active=cols[1].upper()
            if active in result:raise ValueError('Repeated original SLHA block')
            result[active]={}
        elif active and len(cols)>=2:
            try:
                idx=tuple(map(int,cols[:-1]))
                val=float(cols[-1].replace('D','E').replace('d','E'))
            except ValueError:
                continue
            if not idx or idx in result[active] or not math.isfinite(val):
                raise ValueError('Malformed SLHA')
            result[active][idx]=val
    return result

def complex_matrix(blocks,stem):
    full={(i,j) for i in range(1,4) for j in range(1,4)}
    if not set(blocks[stem])==set(blocks['IM'+stem])==full:
        raise ValueError('Incomplete original complex SLHA matrix: '+stem)
    return np.array([[complex(blocks[stem][i,j],blocks['IM'+stem][i,j])
                      for j in range(1,4)] for i in range(1,4)])

def official_class(directory):
    path=Path(directory)/'thdm.py'
    if hashlib.sha256(path.read_bytes()).hexdigest()!=SRC_SHA:
        raise ValueError('Unexpected official corrected thdm.py hash')
    spec=importlib.util.spec_from_file_location('official_zee_2hdm_control',path)
    module=importlib.util.module_from_spec(spec)
    sys.path.insert(0,str(path.parent))
    try:spec.loader.exec_module(module)
    finally:sys.path.remove(str(path.parent))
    return module.thdm

def original_edm_groups(model):
    fn=type(model).electron_EDM
    old=textwrap.dedent(inspect.getsource(fn))
    marker='return de_1loop + de_2loop'
    if old.count(marker)!=1:raise ValueError('Official EDM source changed')
    names={'one_loop':'de_1loop',
      'neutral_fermion_top':'de_2loop_th',
      'neutral_fermion_charm':'de_2loop_ch',
      'neutral_fermion_bottom':'de_2loop_bh',
      'neutral_fermion_tau':'de_2loop_tauh',
      'charged_fermion_top':'de_2loop_tHp',
      'charged_fermion_charm':'de_2loop_cHp',
      'charged_fermion_tau':'de_2loop_tauHp',
      'neutral_hZ':'de_2loop_hZ','kinetic':'de_2loop_kin',
      'charged_bosonic_photon':'de_2loop_HA',
      'charged_bosonic_Z':'de_2loop_HZ','charged_bosonic_W':'de_2loop_HW'}
    replacement='return {'+','.join(repr(k)+':'+v for k,v in names.items())+'}'
    env={}
    exec(old.replace(marker,replacement),fn.__globals__,env)
    terms=env['electron_EDM'](model)
    total=sum(terms.values())
    exact=fn(model)
    if not math.isfinite(float(total)) or not math.isclose(total,exact,rel_tol=1e-12,abs_tol=1e-45):
        raise ArithmeticError('Official pure2HDM EDM group sum fails')
    scale=CM_PER_GEV/model.el
    terms={k:float(v*scale) for k,v in terms.items()}
    return {'groups_e_cm':terms,
            'total_e_cm':float(total*scale),
            'one_loop_e_cm':terms['one_loop'],
            'neutral_fermion_gamma_and_Z_e_cm':sum(
                v for k,v in terms.items() if k.startswith('neutral_fermion'))}

def evaluate(artifact,scalar_path,upstream):
    data=json.loads(Path(scalar_path).read_text())
    # Source artifact contains reconstructed 16x4 records, not the historical
    # candidate_followup table. Reconcile every ID+SHA against that original.
    original=json.loads((Path(__file__).resolve().parents[3]/
        'module14/conditional_scan/candidate_followup.json').read_text())
    if original['dataset_sha256']!=DATASET_SHA:raise ValueError('Original scalar source drift')
    reference={str(x['id']):x for x in original['tables']['CERTIFIED_VACUUM_APPROX_BSG_16']}
    if len(reference)!=16 or len(data['scalars'])!=16:raise ValueError('Wrong scalar count')
    spectra={}
    for row in data['scalars']:
        sid=str(row['scalar_id'])
        if sid not in reference or row['scalar_sha256']!=reference[sid]['scalar_sha256']:
            raise ValueError('Scalar hash mismatch against original historical source')
        physical=row['scalar_input']['physical']
        if physical!=reference[sid]['physical']:
            raise ValueError('Rebuilt scalar physical data mismatch')
        spectra[sid]={'physical':physical,'scalar_sha256':row['scalar_sha256']}
    if len(spectra)!=16:raise ValueError('Incomplete scalar identity set')
    upstream_model=official_class(upstream)
    rows=[]
    with ZipFile(artifact) as z:
        m=[name for name in z.namelist() if name.endswith('/source-manifest.json')]
        if len(m)!=1:raise ValueError('No unique exact-source manifest')
        manifest=json.loads(z.read(m[0]))
        if len(manifest['cards'])!=64:raise ValueError('Wrong original card count')
        for entry in manifest['cards']:
            sid=str(entry['scalar_id'])
            scalar=spectra[sid]
            if scalar['scalar_sha256']!=entry['source_scalar_sha256']:
                raise ValueError('Original scalar SHA mismatch')
            n=[x for x in z.namelist() if x.endswith('/'+entry['slha_file'])]
            if len(n)!=1:raise ValueError('Ambiguous original SLHA')
            raw=z.read(n[0])
            if hashlib.sha256(raw).hexdigest()!=entry['slha_sha256']:
                raise ValueError('Source original Yukawa SHA mismatch')
            b=slha_blocks(raw)
            Y2=complex_matrix(b,'YEE2')
            F=complex_matrix(b,'FZEE')
            if np.max(np.abs(F+F.T))>1e-16:raise ValueError('Zee F antisymmetry broken')
            p=scalar['physical']
            tanb=b['MINPAR'][(10,)]
            if not abs(math.tan(p['beta'])-tanb)<1e-10:raise ValueError('Incorrect tanbeta')
            YeSM=np.diag(np.sqrt(2)*ML/V)
            D=Y2/math.cos(p['beta'])-tanb*YeSM
            old={'id':str(entry['scalar_id'])+'_'+entry['ordering']+'_'+str(entry['seed']),
                 'module2_input':{'scalar':{'record':{'physical':p}}},
                 'yukawas':{'D':{'real':D.real.tolist(),'imag':D.imag.tolist()}}}
            couplings,metadata=make_input(old,'bare')
            group=original_edm_groups(upstream_model(couplings))
            group.update({'id':[entry['scalar_id'],entry['ordering'],entry['seed']],
                'source_SLHA_sha256':entry['slha_sha256'],
                'source_scalar_sha256':entry['source_scalar_sha256'],
                'pure_2HDM_one_charged_mass_proxy':True,
                'genuine_Zee_F_charged_mixed_two_loop':None,
                'physical_Zee_EDM':None})
            rows.append(group)
    if len(rows)!=64 or len({tuple(x['id']) for x in rows})!=64:raise ValueError('Incomplete original source cards')
    peak=max(rows,key=lambda x:abs(x['total_e_cm']))
    return {'status':'CORRECTED_OFFICIAL_2HDM_64_PROXY_NOT_PHYSICAL_ZEE_EDM',
       'pinned_upstream_sha256':SRC_SHA,'n_original_source_cards':64,
       'experimental_bound_e_cm':BOUND_90CL,
       'n_proxy_above_edm_bound':sum(abs(x['total_e_cm'])>BOUND_90CL for x in rows),
       'max_abs_2HDM_proxy_e_cm':abs(peak['total_e_cm']),
       'max_proxy_source_id':peak['id'],
       'max_neutral_fermion_gamma_Z_e_cm':max(abs(x['neutral_fermion_gamma_and_Z_e_cm']) for x in rows),
       'full_Zee_EDM':None,'global_acceptance':None,
       'scope':'Original corrected official source, pure-2HDM; no Zee F, 2 charged eigenstates or mixed Z/W vertices',
       'rows':rows}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--artifact',required=True,type=Path)
    p.add_argument('--scalar-source',required=True,type=Path)
    p.add_argument('--upstream',required=True,type=Path)
    p.add_argument('--output',required=True,type=Path)
    a=p.parse_args()
    if a.output.exists():raise FileExistsError('Refuse overwrite')
    r=evaluate(a.artifact,a.scalar_source,a.upstream)
    a.output.write_text(json.dumps(r,indent=2,allow_nan=False)+'\n')
    print('PURE_2HDM_PROXY',r['n_original_source_cards'],'EDM_ABOVE',r['n_proxy_above_edm_bound'],
          'MAX',r['max_abs_2HDM_proxy_e_cm'],flush=True)
    print('FULL_ZEE_EDM_UNKNOWN')
if __name__=='__main__':main()
