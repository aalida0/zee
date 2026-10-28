"""Fail-closed D6 native-output validation, distinct from reference arithmetic."""
import hashlib
import json
import math
from pathlib import Path
import re
import tarfile
from .d6_production import ROOT, LOCAL, MG, UFO, PROCESSES, gate, parameter_card
from .run_capture import sha, set_card
from .d6_evolved import evolved_card
from .real_run_validation import run_settings, validate_settings, lha_values


def check(condition,message):
    if not condition:raise ValueError(message)


def validate_one(path):
    r=json.loads(path.read_text());folder=path.parent;kind=r['kind'];process=LOCAL/('d6_'+kind)
    check(r['schema_version']=='d6-native-execution-receipt-1' and r['returncode']==0,'Unsuccessful native execution')
    check(kind in PROCESSES and r['command']==[__import__('sys').executable,str(process/'bin/generate_events'),r['tag'],'-f'],'Unexpected native command')
    scheme={'D5 frozen running-at-700 masses':'frozen700','D4 running-at-muR Yukawa masses; separate mass-scheme diagnostic':'evolved_muR'}.get(r['yukawa_scheme'])
    check(scheme is not None and (scheme=='frozen700' or kind=='A'),'Unspecified Yukawa scheme')
    for name,digest in r['artifacts_sha256'].items():check(sha(folder/name)==digest,'Receipt artifact changed '+name)
    for name,digest in r['output_sha256'].items():
        p=(ROOT/name).resolve();check(p.is_relative_to(LOCAL.resolve()) and sha(p)==digest,'Native artifact changed '+name)
    for name,digest in r['input_sha256'].items():
        # Process cards are historical inputs, checked against captured copies;
        # active process cards belong to the most recent run.
        if '/Cards/' in name:
            filename=Path(name).name
            if filename in ('run_card.dat','param_card.dat','proc_card_mg5.dat'):check(sha(folder/filename)==digest,'Captured card changed')
            continue
        if name in ('module8/d6_capture.py','module8/d6_evolved.py') and sha(ROOT/name)!=digest:
            archive=LOCAL/'d6_executed_launchers'/(digest+'.py')
            check(sha(archive)==digest and archive.read_bytes()==(ROOT/name).read_bytes()+b'\n','Executed launcher archive mismatch')
        else:check(sha(ROOT/name)==digest,'Immutable input changed '+name)
    compiled=r.get('compiled_source_snapshot_sha256',{})
    if kind=='F' and r['spectrum']!='source':check(r['tag'].startswith('d6v3_') and bool(compiled),'Shifted full-pair run needs compiled-source snapshots')
    for name,digest in compiled.items():
        p=(folder/'compiled_sources'/name).resolve()
        check(p.is_relative_to((folder/'compiled_sources').resolve()) and sha(p)==digest,'Compiled source snapshot changed '+name)
    sources=json.loads((folder/'sources.json').read_text())
    # MG compilation generates scalar vector.inc (not a physics interaction).
    # All other executable code must retain its pre-execution hash.
    for part,key in [('Source','source_tree_sha256'),('SubProcesses','matrix_tree_sha256')]:
        entries=sources[part]
        check(bool(entries),'Empty executable source manifest')
        check(hashlib.sha256(json.dumps(entries,sort_keys=True,separators=(',',':')).encode()).hexdigest()==r[key],'Source manifest changed')
        for name,digest in entries.items():
            p=(process/part/name).resolve();check(p.is_relative_to((process/part).resolve()),'Source traversal')
            if p.suffix not in ('.py','.f','.f90','.inc','.cc','.h') or name in ('param_card.inc','run_card.inc'):continue
            if compiled:
                check(part+'/'+name in compiled,'Incomplete compiled-source snapshot')
                if name!='vector.inc' and not p.name.endswith('_optim.f'):check(compiled[part+'/'+name]==digest,'Original source changed during compilation')
            if part=='Source' and name=='vector.inc':
                check(p.read_text().split()==['INTEGER','WARP_SIZE','PARAMETER','(WARP_SIZE=1)','INTEGER','NB_WARP','PARAMETER','(NB_WARP=1)','INTEGER','VECSIZE_MEMMAX','PARAMETER','(VECSIZE_MEMMAX=1)'],'Unexpected compiled vector scheme')
            elif p.name.endswith('_optim.f') and compiled:
                check(part+'/'+name in compiled,'Missing per-run optimized source snapshot')
            else:check(sha(p)==digest,'Retained executable source changed '+str(p))
    proc=(folder/'proc_card_mg5.dat').read_text().replace('\\\n','')
    lines=[s.strip() for s in proc.splitlines() if s.startswith(('generate ','add process '))]
    check(lines==PROCESSES[kind],'Both charges/beam orders required exactly once')
    check('define q = u1 u2 d1 d2 d3' in proc and 'define qb = u1bar u2bar d1bar d2bar d3bar' in proc,'Five-flavor process aliases changed')
    banners=[ROOT/n for n in r['output_sha256'] if n.endswith('_banner.txt')];check(len(banners)==1,'Need one native banner')
    banner=banners[0].read_text()
    def tag(name):
        m=re.search('<'+name+'>(.*?)</'+name+'>',banner,re.S);check(m is not None,'Missing banner '+name)
        return m[1].replace('<![CDATA[','').replace(']]>','').strip()
    check(tag('MGVersion')=='#3.6.7','MG version mismatch')
    check(tag('MG5ProcCard').replace('\\\n','')==proc.strip(),'Banner process mismatch')
    active=run_settings(tag('MGRunCard'));original=run_settings((folder/'run_card.dat').read_text());normalized=run_settings((folder/'normalized_run_card.dat').read_text())
    check(active['iseed']==original['iseed']=='4154' and normalized['iseed']=='0','Seed provenance mismatch')
    normalized['iseed']='4154';check(normalized==active,'Banner run card mismatch')
    # Reuse D5 fixed-energy/PDF/statistics/cut validator, then bind new scales.
    validate_settings(set_card(tag('MGRunCard'),{'scale':700.,'dsqrt_q2fact1':700.,'dsqrt_q2fact2':700.}))
    for k,want in [('scale',r['muR']),('dsqrt_q2fact1',r['muF']),('dsqrt_q2fact2',r['muF'])]:
        check(float(active[k])==want and float(original[k])==want,'Scale mismatch '+k)
    params=lha_values(tag('slha'));captured=lha_values((folder/'normalized_param_card.dat').read_text())
    expected_card=evolved_card(r['spectrum'],r['muR']) if scheme=='evolved_muR' else parameter_card(r['spectrum'])
    check(params==captured==lha_values(expected_card),'Native physical/card/banner mismatch')
    check(lha_values((folder/'param_card.dat').read_text())==params,'Original parameter mismatch')
    data=[float(x.replace('D','e')) for x in (folder/'results.dat').read_text().splitlines()[0].split()]
    sigma=data[9];error=math.hypot(data[1],data[2]);samples=data[3]
    check(all(math.isfinite(x) for x in data) and sigma>0 and 0<error/sigma<.01 and samples>=5000,'Invalid native integration statistics')
    integrated=float(re.search(r'Integrated weight \(pb\)\s*:\s*(\S+)',tag('MGGenerationInfo'))[1]);check(abs(integrated/sigma-1)<2e-4,'Banner sigma mismatch')
    log=(folder/'execution.log').read_text();m=re.search(r'Cross-section\s*:\s*([\deE.+-]+)\s*\+-\s*([\deE.+-]+)\s*pb',log)
    check(m is not None and abs(float(m[1])/sigma-1)<.001 and abs(float(m[2])/error-1)<.001,'Native log rate/error mismatch')
    check('interrupted with error' not in log and 'Traceback' not in log,'Native execution failed')
    return {'kind':kind,'yukawa_scheme':scheme,'spectrum':r['spectrum'],'muR_GeV':r['muR'],'muF_GeV':r['muF'],'sigma_LO_pb':sigma,'integration_error_pb':error,'integration_samples':int(samples),'receipt':str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),'receipt_sha256':sha(path),'banner_sha256':sha(banners[0]),'results_sha256':sha(folder/'results.dat'),'source_tree_sha256':r['source_tree_sha256'],'matrix_tree_sha256':r['matrix_tree_sha256'],'input_sha256':r['input_sha256'],'compiled_source_snapshot_count':len(compiled),'compiled_source_snapshot_tree_sha256':hashlib.sha256(json.dumps(compiled,sort_keys=True,separators=(',',':')).encode()).hexdigest() if compiled else None,'status':'D6_NATIVE_RUN_PASS'}


def validate_all():
    d5=gate()
    check(sha(LOCAL/'MG5_release_v3.6.7.tar.gz')==d5['real_execution_validation']['official_release_archive_sha256'],'Pinned official archive mismatch')
    check(sha(LOCAL/'LHAPDF-6.5.6.tar.gz')==d5['runtime']['LHAPDF_source_archive_sha256'],'LHAPDF source archive mismatch')
    lib='validation/module8/local/lhapdf/lib/libLHAPDF.so'
    check(sha(ROOT/lib)==d5['independent_Z_convolution']['source_sha256'][lib],'LHAPDF library mismatch')
    native=json.loads((LOCAL/'d6_native_checks.json').read_text())
    check(native['status']=='D5_UFO_VERTEX_PASS' and native['comparisons']==5904 and native['native_card_count']==36,'Native vertices incomplete')
    check(native['ufo_sha256']==d5['native_model']['ufo_sha256'],'Native UFO provenance mismatch')
    release=json.loads((LOCAL/'d6_release_checks.json').read_text())
    check(release['compared_files']==827 and release['differences']==[] and release['archive_sha256']==sha(LOCAL/'MG5_release_v3.6.7.tar.gz'),'Official generator check failed')
    compared=0;launcher_checked=False
    with tarfile.open(LOCAL/'MG5_release_v3.6.7.tar.gz') as archive:
        for member in archive.getmembers():
            rel=Path(*Path(member.name).parts[1:])
            if member.isfile() and str(rel)=='bin/mg5_aMC':
                check((MG/rel).read_bytes()==archive.extractfile(member).read(),'Official MG launcher changed');launcher_checked=True
            if not member.isfile() or rel.suffix not in ('.py','.f','.f90','.inc','.cc','.h') or rel.parts[0] not in ('madgraph','aloha','models','Template'):continue
            check((MG/rel).read_bytes()==archive.extractfile(member).read(),'Official executable source changed '+str(rel));compared+=1
    check(compared==827 and launcher_checked,'Official source coverage changed')
    matrix=json.loads((LOCAL/'d6_matrix_checks.json').read_text())
    check(matrix['status']=='D6_INDEPENDENT_TREE_MATRIX_PASS' and len(matrix['flavor_checks'])==234 and len(matrix['graphs'])==26,'Independent graph/flavor checks incomplete')
    for name,digest in matrix['source_sha256'].items():check(sha(name)==digest,'Matrix-check source changed')
    for graph in matrix['graphs']:
        check(len(graph['diagrams']) in (6,8),'Unexpected graph coverage')
        for diagram in graph['diagrams']:
            order=diagram['orders'];check(order.get('QED')==2 and order.get('QCD',0)==order.get('HIG',0)==order.get('HIW',0)==0,'Unexpected tree coupling orders')
    paths=[]
    superseded=[]
    for p in sorted((LOCAL/'d6_receipts').glob('*/receipt.json')):
        r=json.loads(p.read_text())
        if r['kind']=='F' and r['spectrum']!='source' and not r['tag'].startswith('d6v3_'):
            superseded.append({'receipt':str(p.relative_to(ROOT)),'receipt_sha256':sha(p),'reason':'Superseded by fresh execution retaining per-run optimized source; historical results not promoted'})
        else:paths.append(p)
    rows=[validate_one(p) for p in paths]
    expected={(k,s,700.,700.) for k in ['F','Z'] for s in ['source','mH1_m50p0','mH1_p50p0']}
    expected|={('A','source',r,f) for r,f in [(700.,700.),(350.,350.),(350.,700.),(700.,350.),(700.,1400.),(1400.,700.),(1400.,1400.)]}
    expected={(*x,'frozen700') for x in expected}
    expected|={('A','source',q,q,'evolved_muR') for q in (350.,1400.)}
    got=[(r['kind'],r['spectrum'],r['muR_GeV'],r['muF_GeV'],r['yukawa_scheme']) for r in rows]
    check(set(got)==expected and len(got)==len(expected),'Missing/duplicated required native runs')
    for row in rows:
        if row['kind']=='Z' or (row['kind']=='A' and row['muR_GeV']==row['muF_GeV']==700.):
            ref=next(s for s in d5['spectra'] if s['spectrum']==row['spectrum'])['P1' if row['kind']=='Z' else 'P2']
            dev=abs(row['sigma_LO_pb']-ref['sigma_LO_pb'])/math.hypot(row['integration_error_pb'],ref['integration_error_pb'])
            check(dev<5,'D5 central discrepancy blocker');row['D5_deviation_combined_integration_errors']=dev
    return {'schema_version':'d6-real-tree-production-validation-1.0.0','status':'D6_NATIVE_VALIDATION_PASS','superseded_executions':superseded,'rates':rows,'d5_evidence_sha256':sha(ROOT/'validation/module8/d5_production.json'),'d4_ledger_sha256':sha(ROOT/'validation/module7/d4_decay_table.json'),'independent_check_sha256':{n:sha(LOCAL/n) for n in ['d6_native_checks.json','d6_release_checks.json','d6_matrix_checks.json','d6_d5_revalidation.json']}}

if __name__=='__main__':
    r=validate_all();(LOCAL/'d6_validated_rates.json').write_text(json.dumps(r,indent=2,allow_nan=False)+'\n');print(r['status'])
