"""Validate captured native executions; independent of arithmetic compose()."""
import hashlib
import json
import math
from pathlib import Path
import re
from .run_capture import ROOT, LOCAL, D4_SHA, sha

EXPECTED={
 'P1':['generate q qb > z > hm3c hm2 QCD=0','add process q qb > z > hm3 hm2c QCD=0',
       'add process qb q > z > hm3c hm2 QCD=0','add process qb q > z > hm3 hm2c QCD=0'],
 'P2':['generate g d3 > u3 hm3 QCD=1 QED=1','add process g d3bar > u3bar hm3c QCD=1 QED=1',
       'add process d3 g > u3 hm3 QCD=1 QED=1','add process d3bar g > u3bar hm3c QCD=1 QED=1']}


def run_settings(raw):
    settings={}
    for line in raw.splitlines():
        data=line.split('!')[0].split('#')[0]
        if '=' not in data:continue
        value,key=data.split('=',1);key=key.strip()
        if key in settings:raise ValueError('Duplicate run setting '+key)
        settings[key]=value.strip().strip("'\"")
    return settings


def validate_settings(raw):
    s=run_settings(raw)
    for key,want in {'lpp1':1,'lpp2':1,'ebeam1':6800.,'ebeam2':6800.,'scale':700.,'dsqrt_q2fact1':700.,'dsqrt_q2fact2':700.,'lhaid':263000,'ptheavy':0.,'dsqrt_shat':0.,'dsqrt_shatmax':-1.}.items():
        if float(s[key])!=want:raise ValueError('Run setting mismatch '+key)
    if s['pdlabel']!='lhapdf':raise ValueError('LHAPDF required')
    for key in ['fixed_ren_scale','fixed_fac_scale']:
        if s[key].lower() not in ['true','.true.','t']:raise ValueError('Fixed scale required')
    if s['use_syst'].lower() not in ['false','.false.','f'] or s['systematics_program']!='none':raise ValueError('Unexpected systematics policy')
    if int(s['nevents'])<5000:raise ValueError('Insufficient requested statistics')
    if s.get('custom_fcts',''):raise ValueError('Unexpected custom cut/scale hook')
    for key in ['pt_min_pdg','pt_max_pdg','eta_min_pdg','eta_max_pdg','mxx_min_pdg']:
        if s.get(key,'{}')!='{}':raise ValueError('Unexpected cut '+key)
    return s


def lha_values(raw):
    values={};block=None
    for line in raw.splitlines():
        cols=line.split('#')[0].split()
        if not cols:continue
        if cols[0].upper()=='BLOCK':block=cols[1].upper();continue
        if cols[0].upper()=='DECAY':key=('DECAY',(int(cols[1]),));value=float(cols[2]);block=None
        elif block:
            key=(block,tuple(map(int,cols[:-1])));value=float(cols[-1].replace('D','e'))
        else:continue
        if key in values:raise ValueError('Duplicate LHA entry')
        values[key]=value
    return values


def validate_sources(folder, sources, receipt):
    """Check captured manifests against retained executable source, not just themselves.

    Madevent rewrites run_card.inc, param_card.inc and integration .dat files
    between runs. Their historical manifests remain bound; generated constants
    are checked through the active banner cards; immutable code is rehashed.
    """
    for part,key in [('Source','source_tree_sha256'),('SubProcesses','matrix_tree_sha256')]:
        entries=sources[part]
        digest=hashlib.sha256(json.dumps(entries,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        if not entries or digest!=receipt[key]:raise ValueError('Executable source manifest changed')
        for name,want in entries.items():
            path=(folder/part/name).resolve()
            if not path.is_relative_to((folder/part).resolve()):raise ValueError('Source path outside process')
            if path.suffix not in ('.py','.f','.f90','.inc','.cc','.h') or name in ('run_card.inc','param_card.inc'):continue
            if sha(path)!=want:raise ValueError('Executable source changed '+part+'/'+name)


def validate_one(receipt_path):
    r=json.loads(receipt_path.read_text());process=r['process'];folder=receipt_path.parent
    if r['schema_version']!='d5-native-execution-receipt-1' or r['returncode']!=0:raise ValueError('Execution unsuccessful')
    if r['command'][-1]!='-f' or r['command'][1]!=str(LOCAL/(process+'_full')/'bin/generate_events'):raise ValueError('Unexpected executable')
    if r['input_sha256']['launcher_implementation']!=sha(ROOT/'module8/run_capture.py'):raise ValueError('Launcher implementation changed')
    sources=json.loads((folder/'sources.json').read_text())
    validate_sources(LOCAL/(process+'_full'),sources,r)
    executable=LOCAL/(process+'_full')/'bin/generate_events'
    if sha(executable)!=r['input_sha256'][str(executable.relative_to(LOCAL))]:raise ValueError('Native launcher changed')
    if sha(LOCAL/'MG5_v3.6.7.tar.gz')!=r['source_archive_sha256']:raise ValueError('Generator archive changed')
    if sha(LOCAL/'ufo_audit.json')!=r['input_sha256']['ufo_audit.json']:raise ValueError('Executed UFO audit changed')
    if r['input_sha256']['full_D4_ledger']!=D4_SHA or sha(ROOT/'validation/module7/d4_decay_table.json')!=D4_SHA:raise ValueError('Exact full D4 ledger mismatch')
    if sha(folder/'execution.log')!=r['log_sha256']:raise ValueError('Execution log changed')
    if sha(folder/'results.dat')!=r['native_results_sha256']:raise ValueError('Native result changed')
    for key,digest in r['output_sha256'].items():
        p=(LOCAL/key).resolve()
        if not p.is_relative_to(LOCAL.resolve()) or sha(p)!=digest:raise ValueError('Output artifact changed '+key)
    for key,digest in r['input_sha256'].items():
        if key.startswith('pdf/') and sha(LOCAL/key)!=digest:raise ValueError('PDF grid changed')
    for filename in ['run_card.dat','param_card.dat','proc_card_mg5.dat']:
        key=f'{process}_full/Cards/{filename}'
        if sha(folder/filename)!=r['input_sha256'][key]:raise ValueError('Captured input changed '+filename)
    settings=validate_settings((folder/'normalized_run_card.dat').read_text())
    for filename in ('run_card.dat','param_card.dat'):
        if sha(folder/('normalized_'+filename))!=r['normalized_card_sha256'][f'{process}_full/Cards/{filename}']:
            raise ValueError('Normalized card changed '+filename)
    rawproc=(folder/'proc_card_mg5.dat').read_text().replace('\\\n','')
    lines=[s.strip() for s in rawproc.splitlines() if s.startswith(('generate ','add process '))]
    if lines!=EXPECTED[process]:raise ValueError('Charge/beam/process definition mismatch')
    banners=[LOCAL/key for key in r['output_sha256'] if key.endswith('_banner.txt')]
    if len(banners)!=1:raise ValueError('Require one native event banner')
    banner=banners[0].read_text()
    def tag(name):
        m=re.search('<'+name+'>(.*?)</'+name+'>',banner,re.S)
        if not m:raise ValueError('Missing native banner '+name)
        return m[1].replace('<![CDATA[','').replace(']]>','').strip()
    if tag('MGVersion')!='#3.6.7':raise ValueError('Generator version mismatch')
    active=run_settings(tag('MGRunCard'))
    normalized=run_settings((folder/'normalized_run_card.dat').read_text())
    # Madevent resets the on-disk seed to zero after the run. The banner
    # preserves the actual fixed seed; require it against the captured input.
    original=run_settings((folder/'run_card.dat').read_text())
    if active['iseed']!='4154' or original['iseed']!='4154' or normalized['iseed']!='0':raise ValueError('Run seed provenance mismatch')
    normalized['iseed']=active['iseed']
    if active!=normalized:raise ValueError('Banner run card mismatch')
    if tag('MG5ProcCard').replace('\\\n','')!=rawproc.strip():raise ValueError('Banner process card mismatch')
    params=lha_values(tag('slha'));captured=lha_values((folder/'normalized_param_card.dat').read_text())
    if params!=captured:raise ValueError('Banner parameter card mismatch')
    native=LOCAL/'cards'/f'd2_NO_{r["spectrum"]}_baseline_H2.dat'
    native_key=str(native.relative_to(LOCAL))
    if sha(native)!=r['input_sha256'][native_key]:raise ValueError('Native mapped card changed')
    audit=json.loads((LOCAL/'ufo_audit.json').read_text())
    case=next(c for c in audit['cases'] if c['id']==f'd2_NO_{r["spectrum"]}_baseline/H2')
    if sha(native)!=case['card_sha256']:raise ValueError('Production card not bound to native audit')
    expected=lha_values(native.read_text())
    for code in (1,2,3,4,5):expected[('MASS',(code,))]=0.
    expected[('MASS',(24,))]=80.379;expected[('DECAY',(6,))]=0.
    if params!=expected:raise ValueError('Production parameters differ from independent native mapping')
    for code in (1,2,3,4,5):
        if params[('MASS',(code,))]!=0.:raise ValueError('Require massless 5FS incoming quarks')
    for code in (6,37,9000037):
        if params[('DECAY',(code,))]!=0.:raise ValueError('Require stable hard-process external particles')
    data=[float(x.replace('D','e')) for x in (folder/'results.dat').read_text().splitlines()[0].split()]
    sigma=data[9];error=math.hypot(data[1],data[2]);samples=int(data[3])
    if not all(math.isfinite(x) for x in [sigma,error]) or sigma<=0 or error<=0 or error/sigma>.01 or samples<5000:raise ValueError('Insufficient native integration statistics')
    integrated=float(re.search(r'Integrated weight \(pb\)\s*:\s*(\S+)',tag('MGGenerationInfo'))[1])
    if abs(integrated/sigma-1)>2e-4:raise ValueError('Banner cross section conflicts with native result')
    log=(folder/'execution.log').read_text()
    m=re.search(r'Cross-section\s*:\s*([\deE.+-]+)\s*\+-\s*([\deE.+-]+)\s*pb',log)
    if not m or abs(float(m[1])/sigma-1)>.001 or abs(float(m[2])/error-1)>.001:raise ValueError('Log cross section/error conflict')
    if 'interrupted with error' in log or 'Traceback' in log:raise ValueError('Generator failure in log')
    return {'process':process,'spectrum':r['spectrum'],'sigma_LO_pb':sigma,'integration_error_pb':error,
            'relative_integration_error':error/sigma,'integration_samples':samples,
            'charge_scope':'H2plus_and_H2minus_inclusive','beam_orders':'both explicitly generated',
            'receipt_sha256':sha(receipt_path),'results_sha256':sha(folder/'results.dat'),
            'execution_log_sha256':sha(folder/'execution.log'),'banner_sha256':sha(banners[0]),
            'source_tree_sha256':r['source_tree_sha256'],'matrix_tree_sha256':r['matrix_tree_sha256'],
            'source_manifest_sha256':sha(folder/'sources.json'),
            'input_sha256':r['input_sha256'],'generator_source_archive_sha256':r['source_archive_sha256']}


def validate_all():
    ufo=json.loads((LOCAL/'ufo_audit.json').read_text());matrix=json.loads((LOCAL/'mg_matrix_checks.json').read_text())
    if ufo['status']!='D5_UFO_VERTEX_PASS' or matrix['status']!='D5_INDEPENDENT_MG_MATRIX_CHECK_PASS':raise ValueError('Independent physics gates incomplete')
    if ufo['comparisons']!=5904 or ufo['native_card_count']!=36:raise ValueError('Incomplete native vertex comparisons')
    if json.loads((LOCAL/'native/export.json').read_text())!=ufo['export']:raise ValueError('Native export record changed')
    for name,digest in ufo['export']['source_sha256'].items():
        if sha(ROOT/name)!=digest:raise ValueError('Frozen model source changed')
    if not matrix['P1_analytical_spin_color_normalization_pass'] or not matrix['P2_independent_Dirac_trace_and_gluon_Ward_pass']:raise ValueError('Independent amplitudes incomplete')
    for name,digest in matrix['source_sha256'].items():
        if sha(ROOT/name)!=digest:raise ValueError('Independent matrix source changed')
    for name,digest in ufo['ufo_sha256'].items():
        if sha(Path(ufo['export']['ufo_directory'])/name)!=digest:raise ValueError('Audited UFO changed')
    for name,digest in ufo['source_sha256'].items():
        if sha(ROOT/name)!=digest:raise ValueError('Audited source changed')
    release=json.loads((LOCAL/'release_comparison.json').read_text())
    if release['differences'] or release['compared_files']!=846:raise ValueError('Official release source equivalence not verified')
    rows=[]
    for spectrum,tag in [('source','source'),('mH1_m50p0','low'),('mH1_p50p0','high')]:
        for p in ('P1','P2'):rows.append(validate_one(LOCAL/'receipts'/('d5_v2_'+tag)/p/'receipt.json'))
    analytical_report=json.loads((LOCAL/'partonic_checks.json').read_text())
    for name,digest in analytical_report['source_sha256'].items():
        if sha(ROOT/name)!=digest:raise ValueError('Analytical convolution source changed')
    analytical=analytical_report['results']
    for row in rows:
        if row['process']=='P1':
            mass={'source':300.,'mH1_m50p0':250.,'mH1_p50p0':350.}[row['spectrum']]
            independent=next(x for x in analytical if x['mH1_GeV']==mass)
            deviation=abs(row['sigma_LO_pb']-independent['sigma_Z_only_charge_inclusive_pb'])
            if deviation>5*row['integration_error_pb']+independent['quadrature_difference_pb']:raise ValueError('Independent PDF convolution disagrees')
            row['independent_analytical_pb']=independent['sigma_Z_only_charge_inclusive_pb']
            row['independent_deviation_in_integration_errors']=deviation/row['integration_error_pb']
    return {'schema_version':'d5-real-two-process-1.0.0','status':'D5_EXECUTED_PARTON_LO_RATE_PASS','rates':rows,
            'optional_4FS':{'sigma_LO_pb':None,'reason':'Not executed: separate 4F PDF/mass scheme not configured; overlapping alternative to 5FS, never summed'},
            'full_D4_ledger_sha256':D4_SHA,'ufo_audit_sha256':sha(LOCAL/'ufo_audit.json'),
            'mg_matrix_checks_sha256':sha(LOCAL/'mg_matrix_checks.json'),
            'analytical_convolution_sha256':sha(LOCAL/'partonic_checks.json'),
            'official_release_archive_sha256':sha(LOCAL/'MG5_release_v3.6.7.tar.gz'),
            'label':'LO parton-level reference benchmark; central scales/PDF only; incomplete Zee constraints'}

if __name__=='__main__':
    report=validate_all();(LOCAL/'validated_rates.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');print(report['status'])
