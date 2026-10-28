"""Execute MG5 Python/ALOHA amplitudes independently of native UFO evaluator."""
import json
import math
import os
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1];LOCAL=ROOT/'validation/module8/local'
# PLY writes its generated parser cache in cwd: keep it in ignored local/.
os.chdir(LOCAL)
sys.path.insert(0,str(LOCAL/'mg5amcnlo-mg5amcnlo-0e6c945'))
from madgraph.interface.master_interface import MasterCmd
from madgraph.core.helas_objects import HelasMatrixElement
from madgraph.various.process_checks import MatrixElementEvaluator
from models.check_param_card import ParamCard


def independent_gb_trace(p,a,b,gs,mt):
    """Two QCD diagrams, explicit Dirac trace; 1/4 spin and 1/6 color."""
    eye=np.eye(2);zero=np.zeros((2,2));pauli=[np.array([[0,1],[1,0]]),np.array([[0,-1j],[1j,0]]),np.diag([1,-1])]
    gamma=[np.block([[eye,zero],[zero,-eye]])]+[np.block([[zero,s],[-s,zero]]) for s in pauli]
    gamma5=1j*gamma[0]@gamma[1]@gamma[2]@gamma[3]
    pl=(np.eye(4)-gamma5)/2;pr=(np.eye(4)+gamma5)/2;C=a*pl+b*pr
    def slash(q):return q[0]*gamma[0]-sum(q[i]*gamma[i] for i in range(1,4))
    def sq(q):return q[0]**2-sum(q[i]**2 for i in range(1,4))
    pg,pb,pt,_=map(np.array,p);svec=pg+pb;tvec=pt-pg
    A=[C@slash(svec)@gm/sq(svec)+gm@(slash(tvec)+mt*np.eye(4))@C/(sq(tvec)-mt*mt) for gm in gamma]
    def trace(op):return np.trace((slash(pt)+mt*np.eye(4))@op@slash(pb)@gamma[0]@op.conj().T@gamma[0]).real
    msq=gs*gs*sum(sign*trace(op) for sign,op in zip([-1,1,1,1],A))/24
    ward=pg[0]*A[0]-sum(pg[i]*A[i] for i in range(1,4))
    return float(msq),float(abs(trace(ward)))


def momenta(ecm,m1,m2,costheta):
    E1=(ecm*ecm+m1*m1-m2*m2)/(2*ecm);E2=ecm-E1
    k=math.sqrt((ecm*ecm-(m1+m2)**2)*(ecm*ecm-(m1-m2)**2))/(2*ecm)
    st=math.sqrt(1-costheta*costheta)
    return [[ecm/2,0.,0.,ecm/2],[ecm/2,0.,0.,-ecm/2],
            [E1,k*st,0.,k*costheta],[E2,-k*st,0.,-k*costheta]]


def main():
    cmd=MasterCmd();cmd.exec_cmd('set auto_update 0');cmd.exec_cmd('import model '+str(LOCAL/'native/sarah/ZeeTypeII/EWSB/UFO')+' -modelname')
    source=LOCAL/'receipts/d5_v2_source/P2/param_card.dat'
    if not source.exists():raise ValueError('Source production input required')
    matrices={}
    for name,process in [('P1','u1 u1bar > z > hm3c hm2 QCD=0'),('P2','g d3 > u3 hm3 QCD=1 QED=1'),('P2cc','g d3bar > u3bar hm3c QCD=1 QED=1')]:
        cmd.exec_cmd('generate '+process);matrices[name]=HelasMatrixElement(cmd._curr_amps[0])
    baseline={};results=[];maxres=0.;normalization={}
    for gamma in (1.089,0.,math.pi/2,-math.pi/2,-1.089,.4,math.pi/2-1.089):
        card=ParamCard(str(source));b=1.394;cb=math.cos(b);sb=math.sin(b);cg=math.cos(gamma);sg=math.sin(gamma)
        zp=[[cb,sb,0],[-sb*cg,cb*cg,sg],[sb*sg,-cb*sg,cg]]
        for i in range(3):
            for j in range(3):card['chargemix'].get((i+1,j+1)).value=zp[i][j]
        out=LOCAL/'cards'/f'mg_control_{gamma}.dat';card.write(str(out), precision=17)
        evaluator=MatrixElementEvaluator(cmd._curr_model,param_card=str(out),reuse=False,cmd=cmd)
        for process in matrices:
            masses=(700.,300.) if process=='P1' else (172.4,700.)
            p=momenta(2000.,*masses,.23)
            got=evaluator.evaluate_matrix_element(matrices[process],p=p)[0]
            if gamma==1.089:baseline[process]=got
            scale=(math.sin(2*gamma)/math.sin(2*1.089))**2 if process=='P1' else (math.sin(gamma)/math.sin(1.089))**2
            want=baseline[process]*scale
            relative=abs(got-want)/max(baseline[process],1e-100)
            if not math.isfinite(got) or relative>1e-10:raise ValueError('MG mixing scaling failed '+process)
            maxres=max(maxres,relative)
            results.append({'process':process,'gamma':gamma,'matrix_element_squared':got,'expected_scaling':scale,'residual_over_baseline':relative})
            if process=='P1' and gamma==1.089:
                g=2*80.379/246.21965;cw=80.379/91.1876;sw2=1-cw*cw;s=2000.**2
                gl=g/cw*(.5-2/3*sw2);gr=-g/cw*(2/3*sw2);c=g*math.sin(2*gamma)/(4*cw)
                lam=(s-1000.**2)*(s-400.**2)
                want=c*c*(gl*gl+gr*gr)*lam*(1-.23**2)/(12*((s-91.1876**2)**2+(91.1876*2.4952)**2))
                if abs(got/want-1)>1e-10:raise ValueError(f'Independent MG Z amplitude normalization: {got} vs {want}')
                normalization['P1']={'MG_m2':got,'analytical_m2':want,'relative_residual':abs(got/want-1)}
                at_threshold=evaluator.evaluate_matrix_element(matrices[process],p=momenta(1000.,700.,300.,.23))[0]
                if abs(at_threshold)>1e-24:raise ValueError('MG scalar-pair threshold amplitude nonzero')
                normalization['P1']['MG_m2_at_threshold']=at_threshold
            if process=='P2' and gamma==1.089:
                from module7.d4_inputs import ckm,yukawa_masses
                ym=yukawa_masses(700.);d=-math.sin(gamma);V=ckm()[2,2]
                a=math.sqrt(2)*ym[2]*d*V/(246.21965*math.tan(1.394))
                b=math.sqrt(2)*ym[5]*d*V*math.tan(1.394)/246.21965
                independent,ward=independent_gb_trace(p,a,b,math.sqrt(4*math.pi*.118),172.4)
                if abs(got/independent-1)>1e-10:raise ValueError(f'Independent gb trace: {got} vs {independent}')
                if ward>1e-7:raise ValueError('gb Ward identity failed')
                normalization['P2']={'MG_m2':got,'independent_Dirac_trace_m2':independent,
                    'relative_residual':abs(got/independent-1),'absolute_Ward_trace':ward,
                    'threshold_phase_space_momentum_GeV':momenta(872.4,172.4,700.,.23)[2][1]}
    if abs(baseline['P2']/baseline['P2cc']-1)>1e-10:raise ValueError('MG charge conjugation failed')
    report={'status':'D5_INDEPENDENT_MG_MATRIX_CHECK_PASS','matrix_checks':results,
            'independent_normalization_checks':normalization,
            'max_scaling_residual_over_baseline':maxres,'P2_charge_conjugation_relative_residual':abs(baseline['P2']/baseline['P2cc']-1),
            'P1_analytical_spin_color_normalization_pass':True,
            'P2_independent_Dirac_trace_and_gluon_Ward_pass':True,
            'thresholds_GeV':{'P1_source':1000.,'P2':872.4},
            'controls':'fixed external masses/energy/angles/Yukawas; vary charged mixing only, not globally viable scalar points'}
    from module8.run_capture import sha
    report['source_sha256']={str(path.relative_to(ROOT)):sha(path) for path in [Path(__file__),source,LOCAL/'ufo_audit.json',LOCAL/'MG5_v3.6.7.tar.gz']}
    (LOCAL/'mg_matrix_checks.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'])

if __name__=='__main__':main()
