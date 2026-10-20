#!/usr/bin/env python3
"""Q4 static inventory of PyR@TE's ALREADY exported Zee one-loop RGEs.

No subprocess generation, no execution of generated Python, no accepted
physics RGE coefficients. Verifies presence and syntax of primary exports,
coupling coverage and provenance hashes. Fail closed for missing tensors.
"""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
from pathlib import Path
import sys

EXPECTED_BETA={
    'gauge':('gp','g2','g3'),
    'yukawa':('Yu1','Yu2','Yd1','Yd2','Ye1','Ye2','f'),
    'quartic':('l1','l2','l3','l4','l5','l6','l7','lh','l8','l9','l10'),
    'scalar_mass':('m1','m2','m12','mchi'),
    'trilinear':('muZee',),
}

STATUS='Q4_PYRATE3_EXPORT_STATIC_INVENTORY_NOT_PHYSICS_VALIDATION'

def sha256(path:Path)->str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):
            h.update(block)
    return h.hexdigest()

def static_inspect(root:Path)->dict:
    if not root.is_dir():
        raise FileNotFoundError(f'Generator output directory missing: {root}')
    candidates=list(root.rglob('RGEs.py'))
    if len(candidates)!=1:
        raise ValueError(f'Expected exactly one RGEs.py, found {len(candidates)}')
    rges=candidates[0]
    if rges.parent.name!='PythonOutput':
        raise ValueError(f'Unexpected RGEs.py location: {rges}')
    scripts=sorted(p for p in rges.parent.glob('*.py') if p.is_file())
    if not (rges.parent/'run.py').is_file():
        raise ValueError('PyR@TE run.py export missing')
    model_scripts=[p for p in scripts if p.name not in ('RGEs.py','run.py')]
    if len(model_scripts)!=1:
        raise ValueError(f'Expected exactly one model solver module, got {[p.name for p in model_scripts]}')
    trees={}
    for p in scripts:
        if p.stat().st_size==0:raise ValueError(f'Empty generated output {p}')
        try:
            trees[p.name]=ast.parse(p.read_text(encoding='utf-8'),filename=str(p))
        except (SyntaxError,UnicodeDecodeError) as exc:
            raise ValueError(f'Invalid generated Python syntax in {p}: {exc}') from exc
    functions=[x.name for x in trees['RGEs.py'].body
               if isinstance(x,(ast.FunctionDef,ast.AsyncFunctionDef))]
    repeated=sorted({n for n in functions if functions.count(n)>1})
    if repeated:raise ValueError(f'Duplicate top-level RGE definitions: {repeated}')
    present=set(functions)
    missing={
        group:[c for c in couplings if 'beta_'+c not in present]
        for group,couplings in EXPECTED_BETA.items()
    }
    missing={k:v for k,v in missing.items() if v}
    rows={}
    for p in scripts:
        rows[p.name]={'sha256':sha256(p),'bytes':p.stat().st_size,
                      'relative_path':str(p.relative_to(root))}
    return {
        'status':STATUS,'export_root':str(root.resolve()),
        'generated_python_exports':rows,
        'exported_beta_function_count':len(functions),
        'exported_beta_function_names':sorted(functions),
        'expected_model_couplings':EXPECTED_BETA,
        'missing_expected_beta_functions':missing,
        'static_export_complete':not bool(missing),
        'source_limit_checks_performed':False,
        'kanemura_f_RGE_limit_validated':False,
        'FLS_f_zero_limit_validated':False,
        'independent_RGBeta_crosscheck_validated':False,
        'general_complex_Zee_RGEs_physics_validated':False,
        'physical_Zee_allowed':None,
    }

def main()->int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--generator-output',type=Path,required=True)
    p.add_argument('--report',type=Path,required=True)
    x=p.parse_args()
    if x.report.exists():p.error('Refusing to overwrite existing audit report')
    report={'status':STATUS,'static_export_complete':False,
            'general_complex_Zee_RGEs_physics_validated':False,
            'physical_Zee_allowed':None}
    try:
        report=static_inspect(x.generator_output)
        print('Q4_EXPORTED_BETA_FUNCTION_COUNT',report['exported_beta_function_count'])
        print('Q4_EXPORTED_BETA_FUNCTION_NAMES',
              ', '.join(report['exported_beta_function_names']))
        print('Q4_STATIC_EXPECTED_BETA_INVENTORY',
              'PASS' if report['static_export_complete'] else 'INCOMPLETE')
        if not report['static_export_complete']:
            print('Q4_MISSING_BETAS',json.dumps(report['missing_expected_beta_functions']))
        print('Q4_FULL_COMPLEX_ZEE_PHYSICS_VALIDATION False')
        return 0 if report['static_export_complete'] else 2
    except Exception as exc:
        report['error']=f'{type(exc).__name__}: {exc}'
        print('Q4_EXPORT_AUDIT_FAIL_CLOSED',report['error'],file=sys.stderr)
        return 1
    finally:
        x.report.parent.mkdir(parents=True,exist_ok=True)
        x.report.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
        print('Q4_EXPORT_AUDIT_REPORT',x.report)

if __name__=='__main__':
    raise SystemExit(main())
