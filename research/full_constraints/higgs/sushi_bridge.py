"""Fixed original-card SusHi LO bridge. No scans or exclusion decisions.

Native ZH=((cos a,sin a),(-sin a,cos a)); SusHi uses
((-sin aS,cos aS),(cos aS,sin aS)). aS=a+pi/2 preserves H,
rephases h by -1, and leaves the native physical A unchanged.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess

from module13.higgstools import inputs
from module4.couplings import quarks
from module7.d4_inputs import SM
from research.full_constraints.higgs.diphoton import loops

ROOT = Path(__file__).resolve().parents[3]
PDF = 'MMHT2014lo68cl'
ARCHIVE_SHA = '509b59fe56a1dbc4274871a5f84150e0ad91b61ef44908b6aa772f2d7c6a183a'
BENCHMARK_SHA = {'D7': 'ff0c551534e5051f223c00435293403e3b553f52e0cbec4344287da8b3dce862',
                 'F13': '9117e7af53f9ad5c21f964a7c216de7af5824e903856fed54b9b237c922f4a1d'}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, sort_keys=True, allow_nan=False)+'\n')


def benchmark(name):
    if name not in BENCHMARK_SHA:
        raise ValueError('Only original D7/F13 witnesses authorized')
    record, witness = inputs(name)
    if record['input_sha256'] != BENCHMARK_SHA[name]:
        raise ValueError('Original scalar hash mismatch')
    return record, witness


def couplings(p, state):
    if state not in ('H', 'A'):
        raise ValueError('Neutral H/A identity required')
    native = [quarks(p['v'], f, p)[state] for f in ('top', 'bottom')]
    native = [z.imag if state == 'A' else z.real for z in native]
    a = p['alpha']+math.pi/2
    mapped = ([math.sin(a)/math.sin(p['beta']), math.cos(a)/math.cos(p['beta'])]
              if state == 'H' else [1/math.tan(p['beta']), math.tan(p['beta'])])
    if max(abs(x-y) for x,y in zip(native,mapped)) > 2e-14:
        raise ValueError('Native/SusHi Yukawa mismatch')
    return dict(zip(('top','bottom'), native))


def lo_amplitude(mass, cp, kt, kb, kc=None, mt=172.4, mb=4.78, mc=1.273):
    if cp not in ('even','odd') or not all(math.isfinite(v) for v in (mass,kt,kb,mt,mb,mc,kt if kc is None else kc)) or min(mass,mt,mb,mc)<=0:
        raise ValueError('Finite masses and CP assignment required')
    index = 1 if cp == 'even' else 3
    terms = [k*loops((mass/(2*m))**2)[index] for k,m in
             ((kt,mt),(kb,mb),(kt if kc is None else kc,mc))]
    return sum(terms), terms


def card(name, state, scale=(1.,1.), member=0, factors=(1.,1.,1.)):
    r,_=benchmark(name);p=r['input']['physical'];couplings(p,state)
    if len(scale)!=2 or any(not math.isfinite(x) or x<=0 for x in scale):
        raise ValueError('Positive finite scale multipliers required')
    if not isinstance(member,int) or isinstance(member,bool) or not 0<=member<=50:
        raise ValueError('PDF member outside pinned set')
    if len(factors)!=3 or any(not math.isfinite(x) for x in factors):
        raise ValueError('Finite charm/top/bottom factors required')
    # The central scales are M/2 for ggF and (M,M/4) for 5FS bbH.
    rr,ff=scale
    return f'''# Original {name}; scalar SHA256 {r['input_sha256']}
Block SUSHI
 1 2
 2 {12 if state=='H' else 21}
 3 0
 4 13000.0
 5 0
 6 0
 7 0
 19 1
 20 0
Block 2HDM
 2
Block SMINPUTS
 1 137.035999084
 2 {1/(math.sqrt(2)*p['v']**2):.16e}
 3 0.135
 4 91.1876
 5 4.183
 6 172.4
 8 1.273
Block MINPAR
 3 {math.tan(p['beta']):.16e}
Block ALPHA
 {p['alpha']+math.pi/2:.16e}
Block MASS
 25 {p['mh1']:.16e}
 35 {p['mh2']:.16e}
 36 {p['ma']:.16e}
Block DISTRIB
 1 0
 2 0
 3 0
 4 0
Block SCALES
 1 {rr*.5:.16e}
 2 {ff*.5:.16e}
 11 {rr:.16e}
 12 {ff*.25:.16e}
 3 0
Block RENORMBOT
 1 0
 4 4.78
Block PDFSPEC
 1 {PDF}.LHgrid
 2 {PDF}.LHgrid
 3 {PDF}.LHgrid
 4 {PDF}.LHgrid
 10 {member}
Block VEGAS
 1 10000
 2 5
 3 0
 4 10000
 5 5
 14 20000
 15 3
 6 0
 7 10000
 8 5
 17 20000
 18 3
 9 0
Block FACTORS
 1 {factors[0]:.16e}
 2 {factors[1]:.16e}
 3 {factors[2]:.16e}
'''


def blocks(path):
    result={};block=None
    for line in Path(path).read_text().splitlines():
        fields=line.split('#')[0].split()
        if not fields:continue
        if fields[0].lower()=='block':
            block=fields[1].lower();result[block]={}
        elif block and len(fields)==2:
            try:result[block][int(fields[0])]=float(fields[1].replace('D','E'))
            except ValueError:pass
    return result


def execute(executable, out, name, state, tag, **kwargs):
    stem=f'{name}_{state}_{tag}';inp=out/(stem+'.in');output=out/(stem+'.out')
    inp.write_text(card(name,state,**kwargs))
    with (out/(stem+'.log')).open('w') as log:
        subprocess.run([str(executable),str(inp),str(output)],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=90)
    data=blocks(output)
    expected=couplings(benchmark(name)[0]['input']['physical'],state)
    for index,key in [(101,'top'),(201,'bottom')]:
        if not math.isclose(data['hggsusy'][index],expected[key],rel_tol=2e-8):
            raise ValueError('Executed SusHi coupling does not match native vertex')
    rates={p:dict(sigma_pb=data[b][1],integration_error_pb=data[b][101])
           for p,b in [('ggF','sushiggh'),('bbH','sushibbh')]}
    if any(v['sigma_pb']<0 or not math.isfinite(v['sigma_pb']) for v in rates.values()):
        raise ValueError('Invalid executed rate')
    return dict(name=name,state=state,tag=tag,input_sha256=sha(inp),output_sha256=sha(output),
                stdout_sha256=sha(out/(stem+'.log')),rates=rates,blocks=data)


def validate_rate(row, metadata, raw_dir):
    """Strict current-evidence reader; validate bytes AND physical contracts."""
    required=dict(energy_GeV=13000.,beams='pp',units='pb',PDF=PDF,PDF_member=0,
                  QCD_order='LO',flavours=5,version='1.7.0',archive_sha256=ARCHIVE_SHA,
                  ggF_mb_scheme='OS 4.78 GeV',bbH_mb_scheme='MSbar evolved from mb(mb)=4.183 GeV',
                  CP_scheme='native A; alpha_SusHi=alpha_native+pi/2')
    if any(metadata.get(k)!=v for k,v in required.items()):
        raise ValueError('Production energy/PDF/order/source/flavour/CP/scheme contract mismatch')
    r,_=benchmark(row['name']);state=row['state'];p=r['input']['physical'];couplings(p,state)
    if row['scalar_sha256']!=r['input_sha256'] or row['mass_GeV']!=p['mh2' if state=='H' else 'ma']:
        raise ValueError('Original scalar identity/mass mismatch')
    stem=f"{row['name']}_{state}_central";central=row['central']
    for suffix,key in [('in','input_sha256'),('out','output_sha256'),('log','stdout_sha256')]:
        if sha(Path(raw_dir)/(stem+'.'+suffix))!=central[key]:raise ValueError('Native run bytes changed')
    if hashlib.sha256(card(row['name'],state).encode()).hexdigest()!=central['input_sha256']:
        raise ValueError('Central input differs from exact original-card mapping')
    data=blocks(Path(raw_dir)/(stem+'.out'))
    for proc,block in [('ggF','sushiggh'),('bbH','sushibbh')]:
        val=central['rates'][proc]
        if not math.isfinite(val['sigma_pb']) or val['sigma_pb']<=0 or val['sigma_pb']!=data[block][1]:
            raise ValueError('Rate is missing, invalid or inconsistent with executed output')
        if val['integration_error_pb']!=data[block][101] or val['integration_error_pb']<0:
            raise ValueError('Integration error mismatch')
    if row['production_status']!='VALIDATED_SCOPED_LO_CTB_QCD':raise ValueError('Unvalidated production')
    return central['rates']


def analysis_gate(matrix):
    """Preserve per-ID physics gate: no complete Zee neutral width exists here.

    This overlay is consumed before any HiggsTools population; no effective-
    coupling default or zero BR is used to fill an uncomputed signal.
    """
    return dict(HiggsTools_version=matrix['version'],datasets={k:v['git_head'] for k,v in matrix['datasets'].items()},
                complete_signals_connected=0,validated_exclusions=0,
                analyses=[dict(id=l['id'],collider=l['collider'],cases={name:dict(
                    status=('NOT_APPLICABLE' if l['cases'][name]['status']=='NOT_APPLICABLE' else 'MISSING_PREDICTION'),
                    reason=l['cases'][name]['reason'] if l['cases'][name]['status']=='NOT_APPLICABLE' else
                    'Complete Zee BR/width, required processes/energies and signal/uncertainty qualification absent; production alone cannot populate a limit')
                    for name in ('D7','F13')}) for l in matrix['limits']],
                physical_higgs='UNKNOWN',exclusion=None,global_acceptance=None)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--sushi',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    args.out.mkdir(parents=True,exist_ok=False)
    result=[]
    for name in ('D7','F13'):
        for state in ('H','A'):
            result.append(execute(args.sushi,args.out,name,state,'central'))
    dump(args.out/'central.json',result)
    print(json.dumps([{k:r[k] for k in ('name','state','rates')} for r in result],indent=2))


if __name__=='__main__':main()
