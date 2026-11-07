"""Bounded independent controls and uncertainties for four original-card rates."""
import argparse
import math
from pathlib import Path
import subprocess
from research.full_constraints.higgs.sushi_bridge import (
    PDF, benchmark, blocks, couplings, dump, execute, lo_amplitude)

SCALES=((.5,.5),(.5,1.),(1.,.5),(1.,1.),(1.,2.),(2.,1.),(2.,2.))


def luminosity(binary,mass,q,member=0,n=4096,parton=21):
    return list(map(float,subprocess.check_output([str(binary),PDF,str(member),str(mass),str(q),str(n),str(parton)],text=True).split()))


def study(sushi,lumi,out):
    out.mkdir(parents=True,exist_ok=False); rows=[]
    for name in ('D7','F13'):
        r,_=benchmark(name);p=r['input']['physical']
        for state in ('H','A'):
            central=execute(sushi,out,name,state,'central')
            b=central['blocks'];mass=p['mh2' if state=='H' else 'ma'];k=couplings(p,state)
            amp,terms=lo_amplitude(mass,'even' if state=='H' else 'odd',k['top'],k['bottom'],
                                   mc=b['internalmasses'][40])
            lum,alph=luminosity(lumi,mass,mass/2)
            lum_fine,_=luminosity(lumi,mass,mass/2,n=8192)
            # Exact LO spin/colour averaged partonic normalization. 1 GeV^-2 in pb.
            gf=1/(math.sqrt(2)*p['v']**2)
            independent=gf*b['alphasout'][1]**2/(512*math.sqrt(2)*math.pi)*abs(amp)**2*lum*389379338.
            residual=independent/central['rates']['ggF']['sigma_pb']-1
            if abs(residual)>2e-5:raise ValueError(f'Independent ggF normalization failed: {residual}')
            alpha_run=lambda q: .135/(1+.135*(23/3)*math.log(q/91.1876)/(2*math.pi))
            if not math.isclose(alpha_run(mass/2),b['alphasout'][1],rel_tol=1e-7):
                raise ValueError('LO alpha_s evolution mismatch')
            bottom_mass=4.183*(alpha_run(mass)/alpha_run(4.183))**(12/23)
            lbb,abb=luminosity(lumi,mass,mass/4,parton=5)
            bb_independent=math.pi/6*math.sqrt(2)*gf/mass**2*389379338.*bottom_mass**2*k['bottom']**2*lbb
            bb_residual=bb_independent/central['rates']['bbH']['sigma_pb']-1
            if abs(bb_residual)>2e-5:raise ValueError('Independent bbH normalization failed')
            controls={}
            for tag,factors in [('top',(0,1,0)),('bottom',(0,0,1)),('charm',(1,0,0)),
                                ('flip_bottom',(1,1,-1)),('double_all',(2,2,2)),
                                ('unit_quarks',(1/k['top'],1/k['top'],1/k['bottom']))]:
                run=execute(sushi,out,name,state,tag,factors=factors)
                cf,tf,bf=factors
                ref=abs(tf*terms[0]+bf*terms[1]+cf*terms[2])**2/abs(amp)**2
                actual=run['rates']['ggF']['sigma_pb']/central['rates']['ggF']['sigma_pb']
                if not math.isclose(actual,ref,rel_tol=3e-6,abs_tol=1e-10):raise ValueError('Amplitude scaling/interference check failed')
                if not math.isclose(run['rates']['bbH']['sigma_pb'],central['rates']['bbH']['sigma_pb']*bf**2,rel_tol=3e-6,abs_tol=1e-14):
                    raise ValueError('bbH squared-Yukawa control failed')
                controls[tag]=dict(ggF_ratio=actual,analytic_ratio=ref,bbH_pb=run['rates']['bbH']['sigma_pb'])
            scale_rows=[]
            for i,scale in enumerate(SCALES):
                run=central if scale==(1.,1.) else execute(sushi,out,name,state,f'scale{i}',scale=scale)
                scale_rows.append(dict(muR_multiplier=scale[0],muF_multiplier=scale[1],rates=run['rates']))
            pdf_rows=[]
            # At LO the PDF/member dependence factorizes exactly from the quark loop.
            # alpha_s is checked per member; use luminosities only after that check.
            for member in range(51):
                lg,ag=luminosity(lumi,mass,mass/2,member)
                lb,ab=luminosity(lumi,mass,mass/4,member,parton=5)
                if abs(ag-alph)>1e-12 or abs(ab-abb)>1e-12:raise ValueError('PDF member alpha_s changed')
                pdf_rows.append(dict(member=member,ggF_pb=central['rates']['ggF']['sigma_pb']*lg/lum,
                                     bbH_pb=central['rates']['bbH']['sigma_pb']*lb/lbb))
            uncertainty={}
            for proc in ('ggF','bbH'):
                sig=central['rates'][proc]['sigma_pb'];key=proc+'_pb'
                vals=[s['rates'][proc]['sigma_pb'] for s in scale_rows]
                # Symmetric Hessian 68% prescription, MMHT2014 25 eigenvector pairs.
                hessian=.5*math.sqrt(sum((pdf_rows[2*i+1][key]-pdf_rows[2*i+2][key])**2 for i in range(25)))
                uncertainty[proc]=dict(scale_down_pb=sig-min(vals),scale_up_pb=max(vals)-sig,
                                       PDF_symmetric_68_percent_pb=hessian,
                                       parametric_error_pb=None,EW_Zee_error_pb=None)
            # Source-restricted SusHi has c,t,b loops. Bound omitted u,d,s at this LO scheme.
            index=1 if state=='H' else 3
            from research.full_constraints.higgs.diphoton import loops
            omitted=sum(ku*loops((mass/(2*m))**2)[index] for ku,m in
                        ((k['top'],.00216),(k['bottom'],.00470),(k['bottom'],.0935)))
            light_shift=abs(amp+omitted)**2/abs(amp)**2-1
            rows.append(dict(name=name,state=state,scalar_sha256=r['input_sha256'],mass_GeV=mass,
                couplings=k,central=central,independent_ggF_pb=independent,
                independent_relative_residual=residual,quadrature_relative_change=lum_fine/lum-1,
                independent_bbH_pb=bb_independent,independent_bbH_relative_residual=bb_residual,
                bbH_MSbar_mass_at_muR_GeV=bottom_mass,
                omitted_light_quark_LO_relative_shift=light_shift,
                controls=controls,scale_variations=scale_rows,PDF_members=pdf_rows,uncertainties=uncertainty,
                production_status='VALIDATED_SCOPED_LO_CTB_QCD',exclusion=None))
            dump(out/'results.json',rows)
            print(name,state,'validated',central['rates'],flush=True)
    return rows


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--sushi',type=Path,required=True)
    ap.add_argument('--luminosity',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args();study(a.sushi,a.luminosity,a.out)
