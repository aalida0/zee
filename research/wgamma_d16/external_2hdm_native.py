"""Substitute strict limits into preserved, actual SARAH expressions.
No SARAH startup, model edits, or loop integrations. Requires wolframscript.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import numpy as np


def validate(root,evidence):
    sys.path.insert(0,str(root))
    from module1.scalar_constraints import reconstruct
    from module3.core import vertices
    from module4.couplings import rotations,trilinears,quarks
    from module4.native import wl
    source=root/'module4/native_evidence.json'
    native=json.loads(source.read_text())
    assert native['status']=='VERTEX_COMPONENTS_PASS'
    blocks=[]
    for record in evidence['records'][::3]:
        p=record['physical'];x=record['author_input']
        d=np.array(record['D']);d=d[:,:,0]+1j*d[:,:,1]
        ml=np.array([x['melectron'],x['mmuon'],x['mtau']])
        zh,za,zp=rotations(p);lag,_,_=reconstruct(p)
        sm=np.diag(np.sqrt(2)*ml/p['v']);cb,sb=np.cos(p['beta']),np.sin(p['beta'])
        mats=dict(Ye=cb*sm-sb*d,Ye2=sb*sm+cb*d,Fzee=np.zeros((3,3)),
                  Ue=np.eye(3),Ve=np.eye(3),ZH=zh,ZA=za,ZP=zp,
                  Uu=np.eye(3),Vu=np.eye(3),Ud=np.eye(3),Vd=np.eye(3),
                  Yu=np.diag([0.,0.,172.4])*np.sqrt(2)/p['v']/sb,
                  Yd=np.diag([0.,0.,4.183])*np.sqrt(2)/p['v']/cb)
        e=np.sqrt(4*np.pi*x['alphaQED']);sw=np.sqrt(x['sw2']);cw=np.sqrt(1-x['sw2'])
        rules=[f'{key}[{i+1},{j+1}]->{wl(a)}' for key,mat in mats.items()
               for i,row in enumerate(mat) for j,a in enumerate(row)]
        rules += [f'{key}->{wl(a)}' for key,a in dict(lag,v1=p['v']*cb,v2=p['v']*sb,
                  g1=e/cw,g2=e/sw,ThetaW=np.arcsin(sw)).items()]
        rules += ['Delta[ct1,ct2]->1']
        checks=[]
        def check(key,tensor,expected):
            checks.append('check['+json.dumps(key)+','+tensor+','+wl(expected)+',rules];')
        for k,(name,(C,M)) in enumerate(vertices(d,p,ml).items(),1):
            for ch,a in [('PL',C[0,1]),('PR',C[1,0].conjugate())]:
                check(f'lepton_{{{k}, 1, 2}}',ch,-1j*a)
            for field,species,m in [('Fu','top',172.4),('Fd','bottom',4.183)]:
                a=quarks(m,species,p)[name]
                for ch,z in [('PL',a),('PR',a.conjugate())]:
                    check(f'quark_{{{k}, {field}}}',ch,-1j*z)
        check('charged_plus_{2, 1, 2}','PR',-1j*d[0,1].conjugate())
        check('charged_plus_{2, 1, 2}','PL',0.)
        check('charged_minus_{2, 1, 2}','PL',-1j*d[0,1])
        check('charged_minus_{2, 1, 2}','PR',0.)
        gs=trilinears(p,lag)
        for k,a,b in [(1,2,2),(1,2,3),(2,3,3),(3,2,3)]:
            check(f'trilinear_{{{k}, {a}, {b}}}','1',-1j*gs[('h','H','A')[k-1]][a-1,b-1])
        for a,b in [(2,2),(2,3)]:
            check(f'scalar_gauge_{{VP, {a}, {b}}}',f'Mom[conj[Hm[{{{b}}}]],lt3]-Mom[Hm[{{{a}}}],lt3]',-1j*e if a==b else 0.)
        check('scalar_gauge_{VZ, 2, 3}','Mom[conj[Hm[{3}]],lt3]-Mom[Hm[{2}],lt3]',0.)
        for k in (1,2):
            kap=(np.cos(p['beta']-p['alpha']),np.sin(p['beta']-p['alpha']))[k-1]
            check(f'WW_{k}','g[lt2,lt3]',1j*2*x['MW']**2/p['v']*kap)
        check('WW_A','1',0.)
        blocks.append('rules={'+','.join(rules)+'};\n'+'\n'.join(checks))
    with tempfile.TemporaryDirectory(prefix='d16-native-') as directory:
        tmp=Path(directory);script=tmp/'check.m';result=tmp/'native.json'
        code='''source=Import[SOURCE,"RawJSON"];
raw=Map[ToExpression,source["raw_representatives"]];
expanded=Map[Function[x,x//.HoldPattern[sum[ind_,lo_Integer,hi_Integer,body_]]:>Total[Table[body,{ind,lo,hi}]]],raw];
checks={};
coefficient[v_,ch_]:=Total[Cases[Rest[v],{c_,l_}/;l===ch:>c]];
check[key_,ch_,expected_,rules_]:=Module[{actual,res},
actual=N[coefficient[expanded[key],ch]/.rules//.conj[a_]:>Conjugate[a]];
res=If[NumericQ[actual],Abs[actual-expected],1.*^300];
AppendTo[checks,<|"key"->key,"tensor"->ToString[ch,InputForm],"actual"->{Re[actual],Im[actual]},"expected"->{Re[expected],Im[expected]},"residual"->res|>]];
'''.replace('SOURCE',json.dumps(str(source)))+'\n'.join(blocks)+'''
report=<|"status"->If[Max[Lookup[checks,"residual"]]<1.*^-9,"PASS","FAIL"],"max_abs_residual"->Max[Lookup[checks,"residual"]],"checks"->checks,"mathematica_version"->$Version|>;
Export[RESULT,report,"RawJSON"];
Exit[If[report["status"]==="PASS",0,1]];
'''.replace('RESULT',json.dumps(str(result)))
        script.write_text(code)
        process=subprocess.run(['wolframscript','-file',str(script)],text=True,capture_output=True)
        if not result.exists():raise RuntimeError(process.stdout+process.stderr)
        report=json.loads(result.read_text())
        if process.returncode or report['status']!='PASS':raise RuntimeError(str(report))
        report.update(native_driver_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),source='module4/native_evidence.json',source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
            scope='Independent numerical substitution into archived native expressions, two strict 2HDM spectra; no regenerated vertices',
            source_mathematica_version=native['mathematica_version'],source_sarah_version=native['sarah_version'])
        return report

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2])
    ap.add_argument('--evidence',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();report=validate(args.root,json.loads(args.evidence.read_text()))
    args.output.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(report['status'],len(report['checks']),'native strict-limit coefficients; max',report['max_abs_residual'])
