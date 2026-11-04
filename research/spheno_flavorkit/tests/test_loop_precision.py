"""Compile the actual experimental functions and compare with mpmath.

Run after the local reduced backend is generated and patched. No backend
source is modified. Tests include the cutoff and the near-degenerate branch.
"""
from pathlib import Path
import subprocess
import tempfile
import mpmath as mp

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT/'local/SPheno-4.0.5/ZeeTypeII/Observables/FlavorKit_LFV_ZeeTypeII.f90'


def run():
    text = SRC.read_text()
    parts = []
    for name in ('C1g', 'C0C1C2'):
        start = text.index('Real(dp) Function '+name+'(')
        end = text.index('End Function '+name, start)+len('End Function '+name)
        body = text[start:end]
        assert 'Elseif (r.eq.0._dp) Then' in body
        parts.append(body)
        parts.append(body.replace(name, 'old_'+name)
                     .replace('Elseif (r.eq.0._dp) Then', 'Elseif (Abs(r).lt.eps) Then'))
    driver = '''program check
implicit none
integer, parameter :: dp=kind(1d0)
real(dp) :: r
 do
 read(*,*,end=10) r
 write(*,'(5(es25.16e3,1x))') r,C1g(r,r,1._dp),C0C1C2(r,r,1._dp),old_C1g(r,r,1._dp),old_C0C1C2(r,r,1._dp)
 end do
10 continue
contains
'''+ '\n'.join(parts)+'\nend program check\n'
    ratios = ['0','1e-30','1e-16','1e-12','1.67e-11','9.99e-11','1e-10','1.001e-10','1e-8','0.1','0.9','0.9989','0.999','0.9991','0.99999','1']
    with tempfile.TemporaryDirectory() as d:
        src, exe = Path(d)/'check.f90', Path(d)/'check'
        src.write_text(driver)
        subprocess.run(['gfortran','-ffree-line-length-none',str(src),'-o',str(exe)],check=True)
        output = subprocess.run([str(exe)],input='\n'.join(ratios)+'\n',text=True,capture_output=True,check=True).stdout
    mp.mp.dps=80
    for line in output.splitlines():
        r,c1,c0,old1,old0 = map(float,line.split())
        if r == 0:
            assert c1 == c0 == 0
            continue
        rr = mp.mpf(r)
        exact = mp.mpf(1)/6 if r == 1 else (3-4*rr+rr**2+2*mp.log(rr))/(4*(rr-1)**3)
        error = abs((mp.mpf(c1)-exact)/exact)
        # The quadratic Taylor branch has a controlled O((1-r)^3) remainder;
        # just outside it, subtraction in the closed form costs about 1e-6.
        tolerance = mp.mpf('2e-6') if .998 <= r < .9991 else mp.mpf('1e-9')
        assert error < tolerance, (r, float(error), float(tolerance))
        assert abs(c0+c1) < 1e-14*max(1.,abs(c1))
        if r < 1e-10:
            assert old1 == old0 == 0 and c1 != 0
        print(f'{r:.9g} relative error {float(error):.3g}, original {old1:.8g}, patched {c1:.8g}')
    print('PASS: equal-first-mass branch versus 80-digit reference; zero is a regulator placeholder')
    # The independent m2=m3 branch has an untouched logarithmic guard.
    # Evaluate it using a second driver invocation: a positive regulator is not zero.
    other_driver = driver.replace('C1g(r,r,1._dp),C0C1C2(r,r,1._dp),old_C1g(r,r,1._dp),old_C0C1C2(r,r,1._dp)',
                                  'C1g(1._dp,r,r),C0C1C2(1._dp,r,r),old_C1g(1._dp,r,r),old_C0C1C2(1._dp,r,r)')
    with tempfile.TemporaryDirectory() as d:
        src, exe = Path(d)/'other.f90', Path(d)/'other'
        src.write_text(other_driver)
        subprocess.run(['gfortran','-ffree-line-length-none',str(src),'-o',str(exe)],check=True)
        out = subprocess.run([str(exe)],input='1e-11\n',text=True,capture_output=True,check=True).stdout
    _, c1, c0, _, _ = map(float,out.split())
    rr = mp.mpf('1e-11')
    reference = (3-4*rr+rr**2+2*mp.log(rr))/(4*(rr-1)**3)
    assert c1 == 0 and abs(reference) > 10
    print('OPEN: C1g(1,1e-11,1e-11) = 0; 80-digit reference =', mp.nstr(reference, 15), '(different unpatched branch)')
    # Try only the corresponding logarithmically divergent guard in a
    # disposable copy; retain the finite-limit and exact-zero branches.
    start = other_driver.index('Real(dp) Function C1g(')
    stop = other_driver.index('End Function C1g', start)
    section = other_driver[start:stop]
    pivot = section.index('Else if (Abs(m2in-m3in)')
    prefix, tail = section[:pivot], section[pivot:]
    tail = tail.replace('Elseif (Abs(r).lt.eps) Then', 'Elseif (r.eq.0._dp) Then', 1)
    corrected = other_driver[:start]+prefix+tail+other_driver[stop:]
    with tempfile.TemporaryDirectory() as d:
        src, exe = Path(d)/'remedy.f90', Path(d)/'remedy'
        src.write_text(corrected)
        subprocess.run(['gfortran','-ffree-line-length-none',str(src),'-o',str(exe)],check=True)
        out = subprocess.run([str(exe)],input='1e-11\n0\n',text=True,capture_output=True,check=True).stdout.splitlines()
    corrected_value = float(out[0].split()[1])
    assert abs((mp.mpf(corrected_value)-reference)/reference) < mp.mpf('1e-14')
    assert float(out[1].split()[1]) == 0
    print('Remedy in disposable copy: relative error', float(abs((mp.mpf(corrected_value)-reference)/reference)))


if __name__ == '__main__':
    run()
