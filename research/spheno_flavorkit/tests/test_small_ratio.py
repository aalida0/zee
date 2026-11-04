"""Regression for the experimental positive-mass FlavorKit branch."""
import math
import subprocess
import sys
import tempfile
from pathlib import Path

import mpmath as mp

SCRIPT = Path(__file__).resolve().parents[1] / 'patch_small_ratio.py'

def test_positive_ratio_logarithm_is_not_its_zero_mass_placeholder():
    # The equal-lepton-mass C1g branch; independently evaluate at high precision.
    with mp.workdps(60):
        r = (mp.mpf('0.00051099893') / 125)**2
        exact = (3 - 4*r + r*r + 2*mp.log(r)) / (4*(r-1)**3)
        binary = (3 - 4*float(r) + float(r)**2 + 2*math.log(float(r))) / (4*(float(r)-1)**3)
    assert r < mp.mpf('1e-10')
    assert abs((binary-float(exact))/float(exact)) < 1e-14
    assert exact != 0  # The previous generated branch returned zero.

def test_patch_is_scoped_and_rejects_second_application(tmp_path):
    source = tmp_path / 'lfv.f90'
    def function(name):
        return (f'Real(dp) Function {name}(a,b,c)\n'
                '   Else \n     r=m1/m2 \n'
                ' Elseif (Abs(r).lt.eps) Then \n'
                'Else if (Abs(m2in-m3in)/Abs(m2in+m3in).lt.eps) Then\n'
                ' Elseif (Abs(r).lt.eps) Then \n'
                f'End Function {name}\n')
    source.write_text(function('C1g')+function('C0C1C2'))
    subprocess.run([sys.executable, str(SCRIPT), str(source)], check=True)
    text = source.read_text()
    assert text.count('Elseif (r.eq.0._dp) Then') == 2
    assert text.count('Elseif (Abs(r).lt.eps) Then') == 2
    first = source.read_bytes()
    result = subprocess.run([sys.executable, str(SCRIPT), str(source)], capture_output=True)
    assert result.returncode != 0
    assert source.read_bytes() == first

if __name__ == '__main__':
    test_positive_ratio_logarithm_is_not_its_zero_mass_placeholder()
    with tempfile.TemporaryDirectory() as directory:
        test_patch_is_scoped_and_rejects_second_application(Path(directory))
    print('2 tests passed')
