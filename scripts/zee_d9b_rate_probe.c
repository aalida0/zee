/* Local GPL-3.0-or-later SuperIso investigative fork client. Q1-Q8, real ms=0. */
#include "include.h"
#define OUT(k,v) printf(k " %.17g\n",(double)(v))
static void vector(const char *label, struct d9b_matching *m) {
    for(int i=1;i<=10;i++) {
        printf("%s_LO_C%d %.17g\n",label,i,creal(m->C0[i]));
        printf("%s_NLO_C%d %.17g\n",label,i,creal(m->C1[i]));
        printf("%s_NNLO_C%d %.17g\n",label,i,creal(m->C2[i]));
    }
}
static double evaluate(struct d9b_matching *m, struct parameters *p) {
    struct d9b_rate_info info;
    return d9b_bsgamma(m,p->mass_b_pole/2.,1.6,p,&info);
}
static void report(const char *label,struct d9b_matching *m,struct parameters *p) {
    struct d9b_rate_info d;
    double r=d9b_bsgamma(m,p->mass_b_pole/2.,1.6,p,&d);
    printf("%s_BR %.17g\n",label,r);
    double complex lo[11]={0},nlo[11]={0},nnlo[11]={0};
    C_calculator_base1(m->C0,m->C1,m->C2,m->mu_W,lo,nlo,nnlo,p->mass_b_pole/2.,p);
    printf("%s_low_C07 %.17g\n",label,creal(lo[7]));
    printf("%s_P0 %.17g\n%s_P1 %.17g\n%s_P2 %.17g\n",label,d.P0,label,d.P1,label,d.P2);
    printf("%s_P_em %.17g\n%s_N_E0 %.17g\n",label,d.P_em,label,d.N_E0);
    printf("%s_nnlo_relative %.17g\n%s_nnlo_dropped %.17g\n",label,d.nnlo_relative,label,(double)d.nnlo_dropped);
}
int main(int argc,char **argv) {
    struct parameters s; Init_param(&s); slha_adjust(&s); s.SM=1;
    struct d9b_matching sm={.mu_W=(argc==2 ? strtod(argv[1],NULL) : argc==10 ? strtod(argv[9],NULL) : 160.),.scheme=1,.order=1};
    CW_calculator(2,sm.C0,sm.C1,sm.C2,sm.mu_W,&s);
    OUT("mu_b",s.mass_b_pole/2.); OUT("mt_match",running_mass(s.mtmt,s.mtmt,sm.mu_W,s.mass_top_pole,s.mass_b,&s));
    OUT("alpha_s_low",alphas_running(s.mass_b_pole/2.,s.mass_top_pole,s.mass_b_pole,&s));
    OUT("alpha_s_match",alphas_running(sm.mu_W,s.mass_top_pole,s.mass_b_pole,&s));
    report("SM",&sm,&s); vector("SM",&sm);
    struct parameters zero=s;zero.SM=0;zero.THDM_model=2;zero.mass_H=550.;
    zero.lambda_u[3][3]=zero.lambda_d[3][3]=0.;
    struct d9b_matching noNP=sm;
    CW_calculator(2,noNP.C0,noNP.C1,noNP.C2,sm.mu_W,&zero);
    OUT("zero_NP_BR",evaluate(&noNP,&zero));
    double max_zero=0.;
    for(int i=1;i<=8;i++) {
        max_zero=fmax(max_zero,cabs(noNP.C0[i]-sm.C0[i]));
        max_zero=fmax(max_zero,cabs(noNP.C1[i]-sm.C1[i]));
    }
    OUT("zero_NP_max_matching_residual",max_zero);
    if(argc<=2) return 0;
    if(argc!=9 && argc!=10) return 2;
    struct parameters n=s; n.SM=0;n.THDM_model=2;n.mass_H=strtod(argv[1],NULL);n.tan_beta=strtod(argv[2],NULL);
    n.lambda_u[3][3]=1./n.tan_beta;n.lambda_d[3][3]=(atoi(argv[3])?1.:-1.)*n.tan_beta;
    struct d9b_matching native=sm, injected=sm;
    CW_calculator(2,native.C0,native.C1,native.C2,sm.mu_W,&n);
    injected.C0[7]+=strtod(argv[4],NULL); injected.C0[8]+=strtod(argv[5],NULL);
    injected.C1[4]+=strtod(argv[6],NULL); injected.C1[7]+=strtod(argv[7],NULL); injected.C1[8]+=strtod(argv[8],NULL);
    /* Unused C2 matching is zero in BOTH paths; NLO rate explicitly removes P2. */
    for(int i=0;i<=10;i++) native.C2[i]=injected.C2[i]=0.;
    vector("native",&native);vector("injected",&injected);
    report("native",&native,&n);report("injected",&injected,&s);report("metadata",&injected,&n);
    struct d9b_matching omitted=injected;omitted.C1[4]-=strtod(argv[6],NULL);
    OUT("omit_C4_BR",evaluate(&omitted,&s));
    struct d9b_matching doubled=injected;doubled.C1[7]-=4./9.*strtod(argv[6],NULL);doubled.C1[8]-=strtod(argv[6],NULL)/6.;
    OUT("double_effective_map_BR",evaluate(&doubled,&s));
    struct d9b_matching high=injected; high.C0[7]+=0.01;report("high_C7",&high,&s);
    struct d9b_matching extra=injected;
    double as=alphas_running(sm.mu_W,s.mass_top_pole,s.mass_b_pole,&s)/4./pi;
    for(int i=4;i<=8;i++) extra.C1[i]=sm.C1[i]+as*(injected.C1[i]-sm.C1[i]);
    OUT("extra_alpha_s_BR",evaluate(&extra,&s));
    struct d9b_matching bad=injected;bad.scheme=2;
    OUT("reject_scheme",isnan(evaluate(&bad,&s)));
    bad=injected;bad.C0[2]+=0.1;OUT("reject_unsupported_LO",isnan(evaluate(&bad,&s)));
    /* Full legacy NNLO diagnostic with original routine kept side by side. */
    struct d9b_matching full=sm;full.order=2;
    CW_calculator(2,full.C0,full.C1,full.C2,sm.mu_W,&n);
    report("legacy_full",&full,&n);
    double complex a[11]={0},b[11]={0},c[11]={0};
    C_calculator_base1(full.C0,full.C1,full.C2,full.mu_W,a,b,c,s.mass_b_pole/2.,&n);
    OUT("legacy_original_entry_BR",bsgamma(a,b,c,full.Cp,s.mass_b_pole/2.,full.mu_W,&n));
    struct d9b_matching forced=full; forced.C2[7]+=1.e5;
    report("forced_fallback",&forced,&n);
    forced.order=1; OUT("forced_NLO_BR",evaluate(&forced,&n));
    return 0;
}
