#!/usr/bin/env python3
"""Independent one-dimensional loop controls and frozen chirality falsifier."""
import glob, hashlib, importlib.util, json, math, sys
from pathlib import Path
import numpy as np
from scipy.integrate import quad
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
from module3.core import vertices
from module4.amplitudes import fermion_component
p=glob.glob('/tmp/zee-public-source/general-2hdm-pheno-*/thdm.py')
assert len(p)==1, 'Pinned author source must be supplied in local cache'
p=Path(p[0]); digest=hashlib.sha256(p.read_bytes()).hexdigest()
assert digest=='9b4af7aa4bf7bf533a7b82c8c2603d118346424e3b7b5f9f06ab8cb41bc4e193'
spec=importlib.util.spec_from_file_location('author_thdm',p); author=importlib.util.module_from_spec(spec);spec.loader.exec_module(author)
def f1(x):
 def integrand(t):
  u=t*(1-t); z=(u-x)/x
  return (math.log1p(z)/z if abs(z)>1e-8 else 1-z/2+z*z/3)/x
 return 2*quad(integrand,0,.5,epsabs=1e-10,epsrel=2e-11,limit=500)[0]
def f2(x):
 def integrand(t):
  u=t*(1-t); z=(u-x)/x
  return (1-2*u)*(math.log1p(z)/z if abs(z)>1e-8 else 1-z/2+z*z/3)/x
 return 2*quad(integrand,0,.5,epsabs=1e-10,epsrel=2e-11,limit=500)[0]
rows=[]
for x,y in [(.03,.4),(.8,3.7),(.006,.12),(1.3,.19)]:
 expected=[y/(x-y)*(f1(x)-f1(y)),y/(x-y)*(f2(x)-f2(y))]
 observed=[author.f3(x,y),author.f4(x,y)]
 errors=[abs(a-b)/max(abs(a),abs(b)) for a,b in zip(expected,observed)]
 assert max(errors)<1e-8,(x,y,expected,observed,errors)
 rows.append(dict(x=x,y=y,quadrature=expected,author=observed,relative_errors=errors))
D=np.zeros((3,3),complex); D[0,1]=.3+.4j
v=vertices(D,{'beta':.8,'alpha':.1,'v':246.,'mh1':125.,'mh2':450.,'ma':500.},[.000511,.10566,1.77686])[0 if False else 'h'][0]
clcr,_=fermion_component((v[0,1],v[1,0].conjugate()),1.,173.,125.,.10566,1/137,3,2/3)
assert clcr[0]!=0 and clcr[1]==0
D2=D.conjugate().T
v2=vertices(D2,{'beta':.8,'alpha':.1,'v':246.,'mh1':125.,'mh2':450.,'ma':500.},[.000511,.10566,1.77686])['h'][0]
clcr2,_=fermion_component((v2[0,1],v2[1,0].conjugate()),1.,173.,125.,.10566,1/137,3,2/3)
assert clcr2[0]==0 and abs(clcr2[1]-clcr[0])<abs(clcr[0])*1e-14
out={'author_sha256':digest,'loop_controls':rows,'source_eq54_R_for_D_e_mu':'nonzero','module4_one_sided_D_e_mu':{'C_L':[clcr[0].real,clcr[0].imag],'C_R':[clcr[1].real,clcr[1].imag]},'conjugate_transpose_falsifier':'PASS: nonzero moves from Module4 C_L to C_R with identical complex amplitude','checks_passed':6,'checks_note':'4 loop-pair comparisons and 2 one-sided routing assertions; no source full-amplitude or physical-card validation'}
Path(__file__).with_name('TEST_RESULTS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
