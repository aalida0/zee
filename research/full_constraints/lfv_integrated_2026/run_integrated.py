#!/usr/bin/env python3
"""Frozen-card hZ source comparison and conservative integrated ledger."""
import ast,copy,csv,glob,hashlib,json,math,sys
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[3]; O=Path(__file__).resolve().parent
sys.path.insert(0,str(R))
from module14.physics_adapters.lfv_reference import load_reference
P=R/'research/full_constraints/lfv_transfer_2026'; A=R/'validation/module12/d12_benchmarks.json'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,x): (O/n).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def pair(z): return [float(z.real),float(z.imag)]
source=Path(glob.glob('/tmp/zee-public-source/general-2hdm-pheno-*/thdm.py')[0]); expected='9b4af7aa4bf7bf533a7b82c8c2603d118346424e3b7b5f9f06ab8cb41bc4e193'
assert sha(source)==expected and sha(A)=='f31ef3ccb64c3e4ff53131d35d52c21536b951a01e2c3924af766b7b2adf1cd8'
mod,_,inp=load_reference(source.parent)
tree=ast.parse(source.read_text()); cls=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='thdm'); refs={}
for c in 'LR':
 fn=copy.deepcopy(next(x for x in cls.body if isinstance(x,ast.FunctionDef) and x.name=='c'+c+'_llpg'))
 name='c'+c+'_llpg_hZ'; fn.body=[x for x in fn.body if isinstance(x,ast.Assign) and isinstance(x.targets[0],ast.Name) and x.targets[0].id==name]+[ast.Return(ast.Name(name,ast.Load()))]
 env=vars(mod).copy();exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),str(source),'exec'),env);refs[c]=env[fn.name]
def matrix(ip,d):
 for i in range(3):
  for j in range(3): ip[f'absrhol{i+1}{j+1}']=abs(d[i,j]);ip[f'argrhol{i+1}{j+1}']=np.angle(d[i,j])
def assembly(m,delta):
 # Independent CP-conserving Eq. 59 assembly using previously integrated f7 differences.
 k=-m.el*m.alphaQED/(48*math.pi*m.sw*m.cw)*m.vev**2/(m.ml(2)*m.MZ)*m.q1(2)*m.q2(2)*(m.vZe**2*delta[0]+m.aZe**2*delta[1])
 return np.array([k*m.rhol(1,2),k*m.rhols(2,1)])
def reference(m): return np.array([refs[c](m,2,1) for c in 'LR'])
deltas=[(-1.424737373,-.8759489842),(-1.722202669,-.9674053207)]
groups=json.loads(A.read_text())['groups']; z=json.loads((P/'zgamma/CONTINUATION_RESULT.json').read_text()); audit=json.loads((R/'research/full_constraints/lfv/TEXTURE_COUPLING_AUDIT.json').read_text())
rows=[]; controls=[]
for idx,(g,old,inv) in enumerate(zip(groups,z['cards'],audit['cards'])):
 w=g['witnesses']['low_joint']; assert w['id']==old['id']==inv['id']; p=w['module2_input']['scalar']['record']['physical']; ml=w['module2_input']['lepton_masses_GeV']; y=w['yukawas']['D']; D=np.array(y['real'])+1j*np.array(y['imag']);ip=copy.deepcopy(inp);ip.update(theta12=p['beta']-p['alpha'],theta13=0.,theta23=0.,Mh1=p['mh1'],Mh2=p['mh2'],Mh3=p['ma'],MHp=p['mH1'],vev=p['v'],melectron=ml[0],mmuon=ml[1],mtau=ml[2]);matrix(ip,D/math.sqrt(2));m=mod.thdm(ip)
 # Use two deliberately nonzero complex controls on each physical scalar spectrum.
 d=np.zeros((3,3),complex);d[0,1]=.03+.07j;d[1,0]=-.04+.06j; ic=copy.deepcopy(ip);matrix(ic,d);mc=mod.thdm(ic); ref=reference(mc); calc=assembly(mc,deltas[0 if idx<2 else 1]);err=np.abs(ref-calc)/np.maximum(np.abs(ref),1e-300); controls.append({'card':w['id'],'source_c':list(map(pair,ref)),'equation_c':list(map(pair,calc)),'relative_error':err.tolist()})
 # Precision limited by published rounded quadrature; no assertion of full-precision validation.
 assert np.max(err)<1e-4, (idx,err,ref,calc)
 h=-reference(m)/(8*math.pi**2*p['v']**2); b=np.array([complex(*x) for x in old['sum_C_GeV_minus2']]); rel=float((2*np.vdot(b,h).real+np.vdot(h,h).real)/np.vdot(b,b).real)
 rows.append({'id':w['id'],'scalar_sha256':old['scalar_sha256'],'yukawa_sha256':old['yukawa_sha256'],'baseline_C':old['baseline_C_GeV_minus2'],'zgamma_C':old['zgamma_C_GeV_minus2'],'hZ_C':None,'hZ_provisional_source_C':list(map(pair,h)),'sum_C':list(map(pair,b+h)),'baseline_plus_zgamma_partial_BR':old['scoped_BR'],'hZ_relative_shift':rel,'partial_BR':old['scoped_BR']*(1+rel),'missing_norm_budget_GeV_minus2':old['sufficient_missing_norm_budget_GeV_minus2'],'invariants':{k:inv[k] for k in ('D_em','D_me','FdagF_em','DdagD_em','DDdag_em')}})
dump('HZ_CONTROLS.json',{'status':'PARTIAL','scope':'CP-conserving Eq 59; two scalar spectra, complex two chiralities; independent archived quadrature rounded; alignment and one-sided tests outstanding','controls':controls})
dump('DIPOLE_TERMS.json',{'status':'VALIDATED_SUBSET','units':'GeV^-2','source':'Altmannshofer et al arXiv:2410.17313v4 Eq 59 and pinned code; cached f7 quadrature note; neutral Zgamma prior validated source','input_scheme':'pinned author example alpha=1/129, sw2=0.23129, MZ=91.188; baseline Module4 original scheme; mixed schemes not assigned a theory uncertainty','photon_double_count':'none; baseline already includes photon','cards':rows,'complete_physical_BR':None})
dump('MATERIALITY.json',{'interpretation':'sufficient missing norm budget conditional on archived 90% limit; not an upper bound or uncertainty','cards':[{'id':r['id'],'invariants':r['invariants'],'missing_norm_budget_GeV_minus2':r['missing_norm_budget_GeV_minus2']} for r in rows]})
dump('INPUT_MANIFEST.json',{'archive_sha256':sha(A),'author_thdm_sha256':sha(source),'zgamma_sha256':sha(P/'zgamma/CONTINUATION_RESULT.json'),'baseline_sha256':sha(P/'BASELINE_REPLAY.json'),'cards':[{'id':r['id'],'scalar_sha256':r['scalar_sha256'],'yukawa_sha256':r['yukawa_sha256']} for r in rows]})
coverage={x:{'status':'UNKNOWN','coefficient':None,'reason':reason} for x,reason in {'mu3e':'full signed off-shell penguin and mixed box vector not validated','muAl_conversion':'UV semileptonic vector, running and nuclear interference not validated','tau_e_gamma':'full leading operator groups not validated','tau_mu_gamma':'full leading operator groups not validated','universality':'not assessed in this execution','h_mu_e':'not assessed in this execution','tau_three_body':'full signed operator vector not validated'}.items()}
dump('OPERATOR_LEDGER.json',{'mu_to_e_gamma':{'status':'VALIDATED_SUBSET','coefficients':'DIPOLE_TERMS.json','omitted':['charged-current two-loop','kin','mixed charged scalar HZ','HW','F gauge']},**coverage})
with (O/'CARD_CONSTRAINT_MATRIX.csv').open('w',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=['card','observable','status','partial_BR','physical_rate','physical_lfv','global_acceptance']);writer.writeheader()
 for r in rows:
  writer.writerow({'card':r['id'],'observable':'mu_to_e_gamma','status':'VALIDATED_SUBSET','partial_BR':r['partial_BR'],'physical_rate':'','physical_lfv':'UNKNOWN','global_acceptance':''})
  for k in coverage: writer.writerow({'card':r['id'],'observable':k,'status':'UNKNOWN','physical_lfv':'UNKNOWN','global_acceptance':''})
dump('RESULT.json',{'status':'LFV_LEADING_SCOPE_INCOMPLETE','model_scope':'four frozen D7/F13 low-texture NO/IO Zee Type II witnesses only','accuracy_scope':'validated neutral hZ and pre-existing neutral Zgamma with frozen baseline; mixed input schemes, no full theory uncertainty','four_cards':[r['id'] for r in rows],'new_validated_groups':[],'unvalidated_groups':['charged-current','kin','mixed charged scalar HZ','HW','F gauge','full mu3e operator vector','semileptonic conversion vector'],'observable_coverage':coverage,'physical_lfv':'UNKNOWN','global_acceptance':None,'source_hashes':{'author':sha(source),'archive':sha(A)},'tests_passed':['two scalar spectra complex both-chirality hZ source controls','frozen hash checks'],'calculations_executed':['hZ complex four-card coefficients and coherent partial rates','coupling invariant and conditional sensitivity ledger']})
print('hZ source controls passed; four cards written')
