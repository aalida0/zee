"""Compile actual generated functions; compare all supported branches at 80 digits.

Run directly. Candidate file is optional; default is the local generated backend.
Unsupported unequal/first-third-equal arguments are explicitly checked as legacy
zero sentinels, not interpreted as physical integrals.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import tempfile
import sys
import mpmath as mp

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT/'local/SPheno-4.0.5/ZeeTypeII/Observables/FlavorKit_LFV_ZeeTypeII.f90'


def functions(text):
    parts=[]
    for name in ('C1g','C0C1C2'):
        start=text.index('Real(dp) Function '+name+'(')
        end=text.index('End Function '+name,start)+len('End Function '+name)
        parts.append(text[start:end])
    return '\n'.join(parts)


def reference(r, kind):
    if r == 1:
        return mp.mpf(1)/6
    if kind == 'A':
        return (-1+4*r-3*r*r+2*r*r*mp.log(r))/(4*(r-1)**3)
    if kind == 'B':
        return (3-4*r+r*r+2*mp.log(r))/(4*(r-1)**3)
    return (-1+r*r-2*r*mp.log(r))/(2*(r-1)**3)


def run(source=SRC):
    mp.mp.dps=80
    text=source.read_text()
    body=functions(text)
    assert body.count('D15 stable series') == 8
    # Reconstruct pristine ratio guards for the before comparison from saved source.
    original = Path.home()/'.Mathematica/Applications/SARAH-4.15.4/Package/SPheno/IncludeSPheno/IncludeLowEnergy.f90'
    old=functions(original.read_text())
    old=old.replace('Elseif (r.eq.0._dp) Then','Elseif (Abs(r).lt.eps) Then')
    old=old.replace('C0C1C2','old_C0C1C2').replace('C1g','old_C1g')
    driver='''program check
implicit none
integer, parameter :: dp=kind(1d0)
real(dp) :: a,b,c
 do
 read(*,*,end=10) a,b,c
 write(*,'(4(es26.17e3,1x))') C1g(a,b,c),C0C1C2(a,b,c),old_C1g(a,b,c),old_C0C1C2(a,b,c)
 end do
10 continue
contains
'''+body+'\n'+old+'\nend program check\n'
    ratios=[10.**(-n) for n in range(30,5,-1)]+[9.99e-11,1e-10,1.001e-10]
    ratios += [.01,.1,.5,.899999,.9,.900001,.9989,.999,.9991,.99999,1-1e-8,1-1e-11,1.]
    cases=[]
    for r in ratios:
        for scale in (1.,125.**2,1e-12):
            for masses,kinds in [((r,r,1.),('B','B')),((1.,1.,r),('A','A')),
                                 ((1.,r,r),('B','C')),((r,1.,1.),('A','C'))]:
                cases.append((tuple(x*scale for x in masses),r,scale,kinds))
    extra=[(0.,0.,1.),(1.,0.,0.),(1.,1.,0.),(0.,1.,1.),(0.,0.,0.),(1.,2.,3.),(.1,1.,.1)]
    inputs=[c[0] for c in cases]+extra
    with tempfile.TemporaryDirectory() as directory:
        src,exe=Path(directory)/'check.f90',Path(directory)/'check'
        src.write_text(driver)
        subprocess.run(['gfortran','-O2','-ffree-line-length-none',str(src),'-o',str(exe)],check=True)
        output=subprocess.run([str(exe)],input='\n'.join(' '.join(map(repr,c)) for c in inputs)+'\n',text=True,capture_output=True,check=True).stdout
    rows=[list(map(float,l.split())) for l in output.splitlines()]
    assert len(rows)==len(inputs)
    maxima=[0.,0.]; old_max=[0.,0.]
    for (masses,r,scale,kinds), row in zip(cases,rows):
        for i,kind in enumerate(kinds):
            ref=reference(mp.mpf(r),kind)/mp.mpf(scale)
            if i==1: ref=-ref
            error=float(abs((mp.mpf(row[i])-ref)/ref))
            maxima[i]=max(maxima[i],error)
            old_max[i]=max(old_max[i],float(abs((mp.mpf(row[i+2])-ref)/ref)))
            # Existing relative mass equality tolerance is 1e-10; branch
            # snapping can change the effective mass by this amount.
            assert error < 1e-10,(masses,kind,error,row)
    for masses,row in zip(extra,rows[len(cases):]):
        assert row[:2]==row[2:],('zero/sentinel behavior changed',masses,row)
    # Independent parameter integrals validate the closed formulas, not just
    # their Taylor expansion. Endpoint logarithms need split quadrature.
    for r in [mp.mpf('1e-30'),mp.mpf('1e-11'),mp.mpf('.999'),mp.mpf('1')]:
        for kind,weight in [('A',lambda x:(1-x)**2/2),('B',lambda x:x*x/2),('C',lambda x:x*(1-x))]:
            integral=mp.quad(lambda x:weight(x)/(1-(1-r)*x),[0,mp.mpf('.9'),1-r,1])
            assert abs(integral/reference(r,kind)-1)<mp.mpf('1e-45'),(r,kind)
    evidence={'status':'PASS (supported equal-adjacent-mass branches only)',
              'positive_cases':len(cases),'zero_and_unsupported_cases':len(extra),
              'max_relative_error':dict(zip(['C1g','C0C1C2'],maxima)),
              'original_max_relative_error':dict(zip(['C1g','C0C1C2'],old_max)),
              'C1g_1_1e-11_1e-11_reference':str(reference(mp.mpf('1e-11'),'B')),
              'candidate_functions_sha256':hashlib.sha256(body.encode()).hexdigest(),
              'patch_sha256':hashlib.sha256((ROOT/'patch_small_ratio.py').read_bytes()).hexdigest(),
              'mpmath':mp.__version__}
    (ROOT/'local/d15-loop-precision.json').write_text(json.dumps(evidence,indent=2)+'\n')
    print(json.dumps(evidence,indent=2))

if __name__=='__main__':
    run(Path(sys.argv[1]) if len(sys.argv)>1 else SRC)
