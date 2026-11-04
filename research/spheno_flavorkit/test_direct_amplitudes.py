"""Independent vertex-level dipole stress tests of actual generated Gamma2l.

Calls compiled generated code on new complex matrices and masses; does not
assert scalar-vacuum/neutrino eligibility. Scalar loop subset, massless nu,
zero external masses in loop integrals, external chirality flips retained.
"""
from pathlib import Path
import sys
import subprocess
import json
import hashlib
import math
import numpy as np
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parents[1]))
from module3.core import dipole_ledger, vertices
B=ROOT/'local/SPheno-4.0.5'
ML=np.array([.00051099895,.1056583755,1.77686])
E=math.sqrt(4*math.pi/137.035999084)


def driver():
    return '''program direct
use FlavorKit_LFV_ZeeTypeII
implicit none
complex(dp) :: z332(3,3,2),hl(3,3,2),hr(3,3,2),al(3,3,2),ar(3,3,2),z333(3,3,3)
complex(dp) :: fl(3,3,3),fr(3,3,3),bl(3,3,3),br(3,3,3),z33(3,3),e33(3,3),hmvp(3,3),z3(3),z0,ol,orr,o1l,o1r
real(dp) :: leptons(3),mh(2),ma(2),mc(3),e
integer :: id,i,j,k,ii,jj
z332=0;z333=0;z33=0;z3=0;z0=0
 do
 read(*,*,end=10) id,ii,jj,e
 read(*,*) leptons,mh,ma,mc
 mf_l=leptons;mf_l2=leptons**2
 e33=0;hmvp=0
 do i=1,3
 e33(i,i)=e;hmvp(i,i)=-e
 end do
 do k=1,2
 do j=1,3
 do i=1,3
 read(*,*) hl(i,j,k),hr(i,j,k),al(i,j,k),ar(i,j,k)
 end do
 end do
 end do
 do k=1,3
 do j=1,3
 do i=1,3
 read(*,*) fl(i,j,k),fr(i,j,k),bl(i,j,k),br(i,j,k)
 end do
 end do
 end do
 call CalculateGamma2l(ii,jj,1,.false.,ma,ma**2,leptons,leptons**2,mh,mh**2,mc,mc**2, &
 80._dp,6400._dp,91._dp,8281._dp,al,ar,hl,hr,e33,e33,z33,z33,bl,br,z33,z33,z3,z0,fl,fr,z33,z33,hmvp,z3,ol,orr,o1l,o1r)
 write(*,'(a,1x,i6,1x,4(es26.17e3,1x))') 'RESULT',id,real(-ol/(2*e*leptons(ii)),dp),aimag(-ol/(2*e*leptons(ii))), &
 real(-orr/(2*e*leptons(ii)),dp),aimag(-orr/(2*e*leptons(ii)))
 end do
10 continue
end program direct
'''


def encode(z):return f'({complex(z).real:.17e},{complex(z).imag:.17e})'


def inputs(n,p,F,D,selected,i=1,j=0):
    hl=np.zeros((3,3,2),complex);hr=hl.copy();al=hl.copy();ar=hl.copy()
    fl=np.zeros((3,3,3),complex);fr=fl.copy();bl=fl.copy();br=fl.copy()
    for name,(c,m) in vertices(D,p,ML).items():
        if name not in selected:continue
        if name=='A':al[:,:,1]=-c;ar[:,:,1]=-c.conj().T
        else:
            k=0 if name=='h' else 1;hl[:,:,k]=-c;hr[:,:,k]=-c.conj().T
    for name,k,d,s in [('H1',1,math.cos(p['gamma']),math.sin(p['gamma'])),('H2',2,-math.sin(p['gamma']),math.cos(p['gamma']))]:
        if name not in selected:continue
        fl[:,:,k]=-s*F;fr[:,:,k]=-d*D.conj().T # R_ka=-d D_ak*
        bl[:,:,k]=fr[:,:,k].conj().T;br[:,:,k]=fl[:,:,k].conj().T
    lines=[f'{n} {i+1} {j+1} {E:.17e}', ' '.join(map(lambda x:repr(float(x)),[*ML,p['mh1'],p['mh2'],91.,p['ma'],80.,p['mH1'],p['mH2']]))]
    for k in range(2):
        for b in range(3):
            for a in range(3):lines.append(' '.join(encode(x[a,b,k]) for x in [hl,hr,al,ar]))
    for k in range(3):
        for b in range(3):
            for a in range(3):lines.append(' '.join(encode(x[a,b,k]) for x in [fl,fr,bl,br]))
    ledger=dipole_ledger(F,D,p,ML,i,j)
    expected=np.zeros(2,complex)
    for name in selected:
        keys=[name] if name in ['h','H','A'] else [name+'_D',name+'_F']
        for key in keys:expected+=np.array([ledger[key]['C_L'],ledger[key]['C_R']])
    return '\n'.join(lines),expected


def main():
    proof=ROOT/'local/crossing_bridge/projector-evidence.json'
    assert json.loads(proof.read_text())['status']=='PASS'
    out=ROOT/'local/d15_direct_amplitudes';out.mkdir(exist_ok=True)
    src=out/'direct.f90';src.write_text(driver());exe=out/'direct'
    subprocess.run(['gfortran','-ffree-line-length-none','-I'+str(B/'include'),'-I'+str(B/'ZeeTypeII'),str(src),'-L'+str(B/'lib'),'-Wl,--start-group','-lSPhenoZeeTypeII','-lSPheno','-Wl,--end-group','-o',str(exe)],check=True)
    rng=np.random.default_rng(151103);cases=[];payload=[]
    def add(label,p,F,D,selected,i=1,j=0):
        text,expected=inputs(len(cases),p,F,D,selected,i,j)
        payload.append(text);cases.append((label,expected))
    for n in range(6):
        p=dict(v=246.21965,mh1=125.25,mh2=float(rng.uniform(180,750)),ma=float(rng.uniform(170,800)),mH1=float(rng.uniform(160,400)),mH2=float(rng.uniform(450,1000)),alpha=float(rng.uniform(-1,1)),beta=float(rng.uniform(.2,1.2)),gamma=float(rng.uniform(-.7,.7)))
        D=.012*(rng.normal(size=(3,3))+1j*rng.normal(size=(3,3)))
        F=.007*(rng.normal(size=(3,3))+1j*rng.normal(size=(3,3)));F=F-F.T
        allstates=['h','H','A','H1','H2']
        for state in allstates:add(f'{n}:{state}',p,F,D,[state])
        add(f'{n}:sum',p,F,D,allstates)
        add(f'{n}:reverse',p,F,D,allstates,0,1)
        add(f'{n}:conjugate',p,F.conj(),D.conj(),allstates)
        phases=np.exp(1j*np.array([.31,-.47,.82]))
        add(f'{n}:rephase',p,phases[:,None]*F*phases[None,:],phases.conj()[:,None]*D*phases[None,:],allstates)
        add(f'{n}:zeroF',p,F*0,D,['H1','H2'])
        add(f'{n}:zeroD',p,F,D*0,['H1','H2'])
        add(f'{n}:zeroCharged',p,F*0,D*0,['H1','H2'])
        add(f'{n}:zeroNeutralLFV',p,F,D*0,['h','H','A'])
        add(f'{n}:gamma0',dict(p,gamma=0.),F,D,['H1','H2'])
        add(f'{n}:degenerate',dict(p,mH2=p['mH1']),F,D,['H1','H2'])
        add(f'{n}:degenerateGamma',dict(p,mH2=p['mH1'],gamma=p['gamma']+.43),F,D,['H1','H2'])
        add(f'{n}:decouple',dict(p,mH1=p['mH1']*10,mH2=p['mH2']*10),F,D,['H1','H2'])
    data='\n'.join(payload)+'\n';(out/'inputs.txt').write_text(data)
    result=subprocess.run([str(exe)],input=data,text=True,capture_output=True)
    (out/'run.log').write_text(result.stdout+result.stderr)
    result.check_returncode()
    records=[]
    for line in result.stdout.splitlines():
        if not line.startswith('RESULT'):continue
        _,index,*values=line.split();index=int(index);v=list(map(float,values));k=np.array([complex(*v[:2]),complex(*v[2:])]);label,c=cases[index]
        residual=abs(k+c.conj());scale=max(np.max(abs(c)),1e-30)
        assert np.all(residual<=1e-10*np.abs(c)+1e-24),(label,k,c,residual)
        records.append({'case':label,'K':[[z.real,z.imag] for z in k],'C':[[z.real,z.imag] for z in c],'max_abs_residual':float(max(residual)),'relative_to_largest_chirality':float(max(residual)/scale)})
    assert len(records)==len(cases)
    bylabel={r['case']:np.array([complex(*z) for z in r['K']]) for r in records}
    transformations=[]
    for n in range(6):
        get=lambda name:bylabel[f'{n}:{name}']
        coherent=get('sum')
        predictions={
            'coherent_sum':(sum((get(x) for x in ['h','H','A','H1','H2']),np.zeros(2,complex)),coherent),
            'conjugate':(coherent.conj(),get('conjugate')),
            'rephase':(coherent*np.exp(1j*(.31+.47)),get('rephase')),
            'reverse':((ML[1]/ML[0])*coherent[::-1].conj(),get('reverse')),
            'decouple':(.01*(get('H1')+get('H2')),get('decouple')),
            'degenerate_gamma':(get('degenerate'),get('degenerateGamma'))}
        for name,(prediction,actual) in predictions.items():
            delta=float(np.max(abs(prediction-actual)))
            relative=delta/max(float(np.max(abs(prediction))),1e-30)
            assert relative<1e-10,(n,name,relative)
            transformations.append({'point':n,'test':name,'relative_residual':relative})
        assert np.max(abs(get('zeroCharged')))==0 and np.max(abs(get('zeroNeutralLFV')))==0
    evidence={'scope':'new vertex-level inputs; scalar one-loop subset only','operator_map_evidence_sha256':hashlib.sha256(proof.read_bytes()).hexdigest(),'seed':151103,'records':records,'transformations':transformations,
              'numerical_criterion':'abs(K+conj(C)) <= 1e-10 abs(C) + 1e-24 GeV^-2 per chirality; no input-scheme uncertainty included',
              'max_relative_to_largest_chirality':max(r['relative_to_largest_chirality'] for r in records),
              'inputs_sha256':hashlib.sha256(data.encode()).hexdigest(),
              'executable_sha256':hashlib.sha256(exe.read_bytes()).hexdigest()}
    (ROOT/'local/d15-direct-amplitudes.json').write_text(json.dumps(evidence,indent=2)+'\n')
    print('cases',len(records),'maximum relative',evidence['max_relative_to_largest_chirality'])
    for r in records:
        if r['relative_to_largest_chirality']>1e-9:print(r['case'],r['relative_to_largest_chirality'])

if __name__=='__main__':main()
