"""Research-only corrected 2HDM comparison. Never supplies a physical Zee W dipole.

Run from repository root: python -m research.wgamma_d16.external_2hdm --output ...
Reference source is external, unmodified, Apache-2.0; scalar master functions
are reused, while the sums below are written in the frozen Zee field basis.
"""
import argparse
import ast
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import platform
import subprocess
import sys

import numpy as np
import scipy

PIN = 'b5035cd58d2a7e4a91e9790d045df062b97adffe'
GROUPS = ('1loop','th','ch','bh','tauh','tHp','cHp','tauHp','hZ','kin','HA','HZ','HW')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_reference(path):
    path = Path(path).resolve()
    if subprocess.check_output(['git','-C',str(path),'rev-parse','HEAD'],text=True).strip() != PIN:
        raise ValueError('Unpinned author source')
    for name in ('thdm.py','rge.py','adm.py','example.py','LICENSE.txt'):
        expected = subprocess.check_output(['git','-C',str(path),'show',f'{PIN}:{name}'])
        if (path/name).read_bytes() != expected:
            raise ValueError('Modified author source: '+name)
    sys.path.insert(0,str(path))
    spec = importlib.util.spec_from_file_location('d16_author_thdm',path/'thdm.py')
    ref = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ref)
    return ref


def example_input(path):
    class NumericDivision(ast.NodeTransformer):
        def visit_BinOp(self,node):
            node=self.generic_visit(node)
            if not isinstance(node.op,ast.Div):raise ValueError('Unsupported template arithmetic')
            return ast.Constant(ast.literal_eval(node.left)/ast.literal_eval(node.right))
    tree = NumericDivision().visit(ast.parse((Path(path)/'example.py').read_text()))
    return next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign)
                and any(isinstance(t,ast.Name) and t.id=='testinput' for t in n.targets))


def capture(model,i,j):
    """Observe returned locals without patching or rewriting the author's file."""
    result = {}
    old = sys.getprofile()
    def observe(frame,event,arg):
        if event=='return' and frame.f_code.co_name in ('cL_llpg','cR_llpg'):
            ch = frame.f_code.co_name[1]
            for g in GROUPS:
                result.setdefault(g,np.zeros(2,complex))[0 if ch=='L' else 1] = frame.f_locals[f'c{ch}_llpg_{g}']
    try:
        sys.setprofile(observe)
        total = np.array([model.cL_llpg(i,j),model.cR_llpg(i,j)])
    finally:
        sys.setprofile(old)
    np.testing.assert_allclose(sum(result.values()),total,rtol=3e-14,atol=1e-18)
    return total,result


def strict_input(ref,template,p,D,ml):
    if p['gamma'] != 0 or any(p[k]!=0 for k in ('k1','k2','k12')):
        raise ValueError('Strict singlet-free limit required')
    from module1.scalar_constraints import reconstruct
    from module4.couplings import trilinears
    x = dict(template)
    x['sw2']=1-x['MW']**2/x['MZ']**2
    x['alphaQED']=(2*x['MW']/p['v'])**2*x['sw2']/(4*np.pi)
    x.update(Mh1=p['mh1'],Mh2=p['mh2'],Mh3=p['ma'],MHp=p['mH1'],
             theta12=p['beta']-p['alpha'],theta13=0.,theta23=0.,vev=p['v'],
             melectron=ml[0],mmuon=ml[1],mtau=ml[2])
    lag,_,closure = reconstruct(p)
    assert lag['Mu4']==0
    gs = trilinears(p,lag)
    c,s = math.cos(x['theta12']),math.sin(x['theta12'])
    # Invert G_h/v=c Z3-s Z7 and G_H/v=s Z3+c Z7.
    z3 = (c*gs['h'][1,1]+s*gs['H'][1,1])/p['v']
    z7 = (-s*gs['h'][1,1]+c*gs['H'][1,1])/p['v']
    cbet,sbet=np.cos(p['beta']),np.sin(p['beta'])
    l1,l2,l3,l4,l5=(lag['Lambda'+str(k)] for k in range(1,6))
    l345=l3+l4+l5
    np.testing.assert_allclose(z3,l3+(l1+l2-2*l345)*sbet**2*cbet**2,atol=2e-13)
    np.testing.assert_allclose(z7,-sbet*cbet*(l1*sbet**2-l2*cbet**2+l345*(cbet**2-sbet**2)),atol=2e-13)
    x.update(Z3=float(z3.real),absZ7=float(abs(z7)),argZ7=float(np.angle(z7)))
    masses = ref.thdm(x)
    matrices = {'l':D/np.sqrt(2),
                'u':np.diag([masses.mumt,masses.mc,masses.mt])/p['v']/math.tan(p['beta']),
                'd':-np.diag([masses.mdmt,masses.msmt,masses.mb])/p['v']*math.tan(p['beta'])}
    for f,mat in matrices.items():
        for a in range(3):
            for b in range(3):
                x[f'absrho{f}{a+1}{b+1}']=float(abs(mat[a,b]))
                x[f'argrho{f}{a+1}{b+1}']=float(np.angle(mat[a,b]))
    return x,gs,closure


def mapped_groups(ref,model,p,D,ml,i,j,gs):
    """Independent compact sums using Zee vertices and author master functions.

    i,j are ZERO based. Retains exactly the author's leading-mass truncation.
    The shared scalar master functions are NOT an independent integral check.
    """
    from module3.core import vertices
    from module4.couplings import quarks
    v,al,mw,mz,sw,cw = p['v'],model.alphaQED,model.MW,model.MZ,model.sw,model.cw
    mi = ml[i]
    rho = D/np.sqrt(2)
    delta = p['beta']-p['alpha']
    q1 = (math.cos(delta),math.sin(delta),0.)
    q2 = (-math.sin(delta),math.cos(delta),1j)
    verts = vertices(D,p,ml)
    out = {g:np.zeros(2,complex) for g in GROUPS}
    # Corrected 5.4,5.5: their approximation omits m_j and electron internal flip.
    for k,(C,M) in enumerate(verts.values()):
        for a in (1,2):
            log = 3+2*np.log(ml[a]**2/M**2)
            out['1loop'] += v*v/(4*M*M)*ml[a]/mi*log*np.array([
                rho[j,a]*rho[a,i]*q2[k].conjugate()**2,
                rho[i,a].conjugate()*rho[a,j].conjugate()*q2[k]**2])
        out['1loop'] -= v*v/(12*M*M)*abs(q2[k])**2*np.array([
            (rho@rho.conj().T)[j,i],(rho.conj().T@rho)[j,i]])
        out['1loop'] += v*mi/(4*M*M)*(8/3+2*np.log(mi**2/M**2))*np.array([
            rho[j,i]*q1[k]*q2[k].conjugate(),rho[i,j].conjugate()*q1[k]*q2[k]])
        external = np.array([C[j,i],C[i,j].conjugate()])
        # Corrected 5.7,5.8 rewritten in native PL/PR couplings.
        for group,mass,species,nc,Q,vz in (
            ('th',model.mt,'top',3,2/3,model.vZu),
            ('ch',model.mc,'charm',3,2/3,model.vZu),
            ('bh',model.mb,'bottom',3,-1/3,model.vZd),
            ('tauh',ml[2],'tau',1,-1,model.vZe)):
            internal = C[2,2] if species=='tau' else quarks(mass,species,p)[list(verts)[k]]
            z,y = mass**2/M**2,mass**2/mz**2
            scalar = Q*ref.f2(z)+vz*model.vZe/4*ref.f4(z,y)
            pseudo = Q*ref.f1(z)+vz*model.vZe/4*ref.f3(z,y)
            out[group] += nc*al*Q/(2*np.pi)*mass/mi*v*v/M**2*external*np.array([
                internal.real*scalar+1j*internal.imag*pseudo,
                internal.real*scalar-1j*internal.imag*pseudo])
        # Corrected published 5.14--5.19. Do not copy code extra 1/MW^2.
        G = gs[list(verts)[k]][1,1].real
        out['HA'] += al/(4*np.pi)*v*v/mi/M**2*G*external*ref.f9(p['mH1']**2/M**2)
        out['HZ'] += al*model.vZe/(16*np.pi)*(cw*cw-sw*sw)/(sw*cw)*v*v/mi/M**2*G*external*ref.f10(p['mH1']**2/M**2,mz*mz/M**2)
        out['HW'] += al/(32*np.pi*sw*sw)*v*v/mi/M**2*G*external*ref.f11(p['mH1']**2/M**2,mw*mw/M**2)
    out['1loop'][0] += v*v/(12*p['mH1']**2)*(rho@rho.conj().T)[j,i]
    ext = np.array([rho[j,i],rho[i,j].conjugate()])
    tb = (model.mt*(model.mt/v/math.tan(p['beta']))*ref.f5(model.mt**2/p['mH1']**2,model.mt**2/mw**2)
          - model.mb*(model.mb/v*math.tan(p['beta']))*ref.f6(model.mt**2/p['mH1']**2,model.mt**2/mw**2))
    out['tHp'] = al/(8*np.pi*sw*sw)*v*v/mi/p['mH1']**2*tb*ext
    wh = mw*mw/p['mH1']**2
    common = al/(16*np.pi*sw*sw)*v*v/mi/p['mH1']**2*np.log(wh)/(1-wh)
    out['cHp'] = common*model.mc**2/v/math.tan(p['beta'])*(13+4*np.log(model.mc**2/p['mH1']**2)+4*np.log(model.mc**2/mw**2))*ext
    out['tauHp'] = common*ml[2]*ext*np.array([rho[2,2].conjugate(),rho[2,2]])
    # Kinetic 5.12,5.13; compare only their gauge-invariant aggregate.
    for k,M in enumerate((p['mh1'],p['mh2'],p['ma'])):
        if k==0:continue
        z,z0,w,w0 = mz*mz/M**2,mz*mz/p['mh1']**2,mw*mw/M**2,mw*mw/p['mh1']**2
        qq = q1[k]*np.array([q2[k].conjugate(),q2[k]])*ext
        out['hZ'] += -model.el*al/(48*np.pi*sw*cw)*v*v/mi/mz*qq*(
            model.vZe**2*(ref.f7p(z)-ref.f7p(z0))+model.aZe**2*(ref.f7m(z)-ref.f7m(z0)))
        out['kin'] += model.el*al/(32*np.pi)*v*v/mi*qq*(
            model.vZe/mz*(ref.f8a(z,cw*cw)-ref.f8a(z0,cw*cw))
            +model.vZe/(sw*sw*mz)*(ref.f8b(z,cw*cw)-ref.f8b(z0,cw*cw))
            +2/(sw*mw)*(ref.f8c(w)-ref.f8c(w0))
            +1/(sw**3*mw)*(ref.f8d(w)-ref.f8d(w0)+ref.f8e(w,wh)-ref.f8e(w0,wh)))
    return out


def pack(x):
    if isinstance(x,np.ndarray):return [pack(a) for a in x]
    if isinstance(x,complex):return [float(x.real),float(x.imag)]
    if isinstance(x,dict):return {k:pack(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [pack(a) for a in x]
    if isinstance(x,np.generic):return x.item()
    return x


def compare(ref,template,p,D,ml,i,j):
    from module3.core import vertices,dipole_ledger
    from module4.amplitudes import fermion_component
    from module4.charged_scalar import component
    from module4.couplings import quarks
    x,gs,closure = strict_input(ref,template,p,D,ml)
    model = ref.thdm(x)
    total,parts = capture(model,i+1,j+1)
    mapped = mapped_groups(ref,model,p,D,ml,i,j,gs)
    scale = -1/(8*np.pi**2*p['v']**2)
    errors = {}
    for g in GROUPS:
        errors[g]=float(max(abs(mapped[g]-parts[g]))/max(1e-30,max(abs(parts[g]))))
        if g=='HW':
            # Exact reproducible source/paper discrepancy; never silently repair.
            np.testing.assert_allclose(mapped[g]/model.MW**2,parts[g],rtol=3e-11,atol=2e-18)
            if max(abs(parts[g]))>1e-14:assert errors[g]>100
        else:
            np.testing.assert_allclose(mapped[g],parts[g],rtol=3e-11,atol=2e-18,err_msg=g)
    # Independent quadrature in frozen Module4, photon projection only.
    photon = np.zeros(2,complex); scalar = np.zeros(2,complex)
    for name,(C,M) in vertices(D,p,ml).items():
        ext = (C[j,i],C[i,j].conjugate())
        scalar += component(ext,gs[name][1,1],p['mH1'],M,ml[i],model.alphaQED)[0]
        for mass,species,nc,Q in ((model.mt,'top',3,2/3),(model.mc,'charm',3,2/3),
                                 (model.mb,'bottom',3,-1/3),(ml[2],'tau',1,-1)):
            cf = C[2,2] if species=='tau' else quarks(mass,species,p)[name]
            photon += fermion_component(ext,cf,mass,M,ml[i],model.alphaQED,nc,Q)[0]
    # Re-evaluate author code at zero Z vector currents: neutral fermion terms
    # then contain photons only. No W term is extracted by this projection.
    saved = model.vZu,model.vZd,model.vZe
    model.vZu=model.vZd=model.vZe=0.
    _,photon_parts = capture(model,i+1,j+1)
    model.vZu,model.vZd,model.vZe = saved
    author_photon = scale*sum(photon_parts[g] for g in ('th','ch','bh','tauh'))
    np.testing.assert_allclose(photon,author_photon,rtol=3e-10,atol=1e-23)
    np.testing.assert_allclose(scalar,scale*parts['HA'],rtol=3e-10,atol=1e-23)
    one = dipole_ledger(np.zeros((3,3),complex),D,p,ml,i,j)
    frozen_one = sum(np.array([r['C_L'],r['C_R']]) for r in one.values())
    width = model.Gamma_l_to_lp_gamma(i+1,j+1)
    converted_width = model.alphaQED*ml[i]**5/4*sum(abs(scale*total)**2)
    np.testing.assert_allclose(converted_width,width,rtol=4e-14)
    # Neutral and charged vertex checks, independently reconstructing Higgs basis.
    for k,(C,M) in enumerate(vertices(D,p,ml).values(),1):
        expected = model.q1(k)*np.diag(np.array(ml)/p['v'])+D/np.sqrt(2)*model.q2s(k)
        np.testing.assert_allclose(C,expected,rtol=2e-14,atol=1e-17)
        np.testing.assert_allclose(gs[list(vertices(D,p,ml))[k-1]][1,1],
            p['v']*(model.q1(k)*model.Z3+model.ReZ7q2(k)),atol=1e-12)
    return dict(physical=p,D=pack(D),F=pack(np.zeros((3,3),complex)),channel=[i+1,j+1],
        author_input=x,closure=closure,author_c_LR=total,groups_c_LR=parts,
        author_two_loop_c_LR=total-parts['1loop'],
        full_published_comparison=('PASS' if max(abs(sum(mapped.values())-total))<3e-11*max(abs(total)) else 'FAIL_HW'),
        published_sum_c_LR=sum(mapped.values()),C_LR_GeV_minus2=scale*total,
        published_HW_c_LR=mapped['HW'],
        published_minus_code_c_LR=sum(mapped.values())-total,
        group_max_relative_residual=errors,width_GeV=width,
        photon_frozen=photon,photon_author=author_photon,
        scalar_photon_frozen=scalar,scalar_photon_author=scale*parts['HA'],
        one_loop_frozen=frozen_one,one_loop_author=scale*parts['1loop'],
        one_loop_difference=frozen_one-scale*parts['1loop'])


def run(root,reference):
    root = Path(root).resolve();sys.path.insert(0,str(root))
    ref=load_reference(reference);template=example_input(reference)
    # Execute the unmodified example, capture its entire output for provenance.
    proc=subprocess.run([sys.executable,'example.py'],cwd=reference,text=True,capture_output=True,check=True)
    base=json.loads((root/'module1/example.json').read_text())['physical']
    ml=[0.00051099895,0.1056583755,1.77693]
    records=[]
    for n in range(2):
        p=dict(base,gamma=0.,k1=0.,k2=0.,k12=0.,mH2=1e4,
               alpha=0.4+0.13*n,beta=1.1-0.18*n,mH1=420.+150*n,
               mh2=580.7+90*n,ma=633.7+60*n)
        rng=np.random.default_rng(241017313+n)
        D=(rng.normal(size=(3,3))+1j*rng.normal(size=(3,3)))*0.003
        for i,j in ((1,0),(2,0),(2,1)):
            records.append(compare(ref,template,p,D,ml,i,j))
    # Also demonstrate full numerical agreement on two consistent restricted
    # potentials Z3=Z7=0. W/kinetic and charged-fermion groups remain nonzero.
    # Generic nonzero-potential discrepancies above remain in the same evidence.
    for record in list(records)[::3]:
        p=dict(record['physical']);d=np.array(record['D']);d=d[:,:,0]+1j*d[:,:,1]
        def zvalues(point):
            xx,_,_=strict_input(ref,template,point,d,ml)
            return np.array([xx['Z3'],xx['absZ7']*np.cos(xx['argZ7'])])
        z=zvalues(p)
        dzsoft=zvalues(dict(p,m12sq=p['m12sq']+10000))-z
        dzmass=zvalues(dict(p,mH1=np.sqrt(p['mH1']**2+10000)))-z
        step=np.linalg.solve(np.array([dzsoft,dzmass]).T,-z)*10000
        assert p['mH1']**2+step[1]>0
        p.update(m12sq=float(p['m12sq']+step[0]),mH1=float(np.sqrt(p['mH1']**2+step[1])))
        for i,j in ((1,0),(2,0),(2,1)):
            r=compare(ref,template,p,d,ml,i,j)
            assert r['full_published_comparison']=='PASS'
            r['restricted_potential']='Z3=Z7=0 up to floating precision'
            records.append(r)
    # Null LFV must vanish for every author group.
    p=records[0]['physical'];D=np.diag([.001,.002,.003]).astype(complex)
    x,_,_=strict_input(ref,template,p,D,ml)
    _,null=capture(ref.thdm(x),2,1)
    assert all(np.max(abs(a))==0 for a in null.values())
    # A removed singlet mass must have no effect on ANY mapped common group.
    p2=dict(p,mH2=2e4)
    x2,_,_=strict_input(ref,template,p2,D,ml)
    assert x==x2
    # Full kinetic set is charged-mass dependent; do not multiply it by mixing.
    d=np.array(records[0]['D']);d=d[:,:,0]+1j*d[:,:,1]
    x1,_,_=strict_input(ref,template,p,d,ml)
    p3=dict(p,mH1=850.)
    x3,_,_=strict_input(ref,template,p3,d,ml)
    _,a=capture(ref.thdm(x1),2,1);_,b=capture(ref.thdm(x3),2,1)
    assert max(abs(a['kin']-b['kin']))>1e-12
    # At fixed dimensionless couplings, common rescaling of all masses and v
    # leaves dimensionless c invariant. The HW code term instead scales 1/L^2.
    scaled=dict(x1)
    for key in ('MW','MZ','vev','Mh1','Mh2','Mh3','MHp','melectron','mmuon','mtau',
                'MTpole','mbmb','mcmc','ms_at_2GeV','md_at_2GeV','mu_at_2GeV'):
        scaled[key]*=2
    _,sc=capture(ref.thdm(scaled),2,1)
    np.testing.assert_allclose(sc['HW'],a['HW']/4,rtol=2e-13,atol=1e-22)
    tracked=['module3/core.py','module4/amplitudes.py','module4/charged_scalar.py',
             'module4/couplings.py','module4/native_evidence.json',
             'research/wgamma_d16/matching.py','research/wgamma_d16/gauge_ledger.json',
             'research/spheno_flavorkit/d15_component_evidence.json']
    return pack(dict(status='PARTIAL_2HDM_REFERENCE_COMPARISON',
        restricted_Z3_Z7_zero_full_comparison='PASS_TWO_COMPLEX_SPECTRA_THREE_CHANNELS',
        reference_reproduction='PASS',
        common_groups_except_HW='PASS',
        strict_full_published_coefficient_comparison='FAIL_HW_EXTRA_INVERSE_MW_SQUARED_IN_AUTHOR_CODE',
        scope='Independent field-basis sums; shared author master functions; independent frozen photon quadratures; no full Zee W matching',
        physical_Zee_W=dict(C_L=None,C_R=None,coherent_inclusion=False),
        author_SHA=PIN,author_license='Apache-2.0',author_files={n:sha(Path(reference)/n) for n in ('thdm.py','rge.py','adm.py','example.py','LICENSE.txt')},
        comparison_source_sha256=sha(__file__),
        environment=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__),
        example_stdout=proc.stdout,example_stdout_sha256=hashlib.sha256(proc.stdout.encode()).hexdigest(),
        frozen_hashes={n:sha(root/n) for n in tracked},records=records,
        checks=dict(null_all_groups='PASS',removed_singlet_mass_independence='PASS',
                    charged_mass_dependence_kin=float(max(abs(a['kin']-b['kin']))),
                    HW_code_rescaling_c_at_doubled_mass=sc['HW'],HW_original=a['HW'])),)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2])
    ap.add_argument('--reference',type=Path)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--require-full',action='store_true',help='Exit 2 while generic published/source consistency fails')
    args=ap.parse_args()
    reference=args.reference or args.root/'research/wgamma_d16/local/general-2hdm-pheno'
    evidence=run(args.root,reference)
    args.output.write_text(json.dumps(evidence,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print(evidence['status'],len(evidence['records']),'complex channel comparisons; expected HW discrepancy retained')
    if args.require_full and any(r['full_published_comparison']!='PASS' for r in evidence['records']):
        raise SystemExit(2)

if __name__=='__main__':main()
