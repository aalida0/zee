"""Takagi U.T M U=diag(m); PDG PMNS phases, with explicit undefined cases."""
import math
import numpy as np
from .core import matrix, NumericalUnknown


def takagi(M, ordering):
    M = matrix(M, 'symmetric')
    if ordering not in ('NO', 'IO'):
        raise ValueError('Select NO or IO explicitly')
    # A Frobenius norm of the unscaled matrix squares entries and can
    # underflow to zero or overflow even when every matrix entry is finite.
    scale = float(np.max(abs(M)))
    if scale == 0:
        return np.zeros(3), np.eye(3, dtype=complex), {'reconstruction_relative': 0., 'unitarity': 0., 'zero_tolerance_eV': 0.}
    # Real symmetric antilinear eigenproblem M u = m u*. Unlike an SVD phase
    # patch, this works within exactly degenerate nonzero singular subspaces.
    normalized = M/scale
    norm = float(np.linalg.norm(normalized))
    A, B = normalized.real, normalized.imag
    values, vectors = np.linalg.eigh(np.block([[A, -B], [-B, -A]]))
    singular = np.linalg.svd(normalized, compute_uv=False)
    rank = int(np.count_nonzero(singular > norm*1e-14))
    positive = vectors[:, -rank:] if rank else np.empty((6, 0))
    U = positive[:3]+1j*positive[3:]
    with np.errstate(over='ignore', invalid='ignore'):
        masses = np.maximum(values[-rank:], 0)*scale if rank else np.array([])
    if not np.isfinite(masses).all():
        raise NumericalUnknown('Takagi singular values exceed finite numerical range')
    if rank < 3:
        _, _, vh = np.linalg.svd(normalized)
        null = vh[rank:].conj().T
        U = np.column_stack((null, U))
        masses = np.r_[np.zeros(3-rank), masses]
    for j in range(3):
        z = U[np.argmax(abs(U[:, j])), j]
        if masses[j] == 0:
            U[:, j] *= np.exp(-1j*np.angle(z))
        elif z.real < 0 or (z.real == 0 and z.imag < 0):
            U[:, j] *= -1
    indices = [0, 1, 2] if ordering == 'NO' else [1, 2, 0]
    masses, U = masses[indices], U[:, indices]
    rec = float(np.linalg.norm(normalized-U.conj()@np.diag(masses/scale)@U.conj().T)/norm)
    unit = float(np.linalg.norm(U.conj().T@U-np.eye(3)))
    if not np.isfinite(masses).all() or not np.isfinite([rec, unit]).all() or max(rec, unit) > 2e-12:
        raise NumericalUnknown('Takagi reconstruction/orthogonality unresolved')
    return masses, U, {'reconstruction_relative': rec, 'unitarity': unit, 'zero_tolerance_eV': scale*(norm*1e-14)}


def wrap(x):
    return float(x % (2*math.pi))


def observables(M, ordering):
    M = matrix(M, 'symmetric')
    m, U, diagnostics = takagi(M, ordering)
    tol = max(m)*1e-11
    degenerate = any(abs(m[i]-m[j]) <= tol for i in range(3) for j in range(i))
    with np.errstate(over='ignore', invalid='ignore'):
        splittings = [float((m[j]-m[i])*(m[j]+m[i])) for i,j in ((0,1),(0,2),(1,2))]
    if not np.isfinite(splittings).all():
        raise NumericalUnknown('Mass-squared splittings exceed finite numerical range')
    if any(value == 0 and m[i] != m[j] for value,(i,j) in zip(splittings,((0,1),(0,2),(1,2)))):
        raise NumericalUnknown('Nonzero mass-squared splitting underflows numerical range')
    out = {'ordering': ordering, 'masses_eV': m.tolist(), 'U': U,
           'dm21_eV2': splittings[0],
           'dm31_eV2': splittings[1],
           'dm32_eV2': splittings[2],
           'dm3l_eV2': splittings[1 if ordering == 'NO' else 2],
           'sum_m_eV': float(sum(m)), 'm_beta_eV': float(max(m)*np.linalg.norm(U[0]*(m/max(m)))) if max(m) else 0.,
           'm_bb_eV': float(abs(M[0, 0])), 'diagnostics': diagnostics,
           'mixing_status': 'UNKNOWN' if degenerate else 'PASS',
           'undefined_reasons': [], 'sin2_theta12': None, 'sin2_theta13': None,
           'sin2_theta23': None, 'J_CP': None, 'sin_delta': None, 'cos_delta': None,
           'delta_rad': None, 'alpha21_rad': None, 'alpha31_rad': None,
           'majorana_pair_phases_rad': {'21': None, '31': None, '32': None}}
    if degenerate:
        out['undefined_reasons'].append('Degenerate masses: PMNS columns are not physically fixed')
        return out
    q13 = float(abs(U[0, 2])**2)
    if 1-q13 < 1e-14:
        out['undefined_reasons'].append('Singular PDG angle chart')
        out['mixing_status'] = 'UNKNOWN'
        return out
    q12, q23 = [float(np.clip(x/(1-q13), 0, 1)) for x in (abs(U[0, 1])**2, abs(U[1, 2])**2)]
    out.update(sin2_theta12=q12, sin2_theta13=q13, sin2_theta23=q23)
    out.update(theta12_rad=float(math.asin(math.sqrt(q12))),
               theta13_rad=float(math.asin(math.sqrt(q13))),
               theta23_rad=float(math.asin(math.sqrt(q23))))
    J = float(np.imag(U[0, 0]*U[1, 1]*U[0, 1].conjugate()*U[1, 0].conjugate()))
    out['J_CP'] = J
    s12, s13, s23 = np.sqrt([q12, q13, q23])
    c12, c13, c23 = np.sqrt(np.clip(1-np.array([q12, q13, q23]), 0, 1))
    denom = c12*c23*c13**2*s12*s23*s13
    delta = None
    if denom > 1e-14:
        sd = J/denom
        cd = (abs(U[1, 0])**2-s12**2*c23**2-c12**2*s23**2*s13**2)/(2*s12*c12*s23*c23*s13)
        if abs(sd*sd+cd*cd-1) > 2e-8:
            raise NumericalUnknown('Independent CP invariants inconsistent')
        delta = wrap(math.atan2(sd, cd))
        out.update(sin_delta=float(sd), cos_delta=float(cd), delta_rad=delta)
    else:
        out['undefined_reasons'].append('Dirac phase undefined at a vanishing mixing factor')
    # alpha_i in PDG U=V(delta) diag(1,e^(i alpha21/2),e^(i alpha31/2)).
    # Pair differences remain useful when m1=0. Never assign a massless column phase.
    for i, j, label in ((0, 1, '21'), (0, 2, '31'), (1, 2, '32')):
        if min(m[i], m[j]) <= diagnostics['zero_tolerance_eV']:
            continue
        if j == 2 and delta is None and s13 <= 1e-14:
            # At theta13=0 the PDG mixing matrix is real and delta drops out.
            # Electron-row ratios cannot determine alpha3, but a mu/tau row
            # with both columns present determines it without a Dirac phase.
            products = U[:, j]*U[:, i].conjugate()
            product = products[np.argmax(abs(products))]
            if abs(product) > 1e-12:
                out['majorana_pair_phases_rad'][label] = wrap(2*np.angle(product))
            continue
        if min(abs(U[0, i]), abs(U[0, j])) < 1e-12:
            continue
        if j == 2 and delta is None:
            continue
        phase = wrap(2*np.angle(U[0, j]*U[0, i].conjugate())+(2*delta if j == 2 else 0))
        out['majorana_pair_phases_rad'][label] = phase
    out['alpha21_rad'] = out['majorana_pair_phases_rad']['21']
    out['alpha31_rad'] = out['majorana_pair_phases_rad']['31']
    if any(x is None for x in out['majorana_pair_phases_rad'].values()):
        out['undefined_reasons'].append('Some Majorana phases undefined (zero mass or singular angle chart)')
    return out
