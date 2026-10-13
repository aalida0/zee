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
 * The pinned SuperIso bsgamma() calculates small internal terms
 * by reloading LO high-scale Wilson coefficients with CW_calculator.
 * Because the source-audited internal dependence is AFFINE in the
 * reloaded LO C7/C8 for fixed LOW-SCALE inputs, that component
 * can be mixed by holding the combined LOW-SCALE arrays fixed,
 * evaluating bsgamma() with internal SM,H1,H2 parameters, and
 * forming BRint=BRint_SM+w1*(BRint_H1-BRint_SM)
 *                  +w2*(BRint_H2-BRint_SM).
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
static double real_br(const struct wc *high,
                      const struct parameters *base,
                      double inner_mass,int inner_is_sm,
                      double muW,double mub)
{
    double complex C0b[NWC]={0},C1b[NWC]={0},C2b[NWC]={0};
    double complex C0w[NWC]={0},C1w[NWC]={0},C2w[NWC]={0};
    double complex Cp[NWC]={0};
    struct parameters p;
    int i;
    at_state(&p,base,inner_mass,inner_is_sm);
    /* SuperIso APIs do not expose const for input coefficient
     * pointers. Copy them to fresh arrays for every internal
     * context so a vendor routine cannot mutate the shared
     * MIXED matching vectors between successive calls. */
    memcpy(C0w,high->C0,sizeof(C0w));
    memcpy(C1w,high->C1,sizeof(C1w));
    memcpy(C2w,high->C2,sizeof(C2w));
    memcpy(Cp,high->Cp,sizeof(Cp));
    C_calculator_base1(C0w,C1w,C2w,
        muW,C0b,C1b,C2b,mub,&p);
    for(i=1;i<=10;i++) {
        if(!is_real_finite(C0b[i])||
           !is_real_finite(C1b[i])||
           !is_real_finite(C2b[i])) {
            fprintf(stderr,"A1U_NONREAL_LOW_WILSON op=%d\n",i);
            return -1.;
        }
    }
    return bsgamma(C0b,C1b,C2b,Cp,mub,muW,&p);
}
int main(int argc,char **argv)
{
    double m1,m2,gamma,tanbeta,muW,mub,c,s,w1,w2;
    double bsm_low,b1_low,b2_low,mixBR;
    double ref1,ref2,refdeg;
    struct parameters p;
    struct wc sm={0},h1={0},h2={0},mixed={0};
    int i;

    if(argc!=5 ||
       !parse_input(argv[1],&m1)||
       !parse_input(argv[2],&m2)||
       !parse_input(argv[3],&gamma)||
       !parse_input(argv[4],&tanbeta)||
       !(200.<=m1 && m1<=m2 && m2<=10000.)||
       !(0.<=gamma && gamma<=1.57079632679489662)||
       !(0.25<=tanbeta && tanbeta<=100.)) {
        fprintf(stderr,
            "A1U_INPUT_ERROR usage: a1u_two_state mH1 mH2 gamma tanbeta"
            " with 200<=mH1<=mH2<=10000 and 0<=gamma<=pi/2\n");
        return 2;
    }
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
    /* Same MIXED low-scale WC input each time; only the internal
     * LO matching reloaded by bsgamma differs SM/H1/H2.
     * This is affine interpolation of the nuisance term, not an
     * average of single-Higgs physical branching ratios.
     */
    bsm_low=real_br(&mixed,&p,m1,1,muW,mub);
    b1_low=real_br(&mixed,&p,m1,0,muW,mub);
    b2_low=real_br(&mixed,&p,m2,0,muW,mub);
    mixBR=bsm_low+w1*(b1_low-bsm_low)+w2*(b2_low-bsm_low);

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
