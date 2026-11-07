"""Bounded saved-card study: finite amplitude and isolated existing rate replay.

All fit/search values are diagnostics until missing theory/input gates close.
The executable never produces a Higgs PASS or a hard physics veto.
"""
import argparse
import io
import json
import math
from pathlib import Path
import unittest
import numpy as np
from module13.higgstools import inputs, h125, applied
from research.full_constraints.higgs.coverage import ROOT, MAP, HBROOT, HSROOT, dump, sha, require, verify_coverage_sources
from research.full_constraints.higgs.diphoton import benchmark, amplitude, MASSES


def serial(value):
    if isinstance(value,dict):return {k:serial(v) for k,v in value.items()}
    if isinstance(value,(list,tuple,np.ndarray)):return [serial(v) for v in value]
    if isinstance(value,(complex,np.complexfloating)):return dict(real=float(value.real),imag=float(value.imag))
    if isinstance(value,np.generic):return value.item()
    return value


def bound_rate(rate, family, row):
    """Exact-card bridge; refuses energy, family, source or charge substitutions."""
    require(rate['energy_TeV']==family['energy_TeV']==13,'Only actual 13 TeV inputs')
    require(rate['id']==family['id']==row['id'],'Scalar ID mismatch')
    require(rate['process']=='pp_tbH2_5FS_gb' and rate['order']=='LO_QCD','Wrong process/order')
    require(rate['charge_definition']=='H2minus_and_H2plus_both_beam_orders_once','Wrong charge sum')
    require(rate['pdf']=='NNPDF30_lo_as_0130_member0_ID263000','Wrong PDF')
    require(rate['sigma_pb']==family['sigma_pb'] and rate['receipt_sha256']==family['receipt_sha256'],'Rate identity mismatch')
    n=row['neutrino'];w=row['widths'];p=row['input_card']['physical']
    require(row['scalar_sha256']==family['scalar_sha256']==w['scalar_sha256'],'Scalar hash mismatch')
    require(n['input_sha256']==family['module2_input_sha256']==w['module2_input_sha256'],'Yukawa witness mismatch')
    require(w['yukawa_sha256']==family['yukawa_sha256'],'Full Yukawa hash mismatch')
    require(p['mH1']==family['mH1_GeV'] and p['mH2']==family['mH2_GeV'] and p['gamma']==family['gamma_rad'] and math.tan(p['beta'])==family['tanbeta'],'Physical card mismatch')
    for label,value in [('muR_GeV',p['mH2']),('muF_GeV',p['mH2'])]:require(rate[label]==value,'Scale mismatch')
    # Check both manifests independently: dictionary merging could hide a
    # conflicting production digest behind an overlapping decay-source key.
    for manifest in (rate['source_sha256'],family['decay_source_sha256']):
        for source,want in manifest.items():require(sha(ROOT/source)==want,'Frozen source changed: '+source)
    t=w['mothers']['H2']['total'];require(t['status']=='D4_COMPLETE_TWO_BODY_BR_PASS' and not t['missing_widths'],'Incomplete two-body decays')
    require(t['total_width_GeV']==family['H2_total_width_GeV'],'Width mismatch')
    require(abs(sum(t['branching_fractions'].values())-1)<1e-12,'BR sum mismatch')
    binding={k:family[k] for k in ['scalar_sha256','module2_input_sha256','yukawa_sha256','mapped_card_sha256','receipt_sha256','energy_TeV']}
    from module14.scan import digest
    require(digest(binding)==family['binding_sha256'],'Family binding changed')
    native=ROOT/'validation/module8/local'/rate['receipt_path']
    native_state='UNAVAILABLE_ON_THIS_CHECKOUT'
    if native.exists():
        require(sha(native)==rate['receipt_sha256'],'Native receipt changed')
        native_state='RECEIPT_HASH_MATCH; nested native artifacts not revalidated by this replay'
    return dict(mass_GeV=p['mH2'],width_GeV=t['total_width_GeV'],BR=t['branching_fractions'],
                sigma_pb=rate['sigma_pb'],integration_error_pb=rate['integration_error_pb'],
                native_receipt_status=native_state,source_binding=family['binding_sha256'])


def charged_replay(bounds,dataset):
    import Higgs.predictions as HP
    m=json.loads(MAP.read_text());require(sha(dataset)==m['dataset_sha256'],'Wrong saved dataset')
    rows=json.loads(Path(dataset).read_text())['rows'];output=[];residual=[]
    rate_index={r['id']:r for r in m['rates'] if r['energy_TeV']==13}
    for f in m['families']:
        if f['energy_TeV']!=13:continue
        row=next(r for r in rows if r['id']==f['id'] and r['neutrino']['input_sha256']==f['module2_input_sha256'])
        inp=bound_rate(rate_index[f['id']],f,row)
        pred=HP.Predictions();h=pred.addParticle(HP.ChargedScalar('H2'));h.setMass(inp['mass_GeV']);h.setTotalWidth(inp['width_GeV'])
        h.setCxn(HP.Collider.LHC13,HP.Production.Hpmtb,inp['sigma_pb'])
        for dec,key in [('tb','t anti-b'),('taunu','tau nu_all'),('enu','e nu_all'),('munu','mu nu_all'),('cs','c anti-s'),('cb','c anti-b')]:h.setBr(getattr(HP.Decay,dec),inp['BR'].get(key,0.))
        result=bounds(pred)
        applications=[applied(v) for v in result.appliedLimits if '/singleCharge/' in v.limit().loadedFrom()]
        # Independent linear interpolation of *absolute* 1D charged limits.
        for v in result.appliedLimits:
            lim=v.limit();d=json.loads(Path(lim.loadedFrom()).read_text())
            ch=d['process'].get('channels',[]) if isinstance(d['process'],dict) else []
            if '/singleCharge/' in lim.loadedFrom() and len(ch)==1 and ch[0][0]=='Hpmtb' and d['limitClass']=='ChannelLimit':
                decay=getattr(HP.Decay,ch[0][1]);signal=inp['sigma_pb']*h.br(decay)
                grid=d['analysis']['grid']['mass'];data=d['analysis']['limit']
                for mode,target in [('observed',v.obsRatio()),('expected',v.expRatio())]:
                    ref=signal/float(np.interp(inp['mass_GeV'],grid,data[mode]))
                    residual.append(abs(ref-target)/max(abs(target),1e-100))
        output.append(dict(id=f['id'],ordering=f['ordering'],family=f['family'],
            scalar_sha256=f['scalar_sha256'],yukawa_sha256=f['yukawa_sha256'],module2_input_sha256=f['module2_input_sha256'],
            receipt_sha256=f['receipt_sha256'],input=inp,width_over_mass=inp['width_GeV']/inp['mass_GeV'],
            selected={k:applied(v) for k,v in result.selectedLimits.items()},applications=applications,
            status='CENTRAL_LO_SUBSET_DIAGNOSTIC',physical_higgs='UNKNOWN',exclusion=None,
            missing=['production scale/PDF and decay theory covariance','signal-model/narrow-width qualification','native production artifacts unavailable where stated','all other applicable processes'],
            global_acceptance=None))
    require(len(output)==64,'Require 16 old scalar rates x 4 original families')
    require(max(residual)<2e-12,'Independent charged-limit interpolation disagrees')
    return dict(rows=output,independent_interpolation_max_relative=max(residual),
                integrations_reused=16,integrations_run=0,energy_TeV=13,
                scope='H2 only, one particle per call. HB default zero for absent processes is NEVER interpreted as coverage or allowedness.')


def h125_diagnostic(name,signals):
    import Higgs.predictions as HP
    record,witness=inputs(name);p=record['input']['physical'];gamma=benchmark(p,witness)
    basepred=HP.Predictions();sm=basepred.addParticle(HP.NeutralScalar('h',HP.CP.even));sm.setMass(p['mh1'])
    HP.effectiveCouplingInput(sm,HP.smLikeEffCouplings,reference=HP.ReferenceModel.SMHiggsEW)
    ref_gamma=sm.br(HP.Decay.gamgam)*sm.totalWidth();ref_z=sm.br(HP.Decay.Zgam)*sm.totalWidth()
    out=[]
    for zratio in (0.,1.,2.):
        pred=HP.Predictions();h125(pred,p,witness)
        h=pred.particle('h')
        before=h.totalWidth();old_gamma=h.br(HP.Decay.gamgam)*before;old_z=h.br(HP.Decay.Zgam)*before
        new_gamma=ref_gamma*gamma['ratio_to_SM'];new_z=ref_z*zratio
        h.setDecayWidth(HP.Decay.gamgam,new_gamma);h.setDecayWidth(HP.Decay.Zgam,new_z)
        target=before-old_gamma-old_z+new_gamma+new_z
        require(math.isclose(h.totalWidth(),target,rel_tol=2e-13),'Width replacement double counts')
        # inv is an inclusive derived channel (ZZ -> 4nu + directInv), not
        # another independent partial width. Summing it would double count.
        total=sum(h.br(d) for key,d in HP.Decay.__members__.items() if key not in ('none','inv'))
        require(abs(total-1)<2e-12,'Partial width sum not normalized')
        out.append(dict(assumed_Zgamma_ratio=zratio,conditional_total_width_GeV=h.totalWidth(),
                        gamma_partial_width_GeV=new_gamma,BR_gamma=h.br(HP.Decay.gamgam),BR_sum=total,
                        chi2_conditional=signals(pred),chi2_SM_reference=signals(basepred),
                        measurements=[dict(id=m.id(),chi2_conditional=m(pred),chi2_SM_reference=m(basepred)) for m in signals.measurements()] if zratio==1 else None))
    return dict(scalar_sha256=record['input_sha256'],yukawa_sha256=witness['yukawa_sha256'],physical=p,
                gamma=serial(gamma),SM_reference_gamma_width_GeV=ref_gamma,SM_reference_Zgamma_width_GeV=ref_z,
                diagnostic_effective_width_study=out,
                interpretation='Fixed missing-Zgamma assumptions are sensitivity controls, not model predictions or confidence tests. gamma width is SMHiggsEW reference rescaled by independently validated LO ratio, not uniformly NLO Zee.',
                status='HIGGS_SCOPED_CHANNEL_VALIDATED; FULL_H125_LIKELIHOOD_UNKNOWN',exclusion=None)


def main():
    p=argparse.ArgumentParser();p.add_argument('--dataset',type=Path,required=True);p.add_argument('--coverage',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=False)
    coverage=json.loads(a.coverage.read_text());require(len(coverage['limits'])==310,'Run full inventory first')
    verify_coverage_sources(coverage)
    from research.full_constraints.higgs import test_higgs
    test_higgs.DATASET=a.dataset
    log=io.StringIO();result=unittest.TextTestRunner(stream=log,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(test_higgs))
    (a.out/'tests.txt').write_text(log.getvalue());require(result.wasSuccessful() and not result.skipped,'Independent tests must pass without skips')
    import Higgs.bounds as HB
    import Higgs.signals as HS
    bounds=HB.Bounds(str(HBROOT),HB.LimitOptions(minExpRatio=0.));signals=HS.Signals(str(HSROOT))
    higgs={name:h125_diagnostic(name,signals) for name in ('D7','F13')}
    replay=charged_replay(bounds,a.dataset)
    files=[*sorted((ROOT/'research/full_constraints/higgs').glob('*.py')),
           ROOT/'research/full_constraints/higgs/SOURCE_MANIFEST.json',
           ROOT/'module4/native_evidence.json',ROOT/'module4/couplings.py',ROOT/'module1/d10_polynomial.py',
           ROOT/'module13/higgstools.py',ROOT/'module3/core.py',ROOT/'module2/interface.py',
           ROOT/'module1/scalar_constraints.py',ROOT/'module1/potential.py',
           ROOT/'module7/d4_inputs.py',ROOT/'module7/d4_decay_table.py',ROOT/'module14/decays.py',
           ROOT/'models/SARAH/ZeeTypeII/ZeeTypeII.m',ROOT/'validation/module13/higgstools_production_inputs.json',
           ROOT/'module1/d10_benchmarks.json',ROOT/'validation/module12/d12_benchmarks.json',MAP]
    external=Path('/home/amine/Tools/higgstools')
    for x in ['src/predictions/CalcHgamgam.cpp','src/predictions/EffectiveCouplings.cpp','include/Higgs/predictions/Basics.hpp','src/predictions/Particle.cpp','src/predictions/ReferenceModels.cpp','src/predictions/data/YR4Brs.cpp']:
        if (external/x).exists():files.append(external/x)
    report=dict(status='HIGGS_FULL_COVERAGE_BLOCKED',date='2026-11-07',scoped_channel='HIGGS_SCOPED_CHANNEL_VALIDATED',
                scoped_exclusion_validated=False,exclusion=None,global_acceptance=None,final_scan_authorized=False,
                sources={str(p):sha(p) for p in files},coverage_sha256=sha(a.coverage),
                library_sha256=coverage['library_sha256'],datasets={k:dict(git_head=v['git_head'],manifest_sha256=v['manifest_sha256']) for k,v in coverage['datasets'].items()},
                tests=dict(run=result.testsRun,failures=len(result.failures),errors=len(result.errors),skips=len(result.skipped),numerical_controls=serial(test_higgs.EVIDENCE)),
                h125=higgs,charged=replay,
                uncertainties=dict(numerical='independent controls only, not a theory error',
                    hgamma_theory_sigma=None,missing='QCD/EW two-loop corrections, physical-input uncertainty/covariance, complete Zgamma and total-width scheme; production scales/PDF and decay uncertainty; finite-width/acceptance transfer'),
                SPheno_full_loop='UNAVAILABLE; never consumed')
    dump(a.out/'HIGGS_VALIDATION.json',report)
    print('Validated tests',result.testsRun,'charged rows',len(replay['rows']),'max r_obs',max(x['observed_ratio'] for r in replay['rows'] for x in r['selected'].values()))
    for name,x in higgs.items():print(name,x['gamma']['ratio_to_SM'],[(r['assumed_Zgamma_ratio'],r['chi2_conditional']) for r in x['diagnostic_effective_width_study']])

if __name__=='__main__':main()
