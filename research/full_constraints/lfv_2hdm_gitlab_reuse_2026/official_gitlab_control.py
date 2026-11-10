#!/usr/bin/env python3
"""Pinned public general-2hdm-pheno comparison on four frozen Zee cards.

Pure-2HDM single-charged-mass proxies only. NO physical Zee rate.
The corrected upstream thdm.py is never overwritten or silently mocked.
"""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, math, pathlib, sys
import numpy as np

SOURCE_SHA='f31ef3ccb64c3e4ff53131d35d52c21536b951a01e2c3924af766b7b2adf1cd8'
EXPECTED_COMMIT='b5035cd5'
ROOT=pathlib.Path(__file__).resolve().parents[3]
DATA=ROOT/'validation/module12/d12_benchmarks.json'
ME=0.00051099895; MMU=0.1056583755; MTAU=1.77686; V=246.21965
QUARKS={'u':.0022,'c':1.273,'t':172.4,'d':.0047,'s':.093,'b':4.183}

def compmat(o):
    return np.asarray(o['real'])+1j*np.asarray(o['imag'])

def make_input(w, charged_option='bare'):
    p=w['module2_input']['scalar']['record']['physical']; D=compmat(w['yukawas']['D'])
    a,b,g=p['alpha'],p['beta'],p['gamma']
    sa,ca,s,c=math.sin(a),math.cos(a),math.sin(b),math.cos(b)
    sg,cg=math.sin(g),math.cos(g)
    m12=p['m12sq'];md2=p['mH1']**2*cg**2+p['mH2']**2*sg**2
    mn11=p['mh1']**2*ca**2+p['mh2']**2*sa**2
    mn22=p['mh1']**2*sa**2+p['mh2']**2*ca**2
    mn12=(p['mh1']**2-p['mh2']**2)*sa*ca
    soft=m12/(s*c)
    l1=(mn11-m12*s/c)/(V*V*c*c)
    l2=(mn22-m12*c/s)/(V*V*s*s)
    l5=(soft-p['ma']**2)/(V*V)
    l4=2*(soft-md2)/(V*V)-l5
    l3=(mn12+m12)/(V*V*s*c)-l4-l5
    l345=l3+l4+l5
    Z3=l3+(l1+l2-2*l345)*s*s*c*c
    Z7=-s*c*(l1*s*s-l2*c*c+l345*(c*c-s*s))
    mass={'bare':math.sqrt(md2),'H1':p['mH1'],'H2':p['mH2']}[charged_option]
    coup={'alphaQED':1/127.95,'alphasMZ':.118,'sw2':.23129,'sw2MS':.23129,
          'MZ':91.1876,'MW':80.379,'MTpole':QUARKS['t'],
          'mbmb':QUARKS['b'],'mcmc':QUARKS['c'],
          'ms_at_2GeV':QUARKS['s'],'md_at_2GeV':QUARKS['d'],'mu_at_2GeV':QUARKS['u'],
          'melectron':ME,'mmuon':MMU,'mtau':MTAU,
          'Mh1':p['mh1'],'Mh2':p['mh2'],'Mh3':p['ma'],'MHp':mass,'vev':V,
          'theta12':b-a,'theta13':0.,'theta23':0.,
          'Z3':Z3,'absZ7':abs(Z7),'argZ7':math.pi if Z7<0 else 0.}
    rt=math.tan(b)
    rhou=np.diag([QUARKS[k]/(V*rt) for k in ('u','c','t')])
    rhod=np.diag([-QUARKS[k]*rt/V for k in ('d','s','b')])
    rhol=D/np.sqrt(2)
    for kind,matrix in [('u',rhou),('d',rhod),('l',rhol)]:
        for i in range(3):
            for j in range(3):
                z=complex(matrix[i,j]);field=f'{kind}{i+1}{j+1}'
                coup['absrho'+field]=abs(z)
                coup['argrho'+field]=float(np.angle(z)) if z else 0.0
    diag={'benchmark_id':w['id'],'MHp_choice':charged_option,
          'm_doublet_bare':math.sqrt(md2), 'Z3':Z3,'Z7':Z7,
          'neutral_yukawa_basis':'rho_l=D/sqrt(2) RH-row LH-col; theta12=beta-alpha',
          'missing_charged_singlet':True,'complete_Zee':False,
          'global_acceptance':None}
    return coup,diag

def source_decomposition(model,name,i,j):
    """Obtain local named terms from exact pinned public source, in memory only.

    No upstream file modification. Verify coherent source sum against its
    unchanged public cR_llpg / cL_llpg method before reporting any group.
    """
    import inspect, textwrap
    original=getattr(type(model),name)
    src=textwrap.dedent(inspect.getsource(original))
    end_name='cR' if name=='cR_llpg' else 'cL'
    marker='return '+end_name
    if src.count(marker)!=1:raise RuntimeError('Source return changed: '+name)
    groups={
      'one_loop':[f'{end_name}_llpg_1loop'],
      'neutral_fermion':[f'{end_name}_llpg_{k}' for k in ('th','ch','bh','tauh')],
      'charged_fermion':[f'{end_name}_llpg_{k}' for k in ('tHp','cHp','tauHp')],
      'neutral_bosonic':[f'{end_name}_llpg_{k}' for k in ('hZ','kin')],
      'charged_bosonic':[f'{end_name}_llpg_{k}' for k in ('HA','HZ','HW')]
    }
    expression=('{'+','.join(repr(k)+':('+ '+'.join(v)+')' for k,v in groups.items())+
                ','+repr('total')+':'+end_name+'}')
    changed=src.replace(marker,'return '+expression)
    scope={}
    exec(changed,original.__globals__,scope)
    result=scope[name](model,i,j)
    exact=original(model,i,j)
    partsum=sum(z for k,z in result.items() if k!='total')
    scale=max(abs(exact),1e-300)
    if abs(partsum-exact)>1e-12*scale or abs(result['total']-exact)>1e-12*scale:
        raise ArithmeticError('Official Wilson decomposition does not close '+name)
    return result

def cplx(z):
    z=complex(z)
    return [z.real,z.imag]

def run(source,revision,limit=4):
    actual=hashlib.sha256(DATA.read_bytes()).hexdigest()
    if actual!=SOURCE_SHA:raise ValueError('Frozen benchmark SHA mismatch '+actual)
    rows=[g['witnesses']['low_joint'] for g in json.loads(DATA.read_text())['groups']]
    assert len(rows)==4
    py=pathlib.Path(source).resolve()/'thdm.py'
    if not py.is_file():raise FileNotFoundError(py)
    modspec=importlib.util.spec_from_file_location('official_thdm',py)
    mod=importlib.util.module_from_spec(modspec)
    sys.path.insert(0,str(py.parent))
    try:modspec.loader.exec_module(mod)
    finally:sys.path.remove(str(py.parent))
    if not hasattr(mod,'thdm'):raise AttributeError('Official thdm class absent')
    records=[]
    for w in rows[:limit]:
        for mode in ('bare','H1','H2'):
            couplings,diag=make_input(w,mode)
            model=mod.thdm(couplings)
            result=model.Gamma_l_to_lp_gamma(2,1)
            if not isinstance(result,(float,int,np.floating)):
                raise TypeError(f'Official Gamma output unexpected: {type(result)} {result}')
            gam=float(result)
            if not math.isfinite(gam) or gam<0:raise ValueError('Invalid Gamma')
            r=source_decomposition(model,'cR_llpg',2,1)
            l=source_decomposition(model,'cL_llpg',2,1)
            group_keys=('one_loop','neutral_fermion','charged_fermion',
                        'neutral_bosonic','charged_bosonic')
            split={k:{'cR':cplx(r[k]),'cL':cplx(l[k]),
                'c_norm':float(np.hypot(abs(r[k]),abs(l[k])))}
                for k in group_keys}
            r2=sum(r[k] for k in group_keys if k!='one_loop')
            l2=sum(l[k] for k in group_keys if k!='one_loop')
            n1=float(np.hypot(abs(r['one_loop']),abs(l['one_loop'])))
            n2=float(np.hypot(abs(r2),abs(l2)))
            pref=-1/(8*np.pi**2*couplings['vev']**2)
            split['neutral_fermion']['source_K2_norm_GeVminus2']=float(
                np.hypot(abs(r['neutral_fermion']*pref),abs(l['neutral_fermion']*pref)))
            records.append({**diag,'pure_2HDM_Gamma_muegamma_GeV':gam,
              'pure_2HDM_proxy_BR':gam/(6.582119569e-25/2.1969811e-6),
              'official_coherent_Wilson':{'cR':cplx(r['total']),'cL':cplx(l['total'])},
              'official_Wilson_source_groups':split,
              'official_two_loop_to_one_loop_norm_ratio':n2/max(n1,1e-300),
              'Zee_physical_BR':None,'physical_lfv':'UNKNOWN'})
            print(w['id'],mode,'2HDM-only BR',records[-1]['pure_2HDM_proxy_BR'],flush=True)
    return {'status':'OFFICIAL_GITLAB_2HDM_PROXY_ONLY_NOT_PHYSICAL_ZEE',
            'gitlab_revision':revision,
            'external_thdm_py_SHA256':hashlib.sha256(py.read_bytes()).hexdigest(),
            'inputs_SHA256':actual,'results':records,'global_acceptance':None,
            'physical_lfv':'UNKNOWN'}

def main():
    pa=argparse.ArgumentParser()
    pa.add_argument('--source',required=True)
    pa.add_argument('--commit',default=EXPECTED_COMMIT)
    pa.add_argument('--limit',type=int,default=4)
    pa.add_argument('--output',default='official_gitlab_control.json')
    args=pa.parse_args()
    assert args.commit.startswith(EXPECTED_COMMIT), 'Unreviewed upstream revision'
    res=run(args.source,args.commit,args.limit)
    pathlib.Path(args.output).write_text(json.dumps(res,indent=2)+'\n')
if __name__=='__main__':main()
