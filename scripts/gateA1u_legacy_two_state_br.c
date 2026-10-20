/*
 * Gate A1U: two charged-Higgs Zee-type sector in the LEGACY SuperIso
 * v5 physical inclusive B -> X_s gamma observable.
 *
 * A modern 2026 NNLO 95% CL exclusion CANNOT be claimed here.
 *
 * The full LO/NLO/NNLO high-scale Wilson arrays and primed arrays
 * are combined at the matching scale, not the branching fractions:
 *
 * C^Zee = C^SM + cos^2(gamma)*(C^H1-C^SM)
 *              + sin^2(gamma)*(C^H2-C^SM).
 *
 * In SuperIso v5 bsgamma() delegates to bsgamma_Ecut(), which may
 * reload high-scale C7/C8 with CW_calculator(). A source-verified
 * helper_reload mode uses the linker --wrap feature to inject the
 * SAME mixed high-scale vector into that helper call, while passing
 * mixed low-scale vectors to the unchanged physical observable.
 * No physical BR averaging or linear BR interpolation is performed.
 * Endpoint closure against real A1R is mandatory.
 *
 * The above is NOT the weighted average of the PHYSICAL single-state
 * BRs, which includes different low-scale Wilson coefficients!
 *
 * Internal source is separately hash-checked by the Python runner,
 * which fails closed if it cannot certify the affine dependence.
 * Code invokes the same pinned A1M archive as Gate A1R.
 */
#include "include.h"
#include <errno.h>
#include <math.h>
#include <complex.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define NWC 11
struct wc {
    double complex C0[NWC], C1[NWC], C2[NWC], Cp[NWC];
};

/* Link-time interposition is scoped to one mixed observable call.
 * No upstream/vendor source is modified. During reference and matching
 * calculations the genuine CW_calculator is always called.
 */
static const struct wc *a1u_mixed_high_override=NULL;
static double a1u_expected_muW=0.;
static int a1u_wrap_hits=0;
static int a1u_wrap_error=0;

void __real_CW_calculator(int gen,double complex C0w[],
                          double complex C1w[],double complex C2w[],
                          double muW,struct parameters *p);
void __wrap_CW_calculator(int gen,double complex C0w[],
                          double complex C1w[],double complex C2w[],
                          double muW,struct parameters *p)
{
    if(a1u_mixed_high_override==NULL) {
        __real_CW_calculator(gen,C0w,C1w,C2w,muW,p);
        return;
    }
    a1u_wrap_hits++;
    if(gen!=2 || fabs(muW-a1u_expected_muW)>1.e-8 ||
       a1u_wrap_hits!=1) {
        a1u_wrap_error=1;
        memset(C0w,0,NWC*sizeof(*C0w));
        memset(C1w,0,NWC*sizeof(*C1w));
        memset(C2w,0,NWC*sizeof(*C2w));
        return;
    }
    memcpy(C0w,a1u_mixed_high_override->C0,NWC*sizeof(*C0w));
    memcpy(C1w,a1u_mixed_high_override->C1,NWC*sizeof(*C1w));
    memcpy(C2w,a1u_mixed_high_override->C2,NWC*sizeof(*C2w));
}


static int parse_input(const char *s,double *v)
{
    char *end=NULL;
    errno=0;
    *v=strtod(s,&end);
    return !errno && end!=s && !*end && isfinite(*v);
}
static int is_real_finite(double complex v)
{
    return isfinite(creal(v)) && isfinite(cimag(v))
        && fabs(cimag(v)) < 1.e-10;
}
static void at_state(struct parameters *p,
                     const struct parameters *base,
                     double mass,int is_sm)
{
    *p=*base;
    p->mass_H=mass;
    p->SM=is_sm;
    p->THDM_model=2;
}
static int high_wc(struct wc *out,
                   const struct parameters *base,
                   double mass,int is_sm,
                   double muW,double mub)
{
    struct parameters p;
    double complex CQprime[3]={0};
    int i;
    at_state(&p,base,mass,is_sm);
    CW_calculator(2,out->C0,out->C1,out->C2,muW,&p);
    Cprime_calculator(2,out->Cp,CQprime,muW,mub,&p);
    for(i=1;i<=10;i++) {
        if(!is_real_finite(out->C0[i]) ||
           !is_real_finite(out->C1[i]) ||
           !is_real_finite(out->C2[i]) ||
           !is_real_finite(out->Cp[i])) {
            fprintf(stderr,"A1U_NONREAL_HIGH_WILSON op=%d\n",i);
            return 0;
        }
    }
    return 1;
}
static void mix_wc(struct wc *out,const struct wc *sm,
                   const struct wc *h1,const struct wc *h2,
                   double w1,double w2)
{
    int i;
    for(i=0;i<NWC;i++) {
        out->C0[i]=sm->C0[i]+w1*(h1->C0[i]-sm->C0[i])
                               +w2*(h2->C0[i]-sm->C0[i]);
        out->C1[i]=sm->C1[i]+w1*(h1->C1[i]-sm->C1[i])
                               +w2*(h2->C1[i]-sm->C1[i]);
        out->C2[i]=sm->C2[i]+w1*(h1->C2[i]-sm->C2[i])
                               +w2*(h2->C2[i]-sm->C2[i]);
        out->Cp[i]=sm->Cp[i]+w1*(h1->Cp[i]-sm->Cp[i])
                              +w2*(h2->Cp[i]-sm->Cp[i]);
    }
}
struct low_wc {
    double complex C0[NWC],C1[NWC],C2[NWC];
};

static int evolve(const struct wc *high,
                  const struct parameters *base,
                  double context_mass,int context_is_sm,
                  double muW,double mub,struct low_wc *low)
{
    double complex C0w[NWC]={0},C1w[NWC]={0},C2w[NWC]={0};
    struct parameters p;
    int i;
    at_state(&p,base,context_mass,context_is_sm);
    memcpy(C0w,high->C0,sizeof(C0w));
    memcpy(C1w,high->C1,sizeof(C1w));
    memcpy(C2w,high->C2,sizeof(C2w));
    memset(low,0,sizeof(*low));
    C_calculator_base1(C0w,C1w,C2w,
        muW,low->C0,low->C1,low->C2,mub,&p);
    for(i=1;i<=10;i++) {
        if(!is_real_finite(low->C0[i])||
           !is_real_finite(low->C1[i])||
           !is_real_finite(low->C2[i])) {
            fprintf(stderr,"A1U_NONREAL_RG_WILSON op=%d\n",i);
            return 0;
        }
    }
    return 1;
}
static double maximum_low_diff(const struct low_wc *a,
                               const struct low_wc *b)
{
    double maxerr=0.;
    int i;
    for(i=1;i<=10;i++) {
        double v=cabs(a->C0[i]-b->C0[i]);
        if(v>maxerr)maxerr=v;
        v=cabs(a->C1[i]-b->C1[i]);
        if(v>maxerr)maxerr=v;
        v=cabs(a->C2[i]-b->C2[i]);
        if(v>maxerr)maxerr=v;
    }
    return maxerr;
}
static double observable_at_fixed_low(const struct low_wc *low,
                                      const struct wc *high,
                                      const struct parameters *base,
                                      double context_mass,int context_is_sm,
                                      double muW,double mub,int helper_reload)
{
    double complex C0b[NWC],C1b[NWC],C2b[NWC],Cp[NWC];
    struct parameters p;
    at_state(&p,base,context_mass,context_is_sm);
    /* Work from fresh COPIES, even if vendor bsgamma mutates inputs.
     * The three calls now receive *identical* low-scale Wilsons.
     */
    memcpy(C0b,low->C0,sizeof(C0b));
    memcpy(C1b,low->C1,sizeof(C1b));
    memcpy(C2b,low->C2,sizeof(C2b));
    memcpy(Cp,high->Cp,sizeof(Cp));
    if(a1u_mixed_high_override!=NULL) {
        fprintf(stderr,"A1U_NESTED_OVERRIDE_UNSAFE\n");
        return -1.;
    }
    a1u_wrap_hits=0;
    a1u_wrap_error=0;
    a1u_expected_muW=muW;
    if(helper_reload) a1u_mixed_high_override=high;
    {
        double result=bsgamma(C0b,C1b,C2b,Cp,mub,muW,&p);
        a1u_mixed_high_override=NULL;
        if(a1u_wrap_error || a1u_wrap_hits!=(helper_reload?1:0)) {
            fprintf(stderr,
               "A1U_CW_WRAP_CALL_CONTRACT_FAILED hits=%d error=%d expected=%d\n",
               a1u_wrap_hits,a1u_wrap_error,helper_reload?1:0);
            return -1.;
        }
        return result;
    }
}
static double real_br(const struct wc *high,
                      const struct parameters *base,
                      double context_mass,int context_is_sm,
                      double muW,double mub)
{
    struct low_wc low;
    if(!evolve(high,base,context_mass,context_is_sm,muW,mub,&low))
        return -1.;
    return observable_at_fixed_low(&low,high,base,
                                   context_mass,context_is_sm,muW,mub,0);
}

int main(int argc,char **argv)
{
    double m1,m2,gamma,tanbeta,muW,mub,c,s,w1,w2;
    double bsm_low,b1_low,b2_low,mixBR;
    double rawsm=0.,raw1=0.,raw2=0.;
    double ref1,ref2,refdeg;
    double rgdiff_H1,rgdiff_H2;
    struct low_wc lowSM,lowH1,lowH2;
    struct parameters p;
    struct wc sm={0},h1={0},h2={0},mixed={0};
    int i;
    int internal_reload;
    if(argc!=6 ||
       !(strcmp(argv[5],"none")==0 || strcmp(argv[5],"helper_reload")==0) ||
       !parse_input(argv[1],&m1)||
       !parse_input(argv[2],&m2)||
       !parse_input(argv[3],&gamma)||
       !parse_input(argv[4],&tanbeta)||
       !(200.<=m1 && m1<=m2 && m2<=10000.)||
       !(0.<=gamma && gamma<=1.57079632679489662)||
       !(0.25<=tanbeta && tanbeta<=100.)) {
        fprintf(stderr,
            "A1U_INPUT_ERROR usage: a1u_two_state mH1 mH2 gamma tanbeta none|reload"
            " with 200<=mH1<=mH2<=10000 and 0<=gamma<=pi/2\n");
        return 2;
    }
    internal_reload=(strcmp(argv[5],"helper_reload")==0);
    c=cos(gamma); s=sin(gamma);
    w1=c*c; w2=s*s;
    if(fabs(w1+w2-1.)>2.e-14) {
        fprintf(stderr,"A1U_MIXING_NONUNITARITY\n");return 3;
    }
    Init_param(&p);
    slha_adjust(&p);
    p.THDM_model=2;
    p.tan_beta=tanbeta;
    for(i=1;i<=3;i++) {
        p.lambda_u[i][i]=1./tanbeta;
        p.lambda_d[i][i]=-tanbeta;
        p.lambda_l[i][i]=-tanbeta;
    }
    muW=2.*p.mass_W;
    mub=p.mass_b_pole/2.;
    if(!isfinite(muW)||!isfinite(mub)||muW<100.||mub<=0.) {
        fprintf(stderr,"A1U_BAD_SUPERISO_SCALE\n");return 3;
    }
    if(!high_wc(&sm,&p,m1,1,muW,mub) ||
       !high_wc(&h1,&p,m1,0,muW,mub) ||
       !high_wc(&h2,&p,m2,0,muW,mub)) return 3;
    mix_wc(&mixed,&sm,&h1,&h2,w1,w2);
    for(i=1;i<=10;i++) {
        if(!is_real_finite(mixed.C0[i])||
           !is_real_finite(mixed.C1[i])||
           !is_real_finite(mixed.C2[i])||
           !is_real_finite(mixed.Cp[i])) {
            fprintf(stderr,"A1U_NONREAL_MIXED_COEFFICIENT op=%d\n",i);
            return 3;
        }
    }
    /* Diagnostic 1: does the pinned vendor RG depend on the context
     * beyond the supplied fixed HIGH-scale Wilson coefficients?
     * Compare the FULL low-scale C0/C1/C2 vectors, not only the BR.
     */
    if(!evolve(&mixed,&p,m1,1,muW,mub,&lowSM) ||
       !evolve(&mixed,&p,m1,0,muW,mub,&lowH1) ||
       !evolve(&mixed,&p,m2,0,muW,mub,&lowH2))
        return 3;
    rgdiff_H1=maximum_low_diff(&lowSM,&lowH1);
    rgdiff_H2=maximum_low_diff(&lowSM,&lowH2);

    /* Diagnostic 2: use the SAME RG-evolved Wilson vectors in each
     * call to the unchanged bsgamma(). This separates genuine model
     * dependence inside the observable from context differences
     * created earlier by C_calculator_base1().
     */
    if(internal_reload) {
        /* Pre-fix reproduction: identical low-scale input but the
         * vendor helper recalculates context-specific HIGH-scale WC. */
        rawsm=observable_at_fixed_low(&lowSM,&mixed,&p,m1,1,muW,mub,0);
        raw1=observable_at_fixed_low(&lowSM,&mixed,&p,m1,0,muW,mub,0);
        raw2=observable_at_fixed_low(&lowSM,&mixed,&p,m2,0,muW,mub,0);
        printf("A1U_UNWRAPPED_CONTEXT_DIAGNOSTIC BR_SM=%.17g "
               "BR_H1=%.17g BR_H2=%.17g\n",rawsm,raw1,raw2);
        fflush(stdout);
    }
    bsm_low=observable_at_fixed_low(&lowSM,&mixed,&p,m1,1,muW,mub,internal_reload);
    b1_low=observable_at_fixed_low(&lowSM,&mixed,&p,m1,0,muW,mub,internal_reload);
    b2_low=observable_at_fixed_low(&lowSM,&mixed,&p,m2,0,muW,mub,internal_reload);
    printf("A1U_CONTEXT_DIAGNOSTIC RG_MAX_ABS_DELTA_H1=%.17g "
           "RG_MAX_ABS_DELTA_H2=%.17g "
           "FIXED_LOW_BR_SM=%.17g FIXED_LOW_BR_H1=%.17g "
           "FIXED_LOW_BR_H2=%.17g\n",
           rgdiff_H1,rgdiff_H2,bsm_low,b1_low,b2_low);
    fflush(stdout);
    /* Never silently choose the SM or a Higgs context if the
     * pinned vendor RG acts differently on identical high-scale
     * coefficients. This would require model-aware treatment.
     */
    if(!isfinite(rgdiff_H1)||!isfinite(rgdiff_H2)||
       rgdiff_H1>1.e-10 || rgdiff_H2>1.e-10) {
        fprintf(stderr,
          "A1U_FIXED_HIGH_RG_CONTEXT_DEPENDENCE_NEEDS_SOURCE_AUDIT "
          "maxH1=%.17g maxH2=%.17g\n",
          rgdiff_H1,rgdiff_H2);
        return 3;
    }
    if(!isfinite(bsm_low)||!isfinite(b1_low)||!isfinite(b2_low)||
       fabs(bsm_low-b1_low)>2.e-12 ||
       fabs(bsm_low-b2_low)>2.e-12) {
        fprintf(stderr,
           "A1U_FIXED_LOW_BSGAMMA_CONTEXT_DEPENDENCE_NEEDS_SOURCE_AUDIT "
           "SM=%.17g H1=%.17g H2=%.17g\n",
           bsm_low,b1_low,b2_low);
        return 3;
    }
    /* With explicit mixed high-scale matching, all contexts now use the
     * SAME physical inputs; do not interpolate full branching ratios. */
    mixBR=bsm_low;

    /* Independently compute full one-state reference observables
     * using that state's OWN matching and low-scale RG input.
     */
    ref1=real_br(&h1,&p,m1,0,muW,mub);
    ref2=real_br(&h2,&p,m2,0,muW,mub);
    refdeg=real_br(&sm,&p,m1,1,muW,mub);

    if(!isfinite(bsm_low)||!isfinite(b1_low)||!isfinite(b2_low)||
       !isfinite(mixBR)||!isfinite(ref1)||!isfinite(ref2)||
       !isfinite(refdeg)||mixBR<=0.||mixBR>.01) {
        fprintf(stderr,"A1U_NONFINITE_OR_UNPHYSICAL_OBSERVABLE\n");
        return 3;
    }
    printf("STATUS GATE_A1U_LEGACY_TWO_STATE_BR_PILOT_NOT_2026_EXCLUSION\n");
    printf("INTERNAL_CW_MODE=%s\n", internal_reload?"helper_reload":"none");
    printf("INPUT mH1_GeV=%.17g mH2_GeV=%.17g "
           "gamma_rad=%.17g tanbeta=%.17g muW_GeV=%.17g "
           "mu_b_GeV=%.17g\n",m1,m2,gamma,tanbeta,muW,mub);
    printf("WEIGHTS w1=%.17g w2=%.17g\n",w1,w2);
    for(i=7;i<=8;i++) {
        printf("MATCH op=%d sm_LO=%.17g "
               "delta1_LO=%.17g delta2_LO=%.17g zee_LO=%.17g\n",
               i,creal(sm.C0[i]),creal(h1.C0[i]-sm.C0[i]),
               creal(h2.C0[i]-sm.C0[i]),creal(mixed.C0[i]));
    }
    printf("INTERNAL_FIXED_LOW BR_SM_CONTEXT=%.17g "
           "BR_H1_CONTEXT=%.17g BR_H2_CONTEXT=%.17g\n",
           bsm_low,b1_low,b2_low);
    printf("FULL_SINGLE_REFERENCE br_H1=%.17g br_H2=%.17g "
           "br_SM=%.17g\n",ref1,ref2,refdeg);
    printf("FULL_LEGACY_ZEE_TWO_STATE_BR=%.17g\n",mixBR);
    printf("EXPERIMENTAL_LIKELIHOOD_VALIDATED false\n");
    printf("MODERN_2026_FULL_NNLO_VALIDATED false\n");
    printf("ZEE_BENCHMARK_ALLOWED_OR_EXCLUDED undetermined\n");
    return 0;
}
