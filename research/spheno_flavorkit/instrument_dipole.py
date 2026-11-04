"""Instrument a private generated LowEnergy file to print complex dipoles."""
import argparse
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('source', type=Path)
a = p.parse_args()
s = a.source.read_text()
marker = 'K2R(3,:) = -0.5_dp*K2R(3,:)/sqrt(Alpha_MZ*4*Pi)/mf_l_mz(3)'
if s.count(marker) != 1 or 'PILOT_K2' in s:
    raise SystemExit('Unexpected generated source or already instrumented')
s = s.replace(marker, marker + "\nWrite(*,*) 'PILOT_K2L_21', K2L(2,1)\nWrite(*,*) 'PILOT_K2R_21', K2R(2,1)")
a.source.write_text(s)
