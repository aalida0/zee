"""Archive executed fixed-card data and exact external-source provenance."""
import argparse
import json
from pathlib import Path
import tarfile

from research.full_constraints.higgs.sushi_bridge import (
    ARCHIVE_SHA, ROOT, analysis_gate, dump, sha, validate_rate)
from research.full_constraints.higgs.decays_bridge import assemble_d7
from research.full_constraints.higgs.native_validation import validate


def export(work,out):
    work=work.resolve();out=out.resolve()
    source=work/'SusHi-1.7.0';runs=work/'validated-r2'
    if sha(work.parent/'SusHi-1.7.0.tar.gz')!=ARCHIVE_SHA:raise ValueError('Source archive changed')
    meta=dict(energy_GeV=13000.,beams='pp',units='pb',PDF='MMHT2014lo68cl',PDF_member=0,
              QCD_order='LO',flavours=5,version='1.7.0',archive_sha256=ARCHIVE_SHA,
              ggF_mb_scheme='OS 4.78 GeV',bbH_mb_scheme='MSbar evolved from mb(mb)=4.183 GeV',
              CP_scheme='native A; alpha_SusHi=alpha_native+pi/2',
              ggF_scales='muR=muF=M/2',bbH_scales='muR=M, muF=M/4',
              alpha_s_MZ=.135,alpha_s_evolution='one-loop nf=5, initialized from PDF alpha_s(MZ)',
              EW_corrections=False,ggF_quarks='coherent t,b,c; light u,d,s omission estimated separately',
              PDF_error='symmetric Hessian 68%: half quadrature of 25 +/- member differences',
              scale_error='7-point envelope with ratios muR/muF in [1/2,2] relative to each process central scales; bbH central muR/muF=4',
              source_url='https://sushi.hepforge.org/downloads/SusHi-1.7.0.tar.gz',
              licenses='SusHi physics source has citation/use notice, no top-level license file; no redistribution of sources/binary',
              LoopTools='not required: bundled analytic integrals.f, integrals=2; no external LoopTools linked')
    rows=json.loads((runs/'results.json').read_text())
    for row in rows:validate_rate(row,meta,runs)
    native=json.loads((work/'native_vertices.json').read_text());native_result=validate(native)
    original=json.loads((ROOT/'research/full_constraints/higgs/COVERAGE.json').read_text())
    for key,info in original['datasets'].items():
        for file,digest in info['files'].items():
            if sha(Path(info['path'])/file)!=digest:raise ValueError('Experimental dataset bytes changed')
    bridge_sources={str(p.relative_to(ROOT)):sha(p) for p in sorted((out).glob('*')) if p.suffix in ('.py','.m','.cpp')}
    anysrc=work/'anyhdecay-src';deps=Path('/home/amine/Tools/ScannerS/build/_deps')
    manifest=dict(SusHi=dict(version='1.7.0',archive_sha256=ARCHIVE_SHA,url=meta['source_url'],
                            executable_sha256=sha(source/'bin/sushi.PLAIN'),
                            compiler='GNU Fortran 11.4.0',compatibility_flag='-fallow-argument-mismatch',
                            source_files={str(p.relative_to(source)):sha(p) for p in sorted((source/'src').rglob('*')) if p.suffix in ('.f','.F')}),
                  LHAPDF=dict(version='6.5.3',source_archive_sha256=sha(Path('/home/amine/codes/Herwig/herwigpp/src/LHAPDF-6.5.3.tar.gz')),
                              library_sha256=sha(Path('/home/amine/codes/Herwig/herwigpp/lib/libLHAPDF.so')),
                              license='GPL-3.0; COPYING in source archive'),
                  PDF=dict(name=meta['PDF'],version=3,archive_sha256=sha(work/'MMHT2014lo68cl.tar.gz'),
                           url='https://lhapdfsets.web.cern.ch/lhapdfsets/current/MMHT2014lo68cl.tar.gz',
                           official_archive_matches_all_installed_files=True,
                           installed_files={p.name:sha(p) for p in sorted(Path('/home/amine/codes/Herwig/herwigpp/share/LHAPDF/MMHT2014lo68cl').glob('*'))}),
                  anyHdecay=dict(version='1.1.0',git_commit='137b6991cafcd32770e64b2b5979de80db1e44af',
                                 url='https://gitlab.com/jonaswittbrodt/anyhdecay',license='GPL-3.0 wrapper; component notices retained upstream',
                                 source_archive_sha256=sha(work/'anyhdecay-source.tar'),
                                 HDECAY='6.60 frozen R2HDM routines, with N2HDECAY shared core',
                                 N2HDECAY_git_commit='5233a141a82674f6adf0bce0343a808ee7bf535a',
                                 auxiliary_archives={k:sha(deps/(k+'-subbuild')/(k+'-populate-prefix/src')/a)
                                     for k,a in [('c2hdm_hdecay','chdecay.tar.gz'),('shdecay','shdecay.tar.gz')]},
                                 auxiliary_source_urls={'c2hdm_hdecay':'https://www.itp.kit.edu/~maggie/C2HDM/chdecay.tar.gz',
                                                        'shdecay':'https://www.itp.kit.edu/~maggie/sHDECAY/shdecay.tar.gz'},
                                 library_sha256=sha(work/'anyhdecay-build/lib/libanyhdecay.a'),
                                 frozen_routines={str(p.relative_to(anysrc)):sha(p) for p in anysrc.rglob('*') if p.suffix in ('.f','.f90','.F90','.cpp','.hpp')},
                                 shared_core={p.name:sha(p) for p in (deps/'n2hdecay-src/src').glob('*.f')},
                                 generated_build_routines={p.name:sha(p) for p in (work/'anyhdecay-build/src/libified_hdecay').glob('*.f')},
                                 test_compatibility_flag='CATCH_CONFIG_NO_POSIX_SIGNALS; affects test harness only'),
                  model_sources={p:sha(ROOT/p) for p in ('models/SARAH/ZeeTypeII/ZeeTypeII.m',
                                 'models/SARAH/ZeeTypeII/parameters.m','models/SARAH/ZeeTypeII/particles.m',
                                 'module1/d10_benchmarks.json','validation/module12/d12_benchmarks.json',
                                 'module4/couplings.py','module7/d4_inputs.py','module7/d4_native.py',
                                 'module7/d4_tree_kernels.py','module3/core.py','validation/module7/d4_native_validation.json')},
                  bridge_sources=bridge_sources)
    evidence=dict(status='VALIDATED_SCOPED_LO_PRODUCTION; INCOMPLETE_ZEE_WIDTHS',production_metadata=meta,
                  records=rows,native_vertex_validation=native_result,
                  decays=assemble_d7(work/'anyhdecay-D7.txt'),
                  HiggsTools=analysis_gate(original),
                  reference=dict(executed_LO_pb=10.1171817,shipped_LO_with_NLO_PDF_pb=10.1762262,
                                 alpha_s_LO=.127025994,alpha_s_NLO=.127396078,
                                 alpha_s_order_translated_LO_pb=10.176219401433707,
                                 translated_relative_difference=-6.680832520533642e-7,
                                 caution='Raw 0.58% difference is from one-loop vs NLO alpha_s evolution, not numerical integration. Translation is only an LO reference control.'),
                  exclusions_newly_usable=[],physical_higgs='UNKNOWN',exclusion=None,global_acceptance=None,
                  final_scan_authorized=False,B_status='B_FULL_RATE_BLOCKED',LFV_status='LFV_FULL_COVERAGE_BLOCKED',
                  HEPfit_stream='QUEUED_NOT_EXECUTED')
    files=list(sorted(p for p in runs.iterdir() if p.is_file() and p.name!='results.json'))
    for name in ('build-first.log','build-compat.log','anyhdecay-configure.log','anyhdecay-build.log',
                 'anyhdecay-tests-build.log','anyhdecay-tests-compat-build.log','anyhdecay-tests.log',
                 'anyhdecay-args.json','anyhdecay-D7.txt','native_inputs.json','native_vertices.json','native-r2.log',
                 'shipped-reference-LO.in','shipped-reference-LO.out','shipped-reference-LO.log','study.log'):
        files.append(work/name)
    receipts={('runs/'+p.name if p.parent==runs else p.name):sha(p) for p in files}
    with tarfile.open(out/'SUSHI_RUNS.tar.gz','w:gz') as tar:
        for p in files:tar.add(p,arcname='runs/'+p.name if p.parent==runs else p.name,recursive=False)
    manifest['raw_receipts']=receipts;manifest['raw_archive_sha256']=sha(out/'SUSHI_RUNS.tar.gz')
    dump(out/'SUSHI_SOURCE_MANIFEST.json',manifest)
    evidence['source_manifest_sha256']=sha(out/'SUSHI_SOURCE_MANIFEST.json')
    dump(out/'SUSHI_EVIDENCE.json',evidence)
    print('Archived',len(files),'native receipts;',len(rows),'validated production records; zero complete exclusions')


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--work',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();export(a.work,a.out)
