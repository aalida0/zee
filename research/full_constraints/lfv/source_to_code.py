"""Bounded published F-sector controls, never a complete LFV adapter.

Only saved D12 central cards and analytic limits are evaluated. External sources
are read, hash checked, and compiled in a temporary directory; no spectrum run.
"""
import argparse
import cmath
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import tempfile

import numpy as np
from scipy.integrate import quad
from numpy.polynomial.legendre import leggauss

from research.full_constraints.lfv.validate import ROOT, HERE, sha, source_check, conversion_sign_control
from module2.interface import decode, canonical_hash
from module3 import tree
from module3.core import vertices


def cpair(z):
    return [float(complex(z).real), float(complex(z).imag)]


def kernel(a, b):
    """Mit01 Eq16 mixed-state radial integral, squared masses in GeV^2."""
    t = (a-b)/b
    return 1/b if t == 0 else math.log1p(t)/(b*t)


def box_kernel(m1, m2, gamma):
    w = np.array([math.sin(gamma)**2, math.cos(gamma)**2])
    m = np.array([m1*m1, m2*m2])
    return sum(w[i]*w[j]*kernel(m[i], m[j]) for i in range(2) for j in range(2))


def subroutine(text, name):
    return re.search(r'(?im)^Subroutine '+name+r'\(.*?^End Subroutine '+name+r'\s*$',
                     text, re.S | re.M).group()


def generated_box_driver(generated, couplings, loops, work):
    """Execute unmodified generated F-only block and native vertex routines.

    At mnu=0 MMD0 is exactly zero. Other topology couplings are zero in this
    analytic F-only control. No doublet result is claimed from this extraction.
    """
    text = generated.read_text()
    block = text.split(' ! Fv,conj[Hm],Fv,conj[Hm]')[1].split(' ! Fv,conj[VWm],Fv,conj[Hm]')[0]
    assignments = re.findall(r'^\s*(BO4l\w+)=', block, re.M)
    names = list(dict.fromkeys(assignments))
    body = subroutine(couplings.read_text(), 'CouplingFvFecHmT')+'\n'+subroutine(couplings.read_text(), 'CouplingcFeFvHmT')
    d00 = re.search(r'^Real\(dp\) Function KilianD00\(.*?^End Function KilianD00\s*$', loops.read_text(), re.M | re.S).group()
    source = '''module audit
implicit none
integer,parameter :: dp=kind(1.d0)
integer :: Iname=0,ErrCan=6
character(80) :: NameOfUnit(100)
contains
subroutine TerminateProgram()
error stop 'unexpected generated-source error'
end subroutine
real(dp) function KilianD00_3m(a,b,c)
real(dp) :: a,b,c
error stop 'nonzero neutrino mass outside control'
end function
real(dp) function D27_Bagger(a,b,c,d)
real(dp) :: a,b,c,d
error stop 'nonzero neutrino mass outside control'
end function
complex(dp) function D00check(a,b,c,d)
real(dp) :: a,b,c,d
D00check=KilianD00(a,b,c,d)
end function
complex(dp) function MMD0(a,b,c,d,e,f)
real(dp) :: a,b,c,d,e,f
if (a/=0.or.b/=0) error stop 'MMD0 control requires massless neutrinos'
MMD0=0
end function
'''+d00+'\n'+body+'''
end module
program main
use audit
implicit none
integer :: i1,i2,i3,i4,gt1=2,gt2=1,gt3=1,gt4=1,j,k,h
logical :: OnlySM=.false.
real(dp) :: MHm(3),MHm2(3),MFv(3)=0,MFv2(3)=0,mf_l2(3)=0,ZP(3,3),g,m1,m2
real(dp) :: mF1,mF12,mF2,mF22,mS1,mS12,mS2,mS22,oo16pi2=1/(16*acos(-1._dp)**2),x,y
complex(dp) :: fzee(3,3),Ye(3,3)=0,Ye2(3,3)=0,UV(3,3)=0,ZEL(3,3)=0,ZER(3,3)=0
complex(dp) :: cplFvFecHmL(3,3,3),cplFvFecHmR(3,3,3),cplcFeFvHmL(3,3,3),cplcFeFvHmR(3,3,3)
complex(dp) :: coup1L,coup1R,coup2L,coup2R,coup3L,coup3R,coup4L,coup4R,int1,int2,chargefactor
complex(dp) :: '''+','.join(names)+'''
do j=1,3
UV(j,j)=1; ZEL(j,j)=1; ZER(j,j)=1
end do
do
read(*,*,end=100) m1,m2,g
do j=1,3
do k=1,3
read(*,*) x,y
fzee(j,k)=cmplx(x,y,dp)
end do
end do
MHm=[80._dp,m1,m2]; MHm2=MHm**2
ZP=0; ZP(1,1)=1; ZP(2,3)=sin(g); ZP(3,3)=cos(g)
do j=1,3
do k=1,3
do h=1,3
call CouplingFvFecHmT(j,k,h,fzee,Ye,Ye2,UV,ZP,ZEL,ZER,cplFvFecHmL(j,k,h),cplFvFecHmR(j,k,h))
call CouplingcFeFvHmT(j,k,h,fzee,Ye,Ye2,UV,ZP,ZEL,ZER,cplcFeFvHmL(j,k,h),cplcFeFvHmR(j,k,h))
end do
end do
end do
'''+ '\n'.join(n+'=0' for n in names)+'\n'+block+'\n'+ '\n'.join(
        "write(*,'(2ES26.17E3)') real("+n+"*oo16pi2,dp),aimag("+n+"*oo16pi2)" for n in names)+'''
end do
100 continue
end program
'''
    path = work/'box.f90'; path.write_text(source)
    subprocess.run(['gfortran','-O0','-fcheck=all','-ffree-line-length-none',str(path),'-o',str(work/'box')],cwd=work,check=True,capture_output=True)
    return names, sha(path)


def z_functions(xi1, xi2, order=100):
    """Gho01 Eq4.3/4.6 and real Appendix A.3 (not a causal off-shell vertex).

    The printed G representation is real. Absorptive completion is not inferred.
    Both unequal-mass orientations are evaluated before subtraction.
    """
    q,w = leggauss(order); q=(q+1)/2; w=w/2
    x=q[:,None]; y=q[None,:]; weight=w[:,None]*w[None,:]
    def f(a,b):
        return float(np.sum(weight*x*np.log(1-(1-a/b)*y-a*x*y*(1-y))))
    def g(a):
        x0=2/(math.sqrt(1+a)+1)
        def lower(x):
            d=4*(1-x)-a*x*x
            return 2*(2*(1-x)-a*x*x)/(math.sqrt(a)*math.sqrt(d))*math.atan(x*math.sqrt(a/d))
        def upper(x):
            d=a*x*x-4*(1-x); r=math.sqrt(d/a)/x
            return (a*x*x-2*(1-x))/(math.sqrt(a)*math.sqrt(d))*2*math.atanh(r)
        return -.5+quad(lower,0,x0,epsabs=2e-10)[0]+quad(upper,x0,1,epsabs=2e-10)[0]
    f1,f2=f(xi1,xi1),f(xi2,xi2)
    h=f(xi1,xi2)+f(xi2,xi1)-f1-f2
    # Independent positive representation, Appendix A.5.
    h2=float(np.sum(weight*x*np.log1p((xi1-xi2)**2/(xi1*xi2)*y*(1-y)/
                                      ((1-xi1*x*y*(1-y))*(1-xi2*x*y*(1-y))))))
    return dict(F1=f1,F2=f2,G1=g(xi1),G2=g(xi2),H=h,H_positive=h2)


def independent_g_real(a):
    """Eq4.4: G=3/4+I+a*dI/da, analytic y integration of log|D|.

    Independent of the printed A.3 representation. Only real parts compared.
    """
    def integral(t):
        x0=2/(math.sqrt(1+t)+1)
        def integrand(x):
            u=cmath.sqrt(complex(4*(1-x)-t*x*x,-1e-30)/(t*x*x))
            return x*(math.log1p(-x)-2+2*u*cmath.atan(1/u)).real
        return quad(integrand,0,x0,epsabs=1e-12)[0]+quad(integrand,x0,1,epsabs=1e-12)[0]
    step=a*1e-4
    derivative=(integral(a-2*step)-8*integral(a-step)+8*integral(a+step)-integral(a+2*step))/(12*step)
    return .75+integral(a)+a*derivative


def nuclear_driver(fs, fk, work):
    text=fs.read_text()
    overlap=text[text.index('overlap_integrals get_overlap_integrals'):text.index('typedef std::valarray')]
    start=text.index('   const auto left  =')
    action=text[start:text.index('   // eq. (3.31)',start)]
    source='''#include <cmath>
#include <complex>
#include <iostream>
#include <iomanip>
#include <stdexcept>
enum class Nucleus {Au,Al};
namespace softsusy {enum {mMuon}; struct QedQcd {double displayMass(int) const {return .1056583755;}};}
struct overlap_integrals {double D,Vp,Vn,Sp,Sn;};
'''+overlap+'''
int main(){
softsusy::QedQcd q;
std::cout<<std::setprecision(17);
for(auto nucleus:{Nucleus::Au,Nucleus::Al}){
auto ff=get_overlap_integrals(nucleus,q);
for(int test=0;test<5;++test){
std::complex<double> DL=0,DR=0,gpLV=0,gnLV=0,gpRV=0,gnRV=0,gpLS=0,gnLS=0,gpRS=0,gnRS=0;
if(test==0){gpRS=5.1;gnRS=4.3;}
if(test==1){gpLV=2.;gnLV=1.;}
if(test==2||test==4){gpRS=1.;gnRS=-1.;}
if(test==3||test==4){gpLV=1.;gnLV=-1.;}
'''+action+'''
std::cout<<test<<" "<<left.real()<<" "<<right.real()<<" "<<4*(std::norm(left)+std::norm(right))/get_capture_rate(nucleus)<<"\\n";
}}
}
'''
    p=work/'nuclear.cpp'; p.write_text(source)
    subprocess.run(['g++','-std=c++17',str(p),'-o',str(work/'nuclear')],check=True,capture_output=True)
    stdout=subprocess.check_output([str(work/'nuclear')],text=True)
    (work/'nuclear.stdout').write_text(stdout)
    # Execute unmodified FlavorKit twice: scalar up and vector up, same source normalization.
    previous=Path.cwd()
    try:
        os.chdir(work)
        scalar=conversion_sign_control(fk,work)
    finally:
        os.chdir(previous)
    driver=(work/'conversion.f90').read_text().replace('OlluuSLL(2,1,1,1)=-sqrt(2._dp)*G_F',
                                                    'OlluuVLL(2,1,1,1)=-sqrt(2._dp)*G_F')
    (work/'vector.f90').write_text(driver)
    subprocess.run(['gfortran','-O0','-fcheck=all','-ffree-line-length-none',str(work/'vector.f90'),'-o',str(work/'vector')],cwd=work,check=True,capture_output=True)
    raw=subprocess.check_output([str(work/'vector')],text=True)
    vector=[float(v) for v in raw.split()]
    rows=[]
    for n,line in enumerate(stdout.splitlines()):
        test,left,right,rate=map(float,line.split()); target='Au' if n<5 else 'Al'
        z,ne,sp,sn,vp,vn=(79,118,.0523,.0610,.0859,.1080) if target=='Au' else (13,14,.0153,.0163,.0159,.0169)
        expected=-[5.1*sp+4.3*sn,2*vp+vn,sp-sn,vp-vn,sp-sn+vp-vn][int(test)]*.1056583755**2.5
        assert abs(left/expected-1)<1e-14 and right==0
        rows.append(dict(target=target,insertion=['scalar_up','vector_up','scalar_isovector','vector_isovector','coherent_isovectors'][int(test)],
                         left_current_GeV_5o2=left,right_current_GeV_5o2=right,
                         rate_over_capture=rate,assignment_relative_residual=abs(left/expected-1)))
    for i,row in enumerate(scalar['records']):
        z,n=[(13,14),(22,26),(38,42),(51,70),(79,118),(82,125)][i]
        # Same nucleus/prefactor, but a vector-up current is 2Z+N.
        expected=row['direct_proton_neutron_rate']*((2*z+n)/row['expected_scalar_current'])**2
        assert abs(vector[i]/expected-1)<1e-7
    iso=[]
    for name,insertion in [
        ('scalar','OlluuSLL(2,1,1,1)=-sqrt(2._dp)*G_F/0.8_dp\nOllddSLL(2,1,1,1)=sqrt(2._dp)*G_F/0.8_dp'),
        ('vector','OlluuVLL(2,1,1,1)=-sqrt(2._dp)*G_F\nOllddVLL(2,1,1,1)=sqrt(2._dp)*G_F')]:
        iso.append((name,insertion))
    iso.append(('coherent',iso[0][1]+'\n'+iso[1][1]))
    iso_results=[]
    for name,insertion in iso:
        body=(work/'conversion.f90').read_text().replace('OlluuSLL(2,1,1,1)=-sqrt(2._dp)*G_F',insertion)
        path=work/('iso_'+name+'.f90'); path.write_text(body)
        binary=work/('iso_'+name)
        subprocess.run(['gfortran','-O0','-fcheck=all','-ffree-line-length-none',str(path),'-o',str(binary)],cwd=work,check=True,capture_output=True)
        rates=[float(v) for v in subprocess.check_output([str(binary)],text=True).split()]
        au=scalar['records'][4]
        prefactor=au['direct_proton_neutron_rate']/au['expected_scalar_current']**2
        desired=(-39 if name!='coherent' else -78)
        expected_rate=prefactor*desired**2
        # GSp/GSn are single precision literals, retained as in the original source.
        ratio=rates[4]/expected_rate
        assert ratio<1e-12 if name=='coherent' else abs(ratio-1)<1e-6
        iso_results.append(dict(insertion=name,target='Au',source_rate=rates[4],
                                correct_pn_assignment_rate=expected_rate,source_over_reference=ratio,
                                driver_sha256=sha(path)))
    return dict(
        flavorkit_scalar=scalar,flavorkit_vector_up_rates=vector,
        flexiblesusy_nucleon_controls=rows,nuclear_driver_sha256=sha(p),
        flavorkit_pure_isovector_and_interference=iso_results,
        nuclear_stdout=stdout,vector_driver_sha256=sha(work/'vector.f90'),
        caveat='Matched nucleon assignments, not identical nuclear approximations or physical Zee conversion.',
        capture_Au_FlexibleSUSY_GeV=8.84868e-18,capture_Au_FlavorKit_GeV=8.59868e-18)


def run(lock):
    locked=json.loads(lock.read_text())
    for item in locked['artifacts']:
        assert sha(item['path_hint'])==item['sha256'],item['id']
    old=json.loads((HERE/'sources.json').read_text()); source_check(old)
    paths={x['id']:Path(x['path_hint']) for x in locked['artifacts']}
    cards=json.loads((ROOT/'validation/module12/d12_benchmarks.json').read_text())['groups']
    records=[]; inputs=[]
    for group in cards:
        w=group['witnesses']['central']; p=w['module2_input']['scalar']['record']['physical']
        f=decode(w['yukawas']['F']); inputs.append((p['mH1'],p['mH2'],p['gamma'],f))
    with tempfile.TemporaryDirectory(prefix='lfv-source-code-') as temp:
        work=Path(temp)
        names,driver_sha=generated_box_driver(paths['generated'],paths['couplings'],paths['loops'],work)
        executable_sha=sha(work/'box')
        # Card, zero-F, common mass, both endpoints, exchange and external rephasing.
        controls=[]
        for a,b,g,f in inputs:
            u=np.diag(np.exp(1j*np.array([.2,-.4,.7])))
            controls.extend([(a,b,g,f),(a,b,g,0*f),(a,a,g,f),(a,b,0.,f),
                             (a,b,math.pi/2,f),(b,a,math.pi/2-g,f),(a,b,g,u@f@u)])
        stdin=''.join(f'{a:.17e} {b:.17e} {g:.17e}\n'+''.join(f'{v.real:.17e} {v.imag:.17e}\n' for v in f.flat)
                      for a,b,g,f in controls)
        stdout=subprocess.check_output([str(work/'box')],input=stdin,text=True)
        raw=np.array([complex(*map(float,line.split())) for line in stdout.splitlines()]).reshape(len(controls),len(names))
        max_residual=0.
        for row,(a,b,g,f) in zip(raw,controls):
            # Raw generated ordered VLL. Paper Eq26 has -L and 1-gamma5=2PL.
            expected=f[1,2]*f[0,2].conjugate()*np.sum(abs(f[0])**2)*box_kernel(a,b,g)/(64*math.pi**2)
            residual=abs(row[names.index('BO4lVLL')]-expected)/max(abs(expected),1e-300)
            max_residual=max(max_residual,residual)
            assert residual<2e-12
            assert all(v==0 for name,v in zip(names,row) if name!='BO4lVLL')
            numerical=quad(lambda t:1/((t+a*a)*(t+b*b)),0,np.inf,epsabs=1e-14)[0]
            assert abs(numerical/kernel(a*a,b*b)-1)<2e-8
        z_checks=[]
        for index,(a,b,g,f) in enumerate(inputs):
            w=cards[index]['witnesses']['central']; p=w['module2_input']['scalar']['record']['physical']
            ew=w['module2_input']['scalar']['record']['electroweak']
            mz=ew['mZ']; xi1,xi2=(mz/a)**2,(mz/b)**2
            z=z_functions(xi1,xi2); z2=z_functions(xi1,xi2,150)
            assert abs(z['H']-z['H_positive'])<2e-12
            independent=[independent_g_real(xi1),independent_g_real(xi2)]
            assert max(abs(independent[i]-z['G'+str(i+1)]) for i in range(2))<2e-8
            z_checks.append(dict(xi=[xi1,xi2],G_real_independent=independent,
                                 max_residual=max(abs(independent[i]-z['G'+str(i+1)]) for i in range(2))))
            # Paper cos(theta) is singlet content of H1, native singlet weight sin(gamma).
            weights=[math.sin(g)**2,math.cos(g)**2]
            sw2=1-(ew['mW']/mz)**2
            kval=(-2*sw2*(weights[0]*z['F1']+weights[1]*z['F2'])+weights[0]*z['G1']+weights[1]*z['G2']-
                  weights[0]*weights[1]*z['H'])/(2*(4*math.pi)**2)
            # Complex extension of paper real f_ik f_kj is explicitly scoped, not an action bridge.
            # Use rephasing-covariant sum f_ik f_jk*; the real antisymmetric paper product is its negative.
            paper=-np.sum((f/2)[0]*np.conj((f/2)[1]))*kval
            box=raw[index*7,names.index('BO4lVLL')]
            assert np.max(abs(raw[index*7]-raw[index*7+5]))<1e-24
            phase=np.exp(1j*(-.4-.2))
            assert abs(raw[index*7+6,names.index('BO4lVLL')]/box-phase)<2e-12
            assert abs(box_kernel(a,b,0.)*b*b-1)<2e-15
            assert abs(box_kernel(a,b,math.pi/2)*a*a-1)<2e-15
            assert abs(box_kernel(a,a,g)*a*a-1)<2e-15
            neutral=vertices(decode(w['yukawas']['D']),p,w['module2_input']['lepton_masses_GeV'])
            scalar_rows=tree.wilsons(neutral,1,0,0)
            scalar_coefficients={'S'+k:cpair(sum(row['direct'][k] for row in scalar_rows.values()))
                                 for k in ('LL','RR','LR','RL')}
            records.append(dict(id=w['id'],witness_sha256=canonical_hash(w),
                input_sha256=canonical_hash(w['module2_input']),charged_masses_GeV=[a,b],gamma=g,
                tree_scalar_contact_coefficients_GeV_minus2=scalar_coefficients,
                F_box=dict(raw_generated_VLL_GeV_minus2=cpair(box),
                           paper_L_PLPL_coefficient_GeV_minus2=cpair(-box),
                           raw_source_relation='B_VLL = - paper L_PLPL coefficient; full ordered-action bridge UNVALIDATED',
                           inverse_Mtilde_squared_GeV_minus2=box_kernel(a,b,g),
                           other_F_only_contact_coefficients={n:cpair(v) for n,v in zip(names,raw[index*7]) if n!='BO4lVLL'}),
                on_shell_Z=dict(q2_GeV2=mz*mz,**z,K_real_printed=kval,
                    flavor_weighted_K=cpair(paper),
                    quadrature_change=max(abs(z[k]-z2[k]) for k in z),
                    status='PUBLISHED_MODEL_LIMIT_ONLY; real printed G; absorptive/ordered-action map unvalidated',
                    generated_comparison=None,reason='Generated PengV4L zero-momentum B0/C0; not an on-shell Z vertex'),
                complete_mu3e_operator_vector={k:None for k in ['K1L','K1R','K2L','K2R','SLL','SRR','SLR','SRL','VLL','VRR','VLR','VRL','TLL','TRR']},
                physical_BR=None,physical_comparison='UNKNOWN'))
        conversion=nuclear_driver(paths['fs_conversion'],paths['fk_conversion'],work)
    source_check(old)
    equal_z=z_functions(.03,.03)
    assert equal_z['H']==0 and equal_z['H_positive']==0
    small_z=z_functions(1e-6,1e-6)
    assert abs(small_z['F1']/(-1e-6/18)-1)<1e-6 and abs(small_z['G1'])<1e-4
    return dict(status='LFV_ONE_LOOP_BLOCKED',physical_lfv='UNKNOWN',exclusion=None,global_acceptance=None,
                source_lock_sha256=sha(lock),records=records,
                executable_source_sha256=sha(Path(__file__)),
                tests=dict(generated_F_box_controls=len(controls),max_complex_relative_residual=max_residual,
                           box_driver_sha256=driver_sha,box_executable_sha256=executable_sha,
                           compilers={c:subprocess.check_output([c,'--version'],text=True).splitlines()[0] for c in ('gfortran','g++')},
                           box_stdin_sha256=hashlib.sha256(stdin.encode()).hexdigest(),
                           box_stdout=stdout,box_stdout_sha256=hashlib.sha256(stdout.encode()).hexdigest(),
                           Z_real_integral_crosscheck=z_checks,
                           Z_equal_mass_H=equal_z['H'],Z_heavy_mass_control=small_z,
                           limits=['F=0','equal masses','both mixing endpoints','state exchange','external complex phase','independent radial integral'],
                           Ward_identity_and_gauge_cancellation='NOT_TESTED; no complete gauge coefficient set'),conversion=conversion)


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--lock',type=Path,default=HERE/'SOURCE_TO_CODE_SOURCES.json'); p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    with args.output.open('x') as out:
        json.dump(run(args.lock),out,indent=2,allow_nan=False); out.write('\n')
