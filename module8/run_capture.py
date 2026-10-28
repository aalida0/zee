"""Independent native-run capture. Never accepts user-supplied cross sections.

Creates an integrity receipt from a subprocess this launcher actually executed.
A receipt is not an independent partonic physics validation or a rate PASS.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
LOCAL=ROOT/'validation/module8/local'
D4_SHA='4845f9e1e050c92cbffd4705a1edfc66d6b8b210a8ee5bc0613ed6a42a40e4e9'


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def tree_digest(path):
    entries={str(p.relative_to(path)):sha(p) for p in sorted(path.rglob('*'))
             if p.is_file() and not p.is_symlink() and p.suffix in ('.py','.f','.f90','.inc','.cc','.h','.dat')
             and '__pycache__' not in p.parts}
    raw=json.dumps(entries,sort_keys=True,separators=(',',':')).encode()
    return hashlib.sha256(raw).hexdigest(),entries


def set_card(raw, settings):
    for name,value in settings.items():
        pattern=r'(?m)^\s*[^\n!]*?=\s*'+re.escape(name)+r'\b[^\n]*$'
        raw,n=re.subn(pattern,f' {value} = {name} ! D5 explicit',raw)
        if n==0:raw+=f'\n {value} = {name} ! D5 explicit\n'
        if n>1:raise ValueError('Repeated run setting '+name)
    return raw


def execute(process,spectrum,tag):
    if process not in ('P1','P2') or spectrum not in ('source','mH1_m50p0','mH1_p50p0'):
        raise ValueError('Unsupported D5 process or spectrum')
    if not re.fullmatch(r'[a-zA-Z0-9_]+',tag):raise ValueError('Invalid run tag')
    audit=json.loads((LOCAL/'ufo_audit.json').read_text())
    if audit['status']!='D5_UFO_VERTEX_PASS':raise ValueError('Native UFO gate not PASS')
    if audit['comparisons']!=5904 or audit['native_card_count']!=36:raise ValueError('Incomplete native gate')
    ufo=Path(audit['export']['ufo_directory'])
    for name,digest in audit['ufo_sha256'].items():
        if sha(ufo/name)!=digest:raise ValueError('UFO changed '+name)
    for name,digest in audit['source_sha256'].items():
        if sha(ROOT/name)!=digest:raise ValueError('Audit implementation/input changed '+name)
    d4=ROOT/'validation/module7/d4_decay_table.json'
    if sha(d4)!=D4_SHA:raise ValueError('Full exact D4 ledger changed')
    folder=LOCAL/(process+'_full')
    if (folder/'Events'/tag).exists():raise ValueError('Refuse existing run')
    card=LOCAL/'cards'/f'd2_NO_{spectrum}_baseline_H2.dat'
    raw=card.read_text()
    # 5FS incoming light/b quarks massless, Yukawas kept independent at Q=700.
    in_mass=False;lines=[]
    for line in raw.splitlines():
        cols=line.split('#')[0].split()
        if cols and cols[0].upper()=='BLOCK':in_mass=cols[1].upper()=='MASS'
        if cols and cols[0].upper()=='DECAY':
            in_mass=False
            if int(cols[1])==6:line='DECAY 6 0.0 # stable hard-process top'
        if in_mass and cols and cols[0].isdigit() and int(cols[0]) in (1,2,3,4,5):
            line=f' {cols[0]} 0.0 # D5 massless incoming 5FS; independent Yukawa'
        lines.append(line)
        if cols and cols[0].upper()=='BLOCK' and cols[1].upper()=='MASS':
            # MW is a dependent UFO parameter; Madevent still requires its
            # computed MASS entry in the LHE card. It is not a new external.
            lines.append(' 24 8.037900000000000e1 # dependent MWm, independently closed')
    (folder/'Cards/param_card.dat').write_text('\n'.join(lines)+'\n')
    settings={'ebeam1':6800.,'ebeam2':6800.,'nevents':5000,'iseed':4154,
        'pdlabel':"'lhapdf'",'lhaid':263000,'fixed_ren_scale':'.true.',
        'fixed_fac_scale':'.true.','scale':700.,'dsqrt_q2fact1':700.,'dsqrt_q2fact2':700.,
        'use_syst':'False','systematics_program':"'none'",'ptheavy':0.}
    run_card=folder/'Cards/run_card.dat'
    raw_run=re.sub(r'(?m)^.*=\s*(req_acc|nocut)\b[^\n]*\n?', '',run_card.read_text())
    run_card.write_text(set_card(raw_run,settings))
    config=folder/'Cards/me5_configuration.txt'
    with config.open('a') as f:
        f.write(f'\nlhapdf = {LOCAL}/lhapdf/bin/lhapdf-config\nnb_core = 2\nrun_mode = 0\nautomatic_html_opening = False\nnotification_center = False\n')
    before={str(p.relative_to(LOCAL)):sha(p) for p in [d4,card,LOCAL/'ufo_audit.json'] if p.is_relative_to(LOCAL)}
    before['full_D4_ledger']=sha(d4)
    before['launcher_implementation']=sha(Path(__file__))
    for p in (folder/'Cards').glob('*'):
        if p.is_file():before[str(p.relative_to(LOCAL))]=sha(p)
    pdf=LOCAL/'pdf/NNPDF30_lo_as_0130'
    for p in pdf.glob('*'):before[str(p.relative_to(LOCAL))]=sha(p)
    executable=folder/'bin/generate_events';before[str(executable.relative_to(LOCAL))]=sha(executable)
    source_hash,source_entries=tree_digest(folder/'Source')
    matrix_hash,matrix_entries=tree_digest(folder/'SubProcesses')
    receipt_dir=LOCAL/'receipts'/tag/process;receipt_dir.mkdir(parents=True)
    for filename in ('run_card.dat','param_card.dat','proc_card_mg5.dat'):
        (receipt_dir/filename).write_bytes((folder/'Cards'/filename).read_bytes())
    (receipt_dir/'sources.json').write_text(json.dumps({'Source':source_entries,'SubProcesses':matrix_entries},sort_keys=True))
    env=os.environ.copy();env['LHAPDF_DATA_PATH']=str(LOCAL/'pdf')
    env['LD_LIBRARY_PATH']=str(LOCAL/'lhapdf/lib')+':'+env.get('LD_LIBRARY_PATH','')
    env['BROWSER']='true'
    command=[sys.executable,str(executable),tag,'-f']
    log=receipt_dir/'execution.log';start=time.time()
    with log.open('w') as out:completed=subprocess.run(command,cwd=folder,env=env,stdout=out,stderr=subprocess.STDOUT)
    native_result=folder/'SubProcesses/results.dat'
    if native_result.exists():
        (receipt_dir/'results.dat').write_bytes(native_result.read_bytes())
    for filename in ('run_card.dat','param_card.dat'):
        (receipt_dir/('normalized_'+filename)).write_bytes((folder/'Cards'/filename).read_bytes())
    after={str(p.relative_to(LOCAL)):sha(p) for p in [folder/'Cards/param_card.dat',run_card]}
    artifacts={str(p.relative_to(LOCAL)):sha(p) for base in [folder/'Events'/tag,folder/'HTML'/tag]
               for p in base.rglob('*') if p.is_file()}
    result={'schema_version':'d5-native-execution-receipt-1','status':'EXECUTED_OUTPUT_UNVALIDATED',
            'process':process,'spectrum':spectrum,'command':command,'returncode':completed.returncode,
            'wall_seconds':time.time()-start,'input_sha256':before,'output_sha256':artifacts,
            'normalized_card_sha256':after,
            'source_tree_sha256':source_hash,'matrix_tree_sha256':matrix_hash,'log_sha256':sha(log),
            'native_results_sha256':sha(receipt_dir/'results.dat') if (receipt_dir/'results.dat').exists() else None,
            'physics_rate_pass':False,'source_archive_sha256':sha(LOCAL/'MG5_v3.6.7.tar.gz'),
            'generator_version':(LOCAL/'mg5amcnlo-mg5amcnlo-0e6c945/VERSION').read_text(),
            'widths':'stable external charged scalars and top; other defaults as captured in card',
            'pdf_policy':'NNPDF30_lo_as_0130 member0 ID263000; PDF alpha_s; no scale/PDF uncertainty evaluated',
            'energy_GeV_per_beam':6800.,'scales_GeV':700.,'all_cuts_disabled':True}
    (receipt_dir/'receipt.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'returncode':completed.returncode,'receipt':str(receipt_dir/'receipt.json')}))
    return completed.returncode


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('process',choices=['P1','P2']);p.add_argument('spectrum');p.add_argument('tag')
    a=p.parse_args();return execute(a.process,a.spectrum,a.tag)

if __name__=='__main__':raise SystemExit(main())
