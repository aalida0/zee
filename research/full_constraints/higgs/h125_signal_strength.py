"""Original-card h125 width ledger and production numerators; no incomplete BRs.

Reuses immutable photon evidence. No loop amplitudes or production are rerun.
The total-width consumer deliberately stays closed until the competing-channel
and uncertainty gates in HIGGS_H125_SIGNAL_STRENGTH_REPORT.md are satisfied.
"""
import json
import math
import tarfile
from pathlib import Path

import numpy as np

from module2.interface import decode
from module3.core import neutral_width, vertices
from module4.couplings import quarks
from module7.d4_inputs import SM
from research.full_constraints.higgs.decays_bridge import read_output, require_complete_width
from research.full_constraints.higgs.sushi_bridge import benchmark, blocks, dump, sha, lo_amplitude, ROOT
from research.full_constraints.higgs.neutral_widths import verify_sources

HERE = Path(__file__).resolve().parent
RECEIPTS = HERE/'h125_receipts'


def signal_strength(width, production_ratio, decay_ratio, sm_total):
    total = require_complete_width(width)
    if any(x is None or not math.isfinite(x) or x < 0 for x in (production_ratio, decay_ratio, sm_total)):
        raise ValueError('MISSING_PREDICTION: finite matched production/decay/reference required')
    return production_ratio*decay_ratio*sm_total/total


def calculate():
    manifest=json.loads((HERE/'SUSHI_SOURCE_MANIFEST.json').read_text())
    verify_sources(manifest)
    with tarfile.open(HERE/'SUSHI_RUNS.tar.gz') as archive:
        data=archive.extractfile('anyhdecay-D7.txt').read()
    import hashlib
    assert hashlib.sha256(data).hexdigest()==manifest['raw_receipts']['anyhdecay-D7.txt']
    raw_d7=dict((k,float(v)) for k,v in (line.split() for line in data.decode().splitlines()))
    f13=HERE/'neutral_receipts/anyhdecay-F13.stdout'
    assert sha(f13)==json.loads((HERE/'neutral_receipts/F13_EXECUTION.json').read_text())['stdout_sha256']
    execution=json.loads((RECEIPTS/'EXECUTION.json').read_text())
    for path,digest in execution['external_source_sha256'].items():
        if sha(path)!=digest:raise ValueError('Pinned external source changed: '+path)
    smraw=read_output(RECEIPTS/'sm125.stdout')
    sm_old={k:smraw['w_H']*smraw['b_H_'+k] for k in ('bb','cc','ss','gg','WW','ZZ')}
    sm_qcd={k:smraw['corrected_w_H']*smraw['corrected_b_H_'+k] for k in sm_old}
    photon=json.loads((HERE.parent/'HIGGS_VALIDATION.json').read_text())['h125']
    z=json.loads((HERE/'ZGAMMA_H125_EVIDENCE.json').read_text())
    results=[]
    prod_sm=blocks(RECEIPTS/'SM_h125.out')
    assert prod_sm['sushi'][2]==11 and prod_sm['sushi'][4]==13000
    mc_prod=prod_sm['internalmasses'][40]
    sm_amp,_=lo_amplitude(125.,'even',1.,1.,mc=mc_prod)
    sm_ledger=dict(sm_qcd)
    for i,f in enumerate(('e','mu','tau')):
        C=np.diag(np.asarray(SM['lepton_masses'])/SM['EW']['v'])
        sm_ledger[f+f]=neutral_width(C,125.,i,i,SM['lepton_masses'])
    for f,m in (('u',.00216),('d',.00470)):
        sm_ledger[f+f]=3*125/(8*math.pi)*(m/SM['EW']['v'])**2*(1-4*m*m/125**2)**1.5
    sm_ledger['gammagamma']=photon['D7']['gamma']['SM']['width_GeV']
    sm_ledger['Zgamma']=z['SM_all_nine']['width_GeV']
    sm_sum=math.fsum(sm_ledger.values())
    for name,raw in (('D7',raw_d7),('F13',read_output(f13))):
        r,w=benchmark(name);p=r['input']['physical'];M=p['mh1']
        ku=quarks(p['v'],'top',p)['h'].real
        kd=quarks(p['v'],'bottom',p)['h'].real
        kv=math.cos(p['beta']-p['alpha'])
        C=vertices(decode(w['yukawas']['D']),p,SM['lepton_masses'])['h'][0]
        widths={k:raw['w_Hl']*raw['b_Hl_'+k] for k in sm_qcd}
        # Native HDECAY charm input is m_c(3 GeV), not m_c(m_c).
        # Its charm/top ratio is 1 for both SM and this Type-II h. Use the
        # separately executed corrected SM charm channel with the exact ku².
        assert math.isclose(widths['cc']/sm_old['cc'],ku**2,rel_tol=1e-10)
        old_cc=widths['cc'];widths['cc']=sm_qcd['cc']*ku**2
        for mode in ('WW','ZZ'):
            assert math.isclose(widths[mode]/sm_old[mode],kv**2,rel_tol=1e-10)
        for i,a in enumerate(('e','mu','tau')):
            for j,b in enumerate(('e','mu','tau')):
                if j<i:continue
                widths[a+b]=neutral_width(C,M,i,j,SM['lepton_masses'])*(2 if i!=j else 1)
        for f,m in (('u',.00216),('d',.00470)):
            widths[f+f]=sm_ledger[f+f]*(ku if f=='u' else kd)**2
        zg=next(row for row in z['cases'] if row['name']==name)
        assert zg['scalar_sha256']==r['input_sha256'] and zg['yukawa_sha256']==w['yukawa_sha256']
        assert photon[name]['scalar_sha256']==r['input_sha256'] and photon[name]['yukawa_sha256']==w['yukawa_sha256']
        widths['gammagamma']=photon[name]['gamma']['full']['width_GeV']
        widths['Zgamma']=zg['full']['width_GeV']
        prod=blocks(RECEIPTS/(name+'_h125.out'))
        assert prod['sushi'][2]==11 and prod['sushi'][4]==13000
        assert prod['internalmasses'][40]==mc_prod
        amp,terms=lo_amplitude(M,'even',ku,kd,mc=mc_prod)
        ratios={proc:prod[key][1]/prod_sm[key][1] for proc,key in (('ggF','sushiggh'),('bbH','sushibbh'))}
        assert math.isclose(ratios['ggF'],abs(amp/sm_amp)**2,rel_tol=3e-7)
        assert math.isclose(ratios['bbH'],kd**2,rel_tol=3e-7)
        ratios.update(VBF=kv**2,WH_DY=kv**2,ZH_DY=kv**2,ttH=ku**2,ZH_inclusive=None)
        ledger_sum=math.fsum(widths.values())
        missing=['Coherent virtual-heavy-scalar contributions to h125 -> W(*)ff, Z(*)ff, four fermions, and interference with retained WW*/ZZ*; no certified numerical materiality bound',
                 'Leading loop h125 -> nu nu from radiative Majorana sector: no native finite-mass numerical bound in this ledger',
                 'Source-matched decay/production truncation and parametric covariance, including Zee EW/scalar effects; theory_sigma not established']
        width=dict(status='INCOMPLETE',partial_widths_GeV=widths,known_channel_sum_GeV=ledger_sum,
                   missing=missing,total_width_GeV=None,branching_fractions=None,theory_sigma=None)
        try: signal_strength(width,ratios['VBF'],kv**2,sm_sum)
        except ValueError as error: rejection=str(error)
        else: raise RuntimeError('Incomplete width was accepted')
        numerators={key:ratios[prodmode]*widths[dec]/sm_ledger[dec] for key,prodmode,dec in
                    (('ggF_gammagamma','ggF','gammagamma'),('VBF_WW','VBF','WW'),('VBF_bb','VBF','bb'))}
        results.append(dict(name=name,scalar_sha256=r['input_sha256'],yukawa_sha256=w['yukawa_sha256'],
            physical=p,couplings=dict(ku=ku,kd=kd,kV=kv,leptons=[dict(real=float(x.real),imag=float(x.imag)) for x in np.diag(C)*p['v']/SM['lepton_masses']]),
            width=width,lfv_both_charge_sum_GeV=sum(widths[x] for x in ('emu','etau','mutau')),
            charm_scheme_correction_GeV=widths['cc']-old_cc,
            production_ratios=ratios,production_pb={k:prod[b][1] for k,b in (('ggF','sushiggh'),('bbH','sushibbh'))},
            ggF_charm_pole_mass_GeV=mc_prod,ggF_coherent_t_b_c_ratio=abs(amp/sm_amp)**2,ggF_incoherent_ratio=sum(abs(x)**2 for x in terms)/sum(abs(x)**2 for x in lo_amplitude(M,'even',1.,1.,mc=mc_prod)[1]),
            signal_strength_numerators=numerators,signal_strengths={k:None for k in numerators},
            width_independent_signal_strength_ratios={
                'VBF_gammagamma_over_VBF_WW': widths['gammagamma']/sm_ledger['gammagamma']/(kv**2),
                'VBF_Zgamma_over_VBF_WW': widths['Zgamma']/sm_ledger['Zgamma']/(kv**2),
                'ggF_gammagamma_over_VBF_WW': numerators['ggF_gammagamma']/numerators['VBF_WW']},
            total_ratio=None,consumer_rejection=rejection,
            positive_extra_width_for_1pct_denominator_suppression_GeV=ledger_sum/99,
            signed_width_budget_for_1pct_linear_precision_GeV=.01*ledger_sum,
            scalar_thresholds_GeV={k:p[k] for k in ('mh2','ma','mH1','mH2')},
            neutrinos=dict(tree_width_GeV=0.,reason='No right-handed neutrino or renormalizable neutral h nu nu Yukawa; massless-neutrino tree order only',leading_loop_width_GeV=None),
            status='H125_TOTAL_WIDTH_QUALIFICATION_BLOCKED'))
    coverage=json.loads((HERE/'COVERAGE.json').read_text())
    category_path=Path(coverage['datasets']['HS']['path'])/'h125/bb_vbfH_LHC13_ATLAS_126.json'
    assert sha(category_path)==coverage['datasets']['HS']['files']['h125/bb_vbfH_LHC13_ATLAS_126.json']
    category=json.loads(category_path.read_text())
    assert category['collider']=='LHC13' and category['id']==201108280
    assert category['subMeasurements']['vbfH_bb']['process']['channels']==[['vbfH','bb']]
    import Higgs
    import Higgs.predictions as HP
    assert sha(next(Path(Higgs.__file__).parent.glob('_Higgs*.so')))==coverage['library_sha256']
    ref=HP.SMHiggsEW(125.)
    rate=ref.cxn(HP.Collider.LHC13,HP.Production.vbfH)*ref.br(HP.Decay.bb)
    sources={str(f.relative_to(ROOT)):sha(f) for f in [HERE/'SUSHI_SOURCE_MANIFEST.json',HERE/'ZGAMMA_H125_EVIDENCE.json',HERE.parent/'HIGGS_VALIDATION.json',HERE/'h125_sm_reference.cpp',HERE/'test_h125_signal_strength.py',HERE/'COVERAGE.json',Path(__file__),*sorted(RECEIPTS.glob('*'))] if f.is_file()}
    return dict(status='H125_SIGNAL_STRENGTH_BLOCKED',cases=results,source_sha256=sources,
                matched_SM_ledger_GeV=sm_ledger,matched_SM_known_sum_GeV=sm_sum,
                mc_at_mc_GeV=1.273,converted_mc3_GeV=smraw['converted_mc3'],
                experimental_category=dict(id=201108280,status='DATA_NORMALIZATION_VALIDATED_MODEL_COMPARISON_BLOCKED',file=str(category_path),dataset_sha256=sha(category_path),pinned_observed_sigma_BR_pb=category['subMeasurements']['vbfH_bb']['obs'],native_SM_reference_sigma_BR_pb=rate,paper_observed_mu=.99,paper_sigma_BR_pb=2.16,paper='https://arxiv.org/html/2011.08280v2',location='Table 6 and results paragraph',normalization='No ref key: JsonSupport.cpp readRateMeasurement defaults to absolute reference-particle process rate; observed 2.16 has pb units, not dimensionless mu',HiggsSignals_calls=0),
                production=dict(energy_GeV=13000,ggF='SusHi 1.7.0 LO QCD massive coherent t,b,c; MMHT2014lo68cl; OS mb=4.78; scales M/2',bbH='LO 5FS same PDF; MSbar mb(mb)=4.183; scales (M,M/4)',VBF_WH_DY_ZH_DY_ttH='Tree EW Lorentz structures; QCD factorizing ratios; no BSM EW corrections; inclusive ZH unavailable'),
                HiggsSignals_comparison='UNKNOWN',exclusion=None,global_acceptance=None,final_scan_authorized=False)


if __name__=='__main__':
    dump(HERE/'H125_SIGNAL_STRENGTH_EVIDENCE.json',calculate())
