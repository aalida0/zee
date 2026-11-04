"""Instrument ignored generated SPheno files for D15 numerical readback.

Use once on a fresh generated model directory. Diagram increments are raw OA
coefficients, before oo16pi2 and wrapper normalization, for (2,1) only.
"""
import argparse
from pathlib import Path

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('model_dir', type=Path)
a = p.parse_args()
low = a.model_dir / 'Observables/LowEnergy_ZeeTypeII.f90'
fk = a.model_dir / 'Observables/FlavorKit_LFV_ZeeTypeII.f90'
s, t = low.read_text(), fk.read_text()
if 'D15_VERTEX' in s or 'D15_COMPONENT' in t:
    raise SystemExit('Already instrumented; use a fresh generated copy')
marker = ' ! **** Gamma2l **** '
if s.count(marker) != 1:
    raise SystemExit('Unexpected LowEnergy marker')
readback = '''
Write(*,*) 'D15_SM', Alpha_MZ, mf_l, mf_l_mz, MVWm, MVZ, v, vd, vu, g1, g2
Write(*,*) 'D15_MASSES', MFe, MHm, Mhh, MAh
Write(*,*) 'D15_MIXING', ZH, ZA
Do i1=1,3
 Do i2=1,3
  Write(*,*) 'D15_INPUT',i1,i2,ZP(i1,i2),ZEL(i1,i2),ZER(i1,i2), &
    & fzee(i1,i2),Ye(i1,i2),Ye2(i1,i2)
  Do i3=1,2
   Write(*,*) 'D15_NEUTRAL',i1,i2,i3,cplcFeFehhL(i1,i2,i3), &
    & cplcFeFehhR(i1,i2,i3),cplcFeFeAhL(i1,i2,i3),cplcFeFeAhR(i1,i2,i3)
  End Do
  Do i3=1,3
   Write(*,*) 'D15_VERTEX',i1,i2,i3,cplFvFecHmL(i1,i2,i3), &
    & cplFvFecHmR(i1,i2,i3),cplcFeFvHmL(i2,i1,i3),cplcFeFvHmR(i2,i1,i3)
  End Do
 End Do
End Do
'''
s = s.replace(marker, readback + marker)
start = t.index('Subroutine CalculateGamma2l(')
end = t.index('End Subroutine CalculateGamma2l', start)
head, sub, tail = t[:start], t[start:end], t[end:]
decl = 'Complex(dp) ::  int1,int2,int3,int4,int5,int6,int7,int8'
if sub.count(decl) != 1:
    raise SystemExit('Unexpected declaration')
sub = sub.replace(decl, decl + '\nComplex(dp) :: d15oldL,d15oldR')
for tag, comment in [('Ah', '! Loop particles: Ah,bar[Fe],bar[Fe]'),
                     ('Hm', '! Loop particles: Fv,conj[Hm],conj[Hm]'),
                     ('hh', '! Loop particles: hh,bar[Fe],bar[Fe]')]:
    begin = sub.index(comment)
    finish = sub.index('! Loop particles:', begin + len(comment))
    chunk = sub[begin:finish]
    pos = chunk.index('  OA2lSL=OA2lSL+')
    chunk = chunk[:pos] + '  d15oldL=OA2lSL\n  d15oldR=OA2lSR\n' + chunk[pos:]
    pos = chunk.index('  OA1L=OA1L')
    output = ("  If (.not.OnlySM.and.gt1.eq.2.and.gt2.eq.1) &\n"
              f"    & Write(*,*) 'D15_COMPONENT_{tag}',i1,i2,i3,OA2lSL-d15oldL,OA2lSR-d15oldR\n")
    chunk = chunk[:pos] + output + chunk[pos:]
    sub = sub[:begin] + chunk + sub[finish:]
low.write_text(s)
fk.write_text(head + sub + tail)
