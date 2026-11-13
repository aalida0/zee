"""Build native ZeeTypeII input cards for the NEW three-zero EDM-repaired 64.

REQUIRES the original known-good native SPheno tree-scheme template from
the user's prior successfully validated native model run. The public CI
synthetic template is NOT validated and cannot be used for physics rates.

Retains full unchanged quark/scalar/SM input scheme while replacing exact
physical new complex F and Ye2. Existing module's native source, scale,
physics-mass, loop and observable gates must still be used at execution.
"""
from __future__ import annotations
import argparse,hashlib,json,math
from pathlib import Path
import numpy as np

from module2.interface import decode,encode
from research.full_constraints.scan_pilot_2026.historical_certified_texture import source_points
from research.full_constraints.lfv_64_native_2026.spheno_64_source_gate import (
    set_model_blocks, split_slha,block_values,MINPAR,
)

SEEDS=(20261111,20261112)
ORDERS=('NO','IO')
MASS=np.array([0.00051099895,0.1056583755,1.77686])

def build(source:Path,template:Path,output_dir:Path,template_provenance:str):
    if template_provenance not in ('VALIDATED_USER_NATIVE','SYNTHETIC_CI_NOT_FOR_PHYSICS'):
        raise ValueError('Explicit actual template provenance required')
    if output_dir.exists():
        raise FileExistsError('Do not overwrite native model evidence')
    data=json.loads(source.read_text())
    if (data['n_original_16x4']!=64 or
        data['n_neutrino_exact_perturbative']!=64 or
        data['n_below_JILA_pure_2HDM_proxy']!=64 or
        len(data['records'])!=64):
        raise ValueError('Incomplete new three-zero Zee source family')
    points={x['id']:x for x in source_points()}
    if len(points)!=16:raise ValueError('Original source scalar inventory modified')
    templ=template.read_text()
    ctrl=split_slha(templ,allowed_repeated=('SPHENOINPUT', 'FZEE', 'YEE2',
                                           'FZEEIN','YEE2IN','IMFZEE','IMYEE2',
                                           'IMFZEEIN','IMYEE2IN'))
    if 'MINPAR' not in ctrl or not any(x in ctrl for x in ('FZEEIN','FZEE')):
        raise ValueError('No model specific native source template')
    output_dir.mkdir(parents=True)
    rows=[];seen=set()
    for card in data['records']:
        k=(card['id'],card['ordering'],card['seed'])
        if k in seen or card['ordering'] not in ORDERS or card['seed'] not in SEEDS:
            raise ValueError('Duplicate/source-incorrect family')
        seen.add(k)
        scalar=points[card['id']]
        if scalar['scalar_sha256']!=card['source_scalar_sha256']:
            raise ValueError('Scalar SHA mismatch')
        p=scalar['input_card']['physical']
        F,D=decode(card['Yukawas']['F']),decode(card['Yukawas']['D'])
        if np.max(abs(F+F.T))>1e-14 or max(abs(D[0,1]),abs(D[1,0]),abs(D[0,0]))>1e-10:
            raise ValueError('Original flavor-zero constraints changed')
        beta=p['beta'];v=p['v']
        # Native SPheno.m: Ye=YeSM/cos(beta)-tan(beta)*Ye2
        # Native D=-sin(beta)*Ye+cos(beta)*Ye2,
        # hence Ye2=cos(beta)*D + sin(beta)*YeSM.
        YeSM=np.sqrt(2)*np.diag(MASS/v)
        Ye2=np.cos(beta)*D+np.sin(beta)*YeSM
        residual=max(abs(Ye2/np.cos(beta)-np.tan(beta)*YeSM-D).flatten())
        if residual>1e-12:
            raise ArithmeticError('Native complex lepton input reconstruction failed')
        encoded={'F':encode(F),'Ye2':encode(Ye2)}
        text=set_model_blocks(templ,scalar['input_card'],encoded)
        filename=f'Zee_{k[0]}_{k[1]}_{k[2]}_newEDM3zero.in'
        dest=output_dir/filename
        dest.write_text(text)
        rows.append({'id':list(k), 'source_scalar_sha256':scalar['scalar_sha256'],
              'neutrino_input_sha256':card['new_neutrino_input_sha256'],
              'new_D_sha256':card['new_Yukawa_D_sha256'],
              'new_F_sha256':card['new_Yukawa_F_sha256'],
              'sha256_SLHA':hashlib.sha256(text.encode()).hexdigest(),
              'SLHA':filename,'max_Ye2_re':float(np.max(np.abs(Ye2))),
              'native_physics_executed':False,'global_acceptance':None})
    if len(seen)!=64 or len(set(k[0] for k in seen))!=16:
        raise ValueError('Original 16x4 matrix identity damaged')
    receipt={'template_provenance':template_provenance,\n       'physically_executable_verified':False,\n       'source_file_SHA256':hashlib.sha256(source.read_bytes()).hexdigest(),
       'template_sha256':hashlib.sha256(templ.encode()).hexdigest(),
       'n_cards':len(rows),'model':'Original ZeeTypeII mass tree scheme; native execution not performed',
       'native_source_status':'STAGED_FOR_USER_VALIDATED_NUCLEAR_PATCHED_SPHENO_NOT_EXECUTED',
       'caveat':'Synthetic public CI templates must never be certified for model physics',
       'global_acceptance':None,'cards':rows}
    (output_dir/'manifest-new-EDM3zero.json').write_text(json.dumps(receipt,indent=2,allow_nan=False)+'\n')
    return receipt

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',required=True,type=Path,help='EDM_SUPPRESSED_64_NEUTRINO_AND_2HDM.json from successful exact CI')
    p.add_argument('--template',required=True,type=Path,help='Native ZeeTypeII tree-scheme input or explicitly synthetic CI source template')\n    p.add_argument('--template-provenance',required=True,choices=('VALIDATED_USER_NATIVE','SYNTHETIC_CI_NOT_FOR_PHYSICS'))
    p.add_argument('--output-dir',required=True,type=Path)
    a=p.parse_args()
    receipt=build(a.source,a.template,a.output_dir,a.template_provenance)
    print('STAGED_NEW_64_EDM_TEX_INPUTS',receipt['n_cards'],
          'ORIGINAL_NATIVE_EXECUTION_REQUIRED',flush=True)
if __name__=='__main__':main()
