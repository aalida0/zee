"""Isolated execution of pinned HEPfit SM Zgamma functions.

This is a dependency shim, not a full HEPfit build or an electroweak fit.
Original function arithmetic is extracted at runtime; transformations are
only class/type qualifiers and abs2 -> std::norm. No HDECAY/SusHi execution.
HEPfit source: https://github.com/silvest/HEPfit at the commit below (GPL).
"""
from pathlib import Path
import re
import subprocess

from research.full_constraints.higgs.sushi_bridge import sha

COMMIT='322bd73a2dadd94ce94a6d71cb79d616e569120a'
SOURCE=Path('/tmp/zee-hepfit')/('HEPfit-'+COMMIT)
PINS={'StandardModel/src/StandardModel.cpp':'c8787292777d3c5eff996b6d53c645e295021bd3a2c9251c411b04dab2e8ac96',
      'GeneralTHDM/src/GeneralTHDMcache.cpp':'6a781868d3e6fdc2f732c84bc1a181eb6992623c95583d2539449931b826dea4'}


def extract(text,name):
    start=text.index(name+'(')
    start=text.rfind('\n',0,start)+1
    opening=text.index('{',start);depth=1;end=opening+1
    while depth:
        depth+=(text[end]=='{')-(text[end]=='}');end+=1
    return text[start:end]


def execute(mh,mw,mz,v,alpha,masses,work=Path('/tmp/zee-zgamma-reference')):
    source=SOURCE/'StandardModel/src/StandardModel.cpp'
    general=SOURCE/'GeneralTHDM/src/GeneralTHDMcache.cpp'
    for path,digest in PINS.items():
        if sha(SOURCE/path)!=digest:raise ValueError('HEPfit source changed: '+path)
    text=source.read_text();gtext=general.read_text()
    names=['f_triangle','g_triangle','I_triangle_1','I_triangle_2','AHZga_f','AHZga_W','GammaHtoZga']
    functions='\n'.join(extract(text,'StandardModel::'+name) for name in names)
    functions=functions.replace('gslpp::complex::i()','std::complex<double>(0,1)')
    functions=functions.replace('gslpp::complex','std::complex<double>').replace('StandardModel::','')
    functions=functions.replace(') const',')').replace('MSM.abs2()','std::norm(MSM)')
    # Expose the original complex MSM for the coherent scalar control.
    functions=functions.replace('    std::complex<double> MSM;','')
    # Execute the GeneralTHDM one-charged-scalar expression verbatim. Its
    # overall tensor convention is opposite to StandardModel's convention.
    scalar=extract(gtext,'GeneralTHDMcache::A_H_Hp')
    expr=re.search(r'newResult = (.*?);',scalar,re.S).group(1)
    header='''#include <cmath>
#include <complex>
#include <iostream>
#include <iomanip>
using namespace std;
complex<double> MSM;
enum {TOP,BOTTOM,CHARM,STRANGE}; enum {TAU,MU};
struct Particle {double m,q,t; double getMass(){return m;}
double getCharge(){return q;} double getIsospin(){return t;}};
'''
    header+=f'double mHl={mh:.17g}, mtpole={masses["t"]:.17g}, Mz={mz:.17g}, GF={1/(2**.5*v*v):.17g}, ale={alpha:.17g};\n'
    header+=f'double Mw(){{return {mw:.17g};}} double cW2(){{return pow(Mw()/Mz,2);}} double sW2(){{return 1-cW2();}}\n'
    header+='Particle quarks[] = {'+','.join('{'+f'{masses[f]:.17g},{q:.17g},{t:.17g}'+'}' for f,q,t in
        [('t',2/3,.5),('b',-1/3,-.5),('c',2/3,.5),('s',-1/3,-.5)])+'};\n'
    header+='Particle leptons[] = {'+','.join('{'+f'{masses[f]:.17g},-1,-.5'+'}' for f in ['tau','mu'])+'};\n'
    tail='''
complex<double> Int1(double a,double b){return I_triangle_1(a,b);}
complex<double> scalar(double mass){
double sW2=::sW2(),cW2=::cW2(),TAUhp=4*mass*mass/mHl/mHl,LAMhp=4*mass*mass/Mz/Mz;
return EXPR;
}
int main(){cout<<setprecision(17)<<GammaHtoZga()<<"\\n";
auto w=AHZga_W(4*Mw()*Mw()/mHl/mHl,4*Mw()*Mw()/Mz/Mz)/sqrt(sW2());
cout<<w.real()<<" "<<w.imag()<<"\\n";
for(double mass : {300.,700.}){auto a=scalar(mass);cout<<a.real()<<" "<<a.imag()<<"\\n";
for(double G : {100.,-100.}){auto total=MSM-ale/(4*M_PI)*G*sqrt(1/(sqrt(2)*GF))/(2*mass*mass)*a;
cout<<GammaHtoZga()*norm(total)/norm(MSM)<<"\\n";}}}
'''.replace('EXPR',expr)
    work.mkdir(exist_ok=True);cpp=work/'reference.cpp';exe=work/'reference'
    cpp.write_text(header+functions+tail)
    build=subprocess.run(['g++','-O2','-std=c++17',str(cpp),'-o',str(exe)],capture_output=True,text=True,check=True)
    run=subprocess.run([str(exe)],capture_output=True,text=True,check=True)
    lines=run.stdout.splitlines()
    return dict(commit=COMMIT,source_url='https://github.com/silvest/HEPfit/tree/'+COMMIT,
                source_hashes={str(p):sha(p) for p in (source,general)},
                functions=names,SM_fermions=['t','b','c','s','tau','mu'],
                SM_width_GeV=float(lines[0]),W=complex(*map(float,lines[1].split())),
                scalar_functions=[complex(*map(float,lines[i].split())) for i in (2,5)],
                one_scalar_widths_GeV=[float(lines[i]) for i in (3,4,6,7)],
                scalar_function_masses_GeV=[300.,700.],
                generated_cpp_sha256=sha(cpp),executable_sha256=sha(exe),
                stdout=run.stdout,stderr=run.stderr,compiler_stderr=build.stderr)
