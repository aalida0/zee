"""Isolated D6 tree production: immutable D5 inputs, fresh MG5 outputs only."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from .run_capture import ROOT, LOCAL, sha, tree_digest, set_card, D4_SHA
from .real_run_validation import EXPECTED as D5_PROCESSES

D5_BASE='e15e9badb8be8be848b1ec8737977086f5ba8e20'
UFO=LOCAL/'native/sarah/ZeeTypeII/EWSB/UFO'
MG=LOCAL/'MG5_aMC_v3_6_7'
ORDERS=' QCD=0 QED=2 HIG=0 HIW=0'
PROCESSES={
 'F':[s.replace(' > z > ',' > ').replace(' QCD=0',ORDERS) for s in D5_PROCESSES['P1']],
 'Z':[s.replace(' QCD=0',ORDERS) for s in D5_PROCESSES['P1']],
 'A':D5_PROCESSES['P2']}

def gate():
    d5=ROOT/'validation/module8/d5_production.json'
    pinned=subprocess.check_output(['git','show',D5_BASE+':validation/module8/d5_production.json'],cwd=ROOT)
    if d5.read_bytes()!=pinned:raise ValueError('D5 evidence changed')
    d=json.loads(pinned);a=json.loads((LOCAL/'ufo_audit.json').read_text())
    if sha(LOCAL/'ufo_audit.json')!=d['native_model']['raw_evidence_sha256']:raise ValueError('D5 UFO audit changed')
    for name,want in d['source_sha256'].items():
        if sha(ROOT/name)!=want:raise ValueError('Frozen source changed '+name)
    for name,want in a['ufo_sha256'].items():
        if sha(UFO/name)!=want:raise ValueError('UFO changed '+name)
    for s in d['spectra']:
        card=LOCAL/'cards'/f'd2_NO_{s["spectrum"]}_baseline_H2.dat'
        want=next(c['card_sha256'] for c in a['cases'] if c['id']==f'd2_NO_{s["spectrum"]}_baseline/H2')
        if sha(card)!=want:raise ValueError('Native card changed')
    for name,want in d['spectra'][0]['P1']['input_sha256'].items():
        if name.startswith('pdf/') and sha(LOCAL/name)!=want:raise ValueError('PDF changed')
    if sha(LOCAL/'MG5_v3.6.7.tar.gz')!=d['spectra'][0]['P1']['generator_source_archive_sha256']:raise ValueError('MG archive changed')
    if not re.search(r'^version = 3\.6\.7$',(MG/'VERSION').read_text(),re.M):raise ValueError('MG version changed')
    return d

def generate():
    gate()
    commands=['set auto_update 0','set automatic_html_opening False','set notification_center False',
      'set lhapdf '+str(LOCAL/'lhapdf/bin/lhapdf-config'),'import model '+str(UFO)+' -modelname',
      'define q = u1 u2 d1 d2 d3','define qb = u1bar u2bar d1bar d2bar d3bar']
    for kind in PROCESSES:
        folder=LOCAL/('d6_'+kind)
        if folder.exists():raise ValueError('Refuse existing process '+str(folder))
        commands+=PROCESSES[kind]+['output '+str(folder)]
    commands+=['quit'];path=LOCAL/'d6_generate.txt';path.write_text('\n'.join(commands)+'\n')
    with (LOCAL/'d6_generate.log').open('x') as log:
        p=subprocess.run([sys.executable,str(MG/'bin/mg5_aMC'),str(path)],cwd=LOCAL,stdout=log,stderr=subprocess.STDOUT)
    if p.returncode:raise RuntimeError('MG generation failed')


def parameter_card(spectrum):
    raw=(LOCAL/'cards'/f'd2_NO_{spectrum}_baseline_H2.dat').read_text()
    in_mass=False;lines=[]
    for line in raw.splitlines():
        cols=line.split('#')[0].split()
        if cols and cols[0].upper()=='BLOCK':in_mass=cols[1].upper()=='MASS'
        if cols and cols[0].upper()=='DECAY':
            in_mass=False
            if int(cols[1])==6:line='DECAY 6 0.0 # stable top'
        if in_mass and cols and cols[0].isdigit() and int(cols[0]) in (1,2,3,4,5):line=f' {cols[0]} 0.0 # massless 5FS; independent frozen Yukawa'
        lines.append(line)
        if cols and cols[0].upper()=='BLOCK' and cols[1].upper()=='MASS':lines.append(' 24 8.037900000000000e1 # dependent MW')
    return '\n'.join(lines)+'\n'


def execute(kind,spectrum,mur=700.,muf=700.):
    gate()
    if kind not in PROCESSES or spectrum not in ('source','mH1_m50p0','mH1_p50p0'):raise ValueError('Unsupported process/spectrum')
    if mur not in (350.,700.,1400.) or muf not in (350.,700.,1400.):raise ValueError('Unsupported scales')
    if kind!='A' and (mur,muf)!=(700.,700.):raise ValueError('Mixed pair central only')
    tag=f'd6_{kind}_{spectrum}_{int(mur)}_{int(muf)}';folder=LOCAL/('d6_'+kind)
    receipt_dir=LOCAL/'d6_receipts'/tag
    if receipt_dir.exists() or (folder/'Events'/tag).exists():raise ValueError('Refuse existing run')
    receipt_dir.mkdir(parents=True)
    (folder/'Cards/param_card.dat').write_text(parameter_card(spectrum))
    settings={'ebeam1':6800.,'ebeam2':6800.,'nevents':5000,'iseed':4154,
        'pdlabel':"'lhapdf'",'lhaid':263000,'fixed_ren_scale':'.true.','fixed_fac_scale':'.true.',
        'scale':mur,'dsqrt_q2fact1':muf,'dsqrt_q2fact2':muf,
        'use_syst':'False','systematics_program':"'none'",'ptheavy':0.}
    run_card=folder/'Cards/run_card.dat'
    raw=re.sub(r'(?m)^.*=\s*(req_acc|nocut)\b[^\n]*\n?', '',run_card.read_text())
    run_card.write_text(set_card(raw,settings))
    config=folder/'Cards/me5_configuration.txt'
    with config.open('a') as f:f.write(f'\nlhapdf = {LOCAL}/lhapdf/bin/lhapdf-config\nnb_core = 2\nrun_mode = 0\nautomatic_html_opening = False\nnotification_center = False\n')
    inputs={str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'validation/module8/d5_production.json',ROOT/'validation/module7/d4_decay_table.json',Path(__file__),LOCAL/'ufo_audit.json',LOCAL/'cards'/f'd2_NO_{spectrum}_baseline_H2.dat',LOCAL/'MG5_v3.6.7.tar.gz',LOCAL/'MG5_release_v3.6.7.tar.gz']}
    for base in [folder/'Cards',LOCAL/'pdf/NNPDF30_lo_as_0130',UFO]:
        for p in base.glob('*'):
            if p.is_file() and p.suffix!='.pkl':inputs[str(p.relative_to(ROOT))]=sha(p)
    executable=folder/'bin/generate_events';inputs[str(executable.relative_to(ROOT))]=sha(executable)
    source_hash,source_entries=tree_digest(folder/'Source');matrix_hash,matrix_entries=tree_digest(folder/'SubProcesses')
    for filename in ('run_card.dat','param_card.dat','proc_card_mg5.dat'):(receipt_dir/filename).write_bytes((folder/'Cards'/filename).read_bytes())
    (receipt_dir/'sources.json').write_text(json.dumps({'Source':source_entries,'SubProcesses':matrix_entries},sort_keys=True))
    env=os.environ.copy();env['LHAPDF_DATA_PATH']=str(LOCAL/'pdf');env['LD_LIBRARY_PATH']=str(LOCAL/'lhapdf/lib')+':'+env.get('LD_LIBRARY_PATH','');env['BROWSER']='true';env['PYTHONDONTWRITEBYTECODE']='1'
    command=[sys.executable,str(executable),tag,'-f'];log=receipt_dir/'execution.log';start=time.time()
    with log.open('w') as out:p=subprocess.run(command,cwd=folder,env=env,stdout=out,stderr=subprocess.STDOUT)
    result=folder/'SubProcesses/results.dat'
    if result.exists():(receipt_dir/'results.dat').write_bytes(result.read_bytes())
    for filename in ('run_card.dat','param_card.dat'):(receipt_dir/('normalized_'+filename)).write_bytes((folder/'Cards'/filename).read_bytes())
    artifacts={str(p.relative_to(ROOT)):sha(p) for base in [folder/'Events'/tag,folder/'HTML'/tag] for p in base.rglob('*') if p.is_file()}
    r={'schema_version':'d6-native-execution-receipt-1','kind':kind,'spectrum':spectrum,'muR':mur,'muF':muf,'tag':tag,'command':command,'returncode':p.returncode,'wall_seconds':time.time()-start,'input_sha256':inputs,'output_sha256':artifacts,'source_tree_sha256':source_hash,'matrix_tree_sha256':matrix_hash,'artifacts_sha256':{p.name:sha(p) for p in receipt_dir.iterdir() if p.is_file()},'physics_rate_pass':False,'yukawa_scheme':'D5 frozen running-at-700 masses'}
    (receipt_dir/'receipt.json').write_text(json.dumps(r,indent=2,allow_nan=False)+'\n');print(tag,p.returncode,flush=True)
    if p.returncode:raise RuntimeError('MG execution failed')


def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['generate','run']);p.add_argument('--kind',choices=list(PROCESSES));p.add_argument('--spectrum',default='source');p.add_argument('--mur',type=float,default=700.);p.add_argument('--muf',type=float,default=700.)
    a=p.parse_args()
    if a.action=='generate':generate()
    else:execute(a.kind,a.spectrum,a.mur,a.muf)
if __name__=='__main__':main()
