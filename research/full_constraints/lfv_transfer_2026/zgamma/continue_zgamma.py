#!/usr/bin/env python3
"""Z-exchange only: quadrature implementation and pinned-author controls."""
import copy, glob, hashlib, json, math, sys
from pathlib import Path
import numpy as np
from scipy.integrate import quad
ROOT=Path(__file__).resolve().parents[4]; sys.path.insert(0,str(ROOT))
from module14.physics_adapters.lfv_reference import load_reference
OUT=Path(__file__).resolve().parent
PARENT=OUT.parent
SOURCE=Path(glob.glob('/tmp/zee-public-source/general-2hdm-pheno-*/thdm.py')[0])
EXPECTED='9b4af7aa4bf7bf533a7b82c8c2603d118346424e3b7b5f9f06ab8cb41bc4e193'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(SOURCE)==EXPECTED
mod, refs, inputs=load_reference(SOURCE.parent)
# Reuse the archived source extraction, but project photon terms to zero in its own globals.
for fn in refs.values():
 fn.__globals__['f1']=lambda x: 0.
 fn.__globals__['f2']=lambda x: 0.
def matrix(ip,kind,a):
 for i in range(3):
  for j in range(3):
   ip[f'absrho{kind}{i+1}{j+1}']=abs(a[i,j]); ip[f'argrho{kind}{i+1}{j+1}']=np.angle(a[i,j])
def integral(x,weighted):
 def f(t):
  u=t*(1-t); z=(u-x)/x
  ratio=math.log1p(z)/z if abs(z)>1e-8 else 1-z/2+z*z/3
  return ratio/x*(1-2*u if weighted else 1)
 return 2*quad(f,0,.5,epsabs=2e-9,epsrel=3e-11,limit=500)[0]
def loops(x,y):
 return [y/(x-y)*(integral(x,b)-integral(y,b)) for b in (False,True)]
def calc(m):
 # Standalone parameter integrals and compact tensor contractions, both chiralities.
 ans=[0j,0j]
 for mass,Q,vz,n,rho,up in [(m.mt,m.Qu,m.vZu,3,m.rhou(3,3),True),(m.mc,m.Qu,m.vZu,3,m.rhou(2,2),True),(m.mb,m.Qd,m.vZd,3,m.rhod(3,3),False),(m.mtau,m.Qe,m.vZe,1,m.rhol(3,3),False)]:
  pref=n*m.alphaQED*Q/(4*math.pi)*mass/m.mmu*m.vev**2*vz*m.vZe/4
  for k,M in enumerate((m.Mh1,m.Mh2,m.Mh3),1):
   f3,f4=loops(mass**2/M**2,mass**2/m.MZ**2)
   q=m.q2(k); q1=m.q1(k)
   for h in range(2):
    L=(h==0); ell=m.rhol(1,2) if L else m.rhols(2,1)
    z=q.conjugate() if L else q
    # Relative up/down conjugations follow Eqs. 54-55.
    if up:
     a=rho.conjugate() if L else rho
     b=rho if L else rho.conjugate()
     t=(f4+f3)*a*abs(q)**2+(f4-f3)*b*z*z
    else:
     a=rho if L else rho.conjugate()
     b=rho.conjugate() if L else rho
     t=(f4+f3)*a*z*z+(f4-f3)*b*abs(q)**2
    ans[h]+=pref/M**2*ell*(t+2*f4*mass/m.vev*q1*z)
 return np.array(ans,dtype=complex)
def pair(z): return [float(z.real),float(z.imag)]
def source(m): return np.array([sum(refs[c](m,2,1)) for c in ('L','R')])
def configure(p,d):
 ip=copy.deepcopy(inputs); ip.update(theta12=p['beta']-p['alpha'],theta13=0.,theta23=0.,Mh1=p['mh1'],Mh2=p['mh2'],Mh3=p['ma'],MHp=p['mH1'],vev=p['v'])
 matrix(ip,'l',d/math.sqrt(2)); zero=np.zeros((3,3),complex); matrix(ip,'u',zero);matrix(ip,'d',zero)
 m=mod.thdm(ip); u=zero.copy(); down=zero.copy()
 u[2,2]=m.mt/p['v']/math.tan(p['beta']);u[1,1]=m.mc/p['v']/math.tan(p['beta']);down[2,2]=-m.mb/p['v']*math.tan(p['beta']);matrix(ip,'u',u);matrix(ip,'d',down)
 return mod.thdm(ip)
def controls():
 cases=[]
 for idx in range(2):
  ip=copy.deepcopy(inputs);ip.update(theta12=.63+idx*.24,theta13=.16-idx*.23,theta23=-.21+idx*.38,Mh1=125.,Mh2=410.+idx*67,Mh3=530.+idx*29)
  d=np.zeros((3,3),complex);d[0,1]=(.03+.07j)*(idx+1);d[1,0]=(-.04+.06j)*(idx+1);d[2,2]=.12-.09j
  u=np.zeros((3,3),complex);u[2,2]=.37+.19j;u[1,1]=-.025+.013j
  b=np.zeros((3,3),complex);b[2,2]=-.16+.08j
  for kind,mat in [('l',d/math.sqrt(2)),('u',u),('d',b)]:matrix(ip,kind,mat)
  m=mod.thdm(ip); got=calc(m); ref=source(m); err=abs(got-ref)/np.maximum(abs(ref),1e-300)
  cases.append({'case':idx+1,'independent_c':[pair(x) for x in got],'author_c':[pair(x) for x in ref],'relative_errors':err.tolist()})
  if max(err)>2e-7: raise RuntimeError(json.dumps(cases,indent=2))
  for ij,h in [((0,1),0),((1,0),1)]:
   isolated=d.copy(); isolated[0,1]=isolated[1,0]=0;isolated[ij]=d[ij];matrix(ip,'l',isolated/math.sqrt(2)); mi=mod.thdm(ip); aa=calc(mi);bb=source(mi)
   assert abs(aa[h])>0 and abs(aa[1-h])<1e-30 and abs(bb[1-h])<1e-30 and abs(aa[h]-bb[h])/abs(bb[h])<2e-7
 return cases
if __name__=='__main__':
 try: tests=controls()
 except Exception as e:
  (OUT/'CONTINUATION_TESTS.json').write_text(json.dumps({'status':'FAIL','discrepancy':str(e)},indent=2)+'\n');raise
 archive=ROOT/'validation/module12/d12_benchmarks.json';assert sha(archive)=='f31ef3ccb64c3e4ff53131d35d52c21536b951a01e2c3924af766b7b2adf1cd8'
 groups=json.loads(archive.read_text())['groups']; baseline=json.loads((PARENT/'BASELINE_REPLAY.json').read_text())['cards'];rows=[]
 for g,base in zip(groups,baseline):
  w=g['witnesses']['low_joint'];assert w['id']==base['id'];p=w['module2_input']['scalar']['record']['physical'];d=w['yukawas']['D'];D=np.array(d['real'])+1j*np.array(d['imag']); m=configure(p,D)
  # Same charged-lepton inputs as original witness and archived comparison.
  ip=copy.deepcopy(m.ip);ml=w['module2_input']['lepton_masses_GeV'];ip.update(melectron=ml[0],mmuon=ml[1],mtau=ml[2]);m=mod.thdm(ip)
  independent=calc(m); reference=source(m); card_errors=abs(independent-reference)/np.maximum(abs(reference),1e-300); assert max(card_errors)<2e-7
  c=-independent/(8*math.pi**2*p['v']**2);b=np.array([complex(base[k]['real'],base[k]['imag']) for k in ('C_L','C_R')]);norm=float(np.vdot(b,b).real);delta=float((2*np.vdot(b,c).real+np.vdot(c,c).real)/norm)
  rows.append({'id':w['id'],'source_comparison_relative_errors':card_errors.tolist(),'scalar_sha256':base['scalar_sha256'],'yukawa_sha256':base['yukawa_sha256'],'baseline_C_GeV_minus2':[pair(x) for x in b],'zgamma_C_GeV_minus2':[pair(x) for x in c],'sum_C_GeV_minus2':[pair(x) for x in b+c],'baseline_BR_partial':base['BR_partial'],'scoped_BR':base['BR_partial']*(1+delta),'relative_interference_shift':delta,'zgamma_to_baseline_norm':float(np.linalg.norm(c)/np.linalg.norm(b)),'sufficient_missing_norm_budget_GeV_minus2':float(1.367785824084e-12-np.linalg.norm(b+c))})
 (OUT/'CONTINUATION_TESTS.json').write_text(json.dumps({'status':'PASS','tolerance_relative':2e-7,'two_complex_controls':tests,'one_sided_controls':'four passed, both chiralities in each case','prior_four_loop_pairs':'preserved in TEST_RESULTS.json; not rerun','photon_comparison':'reused module14/physics_adapters/lfv_reference_evidence.json'},indent=2)+'\n')
 (OUT/'CONTINUATION_RESULT.json').write_text(json.dumps({'status':'SCOPED_NEUTRAL_TRANSFER_VALIDATED','source_sha256':EXPECTED,'archive_sha256':sha(archive),'baseline_sha256':sha(PARENT/'BASELINE_REPLAY.json'),'provenance_sha256':sha(PARENT/'CARD_PROVENANCE.json'),'source_inputs':{'alphaQED':inputs['alphaQED'],'sw2':inputs['sw2'],'MZ':inputs['MZ'],'quark_running_masses_GeV':{'top':m.mt,'charm':m.mc,'bottom':m.mb}},'cards':rows,'physical_lfv':'UNKNOWN','hZ':'NOT_EVALUATED','global_acceptance':None},indent=2)+'\n')
 print(json.dumps({'tests':tests,'cards':rows},indent=2))
