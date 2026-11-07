"""Original D7/F13 H/A partial widths in the frozen physical tree convention.

Photon normalization: 2HDMC 0902.0851v2 Eqs.24--28. Reuses the independently
validated h125 spin functions, keeping both CP tensors and complex thresholds.
HDECAY transfer is channel-specific QCD accuracy, NOT a full Zee total.
"""
import math
from pathlib import Path

import numpy as np

from module1.scalar_constraints import reconstruct
from module2.interface import decode
from module3.core import vertices
from module4.couplings import quarks, rotations, trilinears
from module7.d4_inputs import SM
from module7.d4_tree_kernels import scalar_scalar, scalar_vector
from research.full_constraints.higgs.decays_bridge import extra_widths, neutral_hhh, read_output
from research.full_constraints.higgs.diphoton import amplitude, MASSES
from research.full_constraints.higgs.sushi_bridge import benchmark, sha, ROOT

HERE = Path(__file__).resolve().parent


def verify_sources(manifest):
    """Historical pins are immutable; no acceptance of a modified model/card."""
    for group in ('model_sources', 'bridge_sources'):
        for path, digest in manifest[group].items():
            if sha(ROOT/path) != digest:
                raise ValueError('Source digest mismatch: '+path)


def photons(name, state):
    if state not in ('H', 'A'):
        raise ValueError('H/A required')
    r,w = benchmark(name); p = r['input']['physical']
    mass = p['mh2' if state == 'H' else 'ma']
    k = {f: quarks(p['v'], 'top' if f in ('u','c','t') else 'bottom', p)[state]
         for f in ('u','c','t','d','s','b')}
    C = vertices(decode(w['yukawas']['D']), p, SM['lepton_masses'])[state][0]
    k.update(zip(('e','mu','tau'), np.diag(C)*p['v']/SM['lepton_masses']))
    g = trilinears(p, reconstruct(p)[0])[state][1:,1:]
    if np.max(abs(g-g.conj().T)) > 1e-10:
        raise ValueError('Non-Hermitian scalar interaction')
    # In the restricted real potential G_A is imaginary antisymmetric. With
    # photon Q=1, propagators diagonal, triangles and seagulls contain only
    # G_ii. A single G_12 cannot close the species trace, even for unequal m.
    if state == 'A' and np.max(abs(np.diag(g))) > 1e-10:
        raise ValueError('CP-odd diagonal charged coupling must vanish')
    charged = [(p[f'mH{i+1}'], g[i,i].real, 1) for i in range(2)] if state == 'H' else []
    kv = math.sin(p['beta']-p['alpha']) if state == 'H' else 0.
    alpha = (2*SM['EW']['mW']/p['v'])**2*(1-(SM['EW']['mW']/SM['EW']['mZ'])**2)/(4*math.pi)
    out = amplitude(mass, kv, k, charged, p['v'], alpha=alpha)
    zp = rotations(p)[2][1:]; cw = SM['EW']['mW']/SM['EW']['mZ']
    z = 2*SM['EW']['mW']/p['v']/cw*(.5*zp[:,:2]@zp[:,:2].T-(1-cw*cw)*np.eye(2))
    return dict(amplitude=out, mass_GeV=mass, kappas=k, kV=kv,
                G_charged_GeV=g, Z_current=z, G12_Z21_GeV=g[0,1]*z[1,0],
                alpha_em=alpha, charged=charged,
                status='LEADING_ONE_LOOP_PARTIAL_WIDTH', theory_sigma=None,
                scalar_photon_trace='diagonal G only; Q and QQ seagull diagonal; A diagonal G=0',
                Zgamma_status='MISSING_PREDICTION')


def transferable(name, path):
    """BR_R2HDM times Gamma_R2HDM gives partial widths; reject its total."""
    r,w = benchmark(name); p = r['input']['physical']; raw = read_output(path)
    out = extra_widths(name)
    for state, source in (('H','Hh'),('A','A')):
        brsum = math.fsum(v for k,v in raw.items() if k.startswith('b_'+source+'_'))
        if not math.isclose(brsum, 1, abs_tol=1e-10):
            raise ValueError('HDECAY reference BR sum mismatch')
        modes = ('bb','ss','cc','tt','gg') + (('WW','ZZ','HlHl','ZA','AA') if state == 'H' else ('ZHl','ZHh'))
        out[state].update({mode: raw['w_'+source]*raw['b_'+source+'_'+mode] for mode in modes})
    hhh = scalar_scalar(p['mh2'], p['mh1'], p['mh1'], neutral_hhh(p))/2
    ahz = scalar_vector(p['ma'],p['mh1'],SM['EW']['mZ'],SM['EW']['mZ']/p['v']*math.sin(p['beta']-p['alpha']))
    for a,b in ((hhh,out['H']['HlHl']),(ahz,out['A']['ZHl'])):
        if not math.isclose(a,b,rel_tol=1e-9):
            raise ValueError('Independent Hhh/AhZ width mismatch')
    for mode in ('WW','ZZ'):
        ratio = out['H'][mode]/(raw['SM_w_H']*raw['SM_b_H_'+mode])
        if not math.isclose(ratio,math.sin(p['beta']-p['alpha'])**2,rel_tol=1e-10):
            raise ValueError('Independent vector coupling control failed')
    return out


def calculate(name, raw_path):
    r,w = benchmark(name); p = r['input']['physical']; rows = transferable(name,raw_path)
    result = {}
    for state in ('H','A'):
        photon = photons(name,state); M = photon['mass_GeV']; channels = rows[state]
        channels['gamma gamma'] = photon['amplitude']['width_GeV']
        # Previously omitted u,d: explicit tree masses in both Yukawa and phase
        # space, colour=3. No QCD accuracy is claimed for these tiny widths.
        for f in ('u','d'):
            m = MASSES[f]; C = quarks(m, 'top' if f=='u' else 'bottom',p)[state]
            beta = math.sqrt(1-4*m*m/M**2)
            channels[f+f+' tree'] = 3*M/(8*math.pi)*(C.real**2*beta**3+C.imag**2*beta)
        threshold = []
        for i,j in ((1,1),(1,2),(2,2)):
            t = p[f'mH{i}']+p[f'mH{j}']
            if M >= t: raise ValueError('Open charged-pair mode requires calculation')
            threshold.append(dict(channel=f'H{i}+ H{j}-', threshold_GeV=t,status='CLOSED_ON_SHELL'))
        result[state] = dict(status='TOTAL_WIDTH_INCOMPLETE', partial_widths_GeV=channels,
            known_disjoint_sum_GeV=math.fsum(channels.values()), photon=photon,
            total_width_GeV=None, branching_fractions=None, theory_sigma=None,
            charged_pair_thresholds=threshold,
            charged_W_daughter_domains=[dict(state=f'H{i}',
                threshold_gap_GeV=M-p[f'mH{i}']-SM['EW']['mW'],
                daughter_tree_width_GeV=w['decays'][f'H{i}']['total']['total_width_GeV']) for i in (1,2)],
            missing=[
                ('Complete H Zgamma: unequal-mass charged scalar G12 Z21 triangles, seagull and gauge completion'
                 if state == 'H' else 'A Zgamma fermion amplitudes with general complex lepton couplings; scalar sector CP forbids a bosonic epsilon tensor'),
                'Model-matched charged-W off-shell/finite-daughter correction without double counting the on-shell cascade; no numerical bound',
                ('Nonresonant EW multibody channels outside transferred HDECAY approximations; no numerical materiality bound'
                 if state == 'H' else 'Loop-induced A WW/ZZ with model-matched fermion and gauge amplitudes; no numerical width/materiality bound'),
                'Neutral/scalar off-shell cascades beyond transferred HDECAY approximation, including finite H in F13 A -> H Z*',
                'Channel-specific QCD/EW truncation and parametric/correlated uncertainties; no total error budget'],
            exclusion=None)
    return dict(name=name, scalar_sha256=r['input_sha256'],yukawa_sha256=w['yukawa_sha256'],
                raw_sha256=sha(raw_path),states=result,physical_higgs='UNKNOWN',global_acceptance=None)


def jsonable(value):
    if isinstance(value,dict): return {k:jsonable(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)): return [jsonable(v) for v in value]
    if isinstance(value,np.ndarray): return jsonable(value.tolist())
    if isinstance(value,complex): return dict(real=float(value.real),imag=float(value.imag))
    if isinstance(value,np.generic): return value.item()
    return value
