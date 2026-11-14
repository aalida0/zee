"""Fail-closed selection of 55 conservative *proxy-level* Zee LFV benchmarks.

Uses the original SHA256-pinned 64 genuine neutrino-inverse source cards and
keeps only those with a corrected pure-2HDM electron-EDM proxy < 1% of the
JILA 90%-CL bound. The physical mixed Zee EDM and full LFV remain UNKNOWN.

python -m research.full_constraints.lfv_literature_closure_2026.robust55_evidence \
  --source EDM_SUPPRESSED_64_NEUTRINO_AND_2HDM.json \
  --output /tmp/zee-robust55-scoped.json
"""
from __future__ import annotations
import argparse,hashlib,json,math
from pathlib import Path
from zipfile import ZipFile,is_zipfile
import numpy as np

SOURCE_SHA256='dc8d462146dd1206e9a4e33aefd5b37673dbe052fdfad998b0d2034156f8b0f9'
MEG_BOUND=1.5e-13
JILA_BOUND=4.1e-30
STRICT_JILA_FRACTION=0.01

def source_bytes(path):
    p=Path(path)
    if is_zipfile(p):
        with ZipFile(p) as z:
            names=[name for name in z.namelist()
                   if name.split('/')[-1]=='EDM_SUPPRESSED_64_NEUTRINO_AND_2HDM.json']
            if len(names)!=1:raise ValueError('Wrong or duplicate 64 JSON in ZIP')
            raw=z.read(names[0])
    else:raw=p.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SOURCE_SHA256:
        raise ValueError('Unreviewed 64-card numerical source bytes; cannot silently replace')
    return json.loads(raw)

def decode(src):
    x=np.asarray(src['real'],dtype=float)+1j*np.asarray(src['imag'],dtype=float)
    if x.shape!=(3,3) or not np.isfinite(x).all():
        raise ValueError('Complex 3x3 matrix missing')
    return x

def select(data):
    if any(data.get(k)!=64 for k in ('n_original_16x4',
                                     'n_neutrino_exact_perturbative',
                                     'n_below_MEGII_one_loop',
                                     'n_below_JILA_pure_2HDM_proxy')):
        raise ValueError('Not 64 original source-validated repaired neutrino cases')
    rows=data.get('records',[])
    if len(rows)!=64:raise ValueError('Missing 64 original records')
    seen=set();all_rows=[]
    for r in rows:
        key=(r['id'],r['ordering'],r['seed'])
        if key in seen:raise ValueError('Duplicate source ID')
        seen.add(key)
        if r['ordering'] not in ('NO','IO') or r.get('global_acceptance') is not None:
            raise ValueError('Wrong source ordering or invented global acceptance')
        if (not r['perturbative'] or r['neutrino_reconstruction_relative']>=2e-9
            or r['neutrino_reconstruction_relative']<0):
            raise ValueError('Source one-loop neutrino reconstruction failed')
        F,D=decode(r['Yukawas']['F']),decode(r['Yukawas']['D'])
        if max(abs(D[0,0]),abs(D[0,1]),abs(D[1,0]))>=1e-10:
            raise ValueError('Exact repaired three-Yukawa zeros changed')
        if np.max(abs(F+F.T))>=1e-13:
            raise ValueError('Original Zee antisymmetric F changed')
        gamma=float(r['one_loop_muegamma_BR'])
        edm=abs(float(r['official_2HDM_proxy_EDM']['total_e_cm']))
        if not (math.isfinite(gamma) and 0<gamma<MEG_BOUND
                and math.isfinite(edm) and 0<=edm<JILA_BOUND):
            raise ValueError('Retained leading numerical LFV/EDM thresholds changed')
        row={'id':[r['id'],r['ordering'],r['seed']],
             'source_new_neutrino_sha256':r['new_neutrino_input_sha256'],
             'source_new_D_sha256':r['new_Yukawa_D_sha256'],
             'source_new_F_sha256':r['new_Yukawa_F_sha256'],
             'radiative_1loop_BR':gamma,
             'EDM_pure_2HDM_proxy_abs_e_cm':edm,
             'EDM_proxy_fraction_of_bound':edm/JILA_BOUND,
             'missing_dipole_amplitude_norm_headroom_over_retained':math.sqrt(MEG_BOUND/gamma)-1,
             'missing_eEDM_absolute_budget_e_cm':JILA_BOUND-edm,
             'strict_proxy_tier':edm<STRICT_JILA_FRACTION*JILA_BOUND,
             'new64_full_mu3e_source_executed':False,
             'new64_full_conversion_source_executed':False,
             'full_physical_Zee_LFV':None,'global_zee_acceptance':None}
        all_rows.append(row)
    if len({z[0] for z in seen})!=16 or len(seen)!=64:
        raise ValueError('Original 16 scalar x four texture identities changed')
    retained=[r for r in all_rows if r['strict_proxy_tier']]
    if len(retained)!=55 or len({r['id'][0] for r in retained})!=16:
        raise ValueError('Original conservative 55/16 tier changed')
    return {'status':'SOURCED_55_LEADING_LFV_AND_PURE_2HDM_EDM_PROXY_NOT_PHYSICAL_ZEE_LFV',
       'SHA256_original_repaired64':SOURCE_SHA256,
       'original_64':len(all_rows),'robust_pure_2HDM_proxy_55':len(retained),
       'source_scalar_id_coverage':sorted({r['id'][0] for r in retained}),
       'normal_ordering_count':sum(r['id'][1]=='NO' for r in retained),
       'inverted_ordering_count':sum(r['id'][1]=='IO' for r in retained),
       'strict_eEDM_fraction_of_JILA':STRICT_JILA_FRACTION,
       'max_retained_mu_to_e_gamma_1loop_BR':max(r['radiative_1loop_BR'] for r in retained),
       'max_retained_EDM_proxy_e_cm':max(r['EDM_pure_2HDM_proxy_abs_e_cm'] for r in retained),
       'min_sufficient_conditional_missing_mu_dipole_factor':min(r['missing_dipole_amplitude_norm_headroom_over_retained'] for r in retained),
       'min_absolute_eEDM_missing_budget_e_cm':min(r['missing_eEDM_absolute_budget_e_cm'] for r in retained),
       'experimental_limits':{'MEGII_BR':MEG_BOUND,'JILA_eEDM_abs_e_cm':JILA_BOUND},
       'scope':'Only a leading-Zee-one-loop-muegamma and full-corrected pure-2HDM eEDM proxy screen. Cannot infer full LFV from proxy margins.',
       'physical_new64_mu3e':None,'physical_new64_conversion':None,'full_Zee_EDM':None,
       'full_physical_LFV':None,'global_zee_acceptance':None,
       'retained55':retained,'all64':all_rows}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',required=True,type=Path)
    p.add_argument('--output',required=True,type=Path)
    args=p.parse_args()
    if args.output.exists():raise FileExistsError('Do not overwrite previously validated evidence')
    obj=select(source_bytes(args.source))
    args.output.write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
    print('ROBUST_55_SOURCED_ONLY',obj['robust_pure_2HDM_proxy_55'],
          'ALL_SCALARS',len(obj['source_scalar_id_coverage']),
          'MAX_MUEG',obj['max_retained_mu_to_e_gamma_1loop_BR'])
    print('FULL_PHYSICAL_ZEE_LFV_UNKNOWN')
if __name__=='__main__':main()
