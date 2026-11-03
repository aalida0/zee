#!/usr/bin/env python3
"""Reconstruct the exact D9B source fork locally; no prior audit is overwritten.

Download official https://superiso.in2p3.fr/download/superiso_v5.0.tgz first.
python3 scripts/zee_d12_superiso.py --archive /path/to/superiso_v5.0.tgz
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import tarfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from module11.d11b_offline_fit import scalar_records
from zee_module5_bmu_nlo import matching

ROOT = Path(__file__).resolve().parents[1]
LOCAL = ROOT/'validation/module12/local/superiso'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run(command, label, cwd=ROOT):
    proc = subprocess.run(list(map(str, command)), cwd=cwd, capture_output=True, text=True, timeout=300)
    path = LOCAL/(label+'.log')
    path.write_text(proc.stdout+proc.stderr)
    if proc.returncode:
        raise RuntimeError(str(command[0])+' failed; see '+str(path))
    return proc.stdout


def parsed(command, label):
    return {k: float(v) for k, v in (s.split() for s in run(command, label).splitlines())}


def execute(exe, m1, m2, gamma, tb, base, label):
    parts = [matching(m, tb, base['mt_match'], mu=160., flip=False) for m in (m1, m2)]
    weights = [math.cos(gamma)**2, math.sin(gamma)**2]
    total = {k: sum(w*r[k] for w, r in zip(weights, parts)) for k in parts[0]}
    command = [exe, m1, tb, 0, *(total[k] for k in ('C7_LO', 'C8_LO', 'C4_NLO_raw', 'C7_NLO_raw', 'C8_NLO_raw')), 160.]
    output = parsed(command, label)
    if output['metadata_BR'] != output['injected_BR'] or output['injected_P2'] != 0:
        raise ValueError('D9B metadata/NLO flow failure')
    return dict(masses_GeV=[m1, m2], gamma=gamma, tanbeta=tb, mu0_GeV=160.,
                ordinary_parts=parts, weights=weights, ordinary_total=total,
                BR_legacy_NLO=output['injected_BR'], output=output,
                command=list(map(str, command)), stdout_sha256=sha(LOCAL/(label+'.log')))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--archive', type=Path, required=True)
    args = ap.parse_args()
    LOCAL.mkdir(parents=True, exist_ok=True)
    oldpath = ROOT/'validation/module5/d9b_superiso_repair.json'
    old = json.loads(oldpath.read_text())
    patch = ROOT/'module5/patches/d9b_superiso_v5.0.patch'
    if sha(args.archive) != old['archive_sha256'] or sha(patch) != old['patch_sha256']:
        raise ValueError('D9B archive/patch identity mismatch')
    source = LOCAL/'SuperIso_v5.0'
    if not source.exists():
        with tarfile.open(args.archive) as tar:
            for member in tar.getmembers():
                if member.isdir():
                    continue
                if not member.isfile() or Path(member.name).is_absolute() or '..' in Path(member.name).parts:
                    raise ValueError('Unexpected archive member')
                raw = tar.extractfile(member).read()
                if hashlib.sha256(raw).hexdigest() != old['original_distributed_sha256'][member.name]:
                    raise ValueError('Original distributed source mismatch')
                dest = LOCAL/member.name
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(raw)
        run(['patch', '-p1', '--batch', '-i', patch], 'patch', source)
    checked = {}
    for name, digest in old['fork_distributed_sha256'].items():
        path = LOCAL/name
        if sha(path) != digest:
            raise ValueError('Fork distributed source mismatch: '+name)
        checked[name] = digest
    run(['make', '-B'], 'build', source)
    exe = LOCAL/'rate_probe'
    run(['gcc', '-O2', '-I', source/'src', ROOT/'scripts/zee_d9b_rate_probe.c',
         source/'src/libsuperiso.a', '-lm', '-o', exe], 'client_build')
    base = parsed([exe], 'baseline')
    if not math.isclose(base['SM_BR'], old['baseline']['SM_BR'], rel_tol=1e-12):
        raise ValueError('D9B SM replay failure')
    controls = {}
    for mass in (550., 900.):
        row = execute(exe, mass, mass, 0., 5.3, base, 'reference_'+str(mass))
        expect = next(r for r in old['rows'] if r['mass_GeV'] == mass and r['tanbeta'] == 5.3 and not r['opposite_ld'])
        if abs(row['BR_legacy_NLO']-expect['output']['injected_BR']) > 5e-13:
            raise ValueError('D9B one-state rate replay failure')
        out = row['output']; c = row['ordinary_total']
        residual = []
        for order in ('LO', 'NLO'):
            for i in range(1, 9):
                want = ({7: c['C7_LO'], 8: c['C8_LO']} if order == 'LO' else
                        {4: c['C4_NLO_raw'], 7: c['C7_NLO_raw'], 8: c['C8_NLO_raw']}).get(i, 0.)
                residual.append(out[f'native_{order}_C{i}']-out[f'SM_{order}_C{i}']-want)
        row['max_Q1_Q8_residual'] = max(map(abs, residual))
        if row['max_Q1_Q8_residual'] > 5e-11:
            raise ValueError('Native ordinary Q1-Q8 mismatch')
        controls[str(mass)] = row
    controls['two_state_550_900'] = execute(exe, 550., 900., 1.09, 5.3, base, 'reference_pair')
    if abs(controls['two_state_550_900']['BR_legacy_NLO']-old['two_state']['example']['BR']) > 5e-13:
        raise ValueError('D9B two-state replay failure')
    rows = {}
    for name, scalar in scalar_records()[0].items():
        p = scalar['record']['physical']
        # Native one-state matching also checked at each actual D10 mass/tb.
        for i in (1, 2):
            m = p[f'mH{i}']
            control = execute(exe, m, m, 0., math.tan(p['beta']), base, name+f'_single_{i}')
            if abs(control['BR_legacy_NLO']-control['output']['native_BR']) > 5e-13:
                raise ValueError('D10 one-state native/injected mismatch')
            controls[name+f'_single_{i}'] = control
        row = execute(exe, p['mH1'], p['mH2'], p['gamma'], math.tan(p['beta']), base, name)
        row.update(scalar_sha256=scalar['sha256'])
        repeat = execute(exe, p['mH1'], p['mH2'], p['gamma'], math.tan(p['beta']), base, name+'_repeat')
        row['family_repeat_absolute_difference'] = repeat['BR_legacy_NLO']-row['BR_legacy_NLO']
        rows[name] = row
    report = dict(status='EXECUTED_SOURCE_VERIFIED_D9B_LEGACY_NLO', rows=rows, controls=controls,
                  archive_url='https://superiso.in2p3.fr/download/superiso_v5.0.tgz',
                  archive_sha256=sha(args.archive), patch_sha256=sha(patch),
                  previous_evidence_sha256=sha(oldpath), previous_commit='acfc7e4a9a446125aef6c491e30b239aaba303c4',
                  source_sha256=checked, binary_sha256=sha(exe), library_sha256=sha(source/'src/libsuperiso.a'),
                  client_sha256=sha(ROOT/'scripts/zee_d9b_rate_probe.c'), baseline=base,
                  reconstruction_script_sha256=sha(Path(__file__)),
                  **{'2026_GLOBAL_FLAVOR_FILTER_READY': False}, global_zee_acceptance=None,
                  accuracy=old['accuracy'], physical_accuracy='NOT_CERTIFIED', photon_cut_GeV=1.6)
    (LOCAL.parent/'superiso.json').write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False)+'\n')
    print({name: r['BR_legacy_NLO'] for name, r in rows.items()})


if __name__ == '__main__':
    main()
