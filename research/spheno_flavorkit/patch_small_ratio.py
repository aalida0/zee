"""Preserve nonzero lepton masses in two logarithmic FlavorKit loop functions.

Experimental generated copy only. The existing zero-mass behavior remains
unchanged. For m1=m2<m3, the published analytical expressions are finite for
any positive r, but the generated branch sets them to zero when r<1e-10.
"""
import argparse
from pathlib import Path

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('source', type=Path)
a = p.parse_args()
s = a.source.read_text()
for name in ('C1g', 'C0C1C2'):
    begin = s.index(f'Real(dp) Function {name}(')
    end = s.index(f'End Function {name}', begin)
    part = s[begin:end]
    # Only the first equal-mass branch's m1 < m3 limit is logarithmically
    # singular; leave all other accuracy and degeneracy branches untouched.
    pivot = part.index('   Else \n     r=m1/m2')
    limit = part.index('Else if (Abs(m2in-m3in)', pivot)
    section = part[pivot:limit]
    old = 'Elseif (Abs(r).lt.eps) Then'
    if section.count(old) != 1:
        raise SystemExit(f'Unexpected source in {name}; no change made')
    section = section.replace(old, 'Elseif (r.eq.0._dp) Then')
    s = s[:begin] + part[:pivot] + section + part[limit:] + s[end:]
a.source.write_text(s)
