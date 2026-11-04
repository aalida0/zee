"""Experimental C1g/C0C1C2 correction; generated copies only.

All eight ratio guards are audited here; mass-equality guards are retained.
Positive small ratios use their analytic expression, including finite limits.
For d=1-r <= 0.1 use 19 terms of the convergent series instead of subtracting
nearly equal numbers. The three dimensionless series are respectively
sum d^n/((n+1)(n+2)(n+3)), sum d^n/(2(n+3)), and
sum d^n/((n+2)(n+3)). See LOOP_FUNCTION_AUDIT.md.
"""
import argparse
from pathlib import Path
import re


def corrected_function(body, name):
    if 'D15 stable series' in body:
        raise ValueError('Already patched; use a fresh generated copy')
    # Accept either pristine source or the previous two-guard experiment.
    if body.count('Elseif (Abs(r).lt.eps) Then') + body.count('Elseif (r.eq.0._dp) Then') != 4:
        raise ValueError(f'Unexpected ratio guards in {name}')
    body = body.replace('Elseif (Abs(r).lt.eps) Then', 'Elseif (r.eq.0._dp) Then')
    body = body.replace('epsR=1E-03_dp', 'epsR=1E-01_dp')
    body = body.replace('Real(dp)::m1,m2,r', 'Real(dp)::m1,m2,r,d15s\nInteger :: d15n')
    pattern = rf'(?m)^( +){name}=([^\n]+)\n'
    def replace(m):
        expr = m[2]
        if '**2/' not in expr or 'Log' in expr:
            return m[0]
        # Identify the four original quadratic Taylor expressions explicitly.
        if '/(24._dp*' in expr:
            denom = '(d15n+1._dp)*(d15n+2._dp)*(d15n+3._dp)'
        elif '/(8._dp*' in expr:
            denom = '2._dp*(d15n+3._dp)'
        elif '/(12._dp*' in expr:
            denom = '(d15n+2._dp)*(d15n+3._dp)'
        else:
            raise ValueError(f'Unexpected Taylor expression: {expr}')
        mass = 'm1' if '*m1)' in expr else 'm2'
        sign = '-' if name == 'C0C1C2' else ''
        return (f'{m[1]}! D15 stable series\n'
                f'{m[1]}d15s=0._dp\n{m[1]}Do d15n=18,0,-1\n'
                f'{m[1]}  d15s=d15s*(1._dp-r)+1._dp/({denom})\n'
                f'{m[1]}End Do\n{m[1]}{name}={sign}d15s/{mass}\n')
    result = re.sub(pattern, replace, body)
    if result.count('D15 stable series') != 4:
        raise ValueError(f'Unexpected Taylor branches in {name}')
    return result


def patch(text):
    # Compute everything before writing: malformed input cannot be half patched.
    for name in ('C1g', 'C0C1C2'):
        begin = text.index(f'Real(dp) Function {name}(')
        end = text.index(f'End Function {name}', begin)
        text = text[:begin]+corrected_function(text[begin:end], name)+text[end:]
    return text


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('source', type=Path)
    a = p.parse_args()
    a.source.write_text(patch(a.source.read_text()))
