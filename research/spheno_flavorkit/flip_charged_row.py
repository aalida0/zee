"""Apply a charged-scalar row sign flip only in ignored generated code.

The four Yukawa arrays and all photon/W vertices consumed by Gamma2l are
transformed together. Use on a disposable, already instrumented copy.
"""
import argparse
from pathlib import Path

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('source', type=Path)
p.add_argument('--row', type=int, choices=(2,3), default=2)
a = p.parse_args()
s = a.source.read_text()
marker = ' ! **** Gamma2l **** '
if s.count(marker) != 1 or 'D15_ROW_FLIP' in s:
    raise SystemExit('Unexpected source or already transformed')
code = '''
! D15_ROW_FLIP: Hm(2) -> -Hm(2) throughout the Gamma2l vertices.
cplFvFecHmL(:,:,2) = -cplFvFecHmL(:,:,2)
cplFvFecHmR(:,:,2) = -cplFvFecHmR(:,:,2)
cplcFeFvHmL(:,:,2) = -cplcFeFvHmL(:,:,2)
cplcFeFvHmR(:,:,2) = -cplcFeFvHmR(:,:,2)
cplHmcHmVP(2,:) = -cplHmcHmVP(2,:)
cplHmcHmVP(:,2) = -cplHmcHmVP(:,2)
cplcHmVPVWm(2) = -cplcHmVPVWm(2)
cplHmcVWmVP(2) = -cplHmcVWmVP(2)
'''
code = code.replace('(2)', f'({a.row})').replace('(:,:,2)', f'(:,:,{a.row})').replace('(2,:)', f'({a.row},:)').replace('(:,2)', f'(:,{a.row})')
a.source.write_text(s.replace(marker, code + marker))
