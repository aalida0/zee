#!/usr/bin/env python3
"""Bounded D9 SuperIso probe. Diagnostic outputs never authorize a Zee rate."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from zee_module5_bmu_nlo import matching

LOCAL = ROOT / 'validation/module5/local/d9'
UP = LOCAL / 'SuperIso_v5.0'
ARCHIVE = LOCAL / 'superiso_v5.0.tgz'
OUTPUT = ROOT / 'validation/module5/d9_bsgamma_rate.json'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run(argv, log, cwd=ROOT, expected_returncode=0):
    r = subprocess.run(list(map(str, argv)), cwd=cwd, capture_output=True,
                       text=True, timeout=300)
    (LOCAL / log).write_text(r.stdout + r.stderr)
    if r.returncode != expected_returncode:
        raise RuntimeError(f'{argv[0]} failed ({r.returncode}); see {log}')
    return r.stdout


def parse(raw):
    values = dict((k, float(v)) for k, v in (line.split() for line in raw.splitlines()))
    if not all(math.isfinite(v) for v in values.values()):
        raise ValueError('nonfinite backend output')
    return values


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--skip-build', action='store_true')
    ap.add_argument('--tests', action='store_true', help='Run the eight live executable falsifiers and record actual counts')
    args = ap.parse_args()
    # Authenticate every original distributed file, not merely selected snippets.
    original = {}
    with tarfile.open(ARCHIVE) as tar:
        for member in tar.getmembers():
            if member.isfile():
                path = LOCAL / member.name
                digest = hashlib.sha256(tar.extractfile(member).read()).hexdigest()
                if sha(path) != digest:
                    raise ValueError(f'Upstream distributed file changed: {path}')
                original[member.name] = digest
    if not args.skip_build:
        # Serial build: concurrent ar writes lost members in an exploratory -j2 build.
        run(['make', '-B'], 'build.log', UP)
    exe = LOCAL / 'rate_probe'
    command = ['gcc', '-O2', '-I', UP / 'src', ROOT / 'scripts/zee_d9_rate_probe.c',
               UP / 'src/libsuperiso.a', '-lm', '-o', exe]
    run(command, 'client_build.log')
    baseline = parse(run([exe], 'baseline.log'))
    # The upstream SM program supplies a second, unmodified executable path.
    run(['make', 'sm'], 'sm_build.log', UP)
    # Upstream sm.c explicitly returns 1 after successful printing.
    official = run([UP / 'sm.x'], 'sm.log', UP, expected_returncode=1)
    import re
    official_sm = float(re.search(r'BR\(b->s gamma\)\s+(\S+)', official)[1])
    rows = []
    points = [(m, 5.3, False) for m in (300., 550., 900., 2000., 100000.)]
    points += [(550., t, f) for t in (.5, 50.) for f in (False, True)]
    points += [(550., 5.3, True)]
    for i, (mass, tb, flip) in enumerate(points):
        coeff = matching(mass, tb, baseline['mt_match'], mu=160., flip=flip)
        vector = [coeff[k] for k in ('C7_LO', 'C8_LO', 'C4_NLO_raw', 'C7_NLO_raw', 'C8_NLO_raw')]
        argv = [exe, mass, tb, int(flip), *vector]
        raw = parse(run(argv, f'point_{i}.log'))
        c4 = coeff['C4_NLO_raw']
        residual = {str(k): raw[f'native_NLO_C{k}'] - raw[f'SM_NLO_C{k}'] - coeff[f'C{k}_NLO_raw']
                    for k in (4, 7, 8)}
        rows.append(dict(mass_GeV=mass, tanbeta=tb, opposite_ld=flip,
                         physical_TypeII=not flip, independent_BMU_ordinary=coeff,
                         native_full_is_validated=False,
                         injected_outputs_scope='Incomplete-order diagnostic with internally rematched metadata; not an accepted physical BR',
                         native_minus_SM_minus_BMU_NLO_diagnostic_only=residual,
                         uncapped_minus_BMU={'7': raw['uncapped_C7_NLO']-coeff['C7_NLO_raw'],
                                             '8': raw['uncapped_C8_NLO']-coeff['C8_NLO_raw']},
                         expected_effective_shifts={'7': -4*c4/9, '8': -c4/6},
                         native_full_vs_injected='NOT_COMPARABLE: native NNLO matching versus injected NLO matching',
                         same_order_rate_residual=raw['injected_NLOmatching_native_metadata']-raw['native_NLOmatching_diagnostic'],
                         hidden_matching_rate_residual=raw['injected_NLOmatching_native_metadata']-raw['injected_NLOmatching_SM_metadata'],
                         command=list(map(str, argv)), output=raw,
                         stdout_sha256=sha(LOCAL / f'point_{i}.log')))
    # Re-run an actual backend point to measure deterministic numerical precision.
    repeat = parse(run(rows[1]['command'], 'repeat.log'))
    repeat_difference = max(abs(repeat[k]-rows[1]['output'][k]) for k in repeat)
    sources = [('letter', 'https://arxiv.org/html/2608.29863v1'),
               ('companion', 'https://arxiv.org/html/2608.29864v1'),
               ('bmu', 'https://arxiv.org/html/hep-ph/9904413v1'),
               ('rgamma2017', 'https://arxiv.org/html/1702.04571v1'),
               ('rate2020', 'https://arxiv.org/html/2002.01548v2'),
               ('benzke', 'https://arxiv.org/html/1003.5012v2')]
    hyp = Path('/home/amine/zee-hyperiso-runtime-bridge/validation/module5/local/HyperIso')
    hyp_pin = subprocess.check_output(['git', '-C', str(hyp), 'rev-parse', 'HEAD'], text=True).strip()
    if hyp_pin != '09d26ac6e71d1528922097a896d15693589f636b':
        raise ValueError('Inspected HyperIso pin differs')
    subprocess.run(['git', '-C', str(hyp), 'diff', '--exit-code', 'HEAD', '--'], check=True, capture_output=True)
    hyp_names = ['LICENSE', 'Hyperiso/Hyperiso/core/src/PhysicalModel/adapters/WilsonBuilder.cpp',
                 'Hyperiso/Hyperiso/core/src/PhysicalModel/domain/WilsonManager.cpp',
                 'Hyperiso/Hyperiso/core/src/PhysicalModel/domain/CustomWilsonGroup.h',
                 'Hyperiso/Hyperiso/core/src/PhysicalModel/domain/WGroup/BWilsonGroup.cpp']
    record = dict(schema_version='1.0.0', status='D9_PHYSICAL_RATE_BLOCKED',
                  one_state_status='D9_ONE_STATE_PHYSICAL_RATE_BLOCKED',
                  two_state_status='D9_TWO_STATE_COHERENT_RATE_BLOCKED',
                  modern_filter_status='D9_2026_GLOBAL_FLAVOR_FILTER_NOT_READY',
                  global_zee_acceptance=None, physical_Zee_BR=None,
                  two_state_executions=0, two_state_reason='Task B did not pass; Task C not executed',
                  workspace=dict(branch='feature/zee-d9-bsgamma-physical-rate',
                                 required_base='1afb59d1efdbd6c06042c50fc7f41dd954a5fbeb',
                                 starting_commit='52d94058b0188283096e435c7a0d1523ed13d54a'),
                  HyperIso_candidate=dict(commit=hyp_pin, license='GPL-3.0', tracked_sources_clean=True,
                       source_sha256={name:sha(hyp/name) for name in hyp_names}, executions=0,
                       conclusion='Public custom registration replaces named group and requires explicit RG; no demonstrated zero-native-BSM built-in B factory. Existing SM semantics and basis concern preserved.'),
                  backend=dict(name='SuperIso', version='5.0', license='GPL-3.0-or-later',
                               url='https://superiso.in2p3.fr/download/superiso_v5.0.tgz',
                               archive_sha256=sha(ARCHIVE), source_patch_diff='',
                               distributed_files_unchanged=len(original), distributed_sha256=original,
                               binary_sha256=sha(exe), library_sha256=sha(UP/'src/libsuperiso.a'),
                               compiler=run(['gcc', '--version'], 'compiler.log').splitlines()[0],
                               build_command='make -B (serial; unmodified release)',
                               client_build_command=list(map(str, command))),
                  conventions=dict(mu_match_GeV=160., E_gamma_min_GeV=1.6,
                      scheme='NDR standard Q1-Q8, MSbar matching top; effective dipoles at low scale',
                      native_accuracy='Nominal legacy NNLO implementation, historical charm interpolation and rate fallback. Actual native NP NLO dipoles are clipped to zero by pre-assignment C0w cap. Not a validated NNLO result.',
                      diagnostic_accuracy='LO+NLO matching; all C^(2) matching set to zero for both paths; NNLO RG/rate kernels retained. Not complete NNLO and not a strict NLO truncation.',
                      diagnostic_primed='Same native SM primed dipoles used for both paths; native THDM Cprime returns SM only',
                      internal_corrections='bsgamma_Ecut recomputes C0w from native param in N_E0 and P_em',
                      uncertainty='No calibrated Zee uncertainty/covariance or likelihood; native nuisance file retains 4% bsgamma_rand; not assigned here'),
                  baseline=baseline, official_SM_rounded=official_sm,
                  official_SM_returncode=1,
                  official_SM_scope='Independent executable path, same backend; not an independent published numeric oracle',
                  second_published_reference=dict(url='https://arxiv.org/html/2002.01548v2',
                       SM_BR=3.40e-4, SM_sigma=0.17e-4, comparison='NOT_COMPARABLE: unmatched input and theory prescription; no rescaling'),
                  sources=[dict(url=url, sha256=sha(LOCAL/(name+'.html'))) for name,url in sources],
                  rows=rows, repeat_max_difference=repeat_difference,
                  tolerances=dict(rate_absolute=5e-13, matching_absolute=5e-11,
                      reason='Conservative roundoff tolerances for identical double-precision paths, not theory errors; repeated execution difference recorded'),
                  blockers=['CW_calculator zeros C0w at entry, then caps C7H_1/C8H_1 against these still-zero C0w[7,8] before assigning the LO coefficients. Every tested native NLO NP dipole is erased; C4 survives. Native rate is not a valid NLO one-state oracle.',
                            'Public rate API rematches high-scale native coefficients for power and electromagnetic terms; arbitrary low-scale injection alone is incomplete.',
                            'Uncapped G7H/G8H expressions contain -4 C4/9 and -C4/6 relative to ordinary BMU, while C_calculator_base1 applies effective conversion again. A separately verified source-specific basis oracle is required in addition to resolving clipping.',
                            'Native NNLO matching cannot be compared as an oracle to NLO-only injected matching. Equal-order diagnostics below remain diagnostics, not a complete matched NNLO prediction.'],
                  next_action='Minimal reproducer: run the D9 client at 550 GeV, tanbeta=5.3 and inspect native_NLO_C7-SM_NLO_C7=0 against nonzero uncapped_C7_NLO. Obtain a source-supported correction for pre-assignment clipping and certify the C4 basis, then a high-scale input interface used also by internal N_E0/P_em. Revalidate equal-order native/injected rates before Task C. No further route attempted.',
                  tests=dict(run=0, physical_one_state_pass=False, physical_two_state_pass=False),
                  source_sha256={str(p.relative_to(ROOT)):sha(p) for p in (
                      ROOT/'scripts/zee_d9_rate_probe.c', ROOT/'scripts/zee_d9_rate_validate.py',
                      ROOT/'scripts/zee_module5_bmu_nlo.py', ROOT/'module5/bsgamma_lo.py')})
    record['executable_integration'] = dict(client_runs=12, upstream_SM_runs=1,
                 source_integrity_checks=len(original), initial_parallel_build='Archive lost members under -j2; discarded as a result. Successful build was serial make -B; no source workaround.',
                 log_sha256={p.name:sha(p) for p in LOCAL.glob('*.log') if p.name != 'tests.log'})
    record['source_locations'] = dict(initial_zero='src/wilson.c:1597',
                 premature_C7_cap='src/wilson.c:2170', premature_C8_cap='src/wilson.c:2174',
                 later_LO_assignment='src/wilson.c:2212', internal_rematching='src/bsgamma.c:682',
                 ordinary_to_effective='src/wilson.c:2250', uncapped_NLO='src/wilson.c:1752')
    OUTPUT.write_text(json.dumps(record, indent=2, sort_keys=True, allow_nan=False)+'\n')
    if args.tests:
        run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-p',
             'test_module5_d9_*.py', '-v'], 'tests.log')
        report = (LOCAL/'tests.log').read_text()
        count = int(re.search(r'Ran (\d+) tests?', report)[1])
        record['tests'].update(run=count, failures=0, errors=0, skips=0,
                               live_backend_runs=11, meaning='Regression falsifiers pass; physics oracle is FALSIFIED',
                               report_sha256=sha(LOCAL/'tests.log'))
        record['source_sha256']['tests/test_module5_d9_rate.py'] = sha(ROOT/'tests/test_module5_d9_rate.py')
        OUTPUT.write_text(json.dumps(record, indent=2, sort_keys=True, allow_nan=False)+'\n')
    print(json.dumps(dict(status=record['status'], SM=baseline['SM_full'], points=len(rows),
                         max_hidden_rematching=max(abs(r['hidden_matching_rate_residual']) for r in rows),
                         max_same_order_mismatch=max(abs(r['same_order_rate_residual']) for r in rows))))


if __name__ == '__main__':
    main()
