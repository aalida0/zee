"""Canonical symbolic comparison of emitted PreSARAH coefficient expressions."""
from pathlib import Path
import hashlib
import json
import re
import sys
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication, convert_xor

ROOT=Path(__file__).resolve().parent
INSTALLED=Path.home()/'.Mathematica/Applications/SARAH-4.15.4/FlavorKit/LFV/Operators/Gamma2l.m'
GENERATED=ROOT/'local/PreSARAH-1.0.3/Output/Gamma2l.m'


def coefficients(path):
    s=path.read_text()
    # The accompanying TeX strings contain Mathematica InputForm before TeX
    # substitution. Compare exact rational polynomials, keeping integral names,
    # mass arguments, coupling chirality and signs distinct.
    pattern=r'StringReplace\["([^"\n]*)",SA`SPhenoTeXSub\]'
    expressions=[]
    for match in re.finditer(pattern,s):
        prefix=s[max(0,match.start()-60):match.start()]
        if not re.search(r'OA(?:2lS[LR]|1[LR])= &',prefix):
            continue
        label=re.search(r'(OA(?:2lS[LR]|1[LR]))= &',prefix)[1]
        expr=re.sub(r'I_(\d+)',r'loop\1',match[1])
        names=set(re.findall(r'[A-Za-z][A-Za-z0-9_]*',expr))
        funcs=set(re.findall(r'([A-Za-z][A-Za-z0-9_]*)\(',expr))
        local={n:(sp.Function(n) if n in funcs else sp.Symbol(n)) for n in names}
        expressions.append((label,parse_expr(expr,local_dict=local,transformations=standard_transformations+(implicit_multiplication,convert_xor))))
    # Verify executable Fortran strings too, not merely their TeX siblings.
    emitted=[]
    for raw in re.findall(r'WriteString(?:FLB)?\[file,"((?:\\.|[^"\\])*)"',s):
        value=json.loads('"'+raw+'"',strict=False)
        match=re.fullmatch(r'\s*(OA(?:2lS[LR]|1[LR]))=\1\+(.*?)\s*',value)
        if not match:
            continue
        expr=re.sub(r'\bint(\d+)\b',r'loop\1',match[2].replace('_dp','').replace('**','^'))
        names=set(re.findall(r'[A-Za-z][A-Za-z0-9_]*',expr))
        funcs=set(re.findall(r'([A-Za-z][A-Za-z0-9_]*)\(',expr))
        local={n:(sp.Function(n) if n in funcs else sp.Symbol(n)) for n in names}
        form=sp.nsimplify(parse_expr(expr,local_dict=local,transformations=standard_transformations+(implicit_multiplication,convert_xor)),rational=True)
        emitted.append((match[1],form))
    assert len(emitted)==len(expressions),(len(emitted),len(expressions))
    for (label,tex),(label2,fortran) in zip(expressions,emitted):
        assert label==label2 and sp.expand(tex-fortran)==0,(label,tex,fortran)
    integrals=re.findall(r'WriteString\[file,"  (int\d+)=(.*?)\\n"',s)
    return expressions,integrals


def main():
    generated=Path(sys.argv[1]) if len(sys.argv)>1 else GENERATED
    a,ia=coefficients(INSTALLED); b,ib=coefficients(generated)
    assert len(a)==len(b)>0,(len(a),len(b))
    results=[]
    for n,((label,x),(other,y)) in enumerate(zip(a,b)):
        assert label==other,(n,label,other)
        results.append({'index':n,'operator':label,'equal':sp.expand(x-y)==0})
    evidence={'expressions':results,'all_equal':all(r['equal'] for r in results),
              'integral_assignments_equal':ia==ib,
              'integral_assignment_count':len(ia),
              'installed_sha256':hashlib.sha256(INSTALLED.read_bytes()).hexdigest(),
              'regenerated_sha256':hashlib.sha256(generated.read_bytes()).hexdigest(),
              'sympy':sp.__version__}
    (ROOT/'local/d15-projector-comparison.json').write_text(json.dumps(evidence,indent=2)+'\n')
    print(json.dumps(evidence,indent=2))
    assert evidence['all_equal'] and evidence['integral_assignments_equal']

if __name__=='__main__': main()
