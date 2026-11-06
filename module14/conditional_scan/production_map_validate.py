"""Independent D14D native validation; original D14C validation stays unchanged."""
import math
from pathlib import Path
import re
import sys

from module8.real_run_validation import lha_values, run_settings, validate_settings
from module8.run_capture import set_card
from module14.scan import digest, file_sha
from .candidate_export import ROOT, require
from .production_map_run import LOCAL, WORK, PROCESS, load
from .targeted_validation import within, expected_parameters


def validate_run_card(raw, mass, energy):
    s = run_settings(raw)
    for key, want in {'ebeam1': energy*500., 'ebeam2': energy*500.,
                      'scale': mass, 'dsqrt_q2fact1': mass, 'dsqrt_q2fact2': mass}.items():
        require(float(s[key]) == want, 'D14D run setting mismatch: '+key)
    validate_settings(set_card(raw, {'ebeam1': 6800., 'ebeam2': 6800., 'scale': 700.,
                                    'dsqrt_q2fact1': 700., 'dsqrt_q2fact2': 700.}))
    return s


def validate_one(point_id, energy, rows):
    folder = WORK/f'{point_id}_{energy}TeV'; receipt_dir = WORK/f'receipt_{point_id}_{energy}TeV'
    receipt_path = receipt_dir/'receipt.json'; r = load(receipt_path)
    require(r['schema'] == 'd14d-native-execution-1' and r['id'] == point_id and r['energy_TeV'] == energy and r['returncode'] == 0,
            'Unsuccessful native execution')
    require(r['command'] == [sys.executable, str(folder/'bin/generate_events'), 'd14d', '-f'],
            'Unexpected native command')
    for name, want in r['source_sha256'].items():
        require(file_sha(ROOT/name) == want, 'Executed source changed: '+name)
    for name, want in r['input_sha256'].items():
        require(file_sha(within(LOCAL, name)) == want, 'Immutable input changed: '+name)
    for name, want in r['output_sha256'].items():
        require(file_sha(within(LOCAL, name)) == want, 'Native output changed: '+name)
    for name, want in r['artifacts_sha256'].items():
        require(file_sha(within(receipt_dir, name)) == want, 'Captured artifact changed: '+name)
    snapshots = r['compiled_source_snapshot_sha256']
    require(bool(snapshots), 'Missing compiled-source snapshots')
    for name, want in snapshots.items():
        require(file_sha(within(receipt_dir/'compiled_sources', name)) == want,
                'Compiled source snapshot changed: '+name)
        if Path(name).name == 'vector.inc':
            require((receipt_dir/'compiled_sources'/name).read_text().split() ==
                    ['INTEGER', 'WARP_SIZE', 'PARAMETER', '(WARP_SIZE=1)', 'INTEGER', 'NB_WARP',
                     'PARAMETER', '(NB_WARP=1)', 'INTEGER', 'VECSIZE_MEMMAX', 'PARAMETER', '(VECSIZE_MEMMAX=1)'],
                    'Unexpected compiled vector configuration')
    sources = load(receipt_dir/'sources.json')
    for part, entries in sources.items():
        require(part in ('Source', 'SubProcesses') and bool(entries), 'Missing source manifest')
        for name, want in entries.items():
            if Path(name).suffix not in ('.py', '.f', '.f90', '.inc', '.cc', '.h'):
                continue
            full = part+'/'+name
            require(full in snapshots, 'Incomplete compiled source capture')
            if Path(name).name not in ('run_card.inc', 'param_card.inc', 'vector.inc') and not name.endswith('_optim.f'):
                require(snapshots[full] == want and file_sha(within(folder/part, name)) == want,
                        'Original generated source changed: '+full)
    proc = (receipt_dir/'proc_card_mg5.dat').read_text().replace('\\\n', '')
    require([s.strip() for s in proc.splitlines() if s.startswith(('generate ', 'add process '))] == PROCESS,
            'Charge/beam/order definition mismatch')
    banners = [within(LOCAL, n) for n in r['output_sha256'] if n.endswith('_banner.txt')]
    require(len(banners) == 1, 'Need exactly one native banner')
    banner = banners[0].read_text()

    def tag(name):
        match = re.search('<'+name+'>(.*?)</'+name+'>', banner, re.S)
        require(match is not None, 'Missing native banner tag: '+name)
        return match[1].replace('<![CDATA[', '').replace(']]>', '').strip()

    require(tag('MGVersion') == '#3.6.7' and tag('MG5ProcCard').replace('\\\n', '') == proc.strip(),
            'Actual generator/process mismatch')
    row = next(row for row in rows if row['neutrino']['ordering'] == 'NO' and row['neutrino']['family'] == 0)
    mass = row['input_card']['physical']['mH2']
    require(r['muR_GeV'] == r['muF_GeV'] == mass, 'Receipt scale mismatch')
    active = validate_run_card(tag('MGRunCard'), mass, energy)
    original = validate_run_card((receipt_dir/'run_card.dat').read_text(), mass, energy)
    normalized = validate_run_card((receipt_dir/'normalized_run_card.dat').read_text(), mass, energy)
    require(active['iseed'] == original['iseed'] == '4154' and normalized['iseed'] == '0',
            'Run seed provenance mismatch')
    normalized['iseed'] = '4154'
    require(normalized == active, 'Banner/normalized run card mismatch')
    parameters = lha_values(tag('slha'))
    require(parameters == expected_parameters(row) == lha_values((receipt_dir/'param_card.dat').read_text())
            == lha_values((receipt_dir/'normalized_param_card.dat').read_text()), 'Full LHA point mismatch')
    data = [float(x.replace('D', 'e')) for x in (receipt_dir/'results.dat').read_text().splitlines()[0].split()]
    sigma, error, samples = data[9], math.hypot(data[1], data[2]), data[3]
    require(all(math.isfinite(x) for x in data) and sigma > 0 and 0 < error/sigma < .01 and samples >= 5000,
            'Invalid native integration statistics')
    match = re.search(r'Integrated weight \(pb\)\s*:\s*(\S+)', tag('MGGenerationInfo'))
    require(match is not None and abs(float(match[1])/sigma-1) < 2e-4, 'Native banner rate mismatch')
    log = (receipt_dir/'execution.log').read_text()
    match = re.search(r'Cross-section\s*:\s*([\deE.+-]+)\s*\+-\s*([\deE.+-]+)\s*pb', log)
    require(match is not None and abs(float(match[1])/sigma-1) < .001 and abs(float(match[2])/error-1) < .001,
            'Native log rate/error mismatch')
    require('interrupted with error' not in log and 'Traceback' not in log, 'Native execution error')
    return {'id': point_id, 'status': 'D14D_NATIVE_RUN_PASS', 'sigma_pb': sigma,
            'integration_error_pb': error, 'integration_samples': int(samples), 'energy_TeV': energy,
            'process': 'pp_tbH2_5FS_gb', 'charge_definition': 'H2minus_and_H2plus_both_beam_orders_once',
            'order': 'LO_QCD', 'pdf': 'NNPDF30_lo_as_0130_member0_ID263000',
            'scale_scheme': 'fixed_muR_muF_mH2_Yukawas_D4_running_at_mH2',
            'muR_GeV': mass, 'muF_GeV': mass, 'scale_sensitivity': 'NOT_EVALUATED',
            'pdf_uncertainty': 'UNKNOWN', 'theory_sigma_pb': None,
            'receipt_path': str(receipt_path.relative_to(LOCAL)), 'receipt_sha256': file_sha(receipt_path),
            'results_sha256': file_sha(receipt_dir/'results.dat'), 'banner_sha256': file_sha(banners[0]),
            'execution_log_sha256': file_sha(receipt_dir/'execution.log'),
            'input_sha256': r['input_sha256'], 'source_sha256': r['source_sha256'],
            'compiled_source_snapshot_count': len(snapshots), 'compiled_source_tree_sha256': digest(snapshots)}
