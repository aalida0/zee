"""D6 rerun capture retaining per-run MG helicity-recycled source snapshots."""
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from .d6_production import gate, PROCESSES, parameter_card, ROOT, LOCAL, UFO
from .run_capture import sha, tree_digest, set_card


def execute(kind,spectrum,mur=700.,muf=700.):
    gate()
    if kind not in PROCESSES or spectrum not in ('source','mH1_m50p0','mH1_p50p0'):raise ValueError('Unsupported process/spectrum')
    if mur not in (350.,700.,1400.) or muf not in (350.,700.,1400.):raise ValueError('Unsupported scales')
    if kind!='A' and (mur,muf)!=(700.,700.):raise ValueError('Mixed pair central only')
    tag=f'd6v3_{kind}_{spectrum}_{int(mur)}_{int(muf)}';folder=LOCAL/('d6_'+kind)
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
    with log.open('w') as out:completed=subprocess.run(command,cwd=folder,env=env,stdout=out,stderr=subprocess.STDOUT)
    result=folder/'SubProcesses/results.dat'
    if result.exists():(receipt_dir/'results.dat').write_bytes(result.read_bytes())
    for filename in ('run_card.dat','param_card.dat'):(receipt_dir/('normalized_'+filename)).write_bytes((folder/'Cards'/filename).read_bytes())
    artifacts={str(p.relative_to(ROOT)):sha(p) for base in [folder/'Events'/tag,folder/'HTML'/tag] for p in base.rglob('*') if p.is_file()}
    compiled={}
    for part in ('Source','SubProcesses'):
        for p in (folder/part).rglob('*'):
            if not p.is_file() or p.is_symlink() or p.suffix not in ('.py','.f','.f90','.inc','.cc','.h'):continue
            relative=Path(part)/p.relative_to(folder/part)
            target=receipt_dir/'compiled_sources'/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(p.read_bytes());compiled[str(relative)]=sha(target)
    r={'compiled_source_snapshot_sha256':compiled,'schema_version':'d6-native-execution-receipt-1','kind':kind,'spectrum':spectrum,'muR':mur,'muF':muf,'tag':tag,'command':command,'returncode':completed.returncode,'wall_seconds':time.time()-start,'input_sha256':inputs,'output_sha256':artifacts,'source_tree_sha256':source_hash,'matrix_tree_sha256':matrix_hash,'artifacts_sha256':{p.name:sha(p) for p in receipt_dir.iterdir() if p.is_file()},'physics_rate_pass':False,'yukawa_scheme':'D5 frozen running-at-700 masses'}
    (receipt_dir/'receipt.json').write_text(json.dumps(r,indent=2,allow_nan=False)+'\n');print(tag,completed.returncode,flush=True)
    if completed.returncode:raise RuntimeError('MG execution failed')
