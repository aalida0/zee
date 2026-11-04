"""Independent Fock/Wick and on-shell check of the exported FormCalc chains."""
from pathlib import Path
import json
import hashlib
import numpy as np
from operator_amplitude_test import g, PL, PR, metric, slash, u, bar, tensor
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'local/crossing_bridge'
CHARGE=1j*g[2]@g[0]
IDENT=np.eye(4)


def annihilator(n):
    op=np.zeros((16,16),complex)
    for state in range(16):
        if state & (1<<n):
            target=state^(1<<n)
            op[target,state]=(-1)**((state&((1<<n)-1)).bit_count())
    return op


def bilinear(left,matrix,right):
    return sum(left[a]@right[b]*matrix[a,b] for a in range(4) for b in range(4))


def run():
    assert np.max(abs(CHARGE@CHARGE.conj()+IDENT))<1e-15
    for a in range(4):
        assert np.max(abs(CHARGE@g[a].T@np.linalg.inv(CHARGE)+g[a]))<1e-15
    rows=json.loads((OUT/'chains-numeric.json').read_text())
    mi,mj,e=3.,.7,.3;cl,cr=.37+.83j,-.29+.41j
    X=cl*PL+cr*PR;Xhc=cr.conjugate()*PL+cl.conjugate()*PR
    energy=(mi*mi-mj*mj)/(2*mi)
    direction=np.array([1.,2.,3.])/np.sqrt(14)
    q=np.r_[energy,energy*direction];p=np.array([mi,0,0,0]);k=p-q
    eps=np.r_[0.,np.array([2.,-1.,0.])/np.sqrt(5)]+.4*q
    bi,di,bj,dj=[annihilator(n) for n in range(4)]
    vacuum=np.eye(16)[:,0]
    fock_errors=[];spinor_errors=[];qed_phases=[];ward_errors=[];rephase_errors=[]
    for si in range(2):
        for sj in range(2):
            ui,uj=u(p,mi,si),u(k,mj,sj)
            vi,vj=CHARGE@bar(ui).T,CHARGE@bar(uj).T
            # Two independent field expansions, with anticommuting modes.
            fi=[ui[a]*bi+vi[a]*di.conj().T for a in range(4)]
            fj=[uj[a]*bj+vj[a]*dj.conj().T for a in range(4)]
            bari=[bar(ui)[a]*bi.conj().T+bar(vi)[a]*di for a in range(4)]
            barj=[bar(uj)[a]*bj.conj().T+bar(vj)[a]*dj for a in range(4)]
            ci=[sum(CHARGE[a,b]*bari[b] for b in range(4)) for a in range(4)]
            cj=[sum(CHARGE[a,b]*barj[b] for b in range(4)) for a in range(4)]
            invC=np.linalg.inv(CHARGE)
            barci=[-sum(fi[b]*invC[b,a] for b in range(4)) for a in range(4)]
            barcj=[-sum(fj[b]*invC[b,a] for b in range(4)) for a in range(4)]
            for matrix in [tensor(q,eps)@X,tensor(q,eps)@Xhc,slash(eps)]:
                direct=bilinear(barj,matrix,fi)
                cc_matrix=CHARGE@matrix.T@invC
                rewritten=bilinear(barci,cc_matrix,cj)
                # This checks the full operator matrix, including Wick signs,
                # rather than assigning a minus to the resulting Wilsons.
                error=float(np.max(abs(direct-rewritten)))
                assert error<1e-12,error
                fock_errors.append(error)
            for fourier in [1,-1]:
                # <j|L|i>, including independently expanded F_mu_nu.
                fmunu=fourier*1j*(np.outer(metric*q,metric*eps)-np.outer(metric*eps,metric*q))
                sigmaF=sum(.5j*(g[a]@g[b]-g[b]@g[a])*fmunu[a,b] for a in range(4) for b in range(4))
                lag=bilinear(barj,e*mi/2*sigmaF@X,fi)
                mfock=vacuum.conj()@bj@lag@bi.conj().T@vacuum
                physical=bar(uj)@(1j*fourier*e*mi*tensor(q,eps)@X)@ui
                assert abs(mfock-physical)<1e-12
                pi,pj=np.exp(.31j),np.exp(-.47j)
                transformedX=(pj.conjugate()*pi)*X
                rephased=bar(pj.conjugate()*uj)@(1j*fourier*e*mi*tensor(q,eps)@transformedX)@(pi.conjugate()*ui)
                assert abs(rephased-physical)<1e-12
                rephase_errors.append(float(abs(rephased-physical)))
                qed=e*(bar(uj)@slash(eps)@ui)
                # Exactly the two exported source orders. Analytic crossing
                # v(-p)=u(p) fixes phases consistently; no fitted phase.
                for orientation,(left,right,k1,m1,m2,unphased) in enumerate([
                    (ui,uj,-p,mi,mj,physical.conjugate()),
                    (uj,ui,-k,mj,mi,physical)]):
                    assert np.linalg.norm((slash(k1)+m1*IDENT)@left)<1e-13
                    k2=k if orientation==0 else p
                    assert np.linalg.norm((slash(k2)-m2*IDENT)@right)<1e-13
                    projected=0j;vector=0j
                    for ch in rows[orientation]:
                        for chir,degree,re,im in ch:
                            P=PR if chir==6 else PL
                            value=complex(re,im)
                            if degree==0:
                                value*=fourier
                                projected+=value*(k1@(metric*eps))*(bar(left)@P@right)
                            else:
                                # Numerical export contains QED vector -e in
                                # each chirality and the independent tensor.
                                tensor_part=value+e
                                projected+=fourier*tensor_part*(bar(left)@P@slash(eps)@right)
                                vector+=-e*(bar(left)@P@slash(eps)@right)
                    ward=0j
                    for ch in rows[orientation]:
                        for chir,degree,re,im in ch:
                            P=PR if chir==6 else PL;value=complex(re,im)
                            if degree==0:
                                ward+=value*(k1@(metric*q))*(bar(left)@P@right)
                            else:
                                ward+=(value+e)*(bar(left)@P@slash(q)@right)
                    assert abs(ward)<1e-12
                    ward_errors.append(float(abs(ward)))
                    qed_reference=qed.conjugate() if orientation==0 else qed
                    assert abs(qed_reference)>1e-12
                    # Determine the external-state phase from the signed
                    # vector chain alone, before comparing tensor amplitudes.
                    phase_from_QED=vector/qed_reference
                    assert abs(phase_from_QED+1)<1e-13
                    target=phase_from_QED*unphased
                    err=abs(projected-target)
                    assert err<1e-12,(si,sj,fourier,orientation,projected,target)
                    spinor_errors.append(float(err))
                    qtarget=-qed.conjugate() if orientation==0 else -qed
                    assert abs(vector-qtarget)<1e-13
                    qed_phases.append(float(abs(vector-qtarget)))
    evidence={'status':'PASS','spinor_comparisons':len(spinor_errors),
              'fock_operator_comparisons':len(fock_errors),
              'maximum_spinor_absolute_residual':max(spinor_errors),
              'maximum_fock_absolute_residual':max(fock_errors),
              'maximum_QED_absolute_residual':max(qed_phases),'maximum_Ward_absolute_residual':max(ward_errors),'maximum_rephase_absolute_residual':max(rephase_errors),
              'FormCalc_chain_input_sha256':hashlib.sha256((OUT/'chains-numeric.json').read_bytes()).hexdigest(),
              'phase_reference':'same-state QED-normalized vector; crossed physical M has common minus relative to HC, tensor included',
              'Fourier_signs':[1,-1],'masses':[mi,mj],'coefficients':[[cl.real,cl.imag],[cr.real,cr.imag]]}
    (OUT/'spinor-evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
    print(json.dumps(evidence,indent=2))

if __name__=='__main__':run()
