/* SPDX-License-Identifier: GPL-3.0-or-later
 * Research client of original SuperIso 5.0 / exact historical D9B patch.
 * No rate or evolution implementation is copied here.
 */
#include "include.h"
#define OUT(k,v) printf(k " %.17g\n", (double)(v))

static void ordinary(const char *label, double complex *a, double complex *b,
                     double as) {
    const double y[9]={0,0,0,-1./3.,-4./9.,-20./3.,-80./9.,0,0};
    const double z[9]={0,0,0,1.,-1./6.,20.,-10./3.,0,0};
    double c[9]={0};
    for(int i=1;i<=8;i++) c[i]=creal(a[i]+as/(4*pi)*b[i]);
    for(int i=1;i<=6;i++) { c[7]-=y[i]*c[i]; c[8]-=z[i]*c[i]; }
    for(int i=1;i<=8;i++) printf("%s_C%d %.17g\n",label,i,c[i]);
}

int main(int argc, char **argv) {
    if(argc!=11) return 2;
    double v[10];
    for(int i=0;i<10;i++) { v[i]=strtod(argv[i+1],NULL); if(!isfinite(v[i])) return 3; }
    struct parameters p; Init_param(&p); slha_adjust(&p); p.SM=1;
    double mw=v[3], mb=v[4];
    double complex a[11]={0},b[11]={0},c[11]={0},x[11]={0},y[11]={0},z[11]={0},cp[11]={0};
    CW_calculator(2,a,b,c,mw,&p);
    C_calculator_base1(a,b,c,mw,x,y,z,mb,&p);
    double as=alphas_running(mb,p.mass_top_pole,p.mass_b_pole,&p);
    ordinary("SM_ordinary_low",x,y,as);
    OUT("mu0",mw); OUT("mu_b",mb); OUT("alpha_s_mu_b",as);
    OUT("alpha_s_mu0",alphas_running(mw,p.mass_top_pole,p.mass_b_pole,&p));
    OUT("mt_MSbar_mu0",running_mass(p.mtmt,p.mtmt,mw,p.mass_top_pole,p.mass_b,&p));
    OUT("alpha_s_MZ",p.alphas_MZ); OUT("mass_Z",p.mass_Z);
    OUT("mass_b_MSbar",p.mass_b); OUT("mass_b_pole",p.mass_b_pole);
    OUT("mass_c_MSbar",p.mass_c); OUT("mass_c_pole",p.mass_c_pole);
    OUT("mu_c",p.mu_c_bsg); OUT("mass_s",p.mass_s);
    OUT("alpha_em_rate",1./137.036); OUT("alpha_em_QED_correction",1./p.inv_alpha_em);
    OUT("BR_semileptonic",p.BR_BXclnu_exp);OUT("C_semileptonic",C_BXlnu(&p));
    OUT("CKMratio_squared",pow(cabs(conj(p.Vts)*p.Vtb/p.Vcb),2.));
    OUT("CKM_VtsVtb_squared",pow(cabs(conj(p.Vts)*p.Vtb),2.));
#ifdef D9B
    struct d9b_matching sm={.mu_W=mw,.scheme=1,.order=1};
    for(int i=0;i<=10;i++) {sm.C0[i]=a[i];sm.C1[i]=b[i];}
    struct d9b_rate_info info;
    OUT("SM_BR_NLO",d9b_bsgamma(&sm,mb,1.6,&p,&info));
    struct d9b_matching np=sm;
    np.C0[7]+=v[5];np.C0[8]+=v[6];np.C1[4]+=v[7];np.C1[7]+=v[8];np.C1[8]+=v[9];
    OUT("NP_BR_NLO",d9b_bsgamma(&np,mb,1.6,&p,&info));
    OUT("P0",info.P0);OUT("P1",info.P1);OUT("P2",info.P2);
    OUT("P_em",info.P_em);OUT("N_E0",info.N_E0);
    C_calculator_base1(np.C0,np.C1,np.C2,mw,x,y,z,mb,&p);
    ordinary("NP_ordinary_low",x,y,as);
#else
    OUT("SM_BR_legacy",bsgamma_Ecut(x,y,z,cp,mb,mw,1.6,&p));
    p.SM=0;p.THDM_model=2;p.mass_H=v[0];p.tan_beta=v[1];
    p.lambda_u[3][3]=1./v[1];p.lambda_d[3][3]=(v[2] ? 1. : -1.)*v[1];
    CW_calculator(2,a,b,c,mw,&p);
    C_calculator_base1(a,b,c,mw,x,y,z,mb,&p);
    OUT("TypeII_BR_legacy",bsgamma_Ecut(x,y,z,cp,mb,mw,1.6,&p));
    ordinary("TypeII_ordinary_low",x,y,as);
#endif
    return 0;
}
