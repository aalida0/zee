"""Write minimal MG5 cards from audited particle names into ignored local/.

Fresh directories only. Dependencies are official MG5 3.6.7 and LHAPDF6.
"""
import json
from pathlib import Path
import subprocess
import sys
from .run_capture import LOCAL
from .real_run_validation import EXPECTED


def main():
    audit=json.loads((LOCAL/'ufo_audit.json').read_text())
    if audit['status']!='D5_UFO_VERTEX_PASS':raise ValueError('Native gate must pass first')
    particles={p['name'].lower():p for p in audit['particles']}
    for name,charge in [('hm2',-1.),('hm2c',1.),('hm3',-1.),('hm3c',1.)]:
        if particles[name]['charge']!=charge:raise ValueError('Actual UFO names/charges changed')
    mg=LOCAL/'MG5_aMC_v3_6_7/bin/mg5_aMC'
    if not mg.exists():raise ValueError('Install official MG5 3.6.7 release under local/ first')
    commands=['set auto_update 0','set automatic_html_opening False','set notification_center False',
       'set lhapdf '+str(LOCAL/'lhapdf/bin/lhapdf-config'),
       'import model '+audit['export']['ufo_directory']+' -modelname',
       'define q = u1 u2 d1 d2 d3','define qb = u1bar u2bar d1bar d2bar d3bar']
    for process in ('P1','P2'):
        out=LOCAL/(process+'_full')
        if out.exists():raise ValueError('Refuse existing process directory '+str(out))
        commands+=EXPECTED[process]+['output '+str(out)]
    commands+=['quit'];path=LOCAL/'generate_full.txt';path.write_text('\n'.join(commands)+'\n')
    with (LOCAL/'generate_full.log').open('w') as log:
        return subprocess.run([sys.executable,str(mg),str(path)],cwd=LOCAL,stdout=log,stderr=subprocess.STDOUT).returncode

if __name__=='__main__':raise SystemExit(main())
