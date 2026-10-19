#!/usr/bin/env python3
"""Q4 fail-closed PyR@TE3 input/runner gate for the general Zee theory.

Checks field/operator inventory and one-loop gauge b_i independently from
the YAML header. Optionally executes pinned PyR@TE3. Generated beta functions
remain UNVALIDATED until Kanemura/FLS limits and independent generator agree.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import time
import traceback
from fractions import Fraction
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / 'rge_models/GeneralZee_PyRATE3_CANDIDATE_NOT_VALIDATED.model'
PYRATE_SHA = '04b219c2016f3fc4f2371d72607edc26a7e06364'
PYRATE_REMOTE = 'https://github.com/LSartore/pyrate.git'
STATUS = 'Q4_SOURCE_AND_GENERATOR_EXECUTION_GATE_NOT_VALIDATED_FULL_ZEE_BETAS'
EXPECTED = {
    'Yukawas': {'Yu1','Yu2','Yd1','Yd2','Ye1','Ye2','f'},
    'QuarticTerms': {'l1','l2','l3','l4','l5','l6','l7','lh','l8','l9','l10'},
    'TrilinearTerms': {'muZee'},
    'ScalarMasses': {'m1','m2','m12','mchi'},
}
FIELD_Y = {
    'QLbar':Fraction(-1,6),'QL':Fraction(1,6),
    'LLbar':Fraction(1,2),'LL':Fraction(-1,2),
    'uR':Fraction(2,3),'dR':Fraction(-1,3),'eR':Fraction(-1,1),
    'Phi1':Fraction(1,2),'Phi2':Fraction(1,2),
    'Phi1bar':Fraction(-1,2),'Phi2bar':Fraction(-1,2),
    'Phi1tilde':Fraction(-1,2),'Phi2tilde':Fraction(-1,2),
    'chi':Fraction(1,1),'chibar':Fraction(-1,1),
}
TOKEN_RE = re.compile(r'(?<![A-Za-z0-9_])('+ '|'.join(sorted(FIELD_Y,key=len,reverse=True)) + r')(?![A-Za-z0-9_])')


def sha256(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def block(source:str,name:str)->str:
    """Locate named brace-delimited PyR@TE 3 model section."""
    m=re.search(r'(?m)^\s*'+re.escape(name)+r'\s*:\s*\{',source)
    if not m: raise ValueError(f'Missing model block {name}')
    i=source.index('{',m.start()); depth=0
    for j in range(i,len(source)):
        if source[j]=='{':depth+=1
        if source[j]=='}':
            depth-=1
            if depth==0:return source[i:j+1]
    raise ValueError(f'Unclosed block {name}')


def declared_terms(s:str)->dict[str,str]:
    # Component lists, no nested coupling objects in this candidate.
    d={}
    for line in s.splitlines()[1:-1]:
        line=line.split('#',1)[0].strip()
        if not line:continue
        m=re.fullmatch(r'([A-Za-z]\w*)\s*:\s*(.+?),?',line)
        if m is None:raise ValueError('Unparsable coupling line: '+line)
        k,v=m.group(1),m.group(2).rstrip(',').strip()
        if k in d:raise ValueError('Duplicate coupling '+k)
        d[k]=v
    return d


def group_index(n:int)->Fraction:
    if n==1:return Fraction(0)
    if n==2:return Fraction(1,2)
    if n==3:return Fraction(2)
    raise ValueError(f'Unknown SU2 rep {n}')


def colour_index(n:int)->Fraction:
    if n==1:return Fraction(0)
    if n==3:return Fraction(1,2)
    raise ValueError(f'Unknown SU3 rep {n}')


def gauge_from_content(ferm:dict,scalars:dict)->tuple[Fraction,Fraction,Fraction]:
    """Weyl fermion and complex scalar gauge coefficient calculation."""
    out=[Fraction(0),Fraction(-22,3),Fraction(-11)]
    for dataset,prefac in ((ferm,Fraction(2,3)),(scalars,Fraction(1,3))):
        for name,spec in dataset.items():
            q=spec['Qnb']; ngen=int(spec.get('Gen',1))
            Y=Fraction(str(q['U1Y']))
            d2=int(q.get('SU2L',1)); d3=int(q.get('SU3C',1))
            out[0]+=prefac*ngen*d2*d3*Y*Y
            out[1]+=prefac*ngen*d3*group_index(d2)
            out[2]+=prefac*ngen*d2*colour_index(d3)
    return tuple(out)


def preflight(model:Path)->dict:
    text=model.read_text(encoding='utf-8')
    if any(x in text for x in ('l6 : 0','l7 : 0','l6: 0','l7: 0',
                                'sqrt(5/3)','epsd: 0','epse: 0')):
        raise ValueError('Forbidden Type-II / Z2 / GUT substitution')
    ferm=yaml.safe_load('Fermions: '+block(text,'Fermions'))['Fermions']
    sc=yaml.safe_load('ComplexScalars: '+block(text,'ComplexScalars'))['ComplexScalars']
    if set(sc)!={'Phi1','Phi2','chi'}:raise ValueError('Wrong scalar field inventory')
    if set(ferm)!={'QL','LL','uR','dR','eR'}:raise ValueError('Wrong fermion field inventory')
    if not all(s.get('Gen')==3 for s in ferm.values()):raise ValueError('Wrong generations')
    if (sc['Phi1']['Qnb']['U1Y'],sc['Phi2']['Qnb']['U1Y'],sc['chi']['Qnb']['U1Y'])!=('1/2','1/2',1):
        raise ValueError('Wrong hypercharges')
    values={}
    for sect,expected in EXPECTED.items():
        terms=declared_terms(block(text,sect))
        if set(terms)!=expected:
            raise ValueError(f'{sect}: missing={expected-set(terms)} extra={set(terms)-expected}')
        nfields={'Yukawas':3,'QuarticTerms':4,'TrilinearTerms':3,'ScalarMasses':2}[sect]
        for key,expr in terms.items():
            flds=TOKEN_RE.findall(expr)
            if len(flds)!=nfields:
                raise ValueError(f'{sect}:{key} has {len(flds)} fields, expected {nfields}: {expr}')
            y=sum((FIELD_Y[f] for f in flds),Fraction(0))
            if y!=0:raise ValueError(f'{sect}:{key} has nonzero Y={y}')
        values[sect]=sorted(terms)
    fexpr=declared_terms(block(text,'Yukawas'))['f']
    if (fexpr.count('LL[')!=2 or not fexpr.count('chi')==1
        or 'Eps[i,j]' not in fexpr or fexpr.count('LL[i]')!=1 or fexpr.count('LL[j]')!=1):
        raise ValueError('Zee f operator is missing expected antisymmetric SU2 tensor')
    trilinear=declared_terms(block(text,'TrilinearTerms'))['muZee']
    if 'Eps[i,j]' not in trilinear or not all(z in trilinear for z in ('Phi1[i]','Phi2[j]','chibar')):
        raise ValueError('Zee trilinear missing SU2 epsilon/charged singlet')
    sub=declared_terms(block(text,'Substitutions'))
    if sub!={'g_U1Y':'gp','g_SU2L':'g2','g_SU3C':'g3'}:
        raise ValueError('Generator gauge-coupling substitutions changed')
    b=gauge_from_content(ferm,sc)
    if b!=(Fraction(22,3),Fraction(-3),Fraction(-7)):
        raise ValueError(f'Incorrect Zee gauge b coefficients {b}')
    return {'input_SHA256':sha256(model),'gauge_1loop_SM_gprime':[str(z) for z in b],
            'field_content_real_scalar_dof':10,
            'operators':values,'couplings_quartic_real_components':15,
            'f_tensor_antisymmetry_generator_verified':False,
            'scalar_hc_generation_verified':False,
            'full_complex_beta_functions_verified':False}


PYRATE_DEPENDENCIES=('yaml','sympy','numpy','scipy','h5py','matplotlib')


def dependency_manifest(modules=PYRATE_DEPENDENCIES)->dict[str,dict[str,str]]:
    """Locate PyR@TE requirements using the SAME parent interpreter.

    The AF's parent Python can import yaml; -I suppresses some module roots.
    Explicitly restore package roots *after* the pinned PyR@TE source paths,
    rather than inheriting unrestricted PYTHONPATH from Key4hep.
    """
    out={}
    for name in modules:
        spec=importlib.util.find_spec(name)
        if spec is None or not spec.origin:
            raise RuntimeError(
                f"Missing PyR@TE dependency {name!r} in parent Python "
                f"{sys.executable}; use a Python environment containing it.")
        origin=Path(spec.origin).resolve()
        if spec.submodule_search_locations is not None:
            locs=list(spec.submodule_search_locations)
            if len(locs)!=1:
                raise RuntimeError(f"Ambiguous package location for {name}: {locs}")
            root=Path(locs[0]).resolve().parent
        else:
            root=origin.parent
        if not root.is_dir() or not origin.is_file():
            raise RuntimeError(f"Unusable Python dependency {name}: {origin}")
        out[name]={'origin':str(origin),'search_root':str(root)}
    return out


def external_python_roots(paths=None)->list[str]:
    """Restore parent search roots for transitive scientific dependencies.

    PyR@TE source always remains ahead of these paths. Reject blank/current
    working directory entries and paths containing an unrelated Particles.py
    to prevent the original Key4hep collision from reappearing.
    """
    if paths is None:
        paths=sys.path
    out=[]
    for value in paths:
        if not value or not Path(value).is_absolute():
            continue
        path=Path(value).resolve()
        if not path.is_dir() or (path/'Particles.py').is_file():
            continue
        if str(path) not in out:
            out.append(str(path))
    return out


def isolated_pyrate_command(source:Path,entry:Path,model:Path,target:Path,
                            dependencies:dict|None=None,
                            extra_roots:list[str]|None=None)->list[str]:
    """Run UNMODIFIED PyR@TE under -I, with source first and dependencies second.

    The pinned PyR@TE Core must win over Key4hep's identically named
    Particles.py. Resolve required third-party import roots in the parent,
    then pass them explicitly instead of allowing arbitrary PYTHONPATH.
    """
    if dependencies is None:
        dependencies=dependency_manifest()
    if extra_roots is None:
        extra_roots=external_python_roots()
    bootstrap="""
import importlib.util
import json
import runpy
import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
deps = json.loads(sys.argv[2])
extra_roots = json.loads(sys.argv[3])
internal = [root/'src'/name for name in ('Core','IO','PyLie','GroupTheory')]
dep_roots = list(dict.fromkeys(info['search_root'] for info in deps.values()))
sys.path[:0] = ([str(item) for item in internal] +
                [str(root/'src')] + dep_roots + extra_roots)

internal_particles = (root/'src/Core/Particles.py').resolve()
spec = importlib.util.find_spec('Particles')
origin = Path(spec.origin).resolve() if spec and spec.origin else None
if origin != internal_particles:
    raise RuntimeError(
        f'PyR@TE Particles import collision: {origin} != {internal_particles}')

for name, info in deps.items():
    found = importlib.util.find_spec(name)
    actual = Path(found.origin).resolve() if found and found.origin else None
    expected = Path(info['origin']).resolve()
    if actual != expected:
        raise RuntimeError(
            f'PyR@TE dependency {name} import mismatch: {actual} != {expected}')
    try:
        imported = __import__(name)
        reported_version = getattr(imported, '__version__', None)
        if reported_version is None:
            raise RuntimeError(f'{name} has no importable package version')
    except Exception as exc:
        raise RuntimeError(
            f'PyR@TE dependency {name} failed to import from {actual}: '
            f'{type(exc).__name__}: {exc}') from exc
print('Q4_IMPORT_PROVENANCE',
      json.dumps({'Particles':str(origin),
                  'dependencies':{key:value['origin'] for key,value in deps.items()}},
                 sort_keys=True),flush=True)
sys.argv = [str(root/'pyR@TE.py'), *sys.argv[4:]]
runpy.run_path(sys.argv[0], run_name='__main__')
"""
    return [
        sys.executable,'-I','-c',bootstrap,str(source),
        json.dumps(dependencies,sort_keys=True),json.dumps(extra_roots),
        '--Model',str(model),'--Loops','1',
        '--Results',str(target),'--CheckGaugeInvariance','--PythonOutput',
        '--no-LatexOutput','--no-MathematicaOutput'
    ]


def isolated_environment()->dict[str,str]:
    """Only remove Python import contamination, leave native library env alone."""
    env=os.environ.copy()
    for key in ('PYTHONPATH','PYTHONHOME','PYTHONSTARTUP'):
        env.pop(key,None)
    return env


def execute(model:Path,output:Path,pyrate_root:Path|None,timeout:int)->dict:
    source=pyrate_root.resolve() if pyrate_root else output/'pyrate3_src'
    if pyrate_root is None:
        source.mkdir()
        cmd=['git','-C',str(source),'init','-q']
        subprocess.run(cmd,check=True,timeout=60)
        subprocess.run(['git','-C',str(source),'remote','add','origin',PYRATE_REMOTE],check=True,timeout=15)
        fetch=subprocess.run(['git','-C',str(source),'fetch','--depth','1','origin',PYRATE_SHA],
                             stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=120)
        (output/'pyrate3_git_fetch.log').write_text(fetch.stdout+fetch.stderr)
        if fetch.returncode!=0:
            raise RuntimeError('Pinned PyR@TE fetch failed; inspect pyrate3_git_fetch.log')
        subprocess.run(['git','-C',str(source),'checkout','-q','FETCH_HEAD'],check=True,timeout=30)
    head=subprocess.run(['git','-C',str(source),'rev-parse','HEAD'],capture_output=True,
                        text=True,check=True,timeout=10).stdout.strip()
    if head!=PYRATE_SHA:raise ValueError(f'Unpinned PyR@TE revision {head}, require {PYRATE_SHA}')
    entry=source/'pyR@TE.py'
    if not entry.is_file():raise ValueError(f'Missing PyR@TE entrypoint at {entry}')
    target=output/'generator_output'
    target.mkdir()
    dependencies=dependency_manifest()
    (output/'pyrate3_python_dependency_provenance.json').write_text(
        json.dumps(dependencies,indent=2,sort_keys=True)+'\n')
    restored_roots=external_python_roots()
    (output/'pyrate3_transitive_import_roots.json').write_text(
        json.dumps(restored_roots,indent=2)+'\\n')
    cmd=isolated_pyrate_command(source,entry,model,target,dependencies,
                                extra_roots=restored_roots)
    env=isolated_environment()
    generator_started=time.time()
    done=subprocess.run(cmd,cwd=source,capture_output=True,text=True,
                        timeout=timeout,env=env)
    (output/'pyrate3_stdout.log').write_text(done.stdout)
    (output/'pyrate3_stderr.log').write_text(done.stderr)
    files=[str(p.relative_to(target)) for p in target.rglob('*') if p.is_file()]
    recent_logs=[]
    logdir=source/'log'
    if logdir.is_dir():
        for item in sorted(logdir.glob('PyLog*.log')):
            if item.is_file() and item.stat().st_mtime >= generator_started-2:
                copied=output/('upstream_'+item.name)
                copied.write_bytes(item.read_bytes())
                recent_logs.append({
                    'source':str(item),'copy':str(copied),
                    'tail':'\n'.join(item.read_text(errors='replace').splitlines()[-70:])[-16000:]
                })
    diagnostic={
        'stage':'pyrate3_subprocess',
        'command':cmd,
        'returncode':done.returncode,
        'python_executable':sys.executable,
        'python_version':sys.version,
        'isolated_python_flag':True,
        'PYTHONPATH_PYTHONHOME_PYTHONSTARTUP_removed':True,
        'pyrate_source_imports_prepend':True,
        'third_party_import_locations_allowlisted':True,
        'parent_transitive_dependency_roots_restored':len(restored_roots),
        'generated_file_count':len(files),
        'no_files_despite_zero_returncode':bool(done.returncode==0 and not files),
        'upstream_logs_from_this_run':recent_logs,
        'stdout_last_70_lines':'\n'.join(done.stdout.splitlines()[-70:])[-16000:],
        'stderr_last_70_lines':'\n'.join(done.stderr.splitlines()[-70:])[-16000:],
    }
    (output/'pyrate3_diagnostic.json').write_text(json.dumps(diagnostic,indent=2)+'\n')
    if done.returncode!=0 or not files:
        print('Q4_PYRATE_STDOUT_TAIL_BEGIN\n'+diagnostic['stdout_last_70_lines']+
              '\nQ4_PYRATE_STDOUT_TAIL_END',file=sys.stderr,flush=True)
        print('Q4_PYRATE_STDERR_TAIL_BEGIN\n'+diagnostic['stderr_last_70_lines']+
              '\nQ4_PYRATE_STDERR_TAIL_END',file=sys.stderr,flush=True)
        for log in recent_logs:
            print('Q4_PYRATE_UPSTREAM_LOG '+log['copy']+'\n'+log['tail'],
                  file=sys.stderr,flush=True)
    result={'pyrate_SHA':head,'command':cmd,'returncode':done.returncode,
            'generated_files':files,'generator_executed_successfully':done.returncode==0,
            'physics_source_limit_crosschecked':False,
            'independent_RGBeta_comparison_passed':False}
    if done.returncode!=0:raise RuntimeError(f'PyR@TE exit={done.returncode}; see stdout/stderr logs')
    if not files:
        raise RuntimeError(
            'PyR@TE exited with code 0 but produced no files. '
            'Upstream PyR@TE sometimes uses exit() without nonzero status '
            'after reporting an error. Inspect captured stdout/stderr and recent logs.')
    return result


def main()->int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--model',type=Path,default=MODEL)
    p.add_argument('--output-dir',type=Path,required=True)
    p.add_argument('--pyrate-root',type=Path,help='Already installed official PyR@TE checkout, pinned SHA required')
    p.add_argument('--preflight-only',action='store_true')
    p.add_argument('--timeout-seconds',type=int,default=1800)
    args=p.parse_args()
    output=args.output_dir.resolve()
    if output.exists():p.error('Refusing to overwrite output directory')
    if not args.model.is_file():p.error('Missing model '+str(args.model))
    output.mkdir(parents=True)
    summary={'status':STATUS,'result':'FAIL_CLOSED',
             'full_Zee_RGE_calculation_accepted':False,'allowed_Zee_point':None,
             'PyRATE3_source_sha_expected':PYRATE_SHA,
             'started_epoch':time.time()}
    try:
        if not args.preflight_only:
            tests=subprocess.run([sys.executable,'-m','unittest','discover',
                '-s','tests','-p','test_zee_section8_Q4_pyrate_generator_gate.py','-v'],
                cwd=ROOT,capture_output=True,text=True,timeout=120)
            (output/'q4_unit_tests.log').write_text(tests.stdout+tests.stderr)
            summary['q4_unit_tests_pass']=(tests.returncode==0 and
                'Ran 22 tests' in tests.stderr and
                '\nOK' in tests.stderr)
            if not summary['q4_unit_tests_pass']:
                raise RuntimeError('Q4 input contract unit tests failed: see q4_unit_tests.log')
            print('Q4_SOURCE_INPUT_CONTRACT_TESTS_PASS 22',flush=True)
        summary['preflight']=preflight(args.model)
        summary['preflight_pass']=True
        print('Q4_PREFLIGHT_PASS True',flush=True)
        print('Q4_GAUGE_1LOOP_B',summary['preflight']['gauge_1loop_SM_gprime'],flush=True)
        if args.preflight_only:
            summary['result']='PREFLIGHT_ONLY_GENERATOR_NOT_EXECUTED'
        else:
            summary['generator']=execute(args.model.resolve(),output,args.pyrate_root,args.timeout_seconds)
            summary['result']='GENERATOR_EXECUTED_BUT_COMPLEX_BETAS_UNVALIDATED'
        print('Q4_FULL_ZEE_BETAS_INDEPENDENTLY_VALIDATED False',flush=True)
        return 0
    except Exception as exc:
        diagnostic_file=output/'pyrate3_diagnostic.json'
        if diagnostic_file.is_file():
            summary['generator_failure_diagnostic']=json.loads(diagnostic_file.read_text())
        summary['error']=repr(exc);summary['traceback']=traceback.format_exc()
        print('Q4_FAIL_CLOSED',repr(exc),file=sys.stderr,flush=True)
        return 1
    finally:
        summary['finished_epoch']=time.time()
        (output/'summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
        print('SUMMARY',output/'summary.json',flush=True)


if __name__=='__main__':raise SystemExit(main())
