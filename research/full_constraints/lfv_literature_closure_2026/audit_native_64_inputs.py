"""Audit the original 64 Zee SLHA inputs: direct e-mu D and leading F-only dipole.

Run from repo root:
python -m research.full_constraints.lfv_literature_closure_2026.audit_native_64_inputs \
  --artifact path/to/zee-exact-64-inputs-NOT-native-LFV-rates.zip \
  --out /tmp/zee-64-lfv-materiality.json

This is NOT a physical LFV rate or full-model allowed-region classifier.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
from zipfile import ZipFile
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / 'module14/conditional_scan/candidate_followup.json'
DATASET_SHA = '2d97c2a58cb65f5ec7244282a04c5e19a0cae0897b8a0581b76503180acd4be9'
MEG_NORM = 1.367785824084e-12


def blocks(raw):
    out, active = {}, None
    for line in raw.decode('utf-8').splitlines():
        cols = line.partition('#')[0].split()
        if not cols:
            continue
        if len(cols) == 2 and cols[0].upper() == 'BLOCK':
            active = cols[1].upper()
            if active in out:
                raise ValueError('Repeated SLHA BLOCK ' + active)
            out[active] = {}
        elif active:
            try:
                key = tuple(map(int, cols[:-1]))
                v = float(cols[-1].replace('D', 'E'))
            except ValueError:
                continue
            if not key or not math.isfinite(v) or key in out[active]:
                raise ValueError('Invalid SLHA entry in ' + active)
            out[active][key] = v
    return out


def mat(b, name):
    real, imag = b[name], b['IM' + name]
    keys = {(i,j) for i in (1,2,3) for j in (1,2,3)}
    if set(real) != keys or set(imag) != keys:
        raise ValueError('Incomplete complex matrix ' + name)
    return np.array([[real[i,j] + 1j*imag[i,j] for j in (1,2,3)]
                     for i in (1,2,3)], dtype=complex)


def audit(artifact, scalar_db=DATA):
    source = json.loads(Path(scalar_db).read_text())
    if source.get('dataset_sha256') != DATASET_SHA:
        raise ValueError('Original scalar dataset identity mismatch')
    spectra = source['tables']['CERTIFIED_VACUUM_APPROX_BSG_16']
    if len(spectra) != 16:
        raise ValueError('Expected 16 original scalar spectra')
    scalars = {str(p['id']): p for p in spectra}
    with ZipFile(artifact) as z:
        found = [n for n in z.namelist() if n.endswith('/source-manifest.json')]
        if len(found) != 1:
            raise ValueError('Missing/repeated artifact manifest')
        manifest = json.loads(z.read(found[0]))
        if manifest.get('new_family_count') != 64 or len(manifest.get('cards',[])) != 64:
            raise ValueError('Expected 64 original input cards')
        seen, rows = set(), []
        for card in manifest['cards']:
            key = (card['scalar_id'], card['ordering'], card['seed'])
            if key in seen or card['ordering'] not in ('NO', 'IO'):
                raise ValueError('Duplicate/invalid card identity')
            seen.add(key)
            scalar = scalars[str(card['scalar_id'])]
            if scalar['scalar_sha256'] != card['source_scalar_sha256']:
                raise ValueError('Scalar source SHA mismatch')
            names = [n for n in z.namelist() if n.endswith('/' + card['slha_file'])]
            if len(names) != 1:
                raise ValueError('Card absent/repeated in ZIP')
            raw = z.read(names[0])
            if hashlib.sha256(raw).hexdigest() != card['slha_sha256']:
                raise ValueError('SLHA source SHA mismatch')
            b = blocks(raw)
            F, Y2 = mat(b, 'FZEE'), mat(b, 'YEE2')
            if np.max(abs(F+F.T)) > 1e-16:
                raise ValueError('Fzee antisymmetry mismatch')
            tanb = b['MINPAR'][(10,)]
            if not 0 < tanb < math.inf:
                raise ValueError('Invalid tanbeta')
            if abs(tanb-math.tan(scalar['physical']['beta'])) > 1e-10:
                raise ValueError('Wrong scalar/Yukawa pairing')
            cb = 1/math.hypot(1,tanb)
            ff = (F.conj().T @ F)[0,1]
            p = scalar['physical']
            w = (math.sin(p['gamma'])**2 / p['mH1']**2
                 + math.cos(p['gamma'])**2 / p['mH2']**2)
            cR = -ff*w / (192*math.pi**2)
            rows.append({
                'id': list(key), 'source_SHA256': card['slha_sha256'],
                'abs_D_e_mu': abs(Y2[0,1])/cb, 'abs_D_mu_e': abs(Y2[1,0])/cb,
                'abs_FdagF_e_mu': abs(ff), 'max_abs_F': float(abs(F).max()),
                'abs_C_R_F_only_GeVminus2': abs(cR),
                'full_physical_LFV': None})
    if len(seen) != 64 or len({k[0] for k in seen}) != 16:
        raise ValueError('Incomplete original scalar/flavor coverage')
    return {
        'status': 'SOURCE_64_YUKAWA_MATERIALITY_PASS',
        'input_only_not_native_Wilsons': True,
        'n_original_cards': 64,
        'max_abs_D_e_mu': max(r['abs_D_e_mu'] for r in rows),
        'max_abs_D_mu_e': max(r['abs_D_mu_e'] for r in rows),
        'max_abs_FdagF_e_mu': max(r['abs_FdagF_e_mu'] for r in rows),
        'max_C_R_F_only_GeVminus2': max(r['abs_C_R_F_only_GeVminus2'] for r in rows),
        'MEGII_dipole_norm_limit_GeVminus2': MEG_NORM,
        'full_physical_LFV': None, 'global_acceptance': None,
        'rows': rows,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--artifact', type=Path, required=True)
    p.add_argument('--scalar-db', type=Path, default=DATA)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    if args.out.exists():
        raise FileExistsError('Never overwrite source evidence')
    result = audit(args.artifact, args.scalar_db)
    args.out.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print('SOURCE_64_YUKAWA_MATERIALITY_PASS; FULL_PHYSICAL_ZEE_LFV_UNKNOWN')


if __name__ == '__main__':
    main()
