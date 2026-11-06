"""Isolated 13-TeV D14C LO 5FS probes, using frozen D5/D6 machinery.

No scan submission; exactly three permitted scalar identities. Native artifacts
stay ignored in validation/module8/local/d14c. Each action is a fresh process.
"""
import argparse
import cmath
import importlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile
import time

from module7.d4_inputs import native_card, yukawa_masses, ckm
from module8.run_capture import set_card, tree_digest
from module8.real_run_validation import EXPECTED, lha_values, run_settings, validate_settings
from module8.ufo_audit import external_values, evaluate_parameters, write_card, read_card
from module14.scan import digest, file_sha
from .candidate_export import ROOT, BASE, CERTIFIED, PRODUCTION_IDS, require
from .workflow import load, production

LOCAL = ROOT/'validation/module8/local'
WORK = LOCAL/'d14c'
MG = LOCAL/'MG5_aMC_v3_6_7'
UFO = LOCAL/'native/sarah/ZeeTypeII/EWSB/UFO'
PROCESS = EXPECTED['P2']


def save(path, data):
    path.write_text(json.dumps(data, sort_keys=True, indent=2, allow_nan=False)+'\n')


def runtime_gate():
    d5 = load(ROOT/'validation/module8/d5_production.json')
    for name, want in d5['native_model']['ufo_sha256'].items():
        require(file_sha(UFO/name) == want, 'Frozen UFO changed: '+name)
    for name, want in d5['native_model']['source_sha256'].items():
        require(file_sha(ROOT/name) == want, 'Frozen mapping changed: '+name)
    require(file_sha(LOCAL/'MG5_release_v3.6.7.tar.gz') ==
            d5['real_execution_validation']['official_release_archive_sha256'], 'Official archive changed')
    require(file_sha(LOCAL/'LHAPDF-6.5.6.tar.gz') ==
            d5['runtime']['LHAPDF_source_archive_sha256'], 'LHAPDF source archive changed')
    libkey = 'validation/module8/local/lhapdf/lib/libLHAPDF.so'
    require(file_sha(ROOT/libkey) == d5['independent_Z_convolution']['source_sha256'][libkey],
            'Frozen LHAPDF library changed')
    for name, want in d5['spectra'][0]['P1']['input_sha256'].items():
        if name.startswith('pdf/'):
            require(file_sha(LOCAL/name) == want, 'Frozen PDF changed')
    compared = 0
    with tarfile.open(LOCAL/'MG5_release_v3.6.7.tar.gz') as archive:
        for member in archive.getmembers():
            rel = Path(*Path(member.name).parts[1:])
            if not member.isfile() or not rel.parts:
                continue
            if str(rel) == 'bin/mg5_aMC' or (rel.suffix in ('.py', '.f', '.f90', '.inc', '.cc', '.h')
                    and rel.parts[0] in ('madgraph', 'aloha', 'models', 'Template')):
                require((MG/rel).read_bytes() == archive.extractfile(member).read(),
                        'Official MG source mismatch: '+str(rel))
                compared += str(rel) != 'bin/mg5_aMC'
    require(compared == 827, 'Incomplete official MG comparison')
    return {'official_source_files_compared': compared, 'differences': [],
            'MG_version': (MG/'VERSION').read_text().strip(),
            'ufo_sha256': d5['native_model']['ufo_sha256'],
            'PDF': 'NNPDF30_lo_as_0130 member 0 ID 263000',
            'd5_evidence_sha256': file_sha(ROOT/'validation/module8/d5_production.json'),
            'library_sha256': file_sha(ROOT/libkey),
            'archive_sha256': file_sha(LOCAL/'MG5_release_v3.6.7.tar.gz')}


def stage(source):
    require(not LOCAL.exists(), 'Refuse existing local workspace; preserve previous artifacts')
    LOCAL.mkdir(parents=True)
    for name in ('MG5_aMC_v3_6_7', 'lhapdf', 'native', 'pdf'):
        shutil.copytree(source/name, LOCAL/name, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '*.pkl'))
    for name in ('MG5_release_v3.6.7.tar.gz', 'LHAPDF-6.5.6.tar.gz'):
        shutil.copyfile(source/name, LOCAL/name)
    config = LOCAL/'lhapdf/bin/lhapdf-config'
    before = file_sha(config)
    config.write_text(config.read_text().replace(str(source/'lhapdf'), str(LOCAL/'lhapdf')))
    WORK.mkdir()
    report = runtime_gate()
    report.update(source_local=str(source), lhapdf_config_before_sha256=before,
                  lhapdf_config_after_sha256=file_sha(config),
                  relocation='Only copied lhapdf-config absolute prefix changed; library/source/UFO/PDF unchanged')
    save(WORK/'runtime.json', report)
    print('D14C_RUNTIME_SOURCE_PASS', flush=True)


def selected_rows(dataset, point_id):
    require(point_id in PRODUCTION_IDS, 'Only predeclared production probes are permitted')
    summary = load(BASE/'remote_conditional_summary.json')
    require(file_sha(dataset) == summary['dataset_sha256'], 'Dataset hash mismatch')
    rows = [r for r in load(dataset)['rows'] if r['id'] == point_id]
    require(len(rows) == 4 and len({(r['neutrino']['ordering'], r['neutrino']['family']) for r in rows}) == 4,
            'Four unique families required')
    for row in rows:
        require(row['input_card'] == summary['points'][str(point_id)]['input_card'] and
                digest(row['input_card']) == row['scalar_sha256'], 'Point identity mismatch')
    return rows


def map_cards(dataset):
    runtime_gate()
    output = WORK/'cards'
    output.mkdir(exist_ok=False)
    sys.path.insert(0, str(UFO))
    for name in ('parameters', 'particles', 'couplings', 'lorentz', 'vertices'):
        importlib.import_module(name)
    objects = importlib.import_module('object_library')
    f = importlib.import_module('function_library')
    functions = {n: getattr(f, n) for n in ('complexconjugate', 're', 'im', 'csc', 'sec', 'acsc', 'asec')}
    functions.update(cmath=cmath, complex=complex)
    results = []
    for point_id in PRODUCTION_IDS:
        for row in selected_rows(dataset, point_id):
            n, x = row['neutrino'], row['input_card']['physical']
            card = native_card(x, n, x['mH2'], f'd14c_{point_id}_{n["ordering"]}_{n["family"]}')
            values, closure = external_values(objects.all_parameters, card)
            path = output/(card['id']+'.dat')
            write_card(path, objects.all_parameters, values)
            require(values == read_card(path, objects.all_parameters), 'LHA roundtrip failed')
            env = evaluate_parameters(objects.all_parameters, values, functions)
            cv = {a.name: complex(eval(a.value, {'__builtins__': {}}, env)) for a in objects.all_couplings}
            require(all(math.isfinite(abs(z)) for z in cv.values()), 'Nonfinite native coupling')
            # The actual frozen UFO FFS (2,1) chain reverses projectors, as in D5.
            m = yukawa_masses(x['mH2']); d = -math.sin(x['gamma']); vtb = ckm()[2, 2]
            a = math.sqrt(2)*m[2]*d*vtb/(x['v']*math.tan(x['beta']))
            b = math.sqrt(2)*m[5]*d*vtb*math.tan(x['beta'])/x['v']
            residuals = []
            for ids, wp, wm in [((-6, 5, -9000037), 1j*a, 1j*b),
                               ((-5, 6, 9000037), 1j*b.conjugate(), 1j*a.conjugate())]:
                vertex = next(z for z in objects.all_vertices if tuple(p.pdg_code for p in z.particles) == ids)
                require(vertex.color == ['Identity(1,2)'], 'Unexpected tb vertex color')
                for structure, want in [('ProjP(2,1)', wp), ('ProjM(2,1)', wm)]:
                    got = sum(cv[c.name] for (ci, li), c in vertex.couplings.items()
                              if ci == 0 and vertex.lorentz[li].structure == structure)
                    residuals.append(abs(got-want))
            require(max(residuals) < 2e-10, 'Signed tb UFO coefficient mismatch')
            raw = path.read_text()
            # Independent Yukawa blocks stay at Q=mH2. These edits only affect
            # hard-process kinematics, never reconstruct couplings from a mass edit.
            raw = re.sub(r'(?m)^DECAY 6 .*$', 'DECAY 6 0.0 # stable top', raw)
            lines = []; in_mass = False
            for line in raw.splitlines():
                cols = line.split('#')[0].split()
                if cols and cols[0].upper() == 'BLOCK':
                    in_mass = cols[1].upper() == 'MASS'
                if cols and cols[0].upper() == 'DECAY':
                    in_mass = False
                if in_mass and cols and cols[0].isdigit() and int(cols[0]) in range(1, 6):
                    line = f' {cols[0]} 0.0 # massless hard 5FS; independent Yukawa'
                lines.append(line)
                if cols and cols[:2] == ['BLOCK', 'MASS']:
                    lines.append(' 24 80.379 # dependent MWm')
            path.write_text('\n'.join(lines)+'\n')
            save(output/(card['id']+'.json'), card)
            results.append({'id': point_id, 'ordering': n['ordering'], 'family': n['family'],
                'scalar_sha256': row['scalar_sha256'], 'module2_input_sha256': n['input_sha256'],
                'yukawa_sha256': {k: digest(n[k]) for k in ('F', 'D', 'Ye', 'Ye2')},
                'card': str(path.relative_to(LOCAL)), 'card_sha256': file_sha(path),
                'native_input_sha256': file_sha(path.with_suffix('.json')), 'closure': closure,
                'signed_tb_coefficient_max_residual': max(residuals),
                'quark_Yukawa_masses_GeV': m, 'Q_Yukawa_GeV': x['mH2']})
    save(WORK/'mapping.json', {'status': 'D14C_NATIVE_CARD_MAPPING_PASS', 'cases': results,
                              'source_sha256': source_hashes()})
    print('D14C_NATIVE_CARD_MAPPING_PASS', len(results), flush=True)


def source_hashes():
    names = ('module14/conditional_scan/targeted_production.py', 'module8/ufo_audit.py',
             'module8/mg_matrix_checks.py', 'module8/real_run_validation.py', 'module8/run_capture.py',
             'module7/d4_inputs.py', 'module1/scalar_constraints.py')
    return {name: file_sha(ROOT/name) for name in names}


def matrix_checks():
    """Actual ALOHA vs unchanged independent D5 Dirac trace, at each new card."""
    runtime_gate()
    sys.path.insert(0, str(MG))
    cwd = Path.cwd()
    try:
        from module8.mg_matrix_checks import independent_gb_trace, momenta
    finally:
        os.chdir(cwd)
    from madgraph.interface.master_interface import MasterCmd
    from madgraph.core.helas_objects import HelasMatrixElement
    from madgraph.various.process_checks import MatrixElementEvaluator
    from models.check_param_card import ParamCard
    cmd = MasterCmd()
    cmd.exec_cmd('set auto_update 0')
    cmd.exec_cmd('import model '+str(UFO)+' -modelname')
    matrices = {}
    for name, process in [('minus', 'g d3 > u3 hm3 QCD=1 QED=1'),
                          ('plus', 'g d3bar > u3bar hm3c QCD=1 QED=1')]:
        cmd.exec_cmd('generate '+process)
        matrices[name] = HelasMatrixElement(cmd._curr_amps[0])
    results = []
    for case in load(WORK/'mapping.json')['cases']:
        cardpath = LOCAL/case['card']
        native = load(cardpath.with_suffix('.json')); x = native['physical']
        p = momenta(3*x['mH2'], 172.4, x['mH2'], .23)
        baseline = None
        for gamma in (x['gamma'], 0., math.pi/2, -math.pi/2, -x['gamma']):
            card = ParamCard(str(cardpath)); beta = x['beta']
            cb, sb, cg, sg = math.cos(beta), math.sin(beta), math.cos(gamma), math.sin(gamma)
            zp = [[cb, sb, 0], [-sb*cg, cb*cg, sg], [sb*sg, -cb*sg, cg]]
            for i in range(3):
                for j in range(3):
                    card['chargemix'].get((i+1, j+1)).value = zp[i][j]
            control = WORK/'matrix_control.dat'; card.write(str(control), precision=17)
            evaluator = MatrixElementEvaluator(cmd._curr_model, param_card=str(control), reuse=False, cmd=cmd)
            rates = {name: evaluator.evaluate_matrix_element(matrix, p=p)[0] for name, matrix in matrices.items()}
            if baseline is None:
                baseline = rates['minus']
            m = case['quark_Yukawa_masses_GeV']; d = -math.sin(gamma); vtb = ckm()[2, 2]
            a = math.sqrt(2)*m[2]*d*vtb/(x['v']*math.tan(beta))
            b = math.sqrt(2)*m[5]*d*vtb*math.tan(beta)/x['v']
            trace, ward = independent_gb_trace(p, a, b, math.sqrt(4*math.pi*.118), 172.4)
            scale = (math.sin(gamma)/math.sin(x['gamma']))**2
            require(max(abs(value-trace) for value in rates.values())/baseline < 1e-10,
                    'Independent trace/charge check failed')
            require(abs(rates['minus']/baseline-scale) < 1e-10 and ward < 1e-6,
                    'Endpoint/sign/Ward check failed')
            results.append({'id': case['id'], 'ordering': case['ordering'], 'family': case['family'],
                'gamma_control': gamma, 'MG_m2': rates, 'independent_trace_m2': trace,
                'Ward_trace': ward, 'relative_to_original_gamma': scale})
    save(WORK/'matrix_checks.json', {'status': 'D14C_INDEPENDENT_MG_MATRIX_PASS',
        'rows': results, 'source_sha256': source_hashes(),
        'scope': 'Fixed masses and Yukawas, both charges, signed gamma and endpoints; no hadronic rescaling used'})
    print('D14C_INDEPENDENT_MG_MATRIX_PASS', len(results), flush=True)


def execute(point_id):
    runtime_gate()
    mapping = load(WORK/'mapping.json')
    require(load(WORK/'matrix_checks.json')['status'] == 'D14C_INDEPENDENT_MG_MATRIX_PASS', 'Matrix gate absent')
    require(point_id in PRODUCTION_IDS, 'Unapproved production point')
    case = next(c for c in mapping['cases'] if c['id'] == point_id and c['ordering'] == 'NO' and c['family'] == 0)
    native = load((LOCAL/case['card']).with_suffix('.json')); mass = native['physical']['mH2']
    folder = WORK/str(point_id)
    require(not folder.exists(), 'Refuse existing process output')
    commands = ['set auto_update 0', 'set automatic_html_opening False', 'set notification_center False',
        'set lhapdf '+str(LOCAL/'lhapdf/bin/lhapdf-config'), 'import model '+str(UFO)+' -modelname',
        *PROCESS, 'output '+str(folder), 'quit']
    commandfile = WORK/f'generate_{point_id}.txt'; commandfile.write_text('\n'.join(commands)+'\n')
    env = os.environ.copy()
    env.update(LHAPDF_DATA_PATH=str(LOCAL/'pdf'), LD_LIBRARY_PATH=str(LOCAL/'lhapdf/lib')+':'+env.get('LD_LIBRARY_PATH', ''),
               BROWSER='true', PYTHONDONTWRITEBYTECODE='1', OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1')
    with (WORK/f'generate_{point_id}.log').open('x') as log:
        completed = subprocess.run([sys.executable, str(MG/'bin/mg5_aMC'), str(commandfile)], cwd=WORK,
                                   env=env, stdout=log, stderr=subprocess.STDOUT)
    require(completed.returncode == 0 and folder.exists(), 'MG generation failed')
    (folder/'Cards/param_card.dat').write_bytes((LOCAL/case['card']).read_bytes())
    settings = {'lpp1': 1, 'lpp2': 1, 'ebeam1': 6500., 'ebeam2': 6500., 'nevents': 5000, 'iseed': 4154,
        'pdlabel': "'lhapdf'", 'lhaid': 263000, 'fixed_ren_scale': '.true.', 'fixed_fac_scale': '.true.',
        'scale': mass, 'dsqrt_q2fact1': mass, 'dsqrt_q2fact2': mass,
        'use_syst': 'False', 'systematics_program': "'none'", 'ptheavy': 0.}
    run_card = folder/'Cards/run_card.dat'
    raw = re.sub(r'(?m)^.*=\s*(req_acc|nocut)\b[^\n]*\n?', '', run_card.read_text())
    run_card.write_text(set_card(raw, settings))
    with (folder/'Cards/me5_configuration.txt').open('a') as f:
        f.write(f'\nlhapdf = {LOCAL}/lhapdf/bin/lhapdf-config\nnb_core = 2\nrun_mode = 0\nautomatic_html_opening = False\nnotification_center = False\n')
    receipt = WORK/f'receipt_{point_id}'; receipt.mkdir()
    for name in ('run_card.dat', 'param_card.dat', 'proc_card_mg5.dat'):
        shutil.copyfile(folder/'Cards'/name, receipt/name)
    sources = {part: tree_digest(folder/part)[1] for part in ('Source', 'SubProcesses')}
    save(receipt/'sources.json', sources)
    inputs = {str(p.relative_to(LOCAL)): file_sha(p) for p in
        (WORK/'runtime.json', WORK/'mapping.json', WORK/'matrix_checks.json', LOCAL/case['card'],
         folder/'bin/generate_events', LOCAL/'pdf/NNPDF30_lo_as_0130/NNPDF30_lo_as_0130.info',
         LOCAL/'pdf/NNPDF30_lo_as_0130/NNPDF30_lo_as_0130_0000.dat')}
    command = [sys.executable, str(folder/'bin/generate_events'), 'd14c', '-f']
    start = time.monotonic()
    with (receipt/'execution.log').open('x') as log:
        completed = subprocess.run(command, cwd=folder, env=env, stdout=log, stderr=subprocess.STDOUT)
    for name in ('run_card.dat', 'param_card.dat'):
        shutil.copyfile(folder/'Cards'/name, receipt/('normalized_'+name))
    if (folder/'SubProcesses/results.dat').exists():
        shutil.copyfile(folder/'SubProcesses/results.dat', receipt/'results.dat')
    snapshots = {}
    for part in ('Source', 'SubProcesses'):
        for p in (folder/part).rglob('*'):
            if p.is_file() and not p.is_symlink() and p.suffix in ('.py', '.f', '.f90', '.inc', '.cc', '.h'):
                name = str(p.relative_to(folder)); target = receipt/'compiled_sources'/name
                target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(p, target)
                snapshots[name] = file_sha(target)
    outputs = {str(p.relative_to(LOCAL)): file_sha(p) for base in
               (folder/'Events/d14c', folder/'HTML/d14c') for p in base.rglob('*') if p.is_file()}
    save(receipt/'receipt.json', {'schema': 'd14c-native-execution-1', 'id': point_id, 'returncode': completed.returncode,
        'command': command, 'elapsed_seconds': time.monotonic()-start, 'muR_GeV': mass, 'muF_GeV': mass,
        'input_sha256': inputs, 'output_sha256': outputs, 'source_sha256': source_hashes(),
        'compiled_source_snapshot_sha256': snapshots,
        'artifacts_sha256': {p.name: file_sha(p) for p in receipt.iterdir() if p.is_file()}})
    require(completed.returncode == 0, 'MG native execution failed; retain failed artifacts')
    print('EXECUTED', point_id, flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=('stage', 'map', 'matrix', 'run', 'validate'))
    p.add_argument('--source-local', type=Path)
    p.add_argument('--dataset', type=Path)
    p.add_argument('--point', type=int, choices=PRODUCTION_IDS)
    a = p.parse_args()
    if a.action == 'stage':
        stage(a.source_local.resolve())
    elif a.action == 'map':
        map_cards(a.dataset)
    elif a.action == 'matrix':
        matrix_checks()
    elif a.action == 'run':
        execute(a.point)
    else:
        from .targeted_validation import validate_all
        validate_all(a.dataset)


if __name__ == '__main__':
    main()
