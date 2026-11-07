"""Enumerate every *loaded* pinned HB limit and HS measurement, before rates.

Conservative rectangular mass-domain rejection is one-way only: inside an
axis envelope is not a proof of interpolation-hull/width/selection validity.
No missing rate becomes a zero and no null likelihood is evaluated.
"""
import argparse
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
from module13.higgstools import inputs, sha

ROOT=Path(__file__).resolve().parents[3]
HBROOT=Path('/home/amine/Tools/hbdataset')
HSROOT=Path('/home/amine/Tools/hsdataset')
MAP=ROOT/'module14/conditional_scan/production_map_13_14.json'


def dump(path, value):
    path.write_text(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n')


def require(condition, message):
    if not condition:raise ValueError(message)


def saved_cases(dataset):
    """Read original witnesses only. No inverse-family generation or scans."""
    cases=[]
    for name in ('D7','F13'):
        record,w=inputs(name)
        cases.append(dict(id=name,physical=record['input']['physical'],
                          scalar_sha256=record['input_sha256'],
                          witnesses=[dict(id=w['id'],yukawa_sha256=w['yukawa_sha256'])],
                          production_available=['H1:Hpmtb:LHC13','H2:Hpmtb:LHC13']))
    m=json.loads(MAP.read_text());require(sha(dataset)==m['dataset_sha256'],'Frozen D14 dataset changed')
    data=json.loads(Path(dataset).read_text())
    ids=sorted({r['id'] for r in m['rates'] if r['energy_TeV']==13})
    require(len(ids)==16,'Require exactly 16 historical H2 rates')
    for i in ids:
        rows=[r for r in data['rows'] if r['id']==i]
        require(len(rows)==4,'Four original families required')
        fs=[f for f in m['families'] if f['id']==i and f['energy_TeV']==13]
        for r in rows:
            f=next(f for f in fs if f['module2_input_sha256']==r['neutrino']['input_sha256'])
            require(r['scalar_sha256']==f['scalar_sha256'],'Scalar identity mismatch')
            require(r['widths']['yukawa_sha256']==f['yukawa_sha256'],'Decay family identity mismatch')
        cases.append(dict(id=f'D14_{i}',physical=rows[0]['input_card']['physical'],
                          scalar_sha256=rows[0]['scalar_sha256'],
                          witnesses=[dict(id=f"{r['neutrino']['ordering']}_{r['neutrino']['family']}",
                                          module2_input_sha256=r['neutrino']['input_sha256'],
                                          yukawa_sha256=r['widths']['yukawa_sha256']) for r in rows],
                          production_available=['H2:Hpmtb:LHC13']))
    return cases


def mass_assignments(d, case):
    p=case['physical'];cat=d['category'];cl=d['limitClass']
    masses={'h':p['mh1'],'H':p['mh2'],'A':p['ma']} if cat=='neutral' else {'H1':p['mH1'],'H2':p['mH2']}
    g=d['grid_axes']
    if cat=='doubleCharge':return []
    if cl in ('ChannelLimit','ChannelWidthLimit','LikelihoodLimit'):
        return [dict(states=[s],mass=m) for s,m in masses.items()]
    if cl=='PairProductionLimit':
        return [dict(states=[s,t],massFirstParticle=m,massSecondParticle=n)
                for (s,m),(t,n) in itertools.product(masses.items(),repeat=2)
                if not d['equalParticleMasses'] or s==t]
    if cl=='ChainDecayLimit':
        if cat=='WH':
            return [dict(states=[s,t],massMother=m,massDaughter=n)
                    for s,m in masses.items() for t,n in [('h',p['mh1']),('H',p['mh2']),('A',p['ma'])]]
        return [dict(states=[s,t],massMother=m,massDaughter=n)
                for (s,m),(t,n) in itertools.product(masses.items(),repeat=2)]
    if cl=='PairDecayLimit':
        return [dict(states=[s,t,u],massMother=m,massFirstDaughter=n,massSecondDaughter=o)
                for (s,m),(t,n),(u,o) in itertools.product(masses.items(),repeat=3)
                if not d['equalDaughterMasses'] or t==u]
    raise ValueError('Unknown limit class '+cl)


def classify(d, case):
    if d['category']=='doubleCharge':
        return dict(status='NOT_APPLICABLE',reason='No doubly charged Zee particle')
    assignments=mass_assignments(d,case)
    # Bounding-box rejection proves absence; bounding-box inclusion proves nothing.
    candidates=[a for a in assignments if all(k=='width' or k not in a or lo<=a[k]<=hi
                for k,(lo,hi) in d['grid_axes'].items())]
    if not candidates:
        return dict(status='NOT_APPLICABLE',reason='All model mass assignments outside at least one published axis envelope')
    channels=d['process']
    central=[]
    if d['category']=='singleCharge' and isinstance(channels,dict):
        for a in candidates:
            state=a['states'][0]
            if channels.get('channels') and all(prod=='Hpmtb' for prod,dec in channels['channels']):
                if state+':Hpmtb:'+d['collider'] in case['production_available']:central.append(state)
    return dict(status='MISSING_PREDICTION',mass_candidates=candidates,
                central_LO_two_body_inputs_available=central,
                applicability='POTENTIALLY_APPLICABLE; mass-envelope only; constraints/width/interpolation hull still required',
                missing=(['production/decay theory uncertainty and experimental signal-model/width qualification'] if central else
                         ['source-bound '+d['collider']+' process input '+json.dumps(channels,sort_keys=True),
                          'complete branching fractions/total widths at declared accuracy']),
                reason='Central LO charged inputs do not establish a qualified exclusion' if central else 'Required model prediction or qualification absent')


def neutral_requirements(case):
    """Exact thresholds only; open is not a claim of a nonzero vertex/rate."""
    p=case['physical'];mw=80.379;mz=91.1876
    daughters={'h':p['mh1'],'H':p['mh2'],'A':p['ma'],'H1':p['mH1'],'H2':p['mH2']}
    out={}
    for state,key in [('H','mh2'),('A','ma')]:
        mass=p[key];channels=[]
        modes=[('WW',2*mw),('ZZ',2*mz),('tt',2*172.4),('hh',2*p['mh1']),
               ('AA',2*p['ma']),('hZ',p['mh1']+mz),('HZ',p['mh2']+mz),('AZ',p['ma']+mz)]
        modes += [(f'H{i}+ H{j}-',p[f'mH{i}']+p[f'mH{j}']) for i in (1,2) for j in (1,2)]
        modes += [(f'H{i}+ W- and conjugate',p[f'mH{i}']+mw) for i in (1,2)]
        for mode,threshold in modes:
            channels.append(dict(mode=mode,threshold_GeV=threshold,kinematically_open=mass>threshold,
                                 prediction='MISSING_PREDICTION_OR_VERTEX_QUALIFICATION',
                                 warning='Threshold test only; CP/gauge-forbidden terms must be proved zero, not assigned an invented BR'))
        out[state]=dict(mass_GeV=mass,total_width='UNKNOWN',thresholds=channels,
                        missing=['full quark/lepton and LFV widths','loop gg/gamma gamma/Zgamma',
                                 'all nonzero open scalar/vector competition and relevant off-shell channels',
                                 'source-bound ggH/bbH, VBF/VH/ttH and pair/cascade production at exact energies',
                                 'width/interference/acceptance and theory uncertainty qualification'])
    return out


def verify_coverage_sources(coverage):
    import Higgs
    require(sha(next(Path(Higgs.__file__).parent.glob('_Higgs*.so')))==coverage['library_sha256'],'Native library changed since inventory')
    for data in coverage['datasets'].values():
        for name,want in data['files'].items():require(sha(Path(data['path'])/name)==want,'Dataset changed since inventory: '+name)


def inventory(dataset):
    import Higgs
    import Higgs.bounds as HB
    import Higgs.signals as HS
    import importlib.metadata
    old=json.loads((ROOT/'validation/module13/d13_higgstools.json').read_text())
    require(importlib.metadata.version('HiggsTools')=='1.1.3','Wrong library version')
    lib=next(Path(Higgs.__file__).parent.glob('_Higgs*.so'))
    require(sha(lib)==old['library_sha256'],'Pinned native library changed')
    provenance={}
    for kind,root in [('HB',HBROOT),('HS',HSROOT)]:
        files={str(p.relative_to(root)):sha(p) for p in sorted(root.rglob('*.json'))}
        require(files==old['datasets'][kind]['files'],'Pinned dataset bytes changed: '+kind)
        head=subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()
        require(head==old['datasets'][kind]['git_head'],'Dataset commit changed')
        provenance[kind]=dict(path=str(root),git_head=head,files=files,
                              manifest_sha256=hashlib.sha256(json.dumps(files,sort_keys=True).encode()).hexdigest())
    cases=saved_cases(dataset)
    bounds=HB.Bounds(str(HBROOT),HB.LimitOptions(minExpRatio=0.))
    limits=[]
    for lim in sorted(bounds.limits(),key=lambda x:x.id()):
        path=Path(lim.loadedFrom());raw=json.loads(path.read_text());a=raw['analysis']
        axes={k:[min(v),max(v)] for k,v in a.get('grid',{}).items()}
        if 'stackedLlhGrid' in a:
            masses=[x['mass'] for x in a['stackedLlhGrid']];axes['mass']=[min(masses),max(masses)]
        d={k:raw[k] for k in ('id','limitClass','reference','source','collider','experiment','luminosity','process')}
        d.update(file=str(path.relative_to(HBROOT)),sha256=sha(path),
                 source_url='https://gitlab.com/higgsbounds/hbdataset/-/blob/'+provenance['HB']['git_head']+'/'+str(path.relative_to(HBROOT)),
                 category=path.relative_to(HBROOT).parts[0],process_description=lim.processDesc(),
                 extent=lim.extentDesc(),grid_axes=axes,
                 relativeWidth=a.get('relativeWidth'),massResolution=a.get('massResolution'),
                 equalParticleMasses=a.get('equalParticleMasses',False),
                 equalDaughterMasses=a.get('equalDaughterMasses',False),
                 constraints=raw.get('constraints'),normalization=raw.get('normalization'),
                 suppressLimit=raw.get('suppressLimit'),suppressLimitMassRange=raw.get('suppressLimitMassRange'),
                 acceptances=a.get('acceptances'),productionAcceptances=a.get('productionAcceptances'),
                 required_HiggsTools_input='setMass, setTotalWidth; setCxn(collider, production, pb), setBr(decay); chain/pair BR and pairCxn or coupling where process specifies; source metadata retained verbatim',
                 perturbative_order='Experimental bound has no generator order; model LO central only where identified, higher-order/uncertainty qualification missing',
                 width_validity='Explicit width grid where present; otherwise narrow-width/signal-model interpretation requires source qualification',
                 confidence='95% CL observed limit; choose by expected sensitivity; no independent observed-limit shopping')
        d['cases']={c['id']:classify(d,c) for c in cases};limits.append(d)
    signals=HS.Signals(str(HSROOT));measurements=[]
    hsfiles={json.loads(p.read_text())['id']:p for p in HSROOT.rglob('*.json') if 'id' in json.loads(p.read_text())}
    for mm in sorted(signals.measurements(),key=lambda x:x.id()):
        path=hsfiles[mm.id()];raw=json.loads(path.read_text())
        measurements.append(dict(id=mm.id(),reference=mm.reference(),file=str(path.relative_to(HSROOT)),sha256=sha(path),
            source_url='https://gitlab.com/higgsbounds/hsdataset/-/blob/'+provenance['HS']['git_head']+'/'+str(path.relative_to(HSROOT)),
            collider=raw['collider'],referenceMass=raw.get('referenceMass'),referenceModel=raw.get('referenceModel'),
            massResolution=raw.get('massResolution'),subMeasurements=raw['subMeasurements'],
            n_observables=mm.nSubMeasurements(),correlation_source=raw.get('source'),
            status='MISSING_PREDICTION',cases=[c['id'] for c in cases],
            missing=['hZgamma and consistent total width','production/decay accuracy and theory covariance qualification; complete h125 likelihood confidence prescription'],
            supplied='h gamma gamma one-loop calculator; SM-reference effective-coupling production is an approximation, not exact STXS'))
    require(len(limits)==310 and sum(m['n_observables'] for m in measurements)==159,'Dataset inventory changed')
    return dict(status='HIGGS_FULL_COVERAGE_BLOCKED',library_sha256=sha(lib),version='1.1.3',datasets=provenance,
                input_sha256={str(MAP.relative_to(ROOT)):sha(MAP),str(dataset):sha(dataset)},cases=cases,limits=limits,
                heavy_neutral_requirements={c['id']:neutral_requirements(c) for c in cases},
                measurements=measurements,summary={c['id']:dict(Counter(x['cases'][c['id']]['status'] for x in limits)) for c in cases},
                missing_experimental_coverage=[dict(process=p,status='MISSING_EXPERIMENTAL_COVERAGE',reason='No corresponding single-charged topology among the 310 loaded process definitions') for p in ['Hpmtb -> H2 -> H1 Z','Hpmtb -> H2 -> H1 h','Hpmtb -> H1/H2 -> W h/H/A']],
                classification_policy='NOT_APPLICABLE only for absent charge sector or proven outside mass-axis envelope. Potentially applicable missing amplitudes, including loop-only HpmWZ, remain MISSING_PREDICTION. Tree-zero alone is not all-order inapplicability.',
                global_acceptance=None)


def main():
    p=argparse.ArgumentParser();p.add_argument('--dataset',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=False)
    r=inventory(a.dataset)
    # One limit/measurement per line keeps the exhaustive matrix reviewable.
    lines=['{']
    for key,value in r.items():
        encoded='[\n'+',\n'.join(json.dumps(x,sort_keys=True,allow_nan=False) for x in value)+'\n]' if key in ('limits','measurements') else json.dumps(value,sort_keys=True,allow_nan=False)
        lines.append(json.dumps(key)+': '+encoded+',')
    lines[-1]=lines[-1][:-1];lines.append('}')
    (a.out/'COVERAGE.json').write_text('\n'.join(lines)+'\n')
    print('Loaded HB',len(r['limits']),'HS measurements',len(r['measurements']),'observables',sum(m['n_observables'] for m in r['measurements']))
    print(json.dumps(r['summary'],sort_keys=True))

if __name__=='__main__':main()
