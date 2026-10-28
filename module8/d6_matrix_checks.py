"""Independent MG Python/ALOHA tree graphs, flavor and interference controls."""
import json
import math
import os
import sys
from .d6_production import LOCAL, MG, UFO, ORDERS, parameter_card, gate
from .run_capture import sha


def momenta(ecm,m1,m2,c):
    e=(ecm**2+m1*m1-m2*m2)/(2*ecm)
    k=math.sqrt((ecm**2-(m1+m2)**2)*(ecm**2-(m1-m2)**2))/(2*ecm)
    x=k*math.sqrt(1-c*c)
    return [[ecm/2,0.,0.,ecm/2],[ecm/2,0.,0.,-ecm/2],[e,x,0.,k*c],[ecm-e,-x,0.,-k*c]]


def main():
    gate();os.chdir(LOCAL);sys.path.insert(0,str(MG))
    from madgraph.interface.master_interface import MasterCmd
    from madgraph.core.helas_objects import HelasMatrixElement
    from madgraph.various.process_checks import MatrixElementEvaluator
    from models.check_param_card import ParamCard
    cmd=MasterCmd();cmd.exec_cmd('set auto_update 0');cmd.exec_cmd('import model '+str(UFO)+' -modelname')
    cmd.exec_cmd('define q = u1 u2 d1 d2 d3');cmd.exec_cmd('define qb = u1bar u2bar d1bar d2bar d3bar')
    matrices={};graphs=[]
    for category,mid,orders in [('full','>',ORDERS),('Z','> z >',ORDERS),('Y','>',' / a z hh1 hh2 ah2'+ORDERS),('S','>',' / a z u1 u2 u3 d1 d2 d3'+ORDERS)]:
        for final in ['hm3c hm2','hm3 hm2c']:
            cmd.exec_cmd('generate q qb '+mid+' '+final+orders)
            for amp in cmd._curr_amps:
                ids=tuple(l['id'] for l in amp['process']['legs'])
                matrices[(category,ids)]=HelasMatrixElement(amp)
                if category=='full':
                    diagrams=[]
                    for d in amp['diagrams']:
                        vv=[{'vertex_id':v['id'],'legs':[{'id':l['id'],'number':l['number'],'state':l['state']} for l in v['legs']]} for v in d['vertices']]
                        diagrams.append({'orders':dict(d.get('orders')),'vertices':vv})
                    graphs.append({'external_pdgs':ids,'diagrams':diagrams})
    results=[]
    for spectrum in ['source','mH1_m50p0','mH1_p50p0']:
        path=LOCAL/'d6_matrix_card.dat';path.write_text(parameter_card(spectrum))
        ev=MatrixElementEvaluator(cmd._curr_model,param_card=str(path),reuse=False,cmd=cmd)
        m={'source':300.,'mH1_m50p0':250.,'mH1_p50p0':350.}[spectrum]
        for c in [-.61,.23,.79]:
            p=momenta(2000.,700.,m,c)
            for category,ids in matrices:
                if category!='full':continue
                vals={}
                for label in ['full','Z','Y','S']:
                    me=matrices.get((label,ids));value=ev.evaluate_matrix_element(me,p=p)[0] if me else 0.
                    if not math.isfinite(value) or value<0:raise ValueError('Invalid matrix element')
                    vals[label]=value
                vals['interference_total']=vals['full']-vals['Z']-vals['Y']-vals['S']
                results.append({'spectrum':spectrum,'cos_theta':c,'external_pdgs':ids,'m2':vals})
    controls=[]
    for gamma in [0.,math.pi/2]:
        path=LOCAL/f'd6_gamma_{gamma}.dat';path.write_text(parameter_card('source'));card=ParamCard(str(path))
        b=1.394;cb=math.cos(b);sb=math.sin(b);cg=math.cos(gamma);sg=math.sin(gamma)
        zp=[[cb,sb,0.],[-sb*cg,cb*cg,sg],[sb*sg,-cb*sg,cg]]
        for i in range(3):
            for j in range(3):card['chargemix'].get((i+1,j+1)).value=zp[i][j]
        card.write(str(path),precision=17);ev=MatrixElementEvaluator(cmd._curr_model,param_card=str(path),reuse=False,cmd=cmd)
        for ids in [(2,-2,-9000037,37),(5,-5,-9000037,37)]:
            values={label:ev.evaluate_matrix_element(matrices[(label,ids)],p=momenta(2000.,700.,300.,.23))[0] for label in ['full','Z']}
            if abs(values['Z'])>1e-24:raise ValueError('Endpoint Z control nonzero')
            controls.append({'gamma':gamma,'external_pdgs':ids,'m2':values})
    report={'status':'D6_INDEPENDENT_TREE_MATRIX_PASS','kinematics':'sqrt(shat)=2000 GeV, spin/color-averaged m2, alpha_s card irrelevant for QCD=0','graphs':graphs,'flavor_checks':results,'endpoint_controls':controls,'source_sha256':{str(p):sha(p) for p in [__file__,MG/'madgraph/various/process_checks.py',MG/'madgraph/core/helas_objects.py']}}
    (LOCAL/'d6_matrix_checks.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');print(report['status'])
if __name__=='__main__':main()
