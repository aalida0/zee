"""Independent massless-q Z-only scalar-pair cross section and PDF convolution.

One charge in partonic_pb; two explicit charges and both beam orders in hadronic.
No photons, neutral-Higgs exchange or quark exchange included.
"""
import ctypes
import json
import math
import os
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
LOCAL=ROOT/'validation/module8/local'
GEV2_TO_PB=389379372.1


def partonic_pb(shat,m1,m2,gamma,quark):
    if quark not in (1,2,3,4,5):raise ValueError('five incoming quark flavors only')
    if shat<=(m1+m2)**2:return 0.
    if gamma==0. or abs(gamma)==math.pi/2:return 0.
    v=246.21965;mw=80.379;mz=91.1876;wz=2.4952;cw=mw/mz;sw2=1-cw*cw;g=2*mw/v
    t3,Q=(.5,2/3) if quark in (2,4) else (-.5,-1/3)
    gl=g/cw*(t3-Q*sw2);gr=-g/cw*Q*sw2;scalar=g*math.sin(2*gamma)/(4*cw)
    beta=math.sqrt((1-(m1+m2)**2/shat)*(1-(m1-m2)**2/shat))
    # Spin average 1/4 and color average 1/3, integrated sin^2(theta).
    return GEV2_TO_PB*scalar**2*(gl*gl+gr*gr)*shat*beta**3/(288*math.pi*((shat-mz*mz)**2+(mz*wz)**2))


def hadronic(m1,m2,gamma,n):
    os.environ['LHAPDF_DATA_PATH']=str(LOCAL/'pdf')
    lib=ctypes.CDLL(str(LOCAL/'pdf_bridge.so'))
    lib.d5_pdf_init();lib.d5_xfx.argtypes=[ctypes.c_int,ctypes.c_double,ctypes.c_double];lib.d5_xfx.restype=ctypes.c_double
    lib.d5_alpha.argtypes=[ctypes.c_double];lib.d5_alpha.restype=ctypes.c_double
    x,w=np.polynomial.legendre.leggauss(n);lo=math.log((m1+m2)**2/13600.**2)
    result=0.
    for a,wa in zip(x,w):
        t=lo*(1-a)/2;tau=math.exp(t);shat=tau*13600.**2
        sig={q:partonic_pb(shat,m1,m2,gamma,q) for q in range(1,6)}
        for b,wb in zip(x,w):
            z=t*(1-b)/2;x1=math.exp(z);x2=tau/x1
            luminosity=0.
            for q in range(1,6):
                f1=lib.d5_xfx(q,x1,700.);fb1=lib.d5_xfx(-q,x1,700.)
                f2=lib.d5_xfx(q,x2,700.);fb2=lib.d5_xfx(-q,x2,700.)
                luminosity+=sig[q]*(f1*fb2+fb1*f2)
            result+=wa*wb*(-lo/2)*(-t/2)*luminosity*2 # two conjugate final states
    return result,lib.d5_alpha(700.)


def main():
    results=[]
    for mass in (250.,300.,350.):
        low,alpha=hadronic(mass,700.,1.089,100);high,_=hadronic(mass,700.,1.089,180)
        results.append({'mH1_GeV':mass,'sigma_Z_only_charge_inclusive_pb':high,
                        'quadrature_difference_pb':abs(high-low),'alpha_s_PDF_700':alpha,
                        'threshold_GeV':mass+700.,'nodes_per_dimension':[100,180]})
    report={'status':'INDEPENDENT_ANALYTICAL_CONVOLUTION_NOT_GENERATOR_RATE',
            'formula':'sigma_hat = |g_H12Z|^2*(gL^2+gR^2)*s*beta^3 / (288*pi*[(s-mZ^2)^2+(mZ*GammaZ)^2])',
            'units':'GeV^-2 converted to pb with 389379372.1; spin/color averaged; one charge per sigma_hat',
            'beam_orders_and_charges':'both q(x1)qbar(x2)+qbar(x1)q(x2), final charges twice',
            'results':results}
    from module8.run_capture import sha
    report['source_sha256']={str(path.relative_to(ROOT)):sha(path) for path in [Path(__file__),ROOT/'module8/pdf_bridge.cc',LOCAL/'pdf_bridge.so',LOCAL/'lhapdf/lib/libLHAPDF.so',*(LOCAL/'pdf/NNPDF30_lo_as_0130').glob('*')]}
    (LOCAL/'partonic_checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(results))

if __name__=='__main__':main()
