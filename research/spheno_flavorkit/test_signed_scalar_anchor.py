"""Call the actual generated Gamma2l with pure scalar/pseudoscalar toy vertices.

This is a diagonal sign anchor, not a complex off-diagonal mapping proof.
No Zee mass/Yukawa benchmark or positive rate is used.
"""
from pathlib import Path
import subprocess
import json
import hashlib
import mpmath as mp

ROOT=Path(__file__).resolve().parent
BACKEND=ROOT/'local/SPheno-4.0.5'


def main():
    out=ROOT/'local/d15_signed_anchor';out.mkdir(exist_ok=True)
    driver='''program anchor
use FlavorKit_LFV_ZeeTypeII
implicit none
complex(dp) :: z332(3,3,2), y332(3,3,2), yr332(3,3,2),z333(3,3,3),z33(3,3),e33(3,3),z3(3),z0,ol,orr,o1l,o1r
real(dp) :: leptons(3), scalars(2), charged(3),e,y,m,ms
integer :: kind,n
z332=0; z333=0;z33=0;z3=0;z0=0
leptons=(/0.000511_dp,0.105658_dp,1.77686_dp/)
mf_l=leptons;mf_l2=leptons**2
charged=(/200._dp,300._dp,400._dp/)
e=sqrt(4._dp*acos(-1._dp)/137._dp);y=0.017_dp;m=leptons(2)
e33=0
 do n=1,3
 e33(n,n)=e
 end do
 do kind=1,2
 do n=1,3
 ms=10._dp**(n+1)
 scalars=(/ms,2*ms/)
 y332=0;yr332=0
 if (kind==1) then
 y332(2,2,1)=-y;yr332(2,2,1)=-y
 else
 y332(2,2,1)=cmplx(0._dp,-y,dp);yr332(2,2,1)=cmplx(0._dp,y,dp)
 end if
 call CalculateGamma2l(2,2,1,.false.,scalars,scalars**2,leptons,leptons**2,scalars,scalars**2, &
 charged,charged**2,80._dp,6400._dp,91._dp,8281._dp, &
 z332,z332,y332,yr332,e33,e33,z33,z33,z333,z333,z33,z33,z3,z0,z333,z333,z33,z33,z33,z3,ol,orr,o1l,o1r)
 write(*,'(a,1x,i1,1x,5(es26.17e3,1x))') 'ANCHOR',kind,ms,real(-ol/(2*e*m),dp),real(-orr/(2*e*m),dp),aimag(ol),aimag(orr)
 end do
 end do
end program anchor
'''
    src=out/'anchor.f90';src.write_text(driver)
    includes=[BACKEND/'include',BACKEND/'ZeeTypeII']
    exe=out/'anchor'
    cmd=['gfortran','-ffree-line-length-none']+['-I'+str(p) for p in includes]+[str(src),'-L'+str(BACKEND/'lib'),'-Wl,--start-group','-lSPhenoZeeTypeII','-lSPheno','-Wl,--end-group','-o',str(exe)]
    subprocess.run(cmd,check=True)
    result=subprocess.run([str(exe)],text=True,capture_output=True,check=True)
    (out/'run.log').write_text(result.stdout+result.stderr)
    mp.mp.dps=80
    records=[]
    m=mp.mpf('.105658');y=mp.mpf('.017')
    for line in result.stdout.splitlines():
        if not line.startswith('ANCHOR'):continue
        kind,ms,kl,kr,il,ir=map(float,line.split()[1:]);r=(m/ms)**2
        sign=1 if kind==1 else -1
        numerator=(lambda x:x*x*(2-x)) if kind==1 else (lambda x:x**3)
        exact=sign*y*y/(8*mp.pi**2)*r*mp.quad(lambda x:numerator(x)/(1-x+r*x*x),[0,.9,1])
        zero_external=sign*y*y/(8*mp.pi**2)*r*mp.quad(lambda x:numerator(x)/(1-x+r*x),[0,.9,1])
        generated=-m*m*(kl+kr)
        error=float(abs((generated-zero_external)/zero_external))
        # Accuracy of the other legacy loop functions, outside this patch,
        # is measured here rather than hidden in a BR comparison.
        records.append({'kind':'scalar' if kind==1 else 'pseudoscalar','mass':ms,
                        'K_L':kl,'K_R':kr,'a_from_negative_K_sum':float(generated),
                        'independent_parameter_integral':float(exact),
                        'zero_external_mass_integral':float(zero_external),
                        'relative_residual_zero_external':error,
                        'external_mass_expansion_effect':float(abs(exact/zero_external-1))})
        assert il==ir==0 and generated*exact>0 and error<1e-12,records[-1]
    assert len(records)==6
    evidence={'scope':'diagonal sign anchor only','records':records,
              'driver_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
              'executable_sha256':hashlib.sha256(exe.read_bytes()).hexdigest()}
    (ROOT/'local/d15-signed-anchor.json').write_text(json.dumps(evidence,indent=2)+'\n')
    print(json.dumps(evidence,indent=2))

if __name__=='__main__':main()
