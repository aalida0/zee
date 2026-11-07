"""Extract disjoint transferable HDECAY partial widths; retain missing Zee modes.

Never normalize an incomplete sum into model branching fractions. Charged-W
widths cross the already native-validated D4 vertex and include both charges.
"""
import math
from pathlib import Path

from module1.scalar_constraints import reconstruct
from module2.interface import decode
from module3.core import neutral_width, vertices
from module7.d4_inputs import SM, native_card
from module7.d4_native import expected_coefficients
from module7.d4_tree_kernels import scalar_scalar, scalar_vector
from research.full_constraints.higgs.sushi_bridge import benchmark, dump


def read_output(path):
    result={}
    for line in Path(path).read_text().splitlines():
        k,v=line.split()
        if k in result:raise ValueError('Duplicate HDECAY output')
        result[k]=float(v)
        if not math.isfinite(result[k]) or result[k]<0:raise ValueError('Invalid HDECAY result')
    return result


def neutral_hhh(p):
    """Independent derivative of V(phi1,phi2), contracted with H,h,h rows."""
    q=reconstruct(p)[0];v1=p['v']*math.cos(p['beta']);v2=p['v']*math.sin(p['beta'])
    lm=sum(q[k] for k in ('Lambda3','Lambda4','Lambda5'))
    x=[math.cos(p['alpha']),math.sin(p['alpha'])];y=[-x[1],x[0]]
    def tensor(i,j,k):
        return (3*q['Lambda1']*v1,lm*v2,lm*v1,3*q['Lambda2']*v2)[i+j+k]
    return sum(y[i]*x[j]*x[k]*tensor(i,j,k) for i in range(2) for j in range(2) for k in range(2))


def extra_widths(name):
    r,w=benchmark(name);p=r['input']['physical'];ml=SM['lepton_masses']
    leps=vertices(decode(w['yukawas']['D']),p,ml);result={}
    for state in ('H','A'):
        M=p['mh2' if state=='H' else 'ma'];rows={}
        for k in (1,2):
            card=native_card(p,w['yukawas'],M,name+'/'+state)
            coefficients=expected_coefficients(card)
            index=36+(k-1)*4+2 if state=='H' else 44+(k-1)*2
            c=coefficients[index][0]
            analytic=SM['EW']['mW']/p['v']*(math.cos(p['gamma']) if k==1 else -math.sin(p['gamma']))
            if state=='H':analytic*=math.cos(p['beta']-p['alpha'])
            if not math.isclose(abs(c),abs(analytic),rel_tol=1e-13):raise ValueError('D4 charged-W vertex mismatch')
            rows[f'H{k}+ W- plus conjugate']=2*scalar_vector(M,p[f'mH{k}'],SM['EW']['mW'],c)
        C=leps[state][0]
        for i in range(3):
            for j in range(i,3):
                rows[f'{("e","mu","tau")[i]} {("e","mu","tau")[j]}'+(' both charges' if i!=j else '')]=(2 if i!=j else 1)*neutral_width(C,M,i,j,ml)
        result[state]=rows
    return result


def assemble_d7(path):
    raw=read_output(path);r,w=benchmark('D7');p=r['input']['physical'];extra=extra_widths('D7');out={}
    # Quark-only QCD / tree-vector contributions match the neutral doublet sector.
    # No R2HDM charged-loop, Type-II lepton, or fictitious single H+ contribution is copied.
    for state,source in [('H','Hh'),('A','A')]:
        total=raw['w_'+source]
        brsum=math.fsum(v for k,v in raw.items() if k.startswith('b_'+source+'_'))
        if not math.isclose(brsum,1.,abs_tol=1e-10):raise ValueError('R2HDM BR sum mismatch')
        channels={mode:total*raw['b_'+source+'_'+mode] for mode in ('bb','ss','cc','tt','gg')}
        if state=='H':
            channels.update({mode:total*raw['b_Hh_'+mode] for mode in ('WW','ZZ','HlHl','ZA','AA')})
            g=neutral_hhh(p)
            hhh=scalar_scalar(p['mh2'],p['mh1'],p['mh1'],g)/2
            if not math.isclose(hhh,channels['HlHl'],rel_tol=1e-9):raise ValueError('Neutral potential/HDECAY Hhh mismatch')
            for mode in ('WW','ZZ'):
                ratio=channels[mode]/(raw['SM_w_H']*raw['SM_b_H_'+mode])
                if not math.isclose(ratio,math.sin(p['beta']-p['alpha'])**2,rel_tol=1e-10):
                    raise ValueError('SM/vector coupling-limit control failed')
        else:
            channels.update({mode:total*raw['b_A_'+mode] for mode in ('ZHl','ZHh')})
            ahz=scalar_vector(p['ma'],p['mh1'],SM['EW']['mZ'],SM['EW']['mZ']/p['v']*math.sin(p['beta']-p['alpha']))
            if not math.isclose(ahz,channels['ZHl'],rel_tol=1e-9):raise ValueError('Neutral gauge/HDECAY AhZ mismatch')
        channels.update(extra[state])
        closed=[]
        for i,j in ((1,1),(1,2),(2,2)):
            threshold=p[f'mH{i}']+p[f'mH{j}'];M=p['mh2' if state=='H' else 'ma']
            if M>=threshold:raise ValueError('Open charged scalar pair requires a qualified width')
            closed.append(dict(channel=f'H{i}+ H{j}- and conjugate if distinct',
                               status='CLOSED_ON_SHELL',threshold_GeV=threshold,width_on_shell_GeV=0.))
        out[state]=dict(status='INCOMPLETE',partial_widths_GeV=channels,
                        R2HDM_branching_sum=brsum,charged_pair_threshold_ledger=closed,
                        known_disjoint_sum_GeV=math.fsum(channels.values()),total_width_GeV=None,branching_fractions=None,
                        missing=['Zee gamma gamma with both charged states and complex leptons',
                                 'Zee Z gamma including mixed charged currents',
                                 'loop-induced A WW/ZZ and other EW channels at target accuracy/materiality',
                                 'finite daughter width/off-shell charged-W modes and materiality bounds',
                                 'omitted light u/d channels and order/parametric/scale uncertainty qualification'],
                        rejected_R2HDM_total_GeV=total,exclusion=None)
    return dict(name='D7',scalar_sha256=r['input_sha256'],yukawa_sha256=w['yukawa_sha256'],
                states=out,other_original_card_tree_extras=extra_widths('F13'),
                Hhh_independent_GeV=hhh,AhZ_independent_GeV=ahz,
                scope='HDECAY 6.60 quark-QCD + tree/off-shell vector/neutral sector; native Zee tree extras; incomplete mixed accuracy',
                complete=False,exclusion=None)


def require_complete_width(width):
    if width.get('status')!='COMPLETE' or width.get('missing') or width.get('total_width_GeV') is None:
        raise ValueError('MISSING_PREDICTION: incomplete Zee width cannot enter HiggsTools')
    channels=width['partial_widths_GeV'];total=width['total_width_GeV']
    if any(k in ('inv','inv_derived','total') for k in channels):
        raise ValueError('Inclusive derived channel cannot enter independent partial-width sum')
    if not channels or any(not math.isfinite(x) or x<0 for x in channels.values()) or total<=0:
        raise ValueError('Invalid disjoint partial widths')
    if not math.isclose(math.fsum(channels.values()),total,rel_tol=1e-10):
        raise ValueError('Total width/independent sum mismatch')
    return total


if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--raw',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    if a.out.exists():raise FileExistsError(a.out)
    dump(a.out,assemble_d7(a.raw))
