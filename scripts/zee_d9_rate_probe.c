/* D9 diagnostic client of the unmodified SuperIso v5.0 public C API.
 * No physical injection PASS: bsgamma internally rematches its model.
 */
#include "include.h"

static double rate(double complex a[], double complex b[], double complex c[],
                   double complex cp[], double mw, double mb, struct parameters *p)
{
    double complex x[11]={0},y[11]={0},z[11]={0};
    C_calculator_base1(a,b,c,mw,x,y,z,mb,p);
    return bsgamma(x,y,z,cp,mb,mw,p);
}
#define OUT(name,value) printf(name " %.17g\n",(double)(value))

int main(int argc, char **argv)
{
    struct parameters s;
    Init_param(&s); slha_adjust(&s); s.SM=1;
    const double mw=160., mb=s.mass_b_pole/2.;
    double complex a[11]={0},b[11]={0},c[11]={0},cp[11]={0},cqp[3]={0};
    CW_calculator(2,a,b,c,mw,&s);
    Cprime_calculator(2,cp,cqp,mw,mb,&s);
    OUT("mu_match",mw); OUT("mu_b",mb); OUT("Ecut",1.6);
    OUT("mt_match",running_mass(s.mtmt,s.mtmt,mw,s.mass_top_pole,s.mass_b,&s));
    OUT("alpha_s_match",alphas_running(mw,s.mass_top_pole,s.mass_b_pole,&s));
    OUT("mass_top_pole",s.mass_top_pole); OUT("mtmt",s.mtmt);
    OUT("mass_b_MSbar",s.mass_b); OUT("mass_b_pole",s.mass_b_pole);
    OUT("mass_c_MSbar",s.mass_c); OUT("mass_s",s.mass_s);
    OUT("mb_kin_source_prescription",s.mass_b+0.37);
    OUT("mu_G2_bsg",s.mu_G2_bsg); OUT("rho_D3_bsg",s.rho_D3_bsg); OUT("rho_LS3_bsg",s.rho_LS3_bsg);
    OUT("mass_W",s.mass_W); OUT("mass_Z",s.mass_Z);
    OUT("alphas_MZ",s.alphas_MZ); OUT("inv_alpha_em",s.inv_alpha_em);
    OUT("BR_BXclnu_exp",s.BR_BXclnu_exp); OUT("C_semileptonic",C_BXlnu(&s));
    OUT("lambda2",s.lambda2); OUT("CKM_ratio_squared",pow(cabs(conj(s.Vts)*s.Vtb/s.Vcb),2.));
    OUT("Vts_real",creal(s.Vts)); OUT("Vts_imag",cimag(s.Vts));
    OUT("Vtb_real",creal(s.Vtb)); OUT("Vtb_imag",cimag(s.Vtb));
    OUT("Vcb_real",creal(s.Vcb)); OUT("Vcb_imag",cimag(s.Vcb));
    OUT("SM_full",rate(a,b,c,cp,mw,mb,&s));
    if(argc==1) {
        double dw=2.*s.mass_W;
        CW_calculator(2,a,b,c,dw,&s);
        Cprime_calculator(2,cp,cqp,dw,mb,&s);
        OUT("SM_upstream_default_scale",rate(a,b,c,cp,dw,mb,&s));
        return 0;
    }
    if(argc!=9) return 2;
    double mass=strtod(argv[1],NULL), tb=strtod(argv[2],NULL);
    int flip=atoi(argv[3]);
    struct parameters n=s;
    n.SM=0; n.THDM_model=2; n.mass_H=mass; n.tan_beta=tb;
    n.lambda_u[3][3]=1./tb; n.lambda_d[3][3]=(flip?1.:-1.)*tb;
    double complex na[11]={0},nb[11]={0},nc[11]={0};
    CW_calculator(2,na,nb,nc,mw,&n);
    double mt=running_mass(n.mtmt,n.mtmt,mw,n.mass_top_pole,n.mass_b,&n);
    double yt=pow(mt/mass,2.), lu=1./tb, ld=(flip?1.:-1.)*tb;
    OUT("uncapped_C4_NLO",EH(yt,lu));
    OUT("uncapped_C7_NLO",G7H(yt,lu,ld)+Delta7H(yt,lu,ld)*log(pow(mw/mass,2.))-4./9.*EH(yt,lu));
    OUT("uncapped_C8_NLO",G8H(yt,lu,ld)+Delta8H(yt,lu,ld)*log(pow(mw/mass,2.))-1./6.*EH(yt,lu));
    OUT("native_full",rate(na,nb,nc,cp,mw,mb,&n));
    for(int i=1;i<=8;i++) {
        printf("native_LO_C%d %.17g\n",i,creal(na[i]));
        printf("native_NLO_C%d %.17g\n",i,creal(nb[i]));
        printf("SM_LO_C%d %.17g\n",i,creal(a[i]));
        printf("SM_NLO_C%d %.17g\n",i,creal(b[i]));
    }
    /* Controlled comparison ONLY: zero ALL NNLO matching for both vectors.
     * The NNLO rate/evolution still run; these are explicitly diagnostics.
     * Identical native model metadata supplies identical internal corrections.
     */
    double complex zero[11]={0};
    a[7]+=strtod(argv[4],NULL); a[8]+=strtod(argv[5],NULL);
    b[4]+=strtod(argv[6],NULL); b[7]+=strtod(argv[7],NULL); b[8]+=strtod(argv[8],NULL);
    OUT("native_NLOmatching_diagnostic",rate(na,nb,zero,cp,mw,mb,&n));
    OUT("injected_NLOmatching_native_metadata",rate(a,b,zero,cp,mw,mb,&n));
    OUT("injected_NLOmatching_SM_metadata",rate(a,b,zero,cp,mw,mb,&s));
    b[4]-=strtod(argv[6],NULL);
    OUT("omit_C4_diagnostic",rate(a,b,zero,cp,mw,mb,&s));
    return 0;
}
